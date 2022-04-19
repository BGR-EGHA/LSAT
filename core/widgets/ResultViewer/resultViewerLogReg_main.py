import numpy as np
import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from core.libs.GDAL_Libs.Layers import Raster
from core.libs.Analysis.BivariateSolver import WofE
from core.uis.ResultViewer_ui.tabbedResultViewer_ui import Ui_tabbedResultViewer
from core.widgets.ResultViewer.shared_resultviewer import shared_resultfunc, TableModel


class ResultsForm(QMainWindow):
    def __init__(self, path, result, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_tabbedResultViewer()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(':/icons/Icons/Chart_Bar_Big.png'))
        name = os.path.basename(path)
        self.setWindowTitle(self.tr("Results - {}").format(name))
        self.tree = self.ui.modelTreeWidget
        self.LoadModelData(result, name, path)
        self.LoadRasterData(result)
        self.tree.expandAll()
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tree.header().setStretchLastSection(False)

    def LoadModelData(self, result, name, path):
        """
        Loads statistics of the final model from the npz file.
        """
        self.ui.tabWidget.setTabText(0, name)

        # set source path
        shared_resultfunc.setTopLevelItem(self, 0, self.tr("File Path"), path, self.tree)
        # set training dataset
        shared_resultfunc.setTopLevelItem(
            self, 1, self.tr("Training dataset"), str(
                result["training_data"]), self.tree)

        # set input data
        shared_resultfunc.setTopLevelItem(
            self, 2, self.tr("Explanatory variables"), None, self.tree)
        for i, value in enumerate(list(result["data_list"])):
            rastertype = value[1]
            shared_resultfunc.setChildItem(
                self, 2, i, rastertype, str(
                    list(
                        result["data_list"])[i][0]), self.tree)

        shared_resultfunc.setTopLevelItem(self, 3, self.tr("Model settings"), None, self.tree)
        info_settings = ("penalty", "dual", "tol", "c", "fit_intercept", "intercept_scaling",
                         "class_weight", "random_state", "solver", "max_iter",
                         "multi_class", "verbose", "warm_start", "n_jobs", "l1_ratio")
        for i, value in enumerate(list(result["settings"])):
            shared_resultfunc.setChildItem(self, 3, i, info_settings[i], str(value), self.tree)

        shared_resultfunc.setTopLevelItem(self, 4, self.tr("Model metrics"), None, self.tree)
        info = (self.tr("Intercept"), self.tr("AIC"), self.tr("BIC"), self.tr("AICc"), self.tr("AUC"))
        values = (result["intercept"][0], result["AIC"], result["BIC"], result["AICc"], result["auc"])
        for i, value in enumerate(values):
            shared_resultfunc.setChildItem(
                self, 4, i, info[i], "{:.5f}".format(value), self.tree, str(value))

    def LoadRasterData(self, result):
        """
        Loads statistics of individual rasters from the npz File.
        """
        for i, table in enumerate(result["Statistics"]):
            if i != 0:
                model = TableModel(table)
                tableView = shared_resultfunc.addTabToWidget(self, result["data_list"][i-1][2], self.ui.tabWidget)
                tableView.setModel(model)
                tableView.resizeColumnsToContents()
