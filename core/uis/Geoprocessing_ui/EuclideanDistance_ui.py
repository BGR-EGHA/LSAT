# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\EuclideanDistance.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_EuclideanDistanceForm(object):
    def setupUi(self, EuclideanDistanceForm):
        EuclideanDistanceForm.setObjectName("EuclideanDistanceForm")
        EuclideanDistanceForm.resize(540, 400)
        self.centralwidget = QtWidgets.QWidget(EuclideanDistanceForm)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.mainGridLayout = QtWidgets.QGridLayout()
        self.mainGridLayout.setObjectName("mainGridLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.mainGridLayout.addItem(spacerItem, 3, 0, 1, 1)
        self.outRasterGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.outRasterGroupBox.setObjectName("outRasterGroupBox")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.outRasterGroupBox)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.outRasterGroupBoxGridLayout = QtWidgets.QGridLayout()
        self.outRasterGroupBoxGridLayout.setObjectName("outRasterGroupBoxGridLayout")
        self.outRasterToolButton = QtWidgets.QToolButton(self.outRasterGroupBox)
        self.outRasterToolButton.setObjectName("outRasterToolButton")
        self.outRasterGroupBoxGridLayout.addWidget(self.outRasterToolButton, 0, 1, 1, 1)
        self.outRasterLineEdit = QtWidgets.QLineEdit(self.outRasterGroupBox)
        self.outRasterLineEdit.setObjectName("outRasterLineEdit")
        self.outRasterGroupBoxGridLayout.addWidget(self.outRasterLineEdit, 0, 0, 1, 1)
        self.horizontalLayout_2.addLayout(self.outRasterGroupBoxGridLayout)
        self.mainGridLayout.addWidget(self.outRasterGroupBox, 2, 0, 1, 2)
        self.inputDataGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.inputDataGroupBox.setObjectName("inputDataGroupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.inputDataGroupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.inputDataGroupBoxGridLayout = QtWidgets.QGridLayout()
        self.inputDataGroupBoxGridLayout.setObjectName("inputDataGroupBoxGridLayout")
        self.maskRastercheckBox = QtWidgets.QCheckBox(self.inputDataGroupBox)
        self.maskRastercheckBox.setChecked(True)
        self.maskRastercheckBox.setObjectName("maskRastercheckBox")
        self.inputDataGroupBoxGridLayout.addWidget(self.maskRastercheckBox, 3, 1, 1, 1)
        self.inputFeatureToolButton = QtWidgets.QToolButton(self.inputDataGroupBox)
        self.inputFeatureToolButton.setObjectName("inputFeatureToolButton")
        self.inputDataGroupBoxGridLayout.addWidget(self.inputFeatureToolButton, 1, 3, 1, 1)
        self.label = QtWidgets.QLabel(self.inputDataGroupBox)
        self.label.setObjectName("label")
        self.inputDataGroupBoxGridLayout.addWidget(self.label, 3, 0, 1, 1)
        self.maskRasterToolButton = QtWidgets.QToolButton(self.inputDataGroupBox)
        self.maskRasterToolButton.setEnabled(False)
        self.maskRasterToolButton.setObjectName("maskRasterToolButton")
        self.inputDataGroupBoxGridLayout.addWidget(self.maskRasterToolButton, 4, 3, 1, 1)
        self.inputFeatureLineEdit = QtWidgets.QLineEdit(self.inputDataGroupBox)
        self.inputFeatureLineEdit.setObjectName("inputFeatureLineEdit")
        self.inputDataGroupBoxGridLayout.addWidget(self.inputFeatureLineEdit, 1, 0, 1, 2)
        self.inputFeatureDatasetLabel = QtWidgets.QLabel(self.inputDataGroupBox)
        self.inputFeatureDatasetLabel.setObjectName("inputFeatureDatasetLabel")
        self.inputDataGroupBoxGridLayout.addWidget(self.inputFeatureDatasetLabel, 0, 0, 1, 1)
        self.ignoreOutsideCheckBox = QtWidgets.QCheckBox(self.inputDataGroupBox)
        self.ignoreOutsideCheckBox.setObjectName("ignoreOutsideCheckBox")
        self.inputDataGroupBoxGridLayout.addWidget(self.ignoreOutsideCheckBox, 3, 2, 1, 1)
        self.maskRasterLineEdit = QtWidgets.QLineEdit(self.inputDataGroupBox)
        self.maskRasterLineEdit.setEnabled(False)
        self.maskRasterLineEdit.setObjectName("maskRasterLineEdit")
        self.inputDataGroupBoxGridLayout.addWidget(self.maskRasterLineEdit, 4, 0, 1, 3)
        self.horizontalLayout.addLayout(self.inputDataGroupBoxGridLayout)
        self.mainGridLayout.addWidget(self.inputDataGroupBox, 0, 0, 1, 2)
        self.applyPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.applyPushButton.setObjectName("applyPushButton")
        self.mainGridLayout.addWidget(self.applyPushButton, 3, 1, 1, 1)
        self.optionalSettingsGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.optionalSettingsGroupBox.setObjectName("optionalSettingsGroupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.optionalSettingsGroupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.optionalSettingsGroupBoxGridLayout = QtWidgets.QGridLayout()
        self.optionalSettingsGroupBoxGridLayout.setObjectName("optionalSettingsGroupBoxGridLayout")
        self.fixedBufferValueLabel = QtWidgets.QLabel(self.optionalSettingsGroupBox)
        self.fixedBufferValueLabel.setObjectName("fixedBufferValueLabel")
        self.optionalSettingsGroupBoxGridLayout.addWidget(self.fixedBufferValueLabel, 2, 0, 1, 1)
        self.maximumDistanceLabel = QtWidgets.QLabel(self.optionalSettingsGroupBox)
        self.maximumDistanceLabel.setObjectName("maximumDistanceLabel")
        self.optionalSettingsGroupBoxGridLayout.addWidget(self.maximumDistanceLabel, 0, 0, 1, 1)
        self.maximumDistanceLineEdit = QtWidgets.QLineEdit(self.optionalSettingsGroupBox)
        self.maximumDistanceLineEdit.setObjectName("maximumDistanceLineEdit")
        self.optionalSettingsGroupBoxGridLayout.addWidget(self.maximumDistanceLineEdit, 1, 0, 1, 1)
        self.fixedBufferValueLineEdit = QtWidgets.QLineEdit(self.optionalSettingsGroupBox)
        self.fixedBufferValueLineEdit.setObjectName("fixedBufferValueLineEdit")
        self.optionalSettingsGroupBoxGridLayout.addWidget(self.fixedBufferValueLineEdit, 3, 0, 1, 1)
        self.verticalLayout_2.addLayout(self.optionalSettingsGroupBoxGridLayout)
        self.mainGridLayout.addWidget(self.optionalSettingsGroupBox, 1, 0, 1, 2)
        self.verticalLayout.addLayout(self.mainGridLayout)
        EuclideanDistanceForm.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(EuclideanDistanceForm)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 540, 18))
        self.menubar.setObjectName("menubar")
        EuclideanDistanceForm.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(EuclideanDistanceForm)
        self.statusbar.setObjectName("statusbar")
        EuclideanDistanceForm.setStatusBar(self.statusbar)

        self.retranslateUi(EuclideanDistanceForm)
        QtCore.QMetaObject.connectSlotsByName(EuclideanDistanceForm)
        EuclideanDistanceForm.setTabOrder(self.inputFeatureLineEdit, self.inputFeatureToolButton)
        EuclideanDistanceForm.setTabOrder(self.inputFeatureToolButton, self.maskRastercheckBox)
        EuclideanDistanceForm.setTabOrder(self.maskRastercheckBox, self.maskRasterLineEdit)
        EuclideanDistanceForm.setTabOrder(self.maskRasterLineEdit, self.maskRasterToolButton)
        EuclideanDistanceForm.setTabOrder(self.maskRasterToolButton, self.maximumDistanceLineEdit)
        EuclideanDistanceForm.setTabOrder(self.maximumDistanceLineEdit, self.fixedBufferValueLineEdit)
        EuclideanDistanceForm.setTabOrder(self.fixedBufferValueLineEdit, self.outRasterLineEdit)
        EuclideanDistanceForm.setTabOrder(self.outRasterLineEdit, self.outRasterToolButton)
        EuclideanDistanceForm.setTabOrder(self.outRasterToolButton, self.applyPushButton)

    def retranslateUi(self, EuclideanDistanceForm):
        _translate = QtCore.QCoreApplication.translate
        EuclideanDistanceForm.setWindowTitle(_translate("EuclideanDistanceForm", "Euklidean distance"))
        self.outRasterGroupBox.setTitle(_translate("EuclideanDistanceForm", "Output distance raster"))
        self.outRasterToolButton.setText(_translate("EuclideanDistanceForm", "..."))
        self.inputDataGroupBox.setTitle(_translate("EuclideanDistanceForm", "Input data"))
        self.maskRastercheckBox.setText(_translate("EuclideanDistanceForm", "Use the Projects default Mask raster"))
        self.inputFeatureToolButton.setText(_translate("EuclideanDistanceForm", "..."))
        self.label.setText(_translate("EuclideanDistanceForm", "Mask raster"))
        self.maskRasterToolButton.setText(_translate("EuclideanDistanceForm", "..."))
        self.inputFeatureDatasetLabel.setText(_translate("EuclideanDistanceForm", "Input feature dataset"))
        self.ignoreOutsideCheckBox.setText(_translate("EuclideanDistanceForm", "Ignore feature outside mask raster"))
        self.applyPushButton.setText(_translate("EuclideanDistanceForm", "Apply"))
        self.optionalSettingsGroupBox.setTitle(_translate("EuclideanDistanceForm", "Optional settings"))
        self.fixedBufferValueLabel.setText(_translate("EuclideanDistanceForm", "Fixed buffer value"))
        self.maximumDistanceLabel.setText(_translate("EuclideanDistanceForm", "Maximum distance"))
        self.maximumDistanceLineEdit.setToolTip(_translate("EuclideanDistanceForm", "The maximum distance to be generated. The nodata value will be used for pixels beyond this distance. "))
        self.fixedBufferValueLineEdit.setToolTip(_translate("EuclideanDistanceForm", "Specify a value to be applied to all pixels that are within the -maxdist of target pixels (including the target pixels) instead of a distance value"))
