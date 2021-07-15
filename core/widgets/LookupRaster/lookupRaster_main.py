# -*- coding: utf-8 -*-

from osgeo import gdal, ogr, osr, gdalconst
import os
import math
import time
import numpy as np

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *
import sys
import os
import logging
from core.libs.LSAT_Messages.messages_main import Messenger
from core.libs.GDAL_Libs.Layers import Feature, Raster
from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog as FileDialog
from core.uis.LookupRaster_ui.LookupRaster_ui import Ui_LookupRaster


class LookupRaster(QMainWindow):
    def __init__(self, projectLocation="", parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_LookupRaster()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(':/icons/Icons/lookup.png'))
        self.ui.progress = QProgressBar()
        self.ui.progress.setTextVisible(False)
        self.ui.statusbar.addPermanentWidget(self.ui.progress)
        self.message = Messenger()
        self.fileDialog = FileDialog()
        self.projectLocation = projectLocation

    @pyqtSlot()
    def on_rasterToolButton_clicked(self):
        """
        Adds a raster path to the raster combo box.
        :return: None
        """
        self.fileDialog.openRasterFile(self.projectLocation)
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
            filename = os.path.normpath(self.fileDialog.selectedFiles()[0])
            if self.loadRaster(filename):
                self.ui.rasterComboBox.addItem(filename)
                index = self.ui.rasterComboBox.findText(filename)
                self.ui.rasterComboBox.setCurrentIndex(index)

    @pyqtSlot()
    def on_outRasterToolButton_clicked(self):
        """
        Passes a output path from FileDialog to output line edit.
        :return: None
        """
        self.fileDialog.saveRasterFile(self.projectLocation)
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
            filename = os.path.normpath(self.fileDialog.selectedFiles()[0])
            if not filename.lower().endswith(".tif"):
                filename += ".tif"
            self.ui.outRasterLineEdit.setText(filename)

    @pyqtSlot(int)
    def on_rasterComboBox_activated(self):
        """
        Updates the field list any time the raster combobox is activated.
        :return: None
        """
        self.loadRaster(self.ui.rasterComboBox.currentText())

    def loadRaster(self, rasterPath):
        """
        Reads the raster data and populates the field combo box.
        :param rasterPath: str raster path
        :return: None
        """
        self.raster = Raster(rasterPath)
        self.rat = self.raster.band.GetDefaultRAT()
        if self.rat is None:
            logging.info(self.tr("No RAT detected. Lookup not possible."))
            return False
        self.table = self.rat2array()
        fields = []
        self.ui.lookupFieldComboBox.clear()
        for elem in self.columns:
            if elem[1] != "U100":
                fields.append(str(elem[0]))
        self.ui.lookupFieldComboBox.addItems(fields)
        return True

    def rat2array(self):
        """
        Reads a raster attribute table(rat) to numpy array
        :return: ndarray - structured numpy array
        """
        self.columns = []
        dtype = {0: 'int', 1: 'float', 2: 'U100'}
        for i in range(self.rat.GetColumnCount()):
            self.columns.append((str(self.rat.GetNameOfCol(i)).upper(),
                                str(dtype[self.rat.GetTypeOfCol(i)])))
        self.colNames = self.getColNames()
        table = np.zeros(shape=[self.rat.GetRowCount(), ], dtype=self.columns)
        for i in range(len(self.colNames)):
            array = self.rat.ReadAsArray(i).tolist()
            for row, element in enumerate(array):
                if self.columns[i][1] == "U100":
                    try:
                        table[row][i] = str(element, "utf8")
                    except BaseException:
                        table[row][i] = str(element, "cp1252")
                else:
                    table[row][i] = element
        return table

    def getColNames(self):
        """
        Return a list with column names of the raster attribute table
        :return: list with column names
        """
        names = []
        for i in range(self.rat.GetColumnCount()):
            names.append(str(self.rat.GetNameOfCol(i)))
        return names

    def createLookupRAT(self, rasterPath):
        """
        Generates a lookup attribute table and attaches it to output Raster.
        :param rasterPath: string raster path
        :return: None
        """

        names_and_dtypes = [list(elem) for elem in self.columns]

        # adjust type for value field
        names_and_dtypes[self.old_value_idx][1] = names_and_dtypes[self.new_value_idx][1]

        for elem in self.lookupTable:
            elem[self.old_value_idx] = self.lut[elem[self.old_value_idx]]

        # remove the lookup field since it will be the value field
        for elem in self.lookupTable:
            elem.pop(self.new_value_idx)
        names_and_dtypes.pop(self.new_value_idx)
        rat = gdal.RasterAttributeTable()

        for column in names_and_dtypes:
            if 'int' in str(column[1]):
                DTYPE = gdal.GFT_Integer
            elif 'float' in str(column[1]):
                DTYPE = gdal.GFT_Real
            elif 'U100' in str(column[1]):
                DTYPE = gdal.GFT_String
            else:
                pass
            rat.CreateColumn(str(column[0]), DTYPE, gdalconst.GFU_MinMax)

        for col in range(len(names_and_dtypes)):
            colType = rat.GetTypeOfCol(col)
            for row in range(len(self.lookupTable)):
                if colType == 0:
                    rat.SetValueAsInt(int(row), int(col), int(self.lookupTable[row][col]))
                elif colType == 1:
                    rat.SetValueAsDouble(row, col, self.lookupTable[row][col])
                elif colType == 2:
                    rat.SetValueAsString(row, col, self.lookupTable[row][col])
        raster = Raster(str(rasterPath))
        raster.band.SetDefaultRAT(rat)
        raster = None

    @pyqtSlot()
    def on_cancelPushButton_clicked(self):
        self.close()

    @pyqtSlot()
    def on_applyPushButton_clicked(self):
        if not self.ui.lookupFieldComboBox.currentText() or not self.ui.lookupFieldComboBox.currentText():
            self.message.WarningMissingInput()
            return
        outRasterPath = self.ui.outRasterLineEdit.text()
        if outRasterPath == "":
            self.message.WarningMissingInput()
            return
        self._updateProgress(True)
        self.fieldNames = []
        for name in self.colNames:
            self.fieldNames.append(str(name).upper())
        self.old_value_idx = self.fieldNames.index("VALUE")
        self.new_value_idx = self.fieldNames.index(str(self.ui.lookupFieldComboBox.currentText()))
        self.lookupTable = [list(elem) for elem in self.table.tolist()]
        # lookup table as dictionary
        self.lut = {}
        for i in range(len(self.table)):
            self.lut[self.lookupTable[i][self.old_value_idx]
                     ] = self.lookupTable[i][self.new_value_idx]

        NoData_value = -9999.0
        driver = gdal.GetDriverByName('GTiff')
        if self.columns[self.new_value_idx][1] == "int":
            rasterType = gdal.GDT_Int32
        else:
            rasterType = gdal.GDT_Float32

        outRaster = driver.Create(outRasterPath, self.raster.cols, self.raster.rows, 1, rasterType)
        outRaster.SetProjection(self.raster.proj)
        outRaster.SetGeoTransform(self.raster.geoTrans)
        band = outRaster.GetRasterBand(1).SetNoDataValue(NoData_value)

        # get raster array
        array = self.raster.band.ReadAsArray().astype(np.float32)

        value = np.ones_like(array) * -9999
        for key in self.lut.keys():
            value[np.where(np.equal(array, key))] = self.lut[key]
        outRaster.GetRasterBand(1).WriteArray(value)
        outRaster.GetRasterBand(1).ComputeStatistics(False)
        outRaster = None
        if self.ui.ratCheckBox.isChecked():
            self.createLookupRAT(outRasterPath)
        self._updateProgress(False)
        logging.info(self.tr("Output raster {} created.").format(outRasterPath))

    def _updateProgress(self, switch: bool) -> None:
        """
        Gets called by on_applyPushButton_clicked.
        Changes the progressbar to tell user something is going on.
        """
        if switch:
            self.ui.progress.setRange(0, 0)
        else:
            self.ui.progress.setRange(0, 1)

    def closeEvent(self, event):
        self.raster = None
