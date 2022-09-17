from os import times
import socket
from subprocess import Popen
from time import sleep

from Util import *
import json
import re
from datetime import datetime
from rtlsdr import RtlSdr


MODE_DSP = 1001
MODE_CMU = 1002

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


    def __init__(self, serial, freq, addr, signal, mode) -> None:
        #self.host = "127.0.0.1"
        #self.port = 5555
        self.addr = addr
        self.bufsize = 8192
        self.addr_4_udp = (self.addr.split(":")[0], int(self.addr.split(":")[1]))
        self.rtl_serial = serial
        self.freq = freq
        self.signal = signal
        self.mode = mode

    #def reloadRtls(self):
    #    for i in range(self.rtlCombo.count()):
    #        self.rtlCombo.removeItem(0)

    #    self.getRtls()


    def startRecv(self):
        self.udpServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpServer.bind(self.addr_4_udp)
        self.monitorThread = KThread(target=self.startMonitor)
        self.monitorThread.start()
        self.startAcarsdec()

    def startAcarsdec(self):
        #j = self.host + ":" + str(self.port)
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
            self.signal.emit(data, self.mode)

    #def updateDetail(self):
#
    #    self.detailEdit.clear()
    #    dict = json.loads(self.messageList.selectedItems()[0].text())
    #    timestamp = dict.get("timestamp") 
    #    timestamp = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")
#
    #    block_id = dict.get("block_id")
    #    pattern = re.compile(r"[A-Za-z]")
    #    mode = pattern.match(block_id)
    #    if mode is None:
    #        self.detailEdit.append(
    #            self.downlinkhtml % (timestamp, dict.get("freq"), dict.get("mode"), dict.get("label"), dict.get("tail"), dict.get("ack"), dict.get("block_id"),dict.get("flight"), dict.get("msgno"), dict.get("text")))
    #    else:
    #        self.detailEdit.append(
    #            self.uplinkhtml % (timestamp, dict.get("freq"), dict.get("mode"), dict.get("label"), dict.get("tail"), dict.get("ack"), dict.get("block_id"),dict.get("text")))
#

            

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

    #def refreshList(self):
    #    self.detailEdit.clear()
    #    if self.messageList.count()>0:
    #        for i in range(self.messageList.count()-1,-1,-1):
    #               self.messageList.removeItemWidget(self.messageList.takeItem(i))

    #def addMessage(self, paraDict):
    #    self.messageList.addItem(paraDict)


def getRtls():
    serials = RtlSdr.get_device_serial_addresses()
    devices = []
    for i in range(len(serials)):
        devices.append(str(i))
    return devices
