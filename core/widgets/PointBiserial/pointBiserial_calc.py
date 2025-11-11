from core.libs.GDAL_Libs.Layers import Raster, Feature
import numpy as np
from PyQt5.QtCore import *
import os


class PointBiserialCalc(QObject):
    """
    Point Biserial Calculation in extra Thread.
    """
    finishSignal = pyqtSignal(str)

    def __init__(self, discrete, continuous, inventory, outputName, projectLocation):
        super().__init__()
        self.discrete = discrete
        self.continuous = continuous
        self.inventory = inventory
        self.outputName = outputName
        self.projectLocation = projectLocation

    def run(self):
        discreteArray, continuousArray, inventoryArray = self.getArrays(self.discrete, self.continuous, self.inventory)
        if inventoryArray is not None:
            discreteArrays = self.getDiscreteArraysWithLs(discreteArray, inventoryArray)
        else:
            discreteArrays = self.getDiscreteArrays(discreteArray)
        resultsDict = self.addBasicInfoToResultsDict(len(discreteArrays))
        resultsDict["pointBiserialResults"] = {}
        for discreteValue, discreteArray in discreteArrays.items():
            resultsDict["pointBiserialResults"][str(discreteValue)] = {}
            continuousWithDiscrete = np.where(discreteArray == 1, continuousArray, np.nan)
            continuousWithoutDiscrete = np.where(discreteArray == 0, continuousArray, np.nan)
            pb, M_1, M_0, s_n, n_1, n_0 = self.calculatePointBiserial(continuousWithDiscrete,
                continuousWithoutDiscrete, continuousArray)
            resultsDict["pointBiserialResults"][str(discreteValue)]["pb"] = pb
            resultsDict["pointBiserialResults"][str(discreteValue)]["M_1"] = M_1
            resultsDict["pointBiserialResults"][str(discreteValue)]["M_0"] = M_0
            resultsDict["pointBiserialResults"][str(discreteValue)]["s_n"] = s_n
            resultsDict["pointBiserialResults"][str(discreteValue)]["n_1"] = n_1
            resultsDict["pointBiserialResults"][str(discreteValue)]["n_0"] = n_0
            resultsDict["pointBiserialResults"][str(discreteValue)]["continuousWithDiscreteList"] = continuousWithDiscrete
            resultsDict["pointBiserialResults"][str(discreteValue)]["continuousWithoutDiscreteList"] = continuousWithoutDiscrete
            resultsDict["pointBiserialResults"][str(discreteValue)]["continuousWithDiscreteMean"] = np.nanmean(continuousWithDiscrete)
            resultsDict["pointBiserialResults"][str(discreteValue)]["continuousWithoutDiscreteMean"] = np.nanmean(continuousWithoutDiscrete)
        outputLocation = self.saveResults(resultsDict)
        self.finishSignal.emit(outputLocation)

    def addBasicInfoToResultsDict(self, discreteArrayCount: int) -> dict:
        """
        Returns a dict with basic input information (Which files where used, with/without inventory)
        """
        resultsDict = {}
        resultsDict["discreteInputPath"] = self.discrete
        resultsDict["discreteInputsCount"] = discreteArrayCount
        resultsDict["continuousInputPath"] = self.continuous
        resultsDict["inventoryInputPath"] = self.inventory
        return resultsDict

    def getDiscreteArraysWithLs(self, discrete: np.ndarray, inventory: np.ndarray) -> dict:
        """
        Returns a dict with discrete values, except noData (-9999 expected) as keys and their
        one-hot-encoded values as values with and without landslides.
        """
        discreteArrays = {}
        uniques = np.unique(discrete)
        for unique in uniques:
            if unique == -9999:
                continue
            oneHotLs = np.logical_and(discrete == unique, inventory == 1).astype(float)
            oneHotLs[discrete == -9999] = np.nan
            oneHotNonLs = np.logical_and(discrete == unique, inventory == 0).astype(float)
            oneHotNonLs[discrete == -9999] = np.nan
            discreteArrays[f"{unique}_LS"] = oneHotLs
            discreteArrays[f"{unique}_NOLS"] = oneHotNonLs
        return discreteArrays

    def getDiscreteArrays(self, discrete: np.ndarray, noData=-9999) -> dict:
        """
        Returns a dict with discrete values, except noData (-9999 expected) as keys and their
        one-hot-encoded values as values.
        """
        discreteArrays = {}
        uniques = np.unique(discrete)
        for unique in uniques:
            if unique == noData:
                continue
            oneHot = discrete == unique
            oneHot = oneHot.astype(float)
            oneHot[discrete == noData] = np.nan
            discreteArrays[unique] = oneHot
        return discreteArrays

    def getArrays(self, discrete: str, continuous: str, inventory: str) -> tuple:
        """
        Returns a tuple of numpy arrays: [0] = discreteArray [1] = rasterArray [2] = inventoryArray (=OPTIONAL)
        inventoryArray is None if user did not provide one.
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
        return (discreteHandle.getArrayFromBand(), continuousHandle.getArrayFromBand(), None)

    def calculatePointBiserial(
            self, continuousValuesWithDiscrete, continuousValuesWithoutDiscrete, continuousArray
    ) -> tuple:
        """
        Returns the point biserial correlation coefficient r_pb and all values used to calculate it.
               M_1 - M_0     n_1 * n_0
        r_pb = --------- * √(---------)
                  s_n           n^2
        M_1: Mean of continuous values with discrete value
        M_0: Mean of continuous values without discrete value
        s_n: Standard Deviation of continuous values
        n_1: Count of continuous values with discrete value
        n_0: Count of continuous values without discrete value
        n:   Total count of continuous values in rasterArray
        """
        M_1 = np.nanmean(continuousValuesWithDiscrete)
        M_0 = np.nanmean(continuousValuesWithoutDiscrete)
        s_n = np.nanstd(continuousArray)
        n_1 = np.count_nonzero(~np.isnan(continuousValuesWithDiscrete))
        n_0 = np.count_nonzero(~np.isnan(continuousValuesWithoutDiscrete))
        n = np.count_nonzero(~np.isnan(continuousArray))
        return ((M_1 - M_0) / s_n) * (np.sqrt(((n_1 * n_0) / n ** 2))), M_1, M_0, s_n, n_1, n_0

    def saveResults(self, resultsDict: dict) -> str:
        """
        Returns the full path to the .npz file with the saved results.
        """
        outputPath = os.path.join(self.projectLocation, "results", "statistics", "pb",
            self.outputName+".npz")
        np.savez(outputPath, **resultsDict)
        return outputPath