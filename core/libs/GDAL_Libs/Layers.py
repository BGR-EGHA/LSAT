# -*- coding: utf-8 -*-

from osgeo import gdal, ogr, osr
import os
import sys
import numpy as np
import logging

gdal.AllRegister()


class Raster:
    '''
    Raster object is a gdal dataset object.
    '''

    def __init__(self, rasterPath, mode=gdal.GA_ReadOnly):
        """
        Properties of the raster dataset
        :param rasterPath: path to the raster dataset
        :param mode: GDAL mode (gdal.GA_ReadOnly, gdal.GA_Update)
        """
        self.path = rasterPath
        self.data = gdal.Open(self.path)
        self.cols = self.data.RasterXSize
        self.rows = self.data.RasterYSize
        self.band = self.getBand()
        self.xBlocksize = gdal.Band.GetBlockSize(self.band)[0]
        self.yBlocksize = gdal.Band.GetBlockSize(self.band)[1]
        self.proj = self.data.GetProjection()
        self.spatRef = osr.SpatialReference(self.proj)
        self.geoTrans = self.data.GetGeoTransform()
        self.stats = self.band.ComputeStatistics(False)
        self.nodata = self.band.GetNoDataValue()
        self.max = self.band.GetMaximum()
        self.min = self.band.GetMinimum()
        self.rat = self.getRasterAttributeTableFromBand()
        self.cellsize = [self.geoTrans[1], self.geoTrans[5]]
        self.extent = self.getExtent()  # [x_min, x_max, y_min, y_max]
        self.type = gdal.GetDataTypeName(self.band.DataType)
        self.colorTable = self.band.GetColorTable()
        self.dataType = self.getDataTypeFromBand()
        self.uniqueValues = self.getUniqueValuesFromBand()
        self.uniqueValuesCount = self.getUniqueValuesCountFromBand()
        self.epsg = self.getEPSG_Code()
        self.projName = self.getPROJCS()

    def getDataTypeFromBand(self, band_number=1):
        """
        This method returns the type of the values in the raster band
        """
        dataType = gdal.GetDataTypeName(self.band.DataType)
        return dataType

    def getRasterAttributeTableFromBand(self, band_number=1):
        '''
        This method derive a raster attribute table object from selected band
        If no rastter attribute table exist returns None.
        Args: band_number
        returns: raster attribute table object
        '''
        band = self.getBand(band_number)
        self.rat = band.GetDefaultRAT()
        return self.rat

    def rat2array(self):
        """
        This method convert the a raster attribute table(rat) to structured numpy array.
        Args: None
        returns: structured numpy array
        """
        columns = []
        colNames = []
        dtype = {0: 'int', 1: 'float', 2: 'U100'}
        for i in range(self.rat.GetColumnCount()):
            columns.append((str(self.rat.GetNameOfCol(i)).upper(),
                           str(dtype[self.rat.GetTypeOfCol(i)])))
            colNames.append(str(self.rat.GetNameOfCol(i)))
        table = np.zeros(shape=[self.rat.GetRowCount(), ], dtype=columns)
        for i in range(len(colNames)):
            array = self.rat.ReadAsArray(i).tolist()
            for row, element in enumerate(array):
                if columns[i][1] == "U100":
                    try:
                        table[row][i] = str(element, "utf8")
                    except BaseException:
                        table[row][i] = str(element, "cp1252")
                else:
                    table[row][i] = element
        return table

    def getMinimumFromBand(self, band_number=1):
        '''
        Returns minimum band value from specified rastr band.
        Default band is 1.
        '''
        band = self.getBand(band_number)
        self.min = self.band.GetMinimum()
        return self.min

    def getMaximumFromBand(self, band_number=1):
        '''
        Returns maximum band value from specified rastr band.
        Default band is 1.
        '''
        band = self.getBand(band_number)
        self.max = self.band.GetMaximum()
        return self.max

    def getColNames(self):
        '''
        Returns column names of the raster attribute table.
        '''
        names = []
        for i in range(self.rat.GetColumnCount()):
            names.append(str(self.rat.GetNameOfCol(i)))
        return names

    def getType(self):
        '''
        Returns the data type of raster band.
        '''
        self.band = self.data.GetRasterBand(1)
        self.type = gdal.GetDataTypeName(self.band.DataType)
        return self.type

    def getCellsize(self):
        '''
        Returns cellsize of the raster dataset.
        '''
        self.geoTrans = self.data.GetGeoTransform()
        self.cellsize = [self.geoTrans[1], self.geoTrans[5]]
        return self.cellsize

    def getBand(self, band_number=1):
        '''
        Returns a GDAL raster band object for a specified raster band.
        Parameters: Number of the raster band (default value is 1)
        Returns: <class 'osgeo.gdal.Band'>
        '''
        self.band = self.data.GetRasterBand(band_number)
        return self.band

    def size(self):
        '''
        Returns a GDAL raster size.
        Parameters: -
        Returns: (int, int) Number of rows and cols in the raster dataset
        '''
        self.cols = self.data.RasterXSize
        self.rows = self.data.RasterYSize
        return self.rows, self.cols

    def getArrayFromBand(self, band_number=1):
        '''
        Return a numpy array from defined raster band.
        Default band is 1.
        '''
        band = self.getBand(band_number)
        self.array = band.ReadAsArray()
        return self.array

    def getUniqueValuesFromBand(self, band_number=1):
        '''
        Return unique values from defined raster band. Ignores no data values.
        Default band is 1.
        '''
        band = self.getBand(band_number)
        array = self.band.ReadAsArray()
        self.uniqueValues = np.unique(array)
        self.uniqueValues = np.setdiff1d(self.uniqueValues, self.nodata)
        del array
        return self.uniqueValues

    def getUniqueValuesCountFromBand(self, band_number=1):
        '''
        Return count of unique values from defined raster band.
        Default band is 1.
        '''
        self.uniqueValuesCount = len(self.getUniqueValuesFromBand(band_number))
        return self.uniqueValuesCount

    def getProjection(self):
        '''
        Returns projection of the raster dataset
        '''
        self.proj = self.data.GetProjection()
        return self.proj

    def getSpatialReference(self):
        """
        Returns spatial Reference of the raster dataset.
        :return:
        """
        self.spatRef = osr.SpatialReference(self.proj)
        return self.spatRef

    def getEPSG_Code(self):
        """
        Returns EPSG Code.
        :return: int epsgCode
        """
        proj = self.data.GetProjection()
        self.spatRef = osr.SpatialReference(proj)
        self.epsgCode = self.spatRef.GetAuthorityCode('PROJCS')
        if self.epsgCode is None:
            self.epsgCode = self.spatRef.GetAuthorityCode('GEOGCS')
            try:
                with open(os.path.join("core", "gdal_data", "esri_wkid_list.txt"), "rb") as ESRI_names:
                    lines = ESRI_names.readlines()
                dictionary = {}
                for line in lines:
                    dictionary[str(line.split(",")[1]).lower()[:-3]] = str(line.split(",")[0])
                self.epsgCode = dictionary[str(self.spatRef.GetAttrValue('PROJCS')).lower()]
                if self.epsgCode is None:
                    self.epsgCode = dictionary[str(self.spatRef.GetAttrValue('GEOGCS')).lower()]
            except BaseException:
                self.epsgCode is None
        return self.epsgCode

    def getPROJCS(self):
        '''
        Returns Projection Name
        '''
        with open(os.path.join("core", "gdal_data", "esri_wkid_list.txt"), "rb") as ESRI_names:
            lines = ESRI_names.readlines()
        dictionary = {}
        for line in lines:
            split_str = str(line)[2:-1].split(",")
            dictionary[(split_str[1]).lower()[:-3]] = split_str[0]
        proj = self.data.GetProjection()
        self.spatRef = osr.SpatialReference(proj)
        self.projcs = self.spatRef.GetAttrValue("PROJCS")
        if self.projcs.lower() in dictionary.keys():
            try:
                sr = osr.SpatialReference()
                sr.ImportFromEPSG(int(dictionary[self.projcs.lower()]))
                self.projcs = sr.GetAttrValue("PROJCS")
            except BaseException:
                self.projcs = None
        return self.projcs

    def getDATUM(self):
        '''
        Returns the Datum of the spatial reference.
        '''
        proj = self.data.GetProjection()
        self.spatRef = osr.SpatialReference(proj)
        self.DATUM = self.spatRef.GetAttrValue('DATUM')
        return self.DATUM

    def getUNIT(self):
        '''
        Returns units used in spatial reference.
        '''
        proj = self.data.GetProjection()
        self.spatRef = osr.SpatialReference(proj)
        self.UNIT = self.spatRef.GetAttrValue('UNIT')
        return self.UNIT

    def getGeoTransorm(self):
        '''
        Returns geotransormation parameters of the raster dataset.
        These are: Min_x, Max_y, x_cellsize, y_cellsize.
        '''
        self.geoTrans = self.data.GetGeoTransform()
        return self.geoTrans

    def getStatisticsFromBand(self, band_number=1):
        '''
        Returns raster statistic from the specified raster band.
        '''
        band = self.getBand(band_number)
        self.stats = band.ComputeStatistics(False)
        return self.stats

    def getNoDataValueFromBand(self, band_number=1):
        '''
        Returns NoData value from the specified raster band (default band is 1).
        returns: NoData value from band (Default = 1).
        '''
        band = self.getBand(band_number)
        self.nodata = self.band.GetNoDataValue()
        return self.nodata

    def getColorTableFromBand(self, band_number=1):
        '''
        Returns GDAL Color Table from specified raster band if such exists.
        If no color Table is set for the raster band returns None.
        '''
        band = self.getBand(band_number)
        self.colorTable = band.GetColorTable()
        return self.colorTable

    def getExtent(self):
        '''
        Returns extent of the raster dataset given as list with:
        X_min, X_max, Y_min, Y_max
        '''
        self.rows, self.cols = self.size()
        self.geoTrans = self.data.GetGeoTransform()
        self.cellsize = [self.geoTrans[1], self.geoTrans[5]]
        self.extent = [self.geoTrans[0],
                       self.geoTrans[0] + self.cols * self.cellsize[0],
                       self.geoTrans[3] + self.rows * self.cellsize[1],
                       self.geoTrans[3]]
        return self.extent

    def getQuantile(self, band_number=1, qNumber=20):
        """
        Calculates quantils from the users defined parameters and flat_array
        and returns a list with class boundaries [min-rasterValue, Q1, ...Qn, max-rasterValue]
        """
        self.array = self.getArrayFromBand(band_number).astype(np.float32)
        self.min = self.getMinimumFromBand(band_number)
        self.max = self.getMaximumFromBand(band_number)
        self.nodata = self.getNoDataValueFromBand(band_number=band_number)
        self.array[np.where(self.array == self.nodata)] = np.nan
        interval = []
        k = 0
        for i in range(qNumber - 1):
            k = k + 100 / qNumber
            interval.append(k)
        self.quantile = np.nanpercentile(np.ravel(self.array), interval)
        self.intList = []
        for quant in self.quantile:
            self.intList.append(quant)
        if self.min not in self.intList:
            self.intList.insert(0, self.min)
        if self.max not in self.intList:
            self.intList.append(self.max)
        return self.intList

    def reclass(self, intList, outRasterPath):
        """
        Reclassify an raster dataset based on a class boundary list
        """
        outRasterPath = outRasterPath
        self.array = self.getArrayFromBand().astype(float)
        self.array[np.where(self.array == self.nodata)] = np.nan
        self.out_array = np.zeros_like(self.array)
        self.class_array = 0
        for i in range(len(intList) - 1):
            self.out_array = np.greater(self.array,
                                        intList[i]) * np.less_equal(self.array,
                                                                    intList[i + 1]) * (i + 1)
            self.class_array = self.out_array + self.class_array
        self.class_array[np.where(self.class_array == float(0))] = -9999
        NoData_value = -9999
        driver = gdal.GetDriverByName('GTiff')
        outRaster = driver.Create(outRasterPath, self.cols, self.rows, 1, gdal.GDT_Float32)
        outRaster.SetProjection(self.proj)
        outRaster.SetGeoTransform(self.geoTrans)
        band = outRaster.GetRasterBand(1)
        band.SetNoDataValue(NoData_value)
        outRaster.GetRasterBand(1).WriteArray(self.class_array)
        outRaster.FlushCache()
        return

    def polygonizeBand(self, outLocation, band_number=1):
        array = self.getArrayFromBand(band_number)
        array[np.where((array >= 0) & (array != self.nodata))] = 1
        NoData_value = -9999
        driver = gdal.GetDriverByName('MEM')
        outRaster = driver.Create('', self.cols, self.rows, 1, gdal.GDT_Float32)
        outRaster.SetProjection(self.proj)
        outRaster.SetGeoTransform(self.geoTrans)
        band = outRaster.GetRasterBand(1)
        band.SetNoDataValue(NoData_value)
        outRaster.GetRasterBand(1).WriteArray(array)
        band = outRaster.GetRasterBand(1)
        dst_layername = "Polygon"
        drv = ogr.GetDriverByName("ESRI Shapefile")
        dst_ds = drv.CreateDataSource(outLocation)
        dst_layer = dst_ds.CreateLayer(dst_layername, srs=None)
        gdal.Polygonize(band, None, dst_layer, -1, [], callback=None)
        band = None
        dst_ds = None
        dst_layer = None


