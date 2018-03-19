# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SimPel_config_GUI.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Configurations_Dialog(object):
    def setupUi(self, Configurations_Dialog):
        Configurations_Dialog.setObjectName("Configurations_Dialog")
        Configurations_Dialog.resize(497, 325)
        Configurations_Dialog.setStyleSheet("background-color: rgb(240, 255, 200);")
        self.gridLayout = QtWidgets.QGridLayout(Configurations_Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.plainTextEdit_config = QtWidgets.QPlainTextEdit(Configurations_Dialog)
        self.plainTextEdit_config.setMinimumSize(QtCore.QSize(300, 150))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.plainTextEdit_config.setFont(font)
        self.plainTextEdit_config.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.plainTextEdit_config.setObjectName("plainTextEdit_config")
        self.gridLayout.addWidget(self.plainTextEdit_config, 0, 0, 1, 2)
        self.Accept_conf_Button = QtWidgets.QPushButton(Configurations_Dialog)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.Accept_conf_Button.setFont(font)
        self.Accept_conf_Button.setStyleSheet("background-color: rgb(226, 226, 226);")
        self.Accept_conf_Button.setObjectName("Accept_conf_Button")
        self.gridLayout.addWidget(self.Accept_conf_Button, 1, 0, 1, 1)
        self.Reject_conf_Button = QtWidgets.QPushButton(Configurations_Dialog)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.Reject_conf_Button.setFont(font)
        self.Reject_conf_Button.setStyleSheet("background-color: rgb(226, 226, 226);")
        self.Reject_conf_Button.setObjectName("Reject_conf_Button")
        self.gridLayout.addWidget(self.Reject_conf_Button, 1, 1, 1, 1)

        self.retranslateUi(Configurations_Dialog)
        QtCore.QMetaObject.connectSlotsByName(Configurations_Dialog)

    def retranslateUi(self, Configurations_Dialog):
        _translate = QtCore.QCoreApplication.translate
        Configurations_Dialog.setWindowTitle(_translate("Configurations_Dialog", "Configurations"))
        self.Accept_conf_Button.setText(_translate("Configurations_Dialog", "Accept"))
        self.Reject_conf_Button.setText(_translate("Configurations_Dialog", "Cancel"))

