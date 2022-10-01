import glob
import numpy as np
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import logging

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
        self.autofillRasters()

    def autofillInventory(self) -> None:
        """
        Gets called when widget starts. Autofills the inventoryComboBox with .shp, .geojson and .kml
        files in the *projectLocation*/data/inventory folder and its subfolders.
        """
        extensions = (".shp", ".kml", ".geojson")
        for file in glob.glob(f"{self.projectLocation}/data/inventory/**/*.*", recursive=True):
            if file.lower().endswith(extensions):
                self.ui.inventoryComboBox.addItem(str(os.path.normpath(file)))

    def autofillRasters(self) -> None:
        """
        Gets called when widget starts. Autofills the discreete and continuousComboBox with .tif
        files in the *projectLocation*/data/params folder and its subfolders.
        """
        for file in glob.glob(f"{self.projectLocation}/data/params/**/*.tif", recursive=True):
            self.ui.discreteComboBox.addItem(str(os.path.normpath(file)))
            self.ui.continuousComboBox.addItem(str(os.path.normpath(file)))

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
            self.ax.clear()
            self.thread = QThread()
            self.calc = PointBiserialCalc(inventory, raster, self.projectLocation)
            self.calc.moveToThread(self.thread)
            self.thread.started.connect(self.calc.run)
            self.calc.finishSignal.connect(self.done)
                # pointBiserial, M_1, M_0, s_n, n_1, n_0, rasterValuesWithLs, rasterValuesWithoutLs,
                # inventory, raster))
            self.thread.start()
            

    def _validate(self, inventory: str, raster: str) -> bool:
        if os.path.isfile(inventory) and os.path.isfile(raster):
            return True
        else:
            return False

    def done(self, pointBiserial, M_1, M_0, s_n, n_1, n_0, rasterValuesWithLs,
        rasterValuesWithoutLs, inventory, raster):
        """
        Exit PointBiserialCalc Thread and Update Log and Ui to tell user calculation is done.
        Gets called with finishSignal from PointBiserialCalc Thread.
        """
        self.thread.exit()
        logging.info(
            self.tr("Point biserial correlation coefficient = {}").format(pointBiserial)
        )
        self.plot(
            rasterValuesWithLs,
            rasterValuesWithoutLs,
            M_1,  # Mean of rasterArray values with landslide
            M_0,  # Mean of rasterArray values without landslide
            n_1,  # Count of rasterArray elements with landslide
            n_0,  # Count of rasterArray elements without landslide
            os.path.basename(raster),
            os.path.basename(inventory),
        )

    def plot(
        self,
        rasterValuesWithLs,
        rasterValuesWithoutLs,
        meanWithLs,
        meanWithoutLs,
        withLsCount,
        withoutLsCount,
        rasterName,
        inventoryName,
    ) -> None:
        """Scatters all rasterValues [y-axis] with a landslide at 1 [x-axis] and all without a
        landslide at 0. For both cases we draw a hline indicating the mean of the values.
        """
        self.ax.scatter(np.zeros_like(rasterValuesWithoutLs), rasterValuesWithoutLs, s=1, color="b")
        self.ax.hlines(y=meanWithoutLs, xmin=-0.25, xmax=0.25)
        self.ax.scatter(np.ones_like(rasterValuesWithLs), rasterValuesWithLs, s=1, color="r")
        self.ax.hlines(y=meanWithLs, xmin=0.75, xmax=1.25)
        self.ax.set_xticks([0, 1])
        self.ax.set_xticklabels(
            [
                f"no Landslide\nRaster cell count: {withoutLsCount}\nMean Raster value: {meanWithoutLs}",
                f"Landslide\nRaster cell count: {withLsCount}\nMean Raster value: {meanWithLs}",
            ]
        )
        self.ax.set_xlabel(f"{inventoryName}")
        self.ax.set_ylabel(f"{rasterName} values")
        self.canvas.draw()
        self.canvas.flush_events()
        self.fig.tight_layout()

class PointBiserialCalc(QObject):
    """
    Point Biserial Calculation in extra Thread.
    """
    finishSignal = pyqtSignal(float, float, float, float, int, int, np.ndarray, np.ndarray, str, str)

    def __init__(self, inventory, raster, projectLocation):
        super().__init__()
        self.inventory = inventory
        self.raster = raster
        self.projectLocation = projectLocation
    
    def run(self):
        inventoryArray, rasterArray = self.getArrays(self.inventory, self.raster)
        rasterValuesWithLs, rasterValuesWithoutLs = self.getRasterValuesWithAndWithoutLs(
            inventoryArray, rasterArray
        )
        pointBiserial, M_1, M_0, s_n, n_1, n_0 = self.calculatePointBiserial(
            rasterValuesWithLs, rasterValuesWithoutLs, rasterArray
        )
        self.finishSignal.emit(pointBiserial, M_1, M_0, s_n, n_1, n_0, rasterValuesWithLs,
        rasterValuesWithoutLs, self.inventory, self.raster)

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

    def calculatePointBiserial(
        self, rasterValuesWithLs, rasterValuesWithoutLs, rasterArray
    ) -> tuple:
        """
        Returns the point biserial correlation coefficient r_pb and all values used to calculate it.
               M_1 - M_0     n_1 * n_0
        r_pb = --------- * √(---------)
                  s_n           n^2
        M_1: Mean of rasterArray values with landslide
        M_0: Mean of rasterArray values without landslide
        s_n: Standard Deviation of rasterArray values
        n_1: Count of rasterArray elements with landslide
        n_0: Count of rasterArray elements without landslide
        n:   Total count of elements in rasterArray
        """
        M_1 = np.mean(rasterValuesWithLs)
        M_0 = np.mean(rasterValuesWithoutLs)
        s_n = np.std(rasterArray)
        n_1 = rasterValuesWithLs.size
        n_0 = rasterValuesWithoutLs.size
        n = rasterArray.size
        return (((M_1 - M_0) / s_n) * (np.sqrt(((n_1 * n_0) / n**2))), M_1, M_0, s_n, n_1, n_0)
