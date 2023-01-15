# -*- coding: utf-8 -*-

from osgeo import gdal, ogr, osr, gdalconst
import os
import math
import numpy as np
import time
import logging
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
import os
import random

from core.libs.GDAL_Libs.Layers import Raster, Feature, RasterLayer
from core.libs.Management.LayerManagement import LayerManagement as LM
from core.libs.Analysis.Random_Sampling import RandomSampling
from core.libs.Analysis.BivariateSolver import WofE
from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog
from core.libs.Reporting.woe_report import woe_report
from core.uis.WofE_ui.WofeBatch_ui import Ui_wofeBatch
from core.widgets.WofE.advancedSettings_main import AdvancedSettings
from core.widgets.ParameterSelection.ParameterSelection_main import ParameterSelection
from core.widgets.RasterInfo.rasterInfo_main import RasterInfo
from core.widgets.ResultViewer.resultViewerWofE_main import ResultViewerWofE


class WofETool(QMainWindow):
    signalFilled = pyqtSignal()

    def __init__(self, projectPath, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_wofeBatch()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(":/icons/Icons/cond_prob.png"))

        # Add icons to buttons
        self.ui.addDataToolButton.setIcon(QIcon(":icons/Icons/plus.png"))
        self.ui.removeDataToolButton.setIcon(QIcon(":icons/Icons/minus.png"))

        self.projectLocation = projectPath
        # analysis completed variable is set to true after the first analysis results are available
        self.analysisCompleted = None
        # tree widget containing the raster layers that should be analysed
        self.tree = self.ui.treeWidget
        self.tree.setStyleSheet("QHeaderView::section{background-color:#b7cbeb}")
        # Layer management class (abstract class) that manages the add and delete
        # functions in the tree widget
        self.LM = LM()
        self.fileDialog = CustomFileDialog()
        # advanced settings class
        self.advanced = AdvancedSettings(self.projectLocation)
        ##################### BASIC TOOLBAR ###############################
        # Toolbar contaning the basic actions: Settings and Properties
        self.toolbar = self.ui.toolBar

        self.ui.actionAdvanced_Settings.setIcon(QIcon(":/icons/Icons/Settings.png"))
        self.ui.actionAdvanced_Settings.triggered.connect(self.on_AdvancedSettings)

        self.actionSettings = QAction(
            QIcon(":/icons/Icons/Settings.png"),
            self.tr('Advanced Settings'),
            self)
        self.actionSettings.triggered.connect(self.on_AdvancedSettings)
        self.toolbar.addAction(self.actionSettings)

        self.actionProperties = QAction(
            QIcon(":/icons/Icons/Properties_bw.png"),
            self.tr('Properties'),
            self)
        self.actionProperties.triggered.connect(self.on_Properties)
        self.toolbar.addAction(self.actionProperties)

        self.actionShowResults = QAction(
            QIcon(":/icons/Icons/Chart_Bar_Big.png"),
            self.tr('Show results'),
            self)
        self.actionShowResults.triggered.connect(self.openResults)
        self.actionShowResults.setEnabled(False)
        self.toolbar.addAction(self.actionShowResults)

        self.actionCreateReport = QAction(
            QIcon(":/icons/Icons/WordReport.png"),
            self.tr('Create report (.docx)'),
            self)
        self.actionCreateReport.setEnabled(False)
        self.actionCreateReport.triggered.connect(self.createReport)
        self.toolbar.addAction(self.actionCreateReport)

        # Enable right click on raster to view information
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.open_contextmenu)

    def open_contextmenu(self, point):
        """
        Opens a right click context menu. The features are identical to the ones in the Toolbar.
        """
        index = self.tree.indexAt(point)
        # If the user did not click on an item we do nothing
        if not index.isValid():
            return
        item = self.ui.treeWidget.itemAt(point)

        # We build the menu.
        menu = QMenu()
        action_property = menu.addAction(
            QIcon(":/icons/Icons/Properties_bw.png"),
            self.tr("Properties"))
        action_property.triggered.connect(self.on_Properties)
        action_results = menu.addAction(
            QIcon(":/icons/Icons/Chart_Bar_Big.png"),
            self.tr("Show results"))
        action_results.triggered.connect(self.openResults)
        action_report = menu.addAction(
            QIcon(":/icons/Icons/WordReport.png"),
            self.tr("Create report (.docx)"))
        action_report.triggered.connect(self.createReport)
        # We only enable Results and Report when the calculation is finished
        action_results.setEnabled(self.actionShowResults.isEnabled())
        action_report.setEnabled(self.actionShowResults.isEnabled())
        menu.exec_(self.tree.mapToGlobal(point))

    def on_Properties(self):
        """
        Calls the analysis report widget.
        :param self: widget
        :return: None
        """
        if len(self.tree.selectedItems()) == 0:
            QMessageBox.warning(self, self.tr("Nothing selected!"), self.tr(
                "Select a dataset in the list below to view the properties!"))
            return
        for item in self.tree.selectedItems():
            dataSource = self.LM.treeContent[hash(str(item))]['Source']
        self.rasterInfo = RasterInfo(str(dataSource), parent=self)
        self.rasterInfo.show()

    def on_AdvancedSettings(self):
        """
        Opens the advanced settings prompt
        """
        self.advanced.show()

    def selectParameter(self):
        self.hide()
        self.paramSelection = ParameterSelection(self.projectLocation)
        self.paramSelection.show()
        self.paramSelection.apply_clicked.connect(self.fillData)

    @pyqtSlot()
    def on_addDataToolButton_clicked(self):
        """
        Adds a single raster layer to analyse to the tree content as item with progress bar.
        :param self:
        :return: None
        """
        self.fileDialog.openRasterFiles(self.projectLocation)
        if self.fileDialog.exec_() == 1:
            for filename in self.fileDialog.selectedFiles():
                self.layer = RasterLayer(str(filename))
                self.populateTreeWidget()

    @pyqtSlot(int)
    def on_appendCheckBox_stateChanged(self, state: int):
        self.ui.appendLineEdit.setEnabled(bool(state))

    def getAppend(self):
        """
        Gets called by _checkfornpz and on_applyPushButton_clicked
        Is used to append the outputname and mentions of it with the appendix given in lineEdit.
        """
        if self.ui.appendCheckBox.isChecked() and self.ui.appendLineEdit.text():
            return self.ui.appendLineEdit.text()
        return ""

    def populateTreeWidget(self):
        root = self.tree.invisibleRootItem()
        count = root.childCount()
        item = QTreeWidgetItem(self.tree)
        self.LM.addTreeContent(hash(str(item)), self.layer.properties)
        layerName = self.LM.treeContent[hash(str(item))]['Name']
        globals()[str(layerName) + '_progress'] = QProgressBar(self.tree)
        globals()[str(layerName) + '_progress'].setValue(0)
        item_text = self.layer.name
        item.setText(0, str(item_text))
        self.ui.treeWidget.setItemWidget(item, 1, globals()[str(layerName) + '_progress'])

    @pyqtSlot()
    def on_removeDataToolButton_clicked(self):
        """
        This method removes selected dataset from the dataset tree by click on the remove button.
        :param self
        :return: None
        """
        for item in self.tree.selectedItems():
            root = self.tree.invisibleRootItem()
            index = self.tree.currentIndex().row()
            treeItem = self.tree.topLevelItem(index)
            # remove from LM
            layerName = treeItem.text(0)
            self.LM.removeTreeItemByName(layerName)
            # remove from visibile treeWidget
            root.removeChild(treeItem)

    @pyqtSlot()
    def on_trainingFeatureToolButton_clicked(self):
        """
        Set the path of the landslide shapefile that should be used for training of the model.
        :param self
        :return: None
        """
        self.fileDialog.openFeatureFile(self.projectLocation)
        if self.fileDialog.exec_() == 1:
            for filename in self.fileDialog.selectedFiles():
                filename = os.path.normpath(filename)
                self.ui.trainingFeatureComboBox.insertItem(0, filename)
                self.ui.trainingFeatureComboBox.setCurrentIndex(
                    self.ui.trainingFeatureComboBox.findText(filename))

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
        self.selectedLayers = selectedLayers
        self.data_path = os.path.join(self.projectLocation, "data")
        self.params_path = os.path.join(self.data_path, "params")
        self.inventory_path = os.path.join(self.data_path, "inventory")
        self.training_path = os.path.join(self.inventory_path, "training")

        # Check if the set project path has a valid project structure
        if os.path.exists(self.data_path):
            logging.info(self.tr("data path localized - {}").format(self.data_path))
        else:
            logging.error(self.tr("data path not found. - {} is missing.").format(self.data_path))
            return
        if os.path.exists(self.params_path):
            logging.info(self.tr("param folder localized - {}").format(self.params_path))
        else:
            logging.error(
                self.tr("param folder not found. - {} is missing.").format(self.params_path))
            return
        if os.path.exists(self.inventory_path):
            logging.info(self.tr("inventory folder localized - {}").format(self.inventory_path))
        else:
            logging.error(
                self.tr("inventory folder not found. {} is missing").format(
                    self.inventory_path))
            return
        if os.path.exists(self.training_path):
            logging.info(self.tr("training folder localized - {}").format(self.training_path))
        else:
            logging.error(
                self.tr("training folder not found. - {} is missing").format(self.training_path))
            return
        # iterate for all files in directory training_path and select all files
        # with extention ".shp". Add these files to the combobox.

        for file_name in os.listdir(str(self.training_path)):
            file_type = os.path.splitext(file_name)[1].lower()
            if file_type in [".shp", ".kml", ".geojson"]:
                self.ui.trainingFeatureComboBox.insertItem(
                    0, str(os.path.join(str(self.training_path), file_name)))

        # iterate for all files in directory params and select all files with extention ".tif". Add these files to the tree widget.
        # for param in os.listdir(str(self.params_path)):
        for param in self.selectedLayers:
            param_type = os.path.splitext(param)[1].lower()
            if param_type == ".tif":
                paramPath = os.path.join(str(self.params_path), param)
                self.layer = RasterLayer(paramPath)
                self.populateTreeWidget()
        self.signalFilled.emit()
        return

    def updateProgressBar(self, progress):
        """
        Updates progress bar value based on the signal received from analysis thread
        :param self: widget
        :param i: signal received from the analysis thread containing the value to set to the progress bar
        :return: None
        """
        globals()[str(progress[0]) + '_progress'].setValue(progress[1])

    def updateLogger(self, message):
        logging.info(str(message))

    def done(self):
        self.thread.quit()
        self.ui.applyPushButton.setEnabled(True)
        self.actionShowResults.setEnabled(True)
        self.actionCreateReport.setEnabled(True)
        logging.info(self.tr("Analysis completed!"))

    def openResults(self):
        """
        This method calls the result widget that visualize results for the selected tree item.
        :param self
        :return: None
        """
        if self.tree.selectedItems():
            npz, layerName = self._checkfornpz()
            if layerName:
                result = np.load(npz)
                self.results = ResultViewerWofE(self.projectLocation, npz, layerName, result)
                self.results.show()
            else:
                logging.warning(self.tr("{} does not exist. Can not show Results.").format(npz))
        else:
            logging.info(self.tr("Please select an item."))

    def createReport(self):
        """
        Calls woe_report to generate a Report for the selected raster.
        """
        if self.tree.selectedItems():
            npz, layerName = self._checkfornpz()
            if layerName:
                result = np.load(npz)
                woe_report(self.projectLocation, result, layerName)
            else:
                logging.warning(self.tr("{} does not exist. Can not create report.").format(npz))
        else:
            logging.info(self.tr("Please select an item."))

    def _checkfornpz(self):
        """
        Gets called by createReport and openResults. Checks if a .npz with information exists for
        the selected raster. If yes it returns the path and name, else tuple (False, False).
        """
        for item in self.tree.selectedItems():
            layerName = self.LM.treeContent[hash(str(item))]['Name'] + self.getAppend()
            pathtonpz = os.path.join(self.outputTableLocation, '{}_tab.npz'.format(layerName))
            if os.path.isfile(pathtonpz):
                return pathtonpz, layerName
            else:
                return pathtonpz, False

    @pyqtSlot()
    def on_applyPushButton_clicked(self):
        """
        This methods start the analysis by the click on the apply button.
        :return: None
        """

        # Check if the training feature combo box is not empty path and return a
        # message if path is not set
        if not os.path.isfile(self.ui.trainingFeatureComboBox.currentText()):
            QMessageBox.warning(self, self.tr("Inventory missing!"), self.tr(
                "Select the inventory dataset to be used as training data!"))
            return

        self.ui.applyPushButton.setEnabled(False)
        # Start the logging entry
        logging.info(self.tr("Starting analyis"))
        logging.info(self.tr("Check progress on progress bars"))

        # get the path variables for region raster from project structure
        self.maskPath = os.path.join(self.projectLocation, "region.tif")
        self.maskRaster = Raster(self.maskPath)

        # set the spatial reference of the project based on the spatial reference
        # of the region raster
        self.spatRefProject = osr.SpatialReference()
        self.spatRefProject.ImportFromEPSG(int(self.maskRaster.epsg))

        # get the feature path from GUI
        self.featurePath = str(self.ui.trainingFeatureComboBox.currentText())

        # set the output table location - here the analysis results will be dropped
        self.resultsPath = os.path.join(self.projectLocation, "results", "WoE")
        self.outputTableLocation = os.path.join(self.resultsPath, "tables")

        # if the output table location does not exist, a directory "tables" it
        # will be created in the project's result folder
        if not os.path.exists(self.outputTableLocation):
            os.makedirs(self.outputTableLocation)
        # set the workspace location in which the intermediate results will be dropped
        self.workspace = os.path.join(self.projectLocation, "workspace")
        # if the workspace location does not exists, a directory "workspace" will
        # be created in the root of the project
        if not os.path.exists(self.workspace):
            os.makedirs(self.workspace)

        # get sample size from advanced settings GUI
        self.sampleSize = self.advanced.ui.sampleSizeSlider.value()

        # get the rasterization method that should be used from advanced settings GUI
        self.rasterMethod = self.advanced.ui.rasterizeMethodComboBox.currentText()

        # Subsampling settings
        # get the on-the-fly subsampling properties from advanced settings GUI
        self.onTheFlySubsample = self.advanced.ui.onTheFlySubsamplingCheckBox.isChecked()

        # get the predefined subsample properties from advanced settings GUI
        self.predefinedSubsamples = self.advanced.ui.predefinedSubsamplingCheckBox.isChecked()

        # Set Paths for Training and test dataset
        name, ext = os.path.splitext(os.path.basename(
            self.ui.trainingFeatureComboBox.currentText()))
        if self.advanced.ui.trainingSampleNameLineEdit.text() == "":
            self.outTraining = os.path.join(self.workspace, name + "_training" + ext)
        else:
            self.outTraining = os.path.join(self.workspace,
                                            self.advanced.ui.trainingSampleNameLineEdit.text() + ext)
        if self.advanced.ui.testSampleNameLineEdit.text() == "":
            self.outTest = os.path.join(self.workspace, name + "_test" + ext)
        else:
            self.outTest = os.path.join(self.workspace,
                                        self.advanced.ui.testSampleNameLineEdit.text() + ext)

        # get the root from the tree widget
        self.root = self.tree.invisibleRootItem()

        # get the number of items in the tree widget (number of factors to analyse
        # in the batch mode)
        self.count = self.root.childCount()

        # create layer management instance
        self.LayerManager = self.LM
        self.subsamplesPath = None

        # Define file name appendix to hande over to thread.
        self.nameAppendix = self.getAppend()

        # set the analysis type and number of subsamples based on advanced settings
        randomseed = None # only needed for onTheFlySubsample
        if self.onTheFlySubsample:
            self.numberSubsamples = self.advanced.ui.numberResamplesSpinBox.value()
            # If the user only wants one subsample we analyse the complete feature
            if int(self.numberSubsamples) > 1:
                self.analysisType = 2
                if self.numberSubsamples == "" or None:
                    self.numberSubsamples = 1
                if self.advanced.ui.randomSeedLineEdit.text(): # only if not empty
                    randomseed = self.advanced.ui.randomSeedLineEdit.text()
            else:
                self.analysisType = 1
                self.numberSubsamples = 1

        if self.onTheFlySubsample == False and self.predefinedSubsamples == False:
            self.analysisType = 1
            self.numberSubsamples = 1

        if self.predefinedSubsamples:
            self.analysisType = 3

            # folder with subsamples
            self.subsamplesPath = self.advanced.ui.subsamplesLocationLineEdit.text()

            if os.path.exists(self.subsamplesPath):
                count = 0
                for datafile in os.listdir(self.subsamplesPath):
                    if os.path.splitext(datafile)[1].lower() in [".shp", ".kml", ".geojson"]:
                        count += 1
                    else:
                        pass

                self.numberSubsamples = count
            else:
                QtGui.QMessageBox.warning(
                    self,
                    self.tr("Input error!"),
                    self.tr("Subsampling location not found!"))
                return

        # ANALYSIS
        kwargs = (self.spatRefProject, self.LayerManager, self.featurePath, self.outTraining,
                  self.outTest, self.rasterMethod, self.analysisType, self.workspace,
                  self.outputTableLocation, self.sampleSize, self.numberSubsamples,
                  self.subsamplesPath, self.projectLocation, self.nameAppendix, randomseed)
        self.thread = QThread()
        self.worker = Worker(kwargs)
        self.worker.moveToThread(self.thread)
        self.worker.finishSignal.connect(self.done)
        self.worker.progressSignal.connect(self.updateProgressBar)
        self.worker.loggingInfoSignal.connect(self.updateLogger)
        if self.analysisType == 1:
            self.thread.started.connect(self.worker.crossValidation)
        elif self.analysisType == 2:
            self.thread.started.connect(self.worker.onTheFlySubsampling)
        elif self.analysisType == 3:
            self.thread.started.connect(self.worker.subsamplingWithPredefinedSamples)
        self.thread.start()


