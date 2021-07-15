import logging
import os
import traceback
from PyQt5.QtCore import *
from core.libs.GDAL_Libs.Layers import Feature
from osgeo import gdal, ogr, osr

class GeoprocessingToolsWorker(QObject):
    finishSignal = pyqtSignal()
    loggingInfoSignal = pyqtSignal(str)

    def __init__(self, inDataPath, methodLayerPath, outDataPath, kwargs):
        QObject.__init__(self, parent=None)
        self.inDataPath = inDataPath
        self.methodLayerPath = methodLayerPath
        self.outDataPath = outDataPath
        self.processingType = kwargs[0]
        self.options = kwargs[1]
        self.srCheckBox = kwargs[2]

    def run(self):
        feature = Feature(self.inDataPath)
        methodLayer = Feature(self.methodLayerPath)

        try:
            if feature.getEPSG_Code() != methodLayer.getEPSG_Code():
                self.loggingInfoSignal.emit(
                    self.tr("EPSG Codes of Feature and Method differ ({} / {}). Reprojecting."
                    ).format(feature.getEPSG_Code(), methodLayer.getEPSG_Code()))
                inFeaturePath = self.reprojectLayer(feature, methodLayer)
                feature = Feature(inFeaturePath)
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)

        driverstr = Feature.getDriverFromExtension(self, os.path.splitext(self.inDataPath)[1])
        driver = ogr.GetDriverByName(driverstr)
        outSource = driver.CreateDataSource(self.outDataPath)

        if self.srCheckBox:
            srs = methodLayer.layer.GetSpatialRef()
        else:
            srs = feature.layer.GetSpatialRef()

        if feature.geometryName == "POLYGON":
            geomType = ogr.wkbMultiPolygon
        elif feature.geometryName == "POINT":
            geomType = ogr.wkbMultiPoint
        elif feature.geometryName == "LINESTRING":
            geomType = ogr.wkbMultiCurve

        if self.processingType == 0:
            self.loggingInfoSignal.emit(self.tr("Perform Clip..."))
            outLayer = outSource.CreateLayer("Clipped", srs, geomType)
            feature.layer.Clip(methodLayer.layer, outLayer, self.options)

        elif self.processingType == 1:
            self.loggingInfoSignal.emit(self.tr("Perform Erase..."))
            outLayer = outSource.CreateLayer("Erased", srs, geomType)
            feature.layer.Erase(methodLayer.layer, outLayer, self.options)

        elif self.processingType == 2:
            self.loggingInfoSignal.emit(self.tr("Perform Intersection..."))
            outLayer = outSource.CreateLayer("Intersection", srs, geomType)
            feature.layer.Intersection(methodLayer.layer, outLayer, self.options)

        elif self.processingType == 3:
            self.loggingInfoSignal.emit(self.tr("Perform Symmetrical Difference..."))
            outLayer = outSource.CreateLayer("SymDifference", srs, geomType)
            feature.layer.SymDifference(methodLayer.layer, outLayer, self.options)

        elif self.processingType == 4:
            self.loggingInfoSignal.emit(self.tr("Perform Union..."))
            outLayer = outSource.CreateLayer("Union", srs, geomType)
            feature.layer.Union(methodLayer.layer, outLayer, self.options)

        outSource = None
        feature = None
        methodLayer = None
        self.finishSignal.emit()

    def reprojectLayer(self, feature, methodLayer) -> str:
        """
        Gets called when the EPSG Code of the input feature and methodLayer differ.
        Reprojects an input feature layer.
        Returns a string to the reprojected vector file.
        """
        inSR = osr.SpatialReference()
        outSR = osr.SpatialReference()

        if self.srCheckBox:
            inSR_epsg = int(feature.getEPSG_Code())
            outSR_epsg = int(methodLayer.getEPSG_Code())

        else:
            inSR_epsg = int(methodLayer.getEPSG_Code())
            outSR_epsg = int(feature.getEPSG_Code())

        inSR.ImportFromEPSG(inSR_epsg)
        outSR.ImportFromEPSG(outSR_epsg)
        coordTrans = osr.CoordinateTransformation(inSR, outSR)
        inName, inExt = os.path.splitext(feature.path)
        outLayerName = os.path.basename(inName) + "_proj." + inExt
        driverstr = Feature.getDriverFromExtension(self, inExt)
        driver = ogr.GetDriverByName(driverstr)
        outShapefile = os.path.join(os.path.dirname(feature.path), outLayerName)
        if os.path.exists(outShapefile):
            driver.DeleteDataSource(outShapefile)
        outDataSet = driver.CreateDataSource(outShapefile)
        if self.feature.geometryName == "POLYGON":
            geomType = ogr.wkbMultiPolygon
        elif self.feature.geometryName == "POINT":
            geomType = ogr.wkbMultiPoint
        elif self.feature.geometryName == "POLYLINE":
            geomType = ogr.wkbMultiCurve

        outLayer = outDataSet.CreateLayer(os.path.basename(os.path.splitext(feature.path)[0]),
                                          outSR, geom_type=geomType)

        # add fields
        inLayerDefn = feature.layerDefn
        for i in range(0, inLayerDefn.GetFieldCount()):
            fieldDefn = inLayerDefn.GetFieldDefn(i)
            outLayer.CreateField(fieldDefn)

        # get the output layer's feature definition
        outLayerDefn = outLayer.GetLayerDefn()

        # loop through the input features
        inFeature = feature.layer.GetNextFeature()
        while inFeature:
            # get the input geometry
            geom = inFeature.GetGeometryRef()
            # reproject the geometry
            geom.Transform(coordTrans)
            # create a new feature
            outFeature = ogr.Feature(outLayerDefn)
            # set the geometry and attribute
            outFeature.SetGeometry(geom)
            for i in range(0, outLayerDefn.GetFieldCount()):
                outFeature.SetField(
                    outLayerDefn.GetFieldDefn(i).GetNameRef(),
                    inFeature.GetField(i))
            # add the feature to the shapefile
            outLayer.CreateFeature(outFeature)
            # dereference the features and get the next input feature
            outFeature = None
            inFeature = feature.layer.GetNextFeature()

        # Save and close the shapefiles
        inDataSet = None
        outDataSet = None
        return outShapefile
