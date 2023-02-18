from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *

import Message

class MessageListItem(QtWidgets.QListWidgetItem):
    def __init__(self, msg) -> None:
        super(MessageListItem, self).__init__()
        self.msg = msg
        self.show_string = msg.getProcessedText()

    def getItemWidget(self):

        nameLabel = QLabel(
            "<font>%s<font>" % (self.show_string))

        self.widget = QWidget()
        validity = self.msg.getSignValid()
        if validity == Message.SIGN_IS_VALID:
            self.widget.setStyleSheet('''QWidget{background-color:#90EE90;}''')
        elif validity == Message.SIGN_IS_NOT_VALID:
            self.widget.setStyleSheet('''QWidget{background-color:#FFB6C1;}''')
        else:
            self.widget.setStyleSheet('''QWidget{background-color:#FFFFFF;}''')

        layout_main = QHBoxLayout()
        layout_main.addWidget(nameLabel)

        self.widget.setLayout(layout_main)

        return self.widget

    def getMsgUnit(self):
        return self.msg
