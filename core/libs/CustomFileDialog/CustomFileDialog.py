# -*- coding: utf-8 -*-

from osgeo import gdal, ogr
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import os
import sys
import logging
from osgeo import gdal
import core.resources.icons_rc
from core.libs.GDAL_Libs.Layers import Raster, Feature


class CustomIconProvider(QFileIconProvider):
    """
    This class controls the appearence of the icons in the catalog
    """

    def __init__(self, parent=None):
        QFileIconProvider.__init__(self)

    def icon(self, fileInfo):
        '''
        Reimplement Qt method
        '''
        if isinstance(fileInfo, QFileIconProvider.IconType):
            return super(CustomIconProvider, self).icon(fileInfo)
        else:
            qfileinfo = fileInfo
            fname = os.path.normpath(str(qfileinfo.absoluteFilePath()))

        if os.path.isdir(fname):
            if os.path.basename(fname).startswith("."):
                pass
            else:
                try:
                    if "metadata.xml" in os.listdir(fname):
                        return QIcon(":icons\\Icons\\project_icon.png")
                    else:
                        return super(CustomIconProvider, self).icon(fileInfo)
                except BaseException:
                    super(CustomIconProvider, self).icon(fileInfo)
        try:
            if os.path.isfile(fname):
                ext = os.path.splitext(fname)[1].lower()

            if ext == ".tif":
                return QIcon(':/icons/Icons/raster_icon.png')
            elif ext == ".docx":
                return QIcon(":/icons/Icons/WordReport.png")
            elif ext == ".xlsx":
                return QIcon(":/icons/Icons/OpenInExcel.png")
            elif ext == ".npz" and os.path.basename(os.path.dirname(fname)) == "tables":
                return QIcon(":/icons/Icons/File_Table.png")
            elif ext == ".npz" and os.path.basename(os.path.dirname(fname)) == "susceptibility_maps":
                return QIcon(":/icons/Icons/model.png")
            elif ext == ".shp":
                shapefile = ogr.Open(str(fname))
                layer = shapefile.GetLayer()
                feat = layer.GetFeature(0)
                geomRef = feat.GetGeometryRef()
                geometryName = geomRef.GetGeometryName()

                if geometryName == "POINT":
                    return QIcon(':/icons/Icons/point_shape.png')
                elif geometryName == "POLYGON":
                    return QIcon(':/icons/Icons/polygon_shape.png')
                elif geometryName == "POLYLINE":
                    return QIcon(':/icons/Icons/polyline_shape.png')
                else:
                    return super(CustomIconProvider, self).icon(fileInfo)
            else:
                return super(CustomIconProvider, self).icon(fileInfo)
        except BaseException:
            return super(CustomIconProvider, self).icon(fileInfo)


