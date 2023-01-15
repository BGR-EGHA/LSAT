# -*- coding: utf-8 -*-

from osgeo import gdal, osr
import os
import sys
import numpy as np
import configparser
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *
from core.uis.LogisticRegression_ui.LogisticRegression_ui import Ui_LogisticRegressionFrame
from core.libs.Management.LayerManagement import LayerManagement as LM
from core.libs.GDAL_Libs.Layers import Raster, Feature, RasterLayer
from core.libs.Analysis.LogisticRegressionAnalysis import LogisticRegressionAnalysis
from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog
from core.widgets.ParameterSelection.ParameterSelection_main import ParameterSelection
from core.widgets.LogisticRegression.logisticRegression_settings import Settings
from core.widgets.ResultViewer.resultViewerLogReg_main import ResultsForm as LogResultForm
import time
import logging
import traceback
from datetime import datetime


class LogRegression(QMainWindow):
    signalFilled = pyqtSignal()
    loggingInfoSignal = pyqtSignal(str)

    def __init__(self, project_path, parent=None):
        QMainWindow.__init__(self, parent)
        self.ui = Ui_LogisticRegressionFrame()
        self.ui.setupUi(self)

        self.parent = parent
        self.projectPath = project_path
        self.progressBar = self.ui.progressBar
        # tree widget containing the raster layers that should be analysed
        self.tree = self.ui.treeWidget
        self.tree.setStyleSheet("QHeaderView::section{background-color:#b7cbeb}")
        self.tree.header().setSectionResizeMode(QHeaderView.Stretch)
        # Layer management class (abstract class) that manages the add and delete
        # functions in the tree widget
        self.LM = LM()
        self.dialog = CustomFileDialog()
        self.settings = Settings()

        self.toolbar = self.ui.toolBar
        self.actionAdvancedSettings = QAction(
            QIcon(':/icons/Icons/Settings.png'),
            self.tr("Advanced Settings"),
            self)
        self.actionAdvancedSettings.triggered.connect(self.on_AdvancedSettings)
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

        # Add icons to buttons
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":icons/Icons/plus.png"), QIcon.Normal, QIcon.Off)
        self.ui.addToolButton.setIcon(icon1)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":icons/Icons/minus.png"), QIcon.Normal, QtGui.QIcon.Off)
        self.ui.removeToolButton.setIcon(icon2)

        self.maskRaster = Raster(os.path.join(self.projectPath, "region.tif"))
        self.workspacePath = os.path.join(self.projectPath, "workspace")
        self.resultsPath = os.path.join(self.projectPath, "results", "LR")
        self.tablesPath = os.path.join(self.resultsPath, "tables")

        self.filloutputlineedit()

        self.spatRefProject = osr.SpatialReference()
        self.spatRefProject.ImportFromEPSG(int(self.maskRaster.epsg))

    def filloutputlineedit(self):
        """
        Gets called by init to set a default output name. Default is LR if either
        \tables\\LR.npz or \rasters\\LR.tif exists it changes to LR1, LR2
        and so on.
        """
        name = "LR"
        raster = os.path.join(self.projectPath, "results", "LR", "rasters", name + "_lr.tif")
        table = os.path.join(self.projectPath, "results", "LR", "tables", name + "_lr.npz")
        nr = 0
        # If ANN.tif or ANN.npz already exists we need to change the output name
        while os.path.isfile(raster) or os.path.isfile(table):
            raster = os.path.join(self.projectPath, "results", "LR", "rasters",
                                  name + str(nr + 1) + "_lr.tif")
            table = os.path.join(self.projectPath, "results", "LR", "tables",
                                 name + str(nr + 1) + "_tab.npz")
            nr += 1
        # If no file exists we do not need a number, else we append it at the end
        if nr == 0:
            self.ui.outputlineEdit.setText(name)
        else:
            self.ui.outputlineEdit.setText(name + str(nr))

    def validateInputs(self):
        if self.tree.topLevelItemCount() == 0 or self.ui.landslideInventoryComboBox.currentText() == "":
            self.ui.applyPushButton.setEnabled(False)
        else:
            self.ui.applyPushButton.setEnabled(True)

    def selectParameter(self):
        self.hide()
        self.paramSelection = ParameterSelection(self.projectPath)
        self.paramSelection.show()
        self.paramSelection.apply_clicked.connect(self.fillData)

    def on_showResults(self):
        try:
            result = np.load(self.resultPath, allow_pickle=True)
            self.lrf = LogResultForm(self.resultPath, result)
            self.lrf.show()
        except:
            tb = traceback.format_exc()
            logging.error(tb)

    def on_createReport(self):
        pass

    def on_AdvancedSettings(self):
        self.settings.show()

    def fillData(self, selectedLayers):
        """
        This method is called whenever a new project directory was set.
        In the first step it checks the project structure for the training dataset that is usually located
        in the folder 'inventory/training' and set the training dataset path(s) in the combobox. If there are more
        that one dataset in the training location, the combobox will contain a list of all potential training
        datasets.
        In the second step it checks the project directory for the folder 'data' and populate the
        tree widget with the raster layers in the folder data.
        :param self
        :return: None
        """
        data_path = os.path.join(self.projectPath, "data")
        params_path = os.path.join(data_path, "params")
        inventory_path = os.path.join(data_path, "inventory")
        training_path = os.path.join(inventory_path, "training")

        # iterate for all files in directory training_path and select all files
        # with supported extensions. Add these files to the combobox.
        for file_name in os.listdir(training_path):
            file_type = os.path.splitext(file_name)[1].lower()
            if file_type in [".shp", ".kml", ".geojson"]:
                self.ui.landslideInventoryComboBox.insertItem(
                    0, str(os.path.join(str(training_path), file_name)))

        # iterate for all files in selected Layers and add to tree widget.
        for param in selectedLayers:
            self.populateTreeWidget(param)
        header = self.tree.header()
        for i in range(self.tree.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        header.setStretchLastSection(False)
        self.validateInputs()
        self.signalFilled.emit()

    @pyqtSlot()
    def on_landslideInventoryToolButton_clicked(self):
        """
        Set the path of the landslide faeture set that should be used for training of the model.
        :param self
        :return: None
        """
        self.dialog.openFeatureFile(self.projectPath)
        if self.dialog.exec_() == 1 and self.dialog.selectedFiles()[0]:
            self.ui.landslideInventoryComboBox.insertItem(0, str(self.dialog.selectedFiles()[0]))
            self.ui.landslideInventoryComboBox.setCurrentIndex(
                self.ui.landslideInventoryComboBox.findText(str(self.dialog.selectedFiles()[0])))
            self.validateInputs()
        else:
            self.validateInputs()

    @pyqtSlot()
    def on_addToolButton_clicked(self):
        """
        Adds raster layers to analyse to the tree content as item with progress bar.
        :param self:
        :return: None
        """
        self.dialog.openRasterFiles(self.projectPath)
        if self.dialog.exec_() == 1 and self.dialog.selectedFiles():
            for raster in self.dialog.selectedFiles():
                self.populateTreeWidget(raster)

    def populateTreeWidget(self, rasterFile):
        """
        Populates tree widget with the data from the project structure
        :param rasterFile: str, raster path
        :return: None
        """
        if rasterFile != "":
            self.layer = RasterLayer(str(rasterFile))
            root = self.tree.invisibleRootItem()
            count = root.childCount()

            item = QTreeWidgetItem(self.tree)
            layerName = str(self.layer.properties['Name'])
            self.LM.addTreeContent(hash(str(item)), self.layer.properties)
            item.setText(0, str(layerName))

            # create combo box for types
            globals()[str(layerName) + '_typeCombo'] = QComboBox(self.tree)
            globals()[str(layerName) + '_typeCombo'].addItems(["Continuous", "Discrete"])
            globals()[str(layerName) + '_typeCombo'].activated.connect(self.on_boxActivated)

            item_text = self.layer.name
            item.setText(0, str(item_text))

            self.ui.treeWidget.setItemWidget(item, 1, globals()[str(layerName) + '_typeCombo'])


            if "Float" in str(self.layer.type):
                globals()[str(layerName) + '_typeCombo'].setCurrentIndex(0)
            else:
                globals()[str(layerName) + '_typeCombo'].setCurrentIndex(1)


        self.validateInputs()

    @pyqtSlot(int)
    def on_boxActivated(self, item=None):
        """
        Manages action when a combobox was activated.
        :param item: QTreeWidgetItem
        :return: None
        """
        combo = self.sender()
        currentItem = self.tree.itemAt(combo.pos())
        currentItem.setSelected(True)
        self.tree.setCurrentItem(currentItem)

        if combo.currentText() == "Continuous":
            self.setEnabled(1)
        else:
            self.setEnabled(0)

    def setEnabled(self, enable):
        for item in self.tree.selectedItems():
            root = self.tree.invisibleRootItem()
            index = self.tree.currentIndex().row()
            treeItem = self.tree.topLevelItem(index)


    @pyqtSlot()
    def on_removeToolButton_clicked(self):
        """
        This method removes selected dataset from the dataset tree by click on the remove button.
        :param self
        :return: None
        """
        for item in self.tree.selectedItems():
            root = self.tree.invisibleRootItem()
            index = self.tree.currentIndex().row()
            treeItem = self.tree.topLevelItem(index)
            root.removeChild(treeItem)

    def getResultPath(self, sig):
        self.resultPath = sig

    @pyqtSlot()
    def on_applyPushButton_clicked(self):
        """
        Starts the analysis thread when apply button was clicked.
        :return: None
        """
        try:
            self.ui.applyPushButton.setEnabled(False)
            self.progressBar.setRange(0, 0)
            self.featurePath = str(self.ui.landslideInventoryComboBox.currentText())
            name = self.ui.outputlineEdit.text()
            self.data_list = []
            logging.info(self.tr("Start data preparation..."))
            self.root = self.tree.invisibleRootItem()
            for i in range(self.tree.topLevelItemCount()):
                item = self.root.child(i)
                rasterPath = self.LM.treeContent[hash(str(item))]['Source']
                typeBox = self.tree.itemWidget(item, 1)
                dataType = typeBox.currentText()

                layerName = self.LM.treeContent[hash(str(item))]['Name']

                locals()["dataset" + str(i)] = (rasterPath, dataType, layerName)
                self.data_list.append(locals()["dataset" + str(i)])
            settings = self.getArgsFromConfigFile()

            self.logisticRegAnalysis = LogisticRegressionAnalysis(
                self.projectPath, self.data_list, self.featurePath, self.tablesPath, name, settings)
            self.thread = QThread()
            self.logisticRegAnalysis.moveToThread(self.thread)
            self.logisticRegAnalysis.doneSignal.connect(self.done)

            self.logisticRegAnalysis.loggingInfoSignal.connect(self.updateLogger)
            self.logisticRegAnalysis.resultSignal.connect(self.getResultPath)
            self.thread.started.connect(self.logisticRegAnalysis.run)
            self.thread.start()
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)

    def updateLogger(self, message):
        logging.info(str(message))

    def getArgsFromConfigFile(self):
        """
        Reads the arguments from the config file
        :return: tuple args
        """
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join("core", "Widgets", "LogisticRegression", "configLogReg.ini"))
        penalty = str(self.config["USER_SETTINGS"]["penalty"])
        dual_str = self.config["USER_SETTINGS"]["dual"]
        if dual_str == "True":
            dual = True
        else:
            dual = False
        tol = float(self.config["USER_SETTINGS"]["tol"])
        c = float(self.config["USER_SETTINGS"]["c"])
        fit_intercept_str = str(self.config["USER_SETTINGS"]["fit_intercept"])
        if fit_intercept_str == "True":
            fit_intercept = True
        else:
            fit_intercept = False

        if self.config["USER_SETTINGS"]["class_weight"] == "None":
            class_weight = None
        else:
            class_weight = "balanced"
        intercept_scaling = float(self.config["USER_SETTINGS"]["intercept_scaling"])
        random_state = self.config["USER_SETTINGS"]["random_state"]
        if random_state == "None":
            random_state = None
        else:
            random_state = int(self.config["USER_SETTINGS"]["random_state"])
        solver = str(self.config["USER_SETTINGS"]["solver"])
        max_iter = int(self.config["USER_SETTINGS"]["max_iter"])
        multi_class = str(self.config["USER_SETTINGS"]["multi_class"])
        verbose = int(self.config["USER_SETTINGS"]["verbose"])
        warm_start_str = self.config["USER_SETTINGS"]["warm_start"]
        if warm_start_str == "True":
            warm_start = True
        else:
            warm_start = False
        n_jobs = self.config["USER_SETTINGS"]["n_jobs"]
        if n_jobs == "None":
            n_jobs = None
        else:
            n_jobs = int(n_jobs)
        l1_ratio = self.config["USER_SETTINGS"]["l1_ratio"]
        if l1_ratio == "None":
            l1_ratio = None
        else:
            l1_ratio = float(l1_ratio)

        return (
            penalty,
            dual,
            tol,
            c,
            fit_intercept,
            intercept_scaling,
            class_weight,
            random_state,
            solver,
            max_iter,
            multi_class,
            verbose,
            warm_start,
            n_jobs,
            l1_ratio)

    @pyqtSlot()
    def on_cancelPushButton_clicked(self):
        pass

    def done(self, sig):
        """
        This method is called when the thread emit a signal "done".
        It closes the logfile and updates the tree widget view.
        :param self
        :return: None
        """
        if sig == "error":
            self.ui.progressBar.setRange(0, 100)
            self.ui.progressBar.setValue(0)
            logging.info(self.tr("Analysis failed!"))      
        else:
            self.ui.progressBar.setRange(0, 100)
            self.ui.progressBar.setValue(100)
            logging.info(self.tr("Analysis complete!"))
        self.ui.applyPushButton.setEnabled(True)
        self.actionShowResults.setEnabled(True)
        self.actionCreateReport.setEnabled(True)
        self.thread.quit()
