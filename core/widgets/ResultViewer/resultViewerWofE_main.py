# -*- coding: utf-8 -*-

from osgeo import gdal, ogr, osr, gdalconst
import sys
import os
import math
import time
import numpy as np
from openpyxl import Workbook
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import logging

from core.libs.GDAL_Libs.Layers import Raster, Feature, RasterLayer
from core.uis.ResultViewer_ui.resultsViewerWofE_ui import Ui_MainWindow
from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog
from core.libs.LSAT_Messages.messages_main import Messenger
from core.libs.Reporting.woe_report import woe_report  # used to convert info to string
from core.widgets.ResultViewer.plotViewer_main import PlotViewer
from core.widgets.ResultViewer.tableViewer_main import TableViewer
from core.widgets.ResultViewer.shared_resultviewer import shared_resultfunc


class ResultViewerWofE(QMainWindow):
    def __init__(self, projectLocation, path, layerName, result, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(':/icons/Icons/Chart_Bar_Big.png'))
        self.setWindowTitle(self.tr("Results for {}").format(layerName))
        self.loadModelData(path, result)
        self.ui.modelTreeWidget.expandAll()
        self.ui.modelTreeWidget.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.modelTreeWidget.header().setStretchLastSection(False)
        table = TableViewer(projectLocation, layerName, result, "WoE")
        self.ui.tableTabGridLayout.addWidget(table)
        graphics = PlotViewer(layerName, result)
        self.ui.graphicsTabGridLayout.addWidget(graphics)

    def loadModelData(self, path, result):
        """
        Updates first tab with information about the WoE Calculation.
        """
        self.ui.tabWidget.setTabText(0, os.path.basename(result["source"][0]))
        # path to npz
        shared_resultfunc.setTopLevelItem(
            self, 0, self.tr("File Path"), path, self.ui.modelTreeWidget)
        # path to and info about used feature file
        shared_resultfunc.setTopLevelItem(
            self, 1, self.tr("Training dataset"), woe_report._get_featurepath(
                self, result), self.ui.modelTreeWidget)
        shared_resultfunc.setChildItem(
            self, 1, 0, self.tr("Subsampling type"), woe_report._get_subsample_type(
                self, result["metadata"][3]), self.ui.modelTreeWidget)
        shared_resultfunc.setChildItem(
            self, 1, 1, self.tr("Sample size [%]"), str(
                result["metadata"][2]), self.ui.modelTreeWidget)
        shared_resultfunc.setChildItem(
            self, 1, 2, self.tr("Number of subsamples"), str(
                result["metadata"][4]), self.ui.modelTreeWidget)
        try:
            result["metadata"][5]
            shared_resultfunc.setChildItem(
                self, 1, 3, self.tr("Seed used to Initialize random"), str(
                    result["metadata"][5]), self.ui.modelTreeWidget)
        except IndexError: # only on the fly subsampling uses a randomseed
            pass 
        # path to raster file
        shared_resultfunc.setTopLevelItem(
            self,
            2,
            self.tr("Input raster"),
            result["source"][0],
            self.ui.modelTreeWidget)
        # model metrics
        shared_resultfunc.setTopLevelItem(self, 3, self.tr(
            "Model metrics"), None, self.ui.modelTreeWidget)
        if result["auc"].size == 1:
            shared_resultfunc.setChildItem(
                self, 3, 0, self.tr("AUC"), "{:.5f}".format(
                    result["auc"]), self.ui.modelTreeWidget, str(
                    result["auc"]))
        else:
            shared_resultfunc.setChildItem(
                self, 3, 0, self.tr("Mean AUC"), "{:.5f}".format(
                    np.nanmean(
                        result["auc"])), self.ui.modelTreeWidget, str(
                    result["auc"]))
            shared_resultfunc.setChildItem(
                self, 3, 1, self.tr("Median AUC"), "{:.5f}".format(
                    np.nanmedian(
                        result["auc"])), self.ui.modelTreeWidget, str(
                    result["auc"]))
            shared_resultfunc.setChildItem(
                self, 3, 2, self.tr("Minimum AUC"), "{:.5f}".format(
                    np.nanmin(
                        result["auc"])), self.ui.modelTreeWidget, str(
                    result["auc"]))
            shared_resultfunc.setChildItem(
                self, 3, 3, self.tr("Maximum AUC"), "{:.5f}".format(
                    np.nanmax(
                        result["auc"])), self.ui.modelTreeWidget, str(
                    result["auc"]))
