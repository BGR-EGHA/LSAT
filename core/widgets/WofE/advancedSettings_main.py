# -*- coding: utf-8 -*-

import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from core.uis.WofE_ui.AdvancedSettings_ui import Ui_AdvancedSettings
from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog


class AdvancedSettings(QMainWindow):
    def __init__(self, projectLocation=None, parent=None):
        QMainWindow.__init__(self, parent)
        self.parent = parent
        self.ui = Ui_AdvancedSettings()
        self.ui.setupUi(self)

        self.projectLocation = projectLocation
        self.fileDialog = CustomFileDialog()
        validatorInt = QIntValidator()
        self.ui.sampleSizeLineEdit.setText(str(self.ui.sampleSizeSlider.value()))
        self.ui.sampleSizeLineEdit.textEdited.connect(self.on_sampleSizeLineEdit_textEdited)
        self.ui.sampleSizeLineEdit.setValidator(validatorInt)
        self.setWindowIcon(QIcon(':/icons/Icons/Settings.png'))

    def on_sampleSizeSlider_valueChanged(self):
        self.ui.sampleSizeLineEdit.setText(str(self.ui.sampleSizeSlider.value()))
        if self.ui.sampleSizeSlider.value() == 100:
            self.ui.onTheFlySubsamplingCheckBox.setChecked(False)
            self.ui.numberResamplesSpinBox.setValue(1)

    def on_okPushButton_clicked(self):
        self.close()

    def on_sampleSizeLineEdit_textEdited(self):
        """
        This function manages changes of the training size line edit.
        It updates the slider when a new value was entered.
        :return: None
        """
        if (self.ui.sampleSizeLineEdit.text() == "" or
            not self.ui.sampleSizeLineEdit.text().isdigit()):
            pass
        elif int(self.ui.sampleSizeLineEdit.text()) > 100:
            self.ui.sampleSizeLineEdit.setText("100")
        elif int(self.ui.sampleSizeLineEdit.text()) <= 0:
            self.ui.sampleSizeLineEdit.setText("0")
        else:
            self.ui.sampleSizeSlider.setValue(int(self.ui.sampleSizeLineEdit.text()))

    @pyqtSlot()
    def on_subsamplesLocationToolButton_clicked(self):
        self.fileDialog.openDirectory(self.projectLocation)
        if self.fileDialog.exec_() == 1:
            for filename in self.fileDialog.selectedFiles():
                self.ui.subsamplesLocationLineEdit.setText(str(filename))
                if os.path.exists(filename):
                    count = 0
                    for datafile in os.listdir(str(filename)):
                        if datafile.lower().endswith(".shp"):
                            count += 1
                    self.numberSubsamples = count
                    self.ui.numberResamplesSpinBox.setValue(count)

    @pyqtSlot(int)
    def on_onTheFlySubsamplingCheckBox_stateChanged(self):
        if self.ui.onTheFlySubsamplingCheckBox.checkState() == 2:
            self.ui.sampleSizeSlider.setValue(80)
            self.ui.sampleSizeLineEdit.setText("80")
            self.ui.randomSeedLineEdit.setEnabled(True)
            self.ui.subsamplesLocationLineEdit.setEnabled(False)
            self.ui.subsamplesLocationToolButton.setEnabled(False)
            self.ui.predefinedSubsamplingCheckBox.setChecked(False)
            self.ui.trainingSampleNameLineEdit.setEnabled(True)
            self.ui.testSampleNameLineEdit.setEnabled(True)
            self.ui.sampleSizeSlider.setEnabled(True)
            self.ui.sampleSizeLineEdit.setEnabled(True)
            self.ui.numberResamplesSpinBox.setEnabled(True)
        else:
            if self.ui.onTheFlySubsamplingCheckBox.checkState(
            ) == 0 and self.ui.predefinedSubsamplingCheckBox.checkState() == 0:
                self.ui.sampleSizeSlider.setValue(100)
                self.ui.sampleSizeSlider.setEnabled(False)
                self.ui.sampleSizeLineEdit.setEnabled(False)
                self.ui.randomSeedLineEdit.setEnabled(False)
                self.ui.numberResamplesSpinBox.setEnabled(False)
                self.ui.subsamplesLocationLineEdit.setEnabled(False)
                self.ui.subsamplesLocationToolButton.setEnabled(False)
                self.ui.trainingSampleNameLineEdit.setEnabled(False)
                self.ui.testSampleNameLineEdit.setEnabled(False)

    @pyqtSlot(int)
    def on_predefinedSubsamplingCheckBox_stateChanged(self):
        if self.ui.predefinedSubsamplingCheckBox.checkState() == 2:
            self.ui.sampleSizeSlider.setValue(100)
            self.ui.subsamplesLocationLineEdit.setEnabled(True)
            self.ui.subsamplesLocationToolButton.setEnabled(True)
            self.ui.onTheFlySubsamplingCheckBox.setChecked(False)
            self.ui.trainingSampleNameLineEdit.setEnabled(False)
            self.ui.testSampleNameLineEdit.setEnabled(False)
            self.ui.sampleSizeSlider.setEnabled(False)
            self.ui.sampleSizeLineEdit.setEnabled(False)
            self.ui.numberResamplesSpinBox.setEnabled(False)
            self.ui.randomSeedLineEdit.setEnabled(False)
        else:
            if self.ui.onTheFlySubsamplingCheckBox.checkState(
            ) == 0 and self.ui.predefinedSubsamplingCheckBox.checkState() == 0:
                self.ui.sampleSizeSlider.setValue(100)
                self.ui.sampleSizeSlider.setEnabled(False)
                self.ui.sampleSizeLineEdit.setEnabled(False)
                self.ui.numberResamplesSpinBox.setEnabled(False)
                self.ui.subsamplesLocationLineEdit.setEnabled(False)
                self.ui.subsamplesLocationToolButton.setEnabled(False)
                self.ui.trainingSampleNameLineEdit.setEnabled(False)
                self.ui.testSampleNameLineEdit.setEnabled(False)
