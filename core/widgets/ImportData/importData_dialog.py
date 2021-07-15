from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from core.libs.GDAL_Libs.Layers import Raster
from core.uis.Reprojection_ui.Reprojection_ui import Ui_ProjectionSettings
from core.widgets.RasterInfo.rasterInfo_main import RasterInfo


class ReprojectionSettings(QDialog):
    """
    Gets called when a function wants the user to define the resamplingytpe for
    importData_importRaster.py. Allows the user to pick the kind of reprojection he wants to use.
    """

    def __init__(self, rasterpath, maskpath, parent=None):
        super().__init__()
        self.ui = Ui_ProjectionSettings()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(':/icons/Icons/LoadRaster_bw.png'))
        rasterInfo = RasterInfo(rasterpath)
        self.ui.inputRasterInfoGroupBoxGridLayout.addWidget(rasterInfo)
        maskInfo = RasterInfo(maskpath)
        raster = Raster(rasterpath)
        mask = Raster(maskpath)
        self.ui.sourceEPSGLineEdit.setText(str(raster.epsg))
        self.ui.targetEPSGLineEdit.setText(str(mask.epsg))
        self.ui.srcCellsizeLineEdit.setText(str(raster.cellsize[0]))
        self.ui.targetCellsizeLineEdit.setText(str(mask.cellsize[0]))
        self.guessResamplingBasedOnType(raster)

    def guessResamplingBasedOnType(self, raster: object) -> None:
        """
        Guesses theresamplingtype based on the type of raster the user wants to import.
        Default is Nearest Neighbor which is fine for int/byte types.
        """
        if raster.dataType in ("Float32", "CFloat32", "Float64", "CFloat64"):
            self.ui.CUBICradioButton.setChecked(True)

    @pyqtSlot()
    def on_okPushButton_clicked(self):
        """
        Closes the window and defines a class value that can be used by the function that opened
        the dialog.
        """
        if self.ui.NEARESTradioButton.isChecked():
            self.resamplingType = "NEAREST"
        elif self.ui.CUBICradioButton.isChecked():
            self.resamplingType = "CUBIC"
        elif self.ui.BILINEARradioButton.isChecked():
            self.resamplingType = "BILINEAR"
        self.accept()  # Closes the Dialog
