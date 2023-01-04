import numpy as np
import os
from osgeo import gdal, gdalconst
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import shutil
from core.libs.GDAL_Libs.Layers import Raster


class ImportRaster(QObject):
    infoSignal = pyqtSignal(str)
    """
    Supports 2 Signals:
    infoSignal: To tell the user what is going on during the import.
    doneSignal: To tell the user when the import is finished.
    Both only use strings.
    """

    def __init__(self, rasterpath: str, maskpath: str, outputdir: str, resamplingtype: str) -> str:
        """
        If called by another part of LSAT the resamplingtype can be given as either "CUBIC",
        "NEAREST", or "BILINEAR". Usually importData_dialog is used for this.
        """
        super().__init__()
        self.rasterpath = rasterpath
        self.maskpath = maskpath
        self.outputdir = outputdir
        self.resamplingtype = resamplingtype

    def rasterImport(self):
        """
        Gets called by importData_main and every other part of LSAT that wants to add rasters to a
        project. User first has to initalize the class.
        """
        raster = Raster(self.rasterpath)
        mask = Raster(self.maskpath)
        if self.validate(raster, mask):
            newrasterpath = self.onlycopy(self.rasterpath, self.outputdir, raster)
        else:
            datatype = self.getDataType(raster.type)
            resamplingtypefunc = self.getResampletypeFunc(self.resamplingtype)
            newrasterpath = self.reproject(
                raster, mask, self.outputdir, resamplingtypefunc, datatype)
        self.infoSignal.emit(self.tr("{} created.").format(newrasterpath))

    def validate(self, raster, mask) -> bool:
        """
        Returns a bool indicating if the raster needs to be reprojected or can just be copied over.
        Calls subfunctions that tell the user if (return bool) and where (logging signal) the
        rasters differ.
        """
        epsg = self._checkEPSG(raster, mask)
        dimension = self._checkDimension(raster, mask)
        origin = self._checkOrigin(raster, mask)
        nodatalocation = self._checkNoDataLocation(raster, mask)
        nodatavalue = self._checkNoDataValue(raster, mask)
        return all((epsg, dimension, origin, nodatalocation, nodatavalue))

    def _checkEPSG(self, raster, mask) -> bool:
        """
        Gets called by validate.
        """
        if raster.epsg == mask.epsg:
            return True
        else:
            self.infoSignal.emit(
                self.tr("EPSG differs. Mask: {} - Raster: {}").format(mask.epsg, raster.epsg))
            return False

    def _checkDimension(self, raster, mask) -> bool:
        """
        Gets called by validate.
        """
        if raster.cols == mask.cols and raster.rows == mask.rows:
            return True
        else:
            self.infoSignal.emit(self.tr(
                "Rows/Cols differ. Mask: {}/{} - Raster: {}/{}").format(mask.rows, mask.cols, raster.rows, raster.cols))
            return False

    def _checkOrigin(self, raster, mask) -> bool:
        """
        Gets called by validate.
        """
        if raster.geoTrans[0] == mask.geoTrans[0]:
            return True
        else:
            self.infoSignal.emit(
                self.tr("Origin differs. Mask: {} - Raster: {}").format(mask.geoTrans[0], raster.geoTrans[0]))
            return False

    def _checkNoDataLocation(self, raster, mask) -> bool:
        """
        Gets called by validate.
        """
        rasterarray = raster.getArrayFromBand()
        # "nan" breaks the comparison so we temporarily convert it to -9999
        if raster.nodata:
            if np.isnan(raster.nodata):
                np.nan_to_num(rasterarray, copy=False, nan=-9999)
                rasterNoDataLocation = np.argwhere(rasterarray == -9999)
            else:
                rasterNoDataLocation = np.argwhere(rasterarray == raster.nodata)
        else:
            rasterNoDataLocation = np.array(((), ()))  # tuple of two empty tuples to indicate absence of NoData
        maskarray = mask.getArrayFromBand()
        maskNoDataLocation = np.argwhere(maskarray == mask.nodata)
        if np.array_equal(rasterNoDataLocation, maskNoDataLocation):
            return True
        else:
            self.infoSignal.emit(self.tr(
                "Location of NoData differs."))
            if maskNoDataLocation.shape[0] != rasterNoDataLocation.shape[0]:
                self.infoSignal.emit(self.tr(
                    "Amount of NoData differs. Mask: {} - Raster: {}").format(
                    maskNoDataLocation.shape[0], rasterNoDataLocation.shape[0]))
            return False

    def _checkNoDataValue(self, raster, mask) -> bool:
        """
        Gets called by validate
        """
        if raster.nodata == mask.nodata:
            return True
        else:
            self.infoSignal.emit(
                self.tr("NoData value differs. Mask: {} - Raster: {}").format(mask.nodata, raster.nodata))
            return False

    def onlycopy(self, rasterpath, outputdir, raster):
        """
        Gets called by rasterImport if validate finds out that the files do not differ.
        We check if a file with the same name exists in the directory and only then copy the raster
        from its original location into the output directory.
        Returns string with new rasters path.
        """
        self.infoSignal.emit(self.tr("{} does not need to be reprojected.").format(rasterpath))
        newrasterpath = os.path.join(outputdir, os.path.basename(rasterpath))
        if os.path.isfile(newrasterpath):
            self.infoSignal.emit(
                self.tr("{} already exists and will be overwritten.").format(newrasterpath))
        shutil.copy2(rasterpath, newrasterpath)
        newraster = Raster(newrasterpath)
        self.checkRAT(raster, newraster)
        return newrasterpath

    def checkRAT(self, raster, newraster) -> None:
        """
        Gets called by reproject and onlycopy.
        Checks if the imported raster had a RAT. If that RAT is viable it gets copied over.
        Else LSAT creates a basic RAT if the raster is viable.
        Calls generateBasicRAT.
        """
        if raster.rat is None:
            if "Float" in raster.type or raster.uniqueValuesCount > 500:
                self.infoSignal.emit(
                    self.tr("No RAT created. {} is either type float or has too many values.").format(
                        raster.path))
            else:
                self.generateBasicRAT(newraster)
                self.infoSignal.emit(self.tr("Append basic RAT."))
        else:
            newraster.band.SetDefaultRAT(raster.rat)
            self.infoSignal.emit(self.tr("Append existing RAT."))

    def generateBasicRAT(self, newraster: object) -> None:
        """
        Gets called by checkRAT
        Adds a basic RAT to a raster based on its raster values.
        """
        rat = gdal.RasterAttributeTable()
        values, counts = np.unique(newraster.getArrayFromBand(), return_counts=True)
        if newraster.nodata in values:
            index = np.where(values == newraster.nodata)
            values = np.delete(values, index)
            counts = np.delete(counts, index)
        rat.CreateColumn("OID", gdal.GFT_Integer, gdalconst.GFU_MinMax)
        rat.CreateColumn("VALUE", gdal.GFT_Real, gdalconst.GFU_MinMax)
        rat.CreateColumn("COUNT", gdal.GFT_Integer, gdalconst.GFU_MinMax)
        for i in range(len(values)):
            rat.SetValueAsInt(i, 0, int(i))
            rat.SetValueAsDouble(i, 1, float(values[i]))
            rat.SetValueAsInt(i, 2, int(counts[i]))
        newraster.band.SetDefaultRAT(rat)

    def getDataType(self, rastertype: object) -> object:
        """
        Returns the corresponding gdal constants for the raster type.
        """
        datatype_dic = {
            "Float": gdal.GDT_Float32,
            "Float32": gdal.GDT_Float32,
            "Float64": gdal.GDT_Float64,
            "Int": gdal.GDT_Int16,
            "Int16": gdal.GDT_Int16,
            "UInt16": gdal.GDT_Int32,
            "Int32": gdal.GDT_Int32,
            "Byte": gdal.GDT_Int16
        }
        return datatype_dic[rastertype]

    def getResampletypeFunc(self, resamplingtype: str) -> object:
        """
        Returns the corresponding gdalconstant for each resamplingtype string.
        """
        resample_dic = {
            "BILINEAR": gdalconst.GRA_Bilinear,
            "CUBIC": gdalconst.GRA_Cubic,
            "NEAREST": gdalconst.GRA_NearestNeighbour
        }
        return resample_dic[resamplingtype]

    def reproject(self, raster, mask, outputdir, resamplingtypefunc, datatype):
        """
        Reprojects the raster and returns a string of the path, where the new one was created.
        """
        newrasterpath = os.path.join(outputdir, os.path.basename(raster.path))
        if os.path.isfile(newrasterpath):
            self.infoSignal.emit(
                self.tr("{} already exists and will be overwritten.").format(newrasterpath))
        newraster = gdal.GetDriverByName("Gtiff").Create(
            newrasterpath, mask.cols, mask.rows, 1, datatype)
        # 1 is the number of bands
        newraster.SetGeoTransform(mask.geoTrans)
        newraster.SetProjection(mask.proj)
        newraster.GetRasterBand(1).SetNoDataValue(mask.nodata)
        gdalraster = gdal.Open(raster.path, gdalconst.GA_ReadOnly)
        gdal.ReprojectImage(gdalraster, newraster, raster.proj, mask.proj, resamplingtypefunc)
        newraster.FlushCache()
        self.updateNoDataValue(newrasterpath, mask)
        newraster = Raster(newrasterpath)
        self.checkRAT(raster, newraster)
        return newrasterpath

    def updateNoDataValue(self, newrasterpath, mask) -> None:
        """
        Updates the new raster to have NoData where the mask has NoData.
        """
        dataset = gdal.Open(newrasterpath, gdal.GA_Update)
        band = dataset.GetRasterBand(1)
        newrasterarray = band.ReadAsArray()
        maskarray = mask.getArrayFromBand()
        newrasterarray[maskarray == mask.nodata] = mask.nodata
        band.WriteArray(newrasterarray)
        band.SetNoDataValue(mask.nodata)
        band.ComputeStatistics(False)
        dataset.FlushCache()
        self.infoSignal.emit(self.tr("NoData values updated."))
