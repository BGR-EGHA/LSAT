# -*- coding: utf-8 -*-

from osgeo import gdal
import sys
import os
import numpy as np

import xml.etree.ElementTree as ET
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import logging
import traceback
import webbrowser

from core.uis.LSAT_main_ui.mainFrame_ui import Ui_MainFrame
# Own Libraries
from core.libs.LSAT_Messages.messages_main import Messenger
from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog as FileDialog
from core.libs.Management import Project_configuration as config
from core.widgets.QRibbonToolbar.RibbonWidgetCollection import *
from core.widgets.ProjectManager.ProjectManagement_main import NewProject
from core.widgets.RasterAttributeTable.rat_main import RasterAttributeTable
from core.widgets.ImportInventory.importInventory_main import ImportInventory
from core.widgets.Subsampling.subsampling_main import Subsampling
from core.widgets.ImportData.importData_main import ImportRasterData
from core.widgets.LogisticRegression.logisticRegression_main import LogRegression
from core.widgets.ANN.ann_main import ann
from core.widgets.AHP.ahp_main import ahp
from core.widgets.AttributeTable.fat_main import FeatureAttributeTable
from core.widgets.DEM_Tools.DEM_Tools_main import CalculateSlope, TPI, TRI, Roughness, Aspect, Hillshade
from core.widgets.WofE.wofeBatch_main_thread import WofETool
from core.widgets.ModelBuilder.modelbuilder_main import ModelBuilder
from core.widgets.GeoViewer.BasicViewer_main import Viewer
from core.widgets.EuclideanDistance.euclideanDistance_main import EuclideanDistance
from core.widgets.Zoning.Zoning_main import Zoning
from core.widgets.Combine.combine_main import CombineGUI
from core.widgets.Reclassify.reclass_main import Reclass
from core.widgets.Contingency.contingency_main import ContingencyGUI
from core.widgets.ProjectInfo.projectInfo_main import ProjectInfo
from core.widgets.Settings.languageSettings_main import LanguageSettings
from core.widgets.SelectByAttributes.selectByAttributes_main import SelectByAttributes
from core.widgets.LookupRaster.lookupRaster_main import LookupRaster
from core.widgets.GeoprocessingTools.geoprocessingTools_main import GeoprocessingTools
from core.widgets.SensitivityReclass.SensReclass_main import SensitivityReclass
from core.widgets.Catalog.catalog_main import Catalog

gdal.AllRegister()


