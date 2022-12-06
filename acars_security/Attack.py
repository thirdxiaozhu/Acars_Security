from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import Message

class Attack(QtCore.QObject):
    def __init__(self, dialog, item, dsp) -> None:
        self.dialog = dialog
        self.dsp = dsp
        self.msg = item.getMsgUnit()
        self.tuple = self.msg.getMsgTuple()
        print(self.tuple)
        self.text_to_modi = ""
        self.sign_to_modi = ""
        self.label = ""
        self.initContents()
        self.initComponent()

    def initContents(self):
        self.label = self.tuple[4]

        if self.label != "P8":
            self.text_to_modi = self.tuple[10]
        else:
            self.text_to_modi = self.tuple[11].decode("latin1")
            self.sign_to_modi = self.tuple[12].decode("latin1")

    def initComponent(self):
        text = """
        <div>
            <div> %s</div>
        </div>
        """
        self.textEdit = self.dialog.findChild(QTextEdit, "textEdit")
        self.signEdit = self.dialog.findChild(QTextEdit, "signEdit")
        self.udbiEdit = self.dialog.findChild(QLineEdit, "udbiEdit")
        self.arnEdit = self.dialog.findChild(QLineEdit, "arnEdit")
        self.labelEdit = self.dialog.findChild(QLineEdit, "labelEdit")
        self.sendbtn = self.dialog.findChild(QPushButton, "send_btn")

        self.sendbtn.clicked.connect(lambda: self.send())

        self.labelEdit.setText(self.tuple[4])
        self.arnEdit.setText(self.tuple[5])
        self.udbiEdit.setText(self.tuple[6])

        self.textEdit.append(text % self.text_to_modi)
        self.signEdit.append(text % self.sign_to_modi)

    def send(self):
        self.dsp.initHackRF()
        msg_unit =  self.processMsg()
        msg_unit.generateIQ()
        self.dsp._hackrf_event.putMessage(msg_unit._IQdata)
        self.dsp.startHackRF()


    def processMsg(self):
        if self.label != "P8":
            return Message.Message(self.tuple[:10] + (self.textEdit.toPlainText()[:-1], ))
        else:
            cipher_text = self.textEdit.toPlainText()[:-1]
            sign_text = self.signEdit.toPlainText()[:-1]
            processed_text = chr(len(cipher_text)) + chr(len(sign_text)) + cipher_text + sign_text

            return Message.Message(self.tuple[:10] + (processed_text, ))

