from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import configparser
import logging
import numpy as np
import traceback
import os
import sys
from core.libs.Analysis.ann_calc import ann_calc
from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog
from core.uis.ANN_ui.ann_ui import Ui_ANN
from core.widgets.ANN.ann_advset import ann_advset
from core.widgets.ParameterSelection.ParameterSelection_main import ParameterSelection
from core.libs.GDAL_Libs.Layers import RasterLayer
from core.widgets.ResultViewer.ann_resultviewer import ann_resultviewer


class ann(QMainWindow):

    def __init__(self, project_path: str, parent=None):
        """
        Sets up the ui.
        Defines the following instanace variables:
        self.project_path = Absolute path to the project. (We will start all Filesearches there)
        self.pathNames = Dictionary connecting file name to path
        Called functions:
        self.fillinventorylineedit (Populate inventoryLineEdit with default training inventory)
        self.filloutputlineedit (Populate outputLineEdit with name based on previous calculations)
        """
        super().__init__()
        self.ui = Ui_ANN()
        self.ui.setupUi(self)
        self.progress = QProgressBar()
        self.statusBar().addPermanentWidget(self.progress)
        self.project_path = project_path
        self.pathNames = dict()
        # Connect imported Files
        ann.advanced = ann_advset()
        self.dialog = CustomFileDialog()

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        self.actionAdvancedSettings = QAction(
            QIcon(':/icons/Icons/Settings.png'),
            self.tr("Advanced Settings"),
            self)
        self.actionAdvancedSettings.triggered.connect(self.on_advset)
        self.toolbar.addAction(self.actionAdvancedSettings)

        self.actionShowResults = QAction(
            QIcon(':/icons/Icons/Chart_Bar_Big.png'),
            self.tr("Show Results"),
            self)
        self.actionShowResults.triggered.connect(self.on_showResults)
        self.actionShowResults.setEnabled(False)
        self.toolbar.addAction(self.actionShowResults)

        self.actionCreateReport = QAction(
            QIcon(':/icons/Icons/WordReport.png'),
            self.tr("Create Report"),
            self)
        self.actionCreateReport.triggered.connect(self.on_createReport)
        self.actionCreateReport.setEnabled(False)
        self.toolbar.addAction(self.actionCreateReport)

        # Create Headers and color them for the mainTable
        self.ui.mainTableWidget.setHorizontalHeaderLabels([self.tr("Parameter"), self.tr("Type")])
        self.ui.mainTableWidget.setTextElideMode(Qt.ElideLeft)
        self.ui.mainTableWidget.setWordWrap(False)
        self.ui.mainTableWidget.horizontalHeader().setTextElideMode(Qt.ElideLeft)
        # self.ui.mainTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.mainTableWidget.setStyleSheet("QHeaderView::section{background-color:#b7cbeb}")

        # Fill inventoryLineEdit and outputLineEdit with project defaults
        self.fillinventorylineedit(project_path)
        self.filloutputlineedit(project_path)

        # Add icons to buttons and Window
        self.setWindowIcon(QIcon(":/icons/Icons/ann.png"))
        self.ui.addrasterPushButton.setText("")
        self.ui.addrasterPushButton.setIcon(QIcon(":icons/Icons/plus.png"))
        self.ui.removerasterPushButton.setText("")
        self.ui.removerasterPushButton.setIcon(QIcon(":icons/Icons/minus.png"))

    def fillinventorylineedit(self, project_path: str) -> None:
        """
        Gets called by init to check if a training inventory exists in the default path.
        If it exists we fill the inventoryLineEdit with its absolute path.
        """
        extensions = [".shp", ".kml", ".geojson"]
        for ext in extensions:
            traininginv = os.path.join(project_path, "data", "inventory", "training",
                                       "inventory_training" + ext)
            if os.path.isfile(traininginv):
                self.ui.inventoryLineEdit.setText(traininginv)
                return

    def on_showResults(self):
        try:
            result = np.load(self.resultPath, allow_pickle=True)
            self.lrf = ann_resultviewer(self.project_path, self.resultPath, result)
            self.lrf.show()
        except:
            tb = traceback.format_exc()
            logging.error(tb)

    def getResultPath(self, sig):
        self.resultPath = sig

    def on_createReport(self):
        logging.info(self.tr("Support for ANN is coming soon."))

    def filloutputlineedit(self, project_path: str) -> None:
        """
        Gets called by init to set a default output name. Default is ANN if either
        \tables\\ANN.npz or \rasters\\ANN.tif exists it changes to ANN1, ANN2
        and so on.
        """
        name = "ANN"
        raster = os.path.join(project_path, "results", "ANN", "rasters", name + "_ann.tif")
        table = os.path.join(project_path, "results", "ANN", "tables", name + "_ann.npz")
        nr = 0
        # If ANN.tif or ANN.npz already exists we need to change the output name
        while os.path.isfile(raster) or os.path.isfile(table):
            raster = os.path.join(project_path, "results", "ANN", "rasters",
                                  name + str(nr + 1) + "_ann.tif")
            table = os.path.join(project_path, "results", "ANN", "tables",
                                 name + str(nr + 1) + "_tab.npz")
            nr += 1
        # If no file exists we do not need a number, else we append it at the end
        if nr == 0:
            self.ui.outputLineEdit.setText(name)
        else:
            self.ui.outputLineEdit.setText(name + str(nr))

    def selectParameter(self) -> None:
        """
        Gets called from MainFrame_main when the user starts ANN. First starts Paramter Selection
        allowing the user to pick whichever Rasters he wants to use in the calculation before
        starting the main ANN Widget after recieving a signal from Parameter Selection.
        """
        self.hide()
        self.paramSelection = ParameterSelection(self.project_path)
        self.paramSelection.show()
        self.paramSelection.apply_clicked.connect(self.addRasterList)

    def addRasterList(self, rasterlist: list) -> None:
        """
        Gets called by selectParameter and on_addrasterPushButton_clicked.
        Adds a new raster to the mainTable in a new row with three columns:
        1. Parameter name 2. Type (Continous/Discrete) 3. Sorting (Ascending/Descending)
        """
        for rasterPath in rasterlist:
            layer = RasterLayer(rasterPath)
            # gets the number of rows present and inserts a new one at the
            # end
            rasterFileName = os.path.splitext(os.path.basename(rasterPath))[0]
            if rasterFileName in self.pathNames:
                logging.info(
                    self.tr("{} is already part of the calculation").format(rasterFileName))
                continue
            self.pathNames[rasterFileName] = rasterPath
            rowposition = self.ui.mainTableWidget.rowCount()
            self.ui.mainTableWidget.insertRow(rowposition)

            qraster = QTableWidgetItem(rasterFileName)
            # writes the name of the raster in the first column
            self.ui.mainTableWidget.setItem(rowposition, 0, qraster)

            # used in the table to give each raster a type trough a
            # combobox
            rastertypes = ['Continuous', 'Discrete']
            # writes the type of raster in the second column with a
            # combobox
            comboxrastertype = QComboBox()
            comboxrastertype.addItems(rastertypes)
            comboxrastertype.setProperty('row', rowposition)
            comboxrastertype.setProperty('col', 1)
            if "Float" in layer.type:
                comboxrastertype.setCurrentIndex(0)
            else:
                comboxrastertype.setCurrentIndex(1)

            self.ui.mainTableWidget.setCellWidget(
                rowposition, 1, comboxrastertype)

            self.ui.mainTableWidget.horizontalHeader().setSectionResizeMode(
                0, QHeaderView.Stretch)  # Resizes table to fit given data after adding them
            self.ui.mainTableWidget.horizontalHeader().setSectionResizeMode(1,
                                                                            QHeaderView.ResizeToContents)

        if self.isHidden():  # Used to display ANN if started from Parameter Selection
            self.show()

    @pyqtSlot()
    def on_inventoryPushButton_clicked(self) -> None:
        """
        Opens Filepicker to choose an inventory. Changes text in inventoryLineEdit.
        """
        self.dialog.openFeatureFile(self.project_path)
        if self.dialog.exec_() == 1 and self.dialog.selectedFiles()[0]:
            self.ui.inventoryLineEdit.setText(self.dialog.selectedFiles()[0])

    @pyqtSlot()
    def on_addrasterPushButton_clicked(self) -> None:
        """
        Adds a new raster to the mainTable in a new row with three columns:
        1. Parameter name 2. Type (Continous/Discrete) 3. Sorting (Ascending/Descending)
        """
        self.dialog.openRasterFiles(self.project_path)
        if self.dialog.exec_() == 1 and self.dialog.selectedFiles():  # Only if atleast 1 Raster
            self.addRasterList(self.dialog.selectedFiles())


    @pyqtSlot()
    def on_removerasterPushButton_clicked(self):
        """
        Removes the last selected Raster from mainTable. If none is selected it
        removes starting from the last selected position.
        """
        selectedRow = self.ui.mainTableWidget.currentRow()
        del self.pathNames[self.ui.mainTableWidget.item(selectedRow, 0).text()]
        self.ui.mainTableWidget.removeRow(selectedRow)


    def on_advset(self):
        """
        Opens the Advanced Settings Window and forces it to stay on top
        """
        self.advanced.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.advanced.show()

    def getdata_list(self):
        """
        Returns a list generated from the values in the Ui Table. Returns the list.
        data_list[n]    = Raster in the n. row in mainTable (starts at 0)
        data_list[n][0] = Absolute path to raster
        data_list[n][1] = Type of raster (Continous/Discrete)
        data_list[n][2] = Sorting of raster values (Ascending/Descending)
        data_list[n][3] = Raster name without extension
        """
        data_list = []
        # Adds data to data_list. Iterating trough each row of the mainTableWidget
        for i in range(self.ui.mainTableWidget.rowCount()):
            rasterpath = self.pathNames[self.ui.mainTableWidget.item(i, 0).text()]
            rastertype = self.ui.mainTableWidget.cellWidget(i, 1).currentText()
            rastername = os.path.splitext(os.path.basename(
                self.ui.mainTableWidget.item(i, 0).text()))[0]
            # The contents of one row of the table get temporarily stored
            j = [rasterpath, rastertype, rastername]
            data_list.append(j)  # data_list is appended by the row
        return data_list

    def getsettings(self):
        """
        Returns the [USER_SETTINGS] from the .ini file for use in the calculation.
        """
        config = configparser.ConfigParser()
        config.read(os.path.join("core", "widgets", "ANN", "ann_config.ini"))
        h_l_svalue = config["USER_SETTINGS"]["hidden_layer_sizes"]
        h_l_svalue = tuple(map(int, h_l_svalue.split(' ')))
        activationvalue = config["USER_SETTINGS"]["activation"]
        solvervalue = config["USER_SETTINGS"]["solver"]
        alphavalue = float(config["USER_SETTINGS"]["alpha"])
        if config["USER_SETTINGS"]["batch_size"].lower() == "auto":
            batch_sizevalue = "auto"
        else:
            batch_sizevalue = config["USER_SETTINGS"]["batch_size"]
        learning_ratevalue = config["USER_SETTINGS"]["learning_rate"]
        learning_rate_initvalue = float(config["USER_SETTINGS"]["learning_rate_init"])
        power_tvalue = float(config["USER_SETTINGS"]["power_t"])
        max_itervalue = int(config["USER_SETTINGS"]["max_iter"])
        if config["USER_SETTINGS"]["shuffle"].lower() == "true":
            shufflevalue = True
        else:
            shufflevalue = False
        if config["USER_SETTINGS"]["random_state"] == "None":
            random_statevalue = None
        else:
            random_statevalue = int(config["USER_SETTINGS"]["random_state"])
        tolvalue = float(config["USER_SETTINGS"]["tol"])
        if config["USER_SETTINGS"]["verbose"].lower() == "true":
            verbosevalue = True
        else:
            verbosevalue = False
        if config["USER_SETTINGS"]["warm_start"].lower() == "true":
            warm_startvalue = True
        else:
            warm_startvalue = False
        momentumvalue = float(config["USER_SETTINGS"]["momentum"])
        if config["USER_SETTINGS"]["nesterovs_momentum"].lower() == "true":
            nesterovs_momentumvalue = True
        else:
            nesterovs_momentumvalue = False
        if config["USER_SETTINGS"]["early_stopping"].lower() == "true":
            early_stoppingvalue = True
        else:
            early_stoppingvalue = False
        validation_fractionvalue = float(config["USER_SETTINGS"]["validation_fraction"])
        beta_1value = float(config["USER_SETTINGS"]["beta_1"])
        beta_2value = float(config["USER_SETTINGS"]["beta_2"])
        epsilonvalue = float(config["USER_SETTINGS"]["epsilon"])
        n_iter_no_changevalue = int(config["USER_SETTINGS"]["n_iter_no_change"])
        max_funvalue = int(config["USER_SETTINGS"]["max_fun"])

        return [
            h_l_svalue,
            activationvalue,
            solvervalue,
            alphavalue,
            batch_sizevalue,
            learning_ratevalue,
            learning_rate_initvalue,
            power_tvalue,
            max_itervalue,
            shufflevalue,
            random_statevalue,
            tolvalue,
            verbosevalue,
            warm_startvalue,
            momentumvalue,
            nesterovs_momentumvalue,
            early_stoppingvalue,
            validation_fractionvalue,
            beta_1value,
            beta_2value,
            epsilonvalue,
            n_iter_no_changevalue,
            max_funvalue]

    @pyqtSlot()
    def on_applyPushButton_clicked(self):
        """
        Starts the calculation if an inventory, an outputname and atleast one Raster is given. Else
        it highlights the missing parameters. Before starting the the Analysis Thread it generates
        a list of raster to hand over to it by calling getdata_list() and gathers the settings from
        getsettings().
        """
        if (self.ui.outputLineEdit.text() and self.ui.mainTableWidget.rowCount() and
                os.path.isfile(self.ui.inventoryLineEdit.text())):
            self.ui.applyPushButton.setEnabled(False)
            self.actionShowResults.setEnabled(False)
            self.actionAdvancedSettings.setEnabled(False)
            self.actionCreateReport.setEnabled(False)
            featurePath = self.ui.inventoryLineEdit.text()
            name = self.ui.outputLineEdit.text()
            data_list = self.getdata_list()
            settings = self.getsettings()
            self.solver = ann_calc(self.project_path, data_list, featurePath, name, settings)
            self.thread = QThread()
            self.solver.moveToThread(self.thread)
            self.solver.loggingInfoSignal.connect(self.updateLogger)
            self.solver.loggingErrorSignal.connect(self.loggerError)
            self.solver.resultSignal.connect(self.getResultPath)
            self.thread.started.connect(self.solver.run)
            self.solver.finished.connect(self.updateui)
            # We set the Maximum to 0 to show an animation in the progressbar.
            self.progress.setMaximum(0)
            self.thread.start()
        else:
            # We flash missing infos red once to let the user know something is missing.
            if not os.path.isfile(self.ui.inventoryLineEdit.text()):
                self.ui.inventoryLineEdit.setStyleSheet("background-color: rgb(255, 0, 0)")
                QTimer.singleShot(500, lambda: self.ui.inventoryLineEdit.setStyleSheet(""))
            if self.ui.outputLineEdit.text() == (None or ""):
                self.ui.outputLineEdit.setStyleSheet("background-color: rgb(255, 0, 0)")
                QTimer.singleShot(500, lambda: self.ui.outputLineEdit.setStyleSheet(""))
            if self.ui.mainTableWidget.rowCount() < 1:
                self.ui.mainTableWidget.setStyleSheet("background-color: rgb(255, 0, 0)")
                QTimer.singleShot(500, lambda: self.ui.mainTableWidget.setStyleSheet(""))

    def updateui(self) -> None:
        """
        Gets called once the calculation thread finishes. Updates the Ui Elements.
        """
        # We set the Maximum to 1 to stop the animation in the progressbar.
        self.progress.setMaximum(1)
        self.thread.quit()
        self.ui.applyPushButton.setEnabled(True)
        self.actionShowResults.setEnabled(True)
        self.actionAdvancedSettings.setEnabled(True)
        self.actionCreateReport.setEnabled(True)

    def updateLogger(self, message):
        """
        Recieves signals from the Analysis Thread.
        """
        logging.info(str(message))

    def loggerError(self, message):
        """
        Recieves error signals from the Analysis Thread.
        """
        logging.error(str(message))
