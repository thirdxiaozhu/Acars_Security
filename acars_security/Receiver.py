import socket
from ctypes import *

from Util import *
import multiprocessing
from rtlsdr import RtlSdr

import logging

logging.basicConfig()

MODE_DSP = 220
MODE_CMU = 210

class Receiver:
    __logger = logging.getLogger("Receiver")
    __logger.setLevel(logging.DEBUG)
    downlinkhtml = '''
                <div> 
                      <font color="red">  time: </font> %s <br>
                      <font color="red">  frequency: </font> %s <br>
                      <font color="red">  Mode: </font> %s  <br>
                      <font color="red">  Label: </font> %s <br>
                      <font color="red">  Arn: </font> %s  <br>
                      <font color="red">  Tak: </font> %s  <br>
                      <font color="red">  DBI: </font> %s  <br>
                      <font color="red">  FlightID: </font> %s  <br>
                      <font color="red">  Messge No.: </font> %s  <br>
                      <font color="red">  Text: </font> %s <br>
                </div>
                '''
    uplinkhtml = '''
                <div> 
                      <font color="red">  time: </font> %s <br>
                      <font color="red">  frequency: </font> %s <br>
                      <font color="red">  Mode: </font> %s  <br>
                      <font color="red">  Label: </font> %s <br>
                      <font color="red">  Arn: </font> %s  <br>
                      <font color="red">  Tak: </font> %s  <br>
                      <font color="red">  UBI: </font> %s  <br>
                      <font color="red">  Text: </font> %s <br>
                </div>
                '''


    def __init__(self, serial, freq, addr, mode, protocol) -> None:
        self.addr = addr
        self.bufsize = 8192
        self.addr_4_udp = (self.addr.split(":")[0], int(self.addr.split(":")[1]))
        self.rtl_serial = serial
        self.freq = freq
        self.mode = mode
        self.protocol = protocol
        self.ppm = "-8"



    def startRecv(self):
        self.udpServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udpServer.bind(self.addr_4_udp)
        self.monitorThread = KThread(target=self.startMonitor)
        self.monitorThread.start()
        self.acarsdecThread = KThread(target=self.startAcarsdec)
        self.acarsdecThread.start()

    def startAcarsdec(self):
        self.acarsProcess = RecvProcess(self.mode, self.addr,  self.rtl_serial, str(self.freq))
        self.acarsProcess.start()


    def startMonitor(self):
        self.__logger.debug("Start monitoring")
        while True:
            data, xxx = self.udpServer.recvfrom(self.bufsize)
            data = data.decode("latin1")
            self.__logger.debug(data)
            self.protocol.receive(data)


    def stopRecv(self):

        try:
            self.acarsProcess.terminate()
            self.acarsProcess.kill()
            pass
        except AttributeError:
            pass
        try:
            self.acarsdecThread.kill()
        except AttributeError:
            pass

        try:
            self.monitorThread.kill()
        except AttributeError:
            pass

        try:
            del self.monitorThread
        except AttributeError:
            pass


        try:
            #self.udpServer.shutdown()
            self.udpServer.close()
        except AttributeError:
            pass

        try:
            del self.udpServer
        except AttributeError:
            pass


def getRtls():
    serials = RtlSdr.get_device_serial_addresses()
    devices = []
    for i in range(len(serials)):
        devices.append(str(i))
    return devices

class RecvProcess(multiprocessing.Process):
    def __init__(self, mode, addr, index, freq):
        super().__init__()
        self.dll_test = CDLL("/home/jiaxv/inoproject/Acars_Security/bin/libacarsrec.so")
        ppm = "-8"
        self.v = c_int(1)
        self.mode= c_int(MODE_DSP if mode == MODE_DSP else MODE_CMU)
        self.ppm_i = (c_ubyte*len(ppm)).from_buffer_copy(bytearray(ppm.encode()))
        self.Rawaddr = (c_ubyte*len(addr)).from_buffer_copy(bytearray(addr.encode()))
        self.index_ = (c_ubyte*len(index)).from_buffer_copy(bytearray(index.encode()))
        self.freq_ = (c_ubyte*len(freq)).from_buffer_copy(bytearray(freq.encode()))

    def run(self):
        self.dll_test.startRecv(self.v, self.mode, self.Rawaddr, self.ppm_i, self.index_, self.freq_)
