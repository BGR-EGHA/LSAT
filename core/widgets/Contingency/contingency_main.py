# -*- coding: utf-8 -*-

import numpy as np
import traceback
import os
import logging
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog
from core.uis.Contingency_ui.Contingency_ui import Ui_Contingency
from core.widgets.RasterAttributeTable.rat_main import RasterAttributeTable
from core.widgets.Contingency.contingency_calc import Contingency


class ContingencyGUI(QMainWindow):
    def __init__(self, projectLocation=None, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_Contingency()
        self.ui.setupUi(self)
        # Adding Icons to the buttons
        self.setWindowIcon(QIcon(':/icons/Icons/Contingency_tab.png'))
        self.ui.addRasterToolButton.setIcon(QIcon(':/icons/Icons/plus.png'))
        self.ui.removeRasterToolButton.setIcon(QIcon(':/icons/Icons/minus.png'))
        self.ui.attributeTableToolButton.setIcon(QIcon(':/icons/Icons/AttributeTable.png'))

        self.dialog = CustomFileDialog()
        self.progress = QProgressBar()
        self.statusBar().addPermanentWidget(self.progress)
        self.projectLocation = projectLocation

        self.maskRasterPath = os.path.join(projectLocation, "region.tif")
        self.ui.maskRasterLineEdit.setText(self.maskRasterPath)

        self.matrix_C = None
        self.results = None

    # dragEnterEvent and dropEvent are needed to support Drag & Drop.
    def dragEnterEvent(self, event):
        """
        Gets called when a user drags something into the widget. Changes if the ui indicates
        accepting or ignoring the drop.
        """
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """
        Gets called after the user lets go of the left mouse button in the drag and drop event.
        We check if the dragged elemt is a local raster file and if yes add it to
        listWidget
        """
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            links = []
            for url in event.mimeData().urls():
                if url.isLocalFile() and url.toLocalFile().lower().endswith(".tif"):
                    links.append(os.path.normpath(url.toLocalFile()))
            self.ui.listWidget.addItems(links)
            self.updateMatrix()
        else:
            event.ignore()

    @pyqtSlot(bool)
    def on_referenceCheckBox_clicked(self, state: bool) -> None:
        """
        Enables/Disables maskRaster changes based on checkbox state.
        :return: None
        """
        self.ui.maskRasterLineEdit.setEnabled(not state)
        self.ui.maskRasterToolButton.setEnabled(not state)
        if state:
            self.ui.maskRasterLineEdit.setText(self.maskRasterPath)

    @pyqtSlot()
    def on_applyPushButton_clicked(self):
        """
        If the User supplied 2 or more input rasters we disable all buttons, gather all supplied input
        and start a thread with input and the path to the Mask Raster as arguments
        Else, we inform the User to give more input
        """
        try:
            if self.ui.listWidget.count() < 2:
                QMessageBox.warning(self, self.tr("Insufficient input"), self.tr(
                    "No or insufficient input data! Specify at least two input raster datasets!"))
                return
            self.results = {}
            self.ui.addRasterToolButton.setEnabled(False)
            self.ui.attributeTableToolButton.setEnabled(False)
            self.ui.maskRasterToolButton.setEnabled(False)
            self.ui.removeRasterToolButton.setEnabled(False)
            self.ui.applyPushButton.setEnabled(False)

            logging.info(self.tr("Start contingency analysis..."))
            self.progress.setRange(0, 0)
            # Create data pairs
            data_list = []
            for i in range(self.ui.listWidget.count()):
                # We collect all elements of the listwidget into a list
                item = self.ui.listWidget.item(i)
                data_list.append(item.text())

            self.thread = QThread()
            self.worker = Contingency(self.maskRasterPath, data_list)
            self.worker.moveToThread(self.thread)
            # We reenable the buttons once the thread finishes
            self.worker.finishSignal.connect(self.done)
            self.worker.resultsSignal.connect(self.updateMatrix)
            self.worker.loggingInfoSignal.connect(self.updateLogger)
            self.thread.started.connect(self.worker.run)
            self.thread.start()
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)

    def updateMatrix(self, signal=None) -> None:
        """
        If signal == None we added/removed a raster and prepare arrays.
        If signal != None the calculation finished and we save the results.
        """
        if signal is None:
            count = self.ui.listWidget.count()
            names = []
            if self.matrix_C is None:
                for i in range(count):
                    item = self.ui.listWidget.item(i)
                    names.append((os.path.splitext(os.path.basename(item.text()))[0], 'f'))
                    self.matrix_C = np.ones(shape=(count,), dtype=names)
                    self.matrix_CV = np.ones(shape=(count,), dtype=names)
        else:
            row, col, results = signal
            self.results[(row, col)] = results
            self.results[(col, row)] = results
            self.matrix_C[row][col] = results[0]
            self.matrix_C[col][row] = results[0]
            self.matrix_CV[row][col] = results[1]
            self.matrix_CV[col][row] = results[1]

    def writeOutputFile(self):
        """
        Writes results from the analysis to the npz-file
        :return: None
        """
        outputPath = os.path.join(
            self.projectLocation,
            "results",
            "statistics",
            self.ui.outputFileNameLineEdit.text() +
            "_ctg.npz")
        np.savez_compressed(outputPath,
                            matrix_C=self.matrix_C,
                            matrix_CV=self.matrix_CV,
                            results=[self.results])
        logging.info(self.tr("Results saved in {}").format(outputPath))

    def done(self):
        """
        This method manages the activities on receiving the finish signal from thread.
        It updates the logging info, trigger a message info box and closes the application.
        :return: None
        """
        self.thread.quit()
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        logging.info(self.tr("Analysis completed!"))
        self.ui.applyPushButton.setEnabled(True)
        self.ui.addRasterToolButton.setEnabled(True)
        self.ui.attributeTableToolButton.setEnabled(True)
        self.ui.maskRasterToolButton.setEnabled(True)
        self.ui.removeRasterToolButton.setEnabled(True)
        self.writeOutputFile()

    def updateLogger(self, message):
        logging.info(message)

    @pyqtSlot()
    def on_maskRasterToolButton_clicked(self):
        """
        Set the mask raster dataset on browse function.
        :return: None
        """
        self.dialog.openRasterFile(self.projectLocation)
        if self.dialog.exec_() == 1 and self.dialog.selectedFiles():
            self.ui.maskRasterLineEdit.setText(self.dialog.selectedFiles()[0])

    @pyqtSlot()
    def on_removeRasterToolButton_clicked(self):
        """
        Removes a selected raster dataset from the raster dataset collection.
        :return: None
        """
        if self.ui.listWidget.selectedItems():
            item = self.ui.listWidget.selectedItems()[0]
            self.ui.listWidget.takeItem(self.ui.listWidget.row(item))

    @pyqtSlot()
    def on_attributeTableToolButton_clicked(self):
        if self.ui.listWidget.selectedItems():
            item = self.ui.listWidget.selectedItems()[0]
            self.rat = RasterAttributeTable(item.text())
            self.rat.show()

    @pyqtSlot()
    def on_addRasterToolButton_clicked(self):
        """
        Add a single or multiple rasters (multiple selection allowed) to the raster combo box and the raster
        dataset collection.
        :return: None
        """
        self.dialog.openRasterFiles(self.projectLocation)
        if self.dialog.exec_() == 1 and self.dialog.selectedFiles():
            for file in self.dialog.selectedFiles():
                basename = os.path.basename(file) # Can't have two files with same basename
                exists = self.ui.listWidget.findItems(basename, Qt.MatchEndsWith)
                if not exists:
                    self.ui.listWidget.addItem(file)
                    self.matrix_C = None
                    self.updateMatrix()
                else:
                    logging.info(self.tr("{} already in list. Skipping.").format(basename))
