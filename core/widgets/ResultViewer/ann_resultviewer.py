import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from core.uis.ResultViewer_ui.tabbedResultViewer_ui import Ui_tabbedResultViewer
from core.widgets.ResultViewer.shared_resultviewer import shared_resultfunc, TableModel


class ann_resultviewer(QMainWindow):
    def __init__(self, projectlocation, filelocation, numpyfile):
        """
        numpyfile already is the handle.
        """
        super().__init__()
        # ui
        self.ui = Ui_tabbedResultViewer()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(':/icons/Icons/Chart_Bar_Big.png'))
        self.setWindowTitle(self.tr("Results - {}").format(os.path.basename(filelocation)))
        self.loadModelData(numpyfile, os.path.basename(filelocation), filelocation)
        self.ui.modelTreeWidget.expandAll()
        self.ui.modelTreeWidget.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.modelTreeWidget.header().setStretchLastSection(False)
        self.loadRasterData(numpyfile)

    def loadModelData(self, npfile, name, path):
        """
        Loads statistics of the resulting model from the npz file.
        """
        self.ui.tabWidget.setTabText(0, name)
        # path to npz file
        shared_resultfunc.setTopLevelItem(
            self, 0, self.tr("File Path"), path, self.ui.modelTreeWidget)
        # path to used feature file
        shared_resultfunc.setTopLevelItem(
            self, 1, self.tr("Training dataset"), str(
                npfile["featurePath"]), self.ui.modelTreeWidget)
        # amount of and paths to used rasters (data_list is best explained in rpw_main.py)
        shared_resultfunc.setTopLevelItem(self, 2, self.tr("Explanatory variables"), str(
            len(npfile["data_list"])), self.ui.modelTreeWidget)
        for i, raster in enumerate(npfile["data_list"]):
            rastertype = raster[1]
            shared_resultfunc.setChildItem(
                self, 2, i, rastertype, raster[0], self.ui.modelTreeWidget)
        # sklearn Settings
        shared_resultfunc.setTopLevelItem(self, 3, self.tr(
            "Model settings"), None, self.ui.modelTreeWidget)
        paras = ("hidden_layer_sizes", "activation", "solver", "alpha", "batch_size",
                 "learning_rate", "learning_rate_init", "power_t", "max_iter", "shuffle",
                 "random_state", "tol", "verbose", "warm_start", "momentum", "nesterovs_momentum",
                 "early_stopping", "validation_fraction", "beta_1", "beta_2", "epsilon",
                 "n_iter_no_change", "max_fun")
        for i, para in enumerate(paras):
            shared_resultfunc.setChildItem(self, 3, i, para, str(
                npfile["settings"][i]), self.ui.modelTreeWidget)
        # Model metrics
        shared_resultfunc.setTopLevelItem(self, 4, self.tr(
            "Model metrics"), None, self.ui.modelTreeWidget)
        shared_resultfunc.setChildItem(
            self, 4, 0, self.tr("AUC"), "{:.5f}".format(
                npfile["auc"]), self.ui.modelTreeWidget, str(
                npfile["auc"]))
        shared_resultfunc.setChildItem(
            self, 4, 1, self.tr("Score"), "{:.5f}".format(
                npfile["score"]), self.ui.modelTreeWidget, str(
                npfile["score"]))

    def loadRasterData(self, npfile):
        """
        Adds a new tab for each raster and adds information.
        """
        for i, table in enumerate(npfile["Statistics"]):
            if i != 0:
                model = TableModel(table)
                tableView = shared_resultfunc.addTabToWidget(self, npfile["data_list"][i - 1][2], self.ui.tabWidget)
                tableView.setModel(model)
                tableView.resizeColumnsToContents()
