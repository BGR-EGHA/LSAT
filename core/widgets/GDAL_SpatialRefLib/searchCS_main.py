# -*- coding: utf-8 -*-

from osgeo import gdal, osr
import csv
import os
import sys
import webbrowser

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import *
from core.uis.SetProjection_ui.search_cs_ui import Ui_SearchWindow


class MainForm(QMainWindow):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_SearchWindow()
        self.ui.setupUi(self)
        self.parent = parent
        self.csType = self.ui.csComboBox.currentText()
        self.ui.epsgCodeLineEdit.textChanged.connect(self.val_sizeValue)
        self.updateCSList()
        self.trial = 0

    def updateCSList(self):
        """
        Updates the Coordinate System List view (csListWidget) based on settings in the
        coordinate system combo box (csComboBox).
        :return: None
        """
        self.ui.csListWidget.clear()
        if str(self.ui.csComboBox.currentText()) == "GEOGRAPHIC":
            self.cs_lib_path = os.path.join("core", "gdal_data", "gcs.csv")
        else:
            self.cs_lib_path = os.path.join("core", "gdal_data", "pcs.csv")

        with open(self.cs_lib_path) as dbfile:
            reader = csv.DictReader(dbfile)
            self.epsg_liste = []
            self.names = []
            for row in reader:
                self.epsg_liste.append(str(row["COORD_REF_SYS_CODE"]))
                self.names.append(str(row["COORD_REF_SYS_NAME"]))

        for name in self.names:
            item = QListWidgetItem(name)
            self.ui.csListWidget.addItem(item)

    @pyqtSlot(int)
    def on_csComboBox_activated(self):
        """
        Calls the updateList function anytime when the coordinate system combo box is activated.
        :return: None
        """
        self.updateCSList()
        self.ui.csNameLineEdit.clear()
        self.ui.epsgCodeLineEdit.clear()
        self.ui.selectedCSLineEdit.clear()

    @pyqtSlot()
    def on_filterPushButton_clicked(self):
        """
        Calls the function updateListByName whenever the filterPushButton is clicked.
        :return: None
        """
        self.updateListByName()
        self.ui.csNameLineEdit.clear()
        self.ui.epsgCodeLineEdit.clear()
        self.ui.selectedCSLineEdit.clear()
        self.ui.wktTextEdit.clear()

    @pyqtSlot()
    def on_csNameLineEdit_returnPressed(self):
        """
        Calls the function updateListByName whenever the return button is pressed within csNameLineEdit.
        :return: None
        """
        self.updateListByName()
        self.ui.csNameLineEdit.clear()
        self.ui.epsgCodeLineEdit.clear()
        self.ui.selectedCSLineEdit.clear()
        self.ui.wktTextEdit.clear()

    def searchByEPSG(self):
        """
        Searches the coordinate system by given epsg code.
        :return: None
        """
        idx_csComboBox = self.ui.csComboBox.currentIndex()
        try:
            self.ui.wktTextEdit.clear()
            epsg = str(self.ui.epsgCodeLineEdit.text())
            idx = self.epsg_liste.index(epsg)
            name = self.names[idx].lower()
            for i in range(self.ui.csListWidget.count()):
                item = self.ui.csListWidget.item(i)
                if name == str(item.text()).lower():
                    item.setHidden(False)
                    item.setSelected(True)
                    self.ui.selectedCSLineEdit.setText(str(item.text()))
                else:
                    item.setHidden(True)
            sr = Projection(None, int(epsg))
            wkt = sr.prettyWkt
            self.ui.wktTextEdit.append(wkt)
        except BaseException:
            self.trial += 1
            if self.trial < 2:
                if idx_csComboBox == 0:
                    self.ui.csComboBox.setCurrentIndex(1)
                else:
                    self.ui.csComboBox.setCurrentIndex(0)
                self.updateCSList()
                self.searchByEPSG()
            else:
                self.trial = 0
                self.ui.csNameLineEdit.clear()
                self.ui.selectedCSLineEdit.clear()
                self.ui.wktTextEdit.clear()
                QMessageBox.warning(self, self.tr("EPSG Code error"), self.tr(
                    "EPSG Code not in the list! Please check if the EPSG code is valid!"))
                return

    @pyqtSlot()
    def on_csListWidget_itemSelectionChanged(self):
        """
        Updates the well known text field, epsgCOdeLineEdit value and name of the coordinate system
        whenever the selected item in the csListWidget has changed.
        :return: None
        """
        gdal.PushErrorHandler("CPLQuietErrorHandler")
        # Needed because gdal dislikes some epsg numbers and prints an Error 6 in the console.
        self.ui.wktTextEdit.clear()
        for item in self.ui.csListWidget.selectedItems():
            csName = str(item.text())
            self.ui.selectedCSLineEdit.setText(str(item.text()))
            idx = self.names.index(csName)
            epsg = self.epsg_liste[idx]
            self.ui.epsgCodeLineEdit.setText(str(epsg))
            sr = Projection(None, int(epsg))
            wkt = sr.prettyWkt
            self.ui.wktTextEdit.append(wkt)
        gdal.PushErrorHandler()
        # Normal Error Messages are resumed

    def updateListByName(self):
        """
        Updates/Filters the csListWidget by the name in the csNameLineEdit.
        :return: None
        """
        if str(self.ui.csNameLineEdit.text()).lower() == "":
            self.updateCSList()
        else:
            searchString = str(self.ui.csNameLineEdit.text()).lower()
            SplitsearchString = searchString.split()
            for i in range(self.ui.csListWidget.count()):
                item = self.ui.csListWidget.item(i)
                if all(Part in str(item.text()).lower() for Part in SplitsearchString):
                    item.setHidden(False)
                else:
                    item.setHidden(True)

    @pyqtSlot()
    def on_epsgCodeLineEdit_returnPressed(self):
        self.searchByEPSG()

    @pyqtSlot()
    def on_detailsPushButton_clicked(self):
        self.EPSG_details()

    @pyqtSlot()
    def on_applyPushButton_clicked(self):
        """
        Applies the settings from csWidget to the project GUI.
        :return: None
        """
        if self.ui.epsgCodeLineEdit.text() == "" or self.ui.selectedCSLineEdit.text() == "":
            QMessageBox.warning(self, self.tr("Nothing selected"), self.tr(
                "Please select one coordinate system from the list to proceed!"))
            return
        self.parent.setEPSG_From_Search(
            str(self.ui.epsgCodeLineEdit.text()), str(self.ui.selectedCSLineEdit.text()))
        self.close()

    def EPSG_details(self):
        """
        Opens the epsg website for corresponding coordinate system based on the epsg code
        :return: None
        """
        string = "https://epsg.io/%s" % (str(self.ui.epsgCodeLineEdit.text()))
        webbrowser.open(string)

    def filterList(self, searchString):
        filtList = [name for name in self.names if name.startswith(searchString)]
        return filtList

    def val_sizeValue(self, stringtocheck):
        """
        Gets called when the user edits epsgCodeLineEdit. Only numbers are allowed.
        """
        if not stringtocheck.isdigit() or stringtocheck == "":
            self.ui.epsgCodeLineEdit.backspace()