class Worker(QObject):
    finishSignal = QtCore.pyqtSignal()
    progressSignal = QtCore.pyqtSignal(list)
    loggingInfoSignal = QtCore.pyqtSignal(str)

    def __init__(self, kwargs):
        QObject.__init__(self)
        self.spatRefProject, self.LayerManager, self.featurePath, self.outTraining, \
            self.outTest, self.rasterMethod, self.analysisType, self.workspace,\
            self.outputTableLocation, self.sampleSize, self.numberSubsamples, \
            self.subsamplesPath, self.projectLocation, self.nameAppendix, self.randomseed = kwargs

    @pyqtSlot()
    def crossValidation(self):
        """
        Performs the analysis in the cross validation mode.
        The computation of the weight is done once for each factor based on the entire training inventory.
        :return: None
        """
        self.loggingInfoSignal.emit(self.tr("Start simple cross validation"))
        # iterate for items in the tree widget
        for key in self.LayerManager.treeContent.keys():
            # get the item name from from Layer Manager instance
            layerName = str(self.LayerManager.treeContent[key]['Name'])
            # get the corresponding raster path from Layer Manager instance
            rasterPath = str(self.LayerManager.treeContent[key]['Source'])
            # create a raster instance
            raster = Raster(str(rasterPath))
            feature = Feature(str(self.featurePath))
            # set the result table path - creates a numpy archive file in which the
            # results will be dropped
            self.resultTablePath = os.path.join(
                str(self.outputTableLocation), '%s_tab.npz' % str(layerName + self.nameAppendix))

            self.progressSignal.emit([str(layerName), 30])

            eventRasterPath = feature.rasterizeLayer(
                str(rasterPath), os.path.join(
                    self.workspace, "land_rast.tif"), self.rasterMethod)

            eventRaster = Raster(eventRasterPath)

            self.progressSignal.emit([str(layerName), 50])

            wofe = WofE(raster, eventRaster, "")
            self.progressSignal.emit([str(layerName), 80])

            tab = wofe.table
            auc = wofe.auc
            roc_x = wofe.roc_x
            roc_y = wofe.roc_y
            metadata = (
                self.workspace,
                self.outputTableLocation,
                self.sampleSize,
                self.analysisType,
                self.numberSubsamples)
            source = (rasterPath, self.featurePath)
            np.savez_compressed(
                self.resultTablePath,
                tab=tab,
                auc=auc,
                roc_x=roc_x,
                roc_y=roc_y,
                source=source,
                metadata=metadata)
            self._writeWeightRaster(self.projectLocation, self.resultTablePath, tab, raster)
            self.progressSignal.emit([str(layerName), 100])
            eventRaster = None
            eventRasterPath = None
            eventRaster = None
            raster = None
            feature = None
        self.finishSignal.emit()

    @pyqtSlot()
    def subsamplingWithPredefinedSamples(self):
        """
        Performs the analysis in the subsampling with predefines samples mode.
        The user have to provide a folder containing inventory samples generated beforehand.
        :return: None
        """
        for key in self.LayerManager.treeContent.keys():
            layerName = self.LayerManager.treeContent[key]['Name']

            # Raster Path and Properties
            rasterPath = self.LayerManager.treeContent[key]['Source']
            raster = Raster(rasterPath)

            # Set output table location
            self.resultTablePath = os.path.join(
                str(self.outputTableLocation), '%s_tab.npz' % str(layerName + self.nameAppendix))

            nodata = raster.nodata
            unique = np.unique(raster.getArrayFromBand())
            if nodata in unique.tolist():
                tableSize = len(unique) - 1
            else:
                tableSize = len(unique)

            resamplingTable = np.zeros(shape=(tableSize,), dtype=[('Class', 'i'),
                                                                  ('Landslides', 'i'),
                                                                  ('W_POS', 'f'),
                                                                  ('VAR_POS', 'f'),
                                                                  ('W_NEG', 'f'),
                                                                  ('VAR_NEG', 'f'),
                                                                  ('Variance', 'f'),
                                                                  ('Contrast', 'f'),
                                                                  ('Weight', 'f'),
                                                                  ('Posterior', 'f'),
                                                                  ('sPost', 'f'),
                                                                  ('Expected', 'i'),
                                                                  ('sExpec', 'i')])
            resLandslides = np.zeros(shape=((tableSize), int(self.numberSubsamples)))
            resWpos = np.zeros(shape=((tableSize), int(self.numberSubsamples)))
            resWneg = np.zeros(shape=((tableSize), int(self.numberSubsamples)))
            resContrast = np.zeros(shape=((tableSize), int(self.numberSubsamples)))
            resWeight = np.zeros(shape=((tableSize), int(self.numberSubsamples)))
            resPosterior = np.zeros(shape=((tableSize), int(self.numberSubsamples)))
            resExpected = np.zeros(shape=((tableSize), int(self.numberSubsamples)))

            x_auc = []
            y_auc = []
            auc = []

            barvalue = 0
            barvalue_fraction = float(100 / int(self.numberSubsamples))

            ithSubsample = 0
            for subsample in os.listdir(self.subsamplesPath):
                if os.path.splitext(subsample)[1].lower() in [".shp", ".kml", ".geojson"]:
                    self.featurePath = os.path.join(self.subsamplesPath, subsample)
                    outTest = self.outTest
                    outTraining = self.outTraining
                    RandomSampling(self.featurePath, outTraining, outTest, percent=100,
                                   srProject=self.spatRefProject)
                    trainingSample = Feature(outTraining)
                    eventRasterPath = trainingSample.rasterizeLayer(
                        str(rasterPath), os.path.join(
                            self.workspace, "land_rast.tif"), self.rasterMethod)

                    eventRaster = Raster(eventRasterPath)

                    wofe = WofE(raster, eventRaster, "")  # Weight Calculation
                    resLandslides[:, ithSubsample] = wofe.table['Landslides']
                    resWpos[:, ithSubsample] = wofe.table['W_POS']
                    resWneg[:, ithSubsample] = wofe.table['W_NEG']
                    resContrast[:, ithSubsample] = wofe.table['Contrast']
                    resWeight[:, ithSubsample] = wofe.table['Weight']
                    resPosterior[:, ithSubsample] = wofe.table['Posterior']
                    resExpected[:, ithSubsample] = wofe.table['Expected']

                    x_auc.append(wofe.roc_x)
                    y_auc.append(wofe.roc_y)
                    auc.append(wofe.auc)
                    trainingSample = None
                    eventRaster = None
                    eventRasterPath = None
                    sample = None
                    outTraining = None
                    outTest = None
                    ithSubsample += 1

                    barvalue += barvalue_fraction
                    self.progressSignal.emit([layerName, math.ceil(barvalue)])

                    for i in range(len(wofe.table)):
                        resamplingTable['Class'][i] = wofe.table['Class'][i]
                        resamplingTable['Landslides'][i] = np.mean(resLandslides[i, :])
                        resamplingTable['W_POS'][i] = np.mean(resWpos[i, :])
                        resamplingTable['W_NEG'][i] = np.mean(resWneg[i, :])
                        resamplingTable['Contrast'][i] = np.mean(resContrast[i, :])
                        resamplingTable['Weight'][i] = np.mean(resWeight[i, :])
                        resamplingTable['Posterior'][i] = np.mean(resPosterior[i, :])
                        resamplingTable['Expected'][i] = np.mean(resExpected[i, :])

                    for i in range(len(wofe.table)):
                        for j in range(int(self.numberSubsamples)):
                            resamplingTable['VAR_POS'][i] = 1.0 / (int(self.numberSubsamples) - 1) * (
                                resWpos[i][j] - np.mean(resWpos[i])) ** 2
                            resamplingTable['VAR_NEG'][i] = 1.0 / (int(self.numberSubsamples) - 1) * (
                                resWneg[i][j] - np.mean(resWneg[i])) ** 2
                            resamplingTable['Variance'][i] = 1.0 / (int(self.numberSubsamples) - 1) * (
                                resWeight[i][j] - np.mean(resWeight[i])) ** 2
                            resamplingTable['sPost'][i] = math.sqrt(
                                1.0 / (int(self.numberSubsamples) - 1) * (
                                    resPosterior[i][j] - np.mean(resPosterior[i])) ** 2)
                            resamplingTable['sExpec'][i] = math.sqrt(
                                1.0 / (int(self.numberSubsamples) - 1) * (
                                    resExpected[i][j] - np.mean(resExpected[i])) ** 2)

                    tab = resamplingTable
                    classPix = wofe.table['Class'][i]
                    landslides = resLandslides
                    w_pos = resWpos
                    w_neg = resWneg
                    contrast = resContrast
                    weight = resWeight

                    metadata = (
                        self.workspace,
                        self.outputTableLocation,
                        self.sampleSize,
                        self.analysisType,
                        self.numberSubsamples)
                    source = (rasterPath, self.featurePath)
                    auc = auc
                    roc_x = x_auc
                    roc_y = y_auc
                    np.savez_compressed(self.resultTablePath, tab=tab, landslides=landslides,
                                        w_pos=w_pos,
                                        w_neg=w_neg,
                                        contrast=contrast,
                                        weight=weight,
                                        source=source,
                                        metadata=metadata,
                                        auc=auc,
                                        roc_x=roc_x,
                                        roc_y=roc_y)
            self._writeWeightRaster(self.projectLocation, self.resultTablePath, tab, raster)
        self.finishSignal.emit()

    @pyqtSlot()
    def onTheFlySubsampling(self):
        """
        Performs the analysis in the on-the-fly subsampling mode.
        :return: None
        """
        for key in self.LayerManager.treeContent.keys():
            layerName = self.LayerManager.treeContent[key]['Name']
            # Raster Path and Properties
            rasterPath = self.LayerManager.treeContent[key]['Source']
            raster = Raster(rasterPath)
            # Set output location/ create if such folder does not exist
            self.resultTablePath = os.path.join(
                str(self.outputTableLocation), '%s_tab.npz' % str(layerName + self.nameAppendix))
            nodata = raster.nodata
            unique = np.unique(raster.getArrayFromBand())
            if nodata in unique.tolist():
                tableSize = len(unique) - 1
            else:
                tableSize = len(unique)
            resamplingTable = np.zeros(shape=(tableSize,), dtype=[('Class', 'i'),
                                                                  ('Landslides', 'i'),
                                                                  ('W_POS', 'f'),
                                                                  ('VAR_POS', 'f'),
                                                                  ('W_NEG', 'f'),
                                                                  ('VAR_NEG', 'f'),
                                                                  ('Variance', 'f'),
                                                                  ('Contrast', 'f'),
                                                                  ('Weight', 'f'),
                                                                  ('Posterior', 'f'),
                                                                  ('sPost', 'f'),
                                                                  ('Expected', 'i'),
                                                                  ('sExpec', 'i')])
            resLandslides = np.zeros(shape=((tableSize), int(self.numberSubsamples)))
            resWpos = np.zeros(shape=((tableSize), int(self.numberSubsamples)))
            resWneg = np.zeros(shape=((tableSize), int(self.numberSubsamples)))
            resContrast = np.zeros(shape=((tableSize), int(self.numberSubsamples)))
            resWeight = np.zeros(shape=((tableSize), int(self.numberSubsamples)))
            resPosterior = np.zeros(shape=((tableSize), int(self.numberSubsamples)))
            resExpected = np.zeros(shape=((tableSize), int(self.numberSubsamples)))

            x_auc = []
            y_auc = []
            auc = []

            barvalue = 0
            barvalue_fraction = float(100 / int(self.numberSubsamples))
            raster = None

            random.seed(self.randomseed)
            for i in range(int(self.numberSubsamples)):
                raster = Raster(rasterPath)
                outTest = self.outTest
                outTraining = self.outTraining
                RandomSampling(self.featurePath, outTraining, outTest, percent=self.sampleSize,
                               srProject=self.spatRefProject)

                trainingSample = Feature(outTraining)
                eventRasterPath = os.path.join(str(self.workspace), "land_rast.tif")
                if os.path.exists(eventRasterPath):
                    os.remove(eventRasterPath)
                trainingSample.rasterizeLayer(
                    rasterPath, str(eventRasterPath), str(
                        self.rasterMethod))
                eventRaster = Raster(str(eventRasterPath))

                wofe = WofE(raster, eventRaster, "")  # Calculation
                resLandslides[:, i] = wofe.table['Landslides']
                resWpos[:, i] = wofe.table['W_POS']
                resWneg[:, i] = wofe.table['W_NEG']
                resContrast[:, i] = wofe.table['Contrast']
                resWeight[:, i] = wofe.table['Weight']
                resPosterior[:, i] = wofe.table['Posterior']
                resExpected[:, i] = wofe.table['Expected']

                x_auc.append(wofe.roc_x)
                y_auc.append(wofe.roc_y)
                auc.append(wofe.auc)
                trainingSample = None
                eventRaster = None
                outTraining = None
                outTest = None
                del eventRaster
                barvalue += barvalue_fraction
                self.progressSignal.emit([layerName, math.ceil(barvalue)])

            for i in range(len(wofe.table)):
                resamplingTable['Class'][i] = wofe.table['Class'][i]
                resamplingTable['Landslides'][i] = np.mean(resLandslides[i, :])
                resamplingTable['W_POS'][i] = np.mean(resWpos[i, :])
                resamplingTable['W_NEG'][i] = np.mean(resWneg[i, :])
                resamplingTable['Contrast'][i] = np.mean(resContrast[i, :])
                resamplingTable['Weight'][i] = np.mean(resWeight[i, :])
                resamplingTable['Posterior'][i] = np.mean(resPosterior[i, :])
                resamplingTable['Expected'][i] = np.mean(resExpected[i, :])

            for i in range(len(wofe.table)):
                for j in range(int(self.numberSubsamples)):
                    resamplingTable['VAR_POS'][i] = 1.0 / (int(self.numberSubsamples) - 1) * (
                        resWpos[i][j] - np.mean(resWpos[i])) ** 2
                    resamplingTable['VAR_NEG'][i] = 1.0 / (int(self.numberSubsamples) - 1) * (
                        resWneg[i][j] - np.mean(resWneg[i])) ** 2
                    resamplingTable['Variance'][i] = 1.0 / (int(self.numberSubsamples) - 1) * (
                        resWeight[i][j] - np.mean(resWeight[i])) ** 2
                    resamplingTable['sPost'][i] = math.sqrt(
                        1.0 / (int(self.numberSubsamples) - 1) * (resPosterior[i][j] - np.mean(resPosterior[i])) ** 2)
                    resamplingTable['sExpec'][i] = math.sqrt(
                        1.0 / (int(self.numberSubsamples) - 1) * (resExpected[i][j] - np.mean(resExpected[i])) ** 2)

            tab = resamplingTable
            classPix = wofe.table['Class'][i]
            landslides = resLandslides
            w_pos = resWpos
            w_neg = resWneg
            contrast = resContrast
            weight = resWeight

            metadata = (
                self.workspace,
                self.outputTableLocation,
                self.sampleSize,
                self.analysisType,
                self.numberSubsamples,
                self.randomseed)
            source = (rasterPath, self.featurePath)
            auc = auc
            roc_x = x_auc
            roc_y = y_auc

            np.savez_compressed(self.resultTablePath, tab=tab, landslides=landslides,
                                w_pos=w_pos,
                                w_neg=w_neg,
                                contrast=contrast,
                                weight=weight,
                                source=source,
                                metadata=metadata,
                                auc=auc,
                                roc_x=roc_x,
                                roc_y=roc_y)
            self._writeWeightRaster(self.projectLocation, self.resultTablePath, tab, raster)
            raster = None
        self.finishSignal.emit()

    def _writeWeightRaster(
            self,
            projectLocation: str,
            npzpath: str,
            calcResults: object,
            rasterHandle: object) -> None:
        """
        Gets called by crossValidation, subsamplingWithPredefinedSamples and onTheFlySubsampling.
        Generates a raster with the calculated weights.
        """
        name = os.path.splitext(os.path.basename(npzpath))[0][:-4]  # remove '_tab'
        weightRasterPath = os.path.join(
            projectLocation,
            "results",
            "WoE",
            "rasters",
            name + "_woe.tif")
        weights = list(calcResults['Weight'])
        array = rasterHandle.getArrayFromBand()
        uniques = np.unique(array)
        raster_values = uniques[uniques != rasterHandle.nodata]
        driver = gdal.GetDriverByName("GTiff")
        weightRaster = driver.Create(
            weightRasterPath,
            rasterHandle.cols,
            rasterHandle.rows,
            1,
            gdal.GDT_Float32)
        weightRaster.SetProjection(rasterHandle.proj)
        weightRaster.SetGeoTransform(rasterHandle.geoTrans)
        weightRaster.GetRasterBand(1).SetNoDataValue(-9999.0)
        weightRasterArray = np.ones_like(array) * -9999.0
        for i, value in enumerate(raster_values):
            weightRasterArray[np.equal(array, value)] = weights[i]
        weightRaster.GetRasterBand(1).WriteArray(weightRasterArray)
        weightRaster.GetRasterBand(1).ComputeStatistics(False)
        self.loggingInfoSignal.emit(self.tr("Weight raster {} created.").format(weightRasterPath))
