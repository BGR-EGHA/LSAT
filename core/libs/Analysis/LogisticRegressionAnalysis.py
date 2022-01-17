# -*- coding: utf-8 -*-

from osgeo import gdal, ogr
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import chi2
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.metrics import log_loss
import os
import sys
import time
from core.libs.Analysis.BivariateSolver import WofE  # for statistics
from core.libs.GDAL_Libs.Layers import Raster, Feature
from core.libs.Rasterprepwork.rpw_main import rasterprepwork
import joblib
import logging
import math
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import traceback

logging.captureWarnings(True)


class LogisticRegressionAnalysis(QObject):
    loggingInfoSignal = QtCore.pyqtSignal(str)
    resultSignal = QtCore.pyqtSignal(str)
    doneSignal = QtCore.pyqtSignal(str)

    def __init__(self, projectPath, data_list, featurePath, tablesPath, name, settings):
        QObject.__init__(self, parent=None)
        self.projectPath = projectPath
        self.tablesPath = tablesPath
        self.name = name
        self.workspacePath = os.path.join(self.projectPath, "workspace")
        self.data_list = data_list
        self.featurePath = featurePath
        self.maskRasterPath = os.path.join(self.projectPath, "region.tif")
        self.resultsPath = os.path.join(self.projectPath, "results", "LR")
        self.tablePaths = os.path.join(self.resultsPath, "tables")
        self.maskRaster = Raster(self.maskRasterPath)
        self.settings = settings

    @pyqtSlot()
    def run(self):
        rpw = rasterprepwork()
        stack, labels, stack_full, noDataArray, nr_of_unique_parameters = rasterprepwork.prepareInputData(
            rpw, self.maskRaster, self.workspacePath, self.featurePath, self.data_list)
        self.loggingInfoSignal.emit(self.tr("Settings:") + str(self.settings))
        self.loggingInfoSignal.emit(self.tr("Start training..."))
        # Logistic regression with sklearn
        penalty, dual, tol, c, \
            fit_intercept, intercept_scaling, \
            class_weight, random_state, solver, max_iter, \
            multi_class, verbose, warm_start, n_jobs, \
            l1_ratio = self.settings
        lr = LogisticRegression(
            penalty=penalty,
            dual=bool(dual),
            tol=tol,
            C=c,
            fit_intercept=fit_intercept,
            intercept_scaling=intercept_scaling,
            class_weight=class_weight,
            random_state=random_state,
            solver=solver,
            max_iter=max_iter,
            multi_class=multi_class,
            verbose=verbose,
            warm_start=warm_start,
            n_jobs=n_jobs)

        time1 = time.perf_counter()
        try:
            model = lr.fit(stack.T, labels)
            scores, p_values = chi2(stack.T, labels)
            score = lr.score(stack.T, labels)
            time2 = time.perf_counter()
            self.loggingInfoSignal.emit(
                self.tr("Training accomplished in {} s").format(
                    round(
                        time2 - time1, 3)))

            # get probability array
            probab = model.predict_proba(stack_full.T)[:, 1]

            self.loggingInfoSignal.emit(self.tr("Create prediction array"))
            sum = np.ones(shape=(stack.shape[1]))
            sum *= model.intercept_
            coefs = model.coef_
            AIC = self.getAIC(nr_of_unique_parameters, model, stack, labels)
            BIC = self.getBIC(nr_of_unique_parameters, model, stack, labels)
            AICc = self.getAICc(nr_of_unique_parameters, model, stack, labels)
            Statistics = self.getStatistics(self.data_list, coefs, p_values)
            confidence_score = lr.decision_function(stack.T)

            # calcualte auc
            auc = roc_auc_score(labels, probab[np.where(np.ravel(noDataArray) != -9999)])

            mask_array = self.maskRaster.getArrayFromBand()
            self.result_array = np.resize(probab, new_shape=(mask_array.shape))
            self.result_array[np.where(noDataArray == -9999)] = -9999
            probab[np.where(noDataArray.ravel() == -9999)] = 0
            self.results2raster(self.name)
            self.results2npz(self.name,
                model.intercept_,
                self.data_list,
                coefs, 
                confidence_score,
                p_values,
                score, 
                auc,
                AIC,
                BIC,
                AICc,
                Statistics)
            self.results2pkl(self.name, model)
            self.doneSignal.emit("success")
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)
            self.doneSignal.emit("error")


    def getAIC(self, nr_of_unique_parameters, model, stack, labels):
        """
        Returns the Akaike information criterion (AIC)
        AIC = 2 * K - 2 * LL
        with:   K   = Parameters of the model
                LL  = Log Likelihood
        """
        K = nr_of_unique_parameters
        predictions = model.predict(stack.T)
        resid = labels - predictions
        sse = sum(resid**2)
        LL = math.log(sse)
        AIC = 2 * K - 2 * LL
        return AIC

    def getBIC(self, nr_of_unique_parameters, model, stack, labels):
        """
        Returns the Bayesian information criterion (BIC)
        BIC = K * ln(n) - 2 * LL
        with:   K   = Parameters in the models
                n   = Observations
                LL  = Log Likelihood
        """
        K = nr_of_unique_parameters
        predictions = model.predict(stack.T)
        n = stack.size
        resid = labels - predictions
        sse = sum(resid**2)
        LL = math.log(sse)
        BIC = K * math.log(n) - 2 * LL
        return BIC

    def getAICc(self, nr_of_unique_parameters, model, stack, labels):
        """
        Returns the corrected Akaike Information Criteria (AICc)
        AICc = AIC + (2 * K (K + 1 )) / (n - K - 1)
        with:   AIC = Akaike information criterion (see getAIC)
                K   = Parameters in the model
                n   = Observations
        """
        AIC = self.getAIC(nr_of_unique_parameters, model, stack, labels)
        K = nr_of_unique_parameters
        n = stack.size
        AICc = AIC + (2 * K * (K + 1)) / (n - K - 1)
        return AICc

    def getStatistics(self, data_list, coefs, p_values):
        """
        Uses the landslide raster created by rasterprepwork in combination with WofE and already
        existing information to append statistics to the npz file.
        """
        try:
            lsRaster = os.path.join(self.projectPath, "workspace", "land_rast.tif")
            lsHandle = Raster(lsRaster)

            count = 0
            Statistics = [0]
            for i in range(len(data_list)):
                rasterpath, datatype, name = data_list[i]
                count0 = count
                rasterHandle = Raster(rasterpath)
                uniqueValues = np.unique(rasterHandle.getArrayFromBand())
                rasterValues = uniqueValues[uniqueValues != -9999]
                if datatype == "Discrete":
                    wofe = WofE(rasterHandle, lsHandle)
                    table = np.zeros(shape=(len(wofe.stack),), dtype=[('Value', 'i'),
                                                                      ('Class pix', 'i'),
                                                                      ('Landslides pix', 'i'),
                                                                      ('Coef', 'f'),
                                                                      ('p-value', 'f'),
                                                                      ])
                    for i in range(len(wofe.stack)):
                        table['Value'][i] = rasterValues[i]
                        table['Class pix'][i] = wofe.stack[i][1]
                        table['Landslides pix'][i] = wofe.stack[i][2]
                    count += len(wofe.stack)
                elif datatype == "Continuous":
                    table = np.zeros(shape=(1,), dtype=[('Value', 'U100'),
                                                        ('Class pix', 'U100'),
                                                        ('Landslides pix', 'U100'),
                                                        ('Coef', 'f'),
                                                        ('p-value', 'f'),
                                                        ])
                    count += 1
                    table['Value'][0] = str(rasterValues.min()) + "-" + str(rasterValues.max())
                    table['Class pix'][0] = "Continuous"
                    table['Landslides pix'][0] = "All"

                for j, elem in enumerate(coefs[0][count0:count]):
                    table['Coef'][j] = elem
                    table['p-value'][j] = p_values[count0:count][j]
                Statistics.append(table)
            return Statistics
        except:
            tb = traceback.format_exc()
            logging.error(tb)

    def results2raster(self, name):
        NoData_value = -9999.0
        driver = gdal.GetDriverByName('GTiff')
        rastersPath = os.path.join(self.projectPath, "results", "LR", "rasters")
        outRasterPath = os.path.join(rastersPath, name + "_lr.tif")
        outRaster = driver.Create(
            outRasterPath,
            self.maskRaster.cols,
            self.maskRaster.rows,
            1,
            gdal.GDT_Float32)
        outRaster.SetProjection(self.maskRaster.proj)
        outRaster.SetGeoTransform(self.maskRaster.geoTrans)
        band = outRaster.GetRasterBand(1).SetNoDataValue(NoData_value)
        outRaster.GetRasterBand(1).WriteArray(self.result_array)
        outRaster.GetRasterBand(1).ComputeStatistics(False)
        outRaster = None
        self.loggingInfoSignal.emit(
            self.tr("Raster with Results saved in {}").format(outRasterPath))

    def results2npz(
            self,
            name,
            intercept,
            data_list,
            coefs,
            confidence_score,
            p_values,
            score,
            auc,
            AIC,
            BIC,
            AICc,
            Statistics):
        """
        Saves the results of the LR calculation in an .npz file defined in path.
        """
        path = os.path.join(self.tablesPath, name + "_tab.npz")
        np.savez_compressed(path,
                            intercept=intercept,
                            data_list=np.asarray(data_list, dtype=object),
                            training_data=self.featurePath,
                            settings=np.asarray(self.settings, dtype=object),
                            coefs=coefs,
                            c_score=confidence_score,
                            p_values=p_values,
                            score=score,
                            auc=auc,
                            AIC=AIC,
                            BIC=BIC,
                            AICc=AICc,
                            Statistics=np.asarray(Statistics, dtype = object))
        self.loggingInfoSignal.emit(self.tr("Results saved in {}").format(path))
        self.resultSignal.emit(str(path))

    def results2pkl(self, name, model) -> None:
        path = os.path.join(self.tablesPath, name + "_model.pkl")
        joblib.dump(model, path, compress=True)
        self.loggingInfoSignal.emit(self.tr("Model saved in {}").format(path))
