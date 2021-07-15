# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\mainFrame.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainFrame(object):
    def setupUi(self, MainFrame):
        MainFrame.setObjectName("MainFrame")
        MainFrame.resize(845, 614)
        self.centralwidget = QtWidgets.QWidget(MainFrame)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.mainGridLayout = QtWidgets.QGridLayout()
        self.mainGridLayout.setObjectName("mainGridLayout")
        self.horizontalLayout.addLayout(self.mainGridLayout)
        MainFrame.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainFrame)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 845, 18))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainFrame.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainFrame)
        self.statusbar.setObjectName("statusbar")
        MainFrame.setStatusBar(self.statusbar)
        self.actionNew_Project = QtWidgets.QAction(MainFrame)
        self.actionNew_Project.setObjectName("actionNew_Project")
        self.actionOpen_Project = QtWidgets.QAction(MainFrame)
        self.actionOpen_Project.setObjectName("actionOpen_Project")
        self.actionExit = QtWidgets.QAction(MainFrame)
        self.actionExit.setObjectName("actionExit")
        self.menuFile.addAction(self.actionNew_Project)
        self.menuFile.addAction(self.actionOpen_Project)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainFrame)
        QtCore.QMetaObject.connectSlotsByName(MainFrame)

    def retranslateUi(self, MainFrame):
        _translate = QtCore.QCoreApplication.translate
        MainFrame.setWindowTitle(_translate("MainFrame", "MainWindow"))
        self.menuFile.setTitle(_translate("MainFrame", "File"))
        self.actionNew_Project.setText(_translate("MainFrame", "New Project..."))
        self.actionOpen_Project.setText(_translate("MainFrame", "Open Project..."))
        self.actionExit.setText(_translate("MainFrame", "Exit"))
