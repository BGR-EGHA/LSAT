from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
import logging
import traceback
import numpy as np
import subprocess
import sys
from core.libs.CustomFileDialog.CustomFileDialog import CustomIconProvider
from core.libs.LSAT_Messages.messages_main import Messenger
from core.widgets.AttributeTable.fat_main import FeatureAttributeTable
from core.widgets.FeatureInfo.featureInfo_main import FeatureInfo
from core.widgets.GeoViewer.BasicViewer_main import Viewer
from core.widgets.ModelInfo.modelinfo_main import ModelInfo
from core.widgets.RasterAttributeTable.rat_main import RasterAttributeTable
from core.widgets.RasterInfo.rasterInfo_main import RasterInfo
from core.widgets.ResultViewer.ann_resultviewer import ann_resultviewer
from core.widgets.ResultViewer.ahp_resultviewer import ahp_resultviewer
from core.widgets.ResultViewer.resultViewerWofE_main import ResultViewerWofE
from core.widgets.ResultViewer.resultViewerLogReg_main import ResultsForm as LogResultForm
from core.libs.Reporting.woe_report import woe_report
from core.libs.Reporting.ahp_report import ahp_report
from core.widgets.ResultViewer.resultViewerContingency_main import ContingencyMatrix


class Catalog(QDockWidget):
    """
    This class contains the catalog.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("Catalog"))
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.model = QFileSystemModel()
        self.view = TreeView()  # QTreeView with SizeHint
        self.view.setStyleSheet("QHeaderView::section { background-color:#b7cbeb }")
        self.view.header().setSectionResizeMode(3)
        self.setWidget(self.view)
        self.message = Messenger()

        # set custom context menu
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.contextMenuEvent)
        self.view.doubleClicked.connect(self.mouseDoubleClickEvent)

    def setup(self, projectLocation):
        """
        Gets called by MainFrame_main while loading a project.
        """
        filter = ['*.tif', '*.shp', '*.docx', '*.npz', '*.xlsx', '*.kml', '*.geojson']
        self.projectLocation = projectLocation
        self.model.setRootPath(projectLocation)
        self.model.setNameFilterDisables(0)
        self.model.setNameFilters(filter)
        iconProvider = CustomIconProvider()
        self.model.setIconProvider(iconProvider)
        self.view.setModel(self.model)
        self.view.setRootIndex(self.model.index(projectLocation))
        self.show()

    def contextMenuEvent(self, event):
        """
        Calls a context menu every time when this is requested via right button click
        in the field of layer content tree.
        :param event: mouse event
        :return: None
        """
        try:
            index = self.view.selectedIndexes()[0]
            fileInfo = self.model.fileInfo(index)
            fname = os.path.normpath(fileInfo.absoluteFilePath())
            ext = os.path.splitext(fname)[1].lower()
            menu = QMenu()
            if fileInfo.isDir():
                openExplorerAction = QAction(
                    QIcon(':/icons/Icons/Properties_bw.png'),
                    self.tr('Open Explorer here'),
                    None)
                menu.addAction(openExplorerAction)
                openExplorerAction.triggered.connect(self.openExplorer)
            else:
                actionDelete = QAction(QIcon(':/icons/Icons/Trashbox.png'), self.tr('Delete'), None)
                menu.addAction(actionDelete)
                actionDelete.triggered.connect(self.deleteFile)

                if ext in [".shp", ".kml", ".tif", ".geojson"]:
                    attributeTableAction = QAction(
                        QIcon(':/icons/Icons/AttributeTable.png'), self.tr('Attribute Table'), None)
                    menu.addAction(attributeTableAction)
                    attributeTableAction.triggered.connect(self.showAttributeTable)

                    if ext == '.tif':
                        viewDataAction = QAction(
                            QIcon(':/icons/Icons/geoviewer.png'), self.tr('View Data'), None)
                        menu.addAction(viewDataAction)
                        viewDataAction.triggered.connect(self.dataViewerFromContextMenu)

                        layerPropertiesAction = QAction(
                            QIcon(':/icons/Icons/Properties_bw.png'), self.tr('Properties'), None)
                        layerPropertiesAction.triggered.connect(self.showRasterInfo)
                        menu.addAction(layerPropertiesAction)

                    else:
                        layerPropertiesAction = QAction(
                            QIcon(':/icons/Icons/Properties_bw.png'), self.tr('Properties'), None)
                        layerPropertiesAction.triggered.connect(self.showFeatureInfo)
                        menu.addAction(layerPropertiesAction)

                if ext == ".docx":
                    openDocumentAction = QAction(
                        QIcon(':/icons/Icons/File_Doc_Text_Word.png'), self.tr('Open Document'), None)
                    menu.addAction(openDocumentAction)
                    self.docfilename = fname
                    openDocumentAction.triggered.connect(self.openWordDocument)

                if ext == ".xlsx":
                    openXlsxDocumentAction = QAction(
                        QIcon(':/icons/Icons/File_XLS_Excel.png'), self.tr('Open Excel Document'), None)
                    menu.addAction(openXlsxDocumentAction)
                    self.xlsxfilename = fname
                    openXlsxDocumentAction.triggered.connect(self.openExcelDocument)

                if os.path.basename(os.path.dirname(fname)) == "tables" and ext == ".npz":
                    createReportAction = QAction(
                        QIcon(':/icons/Icons/WordReport.png'),
                        self.tr('Create Analysis Report...'),
                        None)
                    menu.addAction(createReportAction)
                    self.resultFile = fname
                    createReportAction.triggered.connect(self.createReport)

                if os.path.basename(
                        os.path.dirname(fname)) == "susceptibility_maps" and ext == ".npz":
                    modelInfoAction = QAction(
                        QIcon(':/icons/Icons/model_info.png'), self.tr('Model Info'), None)
                    menu.addAction(modelInfoAction)
                    self.resultFile = fname
                    modelInfoAction.triggered.connect(self.showModelInfo)

                if (os.path.basename(os.path.dirname(fname)) == "tables" and ext == ".npz"):
                    showResultsAction = QAction(
                        QIcon(':/icons/Icons/Chart_Bar_Big.png'), self.tr('Show Results'), None)
                    menu.addAction(showResultsAction)
                    showResultsAction.triggered.connect(self.showResults)

                if (os.path.basename(os.path.dirname(fname)) == "statistics" and ext == ".npz"):
                    showResultsAction = QAction(
                        QIcon(':/icons/Icons/Chart_Bar_Big.png'), self.tr('Show Results'), None)
                    menu.addAction(showResultsAction)
                    showResultsAction.triggered.connect(self.showResults)

            menu.exec_(QCursor.pos())
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)

    def createReport(self):
        """
        Calls woe_report to generate a Report for the selected raster.
        """
        index = self.view.selectedIndexes()[0]
        fileInfo = self.model.fileInfo(index)
        fname = os.path.normpath(fileInfo.absoluteFilePath())
        pathparts = fname.split(os.sep)
        result = np.load(fname, allow_pickle=True)
        if pathparts[-3] == "WoE":  # The third to last part corresponds to the used Analysis type
            layerName = os.path.basename(fname[:-len("_tab.npz")])
            woe_report(self.projectLocation, result, layerName)
        elif pathparts[-3] == "AHP":
            ahp_report(os.path.basename(fname[:-len("_tab.npz")]), self.projectLocation, result)
        else:
            logging.info(self.tr("Support for {} is coming soon.").format(pathparts[-3]))

    def keyPressEvent(self, event):
        """
        Deletes the selected file and all corresponding files from the catalog view on 'Del' button ('Entf').
        :param event: key press event
        :return: None
        """
        if event.key() == Qt.Key_Delete:
            try:
                filePath = self.deleteFile()
                event.accept()
                QTreeView.keyPressEvent(self.view, event)
            except BaseException:
                tb = traceback.format_exc()
                logging.error(tb)

    def mouseDoubleClickEvent(self, index):
        """
        Opens *.docx and *.xlsx files on double-click on treeview item.
        :param index: QIndex
        :return: None
        """
        fileInfo = self.model.fileInfo(index)
        fname = os.path.normpath(fileInfo.absoluteFilePath())
        try:
            if os.path.splitext(fname)[1] in [".docx", ".xlsx"]:
                if sys.platform == "win32":
                    os.startfile(fname)
                else:  # ubuntu
                    subprocess.call(("xdg-open", fname))
            elif os.path.splitext(fname)[1] == ".npz":
                self.showResults()
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)

    def dataViewerFromContextMenu(self):
        """
        Calls the basic data viewer from the context menu
        on right mouse bottom click.
        :return: None
        """
        index = self.view.selectedIndexes()[0]
        fileInfo = self.model.fileInfo(index)
        fname = os.path.normpath(fileInfo.absoluteFilePath())
        v = Viewer(self.projectLocation, fname, parent=self)
        v.show()

    def deleteFile(self):
        """
        Delete a file and all corresponding files from the catalog view on
        Delete option of the context menu.
        :return:
        """
        index = self.view.selectedIndexes()[0]
        fileInfo = self.model.fileInfo(index)
        filePath = fileInfo.absoluteFilePath()
        fileName = os.path.basename(filePath)
        dirName = os.path.dirname(filePath)
        plainName = os.path.splitext(fileName)[0]
        fixedFilePath = os.path.join(self.projectLocation, 'region')
        # I'm sorry Dave, I'm afraid I can't do that.
        if filePath in (f"{fixedFilePath}.shp", f"{fixedFilePath}.tif"):
            self.message.WarningOnDeleteBasicFile()
            return
        try:
            for fname in os.listdir(dirName):
                if os.path.splitext(fname)[0] == plainName:
                    os.remove(os.path.join(dirName, fname))
                elif os.path.splitext(fname)[0] == f'{plainName}.tif.aux':
                    os.remove(os.path.join(dirName, fname))
                elif os.path.splitext(fname)[0] == f'{plainName}.tif.vat':
                    os.remove(os.path.join(dirName, fname))
                elif os.path.splitext(fname)[0] == f'{plainName}.shp.aux':
                    os.remove(os.path.join(dirName, fname))
                else:
                    pass
            self.model.remove(index)
            self.message.getLoggingInfoDatasetRemoved(os.path.normpath(filePath))
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)
            self.message.ErrorDeleteFile()

    def openExcelDocument(self):
        """
        Opens an Excel-document.
        :return: None
        """
        index = self.view.selectedIndexes()[0]
        fileInfo = self.model.fileInfo(index)
        fname = os.path.normpath(fileInfo.absoluteFilePath())
        try:
            if sys.platform == "win32":
                os.startfile(fname)
            else:  # ubuntu
                subprocess.call(("xdg-open", fname))
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)

    def openWordDocument(self):
        """
        Opens an Excel-document in Excel. Excel needs to be installed.
        :return: None
        """
        action = self.sender()
        index = self.view.selectedIndexes()[0]
        fileInfo = self.model.fileInfo(index)
        fname = os.path.normpath(fileInfo.absoluteFilePath())
        try:
            if sys.platform == "win32":
                os.startfile(fname)
            else:  # ubuntu
                subprocess.call(("xdg-open", fname))
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)

    def openExplorer(self):
        """
        Opens a new explorer window with the selected folder
        """
        index = self.view.selectedIndexes()[0]
        fileInfo = self.model.fileInfo(index)
        directory = fileInfo.absoluteFilePath()
        try:
            if sys.platform == "win32":
                os.startfile(directory)
            else:  # ubuntu
                subprocess.call(("xdg-open", directory))
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)

    def showAttributeTable(self):
        """
        Calls Attribute Table widget
        :return: Attribute Table object
        """
        index = self.view.selectedIndexes()[0]
        fileInfo = self.model.fileInfo(index)
        fname = os.path.normpath(fileInfo.absoluteFilePath())
        if os.path.splitext(fname)[1] == ".tif":
            self.rat = RasterAttributeTable(fname)
            if not self.rat.RAT_status:
                return
            else:
                self.rat.show()
        else:
            self.fat = FeatureAttributeTable(fname)
            self.fat.show()

    def showFeatureInfo(self):
        """
        Calls raster info widget for the selected raster dataset in the catalog.
        :return: None
        """
        index = self.view.selectedIndexes()[0]
        fileInfo = self.model.fileInfo(index)
        fname = os.path.normpath(fileInfo.absoluteFilePath())
        self.fi = FeatureInfo(fname, parent=self)
        self.fi.show()

    def showRasterInfo(self):
        """
        Calls raster info widget for the selected raster dataset in the catalog.
        :return: None
        """
        index = self.view.selectedIndexes()[0]
        fileInfo = self.model.fileInfo(index)
        fname = os.path.normpath(fileInfo.absoluteFilePath())
        self.ri = RasterInfo(fname, parent=self)
        self.ri.show()

    def showModelInfo(self):
        """
        Calls Model Info Widget for the selected npz.
        """
        index = self.view.selectedIndexes()[0]
        fileInfo = self.model.fileInfo(index)
        fname = os.path.normpath(fileInfo.absoluteFilePath())
        self.mi = ModelInfo(fname, parent=self)
        self.mi.show()

    def showResults(self):
        """
        Calls result widget to visualize the WofE result table and graphics
        :return: None
        """
        index = self.view.selectedIndexes()[0]
        fileInfo = self.model.fileInfo(index)
        fname = os.path.normpath(fileInfo.absoluteFilePath())
        pathparts = fname.split(os.sep)  # Split path to see where it was saved and open accordingly
        layerName = os.path.basename(fname)
        result = np.load(fname, allow_pickle=True)

        if pathparts[-3] == "WoE":  # The third to last part corresponds to the used Analysis type
            self.rvw = ResultViewerWofE(self.projectLocation, fname, layerName, result, parent=self)
            self.rvw.show()
        elif pathparts[-3] == "LR":
            self.lrf = LogResultForm(fname, result)
            self.lrf.show()
        elif pathparts[-3] == "ANN":
            self.annr = ann_resultviewer(self.projectLocation, fname, result)
            self.annr.show()
        elif pathparts[-3] == "AHP":
            self.ahpr = ahp_resultviewer(self.projectLocation, fname, result)
            self.ahpr.show()
        elif pathparts[-2] == "statistics":
            self.contr = ContingencyMatrix(self.projectLocation, fname, result)
            self.contr.show()
        else:
            logging.info(self.tr("Support for {} is coming soon.").format(pathparts[-3]))


class TreeView(QTreeView):
    """
    Used to set inital size of self.view in MainFrame
    """

    def sizeHint(self):
        return QSize(700, 75)
