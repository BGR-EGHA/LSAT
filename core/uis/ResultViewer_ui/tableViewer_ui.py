# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\tableViewer.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_TableViewWidget(object):
    def setupUi(self, TableViewWidget):
        TableViewWidget.setObjectName("TableViewWidget")
        TableViewWidget.resize(1021, 696)
        self.centralwidget = QtWidgets.QWidget(TableViewWidget)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.mainGridLayout = QtWidgets.QGridLayout()
        self.mainGridLayout.setObjectName("mainGridLayout")
        self.tableView = QtWidgets.QTableView(self.centralwidget)
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setObjectName("tableView")
        self.mainGridLayout.addWidget(self.tableView, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.mainGridLayout)
        TableViewWidget.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(TableViewWidget)
        self.statusbar.setObjectName("statusbar")
        TableViewWidget.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(TableViewWidget)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1021, 21))
        self.menubar.setObjectName("menubar")
        TableViewWidget.setMenuBar(self.menubar)
        self.toolBar = QtWidgets.QToolBar(TableViewWidget)
        self.toolBar.setObjectName("toolBar")
        TableViewWidget.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)

        self.retranslateUi(TableViewWidget)
        QtCore.QMetaObject.connectSlotsByName(TableViewWidget)

    def retranslateUi(self, TableViewWidget):
        _translate = QtCore.QCoreApplication.translate
        TableViewWidget.setWindowTitle(_translate("TableViewWidget", "TableViewer"))
        self.toolBar.setWindowTitle(_translate("TableViewWidget", "toolBar"))
