# -*- coding: utf-8 -*-

from osgeo import gdal, ogr, osr, gdalconst
import os
import math
import time
import urllib
import numpy as np
import csv
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *
import xml.etree.ElementTree as ET
import sys
import os
import logging
from core.libs.Management import Project_configuration as config
from core.libs.GDAL_Libs.Layers import Raster, Feature, RasterLayer
from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog
from core.libs.LSAT_Messages.messages_main import Messenger
from core.widgets.GDAL_SpatialRefLib.searchCS_main import MainForm as SR_Lib
from core.widgets.ImportData.importData_dialog import ReprojectionSettings
from core.widgets.ImportData.importData_importRaster import ImportRaster
from core.uis.ProjectManagement_ui.project_ui import Ui_Project


class NewProject(QDialog):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_Project()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(':/icons/Icons/new_project.png'))
        self.setWindowTitle(self.tr("New Project"))
        self.fileDialog = CustomFileDialog()
        self.message = Messenger()
        self.projectLocation = ""

        self.cs_lib_paths = [
            os.path.join(
                "core", "gdal_data", "gcs.csv"), os.path.join(
                "core", "gdal_data", "pcs.csv")]
        self.epsg_list = []
        self.cr_names = []
        self.list_len = []
        for path in self.cs_lib_paths:
            with open(path) as dbfile:
                reader = csv.DictReader(dbfile)
                for row in reader:
                    self.epsg_list.append(str(row["COORD_REF_SYS_CODE"]))
                    self.cr_names.append(str(row["COORD_REF_SYS_NAME"]))
                self.list_len.append(len(self.epsg_list))

        self.ui.createProjectPushButton.setDefault(False)
        self.ui.createProjectPushButton.setAutoDefault(False)

        self.ui.projectLocationLineEdit.setStyleSheet(
            'QLineEdit { background-color: %s }' % '#f2bdb0')
        self.ui.projectNameLineEdit.setStyleSheet('QLineEdit { background-color: %s }' % '#f2bdb0')

        self.intValidator = QIntValidator()
        self.intLocale = self.intValidator.locale()
        self.intLocale.toInt(".")
        self.dblValidator = QDoubleValidator()
        self.dblValidator.setNotation(0)  # validator has standard notation: i.e. 0.123
        self.dblValidator.setLocale(QtCore.QLocale("en_US"))
        # some countries by default use ',' as seperator for decimals, but we use '.'

        self.ui.epsgCodeLineEdit.setStyleSheet('QLineEdit { background-color: %s }' % '#f2bdb0')
        self.ui.epsgCodeLineEdit.setValidator(self.intValidator)
        self.ui.epsgCodeLineEdit.textChanged.connect(self.epsgTextChanged)

        self.ui.maskRadioButton.toggled.connect(self.on_spatialRefRadioButtons_clicked)

        self.ui.topLineEdit.setValidator(self.dblValidator)
        self.ui.topLineEdit.setStyleSheet('QLineEdit { background-color: %s }' % '#f2bdb0')
        self.ui.leftLineEdit.setValidator(self.dblValidator)
        self.ui.leftLineEdit.setStyleSheet('QLineEdit { background-color: %s }' % '#f2bdb0')
        self.ui.rightLineEdit.setValidator(self.dblValidator)
        self.ui.rightLineEdit.setStyleSheet('QLineEdit { background-color: %s }' % '#f2bdb0')
        self.ui.bottomLineEdit.setValidator(self.dblValidator)
        self.ui.bottomLineEdit.setStyleSheet('QLineEdit { background-color: %s }' % '#f2bdb0')

        self.ui.topLineEdit.textChanged.connect(self.checkUnits)
        self.ui.leftLineEdit.textChanged.connect(self.checkUnits)
        self.ui.rightLineEdit.textChanged.connect(self.checkUnits)
        self.ui.bottomLineEdit.textChanged.connect(self.checkUnits)
        self.ui.projectNameLineEdit.textChanged.connect(self.projectNameLineEditStyle)

        self.ui.cellsizeLineEdit.setValidator(self.dblValidator)
        self.ui.cellsizeLineEdit.setStyleSheet('QLineEdit { background-color: %s }' % '#f2bdb0')
        self.ui.cellsizeLineEdit.textChanged.connect(self.cellsizeLineEditStyle)

    def epsgTextChanged(self):
        if str(self.ui.epsgCodeLineEdit.text()) in self.epsg_list:
            self.ui.epsgCodeLineEdit.setStyleSheet('QLineEdit { background-color: %s }' % '#b5f2b0')
            idx = self.epsg_list.index(str(self.ui.epsgCodeLineEdit.text()))
            self.ui.srNameLineEdit.setText(str(self.cr_names[idx]))
            if idx <= self.list_len[0]:
                self.ui.cellsizeLabel.setText(self.tr("Cell size [decimal degree]"))
            else:
                self.ui.cellsizeLabel.setText(self.tr("Cell size [meter]"))
        else:
            self.ui.epsgCodeLineEdit.setStyleSheet('QLineEdit { background-color: %s }' % '#f2bdb0')

        self.checkUnits()

    def cellsizeLineEditStyle(self):
        if self.ui.cellsizeLineEdit.text() == "":
            self.ui.cellsizeLineEdit.setStyleSheet('QLineEdit { background-color: %s }' % '#f2bdb0')
        else:
            self.ui.cellsizeLineEdit.setStyleSheet('QLineEdit { background-color: %s }' % '#b5f2b0')

    def projectNameLineEditStyle(self):
        if (self.ui.projectNameLineEdit.text() == "" or
            # Checks if projectNameLineEdit is a valid windows path
                any(x in ["<", ">", ":", "\"", "/", "\\", "|", "?", "*"] for x in str(self.ui.projectNameLineEdit.text()))):
            self.ui.projectNameLineEdit.setStyleSheet(
                'QLineEdit { background-color: %s }' % '#f2bdb0')
        else:
            self.ui.projectNameLineEdit.setStyleSheet(
                'QLineEdit { background-color: %s }' % '#b5f2b0')

    @pyqtSlot()
    def on_projectLocationToolButton_clicked(self):
        """
        Sets the project location.
        :return: None
        """
        self.fileDialog.openDirectory(os.getcwd())
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
            self.projectLocation = os.path.normpath(self.fileDialog.selectedFiles()[0])
            self.ui.projectLocationLineEdit.setStyleSheet(
                'QLineEdit { background-color: %s }' % '#b5f2b0')
            self.ui.projectLocationLineEdit.setText(self.projectLocation)
        else:
            self.ui.projectLocationLineEdit.setStyleSheet(
                'QLineEdit { background-color: %s }' % '#f2bdb0')

    def on_spatialRefRadioButtons_clicked(self):
        """
        Gets called by toogling the Spatial Reference radioButtons.
        Checks which Spatial Reference choice the user wants to use.
        """
        if self.ui.maskRadioButton.isChecked():
            self._updateSpatialRefChoiceInUi(True)
        elif self.ui.customExtentRadioButton.isChecked():
            self._updateSpatialRefChoiceInUi(False)

    def _updateSpatialRefChoiceInUi(self, spatialRef: bool) -> None:
        """
        Gets called by on_spatialRefRadioButtons_clicked. Updated the Ui.
        spatialRef is True if maskRaster is selected and False if a custom Extent is selected.
        """
        self.ui.maskRasterDatasetLineEdit.setEnabled(spatialRef)
        self.ui.maskRasterDatasetToolButton.setEnabled(spatialRef)
        self.ui.topLineEdit.setEnabled(not spatialRef)
        self.ui.leftLineEdit.setEnabled(not spatialRef)
        self.ui.rightLineEdit.setEnabled(not spatialRef)
        self.ui.bottomLineEdit.setEnabled(not spatialRef)
        self.ui.cellsizeLineEdit.setEnabled(not spatialRef)
        if not spatialRef: # if custom extent clear mask path
            self.ui.maskRasterDatasetLineEdit.setText("")

    @pyqtSlot()
    def on_epsgToolButton_clicked(self):
        """
        Calls the Spatial Reference Library
        :return: None
        """
        self.epsgSearch = SR_Lib(self)
        self.epsgSearch.show()

    def setEPSG_From_Search(self, epsg, name):
        """
        Sets the epsg code selected in the Spatial Reference Library dialog
        :param epsg: int epsg-code
        :param name: string, spatial reference name
        :return: None
        """
        self.ui.epsgCodeLineEdit.setText(str(epsg))
        self.ui.srNameLineEdit.setText(str(name))
        # call the function to update the background color of epsgCodeLineEdit
        self.updateEPSGLineColor()
        self.checkUnits()

    @pyqtSlot()
    def on_maskRasterDatasetToolButton_clicked(self):
        """
        Set the parameter raster dataset.
        """
        self.fileDialog.openRasterFile(os.getcwd())
        if self.fileDialog.exec_() and self.fileDialog.selectedFiles():
            rasterFile = os.path.normpath(self.fileDialog.selectedFiles()[0])
            self.ui.maskRasterDatasetLineEdit.setText(rasterFile)
            self.raster = Raster(rasterFile)
            epsg = self.raster.getEPSG_Code()
            extent = self.raster.extent
            self.cols = self.raster.cols
            self.rows = self.raster.rows
            self.proj = self.raster.getPROJCS()
            self.ui.epsgCodeLineEdit.setText(str(epsg))
            # call the function to update the background color of epsgCodeLineEdit
            self.updateEPSGLineColor()
            self.ui.leftLineEdit.setText(str(extent[0]))
            self.ui.rightLineEdit.setText(str(extent[1]))
            self.ui.bottomLineEdit.setText(str(extent[2]))
            self.ui.topLineEdit.setText(str(extent[3]))
            self.ui.cellsizeLineEdit.setText(self.checkCellSquare(self.raster.cellsize))
            self.ui.srNameLineEdit.setText(str(self.proj))
            self.checkUnits()

    def checkCellSquare(self, rasterCellSize: list) -> str:
        if rasterCellSize[0] == -rasterCellSize[1]: # 0 = X; 1 = Y
            return str(rasterCellSize[0])
        else:
            return self.tr("No support for non-square cells.")

    def updateEPSGLineColor(self):
        if str(self.ui.epsgCodeLineEdit.text()) == "None":
            self.ui.epsgCodeLineEdit.setStyleSheet('QLineEdit { background-color: %s }' % '#f2bdb0')
        else:
            self.ui.epsgCodeLineEdit.setStyleSheet('QLineEdit { background-color: %s }' % '#b5f2b0')

    def checkUnits(self):
        sr = osr.SpatialReference()
        self.check = False
        if self.ui.epsgCodeLineEdit.text() != "None" and self.ui.epsgCodeLineEdit.text() != "":
            if self.ui.epsgCodeLineEdit.text() not in self.epsg_list:
                return
            else:
                sr.ImportFromEPSG(int(self.ui.epsgCodeLineEdit.text()))
                unit = sr.GetAttrValue("UNIT")
            red = 'QLineEdit { background-color: %s }' % '#f2bdb0'
            green = 'QLineEdit { background-color: %s }' % '#b5f2b0'
            if unit == "degree":
                # check the top boundary
                if (self.ui.topLineEdit.text() == "" or
                   not (-90.0 < float(self.ui.topLineEdit.text()) < 90.0)):
                    self.ui.topLineEdit.setStyleSheet(red)
                else:
                    self.ui.topLineEdit.setStyleSheet(green)

                # check the left boundary
                if (self.ui.leftLineEdit.text() == "" or
                   not (-180.0 < float(self.ui.leftLineEdit.text()) < 180.0)):
                    self.ui.leftLineEdit.setStyleSheet(red)
                else:
                    self.ui.leftLineEdit.setStyleSheet(green)

                # check the right boundary
                if (self.ui.rightLineEdit.text() == "" or
                        not (-180.0 < float(self.ui.rightLineEdit.text()) < 180.0)):
                    self.ui.rightLineEdit.setStyleSheet(red)
                else:
                    self.ui.rightLineEdit.setStyleSheet(green)

                # check the bottom boundary
                if (self.ui.bottomLineEdit.text() == "" or
                        not (-180.0 < float(self.ui.bottomLineEdit.text()) < 180.0)):
                    self.ui.bottomLineEdit.setStyleSheet(red)
                else:
                    self.ui.bottomLineEdit.setStyleSheet(green)

            elif unit == "metre":
                # check the top boundary
                if self.ui.topLineEdit.text() == "":
                    self.ui.topLineEdit.setStyleSheet(red)
                else:
                    self.ui.topLineEdit.setStyleSheet(green)

                # check the left boundary
                if self.ui.leftLineEdit.text() == "":
                    self.ui.leftLineEdit.setStyleSheet(red)
                else:
                    self.ui.leftLineEdit.setStyleSheet(green)

                # check the right boundary
                if self.ui.rightLineEdit.text() == "":
                    self.ui.rightLineEdit.setStyleSheet(red)
                else:
                    self.ui.rightLineEdit.setStyleSheet(green)

                # check the bottom boundary
                if self.ui.bottomLineEdit.text() == "":
                    self.ui.bottomLineEdit.setStyleSheet(red)
                else:
                    self.ui.bottomLineEdit.setStyleSheet(green)

            # Following checks are the same for all unit types
            # Check if right boundary > left boundary
            # try except is necessary to deal with empty string upon startup
            try:
                if float(self.ui.rightLineEdit.text()) - float(self.ui.leftLineEdit.text()) <= 0.0:
                    self.ui.rightLineEdit.setStyleSheet(red)
                    self.ui.leftLineEdit.setStyleSheet(red)
            except ValueError:  # LineEdit is not convertible to float
                self.ui.rightLineEdit.setStyleSheet(red)
                self.ui.leftLineEdit.setStyleSheet(red)

            # Check if top boundary > bottom boundary
            try:
                if float(self.ui.topLineEdit.text()) - float(self.ui.bottomLineEdit.text()) <= 0.0:
                    self.ui.topLineEdit.setStyleSheet(red)
                    self.ui.bottomLineEdit.setStyleSheet(red)
            except ValueError:  # LineEdit is not convertible to float
                self.ui.topLineEdit.setStyleSheet(red)
                self.ui.bottomLineEdit.setStyleSheet(red)

            if self.ui.cellsizeLineEdit.text() == "":
                return
            try:
                float(self.ui.cellsizeLineEdit.text())
            except ValueError: # user loaded a raster with non-square cells
                self.ui.cellsizeLineEdit.setStyleSheet(red)
            self.check = True

    def createPolygon(self, projectRasterPath: str):
        """
        Creates a polygon (region.shp) in the project folder with the regions extent.
        projectRasterPath is the path to the region.tif used.
        """
        ring = ogr.Geometry(ogr.wkbLinearRing)
        raster = Raster(projectRasterPath)
        band = raster.data.GetRasterBand(1)
        directory = os.path.dirname(projectRasterPath)
        shpPath = os.path.join(directory, 'region.shp')
        driver = ogr.GetDriverByName("ESRI Shapefile")
        datasource = driver.CreateDataSource(shpPath)
        srsRegion = osr.SpatialReference()
        srsRegion.ImportFromEPSG(int(self.ui.epsgCodeLineEdit.text()))
        layer = datasource.CreateLayer("region", srs=srsRegion)
        gdal.Polygonize(band, band, layer, -1, [])
        self.area = 0
        for feature in layer:
            geom = feature.GetGeometryRef()
            area = geom.GetArea()
            self.area += area # TODO move to own function
        raster = None

    def createProjectMetaDataFile(self, pathProject: str) -> None:
        """
        This method creates a project metadata xml-file.
        :return: None
        """
        projectName = self.ui.projectNameLineEdit.text()
        metaDataFile = os.path.join(pathProject, "metadata.xml")
        epsg = str(self.ui.epsgCodeLineEdit.text())
        proj = str(self.ui.srNameLineEdit.text())
        top = str(self.ui.topLineEdit.text())
        left = str(self.ui.leftLineEdit.text())
        right = str(self.ui.rightLineEdit.text())
        bottom = str(self.ui.bottomLineEdit.text())
        area = str(self.area)
        cellsize = str(self.ui.cellsizeLineEdit.text())
        descr = self.ui.descriptionTextEdit.toPlainText()
        root = ET.Element("Project")
        name = ET.SubElement(root, "Name", name=projectName)
        extent = ET.SubElement(root, "Extent")
        top_ = ET.SubElement(extent, "top", top=top)
        left_ = ET.SubElement(extent, "left", left=left)
        right_ = ET.SubElement(extent, "right", right=right)
        bottom_ = ET.SubElement(extent, "bottom", bottom=bottom)
        area = ET.SubElement(extent, "Area", area=area)
        spatRef = ET.SubElement(root, "SpatialReference", epsg=epsg)
        projection = ET.SubElement(root, "Projection", projection=proj)
        cell = ET.SubElement(root, "Cellsize", cellsize=cellsize)
        description = ET.SubElement(root, "Description", descr=str(descr))
        tree = ET.ElementTree(root)
        tree.write(metaDataFile)
        del metaDataFile

    def _validateInputs(self) -> bool:
        if (str(self.projectLocation) == "" or
                any(x in ["<", ">", "|", "?", "*"] for x in str(self.projectLocation))):
            QMessageBox.warning(self, self.tr("Project location invalid or missing!"), self.tr(
                "Please specify the location of the project to proceed!"))
            return False
        if (self.ui.projectNameLineEdit.text() == "" or any(
                x in ["<", ">", ":", "|", "?", "*"] for x in self.ui.projectNameLineEdit.text())):
            QMessageBox.warning(self, self.tr("Project name invalid or missing!"),
                                self.tr("Please specify the name of the project to proceed!"))
            return False
        if self.ui.epsgCodeLineEdit.text() == "":
            QMessageBox.warning(self, self.tr("EPSG missing"), self.tr(
                "Please specify the spatial reference of the project to proceed!"))
            return False
        if self.ui.topLineEdit.text() == "" or self.ui.leftLineEdit.text() == "" or self.ui.rightLineEdit.text(
        ) == "" or self.ui.bottomLineEdit.text() == "" or self.ui.cellsizeLineEdit.text() == "":
            QMessageBox.warning(self, self.tr("Extent missing"), self.tr(
                "Please specify the extent of the project to proceed!"))
            return False
        try:
            float(self.ui.cellsizeLineEdit.text())
        except ValueError:
            QMessageBox.warning(self, self.tr("Invalid cell size"), self.tr(
                "Please use a raster with square cells to proceed!"))
            return False
        return True

    @pyqtSlot()
    def on_createProjectPushButton_clicked(self):
        if not self._validateInputs():
            return
        # Create Folder structure
        pathProject = os.path.join(self.projectLocation, self.ui.projectNameLineEdit.text())
        if not os.path.exists(pathProject):
            pathRegionRaster = self.createProjectDirectory(pathProject)
        else:
            QMessageBox.warning(
                self,
                self.tr("Project with this name already exists in this directory!"),
                self.tr("Specify other project name or change the host directory!"))
            return
        # Create initial project files
        self.createRaster(pathRegionRaster)
        self.createPolygon(pathRegionRaster)
        self.createProjectMetaDataFile(pathProject)
        self.accept()
        self.message.getLoggingInfoProjectCreated(pathProject)
        if os.path.isfile(self.ui.maskRasterDatasetLineEdit.text()):
            self.importMask(
                self.ui.maskRasterDatasetLineEdit.text(),
                pathRegionRaster,
                os.path.join(
                    pathProject,
                    "data",
                    "params"))

    def createProjectDirectory(self, pathProject: str) -> str:
        """
        Creates the projects directory structure at pathProject.
        Returns path to projects region.tif.
        """
        os.makedirs(pathProject)
        pathRegionRaster = os.path.join(pathProject, "region.tif")
        os.makedirs(os.path.join(pathProject, "workspace"))
        os.makedirs(os.path.join(pathProject, "data", "params"))
        os.makedirs(os.path.join(pathProject, "data", "inventory", "test"))
        os.makedirs(os.path.join(pathProject, "data", "inventory", "training"))
        resultfolders = ("susceptibility_maps", "statistics")
        for resultfolder in resultfolders:
            os.makedirs(os.path.join(pathProject, "results", resultfolder))
        analysistypes = ("ANN", "AHP", "LR", "WoE")
        for analysis in analysistypes:
            os.makedirs(os.path.join(pathProject, "results", analysis, "tables"))
            os.makedirs(os.path.join(pathProject, "results", analysis, "reports"))
            os.makedirs(os.path.join(pathProject, "results", analysis, "rasters"))
        return pathRegionRaster

    def createRaster(self, pathRegionRaster: str) -> None:
        """
        Creates region.tif at pathRegionRaster
        """
        self.spr = osr.SpatialReference()
        self.spr.ImportFromEPSG(int(self.ui.epsgCodeLineEdit.text()))
        NoData_value = -9999
        driver = gdal.GetDriverByName('GTiff')
        top = float(self.ui.topLineEdit.text())
        bottom = float(self.ui.bottomLineEdit.text())
        left = float(self.ui.leftLineEdit.text())
        right = float(self.ui.rightLineEdit.text())
        cellsize = float(self.ui.cellsizeLineEdit.text())
        cols = int(round((right - left) / cellsize, 0))
        rows = int(round((top - bottom) / cellsize, 0))
        outRaster = driver.Create(pathRegionRaster, cols, rows, 1, gdal.GDT_Int16)
        outRaster.SetProjection(self.spr.ExportToWkt())
        # Project uses mask raster
        if os.path.isfile(self.ui.maskRasterDatasetLineEdit.text()):
            geoTransform = (
                self.raster.geoTrans[0],
                cellsize,
                self.raster.geoTrans[2],
                self.raster.geoTrans[3],
                self.raster.geoTrans[4],
                -cellsize)
            array = self.raster.getArrayFromBand().astype(np.float32)
            if np.isnan(self.raster.nodata):
                np.nan_to_num(array, copy=False, nan=-9999)
                rasterNoData = -9999
            else:
                rasterNoData = self.raster.nodata
            array[array != rasterNoData] = 1
            array[array == rasterNoData] = -9999
        # Project coordinates by hand
        else:
            geoTransform = (left, cellsize, 0.0, top, 0.0, -cellsize)
            array = np.ones(shape=(rows, cols))
        outRaster.SetGeoTransform(geoTransform)
        band = outRaster.GetRasterBand(1)
        band.SetNoDataValue(NoData_value)

        outRaster.GetRasterBand(1).WriteArray(array)
        outRaster = None

    def importMask(self, rasterpath: str, maskpath: str, outputdir: str):
        """
        Allows the user to add his mask raster to the project.
        """
        importquestion = QMessageBox.question(
            self,
            self.tr("Add {} to project parameters?").format(
                os.path.basename(rasterpath)),
            self.tr("Do you want to add {} to the project parameters?").format(rasterpath),
            QMessageBox.Yes | QMessageBox.No)
        if importquestion == QMessageBox.Yes:
            self.threadpool = QThreadPool()
            resamplingtypedialog = ReprojectionSettings(rasterpath, maskpath)
            resamplingtypedialog.show()
            if resamplingtypedialog.exec_():  # Finish Dialog before we continue
                resamplingtype = resamplingtypedialog.resamplingType
            else:  # User closed the dialog
                logging.info(self.tr("{} import canceled.").format(rasterpath))
                return
            self.importraster = ImportRaster(rasterpath, maskpath, outputdir, resamplingtype)
            self.importraster.infoSignal.connect(self.logfromimport)
            self.importraster.rasterImport()

    def logfromimport(self, string):
        """
        Gets called by signal from Importthread to display a string in the Main Log.
        """
        logging.info(string)
