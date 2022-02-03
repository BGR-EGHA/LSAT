from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtGui, QtCore, QtWidgets
import sys
import os
import numpy as np
import logging
import matplotlib
from osgeo import gdal
from osgeo import gdalconst
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar

from core.uis.SensitivityReclass_ui.SensReclass_ui import Ui_SensitivityReclass
from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog
from core.libs.LSAT_Messages.messages_main import Messenger as msg
from core.libs.GDAL_Libs.Layers import Raster, Feature
from core.libs.Analysis.BivariateSolver import WofE
from core.widgets.RasterInfo.rasterInfo_main import RasterInfo


class SensitivityReclass(QMainWindow):
    def __init__(self, projectPath, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_SensitivityReclass()
        self.ui.setupUi(self)
        self.projectPath = projectPath
        self.dialog = CustomFileDialog()
        self.msg = msg()
        self.setWindowIcon(QIcon(":/icons/Icons/SensitivityReclass.png"))
        self.progressBar = QProgressBar()
        self.statusBar().addPermanentWidget(self.progressBar)
        self.fig = Figure(facecolor="white")
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.ui.graphicGroupBox)

        # 2x1 Grid in first subplot
        self.axesHist = self.fig.add_subplot(211)
        self.axesHist.set_xlabel(self.tr('Value'))
        self.axesHist.set_ylabel(self.tr('Pixel count'))

        # 2x1 Grid in second subplot
        self.axesSC = self.fig.add_subplot(212)
        SensitivityReclass.axesSC = self.axesSC
        self.axesSC.set_xlabel(self.tr('Value'))
        self.axesSC.set_ylabel(self.tr('Cumulative sC'))
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.ui.graphicGroupBox)
        self.ui.graphicsGroupBoxGridLayout.addWidget(self.canvas)
        self.ui.graphicsGroupBoxGridLayout.addWidget(self.mpl_toolbar)

        # self.ui.graphicGroupBox.setLayout(self.ui.graphicsGroupBoxGridLayout)
        self.press = None
        self.background = None
        self.thisline = None
        self.connectmlpcanvas()
        self.canvas.draw()
        self.fig.tight_layout()

        self.populatecombobox(projectPath)
        if self.ui.inputRasterComboBox.count() != 0:
            self.readRasterData()

    def connectmlpcanvas(self):
        """
        Connects events and handling for Matplotlib Canvas and fig.
        """
        self.cid_onpick = self.canvas.mpl_connect("pick_event", self.onPick)
        self.cid_onpress = self.canvas.mpl_connect("button_press_event", self.onPress)
        self.cid_onrelease = self.canvas.mpl_connect("button_release_event", self.onRelease)
        self.cid_onmotion = self.canvas.mpl_connect("motion_notify_event", self.onMotion)
        self.cid_onresize = self.canvas.mpl_connect("resize_event", self.onResize)

    def populatecombobox(self, projectPath):
        """
        Scans the ProjectPath for inventory and raster information and adds them to the
        corresponding Comboboxes.
        """
        if os.path.isdir(self.projectPath):
            raster_data_path = os.path.join(self.projectPath, "data", "params")
            inventory_data_path = os.path.join(self.projectPath, "data", "inventory", "training")
            for datafile in os.listdir(raster_data_path):
                if datafile.lower().endswith(".tif"):
                    self.ui.inputRasterComboBox.insertItem(
                        0, os.path.join(raster_data_path, datafile))
            for datafile in os.listdir(inventory_data_path):
                if datafile.lower().endswith(".shp"):
                    self.ui.inputFeatureComboBox.insertItem(
                        0, os.path.join(inventory_data_path, datafile))

    def onPick(self, event):
        """
        Provide handling for Matlplotlib onpick event
        """
        self.thisline = event.artist
        self.thisline.set_linewidth(3)
        self.line_xdata = self.thisline.get_xdata()
        self.line_ydata = self.thisline.get_ydata()
        ind = event.ind

    def onPress(self, event):
        """
        Gets called when the user clicks in the canvas
        """
        try:
            if event.inaxes != self.axesSC:
                return
            if event.button == 1 and self.thisline:
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
                if event.xdata > self.raster.max or event.xdata < self.raster.min:
                    QMessageBox.warning(self, self.tr("Invalid value"), self.tr(
                        "Trying to set a class boundary outside data range!"), QMessageBox.Ok)
                    return
                a, b = self.axesSC.get_ylim()
                rowPosition = self.ui.reclassTableTableWidget.rowCount()
                self.ui.reclassTableTableWidget.insertRow(rowPosition)
                self.axesSC.plot([event.xdata, event.xdata], [a, b], color='r',
                                 linestyle='-', linewidth=1, picker=5, label=str(rowPosition), zorder=2)
                self.canvas.draw()
                self.fig.tight_layout()
                self.update()

            if event.button == 1 and event.dblclick and self.thisline:
                ln = self.thisline
                label = ln.get_label()
                rowPosition = int(label)
                self.ui.reclassTableTableWidget.removeRow(rowPosition)
                ln.remove()
                self.canvas.draw()
                self.fig.tight_layout()
        except BaseException:
            pass

    def onRelease(self, event):
        """
        Gets called when the user releases a mouse click made in the canvas.
        """
        if event.xdata > self.raster.max or event.xdata < self.raster.min:
            QMessageBox.warning(self, self.tr("Invalid value"), self.tr(
                "Trying to set a class boundary outside data range!"), QMessageBox.Ok)
            return
        self.press = None
        if self.thisline is not None:
            self.thisline.set_linewidth(1)
            self.update()
            self.thisline = None

    def onMotion(self, event):
        """
        Gets called when the mousecourser moves in the canvas
        """
        try:
            if self.press is not None and event.inaxes == self.thisline.axes:
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

    def onResize(self, event):
        """
        Gets called when the user changes the window size. Tightens the layout.
        """
        self.fig.tight_layout()

    def done(self):
        logging.info(self.tr("Sensitivity analysis completed!"))
        self.ui.updateProgressBar.setRange(0, 100)
        self.ui.updateProgressBar.setValue(100)

    def update(self):
        """
        Updates graphics and tablet widget
        """
        colName1 = QTableWidgetItem(self.tr("Value range"))
        self.ui.reclassTableTableWidget.setHorizontalHeaderItem(0, colName1)
        colName2 = QTableWidgetItem(self.tr("New value"))
        self.ui.reclassTableTableWidget.setHorizontalHeaderItem(1, colName2)
        validation_list = [self.raster.max]
        for child in self.axesSC.get_children():
            if isinstance(child, matplotlib.lines.Line2D) and len(str(child.get_label())) < 4:
                validation_list.append(child.get_xdata()[0])
                child.remove()
        validation_list = np.unique(validation_list).tolist()

        self.ui.reclassTableTableWidget.setRowCount(len(validation_list))
        bottom, top = self.axesSC.get_ylim()
        for i, value in enumerate(validation_list):
            if i == 0:
                item0 = QTableWidgetItem(F"{self.raster.min:.2f}-{value:.2f}")
            else:
                item0 = QTableWidgetItem(F"{validation_list[i-1]:.2f}-{value:.2f}")
            item0.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.ui.reclassTableTableWidget.setItem(i, 0, item0)
            item1 = QTableWidgetItem(f"{i + 1}")
            item1.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.ui.reclassTableTableWidget.setItem(i, 1, item1)

            self.axesSC.plot([value, value], [bottom, top], color='r', linestyle='-',
                             linewidth=1, picker=5, label=str(i), zorder=2)
        self.reclass_list = validation_list
        self.canvas.draw()
        self.canvas.flush_events()
        self.fig.tight_layout()

    def reclassByTable(self):
        """
        Reclasses array based on the validation_list generated in update()
        and writes a classified raster dataset
        """
        array = np.zeros_like(self.raster.getArrayFromBand())
        rasterarray = self.raster.getArrayFromBand()
        for i in range(len(self.reclass_list)):
            if i == 0:
                array[np.where(rasterarray <= self.reclass_list[i])] = i + 1
            else:
                array[np.where((rasterarray > self.reclass_list[i - 1]) &
                               (rasterarray <= self.reclass_list[i]))] = i + 1

        outRasterPath = self.ui.outputRasterLineEdit.text()
        NoData_value = -9999  # Changed from 0
        driver = gdal.GetDriverByName('GTiff')
        outRaster = driver.Create(
            outRasterPath,
            self.raster.cols,
            self.raster.rows,
            1,
            gdal.GDT_Int16)
        outRaster.SetProjection(self.raster.proj)
        outRaster.SetGeoTransform(self.raster.geoTrans)
        self.band = outRaster.GetRasterBand(1)
        self.band.SetNoDataValue(NoData_value)
        outRaster.GetRasterBand(1).WriteArray(array)
        self.band.ComputeStatistics(False)
        outRaster = None
        del array
        self.createRAT(outRasterPath)
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(100)
        logging.info(self.tr("Sensitivity reclass completed!"))
        logging.info(self.tr("Output raster {} created.").format(outRasterPath))

    def createRAT(self, outRasterPath):
        """
        Create a basic RAT for the raster datset contaning value and count field and populate it
        with description
        """
        raster = Raster(outRasterPath)
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

        rows = self.ui.reclassTableTableWidget.rowCount()

        for i in range(rows):
            item = self.ui.reclassTableTableWidget.item(i, 0)
            text = item.text()
            rat.SetValueAsString(i, 2, text)
        raster.band.SetDefaultRAT(rat)
        raster = None

    def readRasterData(self):
        """
        Read the data and calculate default values for intervals.
        """
        # Trys to remove widget. Won't initially work because we haven't added one yet.
        try:
            self.ui.rasterStatisticsGridLayout.removeWidget(self.rasterInfo)
        except AttributeError:
            pass
        self.rasterInfo = RasterInfo(self.ui.inputRasterComboBox.currentText())
        self.ui.rasterStatisticsGridLayout.addWidget(self.rasterInfo)
        self.raster = Raster(self.ui.inputRasterComboBox.currentText())
        self.array = self.raster.getArrayFromBand()
        self.valueList, self.countList = np.unique(self.array, return_counts=True)
        self.getHistogram(self.raster)

    def getHistogram(self, raster):
        """
        Displays a Histogram in the UI (How many pixel with which value exist)
        """
        hist = raster.band.GetHistogram(raster.min, raster.max, 50, 0, 0)
        hist_array = np.array(hist)
        interval = (raster.max - raster.min) / 50
        bins = raster.min
        hist_x = []
        for i in range(50):
            bins += interval
            hist_x.append(bins)
        if "Float" in self.raster.type:
            self.axesHist.fill_between(hist_x, 0, hist_array / 1000, color = "grey", alpha = 0.5)
        else:
            self.axesHist.bar(hist_x, hist_array / 1000, align = "center", color = "grey", alpha = 0.5)
        a, b = self.axesHist.get_ylim()
        self.canvas.draw()

    @pyqtSlot(int)
    def on_inputRasterComboBox_activated(self):
        """
        We clear the Matplotlib Subplots and update them with new Raster Information
        """
        self.axesHist.clear()
        self.axesHist.set_xlabel(self.tr('Value'))
        self.axesHist.set_ylabel(self.tr('Pixel count'))
        self.axesSC.clear()
        self.axesSC.set_xlabel(self.tr('Value'))
        self.axesSC.set_ylabel(self.tr('Cumulative sC'))
        self.readRasterData()

    @pyqtSlot(int)
    def on_quantileSpinBox_valueChanged(self):
        """
        Resets Progressbar when quantileSpinBox changed
        """
        self.ui.updateProgressBar.setValue(0)

    @pyqtSlot()
    def on_applyPushButton_clicked(self):
        """
        Checks if Input Raster, Feature and Output are given and then starts reclassByTable()
        """
        if (self.ui.outputRasterLineEdit.text() == ""
            or self.ui.inputRasterComboBox.currentText() == ""
            or self.ui.inputFeatureComboBox.currentText() == ""):
            self.msg.WarningMissingInput()
            return
        logging.info(self.tr("Start raster reclass..."))
        self.progressBar.setRange(0, 0)
        self.reclassByTable()

    @pyqtSlot()
    def on_outputRasterToolButton_clicked(self):
        """
        Updates Output lineedit with Savedialog
        """
        self.dialog.saveRasterFile(self.projectPath)
        if self.dialog.exec_() and self.dialog.selectedFiles():
            fileName = os.path.normpath(self.dialog.selectedFiles()[0])
            if os.path.splitext(fileName)[1].lower() == ".tif":
                self.ui.outputRasterLineEdit.setText(fileName)
            else:
                self.ui.outputRasterLineEdit.setText(f"{fileName}.tif")

    @pyqtSlot()
    def on_inputRasterToolButton_clicked(self):
        """
        Updates input Raster ComboBox with OpenFileName and calls readRasterData with new Raster
        """
        self.dialog.openRasterFile(self.projectPath)
        if self.dialog.exec_() == 1 and self.dialog.selectedFiles():
            self.ui.inputRasterComboBox.insertItem(0, self.dialog.selectedFiles()[0])
            self.readRasterData()

    @pyqtSlot()
    def on_inputFeatureToolButton_clicked(self):
        """
        Updates input Feature CbomboBox with getOpenFileName
        """
        self.dialog.openFeatureFile(self.projectPath)
        if self.dialog.exec_() == 1 and self.dialog.selectedFiles():
            self.ui.inputFeatureComboBox.insertItem(0, self.dialog.selectedFiles()[0])

    @pyqtSlot()
    def on_updatePushButton_clicked(self):
        """
        Checks if Input Raster and Feature are given and then starts preprocessing()
        """
        if (not self.ui.inputRasterComboBox.currentText() or
                not self.ui.inputFeatureComboBox.currentText()):
            self.msg.WarningMissingInput()
            return
        if int(self.ui.quantileSpinBox.value()) < 2:
            QMessageBox.warning(
                self,
                self.tr("< 2 Quantils"),
                self.tr(">= 2 Quantils needed!"),
                QMessageBox.Ok)
            return
        logging.info(
            self.tr("Calculate sensitivity with {} quantils...").format(
                self.ui.quantileSpinBox.value()))
        self.ui.updateProgressBar.setRange(0, 0)
        self.preprocessing()
        self.done()

    def preprocessing(self):
        self.raster = Raster(self.ui.inputRasterComboBox.currentText())
        self.feat = Feature(self.ui.inputFeatureComboBox.currentText())
        self.intList = self.raster.getQuantile(qNumber=int(self.ui.quantileSpinBox.value()))
        self.workspace = os.path.join(self.projectPath, "workspace")
        recl_raster = self.raster.reclass(
            self.intList, os.path.join(
                self.workspace, "recl_tmp.tif"))
        land_rast = self.feat.rasterizeLayer(
            self.raster.path, os.path.join(
                self.workspace, "landsl_bool.tif"))
        evidenceRaster = Raster(os.path.join(self.workspace, "recl_tmp.tif"))
        eventRaster = Raster(land_rast)
        wofe = WofE(evidenceRaster, eventRaster, "")
        x = self.intList
        y = [0]
        y_val = wofe.table['Contrast'] / np.sqrt(wofe.table['Variance'])
        value = 0
        for i in y_val:
            value = value + i
            y.append(value)
        oldBottom, oldTop = self.axesSC.get_ylim()
        # 1 to keep a tiny distance to border
        Top = max(y)+1 if max(y) > oldTop else oldTop
        Bottom = min(y)-1 if min(y) < oldBottom else oldBottom
        self.axesSC.set_ylim(Bottom, Top)
        self.axesSC.plot(x, y, label=f"{self.ui.quantileSpinBox.value()}_quantils")
        self.update()
