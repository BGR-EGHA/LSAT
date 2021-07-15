# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\PlotViewer.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_GraphicViewer(object):
    def setupUi(self, GraphicViewer):
        GraphicViewer.setObjectName("GraphicViewer")
        GraphicViewer.resize(817, 626)
        self.centralwidget = QtWidgets.QWidget(GraphicViewer)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.mainGridLayout = QtWidgets.QGridLayout()
        self.mainGridLayout.setObjectName("mainGridLayout")
        self.horizontalLayout.addLayout(self.mainGridLayout)
        GraphicViewer.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(GraphicViewer)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 817, 21))
        self.menubar.setObjectName("menubar")
        GraphicViewer.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(GraphicViewer)
        self.statusbar.setObjectName("statusbar")
        GraphicViewer.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(GraphicViewer)
        self.toolBar.setObjectName("toolBar")
        GraphicViewer.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)

        self.retranslateUi(GraphicViewer)
        QtCore.QMetaObject.connectSlotsByName(GraphicViewer)

    def retranslateUi(self, GraphicViewer):
        _translate = QtCore.QCoreApplication.translate
        GraphicViewer.setWindowTitle(_translate("GraphicViewer", "MainWindow"))
        self.toolBar.setWindowTitle(_translate("GraphicViewer", "toolBar"))
