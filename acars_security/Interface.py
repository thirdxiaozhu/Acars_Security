import os
import re
import time

import Attack
import Digalogs
import Entity
import HackRFThread
import Message
import OpenSSL
import Receiver
import Ui.SubUnit
import Ui.Ui_Attack
import Ui.Ui_Cert
import Ui.Ui_Cert_Detail
import Ui.Ui_MsgCryDetail
import Ui.Ui_Stable
from Crypto_Util import Security
from dateutil import parser
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

ALL = 0
RECV = 1
TRAN = 2

SUCCESS = 0
FAIL = 1



class Interface(QtCore.QObject):
    add_block_signal = QtCore.pyqtSignal(object, int)
    add_complete_msg_signal = QtCore.pyqtSignal(object, int)
    notification_signal = QtCore.pyqtSignal(str, str)
    c2_done_verify_signal = QtCore.pyqtSignal()
    c2_sym_key_gen_signal = QtCore.pyqtSignal(str)
    
   

    def __init__(self, mainWindow) -> None:
        super(Interface, self).__init__()
        self.sec_mod = None
        self.mainWindow = mainWindow
        self.dsp = Entity.DSP()
        self.cmu = Entity.CMU()
        self.ca = Entity.CA()
        self.initComponents()
        self.initEvent()
        self.getDevices()
        self.reInitDeviceCombos(ALL)

        self.dsp.putSignals(self.add_block_signal, self.add_complete_msg_signal, self.notification_signal, self.c2_done_verify_signal, self.c2_sym_key_gen_signal)
        self.cmu.putSignals(self.add_block_signal, self.add_complete_msg_signal, self.notification_signal, self.c2_done_verify_signal, self.c2_sym_key_gen_signal)
        self.dsp.setCAEntity(self.ca)
        self.cmu.setCAEntity(self.ca)

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

        #self.dsp_mode_edit = self.mainWindow.findChild(QLineEdit, "dsp_mode_edit")
        self.dsp_label_edit = self.mainWindow.findChild(QLineEdit, "dsp_label_edit")
        self.dsp_arn_edit = self.mainWindow.findChild(QLineEdit, "dsp_arn_edit")
        #self.dsp_ubi_edit = self.mainWindow.findChild(QLineEdit, "dsp_ubi_edit")
        #self.dsp_ack_edit = self.mainWindow.findChild(QLineEdit, "dsp_ack_edit")
        self.dsp_text_edit = self.mainWindow.findChild(QTextEdit, "dsp_text_edit")
        self.dsp_send_btn = self.mainWindow.findChild(QPushButton, "dsp_send_btn")
        self.dsp_test_stable_btn = self.mainWindow.findChild(QPushButton, "dsp_test_stable_btn")

        #self.cmu_mode_edit = self.mainWindow.findChild(QLineEdit, "cmu_mode_edit")
        self.cmu_label_edit = self.mainWindow.findChild(QLineEdit, "cmu_label_edit")
        self.cmu_arn_edit = self.mainWindow.findChild(QLineEdit, "cmu_arn_edit")
        #self.cmu_dbi_edit = self.mainWindow.findChild(QLineEdit, "cmu_dbi_edit")
        #self.cmu_ack_edit = self.mainWindow.findChild(QLineEdit, "cmu_ack_edit")
        self.cmu_id_edit = self.mainWindow.findChild(QLineEdit, "cmu_id_edit")
        self.cmu_text_edit = self.mainWindow.findChild(QTextEdit, "cmu_text_edit")
        self.cmu_send_btn = self.mainWindow.findChild(QPushButton, "cmu_send_btn")
        self.cmu_test_stable_btn = self.mainWindow.findChild(QPushButton, "cmu_test_stable_btn")


        self.dsp_passwd_edit = self.mainWindow.findChild(QLineEdit, "dsp_passwd_edit")
        self.dsp_cert_btn = self.mainWindow.findChild(QPushButton, "dsp_cert_btn")
        self.cmu_passwd_edit = self.mainWindow.findChild(QLineEdit, "cmu_passwd_edit")
        self.cmu_cert_btn = self.mainWindow.findChild(QPushButton, "cmu_cert_btn")
        self.ca_passwd_edit = self.mainWindow.findChild(QLineEdit, "ca_passwd_edit")
        self.ca_cert_btn = self.mainWindow.findChild(QPushButton, "ca_cert_btn")
        self.symmetrickey_edit = self.mainWindow.findChild(QLineEdit, "symmetrickey_edit")

        self.security_mode_combo = self.mainWindow.findChild(QComboBox, "security_mode_combo")

        self.msg_table = self.mainWindow.findChild(QTableWidget, "msg_table")
        self.clear_all_table_item_btn = self.mainWindow.findChild(QPushButton, "clear_all_table_item_btn")
        self.table_mode_filter_combo = self.mainWindow.findChild(QComboBox, "table_mode_filter_combo")

        self.confirm_symkey_btn = self.mainWindow.findChild(QPushButton, "confirm_symkey_btn")
        self.dsp_certs_list = self.mainWindow.findChild(QListWidget, "dsp_certs_list")
        self.cmu_certs_list = self.mainWindow.findChild(QListWidget, "cmu_certs_list")
        self.ca_certs_list = self.mainWindow.findChild(QListWidget, "ca_certs_list")


        self.cmu_confirm_btn = self.mainWindow.findChild(QPushButton, "cmu_confirm_btn")

        self.sec_mod_label = self.mainWindow.findChild(QLabel, "sec_mod_label")
        self.cus_handshake_btn = self.mainWindow.findChild(QPushButton, "cus_handshake_btn")
        self.cus_handshake_btn.setEnabled(False)
        self.cus2_sym_edit = self.mainWindow.findChild(QLineEdit, "cus2_sym_edit")

        self.action_save = self.mainWindow.findChild(QAction, "action_save")
        self.action_load = self.mainWindow.findChild(QAction, "action_load")


        self.initMsgTable()
        self.initCertList()
        self.initMsgList()



    def initEvent(self):
        self.dsp_receiver_confirm.clicked.connect(lambda: self.confirmDevice(
            RECV, self.dsp_receiver_combo, self.dsp_rtl_label, self.dsp, self.dsp_receiver_confirm))
        self.dsp_transmitter_confirm.clicked.connect(lambda: self.confirmDevice(
            TRAN, self.dsp_transmitter_combo, self.dsp_hackrf_label, self.dsp, self.dsp_transmitter_confirm))
        self.cmu_receiver_confirm.clicked.connect(lambda: self.confirmDevice(
            RECV, self.cmu_receiver_combo, self.cmu_rtl_label, self.cmu, self.cmu_receiver_confirm))
        self.cmu_transmitter_confirm.clicked.connect(lambda: self.confirmDevice(
            TRAN, self.cmu_transmitter_combo, self.cmu_hackrf_label, self.cmu, self.cmu_transmitter_confirm))
        self.dsp_start_btn.clicked.connect(lambda: self.startWorking(Entity.MODE_DSP))
        self.dsp_stop_btn.clicked.connect(lambda:self.stopWorking(Entity.MODE_DSP))
        self.cmu_start_btn.clicked.connect(lambda: self.startWorking(Entity.MODE_CMU))
        self.cmu_stop_btn.clicked.connect(lambda:self.stopWorking(Entity.MODE_CMU))
        self.dsp_send_btn.clicked.connect(lambda: self.send(self.dsp))
        self.cmu_send_btn.clicked.connect(lambda: self.send(self.cmu))

        self.dsp_cert_btn.clicked.connect(lambda: self.getCert(Entity.MODE_DSP))
        self.cmu_cert_btn.clicked.connect(lambda: self.getCert(Entity.MODE_CMU))
        self.ca_cert_btn.clicked.connect(lambda: self.getCert(Entity.MODE_CA))
        self.confirm_symkey_btn.clicked.connect(lambda: self.setSymmetricKey())

        self.dsp_test_stable_btn.clicked.connect(lambda: self.testStable(Entity.MODE_DSP))
        self.cmu_test_stable_btn.clicked.connect(lambda: self.testStable(Entity.MODE_CMU))

        self.add_block_signal.connect(self.addBlock)
        self.add_complete_msg_signal.connect(self.addCompleteMsg)
        self.notification_signal.connect(self.showNotification)
        self.c2_done_verify_signal.connect(self.c2DoneVerify)
        self.c2_sym_key_gen_signal.connect(self.c2PutSymKey)
        self.dsp_certs_list.itemDoubleClicked.connect(lambda: self.showCertDetail(self.dsp_certs_list))
        self.cmu_certs_list.itemDoubleClicked.connect(lambda: self.showCertDetail(self.cmu_certs_list))
        self.ca_certs_list.itemDoubleClicked.connect(lambda: self.showCertDetail(self.ca_certs_list))

        self.dsp_msg_list.itemDoubleClicked.connect(
            lambda: self.showMsgDetail(self.dsp_msg_list))

        self.cmu_msg_list.itemDoubleClicked.connect(
            lambda: self.showMsgDetail(self.cmu_msg_list))

        self.cmu_confirm_btn.clicked.connect(lambda:self.confirmAircraftInfos())

        self.cus_handshake_btn.clicked.connect(lambda: self.cus2Handshake())

        self.clear_all_table_item_btn.clicked.connect(lambda: self.clearAllItems())

        self.action_save.triggered.connect(lambda:self.save())
        self.action_load.triggered.connect(lambda:self.load())


    #保存配置文件
    def save(self):
        pass

    #读取配置文件
    def load(self):
        pass

    #获取当前可被调用的rtl/hackrf设备
    def getDevices(self):
        self.hackrfs = HackRFThread.getInfo()
        self.rtls = Receiver.getRtls()

    #重新读取并填充设备下拉框
    def reInitDeviceCombos(self, sign):
        if sign == RECV:
            self.reInitRtlCombo(self.dsp_receiver_combo)
            self.reInitRtlCombo(self.cmu_receiver_combo)
        elif sign == TRAN:
            self.reInitHackRFCombo(self.dsp_transmitter_combo)
            self.reInitHackRFCombo(self.cmu_transmitter_combo)
        else:
            self.reInitRtlCombo(self.dsp_receiver_combo)
            self.reInitRtlCombo(self.cmu_receiver_combo)
            self.reInitHackRFCombo(self.dsp_transmitter_combo)
            self.reInitHackRFCombo(self.cmu_transmitter_combo)

    def reInitHackRFCombo(self, combo):
        for i in range(combo.count()):
            combo.removeItem(0)
        for i in self.hackrfs:
            combo.addItem(i)

    #无用
    def reloadHackRFs(self):
        for i in range(self.device_combo.count()):
            self.device_combo.removeItem(0)

        self.getDevices()

    def reInitRtlCombo(self, combo):
        for i in range(combo.count()):
            combo.removeItem(0)
        for i in self.rtls:
            combo.addItem(i)

    #确认选定设备
    #@param sign: 标识
    #@param combo: 下拉框组件
    #@param label: 标签组件
    #@param entity: 业务实体
    #@param button: 确认按钮组件
    def confirmDevice(self, sign, combo, label, entity, button):
        serial = combo.currentText()
        if sign == RECV:
            entity.setRtl(serial)
            self.rtls.remove(serial)
            self.reInitDeviceCombos(RECV)
        elif sign == TRAN:
            entity.setHackRFSerial(serial)
            self.hackrfs.remove(serial)
            self.reInitDeviceCombos(TRAN)
        else:
            return

        button.setEnabled(False)
        combo.setEnabled(False)
        label.setText(serial)


    #启动设备
    def startWorking(self, mode):
        if mode == Entity.MODE_DSP:
            self.dsp.setSelfKey(self.dsp_passwd_edit.text())
            self.dsp.changeStatu()
            self.dsp.setFrequency(self.dsp_frequency_edit.text())
            self.dsp.setHostAndPort(self.dsp_addr_edit.text())
            self.dsp.initRtl()
            self.dsp.initHackRF()
            self.dsp_start_btn.setEnabled(False)
            #self.dsp.setHackRF(seria)

        elif mode == Entity.MODE_CMU:
            self.cmu.setSelfKey(self.cmu_passwd_edit.text())
            self.cmu.changeStatu()
            self.cmu.setFrequency(self.cmu_frequency_edit.text())
            self.cmu.setHostAndPort(self.cmu_addr_edit.text())
            self.cmu.initRtl()
            self.cmu.initHackRF()
            self.cmu_start_btn.setEnabled(False)
            #self.cmu.setHackRF()

    #停止设备
    def stopWorking(self, mode):
        if mode == Entity.MODE_DSP:
            self.dsp.forceStopDevices()
        elif mode == Entity.MODE_CMU:
            self.cmu.forceStopDevices()

    def send(self, entity):
        paras = self.getParas(entity.getModeNum())
        if paras == FAIL:
            return
        entity.putMessageParas([paras])

    def addBlock(self, msg, mode):
        self.addMsgTableRow(msg.getMsgTuple())


    def addCompleteMsg(self, msg, mode):
        item = Ui.SubUnit.MessageListItem(msg)
        item.setSizeHint(QSize(200, 50))  
        widget = item.getItemWidget()  


        if mode == Entity.MODE_DSP:
            self.dsp_msg_list.addItem(item)  # 添加item
            self.dsp_msg_list.setItemWidget(
                item, widget) 
        elif mode == Entity.MODE_CMU:
            self.cmu_msg_list.addItem(item) 
            self.cmu_msg_list.setItemWidget(
                item, widget)  
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

        if mode == Message.MODE_DSP:
            modeInput = "2"
            arnInput = self.dsp_arn_edit.text()
            labelInput = self.dsp_label_edit.text()
            dubiInput = "A"
            ackInput = ""
            text = self.dsp_text_edit.toPlainText()
        elif mode == Message.MODE_CMU:
            modeInput = "2"
            arnInput = self.cmu.getArn()
            labelInput = self.cmu_label_edit.text()
            idInput = self.cmu.getId()
            dubiInput = "3"
            ackInput = ""
            text = self.cmu_text_edit.toPlainText()
        else:
            return FAIL

        if modeInput != "2":
            QMessageBox.critical(None, "Error", "Only mode a is supported temporarily!", QMessageBox.Yes)
            return FAIL
        #if not arn_pattern.match(arnInput):
        #    QMessageBox.critical(None, "Error", "Illegal Arn character!", QMessageBox.Yes)
        #    return FAIL

        if len(ackInput) != 1 or not ack_pattern.match(ackInput) :
            if ackInput != "":
                QMessageBox.critical(None, "Error", "Illegal Ack character!", QMessageBox.Yes)
                return FAIL
            #else:
            #    ackInput = "%c" % (0x15)

        if self.sec_mod == Message.Message.NORMAL:
            if len(labelInput) > 2:
                QMessageBox.critical(None, "Error", "Length of label more than 2!", QMessageBox.Yes)
                return FAIL
        else:
            labelInput = "P8"

        #Generate context based on context Identifier
        if mode == Message.MODE_DSP:
            if not ubi_pattern.match(dubiInput) or len(dubiInput) > 1:
                if ackInput != "":
                    QMessageBox.critical(None, "Error", "Illegal UBI character!", QMessageBox.Yes)
                    return FAIL
                else:
                    dubiInput = 0x15
            formaltext = text

            return (modeInput, labelInput, arnInput, dubiInput, ackInput, None, formaltext, None)

        else:
            if not dbi_pattern.match(dubiInput) or len(dubiInput) > 1:
                QMessageBox.critical(None, "Error", "Illegal DBI character!", QMessageBox.Yes)
                return FAIL

            if len(idInput) != 6:
                QMessageBox.critical(None, "Error", "Length of flight id not equals to 6!", QMessageBox.Yes)
                return FAIL

            FlightID = idInput
            formaltext = text

            return (modeInput, labelInput, arnInput, dubiInput, ackInput, FlightID, formaltext, "")

    def getCert(self, mode):
        dialog = QDialog()
        window = Ui.Ui_Cert.Ui_Form()
        window.setupUi(dialog)
        if mode == Entity.MODE_DSP:
            self.dsp.setSelfKey(self.dsp_passwd_edit.text())
            CertInterface(dialog, self.dsp)
        elif mode == Entity.MODE_CMU:
            self.cmu.setSelfKey(self.cmu_passwd_edit.text())
            CertInterface(dialog, self.cmu)
        elif mode == Entity.MODE_CA:
            self.ca.setSelfKey(self.ca_passwd_edit.text())
            CertInterface(dialog, self.ca)
        dialog.show()
        dialog.exec_()

    def setSecurityMode(self):
        index = self.security_mode_combo.currentIndex()
        mod_str = ""
        if index == 0:
            mod_str = "Non-Processing"
            self.sec_mod = Message.Message.NORMAL
        elif index == 1:
            mod_str = "Successive Authentication"
            self.sec_mod = Message.Message.CUSTOM
        elif index == 2:
            mod_str = "Trans-Layer Processing"
            self.sec_mod = Message.Message.CUSTOM2
        
        self.sec_mod_label.setText(mod_str)
        QMessageBox.information(self.mainWindow, "Mode Changed", "The Security Mode has changed to %s" % mod_str, QMessageBox.Yes)

    def initMsgList(self):
        self.dsp_msg_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.dsp_msg_list.customContextMenuRequested.connect(
            self.dspListRightMenu)
        self.cmu_msg_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.cmu_msg_list.customContextMenuRequested.connect(
            self.cmuListRightMenu)

    def initMsgTable(self):
        self.msg_table.setColumnCount(11)
        self.msg_table.setAlternatingRowColors(True)
        self.msg_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.msg_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.msg_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.msg_table.setHorizontalHeaderLabels(["Time", "Orient", "Security Level", "Mode", "Label", "Arn", "UBI/DBI", "ACK", "FlightID", "Text", "Serial"])
        self.msg_table.doubleClicked.connect(self.double_click_table_view_item)

        self.msg_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.msg_table.customContextMenuRequested.connect(
            self.msgTableRightMenu)
        
        self.table_mode_filter_combo.currentIndexChanged.connect(self.changeTableMode)

    def addMsgTableRow(self, paras):
        rows_c = self.msg_table.rowCount()
        rows_c += 1
        self.msg_table.setRowCount(rows_c)

        for i in range(self.msg_table.columnCount()):
            newItem = QTableWidgetItem(paras[i])
            self.msg_table.setItem(rows_c - 1,i,newItem)

    def changeTableMode(self):
        index = self.table_mode_filter_combo.currentIndex()
        match_mode = None
        if index == 0:
            match_mode = ""
        elif index == 1:
            match_mode = "U"
        elif index == 2:
            match_mode = "D"

        for i in range(self.msg_table.rowCount()):
            is_match = False
            item = self.msg_table.item(i, 1)
            if item is not None and item.text() == match_mode:
                is_match = True
                break
            self.msg_table.setRowHidden(i, not is_match)


    def double_click_table_view_item(self,qModelIndex):
        print(qModelIndex.row())

    def initCertList(self):
        dsp_cert_path = "/home/jiaxv/inoproject/Acars_Security/users/dsp"
        cmu_cert_path = "/home/jiaxv/inoproject/Acars_Security/users/cmu"
        ca_cert_path = "/home/jiaxv/inoproject/Acars_Security/users/ca"
        self.scanCerts(dsp_cert_path, self.dsp_certs_list)
        self.scanCerts(cmu_cert_path, self.cmu_certs_list)
        self.scanCerts(ca_cert_path, self.ca_certs_list)

    def showCertDetail(self, component):
        item = component.selectedItems()[0]
        dialog = QDialog()
        window = Ui.Ui_Cert_Detail.Ui_Form()
        window.setupUi(dialog)
        CertDetail(dialog, item.text())
        dialog.show()
        dialog.exec_()

    def scanCerts(self, path, component):
        for item in os.scandir(path):
            if item.is_file() and item.path[-8:-4]=="cert":
                component.addItem(item.path)


    def setSymmetricKey(self):
        key = self.symmetrickey_edit.text()
        iv = Security.getIV()
        self.dsp.setSymmetricKeyandIV(key, iv)
        self.cmu.setSymmetricKeyandIV(key, iv)

        self.setSecurityMode()

        self.dsp.setSecurityLevel(self.sec_mod)
        self.cmu.setSecurityLevel(self.sec_mod)

        if self.sec_mod == Message.Message.CUSTOM2:
            self.dsp_send_btn.setEnabled(False)
            self.cmu_send_btn.setEnabled(False)
            self.cus_handshake_btn.setEnabled(True)
        else:
            self.dsp_send_btn.setEnabled(True)
            self.cmu_send_btn.setEnabled(True)
            self.cus_handshake_btn.setEnabled(False)

    def testStable(self, mode):
        dialog = Digalogs.TestTransDialog()
        window = Ui.Ui_Stable.Ui_Form()
        window.setupUi(dialog)
        if mode == Entity.MODE_DSP:
            TestStable(dialog, self.dsp)
        else:
            TestStable(dialog, self.cmu)
        dialog.show()
        dialog.exec_()

    def showMsgDetail(self, list):
        item = list.selectedItems()[0]
        dialog = QDialog()
        window = Ui.Ui_MsgCryDetail.Ui_Form()
        window.setupUi(dialog)
        MsgDetail(dialog, item)
        dialog.show()
        dialog.exec_()

    def replayBlockAttack(self):
        paras = ()
        for i in self.msg_table.selectedItems():
            paras = (paras + (i.text(), ))
        paras = paras[3:]

        if re.compile(
                r"[A-Za-z]").match(paras[3]) :
            self.dsp.putMessageParasExec([paras], True)
        else:
            self.cmu.putMessageParasExec([paras], True)

    def simulateAttack(self, mode):
        if mode == Message.MODE_DSP:
            list_widget = self.dsp_msg_list
            entity = self.cmu
        else:
            list_widget = self.cmu_msg_list
            entity = self.dsp


        items = list_widget.selectedItems()
        if len(items) > 0:
            item = items[0]
            dialog = QDialog()
            window = Ui.Ui_Attack.Ui_Form()
            window.setupUi(dialog)
            Attack.Attack(dialog, item, entity)
            dialog.show()
            dialog.exec_()
        else:
            print("No Choosed Item")

    def confirmAircraftInfos(self):
        #arn = ("%7s" % self.cmu_arn_edit.text()).replace(" ", ".")
        arn = self.cmu_arn_edit.text()
        id = self.cmu_id_edit.text()
        self.cmu.setArnandId(arn, id)
        self.cmu_confirm_btn.setEnabled(False)


    def cus2Handshake(self):
        self.dsp.custom2_statu = Entity.C2_WAIT_HANDSHAKE
        self.cmu.custom2_statu = Entity.C2_WAIT_HANDSHAKE
        self.cmu.putMessageParas([("2", "P8", self.cmu.getArn(), "2", "", self.cmu.getId(), "Hello", "")])

    def showNotification(self, title, str):
        QMessageBox.critical(None, title, str, QMessageBox.Yes)

    def c2DoneVerify(self):
        self.dsp_send_btn.setEnabled(True)
        self.cmu_send_btn.setEnabled(True)

    def c2PutSymKey(self, str):
        self.cus2_sym_edit.setText(str)

    def dspListRightMenu(self, pos):
        menu = QMenu()
        attackAction = QAction(u'Simulate Attack', self)
        menu.addAction(attackAction)
        #sendMessageAction.triggered.connect(self.friendDoubleClicked)
        attackAction.triggered.connect(lambda:self.simulateAttack(Message.MODE_DSP))

        item = self.dsp_msg_list.selectedItems()[0]
        menu.exec_(self.dsp_msg_list.mapToGlobal(pos))

    def cmuListRightMenu(self, pos):
        menu = QMenu()
        attackAction = QAction(u'Simulate Attack', self)
        menu.addAction(attackAction)
        attackAction.triggered.connect(lambda:self.simulateAttack(Message.MODE_CMU))

        item = self.cmu_msg_list.selectedItems()[0]
        menu.exec_(self.cmu_msg_list.mapToGlobal(pos))

    def msgTableRightMenu(self, pos):
        #menu = QMenu()
        #sendMessageAction = QAction(u'发送信息', self)
        #deleteGroupAction = QAction(u'退出此群', self)
        #dismissGroupAction = QAction(u'解散此群', self)
        #sendMessageAction.triggered.connect(self.friendDoubleClicked)
        #deleteGroupAction.triggered.connect(self.deleteGroup)
        #dismissGroupAction.triggered.connect(self.dismissGroup)

        #item = self.groupListWidget.selectedItems()[0]
        #menu.addAction(sendMessageAction)
        #if item.group_master == self.ownerInfo.get("account"):
        #    menu.addAction(dismissGroupAction)
        #else:
        #    menu.addAction(deleteGroupAction)
        row_num = -1
        for i in self.msg_table.selectionModel().selection().indexes():
            row_num = i.row()

        if row_num < 500: # 表格生效的行数，501行点击右键，不会弹出菜单
            menu = QMenu() #实例化菜单
            attack = menu.addAction(u"Attack")
            #item2 = menu.addAction(u"拷贝")
            #item3 = menu.addAction(u"粘贴")

            attack.triggered.connect(self.replayBlockAttack)

            action = menu.exec_(self.msg_table.mapToGlobal(pos))
        else:
            return
        
    def clearAllItems(self):
        self.msg_table.setRowCount(0)
        self.dsp_msg_list.clear()
        self.cmu_msg_list.clear()
        self.dsp.clearItems()
        self.cmu.clearItems()




