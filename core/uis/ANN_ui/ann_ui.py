# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ann.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ANN(object):
    def setupUi(self, ANN):
        ANN.setObjectName("ANN")
        ANN.resize(622, 560)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ANN.sizePolicy().hasHeightForWidth())
        ANN.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(ANN)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.mainGridLayout = QtWidgets.QGridLayout()
        self.mainGridLayout.setContentsMargins(6, 6, 6, 6)
        self.mainGridLayout.setHorizontalSpacing(0)
        self.mainGridLayout.setObjectName("mainGridLayout")
        self.rastergroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.rastergroupBox.setObjectName("rastergroupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.rastergroupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.addrasterPushButton = QtWidgets.QToolButton(self.rastergroupBox)
        self.addrasterPushButton.setText("")
        self.addrasterPushButton.setObjectName("addrasterPushButton")
        self.gridLayout.addWidget(self.addrasterPushButton, 2, 1, 1, 1)
        self.mainTableWidget = QtWidgets.QTableWidget(self.rastergroupBox)
        self.mainTableWidget.setEnabled(True)
        self.mainTableWidget.setAlternatingRowColors(True)
        self.mainTableWidget.setRowCount(0)
        self.mainTableWidget.setColumnCount(2)
        self.mainTableWidget.setObjectName("mainTableWidget")
        self.mainTableWidget.horizontalHeader().setVisible(True)
        self.mainTableWidget.horizontalHeader().setCascadingSectionResizes(False)
        self.mainTableWidget.horizontalHeader().setStretchLastSection(True)
        self.gridLayout.addWidget(self.mainTableWidget, 1, 0, 4, 1)
        self.removerasterPushButton = QtWidgets.QToolButton(self.rastergroupBox)
        self.removerasterPushButton.setText("")
        self.removerasterPushButton.setObjectName("removerasterPushButton")
        self.gridLayout.addWidget(self.removerasterPushButton, 3, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 1, 1, 1)
        self.mainGridLayout.addWidget(self.rastergroupBox, 1, 0, 1, 2)
        self.inventorygroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.inventorygroupBox.setObjectName("inventorygroupBox")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.inventorygroupBox)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.inventoryLineEdit = QtWidgets.QLineEdit(self.inventorygroupBox)
        self.inventoryLineEdit.setObjectName("inventoryLineEdit")
        self.horizontalLayout_2.addWidget(self.inventoryLineEdit)
        self.inventoryPushButton = QtWidgets.QToolButton(self.inventorygroupBox)
        self.inventoryPushButton.setObjectName("inventoryPushButton")
        self.horizontalLayout_2.addWidget(self.inventoryPushButton)
        self.mainGridLayout.addWidget(self.inventorygroupBox, 0, 0, 1, 2)
        self.outputgroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.outputgroupBox.setToolTip("")
        self.outputgroupBox.setObjectName("outputgroupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.outputgroupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.outputLineEdit = QtWidgets.QLineEdit(self.outputgroupBox)
        self.outputLineEdit.setText("")
        self.outputLineEdit.setObjectName("outputLineEdit")
        self.verticalLayout_2.addWidget(self.outputLineEdit)
        self.mainGridLayout.addWidget(self.outputgroupBox, 8, 0, 1, 2)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mainGridLayout.addItem(spacerItem1, 9, 0, 1, 1)
        self.applyPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.applyPushButton.setObjectName("applyPushButton")
        self.mainGridLayout.addWidget(self.applyPushButton, 9, 1, 1, 1)
        self.gridLayout_2.addLayout(self.mainGridLayout, 0, 0, 1, 1)
        ANN.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(ANN)
        self.menubar.setEnabled(True)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 622, 21))
        self.menubar.setObjectName("menubar")
        ANN.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(ANN)
        self.statusbar.setEnabled(True)
        self.statusbar.setObjectName("statusbar")
        ANN.setStatusBar(self.statusbar)

        self.retranslateUi(ANN)
        QtCore.QMetaObject.connectSlotsByName(ANN)
        ANN.setTabOrder(self.inventoryLineEdit, self.inventoryPushButton)
        ANN.setTabOrder(self.inventoryPushButton, self.mainTableWidget)
        ANN.setTabOrder(self.mainTableWidget, self.addrasterPushButton)
        ANN.setTabOrder(self.addrasterPushButton, self.removerasterPushButton)
        ANN.setTabOrder(self.removerasterPushButton, self.outputLineEdit)
        ANN.setTabOrder(self.outputLineEdit, self.applyPushButton)

    def retranslateUi(self, ANN):
        _translate = QtCore.QCoreApplication.translate
        ANN.setWindowTitle(_translate("ANN", "ANN"))
        self.rastergroupBox.setTitle(_translate("ANN", "Explanatory Parameters"))
        self.inventorygroupBox.setTitle(_translate("ANN", "Landslide inventory"))
        self.inventoryLineEdit.setToolTip(_translate("ANN", "Path to inventory"))
        self.inventoryPushButton.setText(_translate("ANN", "..."))
        self.outputgroupBox.setTitle(_translate("ANN", "Output Name"))
        self.outputLineEdit.setToolTip(_translate("ANN", "<html><head/><body><p>LSAT will create three files with the given name.</p><p>*name*_ann.tif in \\results\\ANN\\rasters\\,<br/>*name*_tab.npz in \\results\\ANN\\tables\\ and<br/>*name*_model.pkl in \\results\\ANN\\tables</p></body></html>"))
        self.applyPushButton.setToolTip(_translate("ANN", "Calculate with ANN"))
        self.applyPushButton.setText(_translate("ANN", "Apply"))
