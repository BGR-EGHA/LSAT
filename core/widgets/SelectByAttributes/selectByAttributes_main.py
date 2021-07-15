# -*- coding: utf-8 -*-

from osgeo import gdal, ogr, osr, gdalconst
import os
import math
import time
import numpy as np
import re
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *
import sys
import os
import logging
from core.libs.LSAT_Messages.messages_main import Messenger
from core.libs.GDAL_Libs.Layers import Feature, Raster
from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog
from core.uis.SelectByAttributes_ui.SelectByAttributes_ui import Ui_SelectByAttributes


class SelectByAttributes(QMainWindow):
    def __init__(self, projectLocation="", parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_SelectByAttributes()
        self.ui.setupUi(self)
        self.message = Messenger()
        self.fileDialog = CustomFileDialog()
        self.projectLocation = projectLocation
        self.setWindowTitle(self.tr("Subset By Attributes"))
        self.setWindowIcon(QIcon(':/icons/Icons/SelectByAttributes.png'))
        self.progress = QProgressBar()
        self.ui.statusbar.addPermanentWidget(self.progress)

        if self.projectLocation != "":
            self.maskRaster = Raster(os.path.join(self.projectLocation, "region.tif"))
            self.srProject = osr.SpatialReference()
            self.srProject.ImportFromEPSG(int(self.maskRaster.epsg))

    @pyqtSlot()
    def on_inFeatureToolButton_clicked(self):
        self.fileDialog.openFeatureFile(self.projectLocation)
        if self.fileDialog.exec_() and self.fileDialog.selectedFiles():
            fileName = os.path.normpath(self.fileDialog.selectedFiles()[0])
            self.ui.inFeatureComboBox.addItem(fileName)
            idx = self.ui.inFeatureComboBox.findText(fileName)
            self.ui.inFeatureComboBox.setCurrentIndex(idx)
            try:
                self.loadFeature()
            except Exception as e:
                logging.error(str(e))

    @pyqtSlot()
    def on_outFeatureToolButton_clicked(self):
        self.fileDialog.openFeatureFile(self.projectLocation)
        if self.fileDialog.exec_() and self.fileDialog.selectedFiles():
            fileName = os.path.normpath(self.fileDialog.selectedFiles()[0])
            if fileName.lower().endswith(".shp"):
                self.ui.outFeatureLineEdit.setText(fileName)
            else:
                self.ui.outFeatureLineEdit.setText(fileName + ".shp")

    def loadFeature(self):
        self.ui.fieldsListView.disconnect()
        self.feat = Feature(self.ui.inFeatureComboBox.currentText())
        self.geom = self.feat.geometryType
        self.featSR = osr.SpatialReference()
        self.featSR.ImportFromWkt(self.feat.spatialRefWkt)
        fieldNames = self.feat.fieldNames
        fields = []
        for fieldName in fieldNames:
            fields.append(fieldName[0])
        self.fieldListModel = ListModel(fields)
        self.ui.fieldsListView.setModel(self.fieldListModel)
        self.selectModel = self.ui.fieldsListView.selectionModel()
        self.selectModel.selectionChanged.connect(self.onFieldsListView_selectionChanged)
        self.ui.fieldsListView.doubleClicked.connect(self.onFieldsListView_doubleClicked)

    def onFieldsListView_selectionChanged(self):
        self.getFieldType()

    def getFieldType(self):
        idx = self.ui.fieldsListView.currentIndex().row()
        fieldType = self.feat.fieldNames[idx][1]
        return fieldType

    @pyqtSlot(QModelIndex)
    def onFieldsListView_doubleClicked(self, index):
        self.addStringtoTextEdit(str(index.data()))

    @pyqtSlot(QModelIndex)
    def onUniqueListView_doubleClicked(self, index):
        # removes count from string before adding to textEdit.
        removefromend = len((re.findall('\\((.*?)\\)', index.data())
                            [-1])) + 3  # space and 2 parantheses
        string = index.data()[:-removefromend]
        stringTypes = ["String", "Date"]
        if self.fieldType in stringTypes:
            express = "'{}'".format(string)
        else:
            express = string
        self.addStringtoTextEdit(express)

    @pyqtSlot()
    def on_getUniqueValuesPushButton_clicked(self):
        if not self.ui.inFeatureComboBox.currentText() or not len(self.selectModel.selectedIndexes()):
            return
        self.ui.uniqueListView.disconnect()
        idx = self.ui.fieldsListView.currentIndex().row()
        values = []
        self.feat = Feature(self.ui.inFeatureComboBox.currentText())
        for f in self.feat.layer:
            values.append(str(f.GetField(idx)))
        uniques, counts = np.unique(np.array(values), return_counts=True)
        uniques = uniques.tolist()
        counts = [" ({})".format(count) for count in counts.tolist()]
        combined = [unique + count for unique, count in zip(uniques, counts)]
        self.uniquesListModel = ListModel(combined)
        self.ui.uniqueListView.setModel(self.uniquesListModel)
        self.ui.uniqueListView.doubleClicked.connect(self.onUniqueListView_doubleClicked)
        self.fieldType = self.getFieldType()

    # Set Operators handling
    @pyqtSlot()
    def on_equalToolButton_clicked(self):
        self.addStringtoTextEdit(" =")

    @pyqtSlot()
    def on_nullToolButton_clicked(self):
        self.addStringtoTextEdit(" NULL")

    @pyqtSlot()
    def on_likeToolButton_clicked(self):
        self.addStringtoTextEdit(" LIKE")

    @pyqtSlot()
    def on_notToolButton_clicked(self):
        self.addStringtoTextEdit(" NOT")

    @pyqtSlot()
    def on_greaterToolButton_clicked(self):
        self.addStringtoTextEdit(" >")

    @pyqtSlot()
    def on_greater_equalToolButton_clicked(self):
        self.addStringtoTextEdit(" >=")

    @pyqtSlot()
    def on_andToolButton_clicked(self):
        self.addStringtoTextEdit(" AND")

    @pyqtSlot()
    def on_isToolButton_clicked(self):
        self.addStringtoTextEdit(" IS")

    @pyqtSlot()
    def on_lessToolButton_clicked(self):
        self.addStringtoTextEdit(" <")

    @pyqtSlot()
    def on_less_equalToolButton_clicked(self):
        self.addStringtoTextEdit(" <=")

    @pyqtSlot()
    def on_orToolButton_clicked(self):
        self.addStringtoTextEdit(" OR")

    @pyqtSlot()
    def on_inToolButton_clicked(self):
        self.addStringtoTextEdit(" IN")

    def addStringtoTextEdit(self, str2add: str):
        """
        Gets called by toolButtons and clicking on values in tables.
        Adds the corresponding text to the textEdit at the cursor position.
        Updates to the cursor position.
        """
        cursor = self.ui.textEdit.textCursor()
        pos = cursor.position()
        text = self.ui.textEdit.toPlainText()
        newText = text[:pos] + str2add + text[pos:]
        self.ui.textEdit.setPlainText(newText)
        cursor.setPosition(pos + len(str2add))
        self.ui.textEdit.setTextCursor(cursor)

    @pyqtSlot()
    def on_applyPushButton_clicked(self):
        if self.ui.outFeatureLineEdit.text() == "":
            self.message.WarningMissingInput()
            return
        if self.ui.inFeatureComboBox.currentText() == "":
            self.message.WarningMissingInput()
            return
        if self.ui.textEdit.toPlainText() == "":
            self.message.WarningMissingInput()
            return
        self._updateProgress(True)
        expression = self.ui.textEdit.toPlainText()
        self.feat.layer.SetAttributeFilter(str(expression))
        if self.projectLocation != "":
            try:
                self.coordTrans = osr.CoordinateTransformation(self.featSR, self.srProject)
            except Exception as e:
                logging.error(str(e.message))
        # Create the output
        driver = ogr.GetDriverByName("ESRI Shapefile")
        outDataSource = driver.CreateDataSource(str(self.ui.outFeatureLineEdit.text()))
        outLayer = outDataSource.CreateLayer('inventory', self.featSR, self.geom)

        # Get the output Layer's Feature Definition
        outFeatureDefn = outLayer.GetLayerDefn()

        # Add input Layer Fields to the output Layer if it is the one we want
        inLayerDefn = self.feat.layerDefn
        for i in range(0, inLayerDefn.GetFieldCount()):
            fieldDefn = inLayerDefn.GetFieldDefn(i)
            fieldName = fieldDefn.GetName()
            outLayer.CreateField(fieldDefn)

        for f in self.feat.layer:
            outFeature = ogr.Feature(outFeatureDefn)

            # Add field values from input Layer
            for i in range(0, outFeatureDefn.GetFieldCount()):
                fieldDefn = outFeatureDefn.GetFieldDefn(i)
                fieldName = fieldDefn.GetName()

                outFeature.SetField(outFeatureDefn.GetFieldDefn(i).GetNameRef(),
                                    f.GetField(i))

            geometry = f.GetGeometryRef()
            if self.projectLocation != "":  # and self.projection == True:
                try:
                    geometry.Transform(self.coordTrans)
                except Exception as e:
                    logging.error(str(e))
            outFeature.SetGeometry(geometry)
            outLayer.CreateFeature(outFeature)

            outFeature = None

        # Save and close DataSources
        self.feat = None
        outDataSource = None
        logging.info(self.tr("Selection successful."))
        self._updateProgress(False)
        self.close()

    def _updateProgress(self, switch: bool) -> None:
        """
        Gets called by on_applyPushButton_clicked.
        Changes the progressbar to tell user something is going on.
        """
        self.progress.setRange(0, int(not switch))

    @pyqtSlot()
    def on_cancelPushButton_clicked(self):
        self.close()


class ListModel(QAbstractListModel):
    def __init__(self, datain, parent=None, *args):
        """
         datain: a list of lists
        """
        QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = datain

    def rowCount(self, parent):
        return len(self.arraydata)

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        if role != Qt.DisplayRole:
            return QVariant()

        return QVariant(self.arraydata[index.row()])