class TestStable(QtCore.QObject):
    addMessageSignal = QtCore.pyqtSignal(object, int)
    def __init__(self, dialog, entity) -> None:
        super(TestStable, self).__init__()
        self.dialog = dialog
        self.entity = entity
        self.dialog.entity = entity
        self.repeat_combo = self.dialog.findChild(QComboBox, "repeat_times_combo")
        self.log_edit = self.dialog.findChild(QTextEdit, "log_edit")
        self.start_btn = self.dialog.findChild(QPushButton, "start_btn")
        self.stop_btn = self.dialog.findChild(QPushButton, "stop_btn")
        self.entity.putTestingSignal(self.addMessageSignal)
        self.recv_times = 0
        self.initEvent()

    def initEvent(self):
        self.start_btn.clicked.connect(lambda: self.startTesting())
        self.addMessageSignal.connect(self.receiveMsg)

    def receiveMsg(self, ret, mode):
        self.recv_times += 1
        self.printLog("Receive", self.recv_times)
    

    def startTesting(self):
        self.entity.setFrequency("131.45")
        self.entity.setHostAndPort("127.0.0.1:6666")
        self.entity.startRtl()
        self.entity.initHackRF()
        test_data = ("2", "QQ", "CA1234", "A", "\x15", None, "Testing...")
        para_list = []
        for i in range(3):
            para_list.append(test_data)
        self.entity.putMessageParas(para_list)
        self.printLog("Transmit", 3)


    def printLog(self, patt, time):
        text = """
        <div>
            <div> %s %d time(s) </div>
        </div>
        """
        self.log_edit.append(text % (patt, time))


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