class RasterLayer(Raster):
    '''
    Constructs a raster layer object which inherits methods from Raster object.
    '''

    def __init__(self, path):
        self.path = path
        self.data = gdal.Open(self.path)
        self.name = self.getLayerName()
        self.alias = self.getLayerName()
        self.extent = self.getExtent()
        self.datum = self.getDATUM()
        self.proj = self.getPROJCS()
        self.cellsize = self.getCellsize()
        self.nodata = self.getNoDataValueFromBand()
        self.colorMap = 'Gray2'
        self.properties = self.getRasterLayerProperties()
        self.rat = self.getRasterAttributeTableFromBand()
        self.band = self.getBand()
        self.type = gdal.GetDataTypeName(self.band.DataType)
        #self.colNames = self.getColNames()

    def getLayerName(self):
        '''
        Returns the basename of the dataset without extension.
        '''
        name = os.path.splitext(os.path.basename(self.path))[0]
        return name

    def setLayerName(self, newName):
        '''
        Set new layer name.
        Layer name is not editable by user. This function is called only
        once by construction of the layer object.
        '''
        self.name = newName
        self.properties['Name'] = newName
        return self.name

    def setAliasName(self, newName):
        '''
        Set new alias name to the raster layer.
        Alias name is the editable name of the layer,
        which can be specified by user. This function is
        called from layer properties option if the alias is changed.
        '''
        self.alias = newName
        self.properties['AliasName'] = newName
        return self.alias

    def setColorMap(self, colorMap):
        '''
        Set new color map to the raster layer.
        '''
        self.colorMap = colorMap
        self.layerProperties['ColorMap'] = colorMap
        return self.colorMap

    def getRasterLayerProperties(self):
        '''
        Returns layer properties library.
        '''
        self.layerProperties = {}
        self.layerProperties['Name'] = self.name
        self.layerProperties['Source'] = self.path
        self.layerProperties['Extent'] = self.extent
        self.layerProperties['Projection'] = self.proj
        self.layerProperties['Datum'] = self.datum
        self.layerProperties['Cellsize'] = self.cellsize
        self.layerProperties['Size'] = self.size()
        self.layerProperties['NoData'] = self.nodata
        self.layerProperties['EPSG'] = self.getEPSG_Code()
        self.layerProperties['Unit'] = self.getUNIT()
        self.layerProperties['Type'] = 'Raster layer'
        self.layerProperties['upperLeft'] = (self.extent[0], self.extent[3])
        self.layerProperties['ColorMap'] = self.colorMap
        self.layerProperties['AliasName'] = self.alias
        self.layerProperties['Description'] = ""
        return self.layerProperties


