from base64 import encode
from cgitb import text
from lib2to3.pgen2.token import RPAR
from re import A
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import time
import os
import re


import HackRFThread
import Receiver
import Entity
import Message
import Util

ALL = 0
RECV = 1
TRAN = 2

SUCCESS = 0
FAIL = 1



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

        self.dsp_mode_edit = self.mainWindow.findChild(QLineEdit, "dsp_mode_edit")
        self.dsp_label_edit = self.mainWindow.findChild(QLineEdit, "dsp_label_edit")
        self.dsp_arn_edit = self.mainWindow.findChild(QLineEdit, "dsp_arn_edit")
        self.dsp_ubi_edit = self.mainWindow.findChild(QLineEdit, "dsp_ubi_edit")
        self.dsp_ack_edit = self.mainWindow.findChild(QLineEdit, "dsp_ack_edit")
        self.dsp_text_edit = self.mainWindow.findChild(QTextEdit, "dsp_text_edit")
        self.dsp_send_btn = self.mainWindow.findChild(QPushButton, "dsp_send_btn")

        self.cmu_mode_edit = self.mainWindow.findChild(QLineEdit, "cmu_mode_edit")
        self.cmu_label_edit = self.mainWindow.findChild(QLineEdit, "cmu_label_edit")
        self.cmu_arn_edit = self.mainWindow.findChild(QLineEdit, "cmu_arn_edit")
        self.cmu_dbi_edit = self.mainWindow.findChild(QLineEdit, "cmu_dbi_edit")
        self.cmu_ack_edit = self.mainWindow.findChild(QLineEdit, "cmu_ack_edit")
        self.cmu_id_edit = self.mainWindow.findChild(QLineEdit, "cmu_id_edit")
        self.cmu_text_edit = self.mainWindow.findChild(QTextEdit, "cmu_text_edit")
        self.cmu_send_btn = self.mainWindow.findChild(QPushButton, "cmu_send_btn")



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
        self.dsp_send_btn.clicked.connect(lambda: self.send(Entity.MODE_DSP))
        self.cmu_send_btn.clicked.connect(lambda: self.send(Entity.MODE_CMU))

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
            #paras = self.getParas(Message.UPLINK)
            msg.setMode("2")
            msg.setLabel("23")
            msg.setArn("SP-LDE")
            msg.setUDbi("A")
            msg.setAck("A")
            msg.setText("Hello_World_From_AirAirAirAir")
            msg.setSecurityLevel(Message.Message.NORMAL)

            msg.generateIQ()
            self.dsp.initHackRF()
            self.dsp.putMessage(msg)
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
            self.cmu.putMessage(msg)
            #self.cmu.startHackRF()

    def send(self, mode):

        if mode == Entity.MODE_DSP:
            paras = self.getParas(Message.UPLINK)
            if paras == FAIL:
                return

            text_slices = Util.cut_list(paras[5], 220)
            msgs = []
            for slice in text_slices:
                msg = Message.Message(Message.UPLINK)
                msg.setMode(paras[0])
                msg.setLabel(paras[1])
                msg.setArn(paras[2])
                msg.setUDbi(paras[3])
                msg.setAck(paras[4])
                #msg.setText(paras[5])
                msg.setText(slice)
                msg.setSecurityLevel(Message.Message.NORMAL)

                msg.generateIQ()
                msgs.append(msg)
                
            self.dsp.initHackRF()
            self.dsp.putMessage(msgs)

        if mode == Entity.MODE_CMU:
            paras = self.getParas(Message.DOWNLINK)
            if paras == FAIL:
                return

            text_slices = Util.cut_list(paras[7], 210)
            msgs = []
            for slice in text_slices:
                msg = Message.Message(Message.DOWNLINK)
                msg.setMode(paras[0])
                msg.setLabel(paras[1])
                msg.setArn(paras[2])
                msg.setUDbi(paras[3])
                msg.setAck(paras[4])
                msg.setSerial(paras[5])
                msg.setFlight(paras[6])
                #msg.setText(paras[7])
                msg.setText(slice)
                msg.setSecurityLevel(Message.Message.NORMAL)
                msg.generateIQ()
                msgs.append(msg)

            self.cmu.initHackRF()
            self.cmu.putMessage(msgs)


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

    def getParas(self, mode):
        arn_pattern = re.compile(r"^[A-Z0-9-.]{7}")
        ack_pattern = re.compile(r"^[A-Za-z]")
        ubi_pattern = re.compile(r"[A-Za-z]")
        dbi_pattern = re.compile(r"[0-9]")


        if mode == Message.UPLINK:
            modeInput = self.dsp_mode_edit.text()
            arnInput = ("%7s" % self.dsp_arn_edit.text()).replace(" ", ".")
            labelInput = self.dsp_label_edit.text()
            dubiInput = self.dsp_ubi_edit.text()
            ackInput = self.dsp_ack_edit.text()
            text = self.dsp_text_edit.toPlainText()
        elif mode == Message.DOWNLINK:
            modeInput = self.cmu_mode_edit.text()
            arnInput = ("%7s" % self.cmu_arn_edit.text()).replace(" ", ".")
            labelInput = self.cmu_label_edit.text()
            idInput = self.cmu_id_edit.text()
            dubiInput = self.cmu_dbi_edit.text()
            ackInput = self.cmu_ack_edit.text()
            text = self.cmu_text_edit.toPlainText()
        else:
            return FAIL

        if modeInput != "2":
            QMessageBox.critical(None, "Error", "Only mode a is supported temporarily!", QMessageBox.Yes)
            return FAIL
        if not arn_pattern.match(arnInput):
            QMessageBox.critical(None, "Error", "Illegal Arn character!", QMessageBox.Yes)
            return FAIL

        if len(ackInput) != 1 or not ack_pattern.match(ackInput) :
            if ackInput != "":
                QMessageBox.critical(None, "Error", "Illegal Ack character!", QMessageBox.Yes)
                return FAIL
            else:
                ackInput = "%c" % (0x15)

        if len(labelInput) > 2:
            QMessageBox.critical(None, "Error", "Length of label more than 2!", QMessageBox.Yes)
            return FAIL

        #Generate context based on context Identifier
        if mode == Message.UPLINK:
            print(dubiInput)
            if not ubi_pattern.match(dubiInput) or len(dubiInput) > 1:
                if ackInput != "":
                    QMessageBox.critical(None, "Error", "Illegal UBI character!", QMessageBox.Yes)
                    return FAIL
                else:
                    dubiInput = 0x15
            formaltext = text

            return (modeInput, labelInput, arnInput, dubiInput, ackInput, formaltext)

        else:
            if not dbi_pattern.match(dubiInput) or len(dubiInput) > 1:
                QMessageBox.critical(None, "Error", "Illegal DBI character!", QMessageBox.Yes)
                return FAIL

            if len(idInput) != 6:
                QMessageBox.critical(None, "Error", "Length of flight id not equals to 6!", QMessageBox.Yes)
                return FAIL

            msgNo = "M01A"
            FlightID = idInput
            formaltext = msgNo + FlightID + text

            return (modeInput, labelInput, arnInput, dubiInput, ackInput, msgNo, FlightID, formaltext)

