# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Slope.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Slope(object):
    def setupUi(self, Slope):
        Slope.setObjectName("Slope")
        Slope.resize(535, 443)
        self.centralwidget = QtWidgets.QWidget(Slope)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.mainGridLayout = QtWidgets.QGridLayout()
        self.mainGridLayout.setObjectName("mainGridLayout")
        self.inputGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.inputGroupBox.setObjectName("inputGroupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.inputGroupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.inputGroupBoxGridLayout = QtWidgets.QGridLayout()
        self.inputGroupBoxGridLayout.setObjectName("inputGroupBoxGridLayout")
        self.demRasterLabel = QtWidgets.QLabel(self.inputGroupBox)
        self.demRasterLabel.setObjectName("demRasterLabel")
        self.inputGroupBoxGridLayout.addWidget(self.demRasterLabel, 0, 0, 1, 1)
        self.demRasterToolButton = QtWidgets.QToolButton(self.inputGroupBox)
        self.demRasterToolButton.setObjectName("demRasterToolButton")
        self.inputGroupBoxGridLayout.addWidget(self.demRasterToolButton, 1, 1, 1, 1)
        self.demRasterComboBox = QtWidgets.QComboBox(self.inputGroupBox)
        self.demRasterComboBox.setObjectName("demRasterComboBox")
        self.inputGroupBoxGridLayout.addWidget(self.demRasterComboBox, 1, 0, 1, 1)
        self.horizontalLayout.addLayout(self.inputGroupBoxGridLayout)
        self.mainGridLayout.addWidget(self.inputGroupBox, 0, 0, 1, 4)
        self.cancelPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.cancelPushButton.setObjectName("cancelPushButton")
        self.mainGridLayout.addWidget(self.cancelPushButton, 3, 1, 1, 1)
        self.outputGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.outputGroupBox.setObjectName("outputGroupBox")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.outputGroupBox)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.outputBoxGridLayout = QtWidgets.QGridLayout()
        self.outputBoxGridLayout.setObjectName("outputBoxGridLayout")
        self.outputRasterLineEdit = QtWidgets.QLineEdit(self.outputGroupBox)
        self.outputRasterLineEdit.setObjectName("outputRasterLineEdit")
        self.outputBoxGridLayout.addWidget(self.outputRasterLineEdit, 6, 0, 1, 1)
        self.outputRasterToolButton = QtWidgets.QToolButton(self.outputGroupBox)
        self.outputRasterToolButton.setObjectName("outputRasterToolButton")
        self.outputBoxGridLayout.addWidget(self.outputRasterToolButton, 6, 1, 1, 1)
        self.outputRasterLabel = QtWidgets.QLabel(self.outputGroupBox)
        self.outputRasterLabel.setObjectName("outputRasterLabel")
        self.outputBoxGridLayout.addWidget(self.outputRasterLabel, 5, 0, 1, 1)
        self.horizontalLayout_2.addLayout(self.outputBoxGridLayout)
        self.mainGridLayout.addWidget(self.outputGroupBox, 2, 0, 1, 4)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mainGridLayout.addItem(spacerItem, 3, 0, 1, 1)
        self.okPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.okPushButton.setObjectName("okPushButton")
        self.mainGridLayout.addWidget(self.okPushButton, 3, 2, 1, 1)
        self.optionsGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.optionsGroupBox.setObjectName("optionsGroupBox")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.optionsGroupBox)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.optionsGroupBoxGridLayout = QtWidgets.QGridLayout()
        self.optionsGroupBoxGridLayout.setObjectName("optionsGroupBoxGridLayout")
        self.methodComboBox = QtWidgets.QComboBox(self.optionsGroupBox)
        self.methodComboBox.setObjectName("methodComboBox")
        self.methodComboBox.addItem("")
        self.methodComboBox.addItem("")
        self.optionsGroupBoxGridLayout.addWidget(self.methodComboBox, 3, 0, 1, 1)
        self.slopeUnitComboBox = QtWidgets.QComboBox(self.optionsGroupBox)
        self.slopeUnitComboBox.setObjectName("slopeUnitComboBox")
        self.slopeUnitComboBox.addItem("")
        self.slopeUnitComboBox.addItem("")
        self.optionsGroupBoxGridLayout.addWidget(self.slopeUnitComboBox, 1, 0, 1, 1)
        self.slopeUnitLabel = QtWidgets.QLabel(self.optionsGroupBox)
        self.slopeUnitLabel.setObjectName("slopeUnitLabel")
        self.optionsGroupBoxGridLayout.addWidget(self.slopeUnitLabel, 0, 0, 1, 1)
        self.methodLabel = QtWidgets.QLabel(self.optionsGroupBox)
        self.methodLabel.setObjectName("methodLabel")
        self.optionsGroupBoxGridLayout.addWidget(self.methodLabel, 2, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.optionsGroupBoxGridLayout.addItem(spacerItem1, 2, 1, 1, 1)
        self.optionsGroupBoxGridLayout.setColumnStretch(0, 3)
        self.optionsGroupBoxGridLayout.setColumnStretch(1, 1)
        self.horizontalLayout_3.addLayout(self.optionsGroupBoxGridLayout)
        self.mainGridLayout.addWidget(self.optionsGroupBox, 1, 0, 1, 3)
        self.mainGridLayout.setRowStretch(1, 1)
        self.verticalLayout.addLayout(self.mainGridLayout)
        Slope.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Slope)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 535, 26))
        self.menubar.setObjectName("menubar")
        Slope.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(Slope)
        self.statusbar.setObjectName("statusbar")
        Slope.setStatusBar(self.statusbar)

        self.retranslateUi(Slope)
        QtCore.QMetaObject.connectSlotsByName(Slope)
        Slope.setTabOrder(self.demRasterComboBox, self.demRasterToolButton)
        Slope.setTabOrder(self.demRasterToolButton, self.outputRasterLineEdit)
        Slope.setTabOrder(self.outputRasterLineEdit, self.outputRasterToolButton)
        Slope.setTabOrder(self.outputRasterToolButton, self.cancelPushButton)
        Slope.setTabOrder(self.cancelPushButton, self.okPushButton)

    def retranslateUi(self, Slope):
        _translate = QtCore.QCoreApplication.translate
        Slope.setWindowTitle(_translate("Slope", "MainWindow"))
        self.inputGroupBox.setTitle(_translate("Slope", "Input "))
        self.demRasterLabel.setText(_translate("Slope", "DEM raster"))
        self.demRasterToolButton.setText(_translate("Slope", "..."))
        self.cancelPushButton.setText(_translate("Slope", "Cancel"))
        self.outputGroupBox.setTitle(_translate("Slope", "Output"))
        self.outputRasterToolButton.setText(_translate("Slope", "..."))
        self.outputRasterLabel.setText(_translate("Slope", "Output raster"))
        self.okPushButton.setText(_translate("Slope", "OK"))
        self.optionsGroupBox.setTitle(_translate("Slope", "Options"))
        self.methodComboBox.setItemText(0, _translate("Slope", "Horn"))
        self.methodComboBox.setItemText(1, _translate("Slope", "Zevenbergen & Thorne"))
        self.slopeUnitComboBox.setItemText(0, _translate("Slope", "DEGREE"))
        self.slopeUnitComboBox.setItemText(1, _translate("Slope", "PERCENT"))
        self.slopeUnitLabel.setText(_translate("Slope", "Unit"))
        self.methodLabel.setText(_translate("Slope", "Method"))
