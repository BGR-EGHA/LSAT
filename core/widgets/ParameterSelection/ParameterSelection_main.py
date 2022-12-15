# -*- coding: utf-8 -*-

import os
import sys
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from core.libs.Management.LayerManagement import LayerManagement
from core.libs.GDAL_Libs.Layers import RasterLayer
from core.uis.ParameterSelection_ui.ParameterSelection_ui import Ui_ParameterSelection


class ParameterSelection(QMainWindow):
    apply_clicked = QtCore.pyqtSignal(list)

    def __init__(self, projectLocation=None, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_ParameterSelection()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(':/icons/Icons/Settings.png'))
        self.allchecked = False
        self.projectLocation = projectLocation
        self.dataPath = os.path.join(self.projectLocation, "data")
        self.paramsPath = os.path.join(self.dataPath, "params")
        self.tree = self.ui.treeWidget

        self.LM = LayerManagement()
        self.tree.itemChanged.connect(self.updateView)
        self.getParams()
        self.updateView()

    @pyqtSlot()
    def on_toggleselectAllLayersPushButton_clicked(self):
        """
        Selects/Deselects all layers in the selection tree widget.
        :return: None
        """
        root = self.tree.invisibleRootItem()
        if self.allchecked:
            self.ui.toggleselectAllLayersPushButton.setText(self.tr("Select All Layers"))
            setto = Qt.Unchecked
        else:
            self.ui.toggleselectAllLayersPushButton.setText(self.tr("Deselect All Layers"))
            setto = Qt.Checked
        for i in range(root.childCount()):
            item = self.tree.topLevelItem(i)
            # We toggle between selecting and unselecting all parameters
            item.setCheckState(0, setto)
        self.allchecked = not self.allchecked
        self.updateView()

    def getParams(self):
        """
        Loads list of parameters included in the params folder
        to a tree widget for selection.
        :return: None
        """
        for file_name in os.listdir(self.paramsPath):
            baseName = os.path.splitext(file_name)[0]
            file_type = os.path.splitext(file_name)[1].lower()
            if file_type == ".tif":
                self.layer = RasterLayer(os.path.join(self.paramsPath, file_name))
                item = QTreeWidgetItem()
                self.LM.addTreeContent(hash(str(item)), self.layer.properties)
                item.setText(0, baseName)
                item.setCheckState(0, Qt.Unchecked)
                self.tree.addTopLevelItem(item)

    def updateView(self):
        count = 0
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = self.tree.topLevelItem(i)
            if item.checkState(0):
                count += 1
            else:
                count += 0
        if count > 0:
            self.ui.applyPushButton.setEnabled(1)
        else:
            self.ui.applyPushButton.setEnabled(0)

    @pyqtSlot()
    def on_applyPushButton_clicked(self):
        """
        Emits a signal with a list to the paths of the selected rasters.
        """
        root = self.tree.invisibleRootItem()
        self.selectedLayers = []
        for i in range(root.childCount()):
            item = self.tree.topLevelItem(i)
            if item.checkState(0):
                self.selectedLayers.append((self.LM.treeContent[hash(str(item))]["Source"]))
        self.apply_clicked.emit(self.selectedLayers)
        self.close()