class MainFrame(QMainWindow):
    """
    This class is the main platform of the LSAT application.
    """
    signalViewer = pyqtSignal()

    def __init__(self, parent=None):
        """
        Initializes the UI of the application.
        :param parent: None
        """
        QWidget.__init__(self, parent)
        self.ui = Ui_MainFrame()
        self.ui.setupUi(self)

        # Set the window icon
        self.setWindowIcon(QIcon(':/icons/Icons/LSATLogo.png'))

        # SET IMPORTED core.widgets
        self.fileDialog = FileDialog()
        self.message = Messenger()
        self.config = config.Configuration()

        # Catalog
        self.catalog = Catalog()
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.catalog)

        # Main Log
        self.mainLog = LogForm()
        self.dockWidgetLog = QDockWidget(self.tr("Main Log"), self)
        self.dockWidgetLog.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.dockWidgetLog.setWidget(self.mainLog)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dockWidgetLog)

        # Set actions
        # set icons to menubar actions
        openProjectIcon = QtGui.QIcon(':/icons/Icons/open_project.png')
        self.ui.actionOpen_Project.setIcon(openProjectIcon)
        self.ui.actionOpen_Project.triggered.connect(self.on_open_project)

        newProjectIcon = QtGui.QIcon(':/icons/Icons/new_project.png')
        self.ui.actionNew_Project.setIcon(newProjectIcon)
        self.ui.actionNew_Project.triggered.connect(self.createNewProject)

        exitIcon = QtGui.QIcon(':/icons/Icons/backDoor.png')
        self.ui.actionExit.setIcon(exitIcon)
        self.ui.actionExit.triggered.connect(self.on_exit)

        # Set the ribbon toolbar
        self.ribbon = QRibbonWidget(self)
        self.addToolBar(self.ribbon)

        # ribbon PROJECT tab
        projectTab = self.ribbon.addRibbonTab(self.tr("PROJECT"))

        # Project Pane
        projectPane = projectTab.addRibbonPane(self.tr("Project"))
        self.newProject_action = self.add_action(
            self.tr("New Project"),
            QIcon(':/icons/Icons/new_project.png'),
            self.tr("New Project"),
            True,
            self.createNewProject,
            None)
        projectPane.addRibbonWidget(QRibbonButton(self, self.newProject_action))

        self.openProject_action = self.add_action(
            self.tr("Open Project"),
            QIcon(':/icons/Icons/open_project.png'),
            self.tr("Open Project"),
            True,
            self.on_open_project,
            None)
        projectPane.addRibbonWidget(QRibbonButton(self, self.openProject_action))

        self.info_action = self.add_action(
            self.tr("Project Info"),
            QIcon(':/icons/Icons/project_info.png'),
            self.tr("Info"),
            True,
            self.on_projectInfo,
            None)
        projectPane.addRibbonWidget(QRibbonButton(self, self.info_action))

        # View
        viewPane = projectTab.addRibbonPane(self.tr("View"), "Vertical")

        self.catalogCheckBox = QRibbonCheckBox(self, self.tr("Catalog"))
        viewPane.addRibbonWidget(self.catalogCheckBox, (0, 0, 1, 1))
        self.catalogCheckBox.setChecked(True)
        self.catalogCheckBox.stateChanged.connect(self.on_showCatalog)

        self.logCheckBox = QRibbonCheckBox(self, self.tr("Main Log"))
        viewPane.addRibbonWidget(self.logCheckBox, (1, 0, 1, 1))
        self.logCheckBox.setChecked(True)
        self.logCheckBox.stateChanged.connect(self.on_showLog)

        # Settings
        settingsPane = projectTab.addRibbonPane(self.tr("Settings"), "Vertical")
        self.language_action = self.add_action(
            self.tr("Language"),
            QIcon(':/icons/Icons/language.png'),
            self.tr("Language"),
            True,
            self.on_languageSettings,
            None)
        settingsPane.addRibbonWidget(QRibbonButton(
            self, self.language_action, "SmallButton"), (0, 0, 1, 1))

        # Help
        manualPane = projectTab.addRibbonPane(self.tr("Help"), "Horizontal")
        self.manual_action = self.add_action(self.tr("Manual"), QIcon(':/icons/Icons/Book.png'),
                                             self.tr("Manual"), True, self.on_manual, None)
        manualPane.addRibbonWidget(QRibbonButton(self, self.manual_action))

        # ribbon DATA tab
        dataTab = self.ribbon.addRibbonTab(self.tr("DATA"))

        # Import
        importPane = dataTab.addRibbonPane(self.tr("Import"), "Horizontal")

        self.importRasterData_action = self.add_action(self.tr("Import Raster"),
                                                       QIcon(':/icons/Icons/LoadRaster_bw.png'),
                                                       self.tr("Import raster"), True,
                                                       self.on_importRasterData, None)
        importPane.addRibbonWidget(QRibbonButton(self, self.importRasterData_action))

        self.importFeatureData_action = self.add_action(self.tr("Import Inventory"),
                                                        QIcon(':/icons/Icons/ImportFeature_bw.png'),
                                                        self.tr("Import feature"), True,
                                                        self.on_importFeatureData, None)
        importPane.addRibbonWidget(QRibbonButton(self, self.importFeatureData_action))

        # Preprocessing
        preprocessingPane = dataTab.addRibbonPane(self.tr("Vector Tools"), "Vertical")
        self.random_subset_action = self.add_action(self.tr("Random Sampling"),
                                                    QIcon(':/icons/Icons/random_subset.png'),
                                                    self.tr("Random Subset"),
                                                    True, self.on_random_sampling, None)
        preprocessingPane.addRibbonWidget(QRibbonButton(
            self, self.random_subset_action, "SmallButton"), (0, 0, 1, 1))

        self.temporal_subset_action = self.add_action(self.tr("Subset By Attributes"),
                                                      QIcon(':/icons/Icons/SelectByAttributes.png'),
                                                      self.tr("Subset By Attributes"), True,
                                                      self.on_selectByAttributes)
        preprocessingPane.addRibbonWidget(QRibbonButton(
            self, self.temporal_subset_action, "SmallButton"), (1, 0, 1, 1))

        self.geoprocessingTools_action = self.add_action(
            self.tr("Geoprocessing Tools"),
            QIcon(':/icons/Icons/GeoprocessingTools.png'),
            self.tr("Geoprocessing Tools"),
            True,
            self.on_geoprocessingTools,
            None)
        preprocessingPane.addRibbonWidget(QRibbonButton(
            self, self.geoprocessingTools_action, "SmallButton"), (2, 0, 1, 1))

        # DEM Tools
        demToolsPane = dataTab.addRibbonPane(self.tr("DEM Tools"), "Vertical")
        self.slope_action = self.add_action(self.tr("Slope"), QIcon(':/icons/Icons/Slope.png'),
                                            self.tr("Slope"), True, self.on_calcSlope, None)
        demToolsPane.addRibbonWidget(QRibbonButton(
            self, self.slope_action, "SmallButton"), (0, 0, 1, 1))

        self.aspect_action = self.add_action(
            self.tr("Aspect"),
            QIcon(':/icons/Icons/aspect.png'),
            self.tr("Aspect"),
            True,
            self.on_aspect,
            None)
        demToolsPane.addRibbonWidget(QRibbonButton(
            self, self.aspect_action, "SmallButton"), (1, 0, 1, 1))

        self.hillshade_action = self.add_action(
            self.tr("Hillshade"),
            QIcon(':/icons/Icons/hillshade.png'),
            self.tr("Hillshade"),
            True,
            self.on_hillshade,
            None)
        demToolsPane.addRibbonWidget(QRibbonButton(
            self, self.hillshade_action, "SmallButton"), (2, 0, 1, 1))

        self.tpi_action = self.add_action(
            self.tr("TPI"),
            QIcon(':/icons/Icons/tpi.png'),
            self.tr("Topographic Position Index"),
            True,
            self.on_tpi,
            None)
        demToolsPane.addRibbonWidget(QRibbonButton(
            self, self.tpi_action, "SmallButton"), (0, 1, 1, 1))

        self.roughness_action = self.add_action(
            self.tr("Roughness"),
            QIcon(':/icons/Icons/roughness.png'),
            self.tr("Roughness"),
            True,
            self.on_roughness,
            None)
        demToolsPane.addRibbonWidget(QRibbonButton(
            self, self.roughness_action, "SmallButton"), (1, 1, 1, 1))

        self.tri_action = self.add_action(
            self.tr("TRI"),
            QIcon(':/icons/Icons/TRI.png'),
            self.tr("Terrain Ruggedness Index"),
            True,
            self.on_tri,
            None)
        demToolsPane.addRibbonWidget(QRibbonButton(
            self, self.tri_action, "SmallButton"), (2, 1, 1, 1))

        # Spatial Tools
        spatialToolsPane = dataTab.addRibbonPane(self.tr("Raster Tools"), "Vertical")
        self.euclDist_action = self.add_action(self.tr("Euclidean distance"),
                                               QIcon(':/icons/Icons/EuclideanDist.png'),
                                               self.tr("Euclidean Distance"), True,
                                               self.on_euclideanDistance, None)
        spatialToolsPane.addRibbonWidget(QRibbonButton(
            self, self.euclDist_action, "SmallButton"), (0, 0, 1, 1))

        self.contingency_action = self.add_action(
            self.tr("Contingency Analysis"),
            QIcon(':/icons/Icons/Contingency_tab.png'),
            self.tr("Contingency"),
            True,
            self.on_contingency,
            None)
        spatialToolsPane.addRibbonWidget(QRibbonButton(
            self, self.contingency_action, "SmallButton"), (1, 0, 1, 1))

        self.combine_action = self.add_action(
            self.tr("Combine"),
            QIcon(':/icons/Icons/model.png'),
            self.tr("Combine"),
            True,
            self.on_combine,
            None)
        spatialToolsPane.addRibbonWidget(QRibbonButton(
            self, self.combine_action, "SmallButton"), (2, 0, 1, 1))

        self.reclassify_action = self.add_action(
            self.tr("Reclassify"),
            QIcon(':/icons/Icons/reclassify.png'),
            self.tr("Reclassify"),
            True,
            self.on_reclassify,
            None)
        spatialToolsPane.addRibbonWidget(QRibbonButton(
            self, self.reclassify_action, "SmallButton"), (0, 1, 1, 1))

        self.lookup_action = self.add_action(
            self.tr("Lookup"),
            QIcon(':/icons/Icons/lookup.png'),
            self.tr("Lookup raster"),
            True,
            self.on_lookup,
            None)
        spatialToolsPane.addRibbonWidget(QRibbonButton(
            self, self.lookup_action, "SmallButton"), (1, 1, 1, 1))

        self.sensreclass_action = self.add_action(
            self.tr("Sens Reclass"),
            QIcon(':/icons/Icons/SensitivityReclass.png'),
            self.tr("Sensitivity Reclassification"),
            True,
            self.on_sensreclass,
            None)
        spatialToolsPane.addRibbonWidget(QRibbonButton(
            self, self.sensreclass_action, "SmallButton"), (2, 1, 1, 1))

        # GEO VIEWER
        viewPane = dataTab.addRibbonPane(self.tr("Viewer"), "Horizontal")
        self.geoViewer_action = self.add_action(self.tr("Geodata Viewer"), QIcon(
            ':/icons/Icons/geoviewer.png'), self.tr("Viewer"), True, self.dataViewer, None)
        viewPane.addRibbonWidget(QRibbonButton(self, self.geoViewer_action))

        # ribbon Analysis tab
        analysisTab = self.ribbon.addRibbonTab(self.tr("ANALYSIS"))

        # Analysis
        analysisPane = analysisTab.addRibbonPane(self.tr("Analysis"), "Horizontal")
        self.wofe_action = self.add_action(self.tr("WofE"), QIcon(':/icons/Icons/cond_prob.png'),
                                           self.tr("Weight of Evidence"), True, self.on_wofe, None)
        analysisPane.addRibbonWidget(QRibbonButton(self, self.wofe_action))

        self.LR_action = self.add_action(
            self.tr("LR"),
            QIcon(':/icons/Icons/logisticReg.png'),
            self.tr("Logistic Regression"),
            True,
            self.on_logisticRegression,
            None)
        analysisPane.addRibbonWidget(QRibbonButton(self, self.LR_action))

        self.ANN_action = self.add_action(
            self.tr("ANN"),
            QIcon(':/icons/Icons/ann.png'),
            self.tr("Artificial Neural Network"),
            True,
            self.on_ann,
            None)
        analysisPane.addRibbonWidget(QRibbonButton(self, self.ANN_action))

        self.AHP_action = self.add_action(
            self.tr("AHP"),
            QIcon(':/icons/Icons/ahp.png'),
            self.tr("Analytical Hierarchy Process"),
            True,
            self.on_ahp,
            None)
        analysisPane.addRibbonWidget(QRibbonButton(self, self.AHP_action))

        # Model Managment
        analysisPane = analysisTab.addRibbonPane(self.tr("Model Management"), "Horizontal")
        self.modelbuilder_action = self.add_action(
            self.tr("Model Builder"),
            QIcon(':/icons/Icons/model_builder.png'),
            self.tr("Model Builder"),
            True,
            self.on_modelbuilder,
            None)
        analysisPane.addRibbonWidget(QRibbonButton(self, self.modelbuilder_action))

        self.zoning_action = self.add_action(
            self.tr("Zoning"),
            QIcon(':/icons/Icons/zoning.png'),
            self.tr("Zoning"),
            True,
            self.on_zoning,
            None)
        analysisPane.addRibbonWidget(QRibbonButton(self, self.zoning_action))

    def on_languageSettings(self):
        """
        Calls the language settings widget.
        :return: None
        """
        self.language = LanguageSettings()
        self.language.show()

    def on_manual(self):
        """
        Opens the documentation in a new browser tab.
        :return: None
        """
        path = os.path.abspath(os.path.join('docs', 'html', 'index.html'))
        webbrowser.open("file://" + path, new=2)

    def on_selectByAttributes(self):
        """
        Calls the Subset By Attributes Widget.
        :return: None
        """
        self.selection = SelectByAttributes(self.projectLocation)
        self.selection.show()

    def on_geoprocessingTools(self):
        """
        Calls the Geoprocessing Tools Widget
        :return: None
        """
        self.geoprocessing = GeoprocessingTools(self.projectLocation)
        self.geoprocessing.show()

    def on_lookup(self):
        self.lookup = LookupRaster(self.projectLocation)
        self.lookup.show()

    def on_sensreclass(self):
        self.sensreclass = SensitivityReclass(self.projectLocation)
        self.sensreclass.show()

    def on_exit(self):
        self.close()

    def dataViewer(self):
        try:
            if self.dockWidgetGeoviewer.isVisible() == False:
                self.dockWidgetGeoviewer = None
                self.dataViewer()
        except AttributeError:
            self.dockWidgetGeoviewer = QDockWidget(self.tr('GeoViewer'), self)
            self.geoviewer = Viewer(self.projectLocation)
            self.geoviewer.show()

    def on_showCatalog(self):
        """
        Controls the visibility of the catalog widget.
        Make catalog widget visible when not visible yet.
        :return: None
        """
        if self.catalogCheckBox.isChecked():
            self.catalog.show()
        elif self.catalogCheckBox.isChecked() == False:
            self.catalog.close()

    def on_showLog(self):
        """
        Controls the visibility of the main log widget.
        Make main log widget visible when not visible yet.
        :return: None
        """
        if self.logCheckBox.isChecked():
            self.dockWidgetLog.show()
        elif self.logCheckBox.isChecked() == False:
            self.dockWidgetLog.close()

    def add_action(self, caption, icon, status_tip, icon_visible, connection, shortcut=None):
        action = QAction(icon, caption, self)
        action.setStatusTip(status_tip)
        action.triggered.connect(connection)
        action.setIconVisibleInMenu(icon_visible)
        if shortcut is not None:
            action.setShortcuts(shortcut)
        self.addAction(action)
        return action

    def createNewProject(self):
        """
        This method calls the Project Creator Widget.
        :return: None
        """
        project = NewProject()
        if project.exec_() == 1:
            self.projectLocation = os.path.normpath(
                os.path.join(
                    project.ui.projectLocationLineEdit.text(),
                    project.ui.projectNameLineEdit.text()))
            pathMetadataFile = os.path.join(self.projectLocation, 'metadata.xml')

            if os.path.exists(pathMetadataFile):
                projectMetadata = ET.parse(os.path.join(self.projectLocation, 'metadata.xml'))
                root = projectMetadata.getroot()
                for ptype in root.iter('Type'):
                    self.projectType = ptype.attrib['analysis']
            else:
                self.message.ErrorLoadProject()
                return
            self.loadProjectStructure()
            return True
        else:
            return False

    def openProjectFromShortcut(self, path):
        self.projectLocation = os.path.normpath(path)
        try:
            self.loadProjectStructure()
            self.message.getLoggingInfoOnLoadingProject(self.projectLocation)
        except KeyError:
            return

    def on_open_project(self):
        """
        This method sets the catalogue view to the project structure specified as project.
        :param path: path to the project location
        :return: None
        """
        # If the function gets called from the start window self.projectLocation is not defined
        # and we start the dialog in the current working directory.
        try:
            self.projectLocation
            location = self.projectLocation
        except AttributeError:
            location = os.getcwd()
        self.fileDialog.openProject(location)
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
            projectLocation = self.fileDialog.selectedFiles()[0]
            # try:
            self.projectLocation = os.path.normpath(projectLocation)
            project = self.loadProjectStructure()
            if not project:
                return False
            else:
                self.message.getLoggingInfoOnLoadingProject(self.projectLocation)
                return True
            # except BaseException:
                # QMessageBox.warning(self, self.tr("Open project failed"), self.tr(
                    # "No selection or invalid project file selected!"))
                # return False
        else:
            return False

    def loadProjectStructure(self):
        """
        Gets called whenever we load a project in LSAT.
        Checks the Metadata file, closes opened widgets, updates the logging file if any and updates
        the window title.
        :return: Bool
        """
        pathMetadataFile = os.path.join(self.projectLocation, 'metadata.xml')
        self.updateFileLogger(self.projectLocation)
        configuration = config.Configuration()
        if os.path.exists(pathMetadataFile):
            projectMetadata = ET.parse(pathMetadataFile)

            projectlist = self.config.getProjects()
            new_list = []
            for elem in projectlist:
                if elem == str(self.projectLocation):
                    pass
                else:
                    new_list.append(elem)
            new_list.insert(0, self.projectLocation)
            self.config.updateProjectList(new_list)

            # Closes all windows opened in the last project.
            app = QApplication.instance()
            # Tuple of topLevelWidgets that are present for every project
            keepopen = ("menuFile",
                        "MainFrame",
                        "menuAbout",
                        "",
                        "menuHelp",
                        "menuSettings",
                        "QFileDialog",
                        "StartOptions")
            for w in app.topLevelWidgets():
                if w.objectName() not in keepopen:
                    w.close()

            projectName = os.path.basename(str(self.projectLocation))
            self.setWindowTitle(self.tr("LSAT Project Manager Suite - {}").format(projectName))
            self.catalog.setup(self.projectLocation)
            return True
        else:
            self.message.ErrorLoadProject()
            return False

    def updateFileLogger(self, projectLocation: str) -> None:
        """
        Gets called by loadProjectStructure.
        Updates the logger to write to the file in the project directory. If we opened a project
        before we stop writting to that file and clear the Log in the ui.
        """
        # remove old fileHandle
        for logger in logging.getLogger().handlers:
            if isinstance(logger, logging.FileHandler):
                logging.getLogger().removeHandler(logger)
        # add new one
        projectBasename = os.path.basename(projectLocation)
        pathLogFile = os.path.join(projectLocation, '{}.log'.format(projectBasename))
        fileLogger = logging.FileHandler(pathLogFile)
        fileLoggerFormatter = logging.Formatter("[%(levelname)s] %(asctime)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S")
        fileLogger.setFormatter(fileLoggerFormatter)
        logging.getLogger().addHandler(fileLogger)
        # clear Ui Logger
        self.mainLog.logTextBox.widget.clear()

    def on_open_file(self):
        pass

    def on_save(self):
        pass

    def on_importRasterData(self):
        """
        Calls import raster data widget.
        :return: None
        """
        try:
            self.ird = ImportRasterData(self.projectLocation, parent=self)
            self.ird.show()
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)

    def close_dockWidgetImportRaster(self):
        self.dockWidgetImportRaster.close()

    def on_logisticRegression(self):
        """
        Calls logistic regression widget.
        :return: None
        """
        self.logisticRegression = LogRegression(self.projectLocation, parent=self)
        self.logisticRegression.signalFilled.connect(self.showLogReg)
        self.logisticRegression.selectParameter()

    def on_ann(self):
        """
        Calls ANN widget.
        """
        try:
            self.ann = ann(self.projectLocation, parent=self)
            self.ann.selectParameter()
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)

    def on_ahp(self):
        """
        Calls AHP widget.
        """
        try:
            self.ahp = ahp(self.projectLocation, parent=self)
            self.ahp.selectParameter()
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)

    def on_wofe(self):
        self.wofe = WofETool(self.projectLocation)
        self.wofe.signalFilled.connect(self.showWofE)
        self.wofe.selectParameter()

    def showWofE(self):
        self.dockWidgetWofe = QDockWidget(self.tr('Weight of Evidence'), self)
        self.dockWidgetWofe.setWidget(self.wofe)
        self.dockWidgetWofe.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockWidgetWofe)

    def showLogReg(self):
        self.dockWidgetLogReg = QDockWidget(self.tr('Logistic Regression'), self)
        self.dockWidgetLogReg.setWidget(self.logisticRegression)
        self.dockWidgetLogReg.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockWidgetLogReg)

    def on_random_sampling(self):
        """
        Calls subsampling widget.
        :return: None
        """

        self.randomSampling = Subsampling(self.projectLocation, parent=self)
        self.randomSampling.show()

    def on_combine(self):
        """
        Calls Combine Widget.
        :return: None
        """
        self.combine = CombineGUI(self.projectLocation)
        self.combine.show()

    def on_importFeatureData(self):
        """
        Calls the inventory import widget and load it into dockable window.
        :return: None
        """
        try:
            self.importInv = ImportInventory(self.projectLocation)
            self.importInv.show()
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)

    def on_zoning(self):
        self.zoning = Zoning(projectLocation=self.projectLocation)
        self.zoning.show()

    def on_euclideanDistance(self):
        self.euclidDist = EuclideanDistance(self.projectLocation)
        self.euclidDist.show()

    def on_reclassify(self):
        self.reclass = Reclass(self.projectLocation)
        self.reclass.show()

    def on_projectInfo(self):
        self.projectInfo = ProjectInfo(self.projectLocation)
        self.projectInfo.show()

    def on_contingency(self):
        self.contingency = ContingencyGUI(self.projectLocation)
        self.contingency.show()

    def on_calcSlope(self):
        self.calcSlope = CalculateSlope(self.projectLocation)
        self.calcSlope.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.calcSlope.show()

    def on_tpi(self):
        self.tpi = TPI(self.projectLocation)
        self.tpi.show()

    def on_tri(self):
        self.tri = TRI(self.projectLocation)
        self.tri.show()

    def on_roughness(self):
        self.roughness = Roughness(self.projectLocation)
        self.roughness.show()

    def on_hillshade(self):
        self.hillshade = Hillshade(self.projectLocation)
        self.hillshade.show()

    def on_aspect(self):
        self.aspect = Aspect(self.projectLocation)
        self.aspect.show()

    def on_modelbuilder(self):
        self.modelbuilder = ModelBuilder(self.projectLocation)
        self.modelbuilder.show()

    def closeEvent(self, *args, **kwargs):
        QApplication.closeAllWindows()


