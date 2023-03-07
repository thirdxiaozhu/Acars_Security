# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/ui/msg_crypt_detail.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(665, 575)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setContentsMargins(-1, 10, -1, -1)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_5.addWidget(self.label_3)
        self.origninal_data_edit = QtWidgets.QTextEdit(Form)
        self.origninal_data_edit.setObjectName("origninal_data_edit")
        self.verticalLayout_5.addWidget(self.origninal_data_edit)
        self.verticalLayout.addLayout(self.verticalLayout_5)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.horizontalLayout_5.addWidget(self.label)
        self.cipher_len_line = QtWidgets.QLineEdit(Form)
        self.cipher_len_line.setObjectName("cipher_len_line")
        self.horizontalLayout_5.addWidget(self.cipher_len_line)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_5.addWidget(self.label_2)
        self.sign_len_edit = QtWidgets.QLineEdit(Form)
        self.sign_len_edit.setObjectName("sign_len_edit")
        self.horizontalLayout_5.addWidget(self.sign_len_edit)
        self.horizontalLayout_5.setStretch(0, 1)
        self.horizontalLayout_5.setStretch(1, 2)
        self.horizontalLayout_5.setStretch(2, 2)
        self.horizontalLayout_5.setStretch(3, 1)
        self.horizontalLayout_5.setStretch(4, 2)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setContentsMargins(0, 10, 10, 10)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_4.addWidget(self.label_4)
        self.ciphertext_edit = QtWidgets.QTextEdit(Form)
        self.ciphertext_edit.setObjectName("ciphertext_edit")
        self.verticalLayout_4.addWidget(self.ciphertext_edit)
        self.horizontalLayout_2.addLayout(self.verticalLayout_4)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_6 = QtWidgets.QLabel(Form)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_6.addWidget(self.label_6)
        self.signature_edit = QtWidgets.QTextEdit(Form)
        self.signature_edit.setObjectName("signature_edit")
        self.verticalLayout_6.addWidget(self.signature_edit)
        self.horizontalLayout_2.addLayout(self.verticalLayout_6)
        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(-1, 10, -1, -1)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_5 = QtWidgets.QLabel(Form)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_3.addWidget(self.label_5)
        self.plaintext_edit = QtWidgets.QTextEdit(Form)
        self.plaintext_edit.setObjectName("plaintext_edit")
        self.verticalLayout_3.addWidget(self.plaintext_edit)
        self.verticalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setContentsMargins(-1, 10, -1, -1)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.label_7 = QtWidgets.QLabel(Form)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_7.addWidget(self.label_7)
        self.arinc620_edit = QtWidgets.QTextBrowser(Form)
        self.arinc620_edit.setObjectName("arinc620_edit")
        self.verticalLayout_7.addWidget(self.arinc620_edit)
        self.verticalLayout.addLayout(self.verticalLayout_7)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 10, -1, 10)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.confirm_btn = QtWidgets.QPushButton(Form)
        self.confirm_btn.setObjectName("confirm_btn")
        self.horizontalLayout.addWidget(self.confirm_btn)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.setStretch(0, 2)
        self.verticalLayout.setStretch(1, 1)
        self.verticalLayout.setStretch(2, 2)
        self.verticalLayout.setStretch(3, 2)
        self.verticalLayout.setStretch(4, 2)
        self.verticalLayout.setStretch(5, 1)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_3.setText(_translate("Form", "Original Data"))
        self.label.setText(_translate("Form", "Ciphertext Length"))
        self.label_2.setText(_translate("Form", "Signature Length"))
        self.label_4.setText(_translate("Form", "CipherText"))
        self.label_6.setText(_translate("Form", "Signature"))
        self.label_5.setText(_translate("Form", "Plaintext"))
        self.label_7.setText(_translate("Form", "ARINC 620"))
        self.confirm_btn.setText(_translate("Form", "OK"))
