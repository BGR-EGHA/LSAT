# -*- coding: utf-8 -*-

from osgeo import gdal, gdalconst
import sys
import os
import math
import time
import numpy as np
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog as FileDialog
from core.libs.GDAL_Libs.Layers import Raster
from core.libs.LSAT_Messages.messages_main import Messenger
from core.uis.Zoning_ui.Zoning_ui import Ui_ZoningGUI
from core.widgets.ModelInfo.modelinfo_main import ModelInfo
import traceback
import logging


class Zoning(QMainWindow):
    def __init__(self, modelPath=None, projectLocation=None, parent=None):
        QMainWindow.__init__(self, parent)
        self.ui = Ui_ZoningGUI()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(':/icons/Icons/zoning.png'))
        self.ui.addRowToolButton.setIcon(QIcon(':/icons/Icons/plus.png'))
        self.ui.deleteRowToolButton.setIcon(QIcon(':/icons/Icons/minus.png'))

        # custom file dialog
        self.fileDialog = FileDialog(parent=self)
        # color dialog
        self.colorDialog = QColorDialog()
        # set LSAT Messenger
        self.msg = Messenger()
        # add progress bar
        self.progress = QProgressBar()
        self.progress.setFixedWidth(200)
        self.ui.statusbar.addPermanentWidget(self.progress)

        self.previewer = Viewer()
        self.tabWidget = QTabWidget()

        # set tableWidget signals
        # on doubleClick -> calls the color dialog
        self.ui.tableWidget.cellDoubleClicked.connect(self.getColorDialog)
        # on cell clicked -> used to store the current cell value as a part of validation
        self.ui.tableWidget.cellClicked.connect(self.on_cell_clicked)
        self.ui.tableWidget.cellChanged.connect(self.on_tableWidget_cellChanged)
        self.projectLocation = projectLocation
        self.setupROC()
        self.defaultColors = [QColor(255, 0, 0, 100), QColor(255, 100, 0, 100),
                              QColor(255, 255, 0, 100), QColor(0, 170, 0, 100),
                              QColor(100, 120, 200, 100), QColor(100, 120, 200, 100),
                              QColor(100, 120, 200, 100), QColor(100, 120, 200, 100),
                              QColor(100, 120, 200, 100), QColor(100, 120, 200, 100),
                              QColor(100, 120, 200, 100), QColor(100, 120, 200, 100)]

        self.thresholdValues = [[100, "LABEL", 100], ]
        # self.thresholdValues[n][1]: targeted landslide area in zone [%] - int
        # self.thresholdValues[n][2]: Zone - str
        # self.thresholdValues[n][3]: total summed landslide area [0][3]+[1][3]+.. - int
        count = self.populate_modelComboBox(projectLocation)
        if modelPath:
            self.modelPath = os.path.normpath(modelPath)
            self.append_modelComboBox(self.modelPath, count) # Sets index to modelPath
        elif count == 0 and not modelPath: # enable buttons if there are npz in the directory
            self.enableButtons(False)

    def enableButtons(self, status: bool):
        self.ui.deleteRowToolButton.setEnabled(status)
        self.ui.addRowToolButton.setEnabled(status)
        self.ui.resetTablePushButton.setEnabled(status)
        self.ui.updatePushButton.setEnabled(status)

    def populate_modelComboBox(self, projectLocation) -> int:
        """
        Gets called by init.
        Adds .npz files in /results/susceptibility_maps to the combobox.
        Returns the amount of models found.
        """
        modelpath = os.path.join(projectLocation, "results", "susceptibility_maps")
        count = 0
        for file in os.listdir(modelpath):
            if os.path.splitext(file)[1].lower() == ".npz":
                self.ui.modelComboBox.addItem(os.path.join(modelpath, file))
                count += 1
        return count

    def append_modelComboBox(self, modelPath: str, count: int) -> None:
        """
        Gets called by init and on_modelToolButton_clicked.
        Checks if modelPath is in Combobox if yes selects it and if not adds it add the end and 
        selects it.
        """
        modelInComboBox = self.ui.modelComboBox.findText(modelPath) # -1: False else: Index
        if modelInComboBox != -1: # modelPath in Combobox
            self.ui.modelComboBox.setCurrentIndex(modelInComboBox)
        else: # append modelpath to combobox
            self.ui.modelComboBox.addItem(modelPath)
            self.ui.modelComboBox.setCurrentIndex(count) # index starts at 0; count at 1

    @pyqtSlot(str)
    def on_modelComboBox_currentTextChanged(self, modelpath: str) -> None:
        """
        Gets called when the user selects another model.
        Updates the ui elements to show them for the current model.
        """
        try:
            self.tabWidget.clear()
            self.axes.clear()
            self.previewer.scene.clear()
            self.setAxesLabels()
            self.getModelInfo()
            self.loadData()
            self.initialTable()
            self.enableButtons(True)
        except KeyError:
            tb = traceback.format_exc()
            logging.error(tb)
            logging.error(self.tr("{} is not a valid model.").format(modelpath))

    def initialTable(self):
        """
        Sets table values based on the thresholdValues list.
        :return: None
        """
        self.ui.tableWidget.blockSignals(True)
        self.ui.tableWidget.setRowCount(len(self.thresholdValues))
        for i, value in enumerate(self.thresholdValues):
            # get color label calling the getColorLabel function
            colorLabel = self.getColorLabel(i)
            self.ui.tableWidget.setCellWidget(i, 0, colorLabel)
            # set description string (e.g. "very low") in second column
            itemLabel = QTableWidgetItem(value[1])
            self.ui.tableWidget.setItem(i, 1, itemLabel)
            # set targeted landslide area value
            itemLandslideTargetValue = QTableWidgetItem(str(value[0]))
            if i == self.ui.tableWidget.rowCount() - 1:  # last value
                itemLandslideTargetValue.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.ui.tableWidget.setItem(i, 2, itemLandslideTargetValue)
            # set total landslide area value
            itemLandslideTotalarea = QTableWidgetItem(str(value[2]))
            itemLandslideTotalarea.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.ui.tableWidget.setItem(i, 3, itemLandslideTotalarea)
            # Calculate and set best fit areas
            selectableValueX, selectableValueY = self.find_nearest(value[2])
            realValueItem = QTableWidgetItem("{:.3f}".format(selectableValueY * 100))
            realValueItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            if i == self.ui.tableWidget.rowCount() - 1:
                totalAreaItem = QTableWidgetItem(str(100))
            else:
                totalAreaItem = QTableWidgetItem(str(selectableValueX * 100))
            totalAreaItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.ui.tableWidget.setItem(i, 4, realValueItem)
            self.ui.tableWidget.setItem(i, 5, totalAreaItem)

        self.ui.tableWidget.resizeColumnToContents(0)
        self.thresholds = self.getTresholdsFromTable()
        self.ui.tableWidget.blockSignals(False)
        self.highlightUpdatePushButton(True)

    def updateThresholdValues(self):
        """
        Updates the threholdValues list.
        :return: None
        """
        try:
            cumul = 0
            for i, elem in enumerate(self.thresholdValues):
                if i == 0:  # first zone
                    cumul += int(elem[0])
                    elem[2] = int(elem[0])
                elif i == len(self.thresholdValues) - 1:  # last zone
                    elem[0] = 100 - cumul
                    elem[2] = 100
                else:  # other zones
                    cumul += int(elem[0])
                    elem[2] = cumul
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)

    def on_cell_clicked(self):
        """
        Called any time a table cell is clicked and writes the current cell value to the variable
        self.old_value. This is a part of validation process.
        When the user enters an invalid value, the invalid value is set
        back to the old_value.
        :return:
        """
        try:
            idx = self.ui.tableWidget.currentIndex()
            if idx.column() == 0:
                return
            self.old_value = (self.ui.tableWidget.item(idx.row(), idx.column()).text())
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)

    def on_tableWidget_cellChanged(self, row: int, col: int) -> None:
        """
        Called any time the user modified the cell value.
        The modified value is checked to be convertable to intger.
        If not: the message box notify the user about an invalid input value. The value is reset to
        old value. If user input is valid, the table is updated calling the functions update 
        thresholds and initialTable.
        """
        try:
            value = self.ui.tableWidget.item(row, col).text()
            if col == 1:
                self.thresholdValues[row][1] = value
            elif col == 2:
                try:
                    int(value)
                except ValueError:
                    QMessageBox.warning(
                        self,
                        self.tr("Invalid input"),
                        self.tr("Only integer values allowed as input!"))
                    self.ui.tableWidget.item(row, col).setText(self.old_value)
                    return
                self.thresholdValues[row][0] = value
            self.updateThresholdValues()
            self.initialTable()
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)

    def highlightUpdatePushButton(self, status: bool) -> None:
        """
        Gets called by on_tableWidget_cellChanged, on_resetTablePushButton_clicked and
        on_updatePushButton_clicked.
        Highlights the updatePushButton after the user changes cells in the table.
        """
        if status:
            self.ui.updatePushButton.setStyleSheet("background-color: #b7cbeb")
        else:
            self.ui.updatePushButton.setStyleSheet("")

    @pyqtSlot()
    def on_modelToolButton_clicked(self):
        """
        Gets called when modelToolButton clicked.
        Calls append_modelComboBox
        :return: None
        """
        self.fileDialog.openModelFile(self.projectLocation)
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
            model = os.path.normpath(self.fileDialog.selectedFiles()[0])
            count = self.ui.modelComboBox.count()
            self.append_modelComboBox(model, count)

    @pyqtSlot()
    def on_deleteRowToolButton_clicked(self):
        """
        Removes current row from the table and updates the
        thresholdValue list.
        :return: None
        """
        if self.ui.tableWidget.selectedIndexes():
            row = self.ui.tableWidget.currentRow()
            del self.thresholdValues[row]
            self.updateThresholdValues()
            self.ui.tableWidget.removeRow(row)
            self.initialTable()

    @pyqtSlot()
    def on_addRowToolButton_clicked(self):
        """
        Adds a new row to the table.
        The column values of the new row are set to default.
        Updates the thresholdValues list.
        :return: None
        """
        try:
            self.ui.tableWidget.blockSignals(True)
            if self.ui.tableWidget.rowCount() < 12:
                self.ui.tableWidget.insertRow(0)
                self.thresholdValues.insert(0, [1, self.tr("LABEL"), 0])
                self.updateThresholdValues()
                self.initialTable()
            else:
                QMessageBox.information(
                    self,
                    self.tr("Zoning limit!"),
                    self.tr("You are at the limit of maximum zones"))
            self.ui.tableWidget.blockSignals(False)
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)

    def setupROC(self):
        """
        Setups the ROC plot figure
        :return: None
        """
        self.fig = Figure(facecolor='white')
        self.canvas = FigureCanvas(self.fig)
        self.axes = self.fig.add_subplot(111)
        self.setAxesLabels()
        self.mpl_toolbar = NavigationToolbar(self.canvas, self)
        self.ui.rocCurveGroupBoxGridLayout.addWidget(self.canvas)
        self.ui.rocCurveGroupBoxGridLayout.addWidget(self.mpl_toolbar)
        self.fig.tight_layout()
        self.canvas.draw()

    def setAxesLabels(self):
        """
        Sets the axis labels and limits in the ROC plot
        :return: None
        """
        if os.name == "nt":
            prop = matplotlib.font_manager.FontProperties(fname="C:\\Windows\\Fonts\\Msyh.ttc")
        else:  # ubuntu
            prop = matplotlib.font_manager.FontProperties(
                fname="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
        self.axes.set_xlabel(self.tr("False Positive Rate (1-Specificity)"), fontproperties=prop)
        self.axes.set_ylabel(self.tr("True Positive Rate (Sensitivity)"), fontproperties=prop)
        self.axes.set_xlim([0.0, 1.0])
        self.axes.set_ylim([0.0, 1.0])

    def getROCData(self):
        """
        This method reads out the x and y data for the
        ROC curve from the model file and plots the ROC
        curve into the ROC plot.
        :param datapath: path to the model file
        :return: None
        """
        self.model = np.load(os.path.normpath(self.ui.modelComboBox.currentText()))
        self.roc_x = self.model['roc_x'].astype(np.float32)
        self.roc_y = self.model['roc_ymean'].astype(np.float32)
        self.axes.plot(self.roc_x, self.roc_y, label=self.tr("ROC"))
        self.fig.tight_layout()
        self.canvas.draw()

    def loadData(self):
        """
        This method establishes the workflow for loading data.
        1) Extract ROC curve data, calling getROCData function,
        2) Add raster layer to previewer, calling addRasterLayer function of the previwer object.
        :return: None
        """
        self.getROCData()
        self.previewer.addRasterLayer(self.model["data"], 1.0)

    def getModelInfo(self):
        """
        Loads the Model Info Widget into the model Info tab.
        :return: None
        """
        self.modelInfo = ModelInfo(self.ui.modelComboBox.currentText())
        self.tabWidget.addTab(self.modelInfo, self.tr("Model Info"))
        self.tabWidget.addTab(self.previewer, self.tr("Zoning preview"))
        self.ui.previewGroupBoxGridLayout.addWidget(self.tabWidget)

    def find_nearest(self, value):
        """
        Finds and returns the data point in the roc curve
        closest to the user value.
        :param value: user value for landslide thershold
        :return: float value
        """
        idx = (np.abs(self.roc_y - float(value) / 100)).argmin()
        return self.roc_x[idx], self.roc_y[idx]

    @pyqtSlot()
    def on_resetTablePushButton_clicked(self):
        """
        Generates a default table and Resets the table values to defaults.
        :return: None
        """
        defaultThresholdValues = [[50, self.tr("Very high"), 50], [30, self.tr("High"), 80],
                                  [15, self.tr("Moderate"), 95], [4, self.tr("Low"), 99],
                                  [1, self.tr("Very low"), 100]]
        self.ui.tableWidget.blockSignals(True)
        try:
            self.ui.tableWidget.setRowCount(len(defaultThresholdValues))
            self.thresholdValues = []
            for elem in defaultThresholdValues:
                self.thresholdValues.append(elem)

            for i, value in enumerate(self.thresholdValues):
                # get color label calling the getColorLabel function
                colorLabel = self.getColorLabel(i)
                self.ui.tableWidget.setCellWidget(i, 0, colorLabel)
                # set color label items
                itemLabel = QTableWidgetItem(value[1])
                self.ui.tableWidget.setItem(i, 1, itemLabel)
                # set targeted landslide value
                itemLandslideTargetValue = QTableWidgetItem(str(value[0]))

                if i == len(defaultThresholdValues) - 1:
                    itemLandslideTargetValue.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                   # lineEdit.setEnabled(False)
                self.ui.tableWidget.setItem(i, 2, itemLandslideTargetValue)

                itemLandslideTotalarea = QTableWidgetItem(str(value[2]))
                itemLandslideTotalarea.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.ui.tableWidget.setItem(i, 3, itemLandslideTotalarea)

                selectableValueX, selectableValueY = self.find_nearest(value[2])

                realValueItem = QTableWidgetItem("{:.3f}".format(selectableValueY * 100))
                realValueItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

                if i == len(defaultThresholdValues) - 1:
                    totalAreaItem = QTableWidgetItem(str(100))
                else:
                    totalAreaItem = QTableWidgetItem(str(selectableValueX * 100))
                totalAreaItem.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.ui.tableWidget.setItem(i, 4, realValueItem)
                self.ui.tableWidget.setItem(i, 5, totalAreaItem)

            self.ui.tableWidget.resizeColumnToContents(0)
            self.thresholds = self.getTresholdsFromTable()
            self.highlightUpdatePushButton(True)
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)
        self.ui.tableWidget.blockSignals(False)

    @pyqtSlot()
    def on_updatePushButton_clicked(self):
        """
        Updates the plot based on the table values
        :return: None
        """
        try:
            rowCount = self.ui.tableWidget.rowCount()
            if int(self.ui.tableWidget.item(rowCount - 1, 2).text()) <= 0:
                QMessageBox.warning(self, "Invalid input!", "Check your threshold values!")
                return
            # We set the Maximum to 0 to show an animation in the progressbar.
            self.axes.clear()
            self.setAxesLabels()
            self.getROCData()
            self.setVerticalLinesAndFill(self.thresholds)
            self.colorClass()
            self.previewer.setColorForValuesGreaterThan(self.classBoundaries, self.defaultColors)
            self.highlightUpdatePushButton(False)
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)

    def setVerticalLinesAndFill(self, thresholds):
        """
        Draw vertical lines into the plot between all zones and fill the areas under the curve
        with colors of the table.
        :param thresholds:
        :return: None
        """
        try:
            self.defaultColors_str = []
            for color in self.defaultColors:
                self.defaultColors_str.append(color.name())
            x_values = [0]
            idx_list = []
            for threshold in thresholds:
                x_values.append(float(threshold) / 100.0)
            for i in range(len(x_values)):
                if i < len(x_values) - 1:
                    self.line_v = self.axes.plot([x_values[i], x_values[i]], [0, 1.1], label="lineV_{}".format(
                        i), color='r', linestyle='-', linewidth=1, pickradius=10, zorder=2)
                    idx = np.where(self.roc_x == x_values[i])
                    idx_list.append(idx[0][0])

            for i in range(len(idx_list)):
                if i + 1 == len(idx_list):
                    self.axes.fill_between(self.roc_x[idx_list[i]:len(self.roc_x)], 0, self.roc_y[idx_list[i]:len(
                        self.roc_x)], color=str(self.defaultColors_str[i]), alpha=0.5, linewidth=0,)
                else:
                    self.axes.fill_between(self.roc_x[idx_list[i]:idx_list[i + 1] + 1],
                                           0,
                                           self.roc_y[idx_list[i]:idx_list[i + 1] + 1],
                                           color=str(self.defaultColors_str[i]),
                                           alpha=0.5,
                                           linewidth=0,
                                           )
            self.fig.tight_layout()
            self.canvas.draw()
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)

    def getTresholdsFromTable(self):
        """
        This method read out the threshold values from the table widget.
        :return: list of theresholds
        """
        thresholds = []
        for i in range(self.ui.tableWidget.rowCount()):
            thresholds.append(float(self.ui.tableWidget.item(i, 5).text()))
        return thresholds

    def getColorDialog(self):
        """
        This method estimates the table cell that was doublecklicked,
        then calls the QColorDialog widget, updates the global color list with the
        color obtained from the selection in QColorDialog, passes this color selected
        to the label constructor (getColorLabel method) creating
        a new label object and finally passes the new label object to updateLabel
        method.
        :return: None
        """
        try:
            for idx in self.ui.tableWidget.selectionModel().selectedIndexes():
                if len(self.ui.tableWidget.selectionModel().selectedIndexes()) > 1:
                    return
                row = idx.row()
                col = idx.column()
                if col == 0:
                    colorSelection = self.colorDialog.getColor(
                        parent=self, title=self.tr("Select zone color"))
                    if colorSelection.isValid():
                        color = QColor(colorSelection)
                        newLabel = self.getColorLabel(color=color)
                        color.setAlpha(100)
                        self.defaultColors[row] = color
                        self.updateLabel(row, newLabel)
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)

    def updateLabel(self, row, label):
        """
        This method updates the label in the corresponding
        row with a new label. And
        :param row: int
        :param label: QLabel object
        :return: None
        """
        self.colorClass()
        self.ui.tableWidget.setCellWidget(row, 0, label)

    def getColorLabel(self, i=None, color=None):
        """
        This method is constructs a QLabel object
        containing a pixmap with a specified color.
        :param i: int
        :param color: QColor
        :return: QLabel object
        """
        self.colorLabel = QLabel()
        pixmap = QPixmap(40, 30)
        if color is None and i is not None:
            color = QColor(self.defaultColors[i].rgba())
        pixmap.fill(color)
        self.colorLabel.setPixmap(pixmap)
        return self.colorLabel

    def prepareArray(self):
        # get array data from model
        array = self.model["data"].astype(np.float32)
        # necessary for graphic representation (8 bit colors)
        array[np.where(array == -9999.0)] = np.nan
        if ((np.nanmax(array) - np.nanmin(array))/ np.nanmin(array)) > 500:
            array = np.log(array)

        # get weight values and frequencies
        values, freq = np.unique(array, return_counts=True)
        # sort values
        s_val = values[::-1]
        s_freq = freq[::-1]
        sort_val = s_val[np.where(~np.isnan(s_val))]
        sort_freq = s_freq[np.where(~np.isnan(s_val))]
        cumul = np.cumsum(sort_freq.astype(np.float32) / np.nansum(sort_freq))
        # get the minimum value in the array ignoring NaN values
        minArray = np.nanmin(sort_val)
        range = np.nanmax(sort_val) - minArray
        return array, sort_val, sort_freq, cumul, range, minArray

    def colorClass(self):
        """
        This method update the colors of the classes in the raster layer
        based on a list of class thersholds.
        :param thresholds: numpy array
        :return: None
        """
        array, sort_val, sort_freq, cumul, range, minArray = self.prepareArray()
        self.previewer.scene.clear()
        self.previewer.addRasterLayer(array, 1.0)
        # create a empty list
        self.classBoundaries = []
        # populate the list with imagePixelValues (0-255)
        for x in self.thresholds:
            # get the percentage of the class threshold (x)
            # create a bool mask based on the "Class_perc" column of the table
            # the bool mask provides ones for rows in which the percentage is less or equal than the
            # x-threshold
            idx = (np.abs(cumul - (x / 100))).argmin()
            classAreas = np.less_equal(cumul, cumul[idx])
            # multiply the weight column with the mask delivers weights corresponding to the
            # classes of the ROC curve, non-relevant entries becomes zero (mathematical filter!)
            weights = sort_val * classAreas
            weights[np.where(weights == 0)] = np.nan
            imageValue = ((np.nanmin(weights) - minArray) / range) * 254
            # add the estimated imagePixelValue to the classBoundary list.
            self.classBoundaries.append(int(imageValue))

    @pyqtSlot()
    def on_outputRasterToolButton_clicked(self):
        if self.projectLocation is not None:
            location = os.path.join(self.projectLocation, "results", "susceptibility_maps")
            self.fileDialog.saveRasterFile(location)
        else:
            self.fileDialog.saveRasterFile()
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
            if os.path.splitext(self.fileDialog.selectedFiles()[0])[1].lower() == ".tif":
                self.ui.outputRasterLineEdit.setText(
                    os.path.normpath(self.fileDialog.selectedFiles()[0]))
            else:
                self.ui.outputRasterLineEdit.setText(os.path.normpath(
                    self.fileDialog.selectedFiles()[0] + '.tif'))

    @pyqtSlot()
    def on_applyPushButton_clicked(self):
        try:
            self.outRasterPath = self.ui.outputRasterLineEdit.text()
            if not self.outRasterPath:
                self.msg.WarningMissingInput()
                return
            self._updateProgress(True)
            array, sort_val, sort_freq, cumul, ranges, minArray = self.prepareArray()
            maxWeight = np.nanmax(array)
            # create a empty list
            classBoundaries = []
            # populate the list with imagePixelValues (0-255)
            for x in self.thresholds:
                # get the percentage of the class threshold (x)
                # create a bool mask based on the "Class_perc" column of the table
                # the bool mask provides ones for rows in which the percentage is less or equal than the
                # x-threshold
                idx = (np.abs(cumul - (x / 100))).argmin()
                classAreas = np.less_equal(cumul, cumul[idx])
                # multiply the weight column with the mask delivers weights corresponding to the
                # classes of the ROC curve, non-relevant entries becomes zero (mathematical filter!)
                weights = sort_val * classAreas
                weights[np.where(weights == 0)] = np.nan
                weightValue = np.nanmin(weights)
                # add the estimated imagePixelValue to the classBoundary list.
                classBoundaries.append(weightValue)
            classArray = np.zeros_like(array)

            for i, classBoundary in enumerate(classBoundaries):
                if i == 0:
                    classArray[np.where(array >= classBoundary)] = i + 1
                elif i > 0 and maxWeight - classBoundary != 0 and i != (len(classBoundaries) - 1):
                    classArray[np.where((array < classBoundaries[i - 1]) &
                                        (array >= classBoundary))] = i + 1
                elif i == (len(classBoundaries) - 1):
                    classArray[np.where((array < classBoundaries[i - 1]) &
                                        (array >= classBoundary))] = i + 1
                    classArray[np.where((array < classBoundary))] = i + 1

            classArray[np.where(np.isnan(array))] = -9999.0
            self.modelPath = str(self.ui.modelComboBox.currentText())
            NoData_value = -9999.0
            driver = gdal.GetDriverByName('GTiff')
            outRaster = driver.Create(
                self.outRasterPath,
                array.shape[1],
                array.shape[0],
                1,
                gdal.GDT_Int16)
            if self.projectLocation is not None:
                self.mask = Raster(os.path.join(self.projectLocation, "region.tif"))
                outRaster.SetProjection(self.mask.proj)
                outRaster.SetGeoTransform(self.mask.geoTrans)
            band = outRaster.GetRasterBand(1)
            band.SetNoDataValue(NoData_value)
            outRaster.GetRasterBand(1).WriteArray(classArray)
            band.ComputeStatistics(False)
            outRaster = None
            del array
            self.createRAT()
            self._updateProgress(False)
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)

    def _updateProgress(self, switch: bool) -> None:
        """
        Gets called by on_applyPushButton_clicked.
        Changes the progressbar to tell user something is going on.
        """
        if switch:
            self.progress.setRange(0, 0)
        else:
            self.progress.setRange(0, 1)

    def createRAT(self):
        """
        This method creates a basic RAT for the raster datset contaning
        value and count field and populate it with description.
        :return: None
        """
        raster = Raster(self.outRasterPath)
        rat = gdal.RasterAttributeTable()
        values, counts = np.unique(raster.getArrayFromBand(), return_counts=True)
        value_list = []
        count_list = []

        for i in range(len(values)):
            if values[i] != raster.nodata:
                value_list.append(values[i])
                count_list.append(counts[i])
        # total raster pixels having values
        total_pixels = np.sum(count_list)
        # in the following we estimate real propostion of the class areas based on the reclassification
        # the reason is that the values in the widget table are only approximate values based on
        # the ROC curve estimates. ROC x is however total area - total landslide area and therefore
        # not exact estimate for the class area
        class_areas_real = []
        for class_pixel in count_list:
            class_areas_real.append(float(class_pixel/total_pixels)*100)
        total_area = np.cumsum(class_areas_real)



        rat.CreateColumn("VALUE", gdal.GFT_Integer, gdalconst.GFU_MinMax)
        rat.CreateColumn("COUNT", gdal.GFT_Integer, gdalconst.GFU_MinMax)
        rat.CreateColumn("LABEL", gdal.GFT_String, gdalconst.GFU_MinMax)
        rat.CreateColumn("T_LAND_AREA", gdal.GFT_Integer, gdalconst.GFU_MinMax)
        rat.CreateColumn("M_LAND_AREA", gdal.GFT_Real, gdalconst.GFU_MinMax)
        rat.CreateColumn("TOTAL_AREA", gdal.GFT_Real, gdalconst.GFU_MinMax)

        for i in range(len(value_list)):
            rat.SetValueAsInt(i, 0, int(value_list[i]))
        for i in range(len(count_list)):
            rat.SetValueAsInt(i, 1, int(count_list[i]))

        rows = self.ui.tableWidget.rowCount()
       # index = rows-1
        for i in range(rows):
            item0 = self.ui.tableWidget.item(i, 1)
            labelText = item0.text()
            item1 = self.ui.tableWidget.item(i, 2)
            targetlandAreaText = item1.text()
            item2 = self.ui.tableWidget.item(i, 4)
            landAreaText = item2.text()
            item3 = self.ui.tableWidget.item(i, 5)
            totalAreaText = item3.text()
            rat.SetValueAsString(i, 2, str(labelText))
            rat.SetValueAsDouble(i, 3, int(targetlandAreaText))
            rat.SetValueAsDouble(i, 4, float(landAreaText))
            rat.SetValueAsDouble(i, 5, float(total_area[i]))
        raster.band.SetDefaultRAT(rat)
        raster = None
        self.msg.InfoBoxAnalysisCompleted(self.outRasterPath)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.model = None