class Feature:
    '''
    Feature object


    Properties:
    ------------
    path - string of the feature path
    feat - pointer to the feature
    layer - feature layer
    count - number of features in the feature layer
    geom_type - feature geometry type (POINT, POLYLINE, POLYGON)
    spatial_ref - spatial reference of the feature
    extent - spatial extent of the feature layer

    Methods:
    -----------

    rasterizeLayer(self, maskPath, outRastPath, rasterizeMethod = "DEFAULT")
    euklideanDistance(self, maskPath, outRastPath)
    clip(self, clip_mask_layer, outPath)
    '''

    def __init__(self, path):
        self.path = path
        driverstr = self.getDriverFromExtension(os.path.splitext(path)[1].lower())
        self.driver = ogr.GetDriverByName(driverstr)
        self.feat = self.driver.Open(self.path)
        self.layer = self.getLayer()
        self.layerDefn = self.getLayerDefn()
        self.count = self.getFeatureCount()
        self.extent = self.layer.GetExtent()
        self.geometryType = self.getGeometryType()
        self.geometryName = self.getGeometryName()
        self.spatialRef = self.getSpatialRef()
        self.spatialRefWkt = self.getSpatialRefWkt()
        self.fieldNames = self.getFields()

    def getEPSG_Code(self):
        '''
        Returns EPSG Code.
        '''
        self.epsgCode = self.spatialRef.GetAuthorityCode('PROJCS')
        if self.epsgCode is None:
            self.epsgCode = self.spatialRef.GetAuthorityCode('GEOGCS')
            if self.epsgCode is None:
                try:
                    with open(os.path.join("core", "gdal_data", "esri_wkid_list.txt"), "rb") as ESRI_names:
                        lines = ESRI_names.readlines()
                    dictionary = {}
                    for line in lines:
                        dictionary[str(line.split(",")[1]).lower()[:-3]] = str(line.split(",")[0])
                    self.epsgCode = dictionary[str(self.spatialRef.GetAttrValue('PROJCS')).lower()]
                    if self.epsgCode is None:
                        self.epsgCode = dictionary[str(
                            self.spatialRef.GetAttrValue('GEOGCS')).lower()]
                except BaseException:
                    self.epsgCode is None
        return self.epsgCode

    def getFields(self):
        """
        Returns list of field names and corresponding types.
        :return: list of field names
        """
        fieldNames = []
        for i in range(self.layerDefn.GetFieldCount()):
            fieldDefn = self.layerDefn.GetFieldDefn(i)
            fieldNames.append([fieldDefn.name, fieldDefn.GetFieldTypeName(fieldDefn.GetType())])
        return fieldNames

    def getSpatialRefWkt(self):
        """
        Returns the spatial reference as Wkt (well known text)
        """
        spatRefWkt = self.spatialRef.ExportToWkt()
        return spatRefWkt

    def getLayer(self):
        '''
        Returns the layer instance of the feature
        '''
        layer = self.feat.GetLayer()
        return layer

    def getLayerDefn(self):
        '''
        Returns the layer definition instance of the feature
        '''
        layerDefn = self.layer.GetLayerDefn()
        return layerDefn

    def getFeatureCount(self):
        '''
        Returns number of features in feature layer.
        '''
        count = self.layer.GetFeatureCount()
        return count

    def getSpatialRef(self):
        '''
        Returns spatial reference of the feature layer.
        '''
        spatialRef = self.layer.GetSpatialRef()
        return spatialRef

    def getGeometryType(self):
        '''
        Returns the geometry type of the feature layer
        '''
        geometryType = self.layer.GetGeomType()
        return geometryType

    def getGeometryName(self):
        """
        Returns name of the geometry type
        """
        feat = self.layer.GetNextFeature()
        geomRef = feat.GetGeometryRef()
        geomName = geomRef.GetGeometryName()
        return geomName

    def rasterizeLayer(self, maskPath, outRasterPath, rasterizeMethod="DEFAULT"):
        '''
        Rasterizes a feature layer to raster generating a boolean mask. Two rasterize options
        DEFAULT or ALL_TOUCHED can be specified in advance.
        '''
        sourcePath = self.path
        mask = Raster(str(maskPath))
        noDataValue = 0
        driver = gdal.GetDriverByName('GTiff')
        out = driver.Create(str(outRasterPath), mask.cols, mask.rows, 1, gdal.GDT_Byte)
        out.SetProjection(mask.proj)
        out.SetGeoTransform(mask.geoTrans)
        outBand = out.GetRasterBand(1)
        outBand.SetNoDataValue(noDataValue)
        if rasterizeMethod == "DEFAULT":
            gdal.RasterizeLayer(out, [1], self.layer, burn_values=[1])
        else:
            gdal.RasterizeLayer(out, [1], self.layer, burn_values=[
                                1], options=['ALL_TOUCHED = TRUE'])
        out = None
        return outRasterPath

    def euklideanDistance(self, maskPath, outRasterPath):
        '''
        Compute the Euklidean distance to a feature in geographics units of the projection.
        The analysis extent must be given by a mask raster dataset.
        '''
        mask = Raster(maskPath)
        noDataValue = -9999
        driver = gdal.GetDriverByName('MEM')
        out = driver.Create('', mask.cols, mask.rows, 1, gdal.GDT_Byte)
        out.SetProjection(mask.proj)
        out.SetGeoTransform(mask.geoTrans)
        outBand = out.GetRasterBand(1)
        outBand.SetNoDataValue(noDataValue)
        gdal.RasterizeLayer(out, [1], self.layer, burn_values=[1])
        driver = gdal.GetDriverByName('GTiff')
        euklidean = driver.Create(outRasterPath, mask.cols, mask.rows, 1, gdal.GDT_Float32)
        euklidean.SetProjection(mask.proj)
        euklidean.SetGeoTransform(mask.geoTrans)
        euklideanBand = euklidean.GetRasterBand(1)
        euklideanBand.SetNoDataValue(noDataValue)
        options = ['DISTUNITS=GEO']
        gdal.ComputeProximity(outBand, euklideanBand, options, callback=None)
        euklideanBand.ComputeStatistics(False)
        out = None
        euclidean = None

    def getDriverFromExtension(self, ext: str) -> str:
        """
        Returns a string with which to call GetDriverByName based on file extension. Expects an all
        lowercase extension.
        """
        #   extension: Driver Name
        driver_dic = {
            ".geojson": "GeoJSON",
            ".kml": "KML",
            ".shp": "ESRI Shapefile"
        }
        return driver_dic[ext]
