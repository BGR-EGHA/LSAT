import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
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
    	pass