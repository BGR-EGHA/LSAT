# -*- coding: utf-8 -*-

import os
import sys
from osgeo import gdal, osr, ogr
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *

from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog
from core.libs.Analysis.Random_Sampling import RandomSampling
from core.libs.LSAT_Messages.messages_main import Messenger
from core.uis.Subsampling_ui.Subsampling_ui import Ui_RandomSampling
from core.libs.GDAL_Libs.Layers import Feature
import logging
import math
import random


class Subsampling(QMainWindow):
    def __init__(self, projectLocation="", parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_RandomSampling()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(':/icons/Icons/random_subset.png'))

        self.ui.sizeTrainingLineEdit.textChanged.connect(self.val_sizeValue)
        self.ui.numberOfSubsamplesLineEdit.textChanged.connect(self.val_sizeValue)
        self.progress = QProgressBar()
        self.ui.mainGridLayout.addWidget(self.progress)
        self.fileDialog = CustomFileDialog()
        self.message = Messenger()

        # We set the outputLineEdit to default
        self.projectLocation = projectLocation
        self.ui.outputDirectoryLineEdit.setText(os.path.join(projectLocation, "data", "inventory"))

    @pyqtSlot(int)
    def on_keepTestCheckBox_stateChanged(self):
        """
        This method controls the appearance of the GUI elements based on the state of the checkbox.
        :return: None
        """
        if self.ui.keepTestCheckBox.checkState() == False or self.ui.horizontalSlider.value() == 100:
            self.ui.nameOfTestDatasetLineEdit.setEnabled(False)
        else:
            self.ui.nameOfTestDatasetLineEdit.setEnabled(True)

    @pyqtSlot()
    def on_featureDatasetToolButton_clicked(self):
        """
        This method sets the path to the file containing inventory features
        that should be subsampled.
        :return: None
        """
        self.fileDialog.openFeatureFile(self.projectLocation)
        if self.fileDialog.exec_() == 1:
            for filename in self.fileDialog.selectedFiles():
                self.ui.featureDatasetLineEdit.setText(str(os.path.normpath(filename)))

    @pyqtSlot()
    def on_outputDirectoryToolButton_clicked(self):
        """
        This method sets the path to the output directory.
        Output directory is the directory in which the subsamples will be stored.
        :return: None
        """
        self.fileDialog.openDirectory(self.projectLocation)
        if self.fileDialog.exec_() == 1:
            for filename in self.fileDialog.selectedFiles():
                self.ui.outputDirectoryLineEdit.setText(str(os.path.normpath(filename)))
                self.ui.nameOfTraininDatasetLineEdit.setText("training")
                self.ui.nameOfTestDatasetLineEdit.setText("test")
            else:
                pass

    def on_horizontalSlider_valueChanged(self):
        """
        This method updates the line edit texts based on the values
        of the slider widget.
        :return: None
        """
        self.ui.sizeTrainingLineEdit.setText(str(self.ui.horizontalSlider.value()))
        if self.ui.horizontalSlider.value() == 100 or self.ui.keepTestCheckBox.checkState() == False:
            self.ui.nameOfTestDatasetLineEdit.setEnabled(False)
        else:
            self.ui.nameOfTestDatasetLineEdit.setEnabled(True)

    def on_sizeTrainingLineEdit_textChanged(self):
        """
        This class manages changes of the training size line edit.
        It updates the slider when a new value was entered.
        :return: None
        """
        if not self.ui.sizeTrainingLineEdit.text().isdigit():
            pass
        elif int(self.ui.sizeTrainingLineEdit.text()) > 100:
            self.ui.sizeTrainingLineEdit.setText("100")
        elif int(self.ui.sizeTrainingLineEdit.text()) <= 0:
            self.ui.sizeTrainingLineEdit.setText("0")
        else:
            self.ui.horizontalSlider.setValue(int(self.ui.sizeTrainingLineEdit.text()))

    @pyqtSlot()
    def on_applyPushButton_clicked(self):
        """
        This method controls the actions after the apply button was clicked.
        It checked the input values and return warnings if inputs are incomplete.
        After, it collects the input data and passes it to the analysis thread.
        :return: None
        """
        if str(self.ui.featureDatasetLineEdit.text()) == "":
            self.message.WarningMissingInput()
            return

        if str(self.ui.outputDirectoryLineEdit.text()) == "":
            self.message.WarningMissingInput()
            return

        self.progress.setRange(0, 100)
        self.featurePath = str(self.ui.featureDatasetLineEdit.text())
        self.numSubs = int(self.ui.numberOfSubsamplesLineEdit.text())
        self.directory = self.ui.outputDirectoryLineEdit.text()
        self.nameTraining = self.ui.nameOfTraininDatasetLineEdit.text()
        self.nameTest = self.ui.nameOfTestDatasetLineEdit.text()
        self.sizeTraining = int(self.ui.sizeTrainingLineEdit.text())
        self.keepTestPart = bool(self.ui.keepTestCheckBox.checkState())

        logging.info(self.tr("Subsampling started..."))

        self.thread = Thread(self.subsampling_func)
        self.thread.finishSignal.connect(self.done)
        self.thread.barValueSignal.connect(self.updateProgressBar)
        self.thread.start()

    def updateProgressBar(self, i):
        """
        Updates the progress bar based on the signal value
        received from thread process.
        :param i: int value
        :return: None
        """
        self.progress.setValue(i)

    def done(self):
        """
        This method manages the activities on receiving the finish signal from thread.
        It updates the logging info, trigger a message info box and closes the application.
        :return: None
        """
        logging.info(self.tr("Subsampling completed!"))
        self.close()

    def subsampling_func(self):
        self.feat = Feature(self.featurePath)
        self.featWkt = self.feat.spatialRefWkt
        self.sr = osr.SpatialReference()
        self.sr.ImportFromWkt(self.featWkt)
        self.ext = os.path.splitext(self.featurePath)[1].lower()
        barvalue = 0
        barvalue_fraction = float(100 / int(self.numSubs))
        randomseed = self.ui.RandomSeedLineEdit.text()
        if randomseed != "":
            random.seed(randomseed)
        for num in range(self.numSubs):
            RandomSampling(self.featurePath,
                           os.path.join(self.directory, f"{self.nameTraining}_{num}{self.ext}"),
                           os.path.join(self.directory, f"{self.nameTest}_{num}{self.ext}"),
                           percent=self.sizeTraining, srProject=self.sr, keepTest=self.keepTestPart)
            barvalue = math.ceil(barvalue + barvalue_fraction)
            self.thread.barValueSignal.emit(barvalue)

    def val_sizeValue(self):
        """
        Gets called when the user edits sizeTrainingLineEdit or numberOfSubsamplesLineEdit.
        Checks if number of subsamples and Size of training part is a number.
        """
        try:
            lineedittocheck = self.sender()
            stringtocheck = lineedittocheck.text()
            if not stringtocheck.isdigit() or stringtocheck == "":
                lineedittocheck.backspace()
        except AttributeError:
            # If an incompatible widget calls this function we can not change its values.
            pass


class Thread(QThread):
    """
    Thread instance, called whenever a new process is started.
    """
    barValueSignal = QtCore.pyqtSignal(int)
    finishSignal = QtCore.pyqtSignal()

    def __init__(self, function, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """
        Runs the received function in the thread. Emits a done
        signal when ready.
        :return: None
        """
        self.function(*self.args, **self.kwargs)
        self.finishSignal.emit()
        return
