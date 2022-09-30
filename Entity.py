from HackRFThread import HackRfEvent
import multiprocessing
import queue
from Receiver import Receiver

import Util
from Message import Message

MODE_DSP = 1001
MODE_CMU = 1002

class Entity:

    def __init__(self):
        self._hackrf_serial = None
        self._rtl_serial = None
        self._recv_signal = None
        self._trans_freq = 131.45
        self._addr = None
        self._hackrf_event = None
        self._rtl_event = None
        #self.dataQueue = multiprocessing.Queue()
        #self.qtThread = Util.KThread(
        #    target=self.qtEvent, args=(self.qtQueue, self.qtSignals,))


    def putMessage(self, msgs):
        for msg in msgs:
                if msg.getSecurityLevel() == Message.NORMAL:
                    self._hackrf_event.putMessage(msg._IQdata)

        self.startHackRF()

        #if self._hackrf_event.getMsgQueue().qsize() != 0 and self._is_streaming == False:
        #    self.startHackRF()


    def getHackRF(self):
        return self._hackrf_serial

    def setHackRF(self, serial):
        self._hackrf_serial = serial

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



class DSP(Entity):

    def __init__(self) -> None:
        super().__init__()

    def initHackRF(self):
        self.parent_conn, self.son_conn = multiprocessing.Pipe()
        self._hackrf_event = HackRfEvent(self._hackrf_serial, self._trans_freq, 1, 2, self.son_conn, MODE_DSP)


    def startRtl(self):
        super().startRtl()
        self._rtl_event = Receiver(self._rtl_serial, self._trans_freq, self._addr, self._recv_signal, MODE_DSP)
        self._rtl_event.startRecv()


class CMU(Entity):
    def __init__(self) -> None:
        super().__init__()

    def initHackRF(self):
        self.parent_conn, self.son_conn = multiprocessing.Pipe()
        self._hackrf_event = HackRfEvent(self._hackrf_serial, self._trans_freq, 1, 2, self.son_conn, MODE_CMU)

    def startRtl(self):
        super().startRtl()
        self._rtl_event = Receiver(self._rtl_serial, self._trans_freq, self._addr, self._recv_signal, MODE_CMU)
        self._rtl_event.startRecv()

