from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import time
import os


import HackRFThread
import Receiver
import Entity
import Message

ALL = 0
RECV = 1
TRAN = 2



class Interface(QtCore.QObject):
    addMessageSignal = QtCore.pyqtSignal(str, int)

    def __init__(self, mainWindow) -> None:
        super(Interface, self).__init__()
        self.mainWindow = mainWindow
        self.dsp = Entity.DSP()
        self.cmu = Entity.CMU()
        self.initComponents()
        self.initEvent()
        self.getDevices()
        self.initDevices(ALL)

    def initComponents(self):
        self.dsp_receiver_combo = self.mainWindow.findChild(
            QComboBox, "dsp_receiver_combo")
        self.dsp_transmitter_combo = self.mainWindow.findChild(
            QComboBox, "dsp_transmitter_combo")
        self.cmu_receiver_combo = self.mainWindow.findChild(
            QComboBox, "cmu_receiver_combo")
        self.cmu_transmitter_combo = self.mainWindow.findChild(
            QComboBox, "cmu_transmitter_combo")
        self.dsp_receiver_confirm = self.mainWindow.findChild(
            QPushButton, "dsp_receiver_confirm")
        self.dsp_transmitter_confirm = self.mainWindow.findChild(
            QPushButton, "dsp_transmitter_confirm")
        self.cmu_receiver_confirm = self.mainWindow.findChild(
            QPushButton, "cmu_receiver_confirm")
        self.cmu_transmitter_confirm = self.mainWindow.findChild(
            QPushButton, "cmu_transmitter_confirm")
        self.dsp_rtl_label = self.mainWindow.findChild(QLabel, "dsp_rtl_label")
        self.dsp_hackrf_label = self.mainWindow.findChild(
            QLabel, "dsp_hackrf_label")
        self.cmu_rtl_label = self.mainWindow.findChild(QLabel, "cmu_rtl_label")
        self.cmu_hackrf_label = self.mainWindow.findChild(
            QLabel, "cmu_hackrf_label")
        self.dsp_start_btn = self.mainWindow.findChild(QPushButton, "dsp_start_btn")
        self.dsp_frequency_edit = self.mainWindow.findChild(QLineEdit, "dsp_frequency_edit")
        self.dsp_addr_edit = self.mainWindow.findChild(QLineEdit, "dsp_addr_edit")
        self.dsp_send_test_btn = self.mainWindow.findChild(QPushButton, "dsp_send_test_btn")
        self.dsp_stop_btn = self.mainWindow.findChild(QPushButton, "dsp_stop_btn")
        self.dsp_msg_list = self.mainWindow.findChild(QListWidget, "dsp_msg_list")
        self.cmu_start_btn = self.mainWindow.findChild(QPushButton, "cmu_start_btn")
        self.cmu_frequency_edit = self.mainWindow.findChild(QLineEdit, "cmu_frequency_edit")
        self.cmu_addr_edit = self.mainWindow.findChild(QLineEdit, "cmu_addr_edit")
        self.cmu_send_test_btn = self.mainWindow.findChild(QPushButton, "cmu_send_test_btn")
        self.cmu_stop_btn = self.mainWindow.findChild(QPushButton, "cmu_stop_btn")
        self.cmu_msg_list = self.mainWindow.findChild(QListWidget, "cmu_msg_list")

    def initEvent(self):
        self.dsp_receiver_confirm.clicked.connect(lambda: self.confirmDevice(
            RECV, self.dsp_receiver_combo, self.dsp_rtl_label, self.dsp))
        self.dsp_transmitter_confirm.clicked.connect(lambda: self.confirmDevice(
            TRAN, self.dsp_transmitter_combo, self.dsp_hackrf_label, self.dsp))
        self.cmu_receiver_confirm.clicked.connect(lambda: self.confirmDevice(
            RECV, self.cmu_receiver_combo, self.cmu_rtl_label, self.cmu))
        self.cmu_transmitter_confirm.clicked.connect(lambda: self.confirmDevice(
            TRAN, self.cmu_transmitter_combo, self.cmu_hackrf_label, self.cmu))
        self.dsp_start_btn.clicked.connect(lambda: self.startWorking(Entity.MODE_DSP))
        self.dsp_stop_btn.clicked.connect(lambda:self.stopWorking(Entity.MODE_DSP))
        self.dsp_send_test_btn.clicked.connect(lambda: self.sendTest(Entity.MODE_DSP))
        self.cmu_start_btn.clicked.connect(lambda: self.startWorking(Entity.MODE_CMU))
        self.cmu_stop_btn.clicked.connect(lambda:self.stopWorking(Entity.MODE_CMU))
        self.cmu_send_test_btn.clicked.connect(lambda: self.sendTest(Entity.MODE_CMU))

        self.addMessageSignal.connect(self.addMessage)

    def getDevices(self):
        self.hackrfs = HackRFThread.getInfo()
        #print(self.hackrfs)
        self.rtls = Receiver.getRtls()
        #print(self.rtls)

    def initDevices(self, sign):
        if sign == RECV:
            self.initRtls(self.dsp_receiver_combo)
            self.initRtls(self.cmu_receiver_combo)
        elif sign == TRAN:
            self.initHackRFs(self.dsp_transmitter_combo)
            self.initHackRFs(self.cmu_transmitter_combo)
        else:
            self.initRtls(self.dsp_receiver_combo)
            self.initRtls(self.cmu_receiver_combo)
            self.initHackRFs(self.dsp_transmitter_combo)
            self.initHackRFs(self.cmu_transmitter_combo)

    def initHackRFs(self, combo):
        for i in range(combo.count()):
            combo.removeItem(0)
        for i in self.hackrfs:
            combo.addItem(i)

    def reloadHackRFs(self):
        for i in range(self.device_combo.count()):
            self.device_combo.removeItem(0)

        self.getDevices()

    def initRtls(self, combo):
        for i in range(combo.count()):
            combo.removeItem(0)
        for i in self.rtls:
            combo.addItem(i)

    def confirmDevice(self, sign, combo, label, entity):
        serial = combo.currentText()
        if sign == RECV:
            entity.setRtl(serial, self.addMessageSignal)
            self.rtls.remove(serial)
            self.initDevices(RECV)
        elif sign == TRAN:
            entity.setHackRF(serial)
            self.hackrfs.remove(serial)
            self.initDevices(TRAN)
        else:
            return

        combo.setEnabled(False)
        label.setText(serial)

    def startWorking(self, mode):
        if mode == Entity.MODE_DSP:
            self.dsp.setFrequency(self.dsp_frequency_edit.text())
            self.dsp.setHostAndPort(self.dsp_addr_edit.text())
            self.dsp.startRtl()
            #self.dsp.startHackRF()

        elif mode == Entity.MODE_CMU:
            self.cmu.setFrequency(self.cmu_frequency_edit.text())
            self.cmu.setHostAndPort(self.cmu_addr_edit.text())
            self.cmu.startRtl()
            #self.cmu.startHackRF()


    def stopWorking(self, mode):
        if mode == Entity.MODE_DSP:
            self.dsp.forceStopDevices()
        elif mode == Entity.MODE_CMU:
            self.cmu.forceStopDevices()

    def sendTest(self, mode):

        if mode == Entity.MODE_DSP:
            msg = Message.Message(Message.UPLINK)
            msg.setMode("2")
            msg.setLabel("23")
            msg.setArn("SP-LDE")
            msg.setUDbi("A")
            msg.setAck("A")
            #msg.setSerial("M01A")
            #msg.setFlight("CA1234")
            msg.setText("Hello_World_From_AirAirAirAir")
            msg.setSecurityLevel(Message.Message.NORMAL)

            msg.generateIQ()
            #msg = Message.Message(Message.UPLINK)
            #msg.setMode("2")
            #msg.setLabel("23")
            #msg.setArn("SP-LDE")
            #msg.setUDbi("A")
            #msg.setAck("A")
            #msg.setText("Hello_World_From_Ground")
            #msg.setSecurityLevel(Message.Message.NORMAL)

            #msg.generateIQ()

            self.dsp.initHackRF()
            self.dsp.putMessage(msg, 3)
            #self.dsp.startHackRF()

        if mode == Entity.MODE_CMU:
            msg = Message.Message(Message.DOWNLINK)
            msg.setMode("2")
            msg.setLabel("23")
            msg.setArn("SP-LDE")
            msg.setUDbi("9")
            msg.setAck("A")
            msg.setSerial("M01A")
            msg.setFlight("CA1234")
            msg.setText("Hello_World")
            msg.setSecurityLevel(Message.Message.NORMAL)

            msg.generateIQ()
            self.cmu.initHackRF()
            self.cmu.putMessage(msg, 3)
            #self.cmu.startHackRF()


    def addMessage(self, paraDict, mode):
        if mode == Entity.MODE_DSP:
            self.dsp_msg_list.addItem(paraDict)
        elif mode == Entity.MODE_CMU:
            self.cmu_msg_list.addItem(paraDict)
        else:
            pass

    def closeWindow(self):
        self.dsp.forceStopDevices()
        self.cmu.forceStopDevices()
        #self.receiver.stopRecv()

        time.sleep(1)
        os._exit(0)