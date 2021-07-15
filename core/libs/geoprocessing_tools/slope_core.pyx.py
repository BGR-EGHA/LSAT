"""
pygeo_tools is a for tool for basic geoprocessing utilized in the LSAT Project Manager Suite
"""
from libc.math cimport ceil
from libc.math cimport exp
from libc.math cimport sqrt
from osgeo import gdal
import numpy as np
cimport cython

cimport numpy as np


DTYPE = np.float32
ctypedef np.float32_t DTYPE_t


@cython.boundscheck(False)
def slope(rasterPath, outSlopePath):
    """
    Generates slope from DEM based on Horn 1981 algorithm.
    :param rasterPath: string of the path of the source DEM raster dataset
    :param outSlopePath: string of the path of the output slope raster dataset
    :return: slope array
    """
    # 3x3 window
    # |a b c|
    # |d e f|
    # |g h i|
    #
    # Slope computation according Horn(1981) is based on:
    # degree_slope = arctan(rise/run) * 180 / pi
    # rise/run = sqrt((dz/dx)^2 + (dz/dy)^2)
    # dz/dx = ((c + 2f + i)-(a + 2d + g))/(8 * cellsizeX)
    # dz/dy = ((g + 2h + i)-(a + 2b + c))/(8 * cellsizeY)
    #
    #

    demRaster = gdal.Open(rasterPath)
    demBand = demRaster.GetRasterBand(1)
    demNodata = demBand.GetNoDataValue()

    geoTrans = demRaster.GetGeoTransform()
    cdef float cell_size = geoTrans[1]
    cdef float cell_size_term = cell_size * 8

    cdef int nRows = dem_band.YSize
    cdef int nCols = dem_band.XSize
    cdef int iRow
    cdef int iCol
    cdef int i
    cdef int j
    cdef float cell = cellsize

    dem_dataset = gdal.Open(dem_dataset_path)
    dem_band = dem_dataset.GetRasterBand(1)
    dem_nodata = dem_band.GetNoDataValue()

    geoTrans = dem_dataset.GetGeoTransform()
    cdef float cell_size = geoTrans[1] * 8

    cdef np.ndarray[DTYPE_t, ndim= 2] dz_dy = np.zeros([nRows, nCols], dtype=DTYPE)
    cdef np.ndarray[DTYPE_t, ndim= 2] dz_dx = np.zeros([nRows, nCols], dtype=DTYPE)
    cdef np.ndarray[DTYPE_t, ndim= 2] inArray = np.empty((nRows, nCols))
    inArray = dem_band.ReadAsArray

    for iRow from 1 <= iRow < nRows - 1:
        for iCol from 1 <= iCol < nCols - 1:
            if InArray[iRow, iCol] == nodata:
                dz_dx[iRow, iCol] = np.nan
                dz_dy[iRow, iCol] = np.nan
            else:
                dz_dx[iRow,
                      iCol] = ((InArray[iRow - 1,
                                        iCol + 1] + 2 * InArray[iRow,
                                                                iCol + 1] + InArray[iRow + 1,
                                                                                    iCol + 1]) - (InArray[iRow - 1,
                                                                                                          iCol - 1] + 2 * InArray[iRow,
                                                                                                                                  iCol - 1] + InArray[iRow + 1,
                                                                                                                                                      iCol - 1])) / (8 * cell)
                dz_dy[iRow,
                      iCol] = ((InArray[iRow + 1,
                                        iCol - 1] + 2 * InArray[iRow + 1,
                                                                iCol] + InArray[iRow + 1,
                                                                                iCol + 1]) - (InArray[iRow - 1,
                                                                                                      iCol - 1] + 2 * InArray[iRow - 1,
                                                                                                                              iCol] + InArray[iRow - 1,
                                                                                                                                              iCol + 1])) / (8 * cell)

    slope = np.arctan(((dz_dx)**2 + (dz_dy)**2)**0.5) * 180 / 3.14159265

    slope = np.arctan(((dz_dx)**2 + (dz_dy)**2)**0.5) * 180 / 3.14159265
    return slope