class CertDetail:
    def __init__(self, dialog, path) -> None:
        self.dialog = dialog
        self.path = path
        self.initComponent()
        self.initRaw()
        self.initDetail()

    def initComponent(self):
        self.cert_raw = self.dialog.findChild(QTextEdit, "cert_raw")
        self.cert_detail = self.dialog.findChild(QTextEdit, "cert_detail")

    def initRaw(self):
        raw = '<div>%s</div>'
        f = open(self.path, "r")
        lines = []
        for line in f.readlines():                          #依次读取每行  
            lines.append(line.strip())                             #去掉每行头尾空白  
            self.cert_raw.append(raw % line.strip())
        f.close()

    def initDetail(self):
        cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, open(self.path).read())
        certIssue = cert.get_issuer()
        detail = """
        <div>
            <div>   <font color="red">Version:          </font> %s </div>
            <div>   <font color="red">Serial Number:    </font> %s </div>
            <div>   <font color="red">Algorith:         </font> %s </div>
            <div>   <font color="red">Common Name:      </font> %s </div>
            <div>   <font color="red">Not Before:       </font> %s </div>
            <div>   <font color="red">Not After:        </font> %s </div>
            <div>   <font color="red">Has Expired:      </font> %s </div>
            <div>   <font color="red">Public Key Length:</font> %s </div>
            <div>   <font color="red">Public Key:<br>   </font>      %s </div>
            <div>
                ----------------------------
            </div>
        </div>
        """

        component = '<div><font color = "red">%s: </font> %s</div>'

        not_before = parser.parse(cert.get_notBefore().decode("UTF-8"))
        not_after = parser.parse(cert.get_notAfter().decode("UTF-8"))

        self.cert_detail.append(detail % (
            cert.get_version() + 1,
            hex(cert.get_serial_number()),
            cert.get_signature_algorithm().decode("UTF-8"),
            certIssue.commonName,
            not_before.strftime('%Y-%m-%d %H:%M:%S'),
            not_after.strftime('%Y-%m-%d %H:%M:%S'),
            cert.has_expired(),
            cert.get_pubkey().bits(),
            OpenSSL.crypto.dump_publickey(OpenSSL.crypto.FILETYPE_PEM, cert.get_pubkey()).decode("utf-8"),
        ))

        for item in certIssue.get_components():
            self.cert_detail.append(component % (item[0].decode("utf-8"), item[1].decode("utf-8")))


