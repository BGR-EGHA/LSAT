# -*- coding: utf-8 -*-

import sys
import os
import math
import numpy as np
from osgeo import gdal, gdalconst, ogr
import logging
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog
from core.libs.GDAL_Libs.Layers import Raster, Feature
from core.libs.LSAT_Messages.messages_main import Messenger
from core.uis.Geoprocessing_ui.EuclideanDistance_ui import Ui_EuclideanDistanceForm


class EuclideanDistance(QMainWindow):
    def __init__(self, projectLocation, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_EuclideanDistanceForm()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(':/icons/Icons/EuclideanDist.png'))
        self.setWindowTitle(self.tr("Euclidean Distance"))
        self.progress = QProgressBar()
        self.statusBar().addPermanentWidget(self.progress)
        self.message = Messenger()
        self.fileDialog = CustomFileDialog()
        self.projectLocation = projectLocation
        self.maskRasterPath = os.path.join(self.projectLocation, "region.tif")
        self.ui.maskRasterLineEdit.setText(self.maskRasterPath)
        self.paramsPath = os.path.join(self.projectLocation, "params")

    @pyqtSlot()
    def on_inputFeatureToolButton_clicked(self):
        """
        This method sets the path to the landslide shapefile.
        :return: None
        """
        self.fileDialog.openFeatureFile(self.projectLocation)
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
            self.ui.inputFeatureLineEdit.setText(
                os.path.normpath(self.fileDialog.selectedFiles()[0]))

    @pyqtSlot()
    def on_outRasterToolButton_clicked(self):
        """
        This method sets the location and path of the output raster dataset.
        :return: None
        """
        self.fileDialog.saveRasterFile(self.projectLocation)
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
            outputfile = os.path.normpath(self.fileDialog.selectedFiles()[0])
            if outputfile.lower().endswith(".tif"):
                self.ui.outRasterLineEdit.setText(outputfile)
            else:
                self.ui.outRasterLineEdit.setText(outputfile + ".tif")

    @pyqtSlot()
    def on_maskRasterToolButton_clicked(self):
        """
        This method sets the mask raster dataset.
        :return: None
        """
        self.fileDialog.openRasterFile(self.projectLocation)
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
            self.ui.maskRasterLineEdit.setText(os.path.normpath(self.fileDialog.selectedFiles()[0]))

    @pyqtSlot(bool)
    def on_maskRastercheckBox_clicked(self, state: bool) -> None:
        """
        We only allow the User to change the mask raster if he really wants to do it. If he
        decides against it and checks the Checkbox we reset the lineEdit to its defaults
        (region.tif).
        """
        self.ui.maskRasterLineEdit.setEnabled(not(state))
        self.ui.maskRasterToolButton.setEnabled(not(state))
        if state:
            self.ui.maskRasterLineEdit.setText(self.maskRasterPath)

    @pyqtSlot()
    def on_applyPushButton_clicked(self):
        if not all((os.path.isfile(self.ui.maskRasterLineEdit.text()),
                    self.ui.outRasterLineEdit.text() != "",
                    os.path.isfile(self.ui.inputFeatureLineEdit.text()))):
            self.message.WarningMissingInput()
            return
        self.ui.applyPushButton.setEnabled(False)
        self.progress.setRange(0, 0)
        options = ['DISTUNITS=GEO']
        if self.ui.maximumDistanceLineEdit.text():
            options.append(f'MAXDIST={self.ui.maximumDistanceLineEdit.text()}')
        if self.ui.fixedBufferValueLineEdit.text():
            options.append(f'FIXED_BUF_VAL={self.ui.fixedBufferValueLineEdit.text()}')
        self.featurePath = self.ui.inputFeatureLineEdit.text()
        self.outRasterPath = self.ui.outRasterLineEdit.text()
        self.maskRasterPath = self.ui.maskRasterLineEdit.text()
        args = (
            self.featurePath,
            self.outRasterPath,
            self.maskRasterPath,
            self.projectLocation,
            options,
            self.ui.ignoreOutsideCheckBox.isChecked())
        self.calcEuclideanDistance = EuclideanDistanceAnalysis(args)
        self.thread = QThread()
        self.calcEuclideanDistance.moveToThread(self.thread)
        self.calcEuclideanDistance.finishSignal.connect(self.done)
        self.calcEuclideanDistance.updateLoggerSignal.connect(self.updateLogger)
        self.thread.started.connect(self.calcEuclideanDistance.calcDistance)
        self.thread.start()

    def done(self):
        self.thread.quit()
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.message.getLoggingInfoOnAnalysisCompleted()
        self.ui.applyPushButton.setEnabled(True)

    def updateLogger(self, message):
        logging.info(message)


