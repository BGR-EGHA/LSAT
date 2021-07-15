# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\Contingency.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Contingency(object):
    def setupUi(self, Contingency):
        Contingency.setObjectName("Contingency")
        Contingency.resize(700, 400)
        self.centralwidget = QtWidgets.QWidget(Contingency)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.mainGridLayout = QtWidgets.QGridLayout()
        self.mainGridLayout.setObjectName("mainGridLayout")
        self.applyPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.applyPushButton.setObjectName("applyPushButton")
        self.mainGridLayout.addWidget(self.applyPushButton, 2, 1, 1, 1)
        self.outputGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.outputGroupBox.setObjectName("outputGroupBox")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.outputGroupBox)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.outputGroupBoxGridLayout = QtWidgets.QGridLayout()
        self.outputGroupBoxGridLayout.setObjectName("outputGroupBoxGridLayout")
        self.outputFileNameLabel = QtWidgets.QLabel(self.outputGroupBox)
        self.outputFileNameLabel.setObjectName("outputFileNameLabel")
        self.outputGroupBoxGridLayout.addWidget(self.outputFileNameLabel, 0, 0, 1, 1)
        self.outputFileNameLineEdit = QtWidgets.QLineEdit(self.outputGroupBox)
        self.outputFileNameLineEdit.setObjectName("outputFileNameLineEdit")
        self.outputGroupBoxGridLayout.addWidget(self.outputFileNameLineEdit, 1, 0, 1, 1)
        self.horizontalLayout_3.addLayout(self.outputGroupBoxGridLayout)
        self.mainGridLayout.addWidget(self.outputGroupBox, 1, 0, 1, 2)
        self.inputGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.inputGroupBox.setObjectName("inputGroupBox")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.inputGroupBox)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.inputGroupBoxGridLayout = QtWidgets.QGridLayout()
        self.inputGroupBoxGridLayout.setObjectName("inputGroupBoxGridLayout")
        self.maskRasterToolButton = QtWidgets.QToolButton(self.inputGroupBox)
        self.maskRasterToolButton.setEnabled(False)
        self.maskRasterToolButton.setObjectName("maskRasterToolButton")
        self.inputGroupBoxGridLayout.addWidget(self.maskRasterToolButton, 9, 1, 1, 1)
        self.attributeTableToolButton = QtWidgets.QToolButton(self.inputGroupBox)
        self.attributeTableToolButton.setObjectName("attributeTableToolButton")
        self.inputGroupBoxGridLayout.addWidget(self.attributeTableToolButton, 3, 3, 1, 1)
        self.addRasterToolButton = QtWidgets.QToolButton(self.inputGroupBox)
        self.addRasterToolButton.setObjectName("addRasterToolButton")
        self.inputGroupBoxGridLayout.addWidget(self.addRasterToolButton, 1, 3, 1, 1)
        self.maskRasterLineEdit = QtWidgets.QLineEdit(self.inputGroupBox)
        self.maskRasterLineEdit.setEnabled(False)
        self.maskRasterLineEdit.setObjectName("maskRasterLineEdit")
        self.inputGroupBoxGridLayout.addWidget(self.maskRasterLineEdit, 9, 0, 1, 1)
        self.maskRasterLabel = QtWidgets.QLabel(self.inputGroupBox)
        self.maskRasterLabel.setObjectName("maskRasterLabel")
        self.inputGroupBoxGridLayout.addWidget(self.maskRasterLabel, 8, 0, 1, 1)
        self.listWidget = QtWidgets.QListWidget(self.inputGroupBox)
        self.listWidget.setObjectName("listWidget")
        self.inputGroupBoxGridLayout.addWidget(self.listWidget, 1, 0, 6, 3)
        self.referenceCheckBox = QtWidgets.QCheckBox(self.inputGroupBox)
        self.referenceCheckBox.setChecked(True)
        self.referenceCheckBox.setObjectName("referenceCheckBox")
        self.inputGroupBoxGridLayout.addWidget(self.referenceCheckBox, 9, 2, 1, 1)
        self.removeRasterToolButton = QtWidgets.QToolButton(self.inputGroupBox)
        self.removeRasterToolButton.setObjectName("removeRasterToolButton")
        self.inputGroupBoxGridLayout.addWidget(self.removeRasterToolButton, 2, 3, 1, 1)
        self.label = QtWidgets.QLabel(self.inputGroupBox)
        self.label.setObjectName("label")
        self.inputGroupBoxGridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.inputGroupBoxGridLayout.setColumnStretch(0, 4)
        self.inputGroupBoxGridLayout.setColumnStretch(1, 1)
        self.inputGroupBoxGridLayout.setColumnStretch(2, 1)
        self.horizontalLayout_2.addLayout(self.inputGroupBoxGridLayout)
        self.mainGridLayout.addWidget(self.inputGroupBox, 0, 0, 1, 2)
        self.mainGridLayout.setColumnStretch(0, 3)
        self.mainGridLayout.setColumnStretch(1, 1)
        self.horizontalLayout.addLayout(self.mainGridLayout)
        Contingency.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Contingency)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 700, 22))
        self.menubar.setObjectName("menubar")
        Contingency.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(Contingency)
        self.statusbar.setObjectName("statusbar")
        Contingency.setStatusBar(self.statusbar)

        self.retranslateUi(Contingency)
        QtCore.QMetaObject.connectSlotsByName(Contingency)

    def retranslateUi(self, Contingency):
        _translate = QtCore.QCoreApplication.translate
        Contingency.setWindowTitle(_translate("Contingency", "Contingency Analysis"))
        self.applyPushButton.setText(_translate("Contingency", "Apply"))
        self.outputGroupBox.setTitle(_translate("Contingency", "Output"))
        self.outputFileNameLabel.setText(_translate("Contingency", "Analysis name"))
        self.outputFileNameLineEdit.setToolTip(_translate("Contingency", "<html><head/><body><p>LSAT will create *name*_ctg.npz in \\results\\statistics\\</p></body></html>"))
        self.inputGroupBox.setTitle(_translate("Contingency", "Input"))
        self.maskRasterToolButton.setText(_translate("Contingency", "..."))
        self.attributeTableToolButton.setText(_translate("Contingency", "..."))
        self.addRasterToolButton.setText(_translate("Contingency", "..."))
        self.maskRasterLabel.setText(_translate("Contingency", "Mask raster"))
        self.referenceCheckBox.setText(_translate("Contingency", "Use project reference as default"))
        self.removeRasterToolButton.setText(_translate("Contingency", "..."))
        self.label.setText(_translate("Contingency", "Raster datasets"))
