from os import times
import socket
from subprocess import Popen
from PyQt5.QtWidgets import *
from PyQt5 import QtCore

from Util import *
import json
import re
from datetime import datetime
from rtlsdr import RtlSdr


class Receiver(QtCore.QObject):
    addMessageSignal = QtCore.pyqtSignal(str)

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


    def __init__(self, mainWindow) -> None:
        super(Receiver, self).__init__()
        self.host = "127.0.0.1"
        self.port = 5555
        self.bufsize = 8192
        self.addr = (self.host, self.port)
        self.mainWindow = mainWindow
        self.initReceiver()
        self.initEvent()
        self.getRtls()

    def initReceiver(self):
        self.ipAddrEdit = self.mainWindow.findChild(QLineEdit, "AddressEdit")
        self.portEdit = self.mainWindow.findChild(QLineEdit, "PortEdit")
        self.recfreqEdit = self.mainWindow.findChild(QLineEdit, "ReceFreqEdit")
        self.rtlCombo = self.mainWindow.findChild(QComboBox, "rtlcombo")
        self.reloadRtlsBtn = self.mainWindow.findChild(QPushButton, "reloadRtlsBtn")
        self.startrecBtn = self.mainWindow.findChild(
            QPushButton, "StratReceiverBtn")
        self.stoprecBtn = self.mainWindow.findChild(
            QPushButton, "StopReceiverBtn")
        self.refreshrecBtn = self.mainWindow.findChild(
            QPushButton, "RefreshRecButton")
        self.messageList = self.mainWindow.findChild(
            QListWidget, "MessageList")
        self.detailEdit = self.mainWindow.findChild(QTextEdit, "detailEdit")

    def initEvent(self):
        self.startrecBtn.clicked.connect(self.startRecv)
        self.stoprecBtn.clicked.connect(self.stopRecv)
        self.refreshrecBtn.clicked.connect(self.refreshList)
        self.reloadRtlsBtn.clicked.connect(self.reloadRtls)

        self.addMessageSignal.connect(self.addMessage)

        self.messageList.itemClicked.connect(
            lambda: self.updateDetail())

    def getRtls(self):
        serial_numbers = RtlSdr.get_device_serial_addresses()
        for i in range(len(serial_numbers)):
            self.rtlCombo.addItem(str(i))

    def reloadRtls(self):
        for i in range(self.rtlCombo.count()):
            self.rtlCombo.removeItem(0)

        self.getRtls()


    def startRecv(self):
        self.host = self.ipAddrEdit.text()
        self.port = self.portEdit.text()
        self.addr = (self.host, int(self.port))
        self.freq = self.recfreqEdit.text()
        self.rtl = self.rtlCombo.currentText()

        self.udpServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpServer.bind(self.addr)
        self.monitorThread = KThread(target=self.startMonitor)
        self.monitorThread.start()
        self.startAcarsdec()

    def startAcarsdec(self):
        j = self.host + ":" + self.port
        r = self.freq
        d = self.rtl
        self.acarsdec = Popen(
            ["acarsdec", "-j", j, "-p", "-8", "-r", d, r], shell=False)

    def startMonitor(self):
        print("Start monitoring")
        while True:
            data, xxx = self.udpServer.recvfrom(self.bufsize)
            data = data.decode()
            self.addMessageSignal.emit(data)

    def updateDetail(self):

        self.detailEdit.clear()
        dict = json.loads(self.messageList.selectedItems()[0].text())
        timestamp = dict.get("timestamp") 
        timestamp = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S.%f")

        block_id = dict.get("block_id")
        pattern = re.compile(r"[A-Za-z]")
        mode = pattern.match(block_id)
        if mode is None:
            self.detailEdit.append(
                self.downlinkhtml % (timestamp, dict.get("freq"), dict.get("mode"), dict.get("label"), dict.get("tail"), dict.get("ack"), dict.get("block_id"),dict.get("flight"), dict.get("msgno"), dict.get("text")))
        else:
            self.detailEdit.append(
                self.uplinkhtml % (timestamp, dict.get("freq"), dict.get("mode"), dict.get("label"), dict.get("tail"), dict.get("ack"), dict.get("block_id"),dict.get("text")))


            

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

    def refreshList(self):
        self.detailEdit.clear()
        if self.messageList.count()>0:
            for i in range(self.messageList.count()-1,-1,-1):
                   self.messageList.removeItemWidget(self.messageList.takeItem(i))

    def addMessage(self, paraDict):
        self.messageList.addItem(paraDict)
