# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Schuessler.N\Prog\Py\LSATGitHub\core\uis\Subsampling_ui\Subsampling.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_RandomSampling(object):
    def setupUi(self, RandomSampling):
        RandomSampling.setObjectName("RandomSampling")
        RandomSampling.resize(569, 555)
        self.centralwidget = QtWidgets.QWidget(RandomSampling)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.mainGridLayout = QtWidgets.QGridLayout()
        self.mainGridLayout.setObjectName("mainGridLayout")
        self.applyPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.applyPushButton.setObjectName("applyPushButton")
        self.mainGridLayout.addWidget(self.applyPushButton, 3, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mainGridLayout.addItem(spacerItem, 3, 0, 1, 1)
        self.outputGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.outputGroupBox.setObjectName("outputGroupBox")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.outputGroupBox)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.outputGroupBoxGridLayout = QtWidgets.QGridLayout()
        self.outputGroupBoxGridLayout.setObjectName("outputGroupBoxGridLayout")
        self.outputDirectoryLabel = QtWidgets.QLabel(self.outputGroupBox)
        self.outputDirectoryLabel.setObjectName("outputDirectoryLabel")
        self.outputGroupBoxGridLayout.addWidget(self.outputDirectoryLabel, 0, 0, 1, 1)
        self.nameOfTraininDatasetLineEdit = QtWidgets.QLineEdit(self.outputGroupBox)
        self.nameOfTraininDatasetLineEdit.setObjectName("nameOfTraininDatasetLineEdit")
        self.outputGroupBoxGridLayout.addWidget(self.nameOfTraininDatasetLineEdit, 3, 0, 1, 1)
        self.outputDirectoryToolButton = QtWidgets.QToolButton(self.outputGroupBox)
        self.outputDirectoryToolButton.setObjectName("outputDirectoryToolButton")
        self.outputGroupBoxGridLayout.addWidget(self.outputDirectoryToolButton, 1, 1, 1, 1)
        self.nameOfTrainingDatasetLabel = QtWidgets.QLabel(self.outputGroupBox)
        self.nameOfTrainingDatasetLabel.setObjectName("nameOfTrainingDatasetLabel")
        self.outputGroupBoxGridLayout.addWidget(self.nameOfTrainingDatasetLabel, 2, 0, 1, 1)
        self.outputDirectoryLineEdit = QtWidgets.QLineEdit(self.outputGroupBox)
        self.outputDirectoryLineEdit.setObjectName("outputDirectoryLineEdit")
        self.outputGroupBoxGridLayout.addWidget(self.outputDirectoryLineEdit, 1, 0, 1, 1)
        self.nameOfTestDatasetLabel = QtWidgets.QLabel(self.outputGroupBox)
        self.nameOfTestDatasetLabel.setObjectName("nameOfTestDatasetLabel")
        self.outputGroupBoxGridLayout.addWidget(self.nameOfTestDatasetLabel, 4, 0, 1, 1)
        self.nameOfTestDatasetLineEdit = QtWidgets.QLineEdit(self.outputGroupBox)
        self.nameOfTestDatasetLineEdit.setEnabled(False)
        self.nameOfTestDatasetLineEdit.setObjectName("nameOfTestDatasetLineEdit")
        self.outputGroupBoxGridLayout.addWidget(self.nameOfTestDatasetLineEdit, 5, 0, 1, 1)
        self.horizontalLayout_3.addLayout(self.outputGroupBoxGridLayout)
        self.mainGridLayout.addWidget(self.outputGroupBox, 2, 0, 1, 2)
        self.inputGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.inputGroupBox.setObjectName("inputGroupBox")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.inputGroupBox)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.inputGroupBoxGridLayout = QtWidgets.QGridLayout()
        self.inputGroupBoxGridLayout.setVerticalSpacing(6)
        self.inputGroupBoxGridLayout.setObjectName("inputGroupBoxGridLayout")
        self.numberOfSubsamplesLineEdit = QtWidgets.QLineEdit(self.inputGroupBox)
        self.numberOfSubsamplesLineEdit.setObjectName("numberOfSubsamplesLineEdit")
        self.inputGroupBoxGridLayout.addWidget(self.numberOfSubsamplesLineEdit, 4, 0, 1, 1)
        self.sizeTrainingLabel = QtWidgets.QLabel(self.inputGroupBox)
        self.sizeTrainingLabel.setObjectName("sizeTrainingLabel")
        self.inputGroupBoxGridLayout.addWidget(self.sizeTrainingLabel, 7, 0, 1, 1)
        self.numberOfSubsamplesLabel = QtWidgets.QLabel(self.inputGroupBox)
        self.numberOfSubsamplesLabel.setObjectName("numberOfSubsamplesLabel")
        self.inputGroupBoxGridLayout.addWidget(self.numberOfSubsamplesLabel, 2, 0, 1, 1)
        self.sizeTrainingLineEdit = QtWidgets.QLineEdit(self.inputGroupBox)
        self.sizeTrainingLineEdit.setObjectName("sizeTrainingLineEdit")
        self.inputGroupBoxGridLayout.addWidget(self.sizeTrainingLineEdit, 8, 0, 1, 1)
        self.keepTestCheckBox = QtWidgets.QCheckBox(self.inputGroupBox)
        self.keepTestCheckBox.setObjectName("keepTestCheckBox")
        self.inputGroupBoxGridLayout.addWidget(self.keepTestCheckBox, 8, 1, 1, 1)
        self.horizontalSlider = QtWidgets.QSlider(self.inputGroupBox)
        self.horizontalSlider.setMinimum(1)
        self.horizontalSlider.setMaximum(100)
        self.horizontalSlider.setPageStep(10)
        self.horizontalSlider.setProperty("value", 80)
        self.horizontalSlider.setSliderPosition(80)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.horizontalSlider.setTickInterval(20)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.inputGroupBoxGridLayout.addWidget(self.horizontalSlider, 9, 0, 1, 2)
        self.featureDatasetLabel = QtWidgets.QLabel(self.inputGroupBox)
        self.featureDatasetLabel.setObjectName("featureDatasetLabel")
        self.inputGroupBoxGridLayout.addWidget(self.featureDatasetLabel, 0, 0, 1, 1)
        self.RandomSeedLabel = QtWidgets.QLabel(self.inputGroupBox)
        self.RandomSeedLabel.setObjectName("RandomSeedLabel")
        self.inputGroupBoxGridLayout.addWidget(self.RandomSeedLabel, 5, 0, 1, 1)
        self.featureDatasetLineEdit = QtWidgets.QLineEdit(self.inputGroupBox)
        self.featureDatasetLineEdit.setObjectName("featureDatasetLineEdit")
        self.inputGroupBoxGridLayout.addWidget(self.featureDatasetLineEdit, 1, 0, 1, 2)
        self.featureDatasetToolButton = QtWidgets.QToolButton(self.inputGroupBox)
        self.featureDatasetToolButton.setObjectName("featureDatasetToolButton")
        self.inputGroupBoxGridLayout.addWidget(self.featureDatasetToolButton, 1, 2, 1, 1)
        self.RandomSeedLineEdit = QtWidgets.QLineEdit(self.inputGroupBox)
        self.RandomSeedLineEdit.setText("")
        self.RandomSeedLineEdit.setObjectName("RandomSeedLineEdit")
        self.inputGroupBoxGridLayout.addWidget(self.RandomSeedLineEdit, 6, 0, 1, 1)
        self.horizontalLayout_2.addLayout(self.inputGroupBoxGridLayout)
        self.mainGridLayout.addWidget(self.inputGroupBox, 0, 0, 1, 2)
        self.mainGridLayout.setColumnStretch(0, 3)
        self.mainGridLayout.setColumnStretch(1, 1)
        self.horizontalLayout.addLayout(self.mainGridLayout)
        RandomSampling.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(RandomSampling)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 569, 22))
        self.menubar.setObjectName("menubar")
        RandomSampling.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(RandomSampling)
        self.statusbar.setObjectName("statusbar")
        RandomSampling.setStatusBar(self.statusbar)

        self.retranslateUi(RandomSampling)
        QtCore.QMetaObject.connectSlotsByName(RandomSampling)
        RandomSampling.setTabOrder(self.featureDatasetLineEdit, self.featureDatasetToolButton)
        RandomSampling.setTabOrder(self.featureDatasetToolButton, self.numberOfSubsamplesLineEdit)
        RandomSampling.setTabOrder(self.numberOfSubsamplesLineEdit, self.RandomSeedLineEdit)
        RandomSampling.setTabOrder(self.RandomSeedLineEdit, self.sizeTrainingLineEdit)
        RandomSampling.setTabOrder(self.sizeTrainingLineEdit, self.keepTestCheckBox)
        RandomSampling.setTabOrder(self.keepTestCheckBox, self.horizontalSlider)
        RandomSampling.setTabOrder(self.horizontalSlider, self.outputDirectoryLineEdit)
        RandomSampling.setTabOrder(self.outputDirectoryLineEdit, self.outputDirectoryToolButton)
        RandomSampling.setTabOrder(self.outputDirectoryToolButton, self.nameOfTraininDatasetLineEdit)
        RandomSampling.setTabOrder(self.nameOfTraininDatasetLineEdit, self.nameOfTestDatasetLineEdit)
        RandomSampling.setTabOrder(self.nameOfTestDatasetLineEdit, self.applyPushButton)

    def retranslateUi(self, RandomSampling):
        _translate = QtCore.QCoreApplication.translate
        RandomSampling.setWindowTitle(_translate("RandomSampling", "Random Sampling"))
        self.applyPushButton.setText(_translate("RandomSampling", "Apply"))
        self.outputGroupBox.setTitle(_translate("RandomSampling", "Output"))
        self.outputDirectoryLabel.setText(_translate("RandomSampling", "Output Directory"))
        self.outputDirectoryToolButton.setText(_translate("RandomSampling", "..."))
        self.nameOfTrainingDatasetLabel.setText(_translate("RandomSampling", "Name of training dataset (without extension)"))
        self.nameOfTestDatasetLabel.setText(_translate("RandomSampling", "Name of test dataset (without extension)"))
        self.inputGroupBox.setTitle(_translate("RandomSampling", "Input"))
        self.numberOfSubsamplesLineEdit.setText(_translate("RandomSampling", "1"))
        self.sizeTrainingLabel.setText(_translate("RandomSampling", "Size of the training part in %"))
        self.numberOfSubsamplesLabel.setText(_translate("RandomSampling", "Number of subsamples"))
        self.sizeTrainingLineEdit.setText(_translate("RandomSampling", "80"))
        self.keepTestCheckBox.setText(_translate("RandomSampling", "Keep corresponding test part"))
        self.featureDatasetLabel.setText(_translate("RandomSampling", "Feature dataset"))
        self.RandomSeedLabel.setText(_translate("RandomSampling", "Seed to initialize random"))
        self.featureDatasetToolButton.setText(_translate("RandomSampling", "..."))
