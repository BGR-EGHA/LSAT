# -*- coding: cp1252 -*-

from osgeo import gdal, ogr, osr, gdalconst
import os
import math
import time
import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import os
import logging
import webbrowser
from core.uis.FeatureInfo_ui.FeatureInfo_ui import Ui_FeatureInfo
from core.libs.GDAL_Libs.Layers import Feature


class FeatureInfo(QMainWindow):
    def __init__(self, featurePath, parent=None):
        QMainWindow.__init__(self, parent)
        self.ui = Ui_FeatureInfo()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(":/icons/Icons/featureInfo.png"))

        self.path = featurePath
        self.setWindowTitle(self.tr("Feature info - {}").format(os.path.basename(self.path)))
        self.tree = self.ui.treeWidget
        self.tree.expandAll()

        self.feat = Feature(self.path)
        # set source path
        self.populateTopLevelItem(0, str(self.path))
        # set data type
        self.populateTopLevelItem(1, str(self.feat.geometryName))
        # set feature count
        self.populateTopLevelItem(2, str(self.feat.count))
        # set fields
        for i, name in enumerate(self.feat.fieldNames):
            item = QTreeWidgetItem()
            child_item = self.tree.topLevelItem(3).addChild(item)
            self.populateChildItem(3, i, str(name[0]) + " - " + str(name[1]))

        # set epsg code
        self.populateChildItem(4, 0, str(self.feat.getEPSG_Code()))
        self.populateChildItem(4, 1, str(self.feat.spatialRef.GetAttrValue('PROJCS')))

        # set Extent
        self.populateChildItem(5, 0, str(self.feat.extent[3]))
        self.populateChildItem(5, 1, str(self.feat.extent[0]))
        self.populateChildItem(5, 2, str(self.feat.extent[1]))
        self.populateChildItem(5, 3, str(self.feat.extent[2]))

        self.button = QPushButton(self.tr("Details"))
        self.button.setFixedWidth(100)
        self.button.clicked.connect(self.EPSG_details)
        item = QTreeWidgetItem()
        child_item = self.tree.topLevelItem(4).addChild(item)
        self.tree.setItemWidget(item, 1, self.button)

    def EPSG_details(self):
        string = "https://epsg.io/%s" % (str(self.feat.getEPSG_Code()))
        webbrowser.open(string)

    def populateTopLevelItem(self, index, text):
        item = self.tree.topLevelItem(index)
        item.setText(1, text)

    def populateChildItem(self, index_parent, index_child, text):
        item = self.tree.topLevelItem(index_parent)
        subitem = item.child(index_child)
        subitem.setText(1, text)

    def closeEvent(self, event):
        """
        Closes the widget and cleans up data.
        :param event: closeEvent
        :return: None
        """
        del self.feat
