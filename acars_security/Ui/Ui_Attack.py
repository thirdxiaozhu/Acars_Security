# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/ui/attack.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(720, 538)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.labelEdit = QtWidgets.QLineEdit(Form)
        self.labelEdit.setObjectName("labelEdit")
        self.horizontalLayout.addWidget(self.labelEdit)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.arnEdit = QtWidgets.QLineEdit(Form)
        self.arnEdit.setObjectName("arnEdit")
        self.horizontalLayout.addWidget(self.arnEdit)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.udbiEdit = QtWidgets.QLineEdit(Form)
        self.udbiEdit.setObjectName("udbiEdit")
        self.horizontalLayout.addWidget(self.udbiEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.textEdit = QtWidgets.QTextEdit(Form)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout.addWidget(self.textEdit)
        self.label_5 = QtWidgets.QLabel(Form)
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.signEdit = QtWidgets.QTextEdit(Form)
        self.signEdit.setObjectName("signEdit")
        self.verticalLayout.addWidget(self.signEdit)
        self.send_btn = QtWidgets.QPushButton(Form)
        self.send_btn.setObjectName("send_btn")
        self.verticalLayout.addWidget(self.send_btn)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(5, 1)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "Label"))
        self.label_2.setText(_translate("Form", "ARN"))
        self.label_3.setText(_translate("Form", "UDBI"))
        self.label_4.setText(_translate("Form", "Text"))
        self.label_5.setText(_translate("Form", "Signature"))
        self.send_btn.setText(_translate("Form", "Send"))
