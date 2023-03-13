from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Attack(QtCore.QObject):
    def __init__(self, dialog, item, entity) -> None:
        self.dialog = dialog
        self.entity = entity
        self.msg = item.getMsgUnit()
        self.tuple = self.msg.getMsgTuple()
        self.text_to_modi = ""
        self.sign_to_modi = ""
        self.label = ""
        self.initContents()
        self.initComponent()

    def initContents(self):
        self.label = self.tuple[4]
        self.text_to_modi = self.tuple[9]
        print("'" , self.text_to_modi, "'")

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
        t = self.tuple
        self.entity.putMessageParasExec([(t[3], t[4], t[5],t[6], t[7], t[8], self.textEdit.toPlainText(), "")], True)



