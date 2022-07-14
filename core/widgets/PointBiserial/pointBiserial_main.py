import glob
import numpy as np
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import matplotlib.pyplot as plt

from core.uis.PointBiserial_ui.PointBiserial_ui import Ui_PointBiserial
from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog
from core.libs.GDAL_Libs.Layers import Raster, Feature

class PointBiserial(QMainWindow):
    def __init__(self, projectLocation="", parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_PointBiserial()
        self.ui.setupUi(self)
        self.projectLocation = projectLocation
        self.fileDialog = CustomFileDialog()
        self.autofillInventory()
        self.autofillParameter()

    def autofillInventory(self) -> None:
        """
        Gets called when widget starts. Autofills the inventoryComboBox with .shp, .geojson and .kml
        files in the *projectLocation*/data/inventory folder and its subfolders.
        """
        extensions = (".shp", ".kml", ".geojson")
        for file in glob.glob(f"{self.projectLocation}/data/inventory/**/*.*", recursive=True):
            if file.endswith(extensions):
                self.ui.inventoryComboBox.addItem(str(os.path.normpath(file)))

    def autofillParameter(self) -> None:
        """
        Gets called when widget starts. Autofills the parameterComboBox with .tif files
        in the *projectLocation*/data/params folder and its subfolders.
        """
        for file in glob.glob(f"{self.projectLocation}/data/params/**/*.tif", recursive=True):
                self.ui.parameterComboBox.addItem(str(os.path.normpath(file)))

    @pyqtSlot()
    def on_inventoryToolButton_clicked(self):
        """
        Opens a dialog to select a feature to add its path to inventoryComboBox.
        """
        self.fileDialog.openFeatureFile(self.projectLocation)
        if self.fileDialog.exec_() == 1:
            for filename in self.fileDialog.selectedFiles():
                self.ui.inventoryComboBox.addItem(str(os.path.normpath(filename)))

    @pyqtSlot()
    def on_parameterToolButton_clicked(self):
        """
        Opens a dialog to select a raster to add its path to parameterComboBox.
        """
        self.fileDialog.openRasterFile(self.projectLocation)
        if self.fileDialog.exec_() == 1:
            for filename in self.fileDialog.selectedFiles():
                self.ui.parameterComboBox.addItem(str(os.path.normpath(filename)))

    @pyqtSlot()
    def on_applyPushButton_clicked(self):
        inventory = self.ui.inventoryComboBox.currentText()
        raster = self.ui.parameterComboBox.currentText()
        if self._validate(inventory, raster):
            inventoryArray, rasterArray = self.getArrays(inventory, raster)
            rasterValuesWithLs, rasterValuesWithoutLs = self.getRasterValuesWithAndWithoutLs(
                                                            inventoryArray, rasterArray)
            pointBiserialCorrelationCoefficient = self.calculatePointBiserial(
                                rasterValuesWithLs, rasterValuesWithoutLs, rasterArray)
            self.plot(rasterValuesWithLs, rasterValuesWithoutLs)

    def _validate(self, inventory: str, raster: str) -> bool:
        if os.path.isfile(inventory) and os.path.isfile(raster):
            return True
        else:
            return False

    def getArrays(self, inventory: str, raster: str) -> tuple:
        """
        Converts the feature file inventory into a raster file with raster as a mask to get
        its array and gets rasters array.
        Returns a tuple of numpy arrays: [0] = inventoryArray [1] = rasterArray
        """
        inventoryHandle = Feature(inventory)
        rasterHandle = Raster(raster)
        tmpRaster = os.path.join(self.projectLocation, "workspace", "tmp_raster.tif")
        inventoryHandle.rasterizeLayer(raster, tmpRaster)
        tmpInventoryRaster = Raster(tmpRaster)
        return (tmpInventoryRaster.getArrayFromBand(), rasterHandle.getArrayFromBand())

    def getRasterValuesWithAndWithoutLs(self, inventoryArray, rasterArray) -> tuple:
        """
        Returns a tuple of two arrays: [0] = values in rasterArray with a Landslide
                                       [1] = values in rasterArrray without a Landslide
        """
        elementIndicesWithLs = np.where(inventoryArray == 1)
        elementIndicesWithoutLs = np.where(inventoryArray == 0)
        rasterValuesWithLs = rasterArray[elementIndicesWithLs]
        rasterValuesWithoutLs = rasterArray[elementIndicesWithoutLs]
        return (rasterValuesWithLs, rasterValuesWithoutLs)

    def calculatePointBiserial(self, rasterValuesWithLs, rasterValuesWithoutLs, rasterArray):
        """
        Returns the point biserial correlation coefficient r_pb.
               M_1 - M_0     n_1 * n_0
        r_pb = --------- * √(---------)
                  s_n           n^2
        M_1: Mean of rasterArray values with landslide
        M_0: Mean of rasterArray values without landslide
        s_n: Standard Deviation of rasterArray values
        n_1: Amount of rasterArray elements with landslide 
        n_0: Amount of rasterArray elements without landslide
        n:   Total amount of elements in rasterArray
        """
        M_1 = np.mean(rasterValuesWithLs)
        M_0 = np.mean(rasterValuesWithoutLs)
        s_n = np.std(rasterArray)
        n_1 = rasterValuesWithLs.size
        n_0 = rasterValuesWithoutLs.size
        n = rasterArray.size
        print(((M_1 - M_0) / s_n) * (np.sqrt(((n_1 * n_0) / n**2))))
        return (((M_1 - M_0) / s_n) * (np.sqrt(((n_1 * n_0) / n**2))))

    def plot(self, rasterValuesWithLs, rasterValuesWithoutLs) -> None:
        """Plots the both Arrays values on the y axis.
        """
        plt.figure()
        plt.scatter(np.zeros_like(rasterValuesWithoutLs), rasterValuesWithoutLs, s=1)
        plt.scatter(np.ones_like(rasterValuesWithLs), rasterValuesWithLs, s=1)
        plt.show()