import time
import multiprocessing
#import queue
from Util import *

from pyhackrf import *
from ctypes import *

import logging

logging.basicConfig()


MODE_DSP = 220
MODE_CMU = 210

dll_test = CDLL("bin/libacarstrans.so")

class Hackrf_devs(Structure):
    _fields_ = [
        ("is_repeat", c_bool),
        ("serial_number", POINTER(c_ubyte)),
        ("path", POINTER(c_ubyte)),
        ("vga_p", c_int),
        ("freq_p", c_int64),
        ("data", POINTER(c_ubyte))]


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

    def __init__(self, serial, freq, son_conn):
        super().__init__()
        self.serial = serial
        self.freq = float(freq)
        self.son_conn = son_conn
        self.msg_iq = None

        self._do_stop = False
        self._do_close = False


    def startWorking(self):
        self.to_start = multiprocessing.Process(target=self.run, name="hackrfrun")
        self.to_start.start()
    
    def stopWorking(self):
        self.to_start.kill()

    def run(self):
        hd = Hackrf_devs()
        hd.is_repeat = c_bool(False)
        hd.serial_number = (c_ubyte*len(self.serial)).from_buffer_copy(bytearray(self.serial.encode("latin1")))
        hd.vga_p = c_int(20)
        hd.freq_p = c_int64(int(self.freq * 1e6))
        hd.data = (c_ubyte * (len(self.msg_iq))).from_buffer_copy(bytearray(self.msg_iq))

        dll_test.Transmit.argtypes = [c_void_p]
        dll_test.Transmit(byref(hd))
        time.sleep(0.5)

        self.son_conn.send(1)

    def IsStop(self):
        return self._do_stop

    def IsDeviceCLose(self):
        return self._do_close

 
    def forceStop(self):
        self.closeDevice(0)

    def __del__(self):
        self.__logger.debug("have del")


    def putIQs(self, iq_data):
        self.msg_iq = iq_data
