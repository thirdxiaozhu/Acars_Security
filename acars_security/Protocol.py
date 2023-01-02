from HackRFThread import HackRfEvent
from Receiver import Receiver
import multiprocessing
import Util
import Message
import json
import logging

MODE_DSP = 220
MODE_CMU = 210

MODE_ELSE = 230

class Protocol:
    def __init__(self, enum, entity):
        self.enum = enum
        self.entity = entity
        self.parent_conn = None
        self._hackrf_event = None
        self._rtl_event = None
        self.waiting_send = []

    def setSendingDevice(self, hackrf_serial, trans_freq):
        self.parent_conn, self.son_conn = multiprocessing.Pipe()
        self._hackrf_event = HackRfEvent(hackrf_serial, trans_freq, self.son_conn, self.enum)

    def setReceivingDevice(self, rtl_serial, trans_freq, addr):
        self._rtl_event = Receiver(rtl_serial, trans_freq, addr, self.enum, self)

    def startHackRFWoring(self):
        self.HackRFWorkThread = Util.KThread(target=self.hackRFWorking)
        self.HackRFWorkThread.start()

    def hackRFWorking(self):
        self._hackrf_event.startWorking()

        recv = self.parent_conn.recv()
        self._hackrf_event.stopWorking()
        self.HackRFWorkThread.kill()

    def forceStopDevices(self):
        try:
            self.parent_conn.send(1)
            self._rtl_event.stopRecv()
            del self._rtl_event
        except AttributeError:
            pass

    def startRtl(self):
        self._rtl_event.startRecv()

    def appendWaitsend(self, sec_level, paras, text, crc):
        text_slices = Util.cut_list(text, self.enum)
        msgs = self.generateMsgs(paras, text_slices, sec_level, crc)
        for msg in msgs:
            self.waiting_send.append(msg)
            self._hackrf_event.putIQs(msg._IQdata)

    def send(self):
        self.startHackRFWoring()

    def receive(self, msg):
        dict = json.loads(msg)
        label = dict.get("label")
        if label[0] != "\x5F":
            crc = dict.get("crc")[:2]
            arn = dict.get("flight") if self.enum == MODE_DSP else dict.get("tail")
            if self.enum == MODE_DSP:
                self.appendWaitsend(0, ("2","\x5F\x7F", arn, "D", "3", None, None, ""), "", crc)
            else:
                self.appendWaitsend(0, ("2","\x5F\x7F", arn, "3", "A", "M01A", "CA1234", ""), "", crc)

            self.send()
            self.entity.receiveMessage(dict)


    def generateMsgs(self, paras, slices, sec_level, crc):
        msgs = []
        for slice in slices:
            msg = Message.Message((None, self.enum, sec_level) + paras[:-1] + (slice, crc))
            msg.generateIQ()
            msgs.append(msg)

        return msgs




