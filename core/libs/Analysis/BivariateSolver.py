# -*- coding: utf-8 -*-

from osgeo import gdal, ogr, osr
import sys
import os
import numpy as np
import time
from matplotlib.figure import Figure
import math


class WofE:
    """
     Object holding the weights of evidence procedure
    ---------------------------------------------------------------------------------------------------------
    """

    def __init__(self, evidenceRaster, eventRaster, laplaceSmoothing=""):
        """
        :param evidenceRaster: integer raster holding the categories of the evidential pattern
        :param eventRaster: a raster object from Layers-library containing boolean values for presence and absence of events
        :param laplaceSmoothing: a float value indication a frequency guess in case of event absence
        """

        self.evidenceRaster = evidenceRaster
        self.eventRaster = eventRaster
        self.laplaceSmoothing = laplaceSmoothing
        self.stack = self.getHistogram()
        self.table = self.getTable()
        self.auc = self.calcAUC()[0]
        self.roc_x = self.calcAUC()[1]
        self.roc_y = self.calcAUC()[2]
        self.eventRaster = None

    def getHistogram(self):
        """
        This method estimates unique values within the class raster and
           generates a histogram of the class raster (which gives the frequency of pixels within classes)
           and a histogram of the overlay raster which have class values only on spots where landslides are present
           (this gives the landslide pixel frequencies within the classes)
        :return: ndarray
        """

        nodata1 = self.evidenceRaster.nodata
        nodata2 = self.eventRaster.nodata
        if nodata1 is None:
            nodata1 = 0
        if nodata2 is None:
            nodata2 = 0

        class_array = self.evidenceRaster.getArrayFromBand()
        land_array = self.eventRaster.getArrayFromBand()
        result_array = class_array * land_array
        result_array[np.where(class_array == nodata1)] = -9999.
        result_array[np.where(land_array == nodata2)] = -9999.

        land_class, land_count = np.unique(result_array, return_counts=True)
        dict_land_class = {}
        for i in range(len(land_class)):
            dict_land_class[land_class[i]] = land_count[i]

        unique_class, class_count = np.unique(class_array.astype(np.float32), return_counts=True)

        if nodata1 in unique_class:
            table_shape = len(unique_class) - 1
        else:
            table_shape = len(unique_class)
        table = np.zeros(
            shape=(
                table_shape,), dtype=[
                ('Weight', 'f'), ('Class_pix', 'i'), ('Land_pix', 'i')])
        cor = 0
        for i in range(len(unique_class)):
            if unique_class[i] == nodata1:
                cor += 1
                pass
            else:
                try:
                    table[i - cor] = (unique_class[i], class_count[i],
                                      dict_land_class[unique_class[i]])
                except BaseException:
                    table[i - cor] = (unique_class[i], class_count[i], 0)
        self.stack = table

        return self.stack

    def getTable(self):
        """
        This method constructs and calculates the weights table of the ceratin parameter.
        The table is a structured numpy array.
        Class: number of pixels in a specific raster class
        Landslides: number of landslide pixels in the correcponding class
        W_POS: likelihood ratio to find a landslide given the evidence class
        VAR_POS: variance of W_POS
        W_NEG: likelihood ratio to find a landslide pixel outside evidence class
        Variance: total variance of W_NEG and W_POS
        Contrast: contrast of W_NEG and W_POS
        Weight: total weight
        Posterior: posterior probability
        sPost: standard deviation of the posterior probability
        Expected: number of landslide pixels predicted by the model in the given class
        sExpec: standard deviation of the predicted landslide pixel number.

        :return: table (ndarray, numpy structured array)
        """

        self.table = np.zeros(shape=(len(self.stack),), dtype=[('Class', 'i'),
                                                               ('Landslides', 'i'),
                                                               ('W_POS', 'f'),
                                                               ('VAR_POS', 'f'),
                                                               ('W_NEG', 'f'),
                                                               ('VAR_NEG', 'f'),
                                                               ('Variance', 'f'),
                                                               ('Contrast', 'f'),
                                                               ('Weight', 'f'),
                                                               ('Posterior', 'f'),
                                                               ('sPost', 'f'),
                                                               ('Expected', 'i'),
                                                               ('sExpec', 'i')])

        for i in range(len(self.stack)):
            self.table['Class'][i] = self.stack[i][1]
            self.table['Landslides'][i] = self.stack[i][2]

        # Compute global values
        landsl_total = self.table['Landslides'].sum()

        area_total = self.table['Class'].sum()

        stable_area = area_total - landsl_total
        prior = (float(landsl_total) / float(area_total)) / (float(stable_area) / float(area_total))
        variance_prior = 1 / float(landsl_total)

        # Compute self.table values
        entropy = 0
        account = 0
        for i in range(len(self.stack)):

            # W_POS
            if self.table['Landslides'][i] == 0 and self.laplaceSmoothing != "":
                self.table['W_POS'][i] = np.log((float(self.laplaceSmoothing) /
                                                 float(self.table['Class'][i])) /
                                                ((float(self.table['Class'][i]) -
                                                  float(self.laplaceSmoothing)) /
                                                 float(self.table['Class'][i])) /
                                                float(prior))
            elif self.table['Landslides'][i] == 0 and self.laplaceSmoothing == "":
                self.table['W_POS'][i] = float(0)
            else:
                if float(self.table['Class'][i]) - float(self.table['Landslides'][i]) == 0:
                    self.table['W_POS'][i] = np.log(
                        (float(
                            self.table['Landslides'][i]) /
                            float(
                            self.table['Class'][i])) /
                        1 /
                        float(
                            self.table['Class'][i]) /
                        float(prior))
                else:
                    self.table['W_POS'][i] = np.log(
                        (float(
                            self.table['Landslides'][i]) /
                            float(
                            self.table['Class'][i])) /
                        (
                            (float(
                                self.table['Class'][i]) -
                                float(
                                self.table['Landslides'][i])) /
                            float(
                                self.table['Class'][i])) /
                        float(prior))

            # W_NEG
            if self.table["Landslides"][i] == landsl_total:
                self.table["W_NEG"][i] = float(0)
            else:
                self.table['W_NEG'][i] = np.log((float(landsl_total) -
                                                 float(self.table['Landslides'][i])) /
                                                (float(area_total) -
                                                 float(self.table['Class'][i])) /
                                                ((float(area_total) -
                                                  float(landsl_total) -
                                                    float(self.table['Class'][i]) +
                                                    float(self.table['Landslides'][i])) /
                                                 ((float(area_total) -
                                                   float(self.table['Class'][i])))) /
                                                float(prior))

            # Calculate Contrast
            self.table['Contrast'][i] = float(
                self.table['W_POS'][i]) - float(self.table['W_NEG'][i])

            # Calculate VAR_POS
            if self.table['Landslides'][i] == 0 and self.laplaceSmoothing == "":
                self.table['VAR_POS'][i] = float(0)
            elif self.table['Landslides'][i] == 0 and self.laplaceSmoothing != "":
                self.table['VAR_POS'][i] = 1 + 1 / \
                    (float(self.table['Class'][i]) - float(self.table['Landslides'][i]))
            else:
                if float(self.table['Class'][i]) - float(self.table['Landslides'][i]) == 0:
                    self.table['VAR_POS'][i] = 1 / float(self.table['Landslides'][i]) + 1
                else:
                    self.table['VAR_POS'][i] = 1 / float(self.table['Landslides'][i]) + 1 / (
                        float(self.table['Class'][i]) - float(self.table['Landslides'][i]))

            # Calculate VAR_NEG
            if (float(landsl_total) - float(self.table['Landslides'][i])) != 0:
                self.table['VAR_NEG'][i] = 1 / (float(landsl_total) - float(self.table['Landslides'][i])) + 1 / (float(
                    area_total) - float(landsl_total) - float(self.table['Class'][i]) + float(self.table['Landslides'][i]))
            else:
                self.table['VAR_NEG'][i] = 1 + 1 / (float(area_total) - float(landsl_total) - float(
                    self.table['Class'][i]) + float(self.table['Landslides'][i]))

        W_neg_sum = float(self.table['W_NEG'].sum())
        var_neg_sum = float(self.table['VAR_NEG'].sum())
        for i in range(len(self.stack)):

            # Calculate Weight

            self.table['Weight'][i] = float(self.table['W_POS'][i]) + \
                float(W_neg_sum) - float(self.table['W_NEG'][i])

            # Calculate Variance
            self.table['Variance'][i] = float(
                self.table['VAR_POS'][i]) + float(var_neg_sum) - float(self.table['VAR_NEG'][i])

            # Calculate Posterior

            self.table['Posterior'][i] = 1 / \
                (1 + np.exp(-(self.table['Weight'][i] + np.log(float(prior)))))

            # Calculate Expected

            self.table['Expected'][i] = float(
                self.table['Posterior'][i]) * float(self.table['Class'][i])

            # Calculate s(Posterior)

            self.table['sPost'][i] = np.sqrt(float(self.table['VAR_POS'][i]) + float(var_neg_sum) - float(
                self.table['VAR_NEG'][i]) + float(variance_prior)) * float(self.table['Posterior'][i])

            # Calculate s[Expected)

            self.table['sExpec'][i] = float(self.table['sPost'][i]) * float(self.table['Class'][i])

            s_expected_sum = float(self.table['sExpec'].sum())

            entropy = entropy + float(self.table['Class'][i]) / float(area_total) * - \
                np.log(float(self.table['Class'][i]) / float(area_total))
            max_ent = np.log(len(self.table))
            norm_ent = float(entropy / max_ent)

        return self.table

    def calcAUC(self):
        """
         This method calculates the Area Under Curve (AUC) for the weighted evidence based on training data.

        :return: tuple(auc, x, y)
        """

        sortTable = np.sort(self.table, order=['Weight'])[::-1]
        x = [0.0]
        y = [0.0]
        for i in range(len(self.stack)):
            x.append(x[i] + float(sortTable['Class'][i]) / float(sortTable['Class'].sum()))
            y.append(y[i] + float(sortTable['Landslides'][i]) /
                     float(sortTable['Landslides'].sum()))
        auc = []
        for i in range(len(x) - 1):
            auc.append((x[i + 1] - x[i]) * y[i + 1] - ((x[i + 1] - x[i]) * (y[i + 1] - y[i]) / 2))

        return sum(auc), x, y
