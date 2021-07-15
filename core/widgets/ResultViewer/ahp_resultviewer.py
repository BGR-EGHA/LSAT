import math
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from core.libs.Reporting.ahp_report import ahp_report
from core.uis.ResultViewer_ui.tabbedResultViewerAHP_ui import Ui_tabbedResultViewerAHP
from core.widgets.ResultViewer.shared_resultviewer import shared_resultfunc


class ahp_resultviewer(QMainWindow):
    def __init__(self, projectlocation, filelocation, numpyfile):
        """
        numpyfile already is the handle.
        """
        super().__init__()
        # ui
        self.ui = Ui_tabbedResultViewerAHP()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(':/icons/Icons/Chart_Bar_Big.png'))
        self.setWindowTitle(self.tr("Results - {}").format(os.path.basename(filelocation)))
        self.loadModelData(numpyfile, os.path.basename(filelocation), filelocation)
        self.loadRasterData(numpyfile)
        self.nicerWidgets()

    def loadModelData(self, npfile, name, path):
        """
        Loads model statistics from the npz file into first tab with 3 subtabs.
        3 subtabs for the model:    General Information (self.ui.modelTreeWidget)
                                    Coefficient priorities (self.ui.coefficientPriosTableWidget)
                                    Pairwise raster comparison (self.ui.pairwiseRasterCompTableWidget)
        """
        self.ui.tabWidget.setTabText(0, name)
        self._fillGeneralInformation(npfile, path)
        self._fillCoefficientPrios(npfile)
        self._fillGenericValueComp(self.ui.pairwiseRasterCompTableWidget, npfile["rastercomp"][1],
                                   npfile["rastercomp"][0])

    def _fillGeneralInformation(self, npfile, path):
        # path to npz file
        shared_resultfunc.setTopLevelItem(
            self, 0, self.tr("File Path"), path, self.ui.modelTreeWidget)
        # general information
        shared_resultfunc.setTopLevelItem(self, 1, self.tr(
            "Model information"), None, self.ui.modelTreeWidget)
        shared_resultfunc.setChildItem(
            self,
            1,
            0,
            self.tr("Method to derive the priority vector"),
            ahp_report._get_methodname(
                self,
                npfile["prioritymethod"]),
            self.ui.modelTreeWidget)
        shared_resultfunc.setChildItem(
            self, 1, 1, self.tr("Transformation scale"), ahp_report._get_scalename(
                self, npfile["scale"]), self.ui.modelTreeWidget)
        shared_resultfunc.setChildItem(self, 1, 2, self.tr("Amount of rasters"), str(
            len(npfile["rastervaluescomp"])), self.ui.modelTreeWidget)

    def _fillCoefficientPrios(self, npfile):
        """
        First generates a row for each individual value of each raster and then fills the Table.
        """
        rowcount = 0
        for uniquevalues in npfile["uniquePerRaster"]:
            rowcount += len(uniquevalues[0])
        self.ui.coefficientPriosTableWidget.setRowCount(rowcount)
        p = 0
        for i, raster in enumerate(npfile["uniquePerRaster"]):
            self.ui.coefficientPriosTableWidget.setItem(
                p, 0, QTableWidgetItem(raster[1]))  # path to raster
            for j, uniquevalue in enumerate(raster[0]):  # unique value list
                self.ui.coefficientPriosTableWidget.setItem(
                    p, 1, QTableWidgetItem(str(uniquevalue)))
                self.ui.coefficientPriosTableWidget.setItem(
                    p, 2, QTableWidgetItem(str(npfile["coefficientpriorities"][i][0][j])))
                p += 1

    def _fillGenericValueComp(
            self,
            tableWidget: object,
            valuesobject: object,
            fillobject: object) -> None:
        """
        Gets called by loadRasterData and loadModelData
        Handles filling pairwise Raster, pairwise raster value and pairwise transformed raster
        value comparison.
        """
        values = [str(j) for j in valuesobject]
        for value in values:
            tableWidget.insertRow(0)
            tableWidget.insertColumn(0)
        tableWidget.setHorizontalHeaderLabels(values)
        tableWidget.setVerticalHeaderLabels(values)
        # to get a square shaped array we calculate the Root of the size of the array
        square_valuescomp = fillobject.reshape(int(math.sqrt(fillobject.size)), -1)
        for row in range(len(values)):
            for col in range(len(values)):
                tableWidget.setItem(row, col, QTableWidgetItem(str(square_valuescomp[row][col])))

    def loadRasterData(self, npfile: object) -> None:
        """
        Creates a new tab for each Raster containing 3 subtabs.
        Shows information for each analyzed raster file.
        """
        for i, raster in enumerate(npfile["rastervaluescomp"]):
            # formatting
            name = os.path.splitext(os.path.basename(raster[1]))[0]
            tab = QTabWidget()
            self.ui.tabWidget.addTab(tab, name)
            subtabnames = [self.tr("General Information"), self.tr("Raster value priorities"),
                           self.tr("Pairwise raster value comparison"),
                           self.tr("Pairwise transformed raster value comparison")]
            for j, subtabname in enumerate(subtabnames):
                widgetInTab = QWidget()
                tab.addTab(widgetInTab, subtabname)
                tabGridLayout = QGridLayout(widgetInTab)
                if j == 0:  # General Raster Information
                    widget = QTreeWidget()
                    widget.setColumnCount(2)
                    widget.headerItem().setText(0, self.tr("Info"))
                    widget.headerItem().setText(1, self.tr("Value"))
                    self._fillGeneralRasterInformation(widget, npfile, raster[1], i)
                elif j == 1:  # Raster value priorities
                    widget = QTreeWidget()
                    widget.setColumnCount(3)
                    widget.headerItem().setText(0, self.tr("Values"))
                    widget.headerItem().setText(1, self.tr("Priority vector"))
                    widget.headerItem().setText(2, self.tr("Coefficient Priorities"))
                    self._fillRasterValuePrios(widget, npfile, i)
                elif j == 2:  # Pairwise Raster value comparison
                    widget = QTableWidget()
                    self._fillGenericValueComp(widget, npfile["uniquePerRaster"][i][0],
                                               npfile["rastervaluescomp"][i][0])
                elif j == 3:  # Pairwise transformed Raster value comparison
                    widget = QTableWidget()
                    self._fillGenericValueComp(widget, npfile["uniquePerRaster"][i][0],
                                               npfile["transformedrastervaluescomp"][i][0])
                tabGridLayout.addWidget(widget)

    def _fillGeneralRasterInformation(
            self,
            widget: object,
            npfile: object,
            rasterpath: str,
            i: int) -> None:
        """
        Gets called by loadRasterData.
        Fills the first subtab with information that only exists once per Raster.
        """
        shared_resultfunc.setTopLevelItem(self, 0, self.tr("Raster information"), None, widget)
        shared_resultfunc.setChildItem(self, 0, 0, self.tr("Path to Raster"), rasterpath, widget)
        shared_resultfunc.setChildItem(
            self, 0, 1, self.tr("λ_max"), str(
                round(
                    float(
                        npfile["lambda_max_values"][i][0]), 3)), widget, str(
                npfile["lambda_max_values"][i][0]))
        shared_resultfunc.setChildItem(self, 0, 2, self.tr(
            "n"), str(len(npfile["uniquePerRaster"][i][0])), widget)
        shared_resultfunc.setChildItem(self, 0, 3, self.tr("Consistency Index"), str(
            round(float(npfile["CI"][i][0]), 3)), widget, npfile["CI"][i][0])
        shared_resultfunc.setChildItem(self, 0, 4, self.tr("Random Consistency Index"), str(
            round(float(npfile["RI"][i][0]), 3)), widget, npfile["RI"][i][0])
        shared_resultfunc.setChildItem(self, 0, 5, self.tr("Consistency Ratio (Saaty)"), str(
            round(float(npfile["CR_Saaty"][i][0]), 3)), widget, npfile["CR_Saaty"][i][0])
        shared_resultfunc.setChildItem(self, 0, 6, self.tr("Consistency Ratio (Alonso & Lamata)"), str(
            round(float(npfile["CR_AlonsoLamata"][i][0]), 3)), widget, npfile["CR_AlonsoLamata"][i][0])

    def _fillRasterValuePrios(self, widget: object, npfile: object, i: int) -> None:
        """
        Gets called by loadRasterData.
        Fills the TreeWidget in the second subtab with the (coefficient) priority of each raster
        value.
        """
        for j, value in enumerate(npfile["uniquePerRaster"][i][0]):
            widget.addTopLevelItem(QTreeWidgetItem(j))
            item = widget.topLevelItem(j)
            item.setText(0, str(value))
            item.setToolTip(0, str(value))
            item.setText(1, str(round(float(npfile["rastervaluepriorities"][i][0][j]), 3)))
            item.setToolTip(1, str(npfile["rastervaluepriorities"][i][0][j]))
            item.setText(2, str(round(float(npfile["coefficientpriorities"][i][0][j]), 3)))
            item.setToolTip(2, str(npfile["coefficientpriorities"][i][0][j]))

    def nicerWidgets(self) -> None:
        """
        Gets called by __init__.
        Modifies created Tree- and TableWidgets to fit LSAT Theme.
        """
        for widget in self.findChildren(QTableWidget):
            widget.horizontalHeader().setTextElideMode(Qt.ElideLeft)
            widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            widget.verticalHeader().setTextElideMode(Qt.ElideLeft)
            widget.verticalHeader().setDefaultAlignment(Qt.AlignRight)
            widget.verticalHeader().setMaximumWidth(500)
            widget.setStyleSheet("QHeaderView::section { background-color:#b7cbeb }")
        for widget in self.findChildren(QTreeWidget):
            widget.expandAll()
            widget.header().setSectionResizeMode(QHeaderView.ResizeToContents)
            widget.header().setStretchLastSection(False)