class CustomFileDialog(QFileDialog):
    def __init__(self, parent=None):
        QFileDialog.__init__(self)
        self.valFiles = []
        self.iconProvider = CustomIconProvider()
        self.setIconProvider(self.iconProvider)
        self.setOptions(QFileDialog.DontUseNativeDialog)
        self.filesSelected.connect(self.checkFileNames)

    def openProject(self, path=os.getcwd()):
        """
        Opens the directory file dialog with LSAT Project string.
        :return: None
        """
        self.setWindowTitle(self.tr("Open Project"))
        icon = QIcon(':/icons/Icons/open_project.png')
        self.setWindowIcon(icon)
        self.setDirectory(path)
        self.setIconProvider(self.iconProvider)
        self.setFileMode(QFileDialog.Directory)
        self.setOptions(QFileDialog.ShowDirsOnly)

    def openDirectory(self, path=os.getcwd()):
        """
        Opens the standard directory file dialog.
        :return: None
        """
        self.setWindowTitle(self.tr("Open directory"))
        icon = QIcon(':/icons/Icons/Folder.png')
        self.setWindowIcon(icon)
        self.setDirectory(path)
        self.setIconProvider(self.iconProvider)
        self.setFileMode(QFileDialog.Directory)
        self.setOptions(QFileDialog.ShowDirsOnly)

    def openRasterFile(self, path=""):
        """
        Opens raster file dialog.
        :return: None
        """
        self.setWindowTitle(self.tr("Open raster file"))
        icon = QIcon(':/icons/Icons/project_icon.png')
        self.setWindowIcon(icon)
        self.setDirectory(path)
        self.setIconProvider(self.iconProvider)
        self.setFileMode(QFileDialog.ExistingFile)
        self.setNameFilter(self.tr("Raster (*.tif)"))
        self.setOptions(QFileDialog.DontUseNativeDialog)

    def openRasterFiles(self, path=""):
        """
        Opens raster file dialog.
        :return: None
        """
        self.setWindowTitle(self.tr("Open raster files"))
        icon = QIcon(':/icons/Icons/project_icon.png')
        self.setWindowIcon(icon)
        self.setDirectory(path)
        self.setIconProvider(self.iconProvider)
        self.setFileMode(QFileDialog.ExistingFiles)
        self.setNameFilter(self.tr("Raster (*.tif)"))
        self.setOptions(QFileDialog.DontUseNativeDialog)

    def openModelFile(self, path=""):
        """
        Opens model file dialog.
        :return: None
        """
        self.setWindowTitle(self.tr("Open model"))
        icon = QIcon(':/icons/Icons/project_icon.png')
        self.setWindowIcon(icon)
        self.setDirectory(path)
        self.setIconProvider(self.iconProvider)
        self.setFileMode(QFileDialog.AnyFile)
        self.setNameFilter(self.tr("Model (*.npz)"))

    def openFeatureFile(self, path=""):
        """
        Opens feature dialog.
        :return: None
        """
        self.setWindowTitle(self.tr("Open feature file"))
        icon = QIcon(':/icons/Icons/project_icon.png')
        self.setWindowIcon(icon)
        self.setDirectory(path)
        self.setIconProvider(self.iconProvider)
        self.setFileMode(QFileDialog.AnyFile)
        self.setNameFilter(self.tr("Shapefile or KML or GeoJSON (*.shp *.kml *.geojson)"))

    def openTextFile(self, path=""):
        """
        Opens text file dialog.
        :return: None
        """
        self.setWindowTitle(self.tr("Open text or doc file"))
        icon = QIcon(':/icons/Icons/project_icon.png')
        self.setWindowIcon(icon)
        self.setDirectory(path)
        self.setIconProvider(self.iconProvider)
        self.setFileMode(QFileDialog.AnyFile)
        self.setNameFilter(self.tr("Text or Word (*.txt *.docx)"))

    def saveFeatureFile(self, path="", filename=""):
        """
        Opens shapefile dialog.
        :return: None
        """
        self.setWindowTitle(self.tr("Save feature file"))
        icon = QIcon(':/icons/Icons/project_icon.png')
        self.setWindowIcon(icon)
        self.setDirectory(path)
        self.setIconProvider(self.iconProvider)
        self.setFileMode(QFileDialog.AnyFile)
        self.selectFile(str(filename))
        self.setNameFilter(self.tr("Shapefile (*.shp);; KML (*.kml);; GeoJSON (*.geojson)"))

    def saveRasterFile(self, directory="", filename=""):
        """
        Opens save raster file dialog.
        :return: None
        """
        self.setWindowTitle(self.tr("Save raster"))
        icon = QIcon(':/icons/Icons/project_icon.png')
        self.setWindowIcon(icon)
        self.setIconProvider(self.iconProvider)
        self.setFileMode(QFileDialog.AnyFile)
        self.setDirectory(str(directory))
        self.selectFile(str(filename))
        self.setNameFilter(self.tr("Raster (*.tif)"))

    def saveExcelFile(self, directory="", filename=""):
        """
        Opens save excel file dialog.
        """
        self.setWindowTitle(self.tr("Save table"))
        self.setWindowIcon(QIcon(":/icons/Icons/OpenInExcel.png"))
        self.setIconProvider(self.iconProvider)
        self.setFileMode(QFileDialog.AnyFile)
        self.setDirectory(str(directory))
        self.selectFile(str(filename))
        self.setNameFilter(self.tr("Excel table (*.xlsx)"))

    def saveImageFile(self, directory="", filename=""):
        """
        Opens save image file dialog.
        """
        self.setWindowTitle(self.tr("Save Image"))
        self.setWindowIcon(QIcon(":/icons/Icons/project_icon.png"))
        self.setIconProvider(self.iconProvider)
        self.setFileMode(QFileDialog.AnyFile)
        self.setDirectory(str(directory))
        self.selectFile(str(filename))
        self.setNameFilter(self.tr("PNG (*.png)"))

    def checkFileNames(self, Files: list) -> None:
        """
        Gets called when the user closes the Dialog.
        This function warns the user if the selected names are not valid for windows.
        We only check printable characters, if the user somehow enters a non printing character he
        is beyond saving.
        At the moment checking the extension is done where the files are needed.
        Files is a list of filepaths the user selected just like self.selectedFiles()
        """
        bad_windows = ("\\", "/", ":", "*", "?", "\"", "<", ">", "|")
        bad_fullName = (
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9")
        bad_end = (" ", ".")
        for File in Files:
            fileName = os.path.basename(File)
            fileNameNoExt = os.path.splitext(fileName)[0]
            if fileNameNoExt in bad_fullName:
                logging.warning(self.tr("Reserved name. Consider picking another name."))
                continue
            if any((bad in bad_windows) for bad in fileName):
                logging.warning(self.tr("Reserved characters. Consider picking another name."))
                continue
            try:
                if fileName == fileNameNoExt and fileName[-1] in bad_end:
                    logging.warning(self.tr("Invalid end. Consider picking another name."))
                    continue
            except IndexError:  # empty string
                pass
