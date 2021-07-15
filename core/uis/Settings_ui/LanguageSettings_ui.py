# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\LanguageSettings.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LanguageSettings(object):
    def setupUi(self, LanguageSettings):
        LanguageSettings.setObjectName("LanguageSettings")
        LanguageSettings.resize(280, 125)
        self.centralwidget = QtWidgets.QWidget(LanguageSettings)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.mainGridLayout = QtWidgets.QGridLayout()
        self.mainGridLayout.setObjectName("mainGridLayout")
        self.languageGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.languageGroupBox.setObjectName("languageGroupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.languageGroupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.languageGroupBoxGridLayout = QtWidgets.QGridLayout()
        self.languageGroupBoxGridLayout.setObjectName("languageGroupBoxGridLayout")
        self.applyPushButton = QtWidgets.QPushButton(self.languageGroupBox)
        self.applyPushButton.setObjectName("applyPushButton")
        self.languageGroupBoxGridLayout.addWidget(self.applyPushButton, 1, 2, 1, 1)
        self.cancelPushButton = QtWidgets.QPushButton(self.languageGroupBox)
        self.cancelPushButton.setObjectName("cancelPushButton")
        self.languageGroupBoxGridLayout.addWidget(self.cancelPushButton, 1, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.languageGroupBoxGridLayout.addItem(spacerItem, 1, 0, 1, 1)
        self.comboBox = QtWidgets.QComboBox(self.languageGroupBox)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.languageGroupBoxGridLayout.addWidget(self.comboBox, 0, 0, 1, 2)
        self.gridLayout.addLayout(self.languageGroupBoxGridLayout, 0, 0, 1, 1)
        self.mainGridLayout.addWidget(self.languageGroupBox, 0, 0, 1, 1)
        self.horizontalLayout.addLayout(self.mainGridLayout)
        LanguageSettings.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(LanguageSettings)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 280, 21))
        self.menubar.setObjectName("menubar")
        LanguageSettings.setMenuBar(self.menubar)

        self.retranslateUi(LanguageSettings)
        QtCore.QMetaObject.connectSlotsByName(LanguageSettings)
        LanguageSettings.setTabOrder(self.comboBox, self.cancelPushButton)
        LanguageSettings.setTabOrder(self.cancelPushButton, self.applyPushButton)

    def retranslateUi(self, LanguageSettings):
        _translate = QtCore.QCoreApplication.translate
        LanguageSettings.setWindowTitle(_translate("LanguageSettings", "MainWindow"))
        self.languageGroupBox.setTitle(_translate("LanguageSettings", "Select Language"))
        self.applyPushButton.setText(_translate("LanguageSettings", "Apply"))
        self.cancelPushButton.setText(_translate("LanguageSettings", "Cancel"))
        self.comboBox.setItemText(0, _translate("LanguageSettings", "中国"))
        self.comboBox.setItemText(1, _translate("LanguageSettings", "English"))
        self.comboBox.setItemText(2, _translate("LanguageSettings", "Deutsch"))
        self.comboBox.setItemText(3, _translate("LanguageSettings", "Русский"))
