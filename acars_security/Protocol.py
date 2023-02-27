from HackRFThread import HackRfEvent
from Receiver import Receiver
import multiprocessing
import Util
import Message
import json
import logging
import time
import hashlib

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
        self.currentIndex = 1
        self.msg_send_dict = {}
        self.msg_receive_dict = {}
        self.msg_receive_blocks_list = []
        self.msg_receive_blocks_hash_list = []
        self.msg_checked_dict = {}
        self.transingThread = Util.KThread(target=self.transitting)
        self.transingThread.start()

    def setSendingDevice(self, hackrf_serial, trans_freq):
        self.parent_hackrf_conn, self.son_hackrf_conn = multiprocessing.Pipe()
        self._hackrf_event = HackRfEvent(hackrf_serial, trans_freq, self.son_hackrf_conn)

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
        self.msg_send_dict[self.currentIndex] = hashlib.md5(text.encode("latin1"))
        text_slices = Util.cut_list(text, self.enum)
        msgs = self.generateMsgs(paras, text_slices, sec_level, crc) #只有ACK报文的元组才具有crc，依据此判断是否需要确认报文
        for msg in msgs:
            if crc is None:
                self.msg_checked_dict[msg.getCRC_ASCII()] = False
            else:
                self.msg_checked_dict[msg.getCRC_ASCII()] = True
            self.waiting_send_queue.put(msg)

    def clearItems(self):
        self.msg_receive_blocks_hash_list = []
        self.msg_receive_blocks_list = []
        self.msg_checked_dict = {}


    def receive(self, msg):
        dict = json.loads(msg)
        dict["statu"] = 1000
        dict["errormsg"] = ""
        return dict

    def generateMsgs(self, paras, slices, sec_level, crc):
        msgs = []
        for i in range(len(slices)):
            serial = paras[-1]
            if serial == "":
                #序列号从A开始
                serial = "M"  + ("%2s" % self.currentIndex).replace(" ", "0") + chr(65 + i)

            suffix = Message.Message.ETB
            if i == len(slices) - 1:
                suffix = Message.Message.ETX
            msg = Message.Message((None, self.enum, sec_level) + paras[:-2] + (slices[i], serial, crc, suffix))
            msg.generateIQ()
            msgs.append(msg)

        self.currentIndex = self.currentIndex + 1

        return msgs
    
    def transitting(self):
        parent_is_finsh, son_is_finish = multiprocessing.Pipe()
        while True:
            msg = self.waiting_send_queue.get(block=True)
            self._hackrf_event.putIQs(msg._IQdata)
            transProcess = Trans(self._hackrf_event, son_is_finish, self.parent_hackrf_conn)
            transProcess.start()

            parent_is_finsh.recv()
            transProcess.kill()
            del transProcess

            time.sleep(1)

class DSPProtocol(Protocol):
    def __init__(self, enum, entity):
        super().__init__(enum, entity)

    def receive(self, msg):
        dict = super().receive(msg)
        label = dict.get("label")
        crc = dict.get("crc")
        isEnd = dict.get("end")
        hash = ""
        self.entity.setCurrentArn(dict.get("tail"))

        if crc is not None:
            crc = crc[:2]

        if dict.get("text") is not None:
            hash = hashlib.md5(dict.get("text").encode("latin1")).hexdigest()
        if not self.msg_receive_blocks_hash_list.__contains__(hash):
            self.msg_receive_blocks_hash_list.append(hash)
        else:
            dict = {}
            dict["statu"] = 1001
            dict["errormsg"] = "Replay Attack!"
        self.msg_receive_blocks_list.append(dict.get("text"))

        #发送ACK应答
        if label[0] != "\x5F":
            arn = dict.get("flight")
            #self.appendWaitsend(0, ("2","\x5F\x7F", arn, "D", "3",  None, ""), "", crc)
            #acarsdec对于具有serial number的下行报文，会等到最后具有EXT的报文达到后，将正文重新组合再返回一个具有完整正文的json
            if isEnd is True:
                self.entity.receiveCompleteMsg(dict)
            else:
                pass
        else:
            self.msg_checked_dict[crc] = True  #确认对方已经收到己方之前发送的携带该crc的报文

        self.entity.receiveBlock(dict)



class CMUProtocol(Protocol):
    def __init__(self, enum, entity):
        super().__init__(enum, entity)


    def receive(self, msg):
        dict = super().receive(msg)
        label = dict.get("label")
        crc = dict.get("crc")
        isEnd = dict.get("end")
        hash = ""

        if crc is not None:
            crc = crc[:2]

        if dict.get("text") is not None:
            hash = hashlib.md5(dict.get("text").encode("latin1")).hexdigest()
        if not self.msg_receive_blocks_hash_list.__contains__(hash):
            self.msg_receive_blocks_hash_list.append(hash)
        else:
            dict = {}
            dict["statu"] = 1001
            dict["errormsg"] = "Replay Attack!"
        self.msg_receive_blocks_list.append(dict.get("text"))

        #发送ACK应答
        if label[0] != "\x5F":
            arn = dict.get("tail")
            #self.appendWaitsend(0, ("2","\x5F\x7F", arn, "3", "A",  self.entity.getId(), ""), "", crc)

            #当该报文为结尾报文ETX时
            if isEnd is True:
                complete_msg = ""
                #非ACK报文组合成一个完整的报文
                for i in self.msg_receive_blocks_list:
                   complete_msg = "" if i is None else (complete_msg + i)

                dict["text"] = complete_msg
                self.entity.receiveCompleteMsg(dict)
                #清空所有block
                self.msg_receive_blocks_list = []
        else:
            self.msg_checked_dict[crc] = True

        self.entity.receiveBlock(dict)




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