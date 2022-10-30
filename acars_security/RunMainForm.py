import sys
import os
from time import sleep


import Ui_MainForm
import Modulation
from PyQt5.QtWidgets import *
from PyQt5 import QtCore

import multiprocessing
import Util
import Protocol
from Util import *
from HackRFThread import *
from Receiver import *


def main():
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    ui = Ui_MainForm.Ui_MainWindow()
    ui.setupUi(mainWindow)
    event = Event(mainWindow)
    mainWindow.show()
    app.exec_()
    event.closeWindow()


class Event(QtCore.QObject):
    UPLINK_MODE = 0
    DOWNLINK_MODE = 1

    SUCCESS = 10
    FAIL = 11

    processSignal = QtCore.pyqtSignal(int)
    statuChangeSignal = QtCore.pyqtSignal(str)
    errorSignal = QtCore.pyqtSignal(str)


    def __init__(self, mainWindow):
        super(Event, self).__init__()
        self.mainWindow = mainWindow
        self.transMode = self.UPLINK_MODE
        self.initComponents()
        self.initEvent()
        self.getDevices()
        self.receiver = Receiver(self.mainWindow)
        self.qtSignals = (self.processSignal, self.statuChangeSignal)

    def initComponents(self):
        self.sendButton = self.mainWindow.findChild(QPushButton, "sendMessage")
        self.previewButton = self.mainWindow.findChild(QPushButton, "preview")
        self.device_combo = self.mainWindow.findChild(QComboBox, "deviceCombo")
        self.forceCancelBtn = self.mainWindow.findChild(
            QPushButton, "forceCancelBtn")
        self.repeattimesEdit = self.mainWindow.findChild(
            QLineEdit, "repeatLineEdit")
        self.intervalEdit = self.mainWindow.findChild(
            QLineEdit, "intervalLineEdit")
        self.hackrfFreqEdit = self.mainWindow.findChild(QLineEdit, "hackrffreqEdit")

        self.modeCombo = self.mainWindow.findChild(QComboBox, "modeCombo")
        self.mode = self.mainWindow.findChild(QLineEdit, "modeInput")
        self.arn = self.mainWindow.findChild(QLineEdit, "arnInput")
        self.label = self.mainWindow.findChild(QLineEdit, "labelInput")
        self.id = self.mainWindow.findChild(QLineEdit, "idInput")
        self.idLabel = self.mainWindow.findChild(QLabel, "idLabel")
        self.dubi = self.mainWindow.findChild(QLineEdit, "dubiInput")
        self.dubiLabel = self.mainWindow.findChild(QLabel, "dubiLabel")
        self.tak = self.mainWindow.findChild(QLineEdit, "takInput")
        self.textEdit = self.mainWindow.findChild(QTextEdit, "text")
        self.processBar = self.mainWindow.findChild(
            QProgressBar, "progressBar")
        self.statuLabel = self.mainWindow.findChild(QLabel, "statuLabel")
        self.reloadDevicesBtn = self.mainWindow.findChild(
            QPushButton, "reloadDevicesBtn")

    def initEvent(self):
        self.sendButton.clicked.connect(self.sendEvent)
        self.previewButton.clicked.connect(self.previewEvent)
        self.forceCancelBtn.clicked.connect(self.forceCancel)
        self.reloadDevicesBtn.clicked.connect(self.reloadDevices)
        self.modeCombo.currentIndexChanged.connect(self.modeChange)

        self.processSignal.connect(self.updateProcessBar)
        self.statuChangeSignal.connect(self.statuChange)
        self.errorSignal.connect(self.errorEvent)

    def getParas(self):
        arn_pattern = re.compile(r"^[A-Z0-9-.]{7}")
        ack_pattern = re.compile(r"^[A-Za-z]")
        ubi_pattern = re.compile(r"[A-Za-z]")
        dbi_pattern = re.compile(r"[0-9]")

        self.modeInput = self.mode.text()
        self.arnInput = ("%7s" % self.arn.text()).replace(" ", ".")
        self.labelInput = self.label.text()
        self.idInput = self.id.text()
        self.dubiInput = self.dubi.text()
        self.takInput = self.tak.text()
        self.text = self.textEdit.toPlainText()

        if self.modeInput != "2":
            QMessageBox.critical(None, "Error", "Only mode A is supported temporarily!", QMessageBox.Yes)
            return self.FAIL
        if not arn_pattern.match(self.arnInput):
            QMessageBox.critical(None, "Error", "Illegal Arn character!", QMessageBox.Yes)
            return self.FAIL

        if len(self.takInput) != 1 or not ack_pattern.match(self.takInput) :
            if self.takInput != "":
                QMessageBox.critical(None, "Error", "Illegal Ack character!", QMessageBox.Yes)
                return self.FAIL

        if len(self.labelInput) > 2:
            QMessageBox.critical(None, "Error", "Length of label more than 2!", QMessageBox.Yes)
            return self.FAIL

        #Generate context based on context Identifier
        if self.transMode == self.UPLINK_MODE:
            if not ubi_pattern.match(self.dubiInput) or len(self.dubiInput) > 1:
                QMessageBox.critical(None, "Error", "Illegal UBI character!", QMessageBox.Yes)
                return self.FAIL
            self.formaltext = self.text
        else:
            if not dbi_pattern.match(self.dubiInput) or len(self.dubiInput) > 1:
                QMessageBox.critical(None, "Error", "Illegal DBI character!", QMessageBox.Yes)
                return self.FAIL

            if len(self.idInput) != 6:
                QMessageBox.critical(None, "Error", "Length of flight id not equals to 6!", QMessageBox.Yes)
                return self.FAIL

            msgNo = "M01A"
            FlightID = self.idInput
            self.formaltext = msgNo + FlightID + self.text


        return self.SUCCESS


    def getDevices(self):
        devices = getInfo()
        for i in devices:
            self.device_combo.addItem(i[-19:])

    def reloadDevices(self):
        for i in range(self.device_combo.count()):
            self.device_combo.removeItem(0)

        self.getDevices()

    def modeChange(self):
        if self.modeCombo.currentIndex() == self.UPLINK_MODE:
            self.transMode = self.UPLINK_MODE
            self.idLabel.setEnabled(False)
            self.dubiLabel.setText("UBI")
            self.id.setEnabled(False)
        else:
            self.transMode = self.DOWNLINK_MODE
            self.idLabel.setEnabled(True)
            self.dubiLabel.setText("DBI")
            self.id.setEnabled(True)

    def getDataForHackRF(self, tempMsg, qtQueue, dataQueue):
        pre_diff = []
        diff = []

        ################  prekey  ############################
        pre_key = "{:08b}".format(255).replace("0b", "")
        for i in range(16):
            pre_diff.extend(pre_key)

        ################  acars message  ############################
        for i in tempMsg:
            temp = "{:08b}".format(i).replace("0b", "")
            pre_diff.extend(temp)


        ###################   差分编码   ############################
        diff.append(int(pre_diff[0]))

        for i in range(1, len(pre_diff)):
            last_bit = pre_diff[i-1]
            if pre_diff[i] == last_bit:
                diff.append(1)
            else:
                diff.append(0)

        cpfsk = Modulation.Modulation.MSK(diff)     #MSK Modulation
        [I, Q] = Modulation.Modulation.AM(cpfsk)    #DSB AM Modulation

        qtQueue.put("Data Processing...")

        dataStream = []
        for i in range(len(I)):
            ####   补码  ###
            i_complement = int(intToBin(int(I[i])), 2)
            q_complement = int(intToBin(int(Q[i])), 2)
            dataStream.append(i_complement)
            dataStream.append(q_complement)
            if i % 11520 == 0:
                qtQueue.put(int(i / 11520) + 1)

        dataQueue.put(dataStream)

    def startTransmitting(self, msg):
        # get HackRF settings
        self.serial = self.device_combo.currentText()
        self.freq = self.hackrfFreqEdit.text()
        self.repeattimes = int(self.repeattimesEdit.text())
        self.interval = int(self.intervalEdit.text())

        self.qtQueue = multiprocessing.Queue()
        self.dataQueue = multiprocessing.Queue()
        self.qtThread = KThread(
            target=self.qtEvent, args=(self.qtQueue, self.qtSignals,))

        self.parent_conn, self.son_conn = multiprocessing.Pipe()

        self.waitProcessThread = KThread(target=self.waitAllDone)
        self.processData = multiprocessing.Process(
            target=self.getDataForHackRF, args=(msg, self.qtQueue, self.dataQueue))

        self.qtThread.start()
        self.waitProcessThread.start()
        self.processData.start()

        self.sendButton.setEnabled(False)

    def forceCancel(self):
        try:
            self.parent_conn.send(1)
        except AttributeError:
            pass

    def previewEvent(self):
        pass
        # self.getParas()
        #message = Message.Message(self.text)
        # protocol = Protocol.Protocol(self.modeInput, self.arnInput, self.labelInput, self.idInput, self.dubiInput,
        #                             self.takInput)
        #tempMsg = protocol.getContentData(message.getEncryptMessage(1))
        #msg = []
        # for i in range(4, len(tempMsg)):
        #    if i < 18 or i >= len(tempMsg)-5:
        #        msg.append(Util.TABEL_FOR_8BIT[int(tempMsg[i] & 0x0f)][int((tempMsg[i] >> 4) & 0x07)])
        #    else:
        #        msg.append(Util.TABEL_FOR_6BIT[int(tempMsg[i] & 0x0f)][int((tempMsg[i] >> 4) & 0x07)])

        # print(msg)

    # 传送
    def sendEvent(self):
        if self.getParas() == self.FAIL:
            return 

        protocol = Protocol.Protocol(self.modeInput, self.arnInput, self.labelInput, self.idInput, self.dubiInput,
                                     self.takInput)
        tempMsg = protocol.getContentData(Util.byteString2Ascii(self.formaltext))
        tempMsg = byteString2Ascii(tempMsg)

        self.startTransmitting(tempMsg)

        print("---------------End--------------------")

    # 更新进度条

    def updateProcessBar(self, num):
        self.processBar.setValue(num)

    def statuChange(self, statuString):
        self.statuLabel.setText(statuString)


    #def waitProcessDone(self):
    #    while True:
    #        if not self.dataQueue.empty():
    #            #value = self.q.get(True)
    #            self.dataStream = self.dataQueue.get()
    #            # print(self.dataStream)
    #            self.hackrfEvent = HackRfEvent(
    #                self.serial, self.repeattimes, self.interval, self.dataStream, self.son_conn)
    #            self.hackrfEvent.start()
    #        time.sleep(0.01)

    def waitAllDone(self):
        while True:
            if not self.dataQueue.empty():
                self.forceCancelBtn.setEnabled(True)
                self.statuChangeSignal.emit("Transmitting...")
                self.dataStream = self.dataQueue.get()
                # print(self.dataStream)
                self.hackrfEvent = HackRfEvent(
                    self.serial, self.freq, self.repeattimes, self.interval, self.dataStream, self.qtQueue, self.son_conn)

                self.hackrfEvent.start()

                recv = self.parent_conn.recv()
                self.hackrfEvent.terminate()
                if recv != 0:
                    self.errorSignal.emit("Device Error!")
                    #self.hackrfEvent.join()

                self.updateProcessBar(0)
                self.sendButton.setEnabled(True)
                self.statuChangeSignal.emit("Waitting...")
                del self.hackrfEvent

                self.qtThread.kill()
                self.waitProcessThread.kill()

            time.sleep(0.01)

    def qtEvent(self, queue, qtSignals):
        while True:
            if not queue.empty():
                value = queue.get(True)
                if isinstance(value, int):
                    qtSignals[0].emit(value)
                elif isinstance(value, str):
                    qtSignals[1].emit(value)

            time.sleep(0.01)

    def errorEvent(self, msg):
        QMessageBox.critical(None, "Error", msg, QMessageBox.Yes)
    # 关闭窗口操作

    def closeWindow(self):
        self.forceCancel()
        self.receiver.stopRecv()

        time.sleep(1)
        os._exit(0)


if __name__ == "__main__":
    main()
