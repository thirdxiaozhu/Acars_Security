from multiprocessing import managers
import time
import multiprocessing
from Util import *

from pyhackrf import *
from ctypes import *


MODE_DSP = 1001
MODE_CMU = 1002

class hackrf_tx_context(Structure):
    _fields_ = [("buffer", POINTER(c_ubyte)),
                ("last_tx_pos", c_int),
                ("buffer_length", c_int),
                ("to_repeat", c_int),
                ("have_repeated", c_int),
                ("mode", c_int),
                ("sleep_time", c_int)]

    def __init__(self):
        self.buffer = cast(create_string_buffer(2304000), POINTER(c_ubyte))  #需要首先分配内存


def getInfo():
    HackRF.setLogLevel(logging.INFO)
    pointer = HackRF.getDeviceListPointer()
    devicecount = pointer.contents.devicecount
    devices_serial_number = cast(
        pointer.contents.serial_numbers, POINTER(c_char_p))
    devices = []

    for i in range(devicecount):
        devices.append(devices_serial_number[i].decode()[-15:])

    return devices


class HackRfEvent(multiprocessing.Process):
    def __init__(self, serial, freq, repeattimes, interval, son_conn, mode):
        super().__init__()
        self.serial = serial
        self.freq = float(freq)
        self.repeattimes = repeattimes
        self.interval = interval
        self.son_conn = son_conn
        self.mode = mode
        #self.msg_q = multiprocessing.Queue()
        manager = multiprocessing.Manager()
        self.msg_q = manager.Queue()
        self.msg_q_l = manager.Lock()

        self._do_stop = False
        self._do_close = False

    def initiDevice(self):

        # Initialize pyHackRF library
        # Initialize HackRF instance (could pass board serial or index if specific board is needed)
        result = HackRF.initialize()
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :", result, ",", HackRF.getHackRfErrorCodeName(result))

        self._hackrf_broadcaster = HackRF()

        result = self._hackrf_broadcaster.open(self.serial)
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :", result, ",", HackRF.getHackRfErrorCodeName(result))
            return -1

        result = self._hackrf_broadcaster.setSampleRate(1152000)
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :", result, ",", HackRF.getHackRfErrorCodeName(result))
            return -1


        result = self._hackrf_broadcaster.setFrequency(int(self.freq * 1e6))
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :", result, ",", HackRF.getHackRfErrorCodeName(result))
            return -1

        # week gain (used for wire feed + attenuators)
        result = self._hackrf_broadcaster.setTXVGAGain(20)
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :", result, ",", HackRF.getHackRfErrorCodeName(result))
            return -1

        result = self._hackrf_broadcaster.setAmplifierMode(
            LibHackRfHwMode.HW_MODE_OFF)
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :", result, ",", HackRF.getHackRfErrorCodeName(result))
            return -1

        return 0

    def initContext(self):
        self._tx_context = hackrf_tx_context()
        #if length != 0:
        self._tx_context.last_tx_pos = 0
        self._tx_context.buffer_length = 0
        self._tx_context.to_repeat = self.repeattimes
        self._tx_context.have_repeated = 0
        self._tx_context.sleep_time = self.interval
        self._tx_context.mode = self.mode

    #def broadcast_data(self):

    def run(self):
        res = self.initiDevice()
        if res == 0:
            self.initContext()
            #self.isStopThread = KThread(target=self.isStopThreadEvent)
            #self.isStopThread.start()

            self.SizeThread = KThread(target=self.Sizing)
            self.SizeThread.start()

            result = self._hackrf_broadcaster.startTX(self.hackrfTXCB, self._tx_context)
            if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
                print("Error :", result, ",", HackRF.getHackRfErrorCodeName(result))

            while self._hackrf_broadcaster.isStreaming():
                time.sleep(0.01)

            result = self._hackrf_broadcaster.stopTX()
            if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
                print("Error :", result, ",", HackRF.getHackRfErrorCodeName(result))

        self.closeDevice(res)

    def IsStop(self):
        return self._do_stop

    def IsDeviceCLose(self):
        return self._do_close

    def getProcess(self):
        return int((self._tx_context.have_repeated + 1)/self._tx_context.to_repeat * 100)

    # do hackRF lib and instance cleanup at object destruction time

    def closeDevice(self, res):
        result = self._hackrf_broadcaster.close()
        print("close", result)
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :", result, ",", HackRF.getHackRfErrorCodeName(result))

        self._do_stop = True
        #self.isStopThread.kill()
        self.SizeThread.kill()

        result = HackRF.deinitialize()
        print("dein", result)
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :", result, ",", HackRF.getHackRfErrorCodeName(result))

        self.son_conn.send(res)

    def forceStop(self):
        self.closeDevice(0)

    def __del__(self):
        print("have del")

    def isStopThreadEvent(self):
        recv = self.son_conn.recv()
        print(recv)
        if recv == 1:
            self.forceStop()

    def getMsgQueue(self):
        return self.msg_q

    def hackrfTXCB(self, hackrf_transfer):
        user_tx_context = cast(hackrf_transfer.contents.tx_ctx,
                               POINTER(hackrf_tx_context))

        tx_buffer_length = hackrf_transfer.contents.valid_length
        if user_tx_context.contents.buffer_length == 0:
            if self.msg_q.empty():
                #return 0
                return -1
            else:
                self.msg_q_l.acquire()
                msg = self.msg_q.get()
                self.msg_q_l.release()
                msg_len = len(msg)
                user_tx_context.contents.buffer = (c_ubyte * msg_len).from_buffer_copy(msg)
                user_tx_context.contents.buffer_length = msg_len

        left = user_tx_context.contents.buffer_length - \
            user_tx_context.contents.last_tx_pos
        addr_dest = addressof(hackrf_transfer.contents.buffer.contents)
        addr_src = addressof(user_tx_context.contents.buffer.contents) + \
            user_tx_context.contents.last_tx_pos

        if left > tx_buffer_length:
            memmove(addr_dest, addr_src, tx_buffer_length)
            user_tx_context.contents.last_tx_pos += tx_buffer_length
            return 0
        else:
            memmove(addr_dest, addr_src, left)
            memset(addr_dest+left, 0, tx_buffer_length-left)
            user_tx_context.contents.buffer_length = 0
            user_tx_context.contents.last_tx_pos = 0

            return 0

    def Sizing(self):
        while 1:
            print(self.msg_q.qsize())
            time.sleep(0.1)

    def putMessage(self, iq_data, times):
        for i in range(times):
            self.msg_q_l.acquire()
            self.msg_q.put(iq_data)
            self.msg_q_l.release()

            print("!!!!!!!!!!!!!!!!", self.msg_q)