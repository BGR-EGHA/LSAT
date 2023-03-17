from osgeo import gdal
import logging
import math
import numpy as np
import os
from core.libs.GDAL_Libs.Layers import Raster


class ahp_calc:
    """
    The heart of the AHP function in LSAT.
    Gets called by ahp, does the heavy lifing (calculations) and in the end writes the results into
    a raster and calls ahp_report to create a Word document with information about the calculation.
    """

    def __init__(
            self,
            scale,
            prioritymethod,
            rastervaluescomp,
            rastercomp,
            outputname,
            project_path):
        """
        Variables:
        scale:              int  - 0 - linear only for v 1.0.0
        prioritymethod:     int  - Index of methodpriorityComboBox in the ui. (0 - MOTR, 1 - RGMM
                                   etc.)
        rastervaluescomp:   list - [[Array of values of raster 1, Path to raster 1], ..., [Array of
                                   values of raster n, Path to raster n]]
        rastercomp:         list - [Array of values of raster comparison, [path to raster 1, ...,
                                   path to raster n]]
        outputname          str  - outputLineEdit.text()
        project_path        str  - Path to the project.
        """
        self.scale = scale
        self.prioritymethod = prioritymethod
        self.rastervaluescomp = rastervaluescomp
        self.rastercomp = rastercomp
        self.outputname = outputname
        self.project_path = project_path

    def run(self):
        # We set the scaling and the calculation method
        c_method = self.get_scale(self.scale)
        prioritymethod = self.get_prioritymethod(self.prioritymethod)
        # We transform the input arrays using the given scale
        transformedrastervaluescomp = self.transforminputarray(self.rastervaluescomp, c_method)
        # We calculate the priorities of the individual raster values and of the rasters
        rastervaluepriorities = prioritymethod(transformedrastervaluescomp)  # priority vector
        rasterpriorities = prioritymethod([self.rastercomp])
        # We calculate the principal eigen value (λ_max) of the individual raster
        # values and of the rasters
        lambda_max_values = self.get_lambda_max(rastervaluepriorities, transformedrastervaluescomp)
        lambda_max_comp = self.get_lambda_max(rasterpriorities, self.rastercomp)
        # We calculate the coefficient priority of the values based on their rasters priority
        coefficientpriorities = self.get_coefficientpriorities(
            rastervaluepriorities, rasterpriorities)
        # Returns a list of CI (Consistency Index) for every raster after Saaty 1977
        CI = self.get_consistencyindex_list(rastervaluepriorities, lambda_max_values)
        # We get the random consistency index (RI) after Saaty to check against CI
        RI = self.get_randomconsistencyindex_list(transformedrastervaluescomp)
        # We calculate the CR (Consistency Ratio) after both Saaty and Alonso & Lamata
        CR_Saaty = self.get_consistencyratio_saaty_list(CI, RI)
        CR_AlonsoLamata = self.get_consistencyratio_alonso_lamata_list(
            rastervaluepriorities, lambda_max_values)
        # Writes a raster with the resulting LSI
        self.writeoutputraster(coefficientpriorities, self.outputname, self.project_path)
        # Generate npz
        self.writenpz(
            self.project_path,
            self.outputname,
            self.scale,
            self.prioritymethod,
            self.rastervaluescomp,
            self.rastercomp,
            transformedrastervaluescomp,
            rastervaluepriorities,
            rasterpriorities,
            lambda_max_values,
            lambda_max_comp,
            coefficientpriorities,
            CI,
            RI,
            CR_Saaty,
            CR_AlonsoLamata)

    def get_scale(self, scale: int):
        """
        We define the function call to calculate c based on the Scale the user picked.
        The input (scale) is the index from the combobox.
        """
        c_dict = {
            0: self._get_linear,
            1: self._get_log,
            2: self._get_rootsquare,
            3: self._get_inverselinear,
            4: self._get_balanced,
            5: self._get_power,
            6: self._get_geometric,
            7: self._get_asymptotical}
        get_c = c_dict[scale]
        return get_c

    def get_prioritymethod(self, prioritymethod: int):
        """
        We define the function call to get the priorities based on a UI Choice.
        The input is the index from the combobox
        """
        prioritymethod_dict = {
            0: self._MeanoftheRowMethod,
            1: self._RowGeometricMeanMethod,
            2: self._EigenVectorMethod}
        get_prioritymethod = prioritymethod_dict[prioritymethod]
        return get_prioritymethod

    def transforminputarray(self, arraycomp: list, get_c):
        """
        Calls get_c which is defined by get_scale to transform the input array.
        """
        transformedarraycomp = []
        for array in arraycomp:
            # If there is only one element to transform we need to call the function differently.
            # This typically is the case when we have only one raster and transform the rastercomp.
            if len(array[0]) > 1:
                transformedarray = np.array(list(map(np.vectorize(get_c), array[0])))
            else:
                transformedarray = np.array(get_c(array[0]))
            # We append the path to the raster at the end.
            transformedarraycomp.append([transformedarray, array[1]])
        return transformedarraycomp

    def _MeanoftheRowMethod(self, listoftransformedarrays: list) -> list:
        """
        Returns a list of priority vectors calculated with the Mean of the row method.
        Corresponds to prioritymethod = 0
        """
        listofpriorityvectors = []
        for array in listoftransformedarrays:
            # Sum of elements in each column
            colsumsvector = array[0].sum(axis=0)
            # Normalizedarray = Value / Sums of elements in column
            normalizedarray = array[0] / colsumsvector
            # Normalized Priority vector (Mean of the rows) = Sum of every normalized
            # row / Nr of items in row
            priorityvector = normalizedarray.sum(axis=1) / normalizedarray.shape[1]
            # We append the path to the raster to keep track
            listofpriorityvectors.append([priorityvector, array[1]])
        return listofpriorityvectors

    def _RowGeometricMeanMethod(self, listoftransformedarrays: list) -> list:
        """
        Returns a list of priority vectors calculated with the Row geometric mean method.
        Corresponds to prioritymethod = 1
        """
        listofpriorityvectors = []
        for array in listoftransformedarrays:
            # The sum of each column.
            colsumsvector = array[0].sum(axis=0)
            # We normalize the arrays columns by dividing them with their sum.
            normalizedarray = array[0] / colsumsvector
            # we calculate the n. root of the product of every row, where n is the
            # amount of rows in the array
            priorityvector = np.prod(normalizedarray, axis=1)**(1 / normalizedarray.shape[1])
            # We append the path to the raster to keep track
            listofpriorityvectors.append([priorityvector, array[1]])
        return listofpriorityvectors

    def _EigenVectorMethod(self, listoftransformedarrays: list) -> list:
        """
        Returns a list of priority vectors calculated with the Eigenvector method.
        Corresponds to prioritymethod = 2
        """
        listofpriorityvectors = []
        for array in listoftransformedarrays:
            w, v = np.linalg.eig(array[0])
            # We need the column of v that corresponds to the highest w
            maxcol = np.where(w == np.max(w))[0][0]
            priorityvector = v[:, maxcol].real
            # We normalize the priorityvector by dividing each element trough their sum.
            normalizedpriorityvector = priorityvector / priorityvector.sum()
            # We append the path to the raster to keep track
            listofpriorityvectors.append([normalizedpriorityvector, array[1]])
        return listofpriorityvectors

    def get_lambda_max(self, priorities: list, listoftransformedarrays: list) -> list:
        """
        Calculates the principal eigen value. We sum up each column of the not normalized array
        and multiplicate it with the corresponding part of the normalized priority vector.
        """
        listlambdamax = []
        for prios, transformed in zip(priorities, listoftransformedarrays):
            # Sum of every transformed row
            sumcols = transformed[0].sum(axis=0)
            # lambda_max = sum(sum of cols * priority vector)
            lambdamax = sum(sumcols * prios[0])
            listlambdamax.append([lambdamax, prios[1]])
        return listlambdamax

    def get_coefficientpriorities(self, rastervaluepriorities: list,
                                  rasterpriorities: list) -> list:
        """
        Returns a array with the coefficient priority of every raster value.
        coefficient
        """
        listcoefficient = []
        for n, rasterpriority in enumerate(rasterpriorities[0][0]):
            coefficientvalue = np.multiply(rasterpriority, rastervaluepriorities[n][0])
            listcoefficient.append([coefficientvalue, rastervaluepriorities[n][1]])
        return listcoefficient

    def get_consistencyindex_list(self, rastervaluepriorities: list, lambda_max_list: list) -> list:
        """
        Calls self._get_consistencyindex for each array to get the individual CI.
        Returns a list like [[CI array 1, path to array 1], .... [CI array n, path to array n]]
        """
        listci = []
        for array, lambda_max_part in zip(rastervaluepriorities, lambda_max_list):
            n = array[0].shape[0]  # Dimension of the Matrix
            lambda_max = lambda_max_part[0]
            ci = self._get_consistencyindex(lambda_max, n)
            listci.append([ci, array[1]])
        return listci

    def _get_consistencyindex(self, lambda_max: float, n: int) -> float:
        """
        Calculates the Consistency Index (CI) based on Saaty 1977.
        CI = (λ_max - n) / (n - 1)
        λ_max = max. eigenvalue
        n = dimension of the matrix
        """
        CI = (lambda_max - n) / (n - 1)
        return CI

    def get_randomconsistencyindex_list(self, listoftransformedarrays: list) -> list:
        """
        Calls self._get_randomconsistencyindex for each array to get the individual RI.
        Returns a list like [[RI array 1, path to raster 1], .... [RI array n, path to raster n]]
        """
        listri = []
        for array in listoftransformedarrays:
            n = array[0].shape[0]  # Dimension of the Matrix
            ri = self._get_randomconsistencyindex(n)
            listri.append([ri, array[1]])
        return listri

    def _get_randomconsistencyindex(self, n: int) -> float:
        """
        Looks up the Random Consistency Index (RI) based on Saaty 1980.
        n = dimension of the matrix
        """
        #   n: RI
        RI_dic = {
            1: 0,
            2: 0,
            3: 0.58,
            4: 0.9,
            5: 1.12,
            6: 1.24,
            7: 1.32,
            8: 1.41,
            9: 1.45,
            10: 1.49
        }
        RI = RI_dic[n]
        return RI

    def get_consistencyratio_saaty_list(self, CI: list, RI: list) -> list:
        """
        Calls self._get_consistencyratio_saaty for each array to get the individual CR
        Returns a list like [[CR array 1, path to raster 1], .... [CR array n, path to raster n]]
        """
        listcr = []
        for c, r in zip(CI, RI):
            cr = self._get_consistencyratio_saaty(c[0], r[0])
            listcr.append([cr, c[1]])
        return listcr

    def _get_consistencyratio_saaty(self, CI: float, RI: float) -> float:
        """
        Calculates the Consistency Ratio (CR) based on Saaty 1977.
        CR = CI / RI
        CI = Consistency Index
        RI = Random consistency Index
        """
        CR = CI / RI
        return CR

    def get_consistencyratio_alonso_lamata_list(
            self,
            listoftransformedarrays: list,
            lambda_max_list: list) -> list:
        """
        Calls self._get_consistencyratio_alonso_lamata for each array to get the individual CR
        Returns a list like [[CR array 1, path to raster 1], .... [CR array n, path to raster n]]
        """
        listcr = []
        for array, lambda_max_part in zip(listoftransformedarrays, lambda_max_list):
            n = array[0].shape[0]  # Dimension of the Matrix
            lambda_max = lambda_max_part[0]
            cr = self._get_consistencyratio_alonso_lamata(lambda_max, n)
            listcr.append([cr, array[1]])
        return listcr

    def _get_consistencyratio_alonso_lamata(self, lambda_max: float, n: int) -> float:
        """
        Calculates the Consistency Ratio (CR) based on Alonso & Lamata 2006.
        CR = (λ - n) / (2,7699*n - 4,3513 - n)
        λ_max = max. eigenvalue
        n = dimension of the matrix
        """
        return (lambda_max - n) / (2.7699 * n - 4.3513 - n)

    def writeoutputraster(self, coefficientpriorities: list, outputname: str, project_path: str):
        """
        Generates a new raster with the LSI under \results\rasters\\*outputname*.tif
        """
        lsiarray = self._generateoutputarray(coefficientpriorities)
        self.array2raster(outputname, lsiarray, project_path)

    def _generateoutputarray(self, coefficientpriorities: list):
        """
        Generates a new array with the LSI
        We load each raster into memory and replace their initial values with the corresponding
        priority. Then we sum the arrays and write the result as a new raster. We need to check for
        -9999*(nr of rasters) so we can replicate the NoValue places. While we do that we also get
        their uniqueValues for the npz.
        """
        arraystoaddup = []
        self.uniquePerRaster = []
        for n, raster in enumerate(coefficientpriorities):
            memoryraster = Raster(raster[1])
            array = memoryraster.getArrayFromBand().astype(float)
            uniquevalues = memoryraster.uniqueValues.tolist()
            for j, value in enumerate(raster[0]):
                array[array == uniquevalues[j]] = value
            arraystoaddup.append(array)
            self.uniquePerRaster.append([uniquevalues, raster[1]])
        lsiarray = sum(arraystoaddup)
        # We fix the Novalue. We expect the novalue to be the same across all rasters (-9999)
        lsiarray[lsiarray == -9999 * (n + 1)] = -9999
        return lsiarray

    def array2raster(self, outputname: str, lsiarray, project_path: str):
        """
        Saves the resulting array as a tif raster
        """
        path = os.path.join(project_path, "results", "AHP", "rasters", outputname + "_ahp.tif")
        mask = Raster(os.path.join(project_path, "region.tif"))
        NoData_value = -9999.0
        driver = gdal.GetDriverByName('GTiff')
        outRaster = driver.Create(path, mask.cols, mask.rows, 1, gdal.GDT_Float32)
        outRaster.SetProjection(mask.proj)
        outRaster.SetGeoTransform(mask.geoTrans)
        band = outRaster.GetRasterBand(1).SetNoDataValue(NoData_value)
        outRaster.GetRasterBand(1).WriteArray(lsiarray)
        outRaster.GetRasterBand(1).ComputeStatistics(False)
        outRaster = None

    def writenpz(
            self,
            project_path,
            outputname,
            scale,
            prioritymethod,
            rastervaluescomp,
            rastercomp,
            transformedrastervaluescomp,
            rastervaluepriorities,
            rasterpriorities,
            lambda_max_values,
            lambda_max_comp,
            coefficientpriorities,
            CI,
            RI,
            CR_Saaty,
            CR_AlonsoLamata):
        """
        Generates a npz file with statistical information similiar to the report.
        We save the lists as dtype=object to let numpy handle jagged lists.
        """
        path = os.path.join(project_path, "results", "AHP", "tables", outputname + "_tab.npz")
        rastercomp[0] = rastercomp[0].ravel()
        np.savez_compressed(path,
                            scale=scale,
                            prioritymethod=prioritymethod,
                            rastervaluescomp=np.asarray(rastervaluescomp, dtype=object),
                            rastercomp=np.asarray(rastercomp, dtype=object),
                            transformedrastervaluescomp=np.asarray(transformedrastervaluescomp, dtype=object),
                            rastervaluepriorities=np.asarray(rastervaluepriorities, dtype=object),
                            rasterpriorities=np.asarray(rasterpriorities, dtype=object),
                            lambda_max_values=np.asarray(lambda_max_values, dtype=object),
                            lambda_max_comp=np.asarray(lambda_max_comp, dtype=object),
                            coefficientpriorities=np.asarray(coefficientpriorities, dtype=object),
                            CI=CI,
                            RI=RI,
                            CR_Saaty=CR_Saaty,
                            CR_AlonsoLamata=CR_AlonsoLamata,
                            uniquePerRaster=np.asarray(self.uniquePerRaster, dtype=object))  # _generateoutputarray

