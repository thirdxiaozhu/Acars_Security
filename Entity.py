from HackRFThread import HackRfEvent
import multiprocessing
import re
import json
from datetime import datetime

from Receiver import Receiver
import Util
import Crypto
import Message

MODE_DSP = 220
MODE_CMU = 210


class Entity:

    def __init__(self):
        self._hackrf_serial = None
        self._rtl_serial = None
        self._recv_signal = None
        self._trans_freq = 131.45
        self._addr = None
        self._hackrf_event = None
        self._rtl_event = None
        self._sym_key = None
        self._iv = None
        self._msg_signal = None
        self._sec_level = 0
        self.entity_num = None
        self.work_space = "users/"

    def putMessageParas(self, mode, paras):
        self.initHackRF()
        text = paras[7]

        if self._sec_level == Message.Message.NORMAL:
            pass
        elif self._sec_level == Message.Message.CUSTOM:
            text = self.symmetricEncrypt(text)

        text_slices = Util.cut_list(text, mode)
        print(text_slices)
        msgs = self.generateMsgs(mode, paras, text_slices)
        for msg in msgs:
            self._hackrf_event.putMessage(msg._IQdata)

        self.startHackRF()

    def generateMsgs(self, mode, paras, slices):
        msgs = []
        if mode == MODE_DSP:
            for slice in slices:
                msg = Message.Message((None, Message.UPLINK, self._sec_level) + paras[:-1] + (slice,))
                msg.generateIQ()

                msgs.append(msg)

        elif mode == MODE_CMU:
            for slice in slices:
                msg = Message.Message((None, Message.DOWNLINK, self._sec_level) + paras[:-1] + (slice,))
                msg.generateIQ()

                msgs.append(msg)

        return msgs


    def getHackRF(self):
        return self._hackrf_serial

    def setHackRF(self, serial):
        self._hackrf_serial = serial

    def initHackRF(self):
        pass

    def getRtl(self):
        return self._rtl_serial

    def setRtl(self, serial, signal):
        self._rtl_serial = serial
        self._recv_signal = signal

    def setFrequency(self, freq):
        if freq != '':
            self._trans_freq = float(freq)

    def getFrequency(self):
        return self._trans_freq

    def setHostAndPort(self, addr):
        self._addr = addr

    def getHostAndPort(self):
        return self._addr

    def genEntityNum(self):
        return self.entity_num

    def putMsgSignal(self, signal):
        self._msg_signal = signal


    def startHackRF(self):
        self.HackRFWorkThread = Util.KThread(target=self.hackRFWorking)
        self.HackRFWorkThread.start()

    def startRtl(self):
        pass
        #self._rtl_event.startRecv()

    def hackRFWorking(self):
        self._hackrf_event.start()

        recv = self.parent_conn.recv()
        self._hackrf_event.terminate()
        self.HackRFWorkThread.kill()

    def forceStopDevices(self):
        try:
            self.parent_conn.send(1)
            self._rtl_event.stopRecv()
            del self._rtl_event
        except AttributeError:
            pass

    def setCert(self, paras):
        Crypto.Security.cert_test(self.work_space, paras, self.entity_num)

    def compressMsg(self, text):
        for i in text:
            pp = Util.intTo6bit(i)
            bin = Util.intToBin(pp)
            print(bin)

    def setSymmetricKeyandIV(self, key, iv):
        self._sym_key = key
        self._iv = iv
        #self.symmetricEncrypt()

    def symmetricEncrypt(self, plain_text):
        cip = Crypto.Security.symmetricEncrypt(self._sym_key, self._iv, plain_text)
        return cip

    def symmetricDecrypt(self, cipher_text):
        Crypto.Security.symmetricDecrypt(self._sym_key, self._iv, cipher_text)

    def receiveMessage(self, msg):
        dict = json.loads(msg)

        timestamp = dict.get("timestamp") 
        timestamp = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")

        try:
            orient = "UPLINK" if re.compile(r"[A-Za-z]").match(dict.get("block_id")) else "DOWNLINK"
        except:
            orient = "aaa"

        text = dict.get("text")

        if self._sec_level == Message.Message.NORMAL:
            pass
        elif self._sec_level == Message.Message.CUSTOM:
            text = Crypto.Security.symmetricDecrypt(self._sym_key, self._iv, text)
        else:
            pass
        msg = Message.Message((timestamp, orient, 0, dict.get("mode"), dict.get("label"), dict.get("tail"),  dict.get("block_id"), dict.get("ack"), dict.get("msgno"), dict.get("flight"), text))

        return msg

    def setSecurityLevel(self, level):
        self._sec_level = level

class DSP(Entity):

    def __init__(self) -> None:
        super().__init__()
        self.work_space = self.work_space + "dsp/"
        self.entity_num = MODE_DSP

    def initHackRF(self):
        super().initHackRF()
        self.parent_conn, self.son_conn = multiprocessing.Pipe()
        self._hackrf_event = HackRfEvent(self._hackrf_serial, self._trans_freq, 1, 2, self.son_conn, MODE_DSP)


    def startRtl(self):
        super().startRtl()
        self._rtl_event = Receiver(self._rtl_serial, self._trans_freq, self._addr, self._recv_signal, MODE_DSP, self)
        self._rtl_event.startRecv()

    def receiveMessage(self, msg):
        ret = super().receiveMessage(msg)
        self._msg_signal.emit(ret, MODE_DSP)


class CMU(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.work_space = self.work_space + "cmu/"
        self.entity_num = MODE_CMU

    def initHackRF(self):
        super().initHackRF()
        self.parent_conn, self.son_conn = multiprocessing.Pipe()
        self._hackrf_event = HackRfEvent(self._hackrf_serial, self._trans_freq, 1, 2, self.son_conn, MODE_CMU)

    def startRtl(self):
        super().startRtl()
        self._rtl_event = Receiver(self._rtl_serial, self._trans_freq, self._addr, self._recv_signal, MODE_CMU, self)
        self._rtl_event.startRecv()

    def receiveMessage(self, msg):
        ret = super().receiveMessage(msg)
        self._msg_signal.emit(ret, MODE_CMU)

