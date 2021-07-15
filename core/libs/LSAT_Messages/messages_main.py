# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import sys
import os
import logging


class Messenger(QMainWindow):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setWindowIcon(QIcon(':/icons/Icons/News.png'))

    def AnalysisCompleted(self):
        QMessageBox.information(self, self.tr("Analysis completed!"),
                                self.tr("Analysis successfully completed!"))

    def WarningOverwriteFile(self):
        msg = QMessageBox.warning(self,
                                  self.tr(u"Specified path already exists!"),
                                  self.tr("The file will be overwritten"),
                                  QMessageBox.Ok | QMessageBox.Cancel)
        return msg

    def WarningMissingInput(self):
        QMessageBox.warning(self, self.tr("Missing input data!"),
                            self.tr("Please provide inputs to proceed!"))

    def WarningSelect(self):
        QMessageBox.warning(self, self.tr("No data selected"),
                            self.tr("Please select an item to proceed!"),
                            QtGui.QMessageBox.Ok)

    def InfoExportData(self, output):
        QMessageBox.information(self, self.tr("Data successfuly exported!"),
                                self.tr("Data has been exported to {}!").format(str(output)))

    def InformationConfigurationCompleted(self):
        QMessageBox.information(self, self.tr("Settings completed!"), self.tr(
            "The settings will be active after restart of the application!"))

    def ErrorDataLoad(self):
        QMessageBox.critical(self, self.tr("Failed to load data!"),
                             self.tr("Failed to open the dataset!"))

    def ErrorLoadProject(self):
        QMessageBox.critical(None, self.tr("Failed to load project!"),
                             self.tr("No metadata! No metadata file found in project directory!"))

    def WarningOnDeleteBasicFile(self):
        QMessageBox.warning(self, self.tr("Basic file alert!"),
                            self.tr("This file cannot be deleted!"))

    def WarningMissingInputs_Project(self):
        QMessageBox.warning(self, self.tr("No Project loaded!"),
                            self.tr("Please create or open an existing project to proceed!"))

    def InfoBoxAnalysisCompleted(self, output):
        QMessageBox.information(self, self.tr("Analysis completed!"),
                                self.tr("Output raster {} is created!".format(str(output))))

    def ErrorDeleteFile(self):
        QMessageBox.critical(self, self.tr("Failed to delete file!"), self.tr(
            "Failed to delete file! The file is probably used by another app. Otherwise check permission!"))

    def getLoggingInfo(self, info):
        logging.info(info)

    def getLoggingDebug(self, debug):
        logging.debug(debug)

    def getLoggingInfoProjectCreated(self, projectLocation):
        logging.info(self.tr("Session start. New Project in: {} created").format(projectLocation))

    def getLoggingInfoOnLoadingProject(self, projectLocation):
        logging.info(self.tr("Session start. Loaded Project: {}").format(projectLocation))

    def getLoggingInfoOnApplicationStart(self, action):
        app_name = action.text()
        logging.info(self.tr("{} launched! Waiting for input...").format(app_name))

    def getLoggingInfoOnAnalysisCompleted(self):
        logging.info(self.tr("Analysis completed!"))

    def getLoggingInfoOnUserCancelation(self):
        logging.info(self.tr("Analysis canceled by user!"))

    def getLoggingInfoDatasetRemoved(self, fileName):
        logging.info(self.tr("Dataset {} removed").format(fileName))

    def WarningMSOfficePackage(self):
        QMessageBox.warning(self, self.tr("Operation failed!"), self.tr(
            "Could not launch MS Office! Check if MS Office is installed on your PC."))

    def WarningDataReprojection(self):
        QMessageBox.warning(self, self.tr("Dataset does not match the project settings!"),
                            self.tr("Input data will be reprojected!"))

    def InfoCompletedDataImport(self):
        QMessageBox.information(self, self.tr("Successfully completed!"),
                                self.tr("All data sets have been imported!"))
