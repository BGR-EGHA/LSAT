# -*- coding: utf-8 -*-

import sys
import os
import math
import time
from osgeo import gdal, gdalconst, ogr, osr
import numpy as np
import logging
import traceback

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import matplotlib
import traceback
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog
from core.libs.GDAL_Libs.Layers import Raster
from core.uis.Reclassify_ui.reclass_ui import Ui_Reclassify
from core.widgets.RasterInfo.rasterInfo_main import RasterInfo

gdal.AllRegister()
if os.name == "nt":
    prop = matplotlib.font_manager.FontProperties(fname="C:\\Windows\\Fonts\\Msyh.ttc")
else:  # ubuntu
    prop = matplotlib.font_manager.FontProperties(
        fname="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")


class Reclass(QMainWindow):
    def __init__(self, projectPath, parent=None):
        QMainWindow.__init__(self, parent)
        self.ui = Ui_Reclassify()
        self.ui.setupUi(self)
        self.progress = QProgressBar()
        self.statusBar().addPermanentWidget(self.progress)
        self.projectPath = projectPath
        self.fileDialog = CustomFileDialog()

        # Set the window icon
        self.setWindowIcon(QIcon(':/icons/Icons/reclassify.png'))

        # Set figure
        self.fig = Figure(facecolor='white')
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.ui.plotFrame)
        self.axes = self.fig.add_subplot(111)
        self.axes.set_xlabel(self.tr("Value"), fontproperties=prop)
        self.axes.set_ylabel(self.tr('Pixel count'), fontproperties=prop)
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.ui.plotFrame)
        self.ui.plotGroupBoxGridLayout.addWidget(self.canvas)
        self.ui.plotGroupBoxGridLayout.addWidget(self.mpl_toolbar)


        # set defaults
        self.press = None
        self.background = None
        self.thisline = None

        # Set event handling on the figure
        self.cid_onpick = self.canvas.mpl_connect("pick_event", self.onPick)
        self.cid_onpress = self.canvas.mpl_connect("button_press_event", self.onPress)
        self.cid_onrelease = self.canvas.mpl_connect("button_release_event", self.onRelease)
        self.cid_onmotion = self.canvas.mpl_connect("motion_notify_event", self.onMotion)

        self.ui.tableWidget.cellChanged.connect(self.on_tableValueChanged)

        if self.projectPath:
            raster_data_path = os.path.join(self.projectPath, "data", "params")
            for datafile in os.listdir(raster_data_path):
                if datafile.lower().endswith(".tif"):
                    self.ui.inputRasterComboBox.insertItem(
                        0, str(os.path.join(raster_data_path, datafile)))
            if self.ui.inputRasterComboBox.currentText() != "":
                self.readRasterData()
        self.fig.tight_layout()
        self.canvas.draw()

    def onPick(self, event):
        """
        Defines action on pick event.
        If a line will be picked the line width is set to 3
        (default line thickness is about 1). The coordinates of the
        line are readed out.
        :param event: mouse click event
        :return: None
        """
        try:
            self.thisline = event.artist
            self.thisline.set_linewidth(3)
            self.line_xdata = self.thisline.get_xdata()
            self.line_ydata = self.thisline.get_ydata()
            ind = event.ind
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)

    def onPress(self, event):
        """
        Defines actions on the mouse press event.
        :param event: mouse press event
        :return: None
        """

        if event.inaxes != self.axes:
            return

        if event.button == 1:
            if self.thisline is None:
                return
            ln = self.thisline
            label = ln.get_label()
            if label == str(self.ui.tableWidget.rowCount() - 1):
                return
            containes, attrd = self.thisline.contains(event)
            x0, y0 = self.line_xdata, event.ydata
            self.press = x0, y0, event.xdata, event.ydata
            canvas = self.thisline.figure.canvas
            axes = self.thisline.axes
            self.background = canvas.copy_from_bbox(self.thisline.axes.bbox)
            axes.draw_artist(self.thisline)
            canvas.blit(axes.bbox)
            self.fig.tight_layout()

        if event.button == 3:
            self.ui.reclassMethodComboBox.setCurrentIndex(
                self.ui.reclassMethodComboBox.findText(self.tr("Manual")))
            if event.xdata > self.raster.max or event.xdata < self.raster.min:
                QMessageBox.warning(self, self.tr("Invalid value"), self.tr(
                    "Trying to set a class boundary outside data range!"), QMessageBox.Ok)
                return
            a, b = self.axes.get_ylim()
            rowPosition = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(rowPosition)
            self.axes.plot([event.xdata, event.xdata], [a, b], color='r', linestyle='-',
                           linewidth=1, picker=5, label=str(rowPosition), zorder=2)
            self.fig.tight_layout()
            self.canvas.draw()
            self.update()

        if event.button == 1 and event.dblclick:
            self.ui.reclassMethodComboBox.setCurrentIndex(
                self.ui.reclassMethodComboBox.findText(self.tr("Manual")))
            ln = self.thisline
            label = ln.get_label()
            rowPosition = int(label)
            self.ui.tableWidget.removeRow(rowPosition)
            ln.remove()
            self.fig.tight_layout()
            self.canvas.draw()

    def onMotion(self, event):
        """
        Defines actions on mouse move event.
        :param event: mouse click event (move)
        :return: None
        """
        try:
            if self.press is None:
                return
            if event.inaxes != self.thisline.axes:
                return
            self.ui.reclassMethodComboBox.setCurrentIndex(
                self.ui.reclassMethodComboBox.findText(self.tr("Manual")))
            x0, y0, xpress, ypress = self.press
            dx = event.xdata - xpress
            dy = event.ydata - ypress
            self.thisline.set_xdata(x0 + dx)
            self.thisline.set_linewidth(3)
            canvas = self.thisline.figure.canvas
            axes = self.thisline.axes
            canvas.restore_region(self.background)
            axes.draw_artist(self.thisline)
            canvas.blit(axes.bbox)
        except BaseException:
            pass

    def onRelease(self, event):
        """
        Defines actions on release event.
        :param event: mouse click event (release)
        :return: None
        """
        if event.xdata > self.raster.max or event.xdata < self.raster.min:
            QMessageBox.warning(self, self.tr("Invalid value"), self.tr(
                "Trying to set a class boundary outside data range!"), QMessageBox.Ok)
            return
        self.press = None
        if self.thisline is not None:
            self.thisline.set_linewidth(1)
            self.thisline = None
            self.update()

    # BROWSE FOR DATA
    @pyqtSlot(int)
    def on_inputRasterComboBox_activated(self):
        self.axes.clear()
        # Trys to remove widget. Won't initially work because we haven't added one yet.
        try:
            self.ui.rasterStatisticsGroupBoxGridLayout.removeWidget(self.rasterInfo)
        except AttributeError:
            pass
        self.readRasterData()

    @pyqtSlot()
    def on_inputRasterToolButton_clicked(self):
        """
        This method calls the file dialog, set the raster dataset file,
        reads the data and calls the histogram method.
        :return: None
        """
        self.fileDialog.openRasterFile(self.projectPath)
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles()[0]:
            filename = os.path.normpath(self.fileDialog.selectedFiles()[0])
            self.ui.inputRasterComboBox.addItem(filename)
            self.ui.inputRasterComboBox.setCurrentIndex(
                self.ui.inputRasterComboBox.findText(filename))
            self.axes.clear()
            # Trys to remove widget. Won't initially work because we haven't added one yet.
            try:
                self.ui.rasterStatisticsGroupBoxGridLayout.removeWidget(self.rasterInfo)
            except AttributeError:
                pass
            self.readRasterData()

    @pyqtSlot(int)
    def on_reclassMethodComboBox_currentIndexChanged(self):
        """
        This method handels the actions when the value in the
        reclass method combo box has changed.
        :return: None
        """
        if self.ui.reclassMethodComboBox.currentText() == self.tr("Manual"):
            self.ui.classSpinBox.setEnabled(False)
            self.ui.intervalSizeLineEdit.setEnabled(False)
            self.ui.intervalSizeLineEdit.setText("")
            self.ui.start0CheckBox.setEnabled(False)
        elif self.ui.reclassMethodComboBox.currentText() == self.tr("Quantile"):
            self.ui.classSpinBox.setEnabled(True)
            self.ui.intervalSizeLineEdit.setEnabled(False)
            self.ui.intervalSizeLineEdit.setText("")
            self.ui.start0CheckBox.setEnabled(False)
        elif self.ui.reclassMethodComboBox.currentText() == self.tr("Equal interval"):
            self.ui.classSpinBox.setEnabled(True)
            self.ui.intervalSizeLineEdit.setEnabled(False)
            self.ui.start0CheckBox.setEnabled(False)
        elif self.ui.reclassMethodComboBox.currentText() == self.tr("Defined interval"):
            self.ui.classSpinBox.setEnabled(False)
            self.ui.intervalSizeLineEdit.setEnabled(False)
            self.ui.start0CheckBox.setEnabled(True)
        elif self.ui.reclassMethodComboBox.currentText() == self.tr("Unique"):
            self.ui.intervalSizeLineEdit.setEnabled(False)
            self.ui.intervalSizeLineEdit.setEnabled(False)
            self.ui.start0CheckBox.setEnabled(False)

    @pyqtSlot(int)
    def on_classSpinBox_valueChanged(self):
        """
        Defines action if class spin box value has changed.
        Calls the getClassInterval method.
        :return: None
        """
        self.getClassInterval()

    def on_tableValueChanged(self):
        if self.ui.tableWidget.currentColumn() == 2:
            return
        else:
            idx = self.ui.reclassMethodComboBox.findText("Manual")
            self.ui.reclassMethodComboBox.setCurrentIndex(idx)
            self.updateFromTable()


    def updateFromTable(self):
        ### get the index of the cell in which the value changed
        index = self.ui.tableWidget.currentIndex()
        ### generate a backup list of the values before change
        a, b = self.axes.get_ylim()
        backup_list = []
        for child in self.axes.get_children():
            if isinstance(child, matplotlib.lines.Line2D) and len(str(child.get_label())) < 4:
                backup_list.append(child.get_xdata()[0])
        backup_list = sorted(np.unique(backup_list).tolist())
        ### pick the old cell value from backup list
        old_value = backup_list[index.row()]

        try:
            new_value = float(self.ui.tableWidget.item(index.row(), index.column()).text())

            if new_value > self.raster.min and new_value < self.raster.max:
                for child in self.axes.get_children():
                    if isinstance(child, matplotlib.lines.Line2D) and str(child.get_label()) == str(index.row()):
                        child.remove()
                        self.axes.plot([new_value, new_value], [a, b], color='r', linestyle='-',
                                   linewidth=1, picker=5, label=str(index.row()), zorder=2)
                        self.update()
            else:
                logging.warning(self.tr("Trying to set class boundary outside data range"))
                self.ui.tableWidget.currentItem().setText("{}".format(round(old_value, 2)))
        except:
            logging.error(self.tr("Invalid value!"))
            self.ui.tableWidget.currentItem().setText("{}".format(round(old_value, 2)))



    def update(self):
        """
        This method updates the graphics and the table widget.
        :return: None
        """
        self.ui.tableWidget.blockSignals(True)
        colName1 = QTableWidgetItem()
        colName1.setText(self.tr("FROM"))
        self.ui.tableWidget.setHorizontalHeaderItem(0, colName1)
        colName2 = QTableWidgetItem()
        colName2.setText(self.tr("TO"))
        self.ui.tableWidget.setHorizontalHeaderItem(1, colName2)
        colName3 = QTableWidgetItem()
        colName3.setText(self.tr("NEW VALUE"))
        self.ui.tableWidget.setHorizontalHeaderItem(2, colName3)

        a, b = self.axes.get_ylim()
        validation_list = []
        for child in self.axes.get_children():
            if isinstance(child, matplotlib.lines.Line2D) and len(str(child.get_label())) < 4:
                validation_list.append(child.get_xdata()[0])
                child.remove()

        validation_list = sorted(np.unique(validation_list).tolist())


        self.ui.tableWidget.setRowCount(len(validation_list))
        for i, value in enumerate(validation_list):
            if i == 0:
                item0 = QTableWidgetItem("%.2f" % (self.raster.min))
                item0.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                item0.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.ui.tableWidget.setItem(i, 0, QTableWidgetItem(item0))


                item1 = QTableWidgetItem("%.2f" % (value))
                item1.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.ui.tableWidget.setItem(i, 1, QTableWidgetItem(item1))

                item2 = QTableWidgetItem(str(i + 1))
                item2.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.ui.tableWidget.setItem(i, 2, item2)

            elif i == len(validation_list) - 1:
                item0 = QTableWidgetItem(str("%.2f" % (validation_list[i - 1])))
                item0.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                item0.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.ui.tableWidget.setItem(i, 0, QTableWidgetItem(item0))

                item1 = QTableWidgetItem("%.2f" % (self.raster.max))
                item1.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                item1.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.ui.tableWidget.setItem(i, 1, QTableWidgetItem(item1))

                item2 = QTableWidgetItem(str(i + 1))
                item2.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.ui.tableWidget.setItem(i, 2, item2)


            else:
                item0 = QTableWidgetItem(str("%.2f" % (validation_list[i - 1])))
                item0.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                item0.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.ui.tableWidget.setItem(i, 0, QTableWidgetItem(item0))


                item1 = QTableWidgetItem("%.2f" % (value))
                item1.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.ui.tableWidget.setItem(i, 1, QTableWidgetItem(item1))

                item2 = QTableWidgetItem(str(i + 1))
                item2.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.ui.tableWidget.setItem(i, 2, item2)

            self.axes.plot([value, value], [a, b], color='r', linestyle='-',
                               linewidth=1, picker=5, label=str(i), zorder=2)

        self.axes.set_ylim(a, b)
        self.intList = validation_list
        self.fig.tight_layout()
        self.canvas.draw()
        self.ui.tableWidget.blockSignals(False)

    def getHistogram(self):
        """
        This method generates a histogram from data array and plot it in the graph.
        :return: None
        """
        self.hist = self.raster.band.GetHistogram(self.raster.min, self.raster.max, 50, 0, 0)
        self.hist_array = np.array(self.hist)
        interval = (self.raster.max - self.raster.min) / 50
        bins = self.raster.min
        self.hist_x = []
        for i in range(50):
            bins = bins + interval
            self.hist_x.append(bins)
        if "Float" in self.raster.type:
            self.axes.fill_between(self.hist_x, 0, self.hist_array / 1000, color = "grey", alpha = 0.5)
        else:
            self.axes.bar(self.hist_x, self.hist_array / 1000, align="center", color = "grey", alpha = 0.5)
        a, b = self.axes.get_ylim()
        self.fig.tight_layout()
        self.canvas.draw()

    def updateHistogram(self):
        """
        This method updates the histogram in the graph any time the method is called.
        :return: None
        """
        try:
            self.axes.clear()
            self.axes.set_xlabel(self.tr('Value'))
            self.axes.set_ylabel(self.tr('Pixel count (x 1000)'))
            if self.ui.reclassMethodComboBox.currentText() == self.tr("Unique"):
                self.axes.bar(self.unique, np.array(self.unique_count) / 1000, align='center', color = "grey", alpha = 0.5)
            elif "Float" in self.raster.type:
                self.axes.fill_between(self.hist_x, 0, self.hist_array / 1000, color = "grey", alpha = 0.5)
            else:
                self.axes.bar(self.hist_x, self.hist_array / 1000, align="center", color = "grey", alpha = 0.5)

            a, b = self.axes.get_ylim()
            for i, value in enumerate(self.intList):
                self.axes.plot([value, value], [a, b], color='r', linestyle='-',
                               linewidth=1, picker=5, label=str(i), zorder=2)
            self.fig.tight_layout()
            self.canvas.draw()
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)


    @pyqtSlot()
    def on_outputRasterToolButton_clicked(self):
        """
        This method calls the Save File dialog to specify the output
        location for the classified dataset.
        :return: None
        """
        self.fileDialog.saveRasterFile(directory=self.projectPath)
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
            filename = os.path.normpath(self.fileDialog.selectedFiles()[0])
            if not filename.lower().endswith(".tif"):
                filename = filename + ".tif"
            self.ui.outputRasterComboBox.addItem(filename)
            self.ui.outputRasterComboBox.setCurrentIndex(
                self.ui.outputRasterComboBox.findText(filename))

    @pyqtSlot(int)
    def on_reclassMethodComboBox_activated(self):
        """
        Update reclass method based ob comboBox event
        :return:
        """
        self.getClassInterval()

    def readRasterData(self):
        """
        Read the data and calculate default values intervals.
        Displays Raster Information with RasterInfo(*path to raster*)
        :return: None
        """
        self.rasterInfo = RasterInfo(self.ui.inputRasterComboBox.currentText())
        self.rasterInfo.statusBar().setVisible(False)
        self.ui.rasterStatisticsGroupBoxGridLayout.addWidget(self.rasterInfo)
        self.raster = Raster(self.ui.inputRasterComboBox.currentText())
        self.array = self.raster.getArrayFromBand()
        self.valueList, self.countList = np.unique(self.array, return_counts=True)
        self.getHistogram()
        # estimate default class intervals (Equal interval, 5)
        self.getClassInterval()

    def getClassInterval(self):
        """
        This method calls different methods for computation of the class interval.
        Supported methods: "Equal interval", "Quantile", "Manual", Defined interval", "Unique"
        :return: None
        """
        method = self.ui.reclassMethodComboBox.currentText()
        if method == self.tr("Equal interval"):
            self.ui.classSpinBox.setEnabled(True)
            self.ui.intervalSizeLineEdit.setEnabled(False)
            self.getEqualInterval()
            self.updateHistogram()
        elif method == self.tr("Quantile"):
            self.ui.classSpinBox.setEnabled(True)
            self.ui.intervalSizeLineEdit.setEnabled(False)
            self.getQuantile(int(self.ui.classSpinBox.value()))
            self.updateHistogram()
        elif method == self.tr("Manual"):
            self.ui.classSpinBox.setEnabled(False)
            self.ui.intervalSizeLineEdit.setEnabled(False)
        elif method == self.tr("Defined interval"):
            self.ui.classSpinBox.setEnabled(False)
            self.ui.intervalSizeLineEdit.setEnabled(True)
            self.updateHistogram()
        elif method == self.tr("Unique"):
            self.getUniqueValues()
        self.update()

    def getEqualInterval(self):
        """
        This method computes the equal interval from the data.
        :return: .
        Compute equal interval values from the value range
        """
        try:
            maxValue = self.raster.max
            minValue = self.raster.min
            valueRange = maxValue - minValue
            intSize = valueRange / int(self.ui.classSpinBox.value())
            self.ui.intervalSizeLineEdit.setText(str(intSize))
            intThreshold = minValue
            self.intList = []
            for i in range(int(self.ui.classSpinBox.value())):
                intThreshold = intThreshold + intSize
                self.intList.append(intThreshold)
            return self.intList
        except Exception as e:
            logging.error(str(e))

    def getQuantile(self, number):
        """
        Calculates quantiles from the users defined parameters and flat_array.
        :param number: integer, number of quantiles.
        :return:  list with interval thresholds [ Q1, ...Qn, max-rasterValue]
        """
        try:
            self.array[np.where(self.array == self.raster.nodata)] = np.nan
            self.ui.intervalSizeLineEdit.setText("")
            interval = []
            k = 0
            for i in range(number - 1):
                k = k + 100 / number
                interval.append(k)
            self.quantile = np.nanpercentile(np.ravel(self.array), interval)
            self.intList = []
            for quant in self.quantile:
                self.intList.append(quant)
            self.intList.append(self.raster.max)
            return self.intList
        except Exception as e:
            logging.error(str(e))

    def on_intervalSizeLineEdit_returnPressed(self):
        try:
            self.getDefinedInterval()
            self.updateHistogram()
            self.update()
        except Exception as e:
            logging.error(str(e))

    def getUniqueValues(self):
        """
        Derives unique values from the raster data. In case of unique value numvber larger than 100 rises an
        warning and stop the computation.
        :return: unique value list
        """
        try:
            self.unique = []
            self.unique_count = []
            if len(self.valueList) > 100:
                QMessageBox.warning(None, self.tr("Warning"), self.tr(
                    "Interval number is out of bounds! Too many unique values!"), QMessageBox.Ok)
                return
            else:
                self.intList = []
                for i in range(len(self.valueList)):
                    if self.valueList[i] != self.raster.nodata:
                        self.intList.append(self.valueList[i])
                        self.unique_count.append(self.countList[i])
                        self.unique.append(self.valueList[i])
                self.updateHistogram()
            return self.intList
        except Exception as e:
            logging.error(str(e))

    def getDefinedInterval(self):
        """
        Estimates the class thersholds for defined interval
        :return: list with defined interval thresholds
        """
        try:
            interval = float(self.ui.intervalSizeLineEdit.text())
            maxValue = self.raster.max
            if self.ui.start0CheckBox.isChecked():
                minValue = 0
                if interval < self.raster.min:
                    QMessageBox.warning(
                        None,
                        self.tr("Warning"),
                        self.tr("Interval ({}) is smaller than Raster minimum ({})!").format(
                            interval,
                            self.raster.min),
                        QMessageBox.Ok)
                    return
            else:
                minValue = self.raster.min
            intervalNumber = math.ceil((maxValue - minValue) / interval)
            self.intList = []
            if intervalNumber > 100:
                QMessageBox.warning(
                    None,
                    self.tr("Warning"),
                    self.tr("Interval number is out of bounds! Select a greater interval to proceed!"),
                    QMessageBox.Ok)
                return
            else:
                self.ui.classSpinBox.setValue(intervalNumber)
                for i in range(int(intervalNumber)):
                    if interval * (i + 1) + minValue <= self.raster.max:
                        self.intList.append(interval * (i + 1) + minValue)
                    else:
                        self.intList.append(self.raster.max)
            return self.intList
        except Exception as e:
            logging.error(str(e))

    @pyqtSlot()
    def on_applyPushButton_clicked(self):
        if not self.ui.inputRasterComboBox.currentText() or not self.ui.outputRasterComboBox.currentText():
            QMessageBox.warning(
                self,
                self.tr("Input incomplete"),
                self.tr("Input data missing!"),
                QMessageBox.Ok)
            return
        logging.info(self.tr("Start reclassify data..."))
        self.reclassByTable()

    def reclassByTable(self):
        """
        Reclasses array based on the list
        and writes a classified raster dataset
        :return: None
        """
        array = np.zeros_like(self.array)
        for i, interval in enumerate(self.intList):
            if i == 0:
                array[np.where(self.array <= interval)] = i + 1
            else:
                array[np.where((self.array > self.intList[i - 1]) &
                               (self.array <= self.intList[i]))] = i + 1
        array[np.where(np.isnan(self.array))] = -9999
        array[np.where(self.array == -9999)] = -9999
        self.outRasterPath = str(self.ui.outputRasterComboBox.currentText())
        NoData_value = -9999
        driver = gdal.GetDriverByName('GTiff')
        outRaster = driver.Create(
            self.outRasterPath,
            self.raster.cols,
            self.raster.rows,
            1,
            gdal.GDT_Int32)
        outRaster.SetProjection(self.raster.proj)
        outRaster.SetGeoTransform(self.raster.geoTrans)
        band = outRaster.GetRasterBand(1)
        band.SetNoDataValue(NoData_value)
        outRaster.GetRasterBand(1).WriteArray(array)
        band.ComputeStatistics(False)
        outRaster = None
        array = None
        self.createRAT()
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        logging.info(
            self.tr("Reclassification completed! Reclassified raster {} created.").format(
                self.outRasterPath))

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
        rat.CreateColumn("VALUE", gdal.GFT_Integer, gdalconst.GFU_MinMax)
        rat.CreateColumn("COUNT", gdal.GFT_Integer, gdalconst.GFU_MinMax)
        rat.CreateColumn("DESCR", gdal.GFT_String, gdalconst.GFU_MinMax)
        for i in range(len(value_list)):
            rat.SetValueAsInt(i, 0, int(value_list[i]))
        for i in range(len(count_list)):
            rat.SetValueAsInt(i, 1, int(count_list[i]))

        rows = self.ui.tableWidget.rowCount()

        for i in range(rows):
            item0 = self.ui.tableWidget.item(i, 0)
            text0 = item0.text()
            item1 = self.ui.tableWidget.item(i, 1)
            text1 = item1.text()

            if i != 0:
                rat.SetValueAsString(i, 2, ">" + str(text0) + " - " + str(text1))
            else:
                rat.SetValueAsString(i, 2, str(text0) + " - " + str(text1))
        raster.band.SetDefaultRAT(rat)
        raster = None
