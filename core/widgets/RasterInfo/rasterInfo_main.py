# -*- coding: cp1252 -*-

from osgeo import gdal, ogr, osr, gdalconst
import os
import math
import time
import numpy as np
import webbrowser
import xml.etree.ElementTree as ET
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import os
import logging

from core.uis.RasterInfo_ui.RasterInfo_ui import Ui_RasterInfo
from core.libs.GDAL_Libs.Layers import Raster


class RasterInfo(QMainWindow):
    def __init__(self, rasterPath, parent=None):
        QMainWindow.__init__(self, parent)
        self.ui = Ui_RasterInfo()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(":/icons/Icons/raster_info.png"))

        self.path = rasterPath
        self.setWindowTitle(self.tr("Raster info - {}").format(os.path.basename(self.path)))
        self.tree = self.ui.treeWidget
        self.tree.expandAll()

        self.raster = Raster(self.path)
        # set source path
        self.populateTopLevelItem(0, self.path)
        # set data type
        self.populateTopLevelItem(1, self.raster.dataType)
        # set Spatial Reference EPSG
        self.populateChildItem(2, 0, str(self.raster.epsg))
        # set Spatial Reference Projection
        self.populateChildItem(2, 1, str(self.raster.projName))
        # set Extent
        self.populateChildItem(3, 0, str(self.raster.extent[3]))
        self.populateChildItem(3, 1, str(self.raster.extent[0]))
        self.populateChildItem(3, 2, str(self.raster.extent[1]))
        self.populateChildItem(3, 3, str(self.raster.extent[2]))
        area = self.raster.cols * self.raster.rows * self.raster.cellsize[0]**2
        self.populateChildItem(3, 4, str(area))
        # set Dimensions
        self.populateChildItem(4, 0, str(self.raster.cols))
        self.populateChildItem(4, 1, str(self.raster.rows))

        # set Cellsize
        self.populateChildItem(5, 0, str(self.raster.cellsize[0]))
        self.populateChildItem(5, 1, str(abs(self.raster.cellsize[1])))

        self.populateChildItem(6, 0, str(self.raster.min))
        self.populateChildItem(6, 1, str(self.raster.max))
        self.populateChildItem(6, 2, str(self.raster.nodata))

        self.button = QPushButton(self.tr("Details"))
        self.button.setFixedWidth(100)
        self.button.clicked.connect(self.EPSG_details)
        item = QTreeWidgetItem()
        child_item = self.tree.topLevelItem(2).addChild(item)
        self.tree.setItemWidget(item, 1, self.button)

    def EPSG_details(self):
        string = "https://epsg.io/%s" % (str(self.raster.epsg))
        webbrowser.open(string)

    def closeEvent(self, event):
        """
        Closes the widget and cleanup data.
        :param event: closeEvent
        :return: None
        """
        if hasattr(self, "raster"):
            del self.raster

    def populateTopLevelItem(self, index, text):
        item = self.tree.topLevelItem(index)
        item.setText(1, text)

    def populateChildItem(self, index_parent, index_child, text):
        item = self.tree.topLevelItem(index_parent)
        subitem = item.child(index_child)
        subitem.setText(1, text)
