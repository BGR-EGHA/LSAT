# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ImportInventory.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ImportInventory(object):
    def setupUi(self, ImportInventory):
        ImportInventory.setObjectName("ImportInventory")
        ImportInventory.resize(421, 327)
        self.centralwidget = QtWidgets.QWidget(ImportInventory)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.mainGridLayout = QtWidgets.QGridLayout()
        self.mainGridLayout.setObjectName("mainGridLayout")
        self.splitInventoryCheckBox = QtWidgets.QCheckBox(self.centralwidget)
        self.splitInventoryCheckBox.setChecked(True)
        self.splitInventoryCheckBox.setObjectName("splitInventoryCheckBox")
        self.mainGridLayout.addWidget(self.splitInventoryCheckBox, 2, 0, 1, 1)
        self.featureLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.featureLineEdit.setObjectName("featureLineEdit")
        self.mainGridLayout.addWidget(self.featureLineEdit, 1, 0, 1, 2)
        self.importFeatureLabel = QtWidgets.QLabel(self.centralwidget)
        self.importFeatureLabel.setObjectName("importFeatureLabel")
        self.mainGridLayout.addWidget(self.importFeatureLabel, 0, 0, 1, 1)
        self.testDatasetLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.testDatasetLineEdit.setObjectName("testDatasetLineEdit")
        self.mainGridLayout.addWidget(self.testDatasetLineEdit, 9, 0, 1, 2)
        self.trainingDatasetToolButton = QtWidgets.QToolButton(self.centralwidget)
        self.trainingDatasetToolButton.setObjectName("trainingDatasetToolButton")
        self.mainGridLayout.addWidget(self.trainingDatasetToolButton, 7, 2, 1, 1)
        self.trainingDatasetLabel = QtWidgets.QLabel(self.centralwidget)
        self.trainingDatasetLabel.setObjectName("trainingDatasetLabel")
        self.mainGridLayout.addWidget(self.trainingDatasetLabel, 6, 0, 1, 1)
        self.testDatasetLabel = QtWidgets.QLabel(self.centralwidget)
        self.testDatasetLabel.setObjectName("testDatasetLabel")
        self.mainGridLayout.addWidget(self.testDatasetLabel, 8, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mainGridLayout.addItem(spacerItem, 3, 2, 1, 1)
        self.testDatasetToolButton = QtWidgets.QToolButton(self.centralwidget)
        self.testDatasetToolButton.setObjectName("testDatasetToolButton")
        self.mainGridLayout.addWidget(self.testDatasetToolButton, 9, 2, 1, 1)
        self.featureToolButton = QtWidgets.QToolButton(self.centralwidget)
        self.featureToolButton.setObjectName("featureToolButton")
        self.mainGridLayout.addWidget(self.featureToolButton, 1, 2, 1, 1)
        self.trainingDatasetLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.trainingDatasetLineEdit.setObjectName("trainingDatasetLineEdit")
        self.mainGridLayout.addWidget(self.trainingDatasetLineEdit, 7, 0, 1, 2)
        self.applyPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.applyPushButton.setObjectName("applyPushButton")
        self.mainGridLayout.addWidget(self.applyPushButton, 10, 1, 1, 1)
        self.sizeValueLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.sizeValueLineEdit.setMaxLength(3)
        self.sizeValueLineEdit.setObjectName("sizeValueLineEdit")
        self.mainGridLayout.addWidget(self.sizeValueLineEdit, 4, 0, 1, 1)
        self.sizeValueHorizontalSlider = QtWidgets.QSlider(self.centralwidget)
        self.sizeValueHorizontalSlider.setMaximum(100)
        self.sizeValueHorizontalSlider.setSliderPosition(80)
        self.sizeValueHorizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.sizeValueHorizontalSlider.setInvertedAppearance(False)
        self.sizeValueHorizontalSlider.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.sizeValueHorizontalSlider.setTickInterval(10)
        self.sizeValueHorizontalSlider.setObjectName("sizeValueHorizontalSlider")
        self.mainGridLayout.addWidget(self.sizeValueHorizontalSlider, 5, 0, 1, 1)
        self.sizeOfTrainingDatatsetLabel = QtWidgets.QLabel(self.centralwidget)
        self.sizeOfTrainingDatatsetLabel.setObjectName("sizeOfTrainingDatatsetLabel")
        self.mainGridLayout.addWidget(self.sizeOfTrainingDatatsetLabel, 3, 0, 1, 1)
        self.RandomSeedlineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.RandomSeedlineEdit.setObjectName("RandomSeedlineEdit")
        self.mainGridLayout.addWidget(self.RandomSeedlineEdit, 4, 1, 1, 1)
        self.randomseedlabel = QtWidgets.QLabel(self.centralwidget)
        self.randomseedlabel.setObjectName("randomseedlabel")
        self.mainGridLayout.addWidget(self.randomseedlabel, 3, 1, 1, 1)
        self.mainGridLayout.setColumnStretch(0, 5)
        self.verticalLayout.addLayout(self.mainGridLayout)
        ImportInventory.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(ImportInventory)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 421, 21))
        self.menubar.setObjectName("menubar")
        ImportInventory.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(ImportInventory)
        self.statusbar.setObjectName("statusbar")
        ImportInventory.setStatusBar(self.statusbar)

        self.retranslateUi(ImportInventory)
        QtCore.QMetaObject.connectSlotsByName(ImportInventory)
        ImportInventory.setTabOrder(self.featureLineEdit, self.featureToolButton)
        ImportInventory.setTabOrder(self.featureToolButton, self.splitInventoryCheckBox)
        ImportInventory.setTabOrder(self.splitInventoryCheckBox, self.sizeValueLineEdit)
        ImportInventory.setTabOrder(self.sizeValueLineEdit, self.RandomSeedlineEdit)
        ImportInventory.setTabOrder(self.RandomSeedlineEdit, self.sizeValueHorizontalSlider)
        ImportInventory.setTabOrder(self.sizeValueHorizontalSlider, self.trainingDatasetLineEdit)
        ImportInventory.setTabOrder(self.trainingDatasetLineEdit, self.trainingDatasetToolButton)
        ImportInventory.setTabOrder(self.trainingDatasetToolButton, self.testDatasetLineEdit)
        ImportInventory.setTabOrder(self.testDatasetLineEdit, self.testDatasetToolButton)
        ImportInventory.setTabOrder(self.testDatasetToolButton, self.applyPushButton)

    def retranslateUi(self, ImportInventory):
        _translate = QtCore.QCoreApplication.translate
        ImportInventory.setWindowTitle(_translate("ImportInventory", "Import Inventory"))
        self.splitInventoryCheckBox.setText(_translate("ImportInventory", "Split inventory"))
        self.importFeatureLabel.setText(_translate("ImportInventory", "Import feature"))
        self.trainingDatasetToolButton.setText(_translate("ImportInventory", "..."))
        self.trainingDatasetLabel.setText(_translate("ImportInventory", "Training dataset"))
        self.testDatasetLabel.setText(_translate("ImportInventory", "Test dataset"))
        self.testDatasetToolButton.setText(_translate("ImportInventory", "..."))
        self.featureToolButton.setText(_translate("ImportInventory", "..."))
        self.applyPushButton.setText(_translate("ImportInventory", "Apply"))
        self.sizeOfTrainingDatatsetLabel.setText(_translate("ImportInventory", "Size of the training dataset in %:"))
        self.RandomSeedlineEdit.setToolTip(_translate("ImportInventory", "Leave empty to use random seed"))
        self.randomseedlabel.setText(_translate("ImportInventory", "Seed to initialize random"))
