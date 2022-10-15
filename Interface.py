from operator import mod
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import time
import os
import re
import json
from datetime import datetime


import HackRFThread
import Receiver
import Entity
import Message
import Util
import Ui_Cert
from Crypto import Security

ALL = 0
RECV = 1
TRAN = 2

SUCCESS = 0
FAIL = 1



class Interface(QtCore.QObject):
    addMessageSignal = QtCore.pyqtSignal(object, int)

    def __init__(self, mainWindow) -> None:
        super(Interface, self).__init__()
        self.mainWindow = mainWindow
        self.dsp = Entity.DSP()
        self.cmu = Entity.CMU()
        self.initComponents()
        self.initEvent()
        self.getDevices()
        self.initDevices(ALL)

        self.dsp.putMsgSignal(self.addMessageSignal)
        self.cmu.putMsgSignal(self.addMessageSignal)

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


        self.dsp_passwd_edit = self.mainWindow.findChild(QTextEdit, "dsp_passwd_edit")
        self.dsp_cert_btn = self.mainWindow.findChild(QPushButton, "dsp_cert_btn")
        self.cmu_passwd_edit = self.mainWindow.findChild(QTextEdit, "cmu_passwd_edit")
        self.cmu_cert_btn = self.mainWindow.findChild(QPushButton, "cmu_cert_btn")
        self.symmetrickey_edit = self.mainWindow.findChild(QLineEdit, "symmetrickey_edit")

        self.security_mode_combo = self.mainWindow.findChild(QComboBox, "security_mode_combo")

        self.msg_table = self.mainWindow.findChild(QTableWidget, "msg_table")

        self.confirm_symkey_btn = self.mainWindow.findChild(QPushButton, "confirm_symkey_btn")
        self.initMsgTable()


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
        self.cmu_start_btn.clicked.connect(lambda: self.startWorking(Entity.MODE_CMU))
        self.cmu_stop_btn.clicked.connect(lambda:self.stopWorking(Entity.MODE_CMU))
        self.dsp_send_btn.clicked.connect(lambda: self.send(Entity.MODE_DSP))
        self.cmu_send_btn.clicked.connect(lambda: self.send(Entity.MODE_CMU))

        self.dsp_cert_btn.clicked.connect(lambda: self.getCert(Entity.MODE_DSP))
        self.cmu_cert_btn.clicked.connect(lambda: self.getCert(Entity.MODE_CMU))
        self.confirm_symkey_btn.clicked.connect(lambda: self.setSymmetricKey())

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

    def send(self, mode):

        if mode == Entity.MODE_DSP:
            paras = self.getParas(Message.UPLINK)
            if paras == FAIL:
                return

            self.dsp.putMessageParas(mode, paras)

        if mode == Entity.MODE_CMU:
            paras = self.getParas(Message.DOWNLINK)
            if paras == FAIL:
                return

            self.cmu.putMessageParas(mode, paras)


    def addMessage(self, msg, mode):
        self.addMsgTableRow(msg.getMsgTuple())

        if mode == Entity.MODE_DSP:
            self.dsp_msg_list.addItem(msg.String())
        elif mode == Entity.MODE_CMU:
            self.cmu_msg_list.addItem(msg.String())
        else:
            pass

    def closeWindow(self):
        self.dsp.forceStopDevices()
        self.cmu.forceStopDevices()

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

            return (modeInput, labelInput, arnInput, dubiInput, ackInput, None, None ,formaltext)

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

    def getCert(self, mode):
        dialog = QDialog()
        window = Ui_Cert.Ui_Form()
        window.setupUi(dialog)
        if mode == Entity.MODE_DSP:
            CertInterface(dialog, self.dsp)
        elif mode == Entity.MODE_CMU:
            CertInterface(dialog, self.cmu)
        dialog.show()
        dialog.exec_()

    def getSecurityMode(self):
        index = self.security_mode_combo.currentIndex()
        if index == 0:
            return Message.Message.NORMAL
        elif index == 1:
            return Message.Message.CUSTOM

    def initMsgTable(self):
        self.msg_table.setColumnCount(11)
        self.msg_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.msg_table.setHorizontalHeaderLabels(["Time", "Orient", "Security Level", "Mode", "Label", "Arn", "UBI/DBI", "ACK", "Serial Number", "FlightID", "Text"])

    def addMsgTableRow(self, paras):
        rows_c = self.msg_table.rowCount()
        rows_c += 1
        self.msg_table.setRowCount(rows_c)
        #print(self.msg_table.columnCount())

        for i in range(self.msg_table.columnCount()):
            print(paras[i])
            newItem = QTableWidgetItem(paras[i])
            self.msg_table.setItem(rows_c - 1,i,newItem)

    def setSymmetricKey(self):
        key = self.symmetrickey_edit.text()
        iv = Security.getIV()
        self.dsp.setSymmetricKeyandIV(key, iv)
        self.cmu.setSymmetricKeyandIV(key, iv)

        self.dsp.setSecurityLevel(self.getSecurityMode())
        self.cmu.setSecurityLevel(self.getSecurityMode())
        print(key)


class CertInterface:
    def __init__(self, dialog, entity) -> None:
        self.dialog = dialog
        self.entity = entity
        self.initComponent()
        self.initEvent()

    def initComponent(self):
        self.country_edit = self.dialog.findChild(QLineEdit, "country_edit")
        self.locality_edit = self.dialog.findChild(QLineEdit, "locality_edit")
        self.province_edit = self.dialog.findChild(QLineEdit, "province_edit")
        self.org_edit = self.dialog.findChild(QLineEdit, "org_edit")
        self.orgunit_edit = self.dialog.findChild(QLineEdit, "orgunit_edit")
        self.comname_edit = self.dialog.findChild(QLineEdit, "comname_edit")
        self.confirm_btn = self.dialog.findChild(QPushButton, "confirm_btn")

    def initEvent(self):
        self.confirm_btn.clicked.connect(lambda:self.setCert())

    def getParas(self):
        country = self.country_edit.text()
        locality = self.locality_edit.text()
        province = self.province_edit.text()
        organization = self.org_edit.text()
        org_unit = self.orgunit_edit.text()
        common_name = self.comname_edit.text()
        return (country, locality, province, organization, org_unit, common_name)

    def setCert(self):
        self.entity.setCert(self.getParas())
        self.dialog.close()

