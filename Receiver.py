import errno
from os import times
import socket
from subprocess import Popen
from time import sleep

from Util import *
from datetime import datetime
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



    def startRecv(self):
        self.udpServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpServer.bind(self.addr_4_udp)
        self.monitorThread = KThread(target=self.startMonitor)
        self.monitorThread.start()
        self.startAcarsdec()

    def startAcarsdec(self):
        j = self.addr
        r = str(self.freq)
        d = self.rtl_serial
        if self.mode == MODE_DSP:
            self.acarsdec = Popen(
                ["./acarsdec","-D", "-j", j, "-p", "-8", "-r", d, r], shell=False)
        elif self.mode == MODE_CMU:
            self.acarsdec = Popen(
                ["./acarsdec","-U", "-j", j, "-p", "-8", "-r", d, r], shell=False)
        else:
            return

    def startMonitor(self):
        print("Start monitoring")
        while True:
            data, xxx = self.udpServer.recvfrom(self.bufsize)
            data = data.decode()
            self.entity.receiveMessage(data)


    def stopRecv(self):
        try:
            self.acarsdec.kill()
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
            self.udpServer.shutdown(2)
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
