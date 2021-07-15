from osgeo import gdal, ogr, osr, gdalconst
import os
import math
import time
import numpy as np
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import os
import logging
from core.libs.GDAL_Libs.Layers import Raster
from core.libs.Management.LayerManagement import LayerManagement as LM
from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog
from core.libs.Analysis.combine import Combine
from core.uis.Combine_ui.Combine_ui import Ui_Combine


class CombineGUI(QMainWindow):
    def __init__(self, projectLocation=None, parent=None):
        QWidget.__init__(self, parent)
        # ui
        self.ui = Ui_Combine()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(':/icons/Icons/model.png'))
        self.ui.addToolButton.setIcon(QIcon(":icons/Icons/plus.png"))
        self.ui.removeToolButton.setIcon(QIcon(":icons/Icons/minus.png"))
        self.ui.setAsMaskToolButton.setIcon(QIcon(":icons/Icons/mask.png"))
        self.progress = QProgressBar()
        self.statusBar().addPermanentWidget(self.progress)
        
        self.projectLocation = projectLocation
        self.maskRasterPath = os.path.join(self.projectLocation, "region.tif")
        self.ui.maskLineEdit.setText(self.maskRasterPath)
        self.fileDialog = CustomFileDialog()

    @pyqtSlot()
    def on_addToolButton_clicked(self):
        """
        Add a single or multiple rasters (multiple selection allowed) to the raster combo box and the raster
        dataset collection.
        :return: None
        """
        self.fileDialog.openRasterFiles(self.projectLocation)
        if self.fileDialog.exec_() == 1:
            for filename in self.fileDialog.selectedFiles():
                self.ui.rasterCollectionListWidget.addItem(os.path.normpath(filename))

    @pyqtSlot()
    def on_removeToolButton_clicked(self):
        """
        Removes a selected raster dataset from the raster dataset collection.
        :return: None
        """
        self.items = self.ui.rasterCollectionListWidget.selectedItems()
        if self.items:
            for item in self.items:
                self.ui.rasterCollectionListWidget.takeItem(
                    self.ui.rasterCollectionListWidget.row(item))

    @pyqtSlot()
    def on_maskToolButton_clicked(self):
        self.fileDialog.openRasterFile(self.projectLocation)
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
            mask = os.path.normpath(self.fileDialog.selectedFiles()[0])
            self.ui.maskLineEdit.setText(mask)

    @pyqtSlot(bool)
    def on_maskRasterCheckBox_clicked(self, state: bool) -> None:
        """
        We only allow the User to change the mask raster if he really wants to do it. If he
        decides against it and checks the Checkbox we reset the lineEdit to its defaults
        (region.tif).
        """
        self.ui.maskLineEdit.setEnabled(not(state))
        self.ui.maskToolButton.setEnabled(not(state))
        self.ui.setAsMaskToolButton.setEnabled(not(state))
        if state:
            self.ui.maskLineEdit.setText(self.maskRasterPath)

    @pyqtSlot()
    def on_setAsMaskToolButton_clicked(self):
        """
        Set a selected dataset in the raster dataset collection as mask dataset.
        :return: None
        """
        selected = self.ui.rasterCollectionListWidget.selectedItems()
        if selected:
            self.ui.maskLineEdit.setText(selected[0].text())

    @pyqtSlot()
    def on_combineRasterToolButton_clicked(self):
        self.fileDialog.saveRasterFile(self.projectLocation)
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
            filename = os.path.normpath(self.fileDialog.selectedFiles()[0])
            if filename.lower().endswith(".tif"):
                self.ui.combineRasterLineEdit.setText(filename)
            else:
                self.ui.combineRasterLineEdit.setText(filename + ".tif")

    @pyqtSlot()
    def on_applyPushButton_clicked(self):
        if not self._checkinputs():
            return
        self.ui.applyPushButton.setEnabled(False)
        maskRasterPath = self.ui.maskLineEdit.text()
        outPath = self.ui.combineRasterLineEdit.text()
        rasterPaths = []
        # Set the logging info
        logging.info(self.tr("Start combine analysis..."))
        # Set the progress bar range to (0, 0) -> creates a pulsation progress bar.
        self.progress.setRange(0, 0)
        for idx in range(self.ui.rasterCollectionListWidget.count()):
            raster_path = self.ui.rasterCollectionListWidget.item(idx).text()
            rasterPaths.append(raster_path)
        self.thread = QThread()
        self.worker = Combine(rasterPaths, outPath, maskRasterPath, self.projectLocation)
        self.worker.moveToThread(self.thread)
        self.worker.finishSignal.connect(self.done)
        self.worker.loggingInfoSignal.connect(self.updateLogger)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def _checkinputs(self) -> bool:
        """
        Validate inputs before starting combine.
        Returns bool indicating if inputs are correct.
        """
        if self.ui.rasterCollectionListWidget.count() < 2:
            QMessageBox.warning(self, self.tr("Insufficient input"), self.tr(
                "No or insufficient input data! Specify at least two input raster datasets!"))
            return False
        if not os.path.isfile(self.ui.maskLineEdit.text()):
            logging.info(self.tr("{} is not a valid file.").format(self.ui.maskLineEdit.text()))
            return False
        return True

    def updateLogger(self, message):
        logging.info(str(message))

    def done(self):
        self.thread.quit()
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.ui.applyPushButton.setEnabled(True)

# following functions add Drag and Drop Support to the raster import widget.
    def dragEnterEvent(self, event):
        """
        Gets called when a user drags something into the widget. Changes if the ui indicates
        accepting or ignoring the drop.
        We had to enable acceptDrops in the _ui.py.
        """
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """
        Gets called after the user lets go of the left mouse button in the drag and drop event.
        We check if the dragged elemt is a local raster file and if yes add it to
        rasterCollectionListWidget
        """
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                if url.isLocalFile() and url.toLocalFile().lower().endswith(".tif"):
                    links.append(os.path.normpath(url.toLocalFile()))
            self.ui.rasterCollectionListWidget.addItems(links)
        else:
            event.ignore()
