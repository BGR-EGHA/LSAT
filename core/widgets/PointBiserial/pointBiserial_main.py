import glob
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import logging

from core.uis.PointBiserial_ui.PointBiserial_ui import Ui_PointBiserial
from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog
from core.widgets.PointBiserial.pointBiserial_calc import PointBiserialCalc


class PointBiserial(QMainWindow):
    def __init__(self, projectLocation="", parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_PointBiserial()
        self.ui.setupUi(self)
        self.projectLocation = projectLocation
        self.fileDialog = CustomFileDialog()
        self.autofillInventory()
        self.autofillRasters()

    def autofillInventory(self) -> None:
        """
        Gets called when widget starts. Autofills the inventoryComboBox with .shp, .geojson and .kml
        files in the *projectLocation*/data/inventory folder and its subfolders.
        """
        extensions = (".shp", ".kml", ".geojson")
        for file in glob.glob(f"{self.projectLocation}/data/inventory/**/*.*", recursive=True):
            if file.lower().endswith(extensions):
                self.ui.inventoryComboBox.addItem(str(os.path.normpath(file)))

    def autofillRasters(self) -> None:
        """
        Gets called when widget starts. Autofills the discrete and continuousComboBox with .tif
        files in the *projectLocation*/data/params folder and its subfolders.
        """
        for file in glob.glob(f"{self.projectLocation}/data/params/**/*.tif", recursive=True):
            self.ui.discreteComboBox.addItem(str(os.path.normpath(file)))
            self.ui.continuousComboBox.addItem(str(os.path.normpath(file)))

    @pyqtSlot()
    def on_inventoryToolButton_clicked(self):
        """
        Opens a dialog to select a feature to add its path to inventoryComboBox.
        """
        self.fileDialog.openFeatureFile(self.projectLocation)
        if self.fileDialog.exec_() == 1:
            for filename in self.fileDialog.selectedFiles():
                self.ui.inventoryComboBox.addItem(str(os.path.normpath(filename)))

    @pyqtSlot()
    def on_discreteToolButton_clicked(self):
        """
        Opens a dialog to select a raster to add its path to discreteComboBox.
        """
        self.fileDialog.openRasterFile(self.projectLocation)
        if self.fileDialog.exec_() == 1:
            for filename in self.fileDialog.selectedFiles():
                self.ui.discreteComboBox.addItem(str(os.path.normpath(filename)))

    @pyqtSlot()
    def on_continuousToolButton_clicked(self):
        """
        Opens a dialog to select a raster to add its path to continuousComboBox.
        """
        self.fileDialog.openRasterFile(self.projectLocation)
        if self.fileDialog.exec_() == 1:
            for filename in self.fileDialog.selectedFiles():
                self.ui.continuousComboBox.addItem(str(os.path.normpath(filename)))

    @pyqtSlot()
    def on_applyPushButton_clicked(self):
        discrete = self.ui.discreteComboBox.currentText()
        continuous = self.ui.continuousComboBox.currentText()
        if self.ui.compareLsToNonLsCheckBox.isChecked():
            inventory = self.ui.inventoryComboBox.currentText()
        else:
            inventory = ""
        outputName = self.ui.outputLineEdit.text()
        if self._validate(discrete, continuous, inventory):
            self.thread = QThread()
            self.calc = PointBiserialCalc(discrete, continuous, inventory, outputName, self.projectLocation)
            self.calc.moveToThread(self.thread)
            self.thread.started.connect(self.calc.run)
            self.calc.finishSignal.connect(self.done)
            self.thread.start()

    def _validate(self, discrete: str, continuous: str, inventory: str) -> bool:
        if os.path.isfile(discrete) and os.path.isfile(continuous):
            if inventory == "" or os.path.isfile(inventory):
                return True
        return False

    def done(self, outputPath):
        """
        Exit PointBiserialCalc Thread and Update Log and Ui to tell user calculation is done.
        Gets called with finishSignal from PointBiserialCalc Thread.
        """
        self.thread.exit()
        logging.info(self.tr("Results saved in {}").format(outputPath))
