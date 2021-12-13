# -*- coding: utf-8 -*-

from osgeo import gdal, ogr, osr, gdalconst
import os
import sys
import math
import time
import random
import logging

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *

from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog
from core.uis.ImportInventory_ui.ImportInventory_ui import Ui_ImportInventory
from core.libs.GDAL_Libs.Layers import Raster
from core.libs.LSAT_Messages.messages_main import Messenger
from core.libs.Analysis.Random_Sampling import RandomSampling
from core.widgets.GeoprocessingTools.geoprocessingTools_calc import GeoprocessingToolsWorker
import numpy as np


class ImportInventory(QMainWindow):
    def __init__(self, projectLocation, parent=None):
        QWidget.__init__(self, parent)
        # ui
        self.ui = Ui_ImportInventory()
        self.ui.setupUi(self)
        self.ui.sizeValueLineEdit.textChanged.connect(self.val_sizeValue)
        self.ui.sizeValueLineEdit.setText(str(self.ui.sizeValueHorizontalSlider.value()))
        self.setWindowIcon(QIcon(':/icons/Icons/ImportFeature.png'))
        self.progress = QProgressBar()
        self.statusBar().addPermanentWidget(self.progress)
        # connect
        self.fileDialog = CustomFileDialog()
        self.message = Messenger()
        self.projectLocation = projectLocation
        self.maskRaster = Raster(os.path.join(self.projectLocation, "region.tif"))
        self.srProject = osr.SpatialReference()
        if int(gdal.VersionInfo()) > 3000000:
            self.srProject.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        self.srProject.ImportFromEPSG(int(self.maskRaster.epsg))

    @pyqtSlot(int)
    def on_splitInventoryCheckBox_stateChanged(self):
        if self.ui.splitInventoryCheckBox.isChecked():
            self.ui.testDatasetLineEdit.setEnabled(True)
            self.ui.sizeValueHorizontalSlider.setEnabled(True)
            self.ui.testDatasetToolButton.setEnabled(True)
        else:
            self.ui.testDatasetLineEdit.setEnabled(False)
            self.ui.sizeValueHorizontalSlider.setEnabled(False)
            self.ui.sizeValueHorizontalSlider.setValue(100)
            self.ui.testDatasetToolButton.setEnabled(False)

    @pyqtSlot()
    def on_featureToolButton_clicked(self):
        """
        Sets input feature and sets the output files  with extension based on the input.
        """
        self.fileDialog.openFeatureFile(self.projectLocation)
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
            filename = self.fileDialog.selectedFiles()[0]
            trainingDir = os.path.join(self.projectLocation, "data", "inventory", "training")
            testDir = os.path.join(self.projectLocation, "data", "inventory", "test")
            ext = os.path.splitext(filename)[1]
            self.ui.trainingDatasetLineEdit.setText(
                os.path.join(trainingDir, "inventory_training" + ext))
            self.ui.testDatasetLineEdit.setText(os.path.join(testDir, 'inventory_test' + ext))
            self.ui.featureLineEdit.setText(os.path.normpath(filename))

    @pyqtSlot()
    def on_trainingDatasetToolButton_clicked(self):
        """
        Set the landslide feature class or shapefile
        """
        featureFile = self.saveFeatureFile()
        if featureFile:
            self.ui.trainingDatasetLineEdit.setText(featureFile)

    @pyqtSlot()
    def on_testDatasetToolButton_clicked(self):
        """
        Set the landslide feature class or shapefile
        """
        featureFile = self.saveFeatureFile()
        if featureFile:
            self.ui.testDatasetLineEdit.setText(featureFile)

    def saveFeatureFile(self):
        """
        Gets called by on_trainingDatasetToolButton_clicked and on_testDatasetToolButton_clicked.
        """
        self.fileDialog.saveFeatureFile(self.projectLocation)
        if self.fileDialog.exec_() == 1:
            return self.fileDialog.selectedFiles()[0]

    def on_sizeValueHorizontalSlider_valueChanged(self):
        self.ui.sizeValueLineEdit.setText(str(self.ui.sizeValueHorizontalSlider.value()))

    def on_sizeValueLineEdit_textChanged(self):
        try:
            self.ui.sizeValueHorizontalSlider.setValue(int(self.ui.sizeValueLineEdit.text()))
        except ValueError:
            pass

    @pyqtSlot()
    def on_applyPushButton_clicked(self):
        self.progress.setRange(0,0)
        outTraining = self.ui.trainingDatasetLineEdit.text()
        outTest = self.ui.testDatasetLineEdit.text()
        percent = self.ui.sizeValueHorizontalSlider.value()
        randomseed = self.ui.RandomSeedlineEdit.text()
        if not self.ui.featureLineEdit.text():
            self.message.WarningMissingInput()
            return
        else:
            featPath = self.ui.featureLineEdit.text()
        params = (outTraining, outTest, percent, randomseed)
        if self.ui.ignoreOutsideMaskCheckBox.isChecked():
            logging.info(self.tr("Clipping feature to region.shp"))
            featPath = self._clipBeforeImport(params)
            logging.info(self.tr("Clipped feature {} created").format(featPath))
        else:
            self.startImport(featPath, *params)

    def _clipBeforeImport(self, params: tuple) -> str:
        """
        Returns a string with the path to clipped file.
        Gets called by on_applyPushButton_clicked
        """
        region = os.path.join(self.projectLocation, "region.shp")
        inputFile = self.ui.featureLineEdit.text()
        clippedFile = os.path.join(self.projectLocation, "workspace", "clipped4import.shp")
        args = (0, ["SKIP_FAILURES=NO", "PROMOTE_TO_MULTI=NO"], True)
        # 0 -> clip function
        # "SKIP_FAILURES=NO" -> Don't skip failures, raise error.
        # "PROMOTE_TO_MULTI=NO" -> Keep feature as is.
        # True -> Use SpatialRef of region.shp
        self.thread = QThread()
        self.clip = GeoprocessingToolsWorker(inputFile, region, clippedFile, args)
        self.clip.moveToThread(self.thread)
        self.thread.started.connect(self.clip.run)
        self.clip.finishSignal.connect(lambda: self.startImport(clippedFile, *params))
        self.thread.start()
        return clippedFile

    @pyqtSlot()
    def startImport(self, featPath: str, outTrain: str, outTest: str, percent: int, seed: str):
        try:
            self.thread.exit() # Exit thread if we clipped the input
        except AttributeError:
            pass
        if seed != "":
            random.seed(seed)
        RandomSampling(featPath, outTrain, outTest, percent, self.srProject, i="")
        logging.info(
            self.tr("Successfully created {} - {}% of {}").format(outTrain, percent, featPath))
        if percent < 100:
            logging.info(self.tr("Successfully created {} - {}% of {}").format(outTest,
                         100 - percent, featPath))
        self.progress.setRange(0, 100)
        self.progress.setValue(100)

    def val_sizeValue(self):
        """
        Checks if the size of the training dataset is a number between 0 and 100.
        """
        try:
            lineedittocheck = self.sender()
            stringtocheck = lineedittocheck.text()
            if not stringtocheck.isdigit() or stringtocheck == "":
                lineedittocheck.backspace()
        except AttributeError:
            # If the QCheckbox calls this function we can not change its values.
            pass