class EuclideanDistanceAnalysis(QObject):
    finishSignal = pyqtSignal()
    updateLoggerSignal = pyqtSignal(str)

    def __init__(self, args):
        QObject.__init__(self)
        self.featurePath, self.outRasterPath, self.maskRasterPath, self.projectLocation, self.options, self.ignoreOutsideMask = args

    def calcDistance(self):
        """
        This method computes the Euclidean distance to a feature in geographics units of the data projection.
        The analysis extent must be given by a mask raster dataset.
        :return: None
        """
        self.updateLoggerSignal.emit(self.tr("Start euclidean distance analysis..."))
        feat = Feature(self.featurePath)
        maskRaster = Raster(self.maskRasterPath)
        if not self.checkiffeatinmask(feat, maskRaster):
            self.updateLoggerSignal.emit(
                self.tr("Input Feature is at least partially not inside the mask."))
            if self.ignoreOutsideMask:
                self.updateLoggerSignal.emit(self.tr("Ignoring feature outside the mask."))
            else:
                # We need to create a temporary mask raster. So we stretch the ordinary
                # one to fit the feature
                tmpMaskPath = os.path.join(self.projectLocation, "workspace", "TmpMask.tif")
                maskRaster = self.createTmpMask(
                    self.featurePath,
                    maskRaster.cellsize[0],
                    maskRaster.nodata,
                    tmpMaskPath,
                    maskRaster.proj,
                    maskRaster.extent)
                self.updateLoggerSignal.emit(self.tr("Mask expanded to include the feature."))

        noDataValue = -9999
        driver = gdal.GetDriverByName('MEM')
        featRaster = driver.Create('', maskRaster.cols, maskRaster.rows, 1, gdal.GDT_Byte)
        featRaster.SetProjection(maskRaster.proj)
        featRaster.SetGeoTransform(maskRaster.geoTrans)
        featRasterBand = featRaster.GetRasterBand(1)
        featRasterBand.SetNoDataValue(noDataValue)
        gdal.RasterizeLayer(featRaster, [1], feat.layer, burn_values=[1])
        driver = gdal.GetDriverByName('GTiff')
        euclidean = driver.Create(
            self.outRasterPath,
            maskRaster.cols,
            maskRaster.rows,
            1,
            gdal.GDT_Float32)
        euclidean.SetProjection(maskRaster.proj)
        euclidean.SetGeoTransform(maskRaster.geoTrans)
        euclideanBand = euclidean.GetRasterBand(1)
        euclideanBand.SetNoDataValue(noDataValue)
        gdal.ComputeProximity(featRasterBand, euclideanBand, self.options, callback=None)
        euclideanBand.ComputeStatistics(False)
        featRaster = None
        euclidean = None
        maskRaster = None
        # If necessary we delete the temporary raster file created by createTmpMask
        try:
            tmpMaskPath
        except NameError:
            pass
        else:
            os.remove(tmpMaskPath)
            os.remove(tmpMaskPath + ".aux.xml")
        self.finishSignal.emit()

    def checkiffeatinmask(self, feat, maskRaster) -> bool:
        """
        This functions returns True if the feat is completly inside the maskRaster, else it returns False.
        """
        mask_x_min = maskRaster.extent[0]
        mask_x_max = maskRaster.extent[1]
        mask_y_min = maskRaster.extent[2]
        mask_y_max = maskRaster.extent[3]
        feat_x_min = feat.extent[0]
        feat_x_max = feat.extent[1]
        feat_y_min = feat.extent[2]
        feat_y_max = feat.extent[3]
        check = all((mask_x_min <= feat_x_min,
                     mask_x_max >= feat_x_max,
                     mask_y_min <= feat_y_min,
                     mask_y_max >= mask_y_max))
        return check

    def createTmpMask(self, featPath: str, pixelSize: float, noData: float,
                      tmpRasterPath: str, maskProjection: str, maskExtent: list) -> object:
        """
        Gets called by calcDistance if the feature does not fit into the original mask and the 
        user did not check ignoreOutsideCheckBox.
        Creates a new mask raster similiar to the original but extended to fit the feature.
        The created raster will be bigger than the original mask, but during a later import it will
        be trimmed down.
        Returns a Handle to the tmpRasterPath created in workspace
        """
        # we take the smallest possible extent that fits the feature AND the mask
        featHandle = ogr.Open(featPath)
        featLayer = featHandle.GetLayer()
        xMinFeat, xMaxFeat, yMinFeat, yMaxFeat = featLayer.GetExtent()
        xMin = min(xMinFeat, maskExtent[0])
        xMax = max(xMaxFeat, maskExtent[1])
        yMin = min(yMinFeat, maskExtent[2])
        yMax = max(yMaxFeat, maskExtent[3])
        # max - min % pixelsize > 0 rounds up and catches featurepaths on the edge
        xRes = int(((xMax - xMin) / pixelSize) + ((xMax - xMin) % pixelSize > 0))
        yRes = int(((yMax - yMin) / pixelSize) + ((yMax - yMin) % pixelSize > 0))
        # we create the raster with information from the maskRaster to make import easier
        raster = gdal.GetDriverByName('GTiff').Create(tmpRasterPath, xRes, yRes, 1, gdal.GDT_Int16)
        raster.SetGeoTransform((xMin, pixelSize, 0, yMax, 0, -pixelSize))
        raster.SetProjection(maskProjection)
        band = raster.GetRasterBand(1)
        band.ComputeStatistics(False)
        band.SetNoDataValue(noData)
        gdal.RasterizeLayer(raster, [1], featLayer, burn_values=[1])
        raster = None
        return Raster(tmpRasterPath)
