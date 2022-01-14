from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from osgeo import gdal, ogr
import joblib
import logging
import numpy as np
import os
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import roc_curve, roc_auc_score
import time
from core.libs.Analysis.BivariateSolver import WofE  # for statistics
from core.libs.GDAL_Libs.Layers import Raster, Feature
from core.libs.Rasterprepwork.rpw_main import rasterprepwork
import traceback


class ann_calc(QObject):
    loggingInfoSignal = pyqtSignal(str)
    resultSignal = pyqtSignal(str)
    finished = pyqtSignal()
    loggingErrorSignal = pyqtSignal(str)

    def __init__(self, project_path, data_list, featurePath, name, settings):
        QObject.__init__(self, parent=None)
        self.project_path = project_path
        self.data_list = data_list
        self.featurePath = featurePath
        self.name = name
        self.settings = settings
        # Maskraster
        self.maskraster = Raster(os.path.join(project_path, "region.tif"))
        # Subfolders in Project Path
        self.workspacepath = os.path.join(project_path, "workspace")
        self.resultspath = os.path.join(project_path, "results", "ANN")
        self.tablespath = os.path.join(self.resultspath, "tables")

    def run(self):
        """
        Gets called by on_applyPushButton_clicked in ann_main.py. Main function of the calculation.
        """
        try:
            rpw = rasterprepwork()
            stack, labels, stack_full, noDataArray, nr_of_unique_parameters = rasterprepwork.prepareInputData(
                rpw, self.maskraster, self.workspacepath, self.featurePath, self.data_list)
            ann = MLPClassifier(hidden_layer_sizes=self.settings[0],
                                activation=self.settings[1],
                                solver=self.settings[2],
                                alpha=self.settings[3],
                                batch_size=self.settings[4],
                                learning_rate=self.settings[5],
                                learning_rate_init=self.settings[6],
                                power_t=self.settings[7],
                                max_iter=self.settings[8],
                                shuffle=self.settings[9],
                                random_state=self.settings[10],
                                tol=self.settings[11],
                                verbose=self.settings[12],
                                warm_start=self.settings[13],
                                momentum=self.settings[14],
                                nesterovs_momentum=self.settings[15],
                                early_stopping=self.settings[16],
                                validation_fraction=self.settings[17],
                                beta_1=self.settings[18],
                                beta_2=self.settings[19],
                                epsilon=self.settings[20],
                                n_iter_no_change=self.settings[21],
                                max_fun=self.settings[22])
            self.loggingInfoSignal.emit(self.tr("Starting ANN learning with Parameters:\n"))
            self.loggingInfoSignal.emit("\t\n".join("{}\t\t{}".format(p, pv)
                                        for p, pv in ann.get_params().items()))
            time1 = time.perf_counter()
            model = ann.fit(stack.T, labels)
            time2 = time.perf_counter()
            self.loggingInfoSignal.emit(
                self.tr("Learning completed in {} s").format(
                    round(
                        time2 - time1, 3)))
            probab = model.predict_proba(stack_full.T)[:, 1]
            mask_array = self.maskraster.getArrayFromBand()
            self.result_array = np.resize(probab, new_shape=(mask_array.shape))
            self.result_array[np.where(noDataArray == -9999)] = -9999
            probab[np.where(noDataArray.ravel() == -9999)] = 0

            # calculatations to append infos to npz
            auc = roc_auc_score(labels, probab[np.where(np.ravel(noDataArray) != -9999)])
            score = ann.score(stack.T, labels)
            statistics = self.getStatistics(self.data_list)

            # Writing results to raster, .npz and .pkl
            self.results2raster(self.name)
            self.results2npz(
                self.name,
                self.data_list,
                score,
                auc,
                self.settings,
                self.featurePath,
                statistics)
            self.results2pkl(self.name, model)
            self.finished.emit()
        except:
            tb = traceback.format_exc()
            self.loggingErrorSignal.emit(tb)
            self.finished.emit()

    def getStatistics(self, data_list):
        """
        Uses the landslide raster created by rasterprepwork in combination with WofE and already
        existing information to append statistics to the npz file.
        """
        lsRaster = os.path.join(self.project_path, "workspace", "land_rast.tif")
        lsHandle = Raster(lsRaster)
        count = 0
        Statistics = [0]
        for i in range(len(data_list)):
            rasterpath, datatype, name = data_list[i]
            count0 = count
            if datatype == "Discrete":
                rasterHandle = Raster(rasterpath)
                wofe = WofE(rasterHandle, lsHandle)
                table = np.zeros(shape=(len(wofe.stack),), dtype=[('Class ID', 'i'),
                                                                  ('Class', 'i'),
                                                                  ('Landslides', 'i'),
                                                                  ])
                for i in range(len(wofe.stack)):
                    table['Class ID'][i] = i + 1
                    table['Class'][i] = wofe.stack[i][1]
                    table['Landslides'][i] = wofe.stack[i][2]
                count += int(rasterHandle.max)
            elif datatype == "Continuous":
                table = np.zeros(shape=(1,), dtype=[('Class ID', 'i'),
                                                    ('Class', 'U100'),
                                                    ('Landslides', 'U100'),
                                                    ])
                count += 1
                table['Class ID'][0] = 1
                table['Class'][0] = "Continuous"
                table['Landslides'][0] = "All"
            Statistics.append(table)
        return Statistics

    def results2raster(self, name):
        NoData_value = -9999.0
        driver = gdal.GetDriverByName('GTiff')
        path = os.path.join(self.resultspath, "rasters", name + "_ann.tif")
        outRaster = driver.Create(
            path,
            self.maskraster.cols,
            self.maskraster.rows,
            1,
            gdal.GDT_Float32)
        outRaster.SetProjection(self.maskraster.proj)
        outRaster.SetGeoTransform(self.maskraster.geoTrans)
        band = outRaster.GetRasterBand(1).SetNoDataValue(NoData_value)
        outRaster.GetRasterBand(1).WriteArray(self.result_array)
        outRaster.GetRasterBand(1).ComputeStatistics(False)
        outRaster = None
        self.loggingInfoSignal.emit(self.tr("Raster with Results saved in {}").format(path))

    def results2npz(self, name, data_list, score, auc, calcSettings, featurePath, Statistics):
        path = os.path.join(self.tablespath, name + "_tab.npz")
        np.savez_compressed(path,
                            data_list=np.asarray(data_list, dtype=object),
                            score=score,
                            auc=auc,
                            settings=np.asarray(calcSettings, dtype=object),
                            featurePath=featurePath,
                            Statistics=np.asarray(Statistics, dtype=object))
        self.loggingInfoSignal.emit(self.tr("Results saved in {}").format(path))
        self.resultSignal.emit(str(path))

    def results2pkl(self, name, model) -> None:
        path = os.path.join(self.tablespath, name + "_model.pkl")
        joblib.dump(model, path, compress=True)
        self.loggingInfoSignal.emit(self.tr("Model saved in {}").format(path))