class TreeView(QTreeView):
    """
    Used to set inital size of self.view in MainFrame
    """

    def sizeHint(self):
        return QtCore.QSize(700, 75)


class Thread(QThread):
    """
    Thread instance, called whenever a new process is started.
    """
    signal = QtCore.pyqtSignal()

    def __init__(self, function, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.function = function

        self.args = args
        self.kwargs = kwargs

    def __del__(self):
        self.wait()

    def run(self):
        """
        Runs the received function in the thread. Emits a done
        signal when ready.
        :return: None
        """
        self.function(*self.args, **self.kwargs)
        self.signal.emit()
        return


class QPlainTextEditLogger(logging.Handler):
    """
    This class is the logger object that records all emited
    signals and passes messages to the main log.
    """

    def __init__(self, parent):
        super(QPlainTextEditLogger, self).__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendHtml(msg)
        QApplication.processEvents()

class CustomFormatter(logging.Formatter):
    FORMATS = {
        logging.ERROR: ("[%(levelname)s] %(asctime)s %(message)s", QtGui.QColor("red")),
        logging.DEBUG: ("[%(levelname)s] %(asctime)s [%(filename)s:%(lineno)d] %(message)s", QtGui.QColor("green")),
        logging.INFO: ("[%(levelname)s] %(asctime)s %(message)s", QtGui.QColor("black")),
        logging.WARNING: ("[%(levelname)s] %(asctime)s %(message)s", QtGui.QColor(255, 136, 0))
    }

    def format(self, record):
        self.datefmt = "%Y-%m-%d %H:%M:%S"
        last_fmt = self._style._fmt
        opt = self.FORMATS.get(record.levelno)
        if opt:
            fmt, color = opt
            self._style._fmt = "<font color=\"{}\">{}</font>".format(
                QtGui.QColor(color).name(), fmt)
        res = logging.Formatter.format(self, record)
        self._style._fmt = last_fmt
        return res


class LogForm(QMainWindow):
    """
    The main logging class provides the ui for the logger.
    """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.gridLayoutWidget = QWidget(self)
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.logTextBox = QPlainTextEditLogger(self)
        self.gridLayout.addWidget(self.logTextBox.widget, 0, 0, 1, 1)

        self.logTextBox.setFormatter(CustomFormatter())
        logging.getLogger().addHandler(self.logTextBox)
        logging.getLogger().setLevel(logging.INFO) # TODO: Add config to change logging level
        self.setCentralWidget(self.gridLayoutWidget)
