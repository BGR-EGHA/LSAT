# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\LogisticRegression.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LogisticRegressionFrame(object):
    def setupUi(self, LogisticRegressionFrame):
        LogisticRegressionFrame.setObjectName("LogisticRegressionFrame")
        LogisticRegressionFrame.resize(536, 613)
        self.centralwidget = QtWidgets.QWidget(LogisticRegressionFrame)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.mainGridLayout = QtWidgets.QGridLayout()
        self.mainGridLayout.setObjectName("mainGridLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mainGridLayout.addItem(spacerItem, 4, 0, 1, 1)
        self.applyPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.applyPushButton.setObjectName("applyPushButton")
        self.mainGridLayout.addWidget(self.applyPushButton, 4, 2, 1, 1)
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.mainGridLayout.addWidget(self.progressBar, 5, 1, 1, 2)
        self.cancelPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.cancelPushButton.setObjectName("cancelPushButton")
        self.mainGridLayout.addWidget(self.cancelPushButton, 4, 1, 1, 1)
        self.explanatoryParameterGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.explanatoryParameterGroupBox.setObjectName("explanatoryParameterGroupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.explanatoryParameterGroupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.explanatoryParameterGroupBoxGridLayout = QtWidgets.QGridLayout()
        self.explanatoryParameterGroupBoxGridLayout.setObjectName("explanatoryParameterGroupBoxGridLayout")
        self.addToolButton = QtWidgets.QToolButton(self.explanatoryParameterGroupBox)
        self.addToolButton.setText("")
        self.addToolButton.setObjectName("addToolButton")
        self.explanatoryParameterGroupBoxGridLayout.addWidget(self.addToolButton, 0, 1, 1, 1)
        self.treeWidget = QtWidgets.QTreeWidget(self.explanatoryParameterGroupBox)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.header().setCascadingSectionResizes(False)
        self.treeWidget.header().setDefaultSectionSize(100)
        self.explanatoryParameterGroupBoxGridLayout.addWidget(self.treeWidget, 0, 0, 4, 1)
        self.removeToolButton = QtWidgets.QToolButton(self.explanatoryParameterGroupBox)
        self.removeToolButton.setText("")
        self.removeToolButton.setObjectName("removeToolButton")
        self.explanatoryParameterGroupBoxGridLayout.addWidget(self.removeToolButton, 1, 1, 1, 1)
        self.gridLayout.addLayout(self.explanatoryParameterGroupBoxGridLayout, 0, 0, 1, 1)
        self.mainGridLayout.addWidget(self.explanatoryParameterGroupBox, 1, 0, 1, 3)
        self.landslideInventoryGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.landslideInventoryGroupBox.setObjectName("landslideInventoryGroupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.landslideInventoryGroupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.landslideInventoryGroupBoxGridLayout = QtWidgets.QGridLayout()
        self.landslideInventoryGroupBoxGridLayout.setObjectName("landslideInventoryGroupBoxGridLayout")
        self.landslideInventoryToolButton = QtWidgets.QToolButton(self.landslideInventoryGroupBox)
        self.landslideInventoryToolButton.setObjectName("landslideInventoryToolButton")
        self.landslideInventoryGroupBoxGridLayout.addWidget(self.landslideInventoryToolButton, 0, 1, 1, 1)
        self.landslideInventoryComboBox = QtWidgets.QComboBox(self.landslideInventoryGroupBox)
        self.landslideInventoryComboBox.setObjectName("landslideInventoryComboBox")
        self.landslideInventoryGroupBoxGridLayout.addWidget(self.landslideInventoryComboBox, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.landslideInventoryGroupBoxGridLayout)
        self.mainGridLayout.addWidget(self.landslideInventoryGroupBox, 0, 0, 1, 3)
        self.outputgroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.outputgroupBox.setObjectName("outputgroupBox")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.outputgroupBox)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.outputlineEdit = QtWidgets.QLineEdit(self.outputgroupBox)
        self.outputlineEdit.setObjectName("outputlineEdit")
        self.horizontalLayout_2.addWidget(self.outputlineEdit)
        self.mainGridLayout.addWidget(self.outputgroupBox, 2, 0, 2, 3)
        self.mainGridLayout.setColumnStretch(0, 2)
        self.mainGridLayout.setRowStretch(0, 1)
        self.horizontalLayout.addLayout(self.mainGridLayout)
        LogisticRegressionFrame.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(LogisticRegressionFrame)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 536, 21))
        self.menubar.setObjectName("menubar")
        LogisticRegressionFrame.setMenuBar(self.menubar)
        self.toolBar = QtWidgets.QToolBar(LogisticRegressionFrame)
        self.toolBar.setObjectName("toolBar")
        LogisticRegressionFrame.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)

        self.retranslateUi(LogisticRegressionFrame)
        QtCore.QMetaObject.connectSlotsByName(LogisticRegressionFrame)
        LogisticRegressionFrame.setTabOrder(self.landslideInventoryComboBox, self.landslideInventoryToolButton)
        LogisticRegressionFrame.setTabOrder(self.landslideInventoryToolButton, self.treeWidget)
        LogisticRegressionFrame.setTabOrder(self.treeWidget, self.addToolButton)
        LogisticRegressionFrame.setTabOrder(self.addToolButton, self.removeToolButton)
        LogisticRegressionFrame.setTabOrder(self.removeToolButton, self.outputlineEdit)
        LogisticRegressionFrame.setTabOrder(self.outputlineEdit, self.cancelPushButton)
        LogisticRegressionFrame.setTabOrder(self.cancelPushButton, self.applyPushButton)

    def retranslateUi(self, LogisticRegressionFrame):
        _translate = QtCore.QCoreApplication.translate
        LogisticRegressionFrame.setWindowTitle(_translate("LogisticRegressionFrame", "MainWindow"))
        self.applyPushButton.setText(_translate("LogisticRegressionFrame", "Apply"))
        self.cancelPushButton.setText(_translate("LogisticRegressionFrame", "Cancel"))
        self.explanatoryParameterGroupBox.setTitle(_translate("LogisticRegressionFrame", "Explanatory Parameter (independent variables)"))
        self.treeWidget.headerItem().setText(0, _translate("LogisticRegressionFrame", "Parameter"))
        self.treeWidget.headerItem().setText(1, _translate("LogisticRegressionFrame", "Type"))
        self.landslideInventoryGroupBox.setTitle(_translate("LogisticRegressionFrame", "Landslide inventory (dependend variable)"))
        self.landslideInventoryToolButton.setText(_translate("LogisticRegressionFrame", "..."))
        self.outputgroupBox.setTitle(_translate("LogisticRegressionFrame", "Output Name"))
        self.outputlineEdit.setToolTip(_translate("LogisticRegressionFrame", "<html><head/><body><p>LSAT will create three files with the given name.</p><p>*name*_lr.tif in \\results\\LR\\rasters\\,<br/>*name*_tab.npz in \\results\\LR\\tables\\ and<br/>*name*_model.pkl in \\results\\LR\\tables</p></body></html>"))
        self.toolBar.setWindowTitle(_translate("LogisticRegressionFrame", "toolBar"))