# c calculations taken from BPMSG pdf Goepel, Klaus D. (2013) and  Ishizaka & Labib (2011)
# as of Version 1.0.0 we only use linear scaling in LSAT
    def _get_linear(self, x):
        """
        Returns linear c given the Intensity x
        """
        c = x
        return c

    def _get_log(self, x):
        """
        Returns log c given the Intensity x
        """
        c = math.log(x + 1)
        return c

    def _get_rootsquare(self, x):
        """
        Returns Root square c given the Intensity x
        """
        c = math.sqrt(x)
        return c

    def _get_inverselinear(self, x):
        """
        Returns inverse linear c given the Intensity x
        """
        c = 9 / (10 - x)
        return c

    def _get_balanced(self, x):
        """
        Returns balanced c given the Intensity x
        """
        c = (0.45 + 0.05 * x) / (1 - (0.45 + 0.05 * x))
        return c

    def _get_power(self, x):
        """
        Returns power c given the Intensity x
        """
        c = x * x
        return c

    def _get_geometric(self, x):
        """
        Returns geometric c given Intensity x
        """
        c = 2**(x - 1)
        return c

    def _get_asymptotical(self, x):
        """
        Returns asymptotical c given Intensity x
        """
        c = math.atanh((math.sqrt(3) * (x - 1)) / (14))
        return c
