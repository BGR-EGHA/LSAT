# -*- coding: utf-8 -*-

from osgeo import gdal, ogr, osr, gdalconst
import os
import math
import time
import numpy as np
import logging
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from core.libs.GDAL_Libs.Layers import Raster
from core.libs.LSAT_Messages.messages_main import Messenger
from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog
from core.libs.Management.LayerManagement import LayerManagement as LM

from core.uis.Geoprocessing_ui.Slope_ui import Ui_Slope
from core.uis.Geoprocessing_ui.SimpleGUI_ui import Ui_SimpleGUI
from core.uis.Geoprocessing_ui.Aspect_ui import Ui_Aspect
from core.uis.Geoprocessing_ui.Hillshade_ui import Ui_Hillshade


class Hillshade(QMainWindow):
    def __init__(self, projectLocation="", parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_Hillshade()
        self.ui.setupUi(self)
        self.setWindowTitle(self.tr("Hillshade"))
        self.setWindowIcon(QIcon(':/icons/Icons/hillshade.png'))
        self.progress = QProgressBar()
        self.statusBar().addPermanentWidget(self.progress)
        self.message = Messenger()
        self.fileDialog = CustomFileDialog()
        self.projectLocation = projectLocation
        self.paramsintocombobox()
        self.thread_status = False

        validator = QDoubleValidator()
        self.ui.azimuthLineEdit.setValidator(validator)
        self.ui.zFactorLineEdit.setValidator(validator)
        self.ui.zFactorLineEdit.setValidator(validator)
        self.ui.azimuthLineEdit.setText(str(345))
        self.ui.altitudeLineEdit.setText(str(45))
        self.ui.zFactorLineEdit.setText(str(1))

        self.ui.azimuthLineEdit.textEdited.connect(self.validateAzimuth)
        self.ui.altitudeLineEdit.textEdited.connect(self.validateAltitude)
        self.ui.zFactorLineEdit.textEdited.connect(self.validate_zFactor)

    def validate_zFactor(self):
        if str(self.ui.zFactorLineEdit.text()) == "":
            return self.ui.zFactorLineEdit.setText(str(1))
        if float(self.ui.zFactorLineEdit.text()) <= 0:
            return self.ui.zFactorLineEdit.setText(str(1))

    def validateAzimuth(self):
        if str(self.ui.azimuthLineEdit.text()) == "":
            return self.ui.azimuthLineEdit.setText(str(315))
        if float(self.ui.azimuthLineEdit.text()) > 359 or float(self.ui.azimuthLineEdit.text()) < 0:
            return self.ui.azimuthLineEdit.setText(str(0))

    def validateAltitude(self):
        if str(self.ui.altitudeLineEdit.text()) == "":
            return self.ui.altitudeLineEdit.setText(str(45))
        if float(self.ui.altitudeLineEdit.text()) > 90:
            return self.ui.altitudeLineEdit.setText(str(90))
        if float(self.ui.altitudeLineEdit.text()) <= 0:
            return self.ui.altitudeLineEdit.setText(str(0))

    def paramsintocombobox(self) -> None:
        """
        We fill the demRasterComboBox with rasters (*.tif) from the /data/params folder.
        """
        paramsfolder = os.path.join(self.projectLocation, "data", "params")
        raster = []
        for root, dirs, files in os.walk(paramsfolder):
            for f in files:
                if f.lower().endswith(".tif"):
                    raster.append(os.path.join(root, f))
        for r in raster:
            self.ui.demRasterComboBox.insertItem(0, str(r))

    @pyqtSlot()
    def on_demRasterToolButton_clicked(self):
        """
        This method opens the open file dialog and loads the dem raster path
        to the combo box.
        :return: None
        """
        self.fileDialog.openRasterFile(self.projectLocation)
        if self.fileDialog.exec_() == 1:
            for filename in self.fileDialog.selectedFiles():
                if filename is None or str(filename) == "" or str(
                        self.ui.demRasterComboBox.findText(str(filename))) != "-1":
                    return
                else:
                    self.ui.demRasterComboBox.insertItem(0, str(filename))
                    self.ui.demRasterComboBox.setCurrentIndex(
                        self.ui.demRasterComboBox.findText(str(filename)))

    @pyqtSlot()
    def on_cancelPushButton_clicked(self):
        """
        Cancels the procedure and closes the application.
        :return: None
        """
        if self.thread_status:
            self.thread.terminate()
            self.close()
        else:
            self.close()

    @pyqtSlot()
    def on_outputRasterToolButton_clicked(self):
        """
        Sets the output raster path.
        :return: None
        """
        self.fileDialog.saveRasterFile(self.projectLocation)
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
            filename = os.path.normpath(self.fileDialog.selectedFiles()[0])
            if not filename.lower().endswith(".tif"):
                filename = filename + ".tif"
            if os.path.exists(filename):
                QMessageBox.warning(self, self.tr("Path exists!"), self.tr(
                    "File with this name already exists. It will be overwritten!"))
            self.ui.outputRasterLineEdit.setText(filename)

    @pyqtSlot()
    def on_okPushButton_clicked(self):
        """
        Launch the Hillshade analysis.
        :return: None
        """
        if self.ui.demRasterComboBox.currentText() == "" or self.ui.demRasterComboBox.currentText() is None:
            QMessageBox.warning(
                self,
                self.tr("Missing input"),
                self.tr("Specify DEM raster to proceed!"))
            return
        if self.ui.outputRasterLineEdit.text() == "":
            QMessageBox.warning(self, self.tr("Missing input"), self.tr("Specify output location!"))
            return

        self.thread_status = True
        self.progress.setRange(0, 0)
        self.ui.okPushButton.setEnabled(False)
        self.inDataPath = str(self.ui.demRasterComboBox.currentText())
        self.outDataPath = str(self.ui.outputRasterLineEdit.text())
        azimuth = str(self.ui.azimuthLineEdit.text())
        altitude = str(self.ui.altitudeLineEdit.text())
        zFactor = str(self.ui.zFactorLineEdit.text())
        kwargs = (azimuth, altitude, zFactor)
        self.thread = QThread()
        self.worker = Geoprocessing(self.inDataPath, self.outDataPath, kwargs)
        self.worker.moveToThread(self.thread)
        self.worker.finishSignal.connect(self.done)
        self.worker.loggingInfoSignal.connect(self.updateLogger)
        self.thread.started.connect(self.worker.hillshade)
        self.thread.start()

    def updateLogger(self, message):
        logging.info(str(message))

    def done(self):
        """
        Defines actions after the thread emits the signal "finished()".
        :return: None
        """
        self.thread.quit()
        self.thread_status = False
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.ui.okPushButton.setEnabled(True)
        logging.info(self.tr("Analysis completed!"))
        self.message.InfoBoxAnalysisCompleted(str(self.ui.outputRasterLineEdit.text()))


class Aspect(QMainWindow):
    def __init__(self, projectLocation="", parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_Aspect()
        self.ui.setupUi(self)
        self.setWindowTitle(self.tr("Aspect"))
        self.setWindowIcon(QIcon(':/icons/Icons/aspect.png'))
        self.progress = QProgressBar()
        self.statusBar().addPermanentWidget(self.progress)
        self.message = Messenger()
        self.fileDialog = CustomFileDialog()
        self.projectLocation = projectLocation
        self.paramsintocombobox()
        self.thread_status = False

    def paramsintocombobox(self) -> None:
        """
        We fill the demRasterComboBox with rasters (*.tif) from the /data/params folder.
        """
        paramsfolder = os.path.join(self.projectLocation, "data", "params")
        raster = []
        for root, dirs, files in os.walk(paramsfolder):
            for f in files:
                if f.lower().endswith(".tif"):
                    raster.append(os.path.join(root, f))
        for r in raster:
            self.ui.demRasterComboBox.insertItem(0, str(r))

    @pyqtSlot()
    def on_demRasterToolButton_clicked(self):
        """
        This method opens the open file dialog and loads the dem raster path
        to the combo box.
        :return: None
        """
        self.fileDialog.openRasterFile(self.projectLocation)
        if self.fileDialog.exec_() == 1:
            for filename in self.fileDialog.selectedFiles():
                if filename is None or str(filename) == "" or str(
                        self.ui.demRasterComboBox.findText(str(filename))) != "-1":
                    return
                else:
                    self.ui.demRasterComboBox.insertItem(0, str(filename))
                    self.ui.demRasterComboBox.setCurrentIndex(
                        self.ui.demRasterComboBox.findText(str(filename)))

    @pyqtSlot()
    def on_cancelPushButton_clicked(self):
        """
        Cancels the procedure and closes the application.
        :return: None
        """
        if self.thread_status:
            self.thread.terminate()
            self.close()
        else:
            self.close()

    @pyqtSlot()
    def on_outputRasterToolButton_clicked(self):
        """
        Sets the output raster path.
        :return: None
        """
        self.fileDialog.saveRasterFile(self.projectLocation)
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
            filename = os.path.normpath(self.fileDialog.selectedFiles()[0])
            if not filename.lower().endswith(".tif"):
                filename = filename + ".tif"
            if os.path.exists(filename):
                QMessageBox.warning(self, self.tr("Path exists!"), self.tr(
                    "File with this name already exists. It will be overwritten!"))
            self.ui.outputRasterLineEdit.setText(filename)

    @pyqtSlot()
    def on_okPushButton_clicked(self):
        """
        Launch the aspect analysis.
        :return: None
        """
        if self.ui.demRasterComboBox.currentText() == "" or self.ui.demRasterComboBox.currentText() is None:
            QMessageBox.warning(
                self,
                self.tr("Missing input"),
                self.tr("Specify input raster path!"))
            return
        if self.ui.outputRasterLineEdit.text() == "":
            QMessageBox.warning(
                self,
                self.tr("Missing input"),
                self.tr("Specify output raster path!"))
            return

        self.thread_status = True
        self.progress.setRange(0, 0)
        self.ui.okPushButton.setEnabled(False)
        self.inDataPath = str(self.ui.demRasterComboBox.currentText())
        self.outDataPath = str(self.ui.outputRasterLineEdit.text())
        method = str(self.ui.methodComboBox.currentText())
        kwargs = (type, method)
        self.thread = QThread()
        self.worker = Geoprocessing(self.inDataPath, self.outDataPath, kwargs)
        self.worker.moveToThread(self.thread)
        self.worker.finishSignal.connect(self.done)
        self.worker.loggingInfoSignal.connect(self.updateLogger)
        self.thread.started.connect(self.worker.aspect)
        self.thread.start()

    def updateLogger(self, message):
        logging.info(str(message))

    def done(self):
        """
        Defines actions after the thread emits the signal "finished()".
        :return: None
        """
        self.thread.quit()
        self.thread_status = False
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.ui.okPushButton.setEnabled(True)
        logging.info(self.tr("Analysis completed!"))
        self.message.InfoBoxAnalysisCompleted(str(self.ui.outputRasterLineEdit.text()))


class Roughness(QMainWindow):
    def __init__(self, projectLocation="", parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_SimpleGUI()
        self.ui.setupUi(self)
        self.setWindowTitle(self.tr("Roughness"))
        self.setWindowIcon(QIcon(':/icons/Icons/roughness.png'))
        self.progress = QProgressBar()
        self.statusBar().addPermanentWidget(self.progress)
        self.message = Messenger()
        self.fileDialog = CustomFileDialog()
        self.projectLocation = projectLocation
        self.paramsintocombobox()
        self.thread_status = False

    def paramsintocombobox(self) -> None:
        """
        We fill the demRasterComboBox with rasters (*.tif) from the /data/params folder.
        """
        paramsfolder = os.path.join(self.projectLocation, "data", "params")
        raster = []
        for root, dirs, files in os.walk(paramsfolder):
            for f in files:
                if f.lower().endswith(".tif"):
                    raster.append(os.path.join(root, f))
        for r in raster:
            self.ui.demRasterComboBox.insertItem(0, str(r))

    @pyqtSlot()
    def on_demRasterToolButton_clicked(self):
        """
        This method opens the open file dialog and loads the dem raster path
        to the combo box.
        :return: None
        """
        self.fileDialog.openRasterFile(self.projectLocation)
        if self.fileDialog.exec_() == 1:
            for filename in self.fileDialog.selectedFiles():
                if filename is None or str(filename) == "" or str(
                        self.ui.demRasterComboBox.findText(str(filename))) != "-1":
                    return
                else:
                    self.ui.demRasterComboBox.insertItem(0, str(filename))
                    self.ui.demRasterComboBox.setCurrentIndex(
                        self.ui.demRasterComboBox.findText(str(filename)))

    @pyqtSlot()
    def on_cancelPushButton_clicked(self):
        """
        Cancels the procedure and closes the application.
        :return: None
        """
        if self.thread_status:
            self.thread.terminate()
            self.close()
        else:
            self.close()

    @pyqtSlot()
    def on_outputRasterToolButton_clicked(self):
        """
        Sets the output raster path.
        :return: None
        """
        self.fileDialog.saveRasterFile(self.projectLocation)
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
            filename = os.path.normpath(self.fileDialog.selectedFiles()[0])
            if not filename.lower().endswith(".tif"):
                filename = filename + ".tif"
            if os.path.exists(filename):
                QMessageBox.warning(self, self.tr("Path exists!"), self.tr(
                    "File with this name already exists. It will be overwritten!"))
            self.ui.outputRasterLineEdit.setText(filename)

    @pyqtSlot()
    def on_okPushButton_clicked(self):
        """
        Launch the roughness analysis.
        :return: None
        """
        if self.ui.demRasterComboBox.currentText() == "" or self.ui.demRasterComboBox.currentText() is None:
            QMessageBox.warning(
                self,
                self.tr("Missing input"),
                self.tr("Specify input raster path!"))
            return
        if self.ui.outputRasterLineEdit.text() == "":
            QMessageBox.warning(
                self,
                self.tr("Missing input"),
                self.tr("Specify output raster path!"))
            return
        self.thread_status = True
        self.progress.setRange(0, 0)
        self.ui.okPushButton.setEnabled(False)
        self.inDataPath = str(self.ui.demRasterComboBox.currentText())
        self.outDataPath = str(self.ui.outputRasterLineEdit.text())
        kwargs = None
        self.thread = QThread()
        self.worker = Geoprocessing(self.inDataPath, self.outDataPath, kwargs)
        self.worker.moveToThread(self.thread)
        self.worker.finishSignal.connect(self.done)
        self.worker.loggingInfoSignal.connect(self.updateLogger)
        self.thread.started.connect(self.worker.roughness)
        self.thread.start()

    def updateLogger(self, message):
        logging.info(str(message))

    def done(self):
        """
        Defines actions after the thread emits the signal "finished()".
        :return: None
        """
        self.thread.quit()
        self.thread_status = False
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.ui.okPushButton.setEnabled(True)
        logging.info(self.tr("Analysis completed!"))
        self.message.InfoBoxAnalysisCompleted(str(self.ui.outputRasterLineEdit.text()))


class TRI(QMainWindow):
    def __init__(self, projectLocation="", parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_SimpleGUI()
        self.ui.setupUi(self)
        self.setWindowTitle(self.tr("Terrain Ruggedness Index (TRI)"))
        self.setWindowIcon(QIcon(':/icons/Icons/TRI.png'))
        self.progress = QProgressBar()
        self.statusBar().addPermanentWidget(self.progress)
        self.message = Messenger()
        self.fileDialog = CustomFileDialog()
        self.projectLocation = projectLocation
        self.paramsintocombobox()
        self.thread_status = False

    def paramsintocombobox(self) -> None:
        """
        We fill the demRasterComboBox with rasters (*.tif) from the /data/params folder.
        """
        paramsfolder = os.path.join(self.projectLocation, "data", "params")
        raster = []
        for root, dirs, files in os.walk(paramsfolder):
            for f in files:
                if f.lower().endswith(".tif"):
                    raster.append(os.path.join(root, f))
        for r in raster:
            self.ui.demRasterComboBox.insertItem(0, str(r))

    @pyqtSlot()
    def on_demRasterToolButton_clicked(self):
        """
        This method opens the open file dialog and loads the dem raster path
        to the combo box.
        :return: None
        """
        self.fileDialog.openRasterFile(self.projectLocation)
        if self.fileDialog.exec_() == 1:
            for filename in self.fileDialog.selectedFiles():
                if filename is None or str(filename) == "" or str(
                        self.ui.demRasterComboBox.findText(str(filename))) != "-1":
                    return
                else:
                    self.ui.demRasterComboBox.insertItem(0, str(filename))
                    self.ui.demRasterComboBox.setCurrentIndex(
                        self.ui.demRasterComboBox.findText(str(filename)))

    @pyqtSlot()
    def on_outputRasterToolButton_clicked(self):
        """
        Sets the output raster path.
        :return: None
        """
        self.fileDialog.saveRasterFile(self.projectLocation)
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
            filename = os.path.normpath(self.fileDialog.selectedFiles()[0])
            if not filename.lower().endswith(".tif"):
                filename = filename + ".tif"
            if os.path.exists(filename):
                QMessageBox.warning(self, self.tr("Path exists!"), self.tr(
                    "File with this name already exists. It will be overwritten!"))
            self.ui.outputRasterLineEdit.setText(filename)

    @pyqtSlot()
    def on_okPushButton_clicked(self):
        """
        Launch the TRI analysis.
        :return: None
        """
        if self.ui.demRasterComboBox.currentText() == "" or self.ui.demRasterComboBox.currentText() is None:
            QMessageBox.warning(
                self,
                self.tr("Missing input"),
                self.tr("Specify input raster path!"))
            return
        if self.ui.outputRasterLineEdit.text() == "":
            QMessageBox.warning(
                self,
                self.tr("Missing input"),
                self.tr("Specify output raster path!"))
            return
        self.thread_status = True
        self.progress.setRange(0, 0)
        self.ui.okPushButton.setEnabled(False)
        self.inDataPath = str(self.ui.demRasterComboBox.currentText())
        self.outDataPath = str(self.ui.outputRasterLineEdit.text())
        kwargs = None
        self.thread = QThread()
        self.worker = Geoprocessing(self.inDataPath, self.outDataPath, kwargs)
        self.worker.moveToThread(self.thread)
        self.worker.finishSignal.connect(self.done)
        self.worker.loggingInfoSignal.connect(self.updateLogger)
        self.thread.started.connect(self.worker.tri)
        self.thread.start()

    @pyqtSlot()
    def on_cancelPushButton_clicked(self):
        """
        Cancels the procedure and closes the application.
        :return: None
        """
        if self.thread_status:
            self.thread.terminate()
            self.close()
        else:
            self.close()

    def updateLogger(self, message):
        logging.info(str(message))

    def done(self):
        """
        Defines actions after the thread emits the signal "finished()".
        :return: None
        """
        self.thread.quit()
        self.thread_status = False
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.ui.okPushButton.setEnabled(True)
        logging.info(self.tr("Analysis completed!"))
        self.message.InfoBoxAnalysisCompleted(str(self.ui.outputRasterLineEdit.text()))


class TPI(QMainWindow):
    def __init__(self, projectLocation="", parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_SimpleGUI()
        self.ui.setupUi(self)
        self.setWindowTitle(self.tr("Topographic Position Index (TPI)"))
        self.setWindowIcon(QIcon(':/icons/Icons/tpi.png'))
        self.progress = QProgressBar()
        self.statusBar().addPermanentWidget(self.progress)
        self.message = Messenger()
        self.fileDialog = CustomFileDialog()
        self.projectLocation = projectLocation
        self.paramsintocombobox()
        self.thread_status = False

    def paramsintocombobox(self) -> None:
        """
        We fill the demRasterComboBox with rasters (*.tif) from the /data/params folder.
        """
        paramsfolder = os.path.join(self.projectLocation, "data", "params")
        raster = []
        for root, dirs, files in os.walk(paramsfolder):
            for f in files:
                if f.lower().endswith(".tif"):
                    raster.append(os.path.join(root, f))
        for r in raster:
            self.ui.demRasterComboBox.insertItem(0, str(r))

    @pyqtSlot()
    def on_demRasterToolButton_clicked(self):
        """
        This method opens the open file dialog and loads the dem raster path
        to the combo box.
        :return: None
        """
        self.fileDialog.openRasterFile(self.projectLocation)
        if self.fileDialog.exec_() == 1:
            for filename in self.fileDialog.selectedFiles():
                if filename is None or str(filename) == "" or str(
                        self.ui.demRasterComboBox.findText(str(filename))) != "-1":
                    return
                else:
                    self.ui.demRasterComboBox.insertItem(0, str(filename))
                    self.ui.demRasterComboBox.setCurrentIndex(
                        self.ui.demRasterComboBox.findText(str(filename)))

    @pyqtSlot()
    def on_outputRasterToolButton_clicked(self):
        """
        Sets the output raster path.
        :return: None
        """
        self.fileDialog.saveRasterFile(self.projectLocation)
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
            filename = os.path.normpath(self.fileDialog.selectedFiles()[0])
            if not filename.lower().endswith(".tif"):
                filename = filename + ".tif"
            if os.path.exists(filename):
                QMessageBox.warning(self, self.tr("Path exists!"), self.tr(
                    "File with this name already exists. It will be overwritten!"))
            self.ui.outputRasterLineEdit.setText(filename)

    @pyqtSlot()
    def on_okPushButton_clicked(self):
        """
        Launch the TPI analysis.
        :return: None
        """
        if self.ui.demRasterComboBox.currentText() == "" or self.ui.demRasterComboBox.currentText() is None:
            QMessageBox.warning(
                self,
                self.tr("Missing input"),
                self.tr("Specify input raster path!"))
            return
        if self.ui.outputRasterLineEdit.text() == "":
            QMessageBox.warning(
                self,
                self.tr("Missing input"),
                self.tr("Specify output raster path!"))
            return
        self.thread_status = True
        self.progress.setRange(0, 0)
        self.ui.okPushButton.setEnabled(False)
        self.inDataPath = str(self.ui.demRasterComboBox.currentText())
        self.outDataPath = str(self.ui.outputRasterLineEdit.text())
        kwargs = None
        self.thread = QThread()
        self.worker = Geoprocessing(self.inDataPath, self.outDataPath, kwargs)
        self.worker.moveToThread(self.thread)
        self.worker.finishSignal.connect(self.done)
        self.worker.loggingInfoSignal.connect(self.updateLogger)
        self.thread.started.connect(self.worker.tpi)
        self.thread.start()

    def updateLogger(self, message):
        logging.info(str(message))

    def done(self):
        """
        Defines actions after the thread emits the signal "finished()".
        :return: None
        """
        self.thread.quit()
        self.thread_status = False
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.ui.okPushButton.setEnabled(True)
        logging.info(self.tr("Analysis completed!"))
        self.message.InfoBoxAnalysisCompleted(str(self.ui.outputRasterLineEdit.text()))

    @pyqtSlot()
    def on_cancelPushButton_clicked(self):
        """
        Cancels the procedure and closes the application.
        :return: None
        """
        if self.thread_status:
            self.thread.terminate()
            self.close()
        else:
            self.close()


class CalculateSlope(QMainWindow):
    def __init__(self, projectLocation="", parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_Slope()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(':/icons/Icons/Slope.png'))
        self.setWindowTitle(self.tr("Slope"))

        self.progress = QProgressBar()
        self.statusBar().addPermanentWidget(self.progress)
        self.message = Messenger()
        self.fileDialog = CustomFileDialog()
        self.projectLocation = projectLocation
        self.paramsintocombobox()
        self.thread_status = False

    def paramsintocombobox(self) -> None:
        """
        We fill the demRasterComboBox with rasters (*.tif) from the /data/params folder.
        """
        paramsfolder = os.path.join(self.projectLocation, "data", "params")
        raster = []
        for root, dirs, files in os.walk(paramsfolder):
            for f in files:
                if f.lower().endswith(".tif"):
                    raster.append(os.path.join(root, f))
        for r in raster:
            self.ui.demRasterComboBox.insertItem(0, str(r))

    @pyqtSlot()
    def on_demRasterToolButton_clicked(self):
        """
        This method opens the open file dialog and loads the dem raster path
        to the combo box.
        :return: None
        """
        self.fileDialog.openRasterFile(self.projectLocation)
        if self.fileDialog.exec_() == 1:
            for filename in self.fileDialog.selectedFiles():
                if filename is None or str(filename) == "" or str(
                        self.ui.demRasterComboBox.findText(str(filename))) != "-1":
                    return
                else:
                    self.ui.demRasterComboBox.insertItem(0, str(filename))
                    self.ui.demRasterComboBox.setCurrentIndex(
                        self.ui.demRasterComboBox.findText(str(filename)))

    @pyqtSlot()
    def on_outputRasterToolButton_clicked(self):
        """
        Sets the output raster path.
        :return: None
        """
        self.fileDialog.saveRasterFile(self.projectLocation)
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
            filename = os.path.normpath(self.fileDialog.selectedFiles()[0])
            if not filename.lower().endswith(".tif"):
                filename = filename + ".tif"
            if os.path.exists(filename):
                QMessageBox.warning(self, self.tr("Path exists!"), self.tr(
                    "File with this name already exists. It will be overwritten!"))
            self.ui.outputRasterLineEdit.setText(filename)

    @pyqtSlot()
    def on_okPushButton_clicked(self):
        """
        Launch the slope analysis.
        :return: None
        """
        if self.ui.demRasterComboBox.currentText() == "" or self.ui.demRasterComboBox.currentText() is None:
            QMessageBox.warning(
                self,
                self.tr("Missing input"),
                self.tr("Specify input raster path!"))
            return
        if self.ui.outputRasterLineEdit.text() == "":
            QMessageBox.warning(
                self,
                self.tr("Missing input"),
                self.tr("Specify output raster path!"))
            return
        self.thread_status = True
        self.progress.setRange(0, 0)
        self.ui.okPushButton.setEnabled(False)
        self.inDataPath = str(self.ui.demRasterComboBox.currentText())
        self.outDataPath = str(self.ui.outputRasterLineEdit.text())

        # Start the Analysis as Thread
        unitType = self.ui.slopeUnitComboBox.currentText()
        ListeTypen = [u"DEGREE", u"度", u"GRAD", u"градус"]
        if str(unitType) in ListeTypen:
            type = 1
        else:
            type = 2
        method = str(self.ui.methodComboBox.currentText())
        kwargs = (type, method)
        self.thread = QThread()
        self.worker = Geoprocessing(self.inDataPath, self.outDataPath, kwargs)
        self.worker.moveToThread(self.thread)
        self.worker.finishSignal.connect(self.done)
        self.worker.loggingInfoSignal.connect(self.updateLogger)
        self.thread.started.connect(self.worker.calcSlope)
        self.thread.start()

    def updateLogger(self, message):
        logging.info(str(message))

    def done(self):
        """
        Defines actions after the thread emits the signal "finished()".
        :return: None
        """
        self.thread.quit()
        self.thread_status = False
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.ui.okPushButton.setEnabled(True)
        logging.info(self.tr("Analysis completed!"))
        self.message.InfoBoxAnalysisCompleted(str(self.ui.outputRasterLineEdit.text()))

    @pyqtSlot()
    def on_cancelPushButton_clicked(self):
        """
        Cancels the procedure and closes the application.
        :return: None
        """
        if self.thread_status:
            self.thread.terminate()
            self.close()
        else:
            self.close()


class Geoprocessing(QObject):
    finishSignal = pyqtSignal()
    loggingInfoSignal = pyqtSignal(str)

    def __init__(self, inDataPath, outDataPath, kwargs):
        QObject.__init__(self, parent=None)
        self.inDataPath = inDataPath
        self.outDataPath = outDataPath
        self.kwargs = kwargs

    @pyqtSlot()
    def calcSlope(self):
        """
        Generates a slope map from elevation raster
        :return: None
        """
        type = self.kwargs[0]
        method = self.kwargs[1]
        if type == 1:
            slopeFormat = None
        else:
            slopeFormat = "percent"
        if method == "Horn":
            method = "Horn"
        else:
            method = "ZevenbergenThorne"

        self.loggingInfoSignal.emit(self.tr("Calculate slope..."))
        gdal.DEMProcessing(
            self.outDataPath,
            self.inDataPath,
            "slope",
            computeEdges=True,
            slopeFormat=slopeFormat,
            alg=method)
        gdal.DEMProcessingOptions()
        self.finishSignal.emit()

    @pyqtSlot()
    def aspect(self):
        """
        Generates an aspect map from elevation raster,
        outputs a 32-bit float raster with pixel values from 0-360 indicating azimuth
        :return: None
        """
        self.loggingInfoSignal.emit(self.tr("Calculate aspect..."))
        method = self.kwargs[0]
        gdal.DEMProcessing(
            self.outDataPath,
            self.inDataPath,
            "aspect",
            alg=method,
            computeEdges=True)
        self.finishSignal.emit()

    @pyqtSlot()
    def hillshade(self, kwargs=None):
        """
        Generates a shaded relief map from elevation raster
        :param kwargs:
        :return: None
        """
        azimuth, altitude, zFactor = self.kwargs
        self.loggingInfoSignal.emit(self.tr("Calculate hillshade..."))
        gdal.DEMProcessing(
            self.outDataPath,
            self.inDataPath,
            "hillshade",
            azimuth=azimuth,
            altitude=altitude,
            scale=1,
            zFactor=zFactor,
            computeEdges=True)
        self.finishSignal.emit()

    @pyqtSlot()
    def roughness(self, kwargs=None):
        """
        Generates a roughness map from elevation raster. Roughness is the largest inter-cell difference of a
        central pixel and its surrounding cell, as defined in Wilson et al (2007, Marine Geodesy 30:3-35).
        :param kwargs:
        :return:
        """
        self.loggingInfoSignal.emit(self.tr("Calculate roughness..."))
        gdal.DEMProcessing(self.outDataPath, self.inDataPath, "roughness", computeEdges=True)
        self.finishSignal.emit()

    @pyqtSlot()
    def tpi(self, kwargs=None):
        """
        Generates a Topographic Position Index (TPI) map from elevation raster. TPI is
        defined as the difference between a central pixel and the mean of its surrounding cells
        (see Wilson et al 2007, Marine Geodesy 30:3-35).
        :param kwargs:
        :return: None
        """
        self.loggingInfoSignal.emit(self.tr("Calculate TPI..."))
        gdal.DEMProcessing(self.outDataPath, self.inDataPath, "TPI", computeEdges=True)
        self.finishSignal.emit()

    @pyqtSlot()
    def tri(self):
        """
        Generates a Terrain Ruggedness Index (TRI) map from elevation raster
        :return: None
        """
        self.loggingInfoSignal.emit(self.tr("Calculate TRI..."))
        gdal.DEMProcessing(self.outDataPath, self.inDataPath, "TRI", computeEdges=True)
        self.finishSignal.emit()
