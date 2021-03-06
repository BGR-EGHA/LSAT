# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ResultsContingencyMatrix.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ContingencyMatrix(object):
    def setupUi(self, ContingencyMatrix):
        ContingencyMatrix.setObjectName("ContingencyMatrix")
        ContingencyMatrix.resize(1000, 750)
        ContingencyMatrix.setWindowOpacity(1.0)
        self.centralwidget = QtWidgets.QWidget(ContingencyMatrix)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.mainGridLayout = QtWidgets.QGridLayout()
        self.mainGridLayout.setObjectName("mainGridLayout")
        self.matrixGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.matrixGroupBox.setObjectName("matrixGroupBox")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.matrixGroupBox)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.typeComboBox = QtWidgets.QComboBox(self.matrixGroupBox)
        self.typeComboBox.setObjectName("typeComboBox")
        self.typeComboBox.addItem("")
        self.typeComboBox.addItem("")
        self.verticalLayout_5.addWidget(self.typeComboBox)
        self.label = QtWidgets.QLabel(self.matrixGroupBox)
        self.label.setObjectName("label")
        self.verticalLayout_5.addWidget(self.label)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.tableView = QtWidgets.QTableView(self.matrixGroupBox)
        self.tableView.setObjectName("tableView")
        self.horizontalLayout_2.addWidget(self.tableView)
        self.verticalLayout_5.addLayout(self.horizontalLayout_2)
        self.mainGridLayout.addWidget(self.matrixGroupBox, 0, 0, 1, 1)
        self.horizontalLayout.addLayout(self.mainGridLayout)
        ContingencyMatrix.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(ContingencyMatrix)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1000, 22))
        self.menubar.setObjectName("menubar")
        ContingencyMatrix.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(ContingencyMatrix)
        self.statusbar.setObjectName("statusbar")
        ContingencyMatrix.setStatusBar(self.statusbar)

        self.retranslateUi(ContingencyMatrix)
        QtCore.QMetaObject.connectSlotsByName(ContingencyMatrix)

    def retranslateUi(self, ContingencyMatrix):
        _translate = QtCore.QCoreApplication.translate
        ContingencyMatrix.setWindowTitle(_translate("ContingencyMatrix", "Contingency Matrix"))
        self.matrixGroupBox.setTitle(_translate("ContingencyMatrix", "Contingency Matrix "))
        self.typeComboBox.setItemText(0, _translate("ContingencyMatrix", "Pearson\'s C"))
        self.typeComboBox.setItemText(1, _translate("ContingencyMatrix", "Cramers\' V"))
        self.label.setText(_translate("ContingencyMatrix", "To see details for input pairs, double-click on the corresponding matrix field."))
