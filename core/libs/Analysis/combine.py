# -*- coding: utf-8 -*-

import numpy as np
from osgeo import gdal, gdalconst
from core.libs.GDAL_Libs.Layers import Raster
import os
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import time

gdal.AllRegister()


class Combine(QObject):
    loggingInfoSignal = pyqtSignal(str)
    finishSignal = pyqtSignal()

    def __init__(self, rasterPaths, outPath, maskRasterPath, projectLocation):
        QObject.__init__(self)
        self.rasterPaths = rasterPaths
        self.outRasterPath = outPath
        self.projectLocation = projectLocation
        self.maskRasterPath = maskRasterPath
        self.maskRaster = Raster(self.maskRasterPath)
        self.maskArray = self.maskRaster.getArrayFromBand()
        self.loggingInfoSignal.emit(self.tr("Parameter loaded..."))

    def run(self):
        t1 = time.perf_counter()
        paths = self.reproject(self.maskRasterPath, self.rasterPaths)

        noData_array = self.getNoDataArray(paths)
        stack_list = []
        for path in paths:
            ar = Raster(path).getArrayFromBand()
            ar[np.where(noData_array == -9999.0)] = -9999
            stack_list.append(np.ravel(ar))
        vstack = np.vstack(stack_list).T

        b = np.ascontiguousarray(vstack).view(
            np.dtype((np.void, vstack.dtype.itemsize * vstack.shape[1])))
        uc, idx, inv, count = np.unique(
            b, return_index=True, return_inverse=True, return_counts=True)
        unique_val = vstack[idx]
        try:
            noData_idx = list(unique_val.T[0]).index(-9999)
            inv[np.where(inv == noData_idx)] = -9999
            inv[np.where(inv != -9999)] += 1
        except BaseException:
            pass
        out_array = inv.reshape((self.maskArray.shape[0], -1))
        outraster = self.writeRaster(out_array, self.maskRaster, self.outRasterPath)

        names = [('Value', 'i'), ('Count', 'i')]
        for path in self.rasterPaths:
            names.append((os.path.splitext(os.path.basename(path))[0], "i"))

        table = np.zeros(shape=(len(unique_val),), dtype=names)

        for i, cond in enumerate(unique_val, 1):
            table["Value"][i - 1] = i
            table["Count"][i - 1] = count[i - 1]
            table[i - 1][2] = cond[0]
            table[i - 1][3] = cond[1]

        header_names = []
        for name in names:
            header_names.append(name[0])

        raster = Raster(self.outRasterPath)
        rat = gdal.RasterAttributeTable()

        for name in header_names:
            if 'int' in str(table[str(name)].dtype):
                DTYPE = gdal.GFT_Integer
            elif 'float' in str(table[str(name)].dtype):
                DTYPE = gdal.GFT_Real
            elif '|S100' in str(table[str(name)].dtype):
                DTYPE = gdal.GFT_String
            else:
                pass
            rat.CreateColumn(str(name), DTYPE, gdalconst.GFU_MinMax)

        for col in range(len(header_names)):
            colType = rat.GetTypeOfCol(col)
            for row in range(len(table)):
                if colType == 0:
                    rat.SetValueAsInt(row, col, int(table[row][col]))
                elif colType == 1:
                    rat.SetValueAsDouble(row, col, float(table[row][col]))
                elif colType == 2:
                    rat.SetValueAsString(row, col, str(table[row][col]))

        raster.band.SetDefaultRAT(rat)
        raster = None
        t2 = time.perf_counter()
        self.loggingInfoSignal.emit(self.tr("Combine completed in {} s").format(t2 - t1))
        for tmpfile in paths:
            os.remove(tmpfile)
            os.remove(tmpfile + ".aux.xml")
        self.finishSignal.emit()

    def getNoDataArray(self, paths):
        self.loggingInfoSignal.emit(self.tr("Create NoData mask..."))
        noData_array = np.ones_like(self.maskArray).astype(np.float32)
        for rasterPath in paths:
            raster = Raster(rasterPath)
            ar = raster.getArrayFromBand()
            noData_array[np.where(ar == raster.nodata)] = -9999
        self.loggingInfoSignal.emit(self.tr("NoData mask ready..."))
        return noData_array

    def reproject(self, match_path, src_paths):
        """
        Reprojects the source raster based on a match raster
        :param match_path: str, match raster path
        :param src_paths: list of str, source raster paths
        :return: List of str, reprojected raster paths
        """
        match = Raster(match_path)
        outfile_paths = []
        for src_path in src_paths:
            src = Raster(src_path)
            workspace = os.path.join(self.projectLocation, "workspace")
            outname = os.path.splitext(os.path.basename(src_path))[0] + "_proj.tif"
            outfile_path = os.path.join(workspace, outname)
            outfile = gdal.GetDriverByName('GTiff').Create(
                outfile_path, match.cols, match.rows, 1, gdalconst.GDT_Int16)
            outfile.SetGeoTransform(match.geoTrans)
            outfile.SetProjection(match.proj)
            source = gdal.Open(src_path, gdalconst.GA_ReadOnly)
            gdal.ReprojectImage(source, outfile, src.proj, match.proj, gdalconst.GRA_NearestNeighbour)
            band = outfile.GetRasterBand(1)
            band.SetNoDataValue(0)
            outfile.FlushCache()
            outfile = None
            outfile_paths.append(outfile_path)
        return outfile_paths

    def writeRaster(self, array, mask, outpath):
        NoData_value = -9999
        driver = gdal.GetDriverByName('GTiff')
        outTypeRaster = driver.Create(outpath, array.shape[1], array.shape[0], 1, gdal.GDT_Int32)
        band = outTypeRaster.GetRasterBand(1)
        band.SetNoDataValue(NoData_value)
        outTypeRaster.GetRasterBand(1).WriteArray(array)
        outTypeRaster.SetGeoTransform(mask.geoTrans)
        outTypeRaster.SetProjection(mask.proj)
        outTypeRaster.GetRasterBand(1).ComputeStatistics(False)
        outTypeRaster.FlushCache()
