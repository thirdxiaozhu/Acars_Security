from audioop import add
import socket
from subprocess import Popen
from ctypes import *

from Util import *
from datetime import datetime
import multiprocessing
from rtlsdr import RtlSdr


MODE_DSP = 220
MODE_CMU = 210

class Receiver:

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


    def __init__(self, serial, freq, addr, signal, mode, entity) -> None:
        self.addr = addr
        self.bufsize = 8192
        self.addr_4_udp = (self.addr.split(":")[0], int(self.addr.split(":")[1]))
        self.rtl_serial = serial
        self.freq = freq
        self.signal = signal
        self.mode = mode
        self.entity = entity
        self.ppm = "-8"



    def startRecv(self):
        self.udpServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpServer.bind(self.addr_4_udp)
        self.monitorThread = KThread(target=self.startMonitor)
        self.monitorThread.start()
        self.acarsdecThread = KThread(target=self.startAcarsdec)
        self.acarsdecThread.start()

    def startAcarsdec(self):
        #addr = self.addr
        #freq_str = str(self.freq)
        #serial = self.rtl_serial
        self.acarsProcess = RecvProcess(self.mode, self.addr,  self.rtl_serial, str(self.freq))
        self.acarsProcess.start()

        #v = c_int(1)
        #mode= c_int(MODE_DSP if self.mode == MODE_DSP else MODE_CMU)
        #ppm_i = (c_ubyte*len(self.ppm)).from_buffer_copy(bytearray(self.ppm.encode()))
        #Rawaddr = (c_ubyte*len(addr)).from_buffer_copy(bytearray(addr.encode()))
        #index_ = (c_ubyte*len(d)).from_buffer_copy(bytearray(d.encode()))
        #freq_ = (c_ubyte*len(freq_str)).from_buffer_copy(bytearray(freq_str.encode()))
        #dll_test.startRecv(v, mode, Rawaddr, ppm_i, index_, freq_)
        #if self.mode == MODE_DSP:
        #    self.acarsdec = Popen(
        #        ["bin/acarsdec","-D", "-v", "-j", j, "-p", "-8", "-r", d, r], shell=False)
        #elif self.mode == MODE_CMU:
        #    self.acarsdec = Popen(
        #        ["bin/acarsdec","-U", "-v", "-j", j, "-p", "-8", "-r", d, r], shell=False)
        #else:
        #    return

    def startMonitor(self):
        print("Start monitoring")
        while True:
            data, xxx = self.udpServer.recvfrom(self.bufsize)
            data = data.decode()
            self.entity.receiveMessage(data)


    def stopRecv(self):

        try:
            #self.udpServer.shutdown(2)
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
        print(self.dll_test)
        self.dll_test.startRecv(self.v, self.mode, self.Rawaddr, self.ppm_i, self.index_, self.freq_)
