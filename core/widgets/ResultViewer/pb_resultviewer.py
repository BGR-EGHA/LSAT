import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import matplotlib.pyplot as plt
from core.uis.ResultViewer_ui.tabbedResultViewer_ui import Ui_tabbedResultViewer
from core.widgets.ResultViewer.shared_resultviewer import shared_resultfunc, TableModel


class pb_resultviewer(QMainWindow):
    def __init__(self, projectlocation, filelocation, npfile):
        super().__init__()
        # ui
        self.ui = Ui_tabbedResultViewer()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(':/icons/Icons/Chart_Bar_Big.png'))
        self.setWindowTitle(self.tr("Results - {}").format(os.path.basename(filelocation)))
        self.loadModelData(npfile, os.path.basename(filelocation), filelocation)
        self.ui.modelTreeWidget.expandAll()
        self.ui.modelTreeWidget.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.modelTreeWidget.header().setStretchLastSection(False)

    def loadModelData(self, npfile, name, path):
        """
        """
        npfile = {key:npfile[key].item() for key in npfile}
        self.ui.tabWidget.setTabText(0, "General information")
        shared_resultfunc.setTopLevelItem(
            self, 0, self.tr("File Path"), path, self.ui.modelTreeWidget)
        shared_resultfunc.setTopLevelItem(
            self, 1, self.tr("Continuous dataset"), str(npfile["continuousInputPath"]), self.ui.modelTreeWidget)
        shared_resultfunc.setTopLevelItem(
            self, 2, self.tr("Discrete dataset"), str(npfile["discreteInputPath"]), self.ui.modelTreeWidget)
        shared_resultfunc.setChildItem(
            self, 2, 0, self.tr("Unique discrete values"), str(npfile["discreteInputsCount"]), self.ui.modelTreeWidget)
        shared_resultfunc.setChildItem(
            self, 2, 1, self.tr("Unique discrete values"), str([*npfile["pointBiserialResults"]]), self.ui.modelTreeWidget)

    def plotPointBiserial(true_list, false_list, true_mean, false_mean, cont_name) -> None:
        plt.ylabel(cont_name)
        ax.boxplot((true_list, false_list))
        ax.set_xticklabels((f"{discrete} \n Avg. {cont}: {round(true_mean, 4)}", f"{discrete} \n Avg. {cont}: {round(false_mean, 4)}"))
