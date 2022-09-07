import time
import multiprocessing
from Util import *

from pyhackrf import *
from ctypes import *


class hackrf_tx_context(Structure):
    _fields_ = [("buffer", POINTER(c_ubyte)),
                ("last_tx_pos", c_int),
                ("buffer_length", c_int),
                ("to_repeat", c_int),
                ("have_repeated", c_int),
                ("sleep_time", c_int)]


def hackrfTXCB(hackrf_transfer):
    user_tx_context = cast(hackrf_transfer.contents.tx_ctx,
                           POINTER(hackrf_tx_context))
    tx_buffer_length = hackrf_transfer.contents.valid_length
    left = user_tx_context.contents.buffer_length - \
        user_tx_context.contents.last_tx_pos
    addr_dest = addressof(hackrf_transfer.contents.buffer.contents)
    addr_src = addressof(user_tx_context.contents.buffer.contents) + \
        user_tx_context.contents.last_tx_pos

    to_repeat_time = user_tx_context.contents.to_repeat
    have_repeated_time = user_tx_context.contents.have_repeated
    sleep_time = user_tx_context.contents.sleep_time

    if (left > tx_buffer_length):
        memmove(addr_dest, addr_src, tx_buffer_length)
        user_tx_context.contents.last_tx_pos += tx_buffer_length
        return 0
    else:
        memmove(addr_dest, addr_src, left)
        memset(addr_dest+left, 0, tx_buffer_length-left)

        #重复插入addr_dest地址之后
        if to_repeat_time > 0 and have_repeated_time < to_repeat_time-1:
            print(to_repeat_time, sleep_time)
            time.sleep(sleep_time)
            user_tx_context.contents.last_tx_pos = 0
            left = user_tx_context.contents.buffer_length - \
                user_tx_context.contents.last_tx_pos  # buffer_length - 0
            addr_src = addressof(user_tx_context.contents.buffer.contents)

            user_tx_context.contents.have_repeated += 1
            print(user_tx_context.contents.have_repeated)

            return 0
        else:
            return -1


def getInfo():
    HackRF.setLogLevel(logging.INFO)
    pointer = HackRF.getDeviceListPointer()
    devicecount = pointer.contents.devicecount
    devices_serial_number = cast(
        pointer.contents.serial_numbers, POINTER(c_char_p))
    devices = []

    for i in range(devicecount):
        devices.append(devices_serial_number[i].decode())

    return devices


class HackRfEvent(multiprocessing.Process):
    def __init__(self, serial, freq, repeattimes, interval, int8Stream, qtQueue, son_conn):
        super().__init__()
        self.serial = serial
        self.freq = float(freq)
        self.repeattimes = repeattimes
        self.interval = interval
        self.int8Stream = int8Stream
        self.qtQueue = qtQueue
        self.son_conn = son_conn
        self._do_stop = False
        self._do_close = False
        self.q = multiprocessing.Queue()

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
        print(self.int8Stream[:10])
        data = bytearray(self.int8Stream)
        print(data[:10])
        length = len(data)
        if length != 0:
            self._tx_context.last_tx_pos = 0
            self._tx_context.buffer_length = length
            self._tx_context.to_repeat = self.repeattimes
            self._tx_context.have_repeated = 0
            self._tx_context.sleep_time = self.interval
            self._tx_context.buffer = (
                c_ubyte*self._tx_context.buffer_length).from_buffer_copy(data)

    #def broadcast_data(self):

    def run(self):
        res = self.initiDevice()
        print(res)
        if res == 0:
            self.initContext()
            self.isStopThread = KThread(target=self.isStopThreadEvent)
            self.updateProcessThread = KThread(target=self.updateTransProcessEvent)
            self.isStopThread.start()
            self.updateProcessThread.start()

            result = self._hackrf_broadcaster.startTX(hackrfTXCB, self._tx_context)
            if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
                print("Error :", result, ",", HackRF.getHackRfErrorCodeName(result))

            while self._hackrf_broadcaster.isStreaming():
                time.sleep(0)

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
        #result = self._hackrf_broadcaster.stopTX()
        #print("stop", result)
        #if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
        #    print("Error :",result, ",", HackRF.getHackRfErrorCodeName(result))

        result = self._hackrf_broadcaster.close()
        print("close", result)
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :", result, ",", HackRF.getHackRfErrorCodeName(result))

        self._do_stop = True
        self.son_conn.send(res)
        self.updateProcessThread.kill()
        self.isStopThread.kill()

        result = HackRF.deinitialize()
        print("dein", result)
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :", result, ",", HackRF.getHackRfErrorCodeName(result))

    def forceStop(self):
        self.closeDevice(0)

    def __del__(self):
        print("have del")

    def isStopThreadEvent(self):
        recv = self.son_conn.recv()
        if recv == 1:
            self.forceStop()

    def updateTransProcessEvent(self):
        while True:
            num = self.getProcess()
            self.qtQueue.put(num)

            time.sleep(0.5)
