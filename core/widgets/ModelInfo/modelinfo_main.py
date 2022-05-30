import numpy as np
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from core.uis.ModelInfo_ui.ModelInfo_ui import Ui_ModelInfo


class ModelInfo(QMainWindow):
    def __init__(self, filepath, parent=None):
        """
        The npz with the the information we feed the ui with gets generated in modelbuilder_calc.
        """
        super().__init__()
        model = np.load(filepath, allow_pickle=True)
        # ui
        self.ui = Ui_ModelInfo()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(":/icons/Icons/model_info.png"))
        self.setWindowTitle(self.tr("Model Info - {}").format(model["name"]))
        # Add information
        self.addinfo(model, filepath)
        self.ui.treeWidget.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.treeWidget.expandAll()
        self.ui.treeWidget.resizeColumnToContents(1)

    def addinfo(self, model, filepath):
        """
        Fills the ui with information about the model.
        """
        self.ui.treeWidget.topLevelItem(0).setText(1, filepath)  # Path to .npz
        self.ui.treeWidget.topLevelItem(1).setText(1, str(round(float(model["auc"]), 2)))  # AUC
        self.ui.treeWidget.topLevelItem(1).setToolTip(1, str(model["auc"]))
        self.ui.treeWidget.topLevelItem(2).setText(
            1, str(len(model["params"])))  # Number of rasters used
        for i in range(len(model["params"])):  # Paths to the used rasters
            tmp = QTreeWidgetItem()
            self.ui.treeWidget.topLevelItem(2).addChild(tmp)
            tmp.setText(1, model["params"][i])
        self.ui.treeWidget.topLevelItem(3).setText(
            1, str(model["expression"]))  # Model generating mathematic expression
        self.ui.treeWidget.topLevelItem(4).setText(
            1, str(len(model["unique_values"])))  # Unique values
        self.ui.treeWidget.topLevelItem(5).setText(
            1, str(model["analysistype"]))  # e.g. Subsampling type
        self.ui.treeWidget.topLevelItem(6).setText(1, self._getInputFeature(model))
        if model["randomseed"] != None: # only for on-the-fly subsampled models
            self.ui.treeWidget.topLevelItem(7).setText(1, str(model["randomseed"]))
        else:
            self.ui.treeWidget.takeTopLevelItem(7)

    def _getInputFeature(self, model) -> str:
        """
        Gets called by addinfo.
        If there is only one input feature we return its path, else we return the directory.
        """
        if str(model["analysistype"]) == "Predefined subsamples":  # multiple in dir
            feature = self.tr("{} predefined features in {}").format(
                str(model["samplecount"]), os.path.normpath(str(model["featurepath"])))
        elif str(model["analysistype"]) == "On-the-fly subsampling":  # multi from original
            feature = self.tr("{} subsampled from {}").format(
                str(model["samplecount"]), os.path.normpath(str(model["featurepath"])))
        elif str(model["analysistype"]) == "Single sample":
            feature = os.path.normpath(str(model["featurepath"]))
        return feature
