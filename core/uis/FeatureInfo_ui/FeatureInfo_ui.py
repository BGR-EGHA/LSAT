# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\FeatureInfo.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_FeatureInfo(object):
    def setupUi(self, FeatureInfo):
        FeatureInfo.setObjectName("FeatureInfo")
        FeatureInfo.resize(700, 600)
        self.centralwidget = QtWidgets.QWidget(FeatureInfo)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.mainGridLayout = QtWidgets.QGridLayout()
        self.mainGridLayout.setObjectName("mainGridLayout")
        self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        self.treeWidget.setObjectName("treeWidget")
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item_0.setFont(0, font)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item_0.setFont(0, font)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item_0.setFont(0, font)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item_0.setFont(0, font)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item_0.setFont(0, font)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_0 = QtWidgets.QTreeWidgetItem(self.treeWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item_0.setFont(0, font)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        item_1 = QtWidgets.QTreeWidgetItem(item_0)
        self.treeWidget.header().setDefaultSectionSize(150)
        self.treeWidget.header().setHighlightSections(True)
        self.mainGridLayout.addWidget(self.treeWidget, 0, 0, 1, 1)
        self.horizontalLayout.addLayout(self.mainGridLayout)
        FeatureInfo.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(FeatureInfo)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 700, 22))
        self.menubar.setObjectName("menubar")
        FeatureInfo.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(FeatureInfo)
        self.statusbar.setObjectName("statusbar")
        FeatureInfo.setStatusBar(self.statusbar)

        self.retranslateUi(FeatureInfo)
        QtCore.QMetaObject.connectSlotsByName(FeatureInfo)

    def retranslateUi(self, FeatureInfo):
        _translate = QtCore.QCoreApplication.translate
        FeatureInfo.setWindowTitle(_translate("FeatureInfo", "Feature Info"))
        self.treeWidget.headerItem().setText(0, _translate("FeatureInfo", "Info"))
        self.treeWidget.headerItem().setText(1, _translate("FeatureInfo", "Value"))
        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        self.treeWidget.topLevelItem(0).setText(0, _translate("FeatureInfo", "Source path"))
        self.treeWidget.topLevelItem(1).setText(0, _translate("FeatureInfo", "Type"))
        self.treeWidget.topLevelItem(2).setText(0, _translate("FeatureInfo", "Feature count"))
        self.treeWidget.topLevelItem(3).setText(0, _translate("FeatureInfo", "Fields"))
        self.treeWidget.topLevelItem(4).setText(0, _translate("FeatureInfo", "Spatial Reference"))
        self.treeWidget.topLevelItem(4).child(0).setText(0, _translate("FeatureInfo", "EPSG Code"))
        self.treeWidget.topLevelItem(4).child(1).setText(0, _translate("FeatureInfo", "Projection"))
        self.treeWidget.topLevelItem(5).setText(0, _translate("FeatureInfo", "Extent"))
        self.treeWidget.topLevelItem(5).child(0).setText(0, _translate("FeatureInfo", "top"))
        self.treeWidget.topLevelItem(5).child(1).setText(0, _translate("FeatureInfo", "left"))
        self.treeWidget.topLevelItem(5).child(2).setText(0, _translate("FeatureInfo", "right"))
        self.treeWidget.topLevelItem(5).child(3).setText(0, _translate("FeatureInfo", "bottom"))
        self.treeWidget.setSortingEnabled(__sortingEnabled)
