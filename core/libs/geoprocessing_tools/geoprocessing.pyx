cimport cython
import numpy as np
import math
cimport numpy as np

DTYPE = np.float32

ctypedef np.float32_t DTYPE_t


### Slope compute slope in degrees or % based on the Horn(1981).

cpdef slope_degree(np.ndarray[DTYPE_t, ndim=2]InArray, float nodata, float cellsize, int type):
    cdef int nRows = InArray.shape[0]
    cdef int nCols = InArray.shape[1]
    cdef int iRow
    cdef int iCol
    cdef int i
    cdef int j
    cdef float cell = cellsize * 8
    cdef np.ndarray[DTYPE_t, ndim=2] slope

    cdef np.ndarray[DTYPE_t, ndim=2] dz_dy = np.empty([nRows, nCols], dtype=DTYPE)
    cdef np.ndarray[DTYPE_t, ndim=2] dz_dx = np.empty([nRows, nCols], dtype=DTYPE)

    '''
    Define the matrix to compute slope python 
    |a b c|
    |d e f|
    |g h i| forms the 3x3 window
    Slope computation according Horn(1981) is based on:
    degree_slope = arctan(rise/run) * 180 / pi
    rise/run = sqrt((dz/dx)^2 + (dz/dy)^2)
    dz/dx = ((c + 2f + i)-(a + 2d + g))/(8 * cellsizeX)
    dz/dy = ((g + 2h + i)-(a + 2b + c))/(8 * cellsizeY)
    
    '''
    
    for iRow from 1 <=  iRow <  nRows-1:
        for  iCol from 1 <=  iCol <  nCols-1:
            if InArray[iRow, iCol] == nodata:
                dz_dx[iRow, iCol] = np.nan
                dz_dy[iRow, iCol] = np.nan
            else:
                dz_dx[iRow, iCol] = ((InArray[iRow-1, iCol+1] + 2 * InArray[iRow, iCol+1] + InArray[iRow+1, iCol+1])-
                                     (InArray[iRow-1, iCol-1] + 2 * InArray[iRow, iCol-1] + InArray[iRow+1, iCol-1])) / (cell)
                dz_dy[iRow, iCol] = ((InArray[iRow+1, iCol-1] + 2 * InArray[iRow+1, iCol] + InArray[iRow+1, iCol +1])-
                                     (InArray[iRow-1, iCol-1] + 2 * InArray[iRow-1, iCol] + InArray[iRow-1, iCol+1])) / (cell)
                        
                        
    if type == 1:
        slope = np.arctan(((dz_dx)**2 + (dz_dy)**2)**0.5) * 180 / 3.14159265
    else:
        slope = np.arctan(((dz_dx)**2 + (dz_dy)**2)**0.5) * 100
            
    return slope
