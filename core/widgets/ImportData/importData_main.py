import logging
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog
from core.uis.ImportRasterData_ui.ImportRasterData_ui import Ui_ImportRasterData
from core.widgets.ImportData.importData_importRaster import ImportRaster
from core.widgets.ImportData.importData_dialog import ReprojectionSettings


class ImportRasterData(QMainWindow):
    def __init__(self, projectlocation, parent=None):
        super().__init__()
        self.projectlocation = projectlocation
        self.maskpath = os.path.join(projectlocation, "region.tif")
        self.paramspath = os.path.join(projectlocation, "data", "params")
        self.dialog = CustomFileDialog()
        # ui
        self.ui = Ui_ImportRasterData()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(':/icons/Icons/LoadRaster_bw.png'))
        self.ui.maskRasterLineEdit.setText(self.maskpath)
        self.ui.outputLocationLineEdit.setText(self.paramspath)
        # Can't add Progressbar to Statusbar with Qt Designer
        self.ui.progress = QProgressBar()
        self.ui.statusbar.addPermanentWidget(self.ui.progress)
        # Add icons to buttons
        self.ui.addToolButton.setIcon(QIcon(":icons/Icons/plus.png"))
        self.ui.removeToolButton.setIcon(QIcon(":icons/Icons/minus.png"))
        self.ui.setAsMaskToolButton.setIcon(QIcon(":icons/Icons/mask.png"))

    @pyqtSlot()
    def on_addToolButton_clicked(self):
        """
        Calls CustomFileDialog to add Rasters to the rasterCollectionListWidget.
        """
        self.dialog.openRasterFiles(self.projectlocation)
        if self.dialog.exec_() == 1 and self.dialog.selectedFiles():
            self.ui.rasterCollectionListWidget.addItems(
                [*map(os.path.normpath, self.dialog.selectedFiles())])

    @pyqtSlot()
    def on_removeToolButton_clicked(self):
        """
        Removes the selected raster from the rasterCollectionListWidget
        """
        items = self.ui.rasterCollectionListWidget.selectedItems()
        for item in items:
            self.ui.rasterCollectionListWidget.takeItem(
                self.ui.rasterCollectionListWidget.row(item))

    @pyqtSlot()
    def on_setAsMaskToolButton_clicked(self):
        """
        Sets the selected raster as mask dataset, but only if the user unchecked maskRastercheckBox.
        """
        if not self.ui.maskRastercheckBox.isChecked():
            if len(self.ui.rasterCollectionListWidget.selectedItems()) > 0:
                newmask = self.ui.rasterCollectionListWidget.selectedItems()[0]
                self.ui.maskRasterLineEdit.setText(newmask.text())
            else:
                logging.info(self.tr("Please select a raster."))
        else:
            logging.info(self.tr("Can not change mask raster. Project default selected."))
            self.ui.maskRastercheckBox.setStyleSheet("background-color: rgb(255, 0, 0)")
            QTimer.singleShot(500, lambda: self.ui.maskRastercheckBox.setStyleSheet(""))

    @pyqtSlot()
    def on_maskRasterToolButton_clicked(self):
        """
        Calls CustomFileDialog to pick another mask Raster.
        """
        self.dialog.openRasterFile(self.projectlocation)
        if self.dialog.exec_() == 1 and self.dialog.selectedFiles():
            self.ui.maskRasterLineEdit.setText(os.path.normpath(self.dialog.selectedFiles()[0]))

    @pyqtSlot(bool)
    def on_maskRastercheckBox_clicked(self, signal: bool):
        """
        The checkbox safeguards changing the mask raster. By default it is checked but if it is
        unchecked the user can select another mask raster besides the project default.
        signal signifies if the checkbox is checked
        """
        self.ui.maskRasterLineEdit.setEnabled(not signal)
        self.ui.maskRasterToolButton.setEnabled(not signal)
        if signal:
            self.ui.maskRasterLineEdit.setText(self.maskpath)

    @pyqtSlot()
    def on_outputLocationToolButton_clicked(self):
        """
        Changes outputLocationLineEdit and as such the the output location of the imported files.
        """
        self.dialog.openDirectory(self.projectlocation)
        if self.dialog.exec_() == 1 and self.dialog.selectedFiles():
            self.ui.outputLocationLineEdit.setText(os.path.normpath(self.dialog.selectedFiles()[0]))

    @pyqtSlot()
    def on_applyPushButton_clicked(self):
        """
        Starts the import after calling _checkInputs to check validity of the inputs.
        Calls a threaded function for import process.
        """
        inputs = self._checkandgetInputs()
        if inputs:
            self._importRastertuple(inputs)

    def _checkandgetInputs(self) -> tuple:
        """
        Checks if atleast one valid raster is imported, and if the mask and the output location
        are also valid. If all are valid we return their values in a tuple else False.
        """
        valid = True
        rasters = []
        for i in range(self.ui.rasterCollectionListWidget.count()):
            rasters.append(self.ui.rasterCollectionListWidget.item(i).text())
        if not rasters:
            logging.info(self.tr("Please add atleast one raster"))
            self.ui.addToolButton.setStyleSheet("background-color: rgb(255, 0, 0)")
            QTimer.singleShot(500, lambda: self.ui.addToolButton.setStyleSheet(""))
            valid = False
        else:
            for raster in rasters:
                if not os.path.isfile(raster):
                    logging.info(self.tr("Invalid raster {} in input.").format(raster))
                    valid = False
        mask = self.ui.maskRasterLineEdit.text()
        if not os.path.isfile(mask):
            logging.info(self.tr("Not a valid mask raster."))
            self.ui.maskRasterLineEdit.setStyleSheet("background-color: rgb(255, 0, 0)")
            QTimer.singleShot(500, lambda: self.ui.maskRasterLineEdit.setStyleSheet(""))
            valid = False
        outputdir = self.ui.outputLocationLineEdit.text()
        if not os.path.isdir(outputdir):
            logging.info(self.tr("Not a valid output location"))
            self.ui.outputLocationLineEdit.setStyleSheet("background-color: rgb(255, 0, 0)")
            QTimer.singleShot(500, lambda: self.ui.outputLocationLineEdit.setStyleSheet(""))
            valid = False
        if valid:
            return (rasters, mask, outputdir)
        else:
            return (False)

    def _importRastertuple(self, inputs: tuple):
        """
        Gets called by on_applyPushButton_clicked.
        Starts a new import thread for each raster.
        inputs[0] = List of rasterpaths to import.
        inputs[1] = String of path to maskraster.
        inputs[2] = String of output directory.
        """
        self.threadpool = QThreadPool()
        for i, raster in enumerate(inputs[0]):
            resamplingtypedialog = ReprojectionSettings(raster, inputs[1])
            resamplingtypedialog.show()
            if resamplingtypedialog.exec_():  # Finish Dialog before we continue
                resamplingtype = resamplingtypedialog.resamplingType
            else:  # User canceled the import
                logging.info(self.tr("{} import canceled.").format(raster))
                continue
            self.importraster = ImportRaster(raster, inputs[1], inputs[2], resamplingtype)
            self.importraster.infoSignal.connect(self.logfromthread)
            self.threadpool.start(self.importraster.rasterImport)

    def logfromthread(self, string):
        """
        Gets called by signal from Importthread to display a string in the Main Log.
        """
        logging.info(string)

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