class Datum:
    def __init__(self, srs):
        self.srs = srs
        self.name = self.getDatumName()

    def getDatumName(self):
        name = self.srs.GetAttrValue("DATUM")
        return name


class Projection:
    def __init__(self, srs=None, epsg=None):
        if srs is not None:
            self.srs = srs
        else:
            self.srs = osr.SpatialReference()
        if epsg is not None:
            self.srs.ImportFromEPSG(epsg)

        self.wkt = self.srs.ExportToWkt()
        self.prettyWkt = self.srs.ExportToPrettyWkt()
        self.epsg = self.getEPSG()
        self.projName = self.getProjectionName()
        self.datum = self.getDatum()
        self.angularUnit = self.getAngularUnitsName()
        self.linearUnit = self.getLinearUnitsName()
        self.semiMajorAxis = self.getSemiMajorAxis()
        self.semiMinorAxis = self.getSemiMinorAxis()

    def getEPSG(self):
        """
        Returns EPSG Code of the Coordinate System (CS)
        :return: int epsg
        """
        epsg = self.srs.GetAuthorityCode("PROJCS")
        return epsg

    def getLinearUnitsName(self):
        """
        Returns the name of the linear unit of the CS.
        :return: string unitName
        """
        unitName = self.srs.GetLinearUnitsName()
        return unitName

    def getAngularUnitsName(self):
        """
        Returns the name of the angular unit of the CS.
        :return: string unitName
        """
        unitName = self.srs.GetAngularUnitsName()
        return unitName

    def getProjectionName(self):
        """
        Returns name of the CS projection.
        :return: string name
        """
        name = self.srs.GetAttrValue("PROJCS")
        return name

    def getGEOGCS(self):
        """
        Returns the name of the geographic coordinate system.
        :return: string geogCS
        """
        geogCS = self.srs.GetAttrValue("GEOGCS")
        return geogCS

    def getDatum(self):
        """
        Returns the datum of the CS.
        :return: string datum
        """
        datum = Datum(self.srs)
        return datum

    def getCentralMeridian(self):
        """
        Returns the central meridian value.
        :return: int cmeridian
        """
        cmeridian = self.srs.GetProjParm(osr.SRS_PP_CENTRAL_MERIDIAN)
        return cmeridian

    def getSemiMajorAxis(self):
        """
        Returns the value of the semimajor axis.
        :return: float semiMajor
        """
        semiMajor = self.srs.GetSemiMajor()
        return semiMajor

    def getSemiMinorAxis(self):
        """
        Returns the value of the semiminor axis.
        :return: float semiMinor
        """
        semiMinor = self.srs.GetSemiMinor()
        return semiMinor
