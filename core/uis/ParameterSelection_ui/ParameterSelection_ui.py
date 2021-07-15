# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ParameterSelection.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ParameterSelection(object):
    def setupUi(self, ParameterSelection):
        ParameterSelection.setObjectName("ParameterSelection")
        ParameterSelection.resize(600, 600)
        self.centralwidget = QtWidgets.QWidget(ParameterSelection)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.mainGridLayout = QtWidgets.QGridLayout()
        self.mainGridLayout.setObjectName("mainGridLayout")
        self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.header().setDefaultSectionSize(90)
        self.mainGridLayout.addWidget(self.treeWidget, 1, 0, 1, 2)
        self.applyPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.applyPushButton.setObjectName("applyPushButton")
        self.mainGridLayout.addWidget(self.applyPushButton, 2, 1, 1, 1)
        self.toggleselectAllLayersPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.toggleselectAllLayersPushButton.setObjectName("toggleselectAllLayersPushButton")
        self.mainGridLayout.addWidget(self.toggleselectAllLayersPushButton, 2, 0, 1, 1)
        self.verticalLayout.addLayout(self.mainGridLayout)
        ParameterSelection.setCentralWidget(self.centralwidget)

        self.retranslateUi(ParameterSelection)
        QtCore.QMetaObject.connectSlotsByName(ParameterSelection)
        ParameterSelection.setTabOrder(self.treeWidget, self.applyPushButton)

    def retranslateUi(self, ParameterSelection):
        _translate = QtCore.QCoreApplication.translate
        ParameterSelection.setWindowTitle(_translate("ParameterSelection", "Parameter Selection"))
        self.treeWidget.headerItem().setText(0, _translate("ParameterSelection", "Layer Name"))
        self.applyPushButton.setText(_translate("ParameterSelection", "Apply"))
        self.toggleselectAllLayersPushButton.setText(_translate("ParameterSelection", "Select All Layers"))
