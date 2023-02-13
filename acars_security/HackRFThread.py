import time
import multiprocessing
#import queue
from Util import *

from pyhackrf import *
from ctypes import *

import logging

logging.basicConfig()

"""
尚无法使用多进程队列动态管理消息，未找出原因
"""

MODE_DSP = 220
MODE_CMU = 210

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


#class HackRfEvent(multiprocessing.Process):
class HackRfEvent:
    __logger = logging.getLogger("HackRFEvent")
    __logger.setLevel(logging.DEBUG)

    def __init__(self, serial, freq, son_conn, mode):
        super().__init__()
        self.serial = serial
        self.freq = float(freq)
        self.son_conn = son_conn
        self.mode = mode
        self.msg_queue = multiprocessing.Queue()
        self.msg_iq = None

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
        result = self._hackrf_broadcaster.setTXVGAGain(25)
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
        self._tx_context.buffer_length = len(self.msg_iq)
        self._tx_context.mode = self.mode
        self._tx_context.buffer = (
                c_ubyte*self._tx_context.buffer_length).from_buffer_copy(bytearray(self.msg_iq))

    #def broadcast_data(self):


    def startWorking(self):
        self.to_start = multiprocessing.Process(target=self.run, name="hackrfrun")
        self.to_start.start()
    
    def stopWorking(self):
        self.to_start.terminate()

    def run(self):
        res = self.initiDevice()
        if res == 0:
            self.initContext()
            result = self._hackrf_broadcaster.startTX(self.hackrfTXCB, self._tx_context)
            if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
                print("Error :", result, ",", HackRF.getHackRfErrorCodeName(result))

            while self._hackrf_broadcaster.isStreaming():
                time.sleep(0.3)

            result = self._hackrf_broadcaster.stopTX()
            if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
                print("Error :", result, ",", HackRF.getHackRfErrorCodeName(result))

        self.closeDevice(res)

    def IsStop(self):
        return self._do_stop

    def IsDeviceCLose(self):
        return self._do_close

    # do hackRF lib and instance cleanup at object destruction time
    def closeDevice(self, res):
        result = self._hackrf_broadcaster.close()
        self.__logger.debug("close  %d" % result)
        if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
            print("Error :", result, ",", HackRF.getHackRfErrorCodeName(result))

        self._do_stop = True

        #result = HackRF.deinitialize()
        #    
        #self.__logger.debug("dein  %d" % result)
        #if (result != LibHackRfReturnCode.HACKRF_SUCCESS):
        #    print("Error :", result, ",", HackRF.getHackRfErrorCodeName(result))

        self.son_conn.send(res)

    def forceStop(self):
        self.closeDevice(0)

    def __del__(self):
        self.__logger.debug("have del")

    def isStopThreadEvent(self):
        pass
    def getMsgQueue(self):
        return self.msg_queue

    def hackrfTXCB(self, hackrf_transfer):
        user_tx_context = cast(hackrf_transfer.contents.tx_ctx,
                               POINTER(hackrf_tx_context))

        tx_buffer_length = hackrf_transfer.contents.valid_length
        #msg = bytearray(self.msg_iq)
        #user_tx_context.contents.buffer = (c_ubyte * len(msg)).from_buffer_copy(msg)
        #user_tx_context.contents.buffer_length = len(msg)
        #if user_tx_context.contents.buffer_length == 0:
        #    if self.msg_queue.empty():
        #        #return 0
        #        return -1
        #    else:
        #        msg = self.msg_queue.get()
        #        msg_len = len(msg)
        #        user_tx_context.contents.buffer = (c_ubyte * msg_len).from_buffer_copy(msg)
        #        user_tx_context.contents.buffer_length = msg_len

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
            #user_tx_context.contents.buffer_length = 0
            #user_tx_context.contents.last_tx_pos = 0

            return -1

    def putIQs(self, iq_data):
        #self.msg_queue.put(iq_data)
        self.msg_iq = iq_data
