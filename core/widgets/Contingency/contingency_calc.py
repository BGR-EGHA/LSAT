import itertools
import math
import numpy as np
import os
from PyQt5.QtCore import *
from core.libs.GDAL_Libs.Layers import Raster


class Contingency(QObject):
    finishSignal = pyqtSignal()
    loggingInfoSignal = pyqtSignal(str)
    resultsSignal = pyqtSignal(list)

    def __init__(self, maskRasterPath, rasterPaths):
        """
        maskRasterPath typically is region.tif
        rasterPaths is a list of Paths to raster files
        """
        QObject.__init__(self)
        self.rasterPaths = rasterPaths
        self.maskRasterPath = maskRasterPath
        self.maskArray = Raster(self.maskRasterPath).getArrayFromBand()

    @pyqtSlot()
    def run(self):
        combs = itertools.combinations(enumerate(self.rasterPaths), 2)
        # combs is a list of lists with every possible 2 raster combination of every rasterPath
        # without caring for their position. Every raster has his own number in its list. Combined
        # with the other raster they form another list.
        indexed_data_pairs = [[(row, col), (arr1, arr2)] for ((row, arr1), (col, arr2)) in combs]
        for idx, data_pair in enumerate(indexed_data_pairs):
            self.getValues(data_pair)
        self.finishSignal.emit()

    def getNoDataArray(self, data_pair):
        self.loggingInfoSignal.emit(self.tr("Create NoData mask..."))
        noData_array = np.ones_like(self.maskArray).astype(np.float32)
        for rasterPath in data_pair[1]:
            raster = Raster(rasterPath)
            ar = raster.getArrayFromBand()
            noData_array[np.where(ar == raster.nodata)] = -9999
        self.loggingInfoSignal.emit(self.tr("NoData mask ready..."))
        return noData_array

    def getValues(self, data_pair):
        """
        We calculate the statistics for every possible 2 raster combination
        """
        row, col = data_pair[0]
        noData_array = self.getNoDataArray(data_pair)
        stack_list = []
        unique_list = []
        for path in data_pair[1]:
            ar = Raster(path).getArrayFromBand().astype(np.float32)
            ar[np.where(noData_array == -9999)] = np.nan
            stack_list.append(np.ravel(ar[~np.isnan(ar)]))
            unique_list.append(np.unique(ar[~np.isnan(ar)]))
        vstack = np.vstack(stack_list).T

        b = np.ascontiguousarray(vstack).view(
            np.dtype((np.void, vstack.dtype.itemsize * vstack.shape[1])))
        uc, idx, inv, count = np.unique(
            b, return_index=True, return_inverse=True, return_counts=True)
        unique_val = vstack[idx]

        # create dtypes and vertical header
        name_v = os.path.basename(data_pair[1][0]).split(".")[0]
        name_h = os.path.basename(data_pair[1][1]).split(".")[0]
        header_h = []
        header_v = []
        for i, value in enumerate(unique_list[0]):
            header_v.append(str(name_v) + str(int(value)))
        for i, value in enumerate(unique_list[1]):
            header_h.append(str(name_h) + str(int(value)))

        # create cross table
        cross_table = np.zeros(shape=(len(header_v), len(header_h)))

        for i, value in enumerate(unique_val):
            idx_row = list(unique_list[0]).index(value[0])
            idx_col = list(unique_list[1]).index(value[1])
            cross_table[idx_row, idx_col] = count[i]

        Chi = np.zeros(shape=(cross_table.shape[0], cross_table.shape[1]))

        # update the zeros table by calculating Chi-values:

        for a in range(cross_table.shape[0]):
            for b in range(cross_table.shape[1]):
                B = 0
                while B < cross_table.shape[1]:
                    A = 0
                    while A < cross_table.shape[0]:
                        Chi[A, B] = math.pow(
                            (cross_table[A, B] - (cross_table[:, B].sum() * cross_table[A, :].sum() / cross_table.sum())),
                            2) / (cross_table[:, B].sum() * cross_table[A, :].sum() / cross_table.sum())
                        if np.isnan(Chi[A, B]):
                            Chi[A, B] = 0
                        else:
                            pass
                        A += 1
                    B += 1

        # determine the coefficients from the Chi-square table:
        self.Chi = Chi

        self.C_coef = math.sqrt(Chi.sum() / (Chi.sum() + cross_table.sum()))
        self.Cramers_V = math.sqrt(Chi.sum() / (cross_table.sum() *
                                   (min(cross_table.shape[0], cross_table.shape[1]) - 1)))

        Phi = np.zeros(shape=(cross_table.shape[0], cross_table.shape[1]))
        for a in range(cross_table.shape[0]):
            for b in range(cross_table.shape[1]):
                B = 0
                while B < cross_table.shape[1]:
                    A = 0
                    while A < cross_table.shape[0]:
                        a = cross_table[A, B]
                        b = cross_table[:, B].sum() - cross_table[A, B]
                        c = cross_table[A, :].sum() - cross_table[A, B]
                        d = cross_table.sum() - cross_table[:, B].sum() - \
                            cross_table[A, :].sum() + cross_table[A, B]

                        phi = (a * d - b * c) / math.sqrt((a + b) * (c + d) * (a + c) * (b + d))
                        Phi[A, B] = phi
                        if np.isnan(Phi[A, B]):
                            Phi[A, B] = 0
                        else:
                            pass
                        A += 1
                    B += 1
        self.Phi = Phi
        self.resultsSignal.emit([row, col, (self.C_coef, self.Cramers_V,
                                self.Phi, self.Chi, cross_table, header_v, header_h)])
