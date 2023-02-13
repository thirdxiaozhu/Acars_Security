from HackRFThread import HackRfEvent
from Receiver import Receiver
import multiprocessing
import Util
import Message
import json
import logging
import time

MODE_DSP = 220
MODE_CMU = 210

MODE_ELSE = 230

class Protocol:
    def __init__(self, enum, entity):
        self.enum = enum
        self.entity = entity
        self._hackrf_event = None
        self._rtl_event = None
        self.waiting_send_queue = multiprocessing.Queue()
        self.msg_checked_dict = {}
        self.transingThread = Util.KThread(target=self.transitting)
        self.transingThread.start()

    def setSendingDevice(self, hackrf_serial, trans_freq):
        self.parent_hackrf_conn, self.son_hackrf_conn = multiprocessing.Pipe()
        self._hackrf_event = HackRfEvent(hackrf_serial, trans_freq, self.son_hackrf_conn, self.enum)

    def setReceivingDevice(self, rtl_serial, trans_freq, addr):
        self._rtl_event = Receiver(rtl_serial, trans_freq, addr, self.enum, self)

    def forceStopDevices(self):
        try:
            self.parent_hackrf_conn.send(1)
            self._rtl_event.stopRecv()
            del self._rtl_event
        except AttributeError:
            pass

    def startRtl(self):
        self._rtl_event.startRecv()

    def appendWaitsend(self, sec_level, paras, text, crc):
        text_slices = Util.cut_list(text, self.enum)
        msgs = self.generateMsgs(paras, text_slices, sec_level, crc) #只有ACK报文的元组才具有crc，依据此判断是否需要确认报文
        for msg in msgs:
            if crc is None:
                self.msg_checked_dict[msg.getCRC_ASCII()] = False
            else:
                self.msg_checked_dict[msg.getCRC_ASCII()] = True
            self.waiting_send_queue.put(msg)
            print(self.msg_checked_dict)


    def receive(self, msg):
        dict = json.loads(msg)
        label = dict.get("label")
        crc = dict.get("crc")[:2]
        if label[0] != "\x5F":
            arn = dict.get("flight") if self.enum == MODE_DSP else dict.get("tail")
            if self.enum == MODE_DSP:
                self.appendWaitsend(0, ("2","\x5F\x7F", arn, "D", "3", None, None, ""), "", crc)
            else:
                self.appendWaitsend(0, ("2","\x5F\x7F", arn, "3", "A", "M01A", self.entity.getId(), ""), "", crc)

        else:
            self.msg_checked_dict[crc] = True
        self.entity.receiveMessage(dict)


    def generateMsgs(self, paras, slices, sec_level, crc):
        msgs = []
        for i in range(len(slices)):
            suffix = Message.Message.ETB
            if i == len(slices) - 1:
                suffix = Message.Message.ETX
            msg = Message.Message((None, self.enum, sec_level) + paras[:-1] + (slices[i], crc, suffix))
            msg.generateIQ()
            msgs.append(msg)

        return msgs
    
    def transitting(self):
        parent_is_finsh, son_is_finish = multiprocessing.Pipe()
        while True:
            if self.waiting_send_queue.empty():
                time.sleep(0.1)
                continue
            msg = self.waiting_send_queue.get_nowait()
            #msg = self.waiting_send_queue.get(block=True)
            self._hackrf_event.putIQs(msg._IQdata)
            transProcess = Trans(self._hackrf_event, son_is_finish, self.parent_hackrf_conn)
            transProcess.start()

            parent_is_finsh.recv()
            transProcess.kill()
            del transProcess




class Trans(multiprocessing.Process):
    def __init__(self, hackrf_event, son_is_finish, parent_hackrf_conn):
        super().__init__()
        self.son_is_finish = son_is_finish
        self.parent_hackrf_conn = parent_hackrf_conn
        self._hackrf_event = hackrf_event

    def run(self):
        self._hackrf_event.startWorking()

        self.parent_hackrf_conn.recv()
        self._hackrf_event.stopWorking()
        self.son_is_finish.send("1")