class MsgDetail:
    def __init__(self, dialog, item) -> None:
        self.dialog = dialog
        self.msg = item.getMsgUnit()
        self.initComponent()
        
    def initComponent(self):
        self.origninal_data_edit = self.dialog.findChild(QTextEdit, "origninal_data_edit")
        self.ciphertext_edit = self.dialog.findChild(QTextEdit, "ciphertext_edit")
        self.plaintext_edit = self.dialog.findChild(QTextEdit, "plaintext_edit")
        self.signature_edit = self.dialog.findChild(QTextEdit, "signature_edit")
        self.cipher_len_line = self.dialog.findChild(QLineEdit, "cipher_len_line")
        self.sign_len_edit = self.dialog.findChild(QLineEdit, "sign_len_edit")
        self.arinc620_edit = self.dialog.findChild(QTextEdit, "arinc620_edit")

        detail = """
        <div>
            %s
        </div>
        """

        self.origninal_data_edit.append(detail % (self.msg.getOriginText()))
        self.plaintext_edit.append(detail % (self.msg.getProcessedText()))
        self.ciphertext_edit.append(detail % (self.msg.getCipherText()))
        self.signature_edit.append(detail % (self.msg.getSignText()))
        self.cipher_len_line.setText(str(self.msg.getCipherLen()))
        self.sign_len_edit.setText(str(self.msg.getSignLen()))
        self.arinc620_edit.setText(detail % self.msg.getArinc620())



