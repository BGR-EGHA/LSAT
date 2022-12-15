import docx
import folium
import json
import logging
import os
from osgeo import ogr
from osgeo import osr
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import random
import webbrowser
import xml.etree.ElementTree as ET
from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog
from core.libs.GDAL_Libs.Layers import Feature
from core.uis.ProjectInfo_ui.ProjectInfo_ui import Ui_ProjectInfo


class ProjectInfo(QMainWindow):
    def __init__(self, projectlocation, parent=None):
        super().__init__()
        # ui
        self.ui = Ui_ProjectInfo()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(":/icons/Icons/project_info.png"))
        self.ui.saveToolButton.setIcon(QIcon(':/icons/Icons/SaveEdits.png'))
        self.ui.loadToolButton.setIcon(QIcon(':/icons/Icons/plus.png'))
        self.ui.progress = QProgressBar()
        self.ui.progress.setTextVisible(False)
        self.ui.statusbar.addPermanentWidget(self.ui.progress)
        # class parameters
        self.dialog = CustomFileDialog()
        self.projectlocation = projectlocation
        # Qt Designer can't add Buttons to TreeWidgets
        self.ui.detailPushButton = QPushButton(self.tr("Details"))
        item = QTreeWidgetItem()
        self.ui.generalInfoTreeWidget.topLevelItem(1).addChild(item)
        self.ui.generalInfoTreeWidget.setItemWidget(item, 0, self.ui.detailPushButton)
        self.ui.detailPushButton.clicked.connect(self.on_detailPushButton_clicked)
        self.xml = ET.parse(os.path.join(self.projectlocation, "metadata.xml"))
        self.getMetadata(self.xml)
        self.ui.generalInfoTreeWidget.expandAll()
        self.ui.generalInfoTreeWidget.header().setSectionResizeMode(QHeaderView.ResizeToContents)

    def getMetadata(self, xml) -> None:
        """
        Gets called by init.
        Gathers information from the projects xml file and updates the ui.
        """
        for child in xml.getroot().iter():
            if child.tag == "Name":
                self.ui.generalInfoTreeWidget.topLevelItem(0).setText(1, child.attrib["name"])
            elif child.tag == "top":
                self.ui.generalInfoTreeWidget.topLevelItem(
                    2).child(0).setText(1, child.attrib["top"])
            elif child.tag == "left":
                self.ui.generalInfoTreeWidget.topLevelItem(
                    2).child(1).setText(1, child.attrib["left"])
            elif child.tag == "right":
                self.ui.generalInfoTreeWidget.topLevelItem(
                    2).child(2).setText(1, child.attrib["right"])
            elif child.tag == "bottom":
                self.ui.generalInfoTreeWidget.topLevelItem(
                    2).child(3).setText(1, child.attrib["bottom"])
            elif child.tag == "SpatialReference":
                self.ui.generalInfoTreeWidget.topLevelItem(
                    1).child(0).setText(1, child.attrib["epsg"])
            elif child.tag == "Projection":
                self.ui.generalInfoTreeWidget.topLevelItem(1).child(
                    1).setText(1, child.attrib["projection"])
            elif child.tag == "Area":
                self.ui.generalInfoTreeWidget.topLevelItem(
                    2).child(4).setText(1, child.attrib["area"])
            elif child.tag == "Cellsize":
                self.ui.generalInfoTreeWidget.topLevelItem(
                    3).child(0).setText(1, child.attrib["cellsize"])
                self.ui.generalInfoTreeWidget.topLevelItem(
                    3).child(1).setText(1, child.attrib["cellsize"])
            elif child.tag == "Description":
                self.ui.descriptionPlainTextEdit.setPlainText(child.attrib["descr"])

    def on_detailPushButton_clicked(self):
        """
        Gets called by clicking on the Details button in the TreeWidget.
        Opens the the EPSG Website for that EPSG in a new browser tab.
        """
        epsg = self.ui.generalInfoTreeWidget.topLevelItem(1).child(0).text(1)
        string = f"https://epsg.io/{epsg}"
        webbrowser.open(string, new=2)

    @pyqtSlot()
    def on_saveToolButton_clicked(self):
        """
        Allows the user to save his changes to the description in the projects xml file.
        """
        descr = self.ui.descriptionPlainTextEdit.toPlainText()
        for element in self.xml.getroot().iter("Description"):
            element.attrib["descr"] = descr
        path = os.path.join(self.projectlocation, "metadata.xml")
        self.xml.write(path, method="xml")
        logging.info(self.tr("Project description saved in {}").format(path))

    @pyqtSlot()
    def on_loadToolButton_clicked(self):
        """
        Allows the user to select a Word or Text file.
        Calls _loadText to add the text in the file to the descriptions.
        """
        self.dialog.openTextFile(self.projectlocation)
        if self.dialog.exec_() == 1 and self.dialog.selectedFiles():
            self._loadText(self.dialog.selectedFiles()[0])

    @pyqtSlot()
    def _loadText(self, file: str) -> None:
        """
        Replaces the descriptions in the ui with the contents of file
        """
        ext = os.path.splitext(file)[1].lower()
        if ext == ".txt":
            with open(file, encoding='utf-8') as doc:
                text = doc.read()
        elif ext == ".docx":
            doc = docx.Document(file)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
        self.ui.descriptionPlainTextEdit.setPlainText(text)

    @pyqtSlot()
    def on_viewInBrowserPushButton_clicked(self):
        """
        Calls generateMap to generate a folium based map and opens it in the default browser and
        updateProgress to update the progressbar.
        """
        self.updateProgress(True)
        mappath = self.generateMap()
        webbrowser.open("file://" + mappath, new=2)
        self.updateProgress(False)

    def updateProgress(self, switch: bool) -> None:
        """
        Gets called by on_viewinBrowserPushButton_clicked.
        Changes the progressbar to tell user something is going on.
        """
        if switch:
            self.ui.progress.setRange(0, 0)
        else:
            self.ui.progress.setRange(0, 1)

    def generateMap(self) -> str:
        """
        Gets called by on_viewInBrowserPushButton_clicked.
        Generates a html with the map.
        Returns a string with path to the html.
        Calls _delTmpGeoJSON to clean up files in workspace
        """
        features = self._getFeatures()  # list of paths to converted landslide geojsons
        region = self.convert2GeoJSON(os.path.join(self.projectlocation, "region.shp"))
        center = self._getCenter(region)
        foliummap = folium.Map(location=center)
        self.addFeature2Map(region, self.tr("Project area"), foliummap, "", "red")
        for feature in features:
            self.addFeature2Map(feature, feature, foliummap, "", "")
        folium.LayerControl().add_to(foliummap)
        projectname = self.ui.generalInfoTreeWidget.topLevelItem(0).text(1)
        outputpath = os.path.join(self.projectlocation, "workspace", projectname + ".html")
        foliummap.save(outputpath)
        self._delTmpGeoJSON(region, features)
        return outputpath

    def _getFeatures(self):
        """
        Gathers all landslide features found in the project and the region.shp and converts them to
        GeoJSON using convert2GeoJSON. Returns a list of strings to resulting files.
        """
        files = []
        for folder in ["training", "test"]:
            path = os.path.join(self.projectlocation, "data", "inventory", folder)
            for file in os.listdir(path):
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in [".shp", ".kml", ".geojson"]:  # .geojson need convertion to WGS84
                    newGeoJSON = self.convert2GeoJSON(os.path.join(path, file))
                    files.append(newGeoJSON)
        return files

    def convert2GeoJSON(self, inputpath: str) -> str:
        """
        Gets called by _getFeatures.
        Converts Featurefiles to GeoJSON for use in the folium map. Saves them under the same name
        in the workspace folder.
        """
        inputfeature = Feature(inputpath)
        name = os.path.splitext(os.path.split(inputpath)[1])[0]
        outputpath = os.path.join(self.projectlocation, "workspace", name + ".geojson")
        coordTrans = self._getCoordTrans(inputfeature, 4326)
        outputDriver = ogr.GetDriverByName("GeoJSON")
        outputDataSource = outputDriver.CreateDataSource(outputpath)
        outputLayer = outputDataSource.CreateLayer(name, geom_type=inputfeature.geometryType)
        featureDefn = outputLayer.GetLayerDefn()
        outputFeature = ogr.Feature(featureDefn)
        for feat in inputfeature.layer:
            geom = feat.GetGeometryRef()
            geom.Transform(coordTrans)
            outputFeature.SetGeometry(geom)
            outputLayer.CreateFeature(outputFeature)
        outputDataSource = None
        return outputpath

    def _getCenter(self, geojson):
        """
        Gets called by generateMap.
        Calculates the center of the region to center the map on.
        """
        x_coords = []
        y_coords = []
        with open(geojson) as data:
            jsoncontent = json.load(data)
            for coord in jsoncontent["features"][0]["geometry"]["coordinates"][0]:
                x_coords.append(coord[0])
                y_coords.append(coord[1])
        x_center = (max(x_coords) + min(x_coords)) / 2
        y_center = (max(y_coords) + min(y_coords)) / 2
        return [y_center, x_center]

    def _getCoordTrans(self, inputfeature: object, outputEPSG=4326):
        """
        Gets called by convert2GeoJSON.
        Returns a CoordinateTransformation item.
        """
        sourceSR = inputfeature.spatialRef
        outputRef = osr.SpatialReference()
        sourceSR.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        outputRef.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        outputRef.ImportFromEPSG(outputEPSG)
        return osr.CoordinateTransformation(sourceSR, outputRef)

    def addFeature2Map(self, featurepath, name: str, foliummap, fillcolor: str, color: str) -> None:
        """
        Gets called by generateMap. Adds the geojsons found in featurepath to the foliummap.
        name is displayed in the folium map LayerControl. fillcolor can either be a string of the
        color the user wants or an empty string, in which case the Polygon wont be filled.
        color specifies the color of the border of the feature.
        If both fillcolor and color are empty string we pick a random color.
        """
        if fillcolor == "" and color == "":
            fillcolor, color = self._getRandomColor()
        fillbool = bool(fillcolor)
        group = folium.FeatureGroup(name=name).add_to(foliummap)
        with open(featurepath) as data:
            jsoncontent = json.load(data)
            for feature in jsoncontent["features"]:
                poly = (folium.GeoJson(feature, name=name,
                                       style_function=lambda feature: {
                                           'fill': fillbool,
                                           'fillColor': fillcolor,
                                           'color': color,
                                           'weight': 2
                                       }))
                group.add_child(poly)

    def _getRandomColor(self):
        """
        Gets called by addFeature2Map.
        Returns two identical strings with colors to use in the Map.
        """
        colorList = [  # from folium documentation
            "red", "blue", "green", "purple", "orange", "darkred", "lightred", "beige", "darkblue",
            "darkgreen", "cadetblue", "darkpurple", "white", "pink", "lightblue", "lightgreen",
            "gray", "black", "lightgray"
        ]
        color = random.choice(colorList)
        return color, color

    def _delTmpGeoJSON(self, regionpath: str, featurepaths: list) -> None:
        """
        Gets called by generateMap.
        Deletes the temporary GeoJSONs after the map was created.
        """
        os.remove(regionpath)
        for tmp in featurepaths:
            os.remove(tmp)