class Viewer(QGraphicsView):
    """
    The viewer is a simple class resembling QGraphics Object.
    It is capable to load a nd array as QImage and update
    the colors of the QImage based on the defined colorTable.
    It has a simple mouse wheel function.
    """

    def __init__(self, raster=None, parent=None):
        QGraphicsView.__init__(self, parent)

        # set scene
        self.scene = QGraphicsScene()
        # set variable imagePixmap
        self.imagePixmap = None

        # set scene to graphic view
        self.setScene(self.scene)

        # set properties of the graphic view
        self.setAcceptDrops(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setFocusPolicy(Qt.WheelFocus)

    def addRasterLayer(self, array, zValue):
        """
        This method creates a QImage from numpy array
        and adds it as layer to the scene.
        :param array: numpy array (2d)
        :return: None
        """
        # create an array normalized to values between 0 and 254
        array[np.where(array == -9999.0)] = np.nan
        self.image = ((array.astype(np.float32) - np.nanmin(array)) /
                      (np.nanmax(array) - np.nanmin(array))) * 254
        # set nodatavalues of the raster to 255
        where_NaN = np.isnan(array)
        self.image[where_NaN] = 255

        # get unique values in the image array (for continous data from 1 to 255,
        # for dicrete values dicrete number in the range of 1 and 255)
        self.uniq_int = np.unique(self.image.astype(np.uint8))

        # create Qimage from image array
        self.QImage = QImage(
            self.image.astype(
                np.uint8),
            self.image.shape[1],
            self.image.shape[0],
            self.image.shape[1],
            QImage.Format_Indexed8)

        # create a GDAL color table
        self.GDAL_colorTable = gdal.ColorTable()
        # create color ramp to set colors in the image
        if zValue == 0.0:
            self.GDAL_colorTable.CreateColorRamp(0, (0, 0, 0, 255), 254, (255, 255, 255, 255))
        else:
            self.GDAL_colorTable.CreateColorRamp(0, (0, 0, 0, 100), 254, (255, 255, 255, 100))

        # set the color from color ramp to the Qimage
        for value in self.uniq_int:
            if value == 255:
                r, g, b, a = (0, 0, 0, 0)
            else:
                r, g, b, a = self.GDAL_colorTable.GetColorEntry(int(value))
            self.QImage.setColor(value, QColor(r, g, b, a).rgba())

        # create image Pixmap from QImage
        self.imagePixmap = QPixmap.fromImage(self.QImage)

        # create item from image Pixmap and set some properties (e.g. selectable)
        item = QGraphicsPixmapItem(self.imagePixmap)
        item.setFlag(QGraphicsItem.ItemIsSelectable, True)
        item.setZValue(zValue)
        # Set the image to the graphic scene as a pixmap object
        mapItem = self.scene.addItem(item)
        self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    def setColorForValuesGreaterThan(self, classBoundaries, colors):
        """
        This method updates the colors for the QImage based on
        a color table and specified class boundaries.
        :param classBoundaries: numpy array containing thresholds for classes
        :return: None
        """
        # Get the graphicItem from scene (because the QImage of the model is the
        # only item it is automatically selected)

        colors_rgba = []
        for color in colors:
            colors_rgba.append(color.rgba())

        for item in self.scene.items():
            if item.zValue() == 1:
                # create a new QImage which is absolutely equal to the loaded image (
                # This is necessary here because copying QObject is not easy and a reference would change the original object. We need the
                # original object as an unchanged reference.
                QImage_new = QImage(
                    self.image.astype(
                        np.uint8),
                    self.image.shape[1],
                    self.image.shape[0],
                    self.image.shape[1],
                    QImage.Format_Indexed8)

                colorTable = self.QImage.colorTable()
                if len(colorTable) < 256:
                    colorTable.append(QColor(0, 0, 0, 0).rgba())

                QImage_new.setColorTable(colorTable)
                new_colorTable = np.array(QImage_new.colorTable())
                index_value = np.arange(256)

                for i, classBoundary in enumerate(classBoundaries):
                    if i == 0:
                        new_colorTable[np.where(
                            (index_value >= classBoundaries[i]))] = colors_rgba[i]
                        new_colorTable[np.where((index_value == 255))] = QColor(0, 0, 0, 0).rgba()
                    if i < len(classBoundaries) - 1:
                        new_colorTable[np.where((index_value >= classBoundaries[i]) & (
                            index_value < classBoundaries[i - 1]))] = colors_rgba[i]
                    else:
                        new_colorTable[np.where((index_value >= classBoundaries[i]) & (
                            index_value < classBoundaries[i - 1]))] = colors_rgba[i]
                        new_colorTable[np.where(index_value < classBoundaries[i])] = colors_rgba[i]
                QImage_new.setColorTable(new_colorTable.tolist())
                new_pix = QPixmap.fromImage(QImage_new)
                item.setPixmap(new_pix)
            else:
                pass

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseMove and source == self.viewport():
            if event.buttons() == Qt.NoButton:
                self.scaleRatioX, self.scaleRatioY = self.getScaleRatio()
                # event position in Coordinaten des Viewports
                x = event.pos().x()
                y = event.pos().y()
                #xGeo, yGeo = self.TransformImageCoordsToGeoCoords(x, y)
                #self.statusBar().showMessage('%f %f %s' % (xGeo, yGeo, self.georef), 2000)
        return QMainWindow.eventFilter(self, source, event)

    def getScaleRatio(self):
        viewGeometry = self.viewport().geometry()
        scaleRatioX = self.scene.width() / viewGeometry.width()
        scaleRatioY = self.scene.height() / viewGeometry.height()
        return scaleRatioX, scaleRatioY

    def wheelEvent(self, event):
        zoomFactor = 1.5
        if self.imagePixmap:
            cursor = QCursor()
            if event.angleDelta().y() > 0:
                self.scale(zoomFactor, zoomFactor)
                curPos_new = self.mapToScene(cursor.pos())
                self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
                self.centerOn(curPos_new)
            else:
                self.scale(1 / zoomFactor, 1 / zoomFactor)
                curPos_new = self.mapToScene(cursor.pos())
                self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
                self.centerOn(curPos_new)
