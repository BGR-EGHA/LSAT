from osgeo import gdal
import numpy as np
import os
from core.libs.GDAL_Libs.Layers import Raster, Feature


class rasterprepwork():
    """
    This class bundles data preperation functions currently used by ANN and LR in order to simplify
    and streamline LSAT.
    """

    def prepareInputData(self, maskraster, workspacepath, featurePath, data_list):
        """
        We create multiple Arrays:
        1. No Data Array of the mask raster
        2. Boolean Landslide Array
        3. Boolean Landslide Array without positions where the No Data Array has no Data
        4. + 5. We also create two Array for every Input Raster based on its type and sorting
        one with No Data and one without
        """
        noDataArray = self.getNoDataArray(maskraster, data_list)
        land_rast_array = self.getLandslideArray(workspacepath, featurePath, maskraster)
        # land_rast_array_red is land_rast_array without Values where we have
        # NoData in input rasters.
        land_rast_array_red = land_rast_array[noDataArray != -9999]
        locals_list = []
        full_array_list = []
        # data_list[n][0] = Absolute path to raster
        # data_list[n][1] = Type of raster (Continous/Discrete)
        # data_list[n][2] = Raster name without extension
        for data in data_list:
            if data[1] == "Continuous":
                minMaxScaledArray_red, minMaxScaledArray = self.getMinMaxScaledArray(data[0], noDataArray)
                locals_list.append(minMaxScaledArray_red.ravel())
                full_array_list.append(minMaxScaledArray.ravel())
            else:
                # Appending to lists happens in getstackFromCategoricalData()
                stack_red, stack = self.getstackFromCategoricalData(
                    data[0], maskraster, data[2], noDataArray)
                # We add every return array to its coressponding list
                for n in stack_red:
                    locals_list.append(n.ravel())
                for n in stack:
                    full_array_list.append(n.ravel())
        nr_of_unique_parameters = len(locals_list)
        stack_red = np.vstack(tuple(locals_list))
        stack_full = np.vstack(tuple(full_array_list))
        labels_red = land_rast_array_red.ravel()
        return stack_red, labels_red, stack_full, noDataArray, nr_of_unique_parameters

    def getNoDataArray(self, raster, data_list):
        """
        Returns a raster filled with ones and No Data of the size of the Input (raster). If a
        Input Raster has No Data at any point this point will be No Data for the whole calculation.
        """
        noDataArray = np.ones_like(raster.getArrayFromBand()).astype(np.float32)
        for data in data_list:
            # data[0] is a string of the absolute Path to the raster
            raster = Raster(data[0])
            ar = raster.getArrayFromBand()
            noDataArray[np.where(ar == raster.nodata)] = -9999
        return noDataArray

    def getLandslideArray(self, workspacepath, featurePath, maskraster):
        """
        Creates a boolean Raster from the input feature (featurePath) in workspacepath. maskraster
        defines the boundaries of the output raster.
        """
        outRaster = os.path.join(workspacepath, "land_rast.tif")
        feature = Feature(featurePath)
        feature.rasterizeLayer(maskraster.path, outRaster)
        LandslideRaster = Raster(outRaster)
        LandslideArray = LandslideRaster.getArrayFromBand()
        return LandslideArray

    def getMinMaxScaledArray(self, path: str, noDataArray) -> tuple:
        """
        Creates 2 normalized arrays with value range [0, 1] from input raster:
        NormalizedArray_ascending with NoData and NormalizedArray_ascending_red without.
        :return: ndarray, normalized numpy array
        """
        raster = Raster(path)
        array = raster.getArrayFromBand()
        array_red = array[noDataArray != raster.nodata]
        # Make NoData nan so it does not influence the scaling
        array[array == raster.nodata] = np.nan
        minMaxScaledArray = (array - np.nanmin(array)) / \
            (np.nanmax(array) - np.nanmin(array))
        minMaxScaledArray_red = (
            array_red - np.nanmin(array_red)) / (np.nanmax(array_red) - np.nanmin(array_red))
        # Reverse nan back to NoData (-9999)
        minMaxScaledArray[np.isnan(minMaxScaledArray)] = raster.nodata
        return minMaxScaledArray_red, minMaxScaledArray

    def getstackFromCategoricalData(self, path, maskraster, name, noDataArray):
        """
        Creates 2 times n arrays from a raster with n discrete values. The n. output Raster will be 1 where
        the n. value is and 0 everywhere else.
        stackFromCategoricalData with NoData and stackFromCategoricalData_red without.
        """
        raster = Raster(path)
        array = raster.getArrayFromBand()
        mask_array = maskraster.getArrayFromBand()
        unique_array = np.unique(array)
        unique_array = unique_array[unique_array != raster.nodata]
        stackFromCategoricalData = []
        stackFromCategoricalData_red = []

        for i in unique_array:
            value_array = np.zeros_like(mask_array)
            value_array[np.where(array == i)] = 1
            stackFromCategoricalData.append(value_array.ravel())
            value_array_red = value_array[noDataArray != raster.nodata]
            stackFromCategoricalData_red.append(value_array_red.ravel())
        return stackFromCategoricalData_red, stackFromCategoricalData
