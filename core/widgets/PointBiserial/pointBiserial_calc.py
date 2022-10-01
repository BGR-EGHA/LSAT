from core.libs.GDAL_Libs.Layers import Raster, Feature
import numpy as np
from PyQt5.QtCore import *
import os


class PointBiserialCalc(QObject):
    """
    Point Biserial Calculation in extra Thread.
    """
    finishSignal = pyqtSignal(str, str)

    def __init__(self, discrete, continuous, inventory, outputName, projectLocation):
        super().__init__()
        self.discrete = discrete
        self.continuous = continuous
        self.inventory = inventory
        self.outputName = outputName
        self.projectLocation = projectLocation

    def run(self):
        discreteArray, continuousArray, inventoryArray = self.getArrays(self.discrete, self.continuous, self.inventory)
        if inventoryArray:
            discreteArrays = self.getOneHotArraysWithLs(discreteArray, inventoryArray)
        else:
            discreteArrays = self.getOneHotArrays(discreteArray)
        pointBiserial = self.calculatePointBiserial(
            rasterValuesWithLs, rasterValuesWithoutLs, rasterArray
        )
        self.finishSignal.emit(pointBiserial)

    def getArrays(self, discrete: str, continuous: str, inventory: str) -> tuple:
        """
        Returns a tuple of numpy arrays: [0] = discreteArray [1] = rasterArray [2] = inventoryArray(=OPTIONAL)
        inventoryArray only gets returned if the user provided one, else tuple only contains two arrays.
        """
        continuousHandle = Raster(continuous)
        discreteHandle = Raster(discrete)
        if inventory: # if not the user did not specify an inventory
            inventoryHandle = Feature(inventory)
            tmpRaster = os.path.join(self.projectLocation, "workspace", "tmp_raster.tif")
            inventoryHandle.rasterizeLayer(discrete, tmpRaster)
            tmpInventoryRaster = Raster(tmpRaster)
            return (discreteHandle.getArrayFromBand(), continuousHandle.getArrayFromBand(),
                    tmpInventoryRaster.getArrayFromBand())
        return (discreteHandle.getArrayFromBand(), continuousHandle.getArrayFromBand())

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
            self, continuousValuesWithDiscrete, continuousValuesWithoutDiscrete, continuousArray
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
        M_1 = np.mean(continuousValuesWithDiscrete)
        M_0 = np.mean(continuousValuesWithoutDiscrete)
        s_n = np.std(continuousArray)
        n_1 = continuousValuesWithDiscrete.size
        n_0 = continuousValuesWithoutDiscrete.size
        n = continuousArray.size
        return (((M_1 - M_0) / s_n) * (np.sqrt(((n_1 * n_0) / n ** 2))), M_1, M_0, s_n, n_1, n_0)
