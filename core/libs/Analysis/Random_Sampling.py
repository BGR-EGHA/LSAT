# -*- coding: utf-8 -*-

from osgeo import gdal, ogr, osr
import sys
import os
import random
import numpy as np
import time
from core.libs.GDAL_Libs.Layers import Raster, Feature

gdal.AllRegister()


class RandomSampling:
    """
    Class containing a sample object
    """

    def __init__(
            self,
            feature_path,
            outTraining,
            outTest,
            percent=50,
            srProject="",
            i="",
            keepTest=True):
        """
        Initialize the parameters for random sampling and launching of the sampling procedure.
        :param feature_path:  path of the dataset that should be subdivided into training and test samples
        :param outTraining: path of the output training dataset
        :param outTest: path of the output test dataset
        :param percent: propostion of the training dataset in percent (default value is 50%)
        :param srProject: osr coordinate transformation
        :param i:  process counter if the analysis is multiprocess supported (default = empty string)
        :param keepTest: boolean True or False for keeping the test data set as a file
        """
        self.percent = percent
        self.numer = i
        ext = os.path.splitext(feature_path)[1].lower()
        driverstr = Feature.getDriverFromExtension(self, ext)
        self.driver = ogr.GetDriverByName(driverstr)
        self.feature_path = feature_path
        self.outTraining = outTraining
        self.outTest = outTest
        self.srProject = srProject
        self.keepTest = keepTest
        self.feat = Feature(self.feature_path)
        self.featSR = osr.SpatialReference()
        if int(gdal.VersionInfo()) > 3000000:
            self.srProject.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
            self.featSR.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        self.featSR.ImportFromWkt(self.feat.spatialRefWkt)
        self.coordTrans = osr.CoordinateTransformation(self.featSR, self.srProject)
        self.Sampling()

    def Sampling(self):
        """
        Random sampling of numbers and its subdivision into training and test data
        """
        if self.srProject != "":
            spr = self.srProject
        else:
            spr = self.featSR
        global training
        training = []
        FileNameTraining = self.outTraining
        FileNameTest = self.outTest
        geom = self.feat.geometryType
        # check if the output path already exist and delete if true
        if os.path.exists(FileNameTraining):
            self.driver.DeleteDataSource(FileNameTraining)
        # If the file did not exist we check the directory structure and create it if needed
        else:
            os.makedirs(os.path.dirname(FileNameTraining), exist_ok=True)
        # create outDataSources for training
        training_shp = self.driver.CreateDataSource(FileNameTraining)
        training_lyr = training_shp.CreateLayer("Training", spr, geom)
        training_lyr_Defn = training_lyr.GetLayerDefn()
        # Add input Layer Fields to the output Layer if it is the one we want
        inLayerDefn = self.feat.layerDefn
        for i in range(0, inLayerDefn.GetFieldCount()):
            fieldDefn = inLayerDefn.GetFieldDefn(i)
            fieldName = fieldDefn.GetName()
            training_lyr.CreateField(fieldDefn)
        # We only create the outDataSource for the Test Data if it is necessary.
        # Also we only then delete existing test data.
        if self.keepTest and self.percent != 100:
            global test
            test = []
            if os.path.exists(FileNameTest):
                self.driver.DeleteDataSource(FileNameTest)
            test_shp = self.driver.CreateDataSource(FileNameTest)
            test_lyr = test_shp.CreateLayer("Test", spr, geom)
            test_lyr_Defn = test_lyr.GetLayerDefn()
            inLayerDefn = self.feat.layerDefn
            for i in range(0, inLayerDefn.GetFieldCount()):
                fieldDefn = inLayerDefn.GetFieldDefn(i)
                fieldName = fieldDefn.GetName()
                test_lyr.CreateField(fieldDefn)
        # generate training sample
        while len(training) < int((self.feat.count * self.percent) / 100):
            k = random.randint(0, self.feat.count)
            if k not in training:
                training.append(k)
        for i in range(self.feat.count):
            feature = self.feat.layer.GetFeature(i)
            geom = feature.GetGeometryRef()
            geom.Transform(self.coordTrans)
            if i in training:
                outFeature = ogr.Feature(training_lyr_Defn)
                # Add field values from input Layer
                for j in range(0, training_lyr_Defn.GetFieldCount()):
                    fieldDefn = training_lyr_Defn.GetFieldDefn(j)
                    fieldName = fieldDefn.GetName()
                    try:
                        outFeature.SetField(training_lyr_Defn.GetFieldDefn(j).GetNameRef(),
                                            feature.GetField(j))
                    except KeyError:
                        pass
                outFeature.SetGeometry(geom)
                training_lyr.CreateFeature(outFeature)
            else:
                # Keep remains of Layer as test
                # We can check if test exists
                if self.keepTest and self.percent < 100:
                    outFeature = ogr.Feature(test_lyr_Defn)
                    # Add field values from input Layer
                    for j in range(0, test_lyr_Defn.GetFieldCount()):
                        fieldDefn = test_lyr_Defn.GetFieldDefn(j)
                        fieldName = fieldDefn.GetName()
                        outFeature.SetField(test_lyr_Defn.GetFieldDefn(j).GetNameRef(),
                                            feature.GetField(j))
                    outFeature.SetGeometry(geom)
                    test_lyr.CreateFeature(outFeature)
        feature = None
        self.feat = None
        self.training_shp = None
        outFeature = None
        test_shp = None
