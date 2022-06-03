import math
import random
import numpy as np
import os, logging, traceback
from PyQt5.QtCore import *
from sklearn.metrics import roc_curve, roc_auc_score
from sklearn.metrics import auc as aucfunc
from core.libs.Analysis.Random_Sampling import RandomSampling
from core.libs.GDAL_Libs.Layers import Raster, Feature


class ModelBuilder_calc(QObject):
    # Signals to communicate with ui.
    progressSignal = pyqtSignal(int)
    dataSignal = pyqtSignal(str)
    finishSignal = pyqtSignal()
    expressionErrorSignal = pyqtSignal()

    def __init__(self, projectpath: str, inputs: tuple, spatref, axes_roc, canvas_roc):
        super().__init__()
        self.projectpath = projectpath
        self.rasterpaths = inputs[0]  # list - Strings of raster paths
        self.featurepath = inputs[1]  # str - Featurepath
        self.samplecount = inputs[2]  # int - Samplecount
        self.samplesize = inputs[3]  # int - Samplesize (How much of the Feature gets used [%])
        self.subsampledir = inputs[4]  # str - Subsample location ("" if no subsamples)
        # int - Analysis type (1 - On-the-Fly, 2 - Predef, 3 - Single)
        self.analysistype = inputs[5]
        self.modelname = inputs[6]  # str - Model name
        self.expression = inputs[7] # str - Expression to build the array
        self.randomseed = inputs[8] # str/None - Random Seed only necessary for On-the-Fly
        self.spatref = spatref
        self.axes_roc = axes_roc
        self.canvas_roc = canvas_roc  # Used to update the plot
        self.all_x = []
        self.all_y = []
        self.all_auc = []
        self.progfraction = 100 / self.samplecount  # by how much the progressbar increases

    def run(self):
        """
        Calculation starts here.
        """
        sumarray = self.rasterlist2array(self.rasterpaths, self.expression)
        maskpath = os.path.join(self.projectpath, "region.tif")
        if self.analysistype == 1:  # On-the-fly Subsampling
            self.ontheflymodel(self.projectpath, self.samplecount, self.featurepath,
                               self.progfraction, self.samplesize, sumarray, maskpath, self.spatref,
                               self.randomseed, 0)
            analysisstr = "On-the-fly subsampling"
            featurepath = self.featurepath
            samplecount = self.samplecount
        elif self.analysistype == 2:  # Predefined Subsamples
            samplecount = self.predefinedsamplemodel(self.projectpath, self.subsampledir,
                                                     self.progfraction, self.spatref, maskpath,
                                                     sumarray)
            analysisstr = "Predefined subsamples"
            featurepath = self.subsampledir
        else:  # Single Sample
            self.singlemodel(self.projectpath, self.featurepath, maskpath, self.spatref, sumarray)
            analysisstr = "Single sample"
            featurepath = self.featurepath
            samplecount = 1
        fpr_unique, max_tpr, min_tpr, mean_tpr, median_tpr, auc = self.statisticalresults()  # Stats

        path = self.savemodel(self.projectpath, self.modelname, auc,
                              sumarray, fpr_unique, min_tpr, max_tpr, mean_tpr,
                              median_tpr, self.uniques, self.all_auc, analysisstr, featurepath,
                              samplecount, self.randomseed)  # Save
        self.updateplot(fpr_unique, min_tpr, max_tpr, self.modelname, mean_tpr)  # Update Plot
        self.dataSignal.emit(path)
        self.finishSignal.emit()

    def rasterlist2array(self, rasterpathlist: list, expression: str) -> np.ndarray:
        """
        Uses the user defined expression to build an output array with evaluate.
        Because the expression can contain the rasters names for the calculation we load them into
        the local namespace.
        Returns an array.
        """
        for rasterpath in rasterpathlist:
            layerName = os.path.splitext(os.path.basename(rasterpath))[0].replace(".", "").replace(" ","")
            raster = Raster(rasterpath)
            locals()[layerName] = raster.getArrayFromBand().astype(np.float32)
            locals()[layerName][locals()[layerName] == -9999] = np.nan
        try:
            array = eval(expression)
            if not isinstance(array, np.ndarray):
                self.expressionErrorSignal.emit()
                return
            return array
        except:
            tb = traceback.format_exc()
            logging.error(tb)

    def ontheflymodel(self, projectpath, samplecount, featurepath, proincrement, samplesize,
                      sumarray, maskpath, spatref, randomseed, progress=0):
        """
        Gets called by run.
        Generates a model with on the fly subsampled inventory.
        """
        if randomseed:
            random.seed(randomseed)
        outtraining, outtest = self._getFeaturePaths(featurepath, projectpath)
        for i in range(samplecount):
            RandomSampling(featurepath, outtraining, outtest, percent=samplesize, srProject=spatref,
                           keepTest=False)
            self.ROC(outtraining, projectpath, maskpath, sumarray)
            progress = self._updateprogress(progress, proincrement)

    def _getFeaturePaths(self, featurepath, projectpath):
        """
        Gets called by ontheflymodel, predefinedsamplemodel and singlemodel
        Returns two paths to the temporary generated Feature Files (training/test).
        """
        extension = os.path.splitext(featurepath)[1].lower()
        outtraining = os.path.join(projectpath, "workspace", "training" + extension)
        outtest = os.path.join(projectpath, "workspace", "test" + extension)
        return outtraining, outtest

    def _updateprogress(self, progress: int, proincrement: float) -> int:
        """
        Gets called by ontheflymodel, predefinedsamplemodel.
        Calculates, returns the new progress and updates the ui.
        """
        progress = math.ceil(progress + proincrement)  # Round progress up to next highest int.
        self.progressSignal.emit(progress)
        return progress

    def predefinedsamplemodel(self, projectpath, subsampledir, proincrement, spatref, maskpath,
                              sumarray, progress=0) -> int:
        """
        Gets called by run.
        Computes the Model with predefined samples.
        Returns the amount of used features
        """
        samples = 0
        for subsample in os.listdir(subsampledir):
            if os.path.splitext(subsample)[1].lower() in [".shp", ".kml", ".geojson"]:
                subsamplepath = os.path.join(subsampledir, subsample)
                outtraining, outtest = self._getFeaturePaths(subsamplepath, projectpath)
                RandomSampling(subsamplepath, outtraining, outtest, percent=100, srProject=spatref,
                               keepTest=False)
                self.ROC(outtraining, projectpath, maskpath, sumarray)
                progress = self._updateprogress(progress, proincrement)
                samples += 1
        return samples

    def singlemodel(self, projectpath, featurepath, maskpath, spatref, sumarray):
        """
        Called by run.
        Computes ROC with one pass of the complete feature.
        """
        outtraining, outtest = self._getFeaturePaths(featurepath, projectpath)
        RandomSampling(featurepath, outtraining, outtest, percent=100, srProject=spatref,
                       keepTest=False)
        self.ROC(outtraining, projectpath, maskpath, sumarray)

    def ROC(self, pathtofeature, projectpath, maskpath, sumarray):
        """
        Gets called by ontheflymodel, predefinedsamplemodel, singlemodel
        Calculates ROC and updates the models lists.
        """
        auc, self.uniques, x, y = self._calcROC(pathtofeature, projectpath, maskpath, sumarray)
        self.all_auc.append(auc)  # Initially empty lists
        if len(x) > 50000:
            slice_interval = len(x) // 50000 # 100k -> 2, 150k -> 3 etc.
        else:
            slice_interval = 1
        self.all_x.append(x[::slice_interval])
        self.all_y.append(y[::slice_interval])

    def _calcROC(self, pathtofeature, projectpath, maskpath, sumarray):
        """
        Gets called by ROC.
        Computes ROC curves
        Returns Area under curve for that feature, unique values in the model, false positive rate
        and true positive rate of the Model.
        """
        # First we need a bool array where the landslides are
        handle = Feature(pathtofeature)
        tmpraster = os.path.join(projectpath, "workspace", "tmp_raster.tif")
        handle.rasterizeLayer(maskpath, tmpraster)
        tmprasterarray = Raster(tmpraster).getArrayFromBand()
        model_array = sumarray[~np.isnan(sumarray)] # sumarray without NoData
        model_ls_array = tmprasterarray[~np.isnan(sumarray)]  # landslide array without NoData

        auc = roc_auc_score(np.ravel(model_ls_array), np.ravel(model_array))
        fpr, tpr, _ = roc_curve(np.ravel(model_ls_array), np.ravel(
            model_array), drop_intermediate=False)
        uniques = np.unique(model_array)
        return auc, uniques, fpr, tpr

    def statisticalresults(self):
        """
        Gets called by run.
        Calculates statistical information based on calculation results.
        """

        fpr_unique = np.unique(self.all_x)  # all unique false positive rates
        tpr_unique_tmp = []
        for i in range(len(self.all_x)):  # We interpolate coressponding values
            tpr_unique_tmp.append(np.interp(fpr_unique, self.all_x[i], self.all_y[i]))
        transp_tpr = np.transpose(tpr_unique_tmp)
        max_tpr = transp_tpr.max(axis=1)
        min_tpr = transp_tpr.min(axis=1)
        mean_tpr = transp_tpr.mean(axis=1)
        median_tpr = np.median(transp_tpr, axis=1)

        if len(self.all_x) > 1:  # Multiple samples -> We need the statistical data
            auc = aucfunc(fpr_unique, mean_tpr)  # Recalculate auc
        else:  # One sample
            auc = self.all_auc[0]  # There is only one auc value

        if len(fpr_unique) > 300:
            slice_interval = len(fpr_unique) // 300
        else:
            slice_interval = 1
        #reduce arrays
        fpr_unique_ = fpr_unique[::slice_interval]
        max_tpr_ = max_tpr[::slice_interval]
        min_tpr_ = min_tpr[::slice_interval]
        mean_tpr_ = mean_tpr[::slice_interval]
        median_tpr_ = median_tpr[::slice_interval]

        return fpr_unique_, max_tpr_, min_tpr_, mean_tpr_, median_tpr, auc

    def updateplot(self, fpr_unique, min_tpr, max_tpr, modelname, mean_tpr):
        """
        Gets called by run.
        Uses mostly the results from statisticalresults to update the plot in the ui.
        """
        if len(fpr_unique) > 300:  # Over 300 unique Data points
            slice_interval = len(fpr_unique) // 300
        else:
            slice_interval = 1
        self.axes_roc.fill_between(fpr_unique[::slice_interval], min_tpr[::slice_interval],
                                   max_tpr[::slice_interval], color="grey", linestyle="--",
                                   alpha=0.5, label=modelname)
        self.axes_roc.plot(fpr_unique[::slice_interval], mean_tpr[::slice_interval],
                           label=modelname)
        self.canvas_roc.draw()

    def savemodel(self, projectpath, modelname, auc, sumarray, fpr_unique, min_tpr, max_tpr, mean_tpr,
                  median_tpr, uniques, all_auc, analysisstr, featurepath, samplecount, randomseed):
        """
        Gets called by run.
        Replaces NaN with the default NoData value (-9999) before saving the model as npz.
        """
        path = os.path.join(projectpath, "results", "susceptibility_maps", modelname + ".npz")
        sumarray[np.isnan(sumarray)] = -9999  # replace Nan with -9999
        np.savez_compressed(path, data=sumarray, name=modelname,
                            auc=auc, all_auc = self.all_auc, unique_values=uniques, params=self.rasterpaths,
                            roc_x=fpr_unique, roc_ymean=mean_tpr, roc_ymax = max_tpr, roc_ymedian = median_tpr,
                            roc_ymin = min_tpr,
                            analysistype=analysisstr, featurepath=featurepath,
                            samplecount=samplecount, expression = self.expression,
                            randomseed = randomseed)
        return path
