# -*- coding: utf-8 -*-

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *
import sys
import os
import math
import logging
from osgeo import gdal, ogr, osr
from core.uis.GeoViewer_ui.BasicViewer_ui import Ui_Viewer

import numpy as np
from core.libs.GDAL_Libs.Layers import Raster, Feature
from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog

zoomFactor = 1.05


class Viewer(QMainWindow):
    def __init__(self, projectLocation=None, raster=None, parent=None):
        QMainWindow.__init__(self, parent)
        self.ui = Ui_Viewer()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(":/icons/Icons/geoviewer.png"))
        self.ui.progress = QProgressBar()
        self.ui.progress.setTextVisible(False)
        self.ui.statusbar.addPermanentWidget(self.ui.progress)

        self.projectLocation = projectLocation
        self.rasterPath = raster
        self.fileDialog = CustomFileDialog()

        # set scene
        self.scene = QGraphicsScene()
        # set variable imagePixmap
        self.imagePixmap = None

        # set scene to graphic view
        self.ui.graphicsView.setScene(self.scene)
        # set actions to toolbar
        actionLoadRaster = QAction(
            QIcon(":/icons/Icons/LoadRaster_bw.png"),
            self.tr('Load Raster'),
            self)
        actionLoadRaster.triggered.connect(self.openRasterFile)
        self.ui.toolBar.addAction(actionLoadRaster)
        actionSetLegend = QAction(QIcon(":/icons/Icons/Legend.png"), self.tr('Set Legend'), self)
        actionSetLegend.triggered.connect(self.getLegend)
        self.ui.toolBar.addAction(actionSetLegend)
        actionSetBoundingBox = QAction(
            QIcon(":/icons/Icons/BoundingBox.png"),
            self.tr('Set bounding box'),
            self)
        actionSetBoundingBox.triggered.connect(self.setCoordinateFrame)
        self.ui.toolBar.addAction(actionSetBoundingBox)
        actionSaveImage = QAction(QIcon(":/icons/Icons/SaveEdits.png"),
                                  self.tr('Export map to Image'), self)
        actionSaveImage.triggered.connect(self.saveMap2Image)
        self.ui.toolBar.addAction(actionSaveImage)

        # set globals
        self.origin = [0, 0]
        self.xres = 30
        self.yres = 30

        self.georef = "unknown units"
        if self.rasterPath:
            self.loadRaster(self.rasterPath)

    def openRasterFile(self):
        self.rasterPath = self.fileDialog.openRasterFile(self.projectLocation)
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
                self.rasterPath = self.fileDialog.selectedFiles()[0]
                self.loadRaster(self.rasterPath)

    def loadRaster(self, rasterPath: str) -> None:
        """
        Adds a raster to the scene.
        """
        # open Raster dataset and load to the Raster object
        raster = Raster(rasterPath)
        array = raster.getArrayFromBand()
        # cellsize
        self.xres = raster.cellsize[0]
        self.yres = raster.cellsize[1]
        # epsg code from spatial reference
        self.epsg = raster.getEPSG_Code()

        # set Transformation from raster object epsg to WGS84 (see function below)
        self.coordTrans = self.getTransform()
        if raster.geoTrans:
            self.georef = str(raster.getUNIT())
        # get the x_min coordinate
        x_min = raster.geoTrans[0]
        # calculate the x_max coordinate from x-range and cellsize
        x_max = x_min + raster.geoTrans[1] * raster.cols
        # get the y_max coordinate
        y_max = raster.geoTrans[3]
        # calculate the y_min coordinate from y-range and cellsize
        y_min = raster.geoTrans[3] + raster.geoTrans[5] * raster.rows
        # create the origin variable holding x_min and y_max (coordinates of the
        # upper left corner)
        self.origin = [x_min, y_max]

        # create an array normalized to values between 0 and 254
        # If .min == .max we divide by 0, so we need to surpress the warning
        with np.errstate(divide='ignore', invalid='ignore'):
            image = ((array.astype(np.float32) - raster.min) / (raster.max - raster.min)) * 254
        # set nodatavalues of the raster to 255
        image[np.where(array == raster.nodata)] = 255
        # get unique values in the image array (for continous data from 1 to 255,
        # for dicrete values dicrete number in the range of 1 and 255)
        uniq_int = np.unique(image.astype(np.uint8))
        # create Qimage from image array
        qImage = QImage(
            image.astype(
                np.uint8),
            image.shape[1],
            image.shape[0],
            image.shape[1],
            QImage.Format_Indexed8)

        # create a GDAL color table
        self.GDAL_colorTable = gdal.ColorTable()
        # create color ramp to set colors in the image
        self.GDAL_colorTable.CreateColorRamp(0, (0, 0, 255, 255), 254, (255, 0, 0, 255))

        # set the color from color ramp to the Qimage
        for value in uniq_int:
            if value == 255:
                r, g, b, a = (0, 0, 0, 0)
            else:
                r, g, b, a = self.GDAL_colorTable.GetColorEntry(int(value))
            qImage.setColor(value, QColor(r, g, b, a).rgba())

        # create image Pixmap from QImage
        self.imagePixmap = QPixmap.fromImage(qImage)

        # create item from image Pixmap and set some properties (e.g. selectable)
        item = QGraphicsPixmapItem(self.imagePixmap)
        item.setFlag(QGraphicsItem.ItemIsSelectable, True)

        # Set the image to the graphic scene as a pixmap object
        mapItem = self.scene.addItem(item)

    def fitToView(self):
        self.ui.graphicsView.fitInView(self.scene.itemsBoundingRect(), QtCore.Qt.KeepAspectRatio)

    def saveMap2Image(self):
        self.fileDialog.saveImageFile(self.projectLocation)
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
            self._updateProgress(True)
            if os.path.splitext(self.fileDialog.selectedFiles()[0])[1].lower() == ".png":
                path = self.fileDialog.selectedFiles()[0]
            else:
                path = self.fileDialog.selectedFiles()[0] + ".png"
            pixmap = QPixmap(self.ui.graphicsView.viewport().size())
            self.ui.graphicsView.viewport().render(pixmap)
            pixmap.save(path, quality=100)
            logging.info(self.tr("{} saved.").format(os.path.normpath(path)))
            self._updateProgress(False)

    def _updateProgress(self, switch: bool) -> None:
        """
        Gets called by saveMap2Image.
        Changes the progressbar to tell user something is going on.
        """
        self.ui.progress.setRange(0, int(not switch))

    def getLegend(self):
        # Checks if LSAT already shows a legend. If yes do not draw a second one.
        for item in self.scene.items():
            try:
                if "legend_" + self.rasterPath == item.objectName():
                    return 1
            except AttributeError:
                continue
        try:
            # Hides GDAL Error that appears if no file is selected
            gdal.PushErrorHandler("CPLQuietErrorHandler")
            raster = Raster(self.rasterPath)
            fontsize = self._getFontSizeLegend(raster)
            gdal.PushErrorHandler()
            item_group = QGraphicsItemGroup()
            item_group.setFlag(QGraphicsItem.ItemIsMovable)
            item_group.setFlag(QGraphicsItem.ItemIsSelectable)
            item_group.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

            colorBar = QtCore.QRectF(0, 0, 100, 500)
            gradient = QLinearGradient(QPointF(colorBar.bottomLeft()), QPointF(colorBar.topLeft()))
            gradient.setColorAt(0, QColor(0, 0, 255, 255))
            gradient.setColorAt(1, QColor(255, 0, 0, 255))

            titleFont = QFont("Arial", fontsize)
            titleFont.setBold(1)
            titleTextItem = self.scene.addText(self.tr("Values"), font=titleFont)
            # We name the title after raster to check if it exists
            titleTextItem.setObjectName("legend_" + self.rasterPath)
            titleTextItem.setPos(QPointF(0, 0))
            item_group.addToGroup(titleTextItem)

            colorBarItem = self.scene.addRect(colorBar, pen=QPen(Qt.black), brush=QBrush(gradient))
            colorBarItem.setPos(QPointF(0, 150))
            item_group.addToGroup(colorBarItem)

            maxValueTextItem = self.scene.addText(str(raster.max), font=QFont("Arial", fontsize))
            maxValueTextItem.setPos(QPointF(110, 100))
            item_group.addToGroup(maxValueTextItem)

            minValueTextItem = self.scene.addText(str(raster.min), font=QFont("Arial", fontsize))
            minValueTextItem.setPos(QPointF(110, 600))
            item_group.addToGroup(minValueTextItem)
            self.scene.addItem(item_group)
        except Exception as e:
            if str(e) != "'NoneType' object has no attribute 'RasterXSize'":
                # This is the error message that shows up if no raster is selected. We hide it, to not
                # confuse the user.
                logging.error(str(e))

    def _getFontSizeLegend(self, rasterHandle: object) -> int:
        """
        Gets called getLegend.
        The font size should be well sized when the raster fills the whole scene
        Returns the font size (int) based on the raster size.
        """
        minVal = min(rasterHandle.cols, rasterHandle.rows)
        fontSize = minVal // 30 if minVal > 240 else 8
        return fontSize

    def setCoordinateFrame(self):
        """
        Draws a Box with longtitude and latitude around the selected item.
        """
        if self.scene.selectedItems():
            item = self.scene.selectedItems()[0]
        else:
            return # nothing selected
        # get the bounding box of the item
        coordinateFrame = QGraphicsItemGroup()
        coordinateFrame.setFlag(QGraphicsItem.ItemIsSelectable, True)
        frameBox = QRectF(item.boundingRect())
        # get size of font/offset based on frameBox size
        size = self._getSizeFrame(frameBox)
        offset = size // 2
        # add boundingBox to coordinateFrame
        coordinateFrame = self._addBoundingBox(offset, frameBox, coordinateFrame)
        # Creation of ticks
        x_tick_spaces = 4
        y_tick_spaces = 4
        # get the width and height of the item
        width = item.sceneBoundingRect().topRight().x() - item.sceneBoundingRect().topLeft().x()
        x_tick_distance = width / x_tick_spaces
        height = item.sceneBoundingRect().bottomRight().y() - item.sceneBoundingRect().topRight().y()
        y_tick_distance = height / y_tick_spaces
        # add axes
        coordinateFrame = self._addXAxis(size, x_tick_spaces, x_tick_distance, item, coordinateFrame)
        coordinateFrame = self._addYAxis(size, y_tick_spaces, y_tick_distance, item, coordinateFrame)
        self.scene.addItem(coordinateFrame)

    def _getSizeFrame(self, frame: object) -> int:
        """
        Gets called setCoordinateFrame.
        The font size and offset should be well sized when the frame fills the whole scene
        Returns the font size/offset (int) based on the QGraphicsPixmapItem size.
        """
        minVal = min(frame.width(), frame.height())
        size = minVal // 30 if minVal > 240 else 8
        return size

    def _addBoundingBox(self, offset: int, frameBox, coordinateFrame) -> tuple:
        """
        Gets called by setCoordinateFrame.
        Returns coordinateFrame with added boundingBox.
        """
        # adjust frameBox with offset
        boundingBox = frameBox.adjusted(-offset, -offset, offset, offset)
        # create boundingBox item
        boundingBoxItem = self.scene.addRect(
            boundingBox, pen=QPen(
                QtCore.Qt.black, 4), brush=QBrush(
                Qt.transparent))
        coordinateFrame.addToGroup(boundingBoxItem)
        return coordinateFrame

    def _addXAxis(self, size: int, x_tick_spaces: int, x_tick_distance: int, item, coordinateFrame):
        """
        Gets called by setCoordinateFrame.
        Adds Ticks, Labels (calculated GeoRef WGS84) to the x-Axis.
        Returns the enhanced coordinateFrame.
        """
        for i in range(0, x_tick_spaces + 1):
            # set ticks along x-axis
            xTick = QtCore.QLineF(
                item.sceneBoundingRect().topLeft().x() + x_tick_distance * i,
                item.sceneBoundingRect().topLeft().y() - size ,
                item.sceneBoundingRect().topLeft().x() + x_tick_distance * i,
                item.sceneBoundingRect().topLeft().y() - size // 2)
            xTickItem = self.scene.addLine(xTick, pen=QPen(Qt.black, 4))
            coordinateFrame.addToGroup(xTickItem)

            # x and y points for coordinate of the tick
            xtickCoord = QPointF(
                item.sceneBoundingRect().topLeft().x() + x_tick_distance * i,
                item.sceneBoundingRect().topLeft().y())
            # points to relative view
            xtickCoord_rel = self.ui.graphicsView.mapFromScene(xtickCoord)
            # relative view coordinates to projected coordinates
            geoX, geoY = self.TransformImageCoordsToGeoCoords(
                xtickCoord_rel.x(), xtickCoord_rel.y())
            # text to wgs84 coorindates
            _, xLabelValue, _ = self.coordTrans.TransformPoint(geoX, geoY, 0.0) # y, x, z
            # degree to degrees, minutes, seconds
            deg, minute, sec = self.decimalDegree2Degree(xLabelValue)
            # add text label to scene
            xLabelTextItem = self.scene.addText(
                (f"{deg}° {minute}' {sec}''"), font=QFont("Arial", size))
            # get width of the textbox
            xLabelBox_length = xLabelTextItem.boundingRect().topRight().x() - \
                xLabelTextItem.boundingRect().topLeft().x()
            # adjust the position of the textbox above the tick
            xLabelTextItem.setPos(
                QPointF(
                    item.sceneBoundingRect().topLeft().x() +
                    x_tick_distance *
                    i -
                    xLabelBox_length /
                    2,
                    item.sceneBoundingRect().topLeft().y() -
                    100))
            coordinateFrame.addToGroup(xLabelTextItem)
        return coordinateFrame

    def _addYAxis(self, size: int, y_tick_spaces: int, y_tick_distance: int, item, coordinateFrame):
        """
        Gets called by setCoordinateFrame.
        Adds Ticks, Labels (calculated GeoRef WGS84) to the y-Axis.
        Returns the enhanced coordinateFrame.
        """
        for i in range(0, y_tick_spaces + 1):
            # set ticks along y-axis
            yTick = QLineF(item.sceneBoundingRect().topLeft().x() - size,
                           item.sceneBoundingRect().topLeft().y() + y_tick_distance * i,
                           item.sceneBoundingRect().topLeft().x() - size // 2,
                           item.sceneBoundingRect().topLeft().y() + y_tick_distance * i)
            yTickItem = self.scene.addLine(yTick, pen=QPen(Qt.black, 4))
            coordinateFrame.addToGroup(yTickItem)
            ytickCoord = QPointF(
                item.sceneBoundingRect().topLeft().x(),
                item.sceneBoundingRect().topLeft().y() + y_tick_distance * i)
            ytickCoord_rel = self.ui.graphicsView.mapFromScene(ytickCoord)
            geoX, geoY = self.TransformImageCoordsToGeoCoords(
                ytickCoord_rel.x(), ytickCoord_rel.y())
            yLabelValue, _, _ = self.coordTrans.TransformPoint(geoX, geoY, 0.0) # returns y, x, z
            # degree to degrees, minutes, seconds
            deg, minute, sec = self.decimalDegree2Degree(yLabelValue)
            # add text label to scene
            yLabelTextItem = self.scene.addText(
                (f"{deg}° {minute}' {sec}''"), font=QFont("Arial", size))
            yLabelBox_height = yLabelTextItem.boundingRect().bottomLeft().y() - \
                yLabelTextItem.boundingRect().topLeft().y()
            yLabelBox_length = yLabelTextItem.boundingRect().topRight().x() - \
                yLabelTextItem.boundingRect().topLeft().x()
            yLabelTextItem.setPos(
                QPointF(
                    item.sceneBoundingRect().topLeft().x() -
                    yLabelBox_length -
                    20,
                    item.sceneBoundingRect().topLeft().y() +
                    y_tick_distance *
                    i -
                    yLabelBox_height /
                    2))
            coordinateFrame.addToGroup(yLabelTextItem)
        return coordinateFrame

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            for itemSelected in self.scene.selectedItems():
                self.scene.removeItem(itemSelected)

    def getScaleRatio(self):
        viewGeometry = self.ui.graphicsView.viewport().geometry()
        scaleRatioX = self.scene.width() / viewGeometry.width()
        scaleRatioY = self.scene.height() / viewGeometry.height()
        return scaleRatioX, scaleRatioY

    def decimalDegree2Degree(self, value):
        decimal, degree = math.modf(value)
        second_part, minutes = math.modf(decimal * 3600 / 60)
        minutes = abs(minutes)
        seconds = abs(second_part * 60)
        return int(degree), int(minutes), int(seconds)

    def getTransform(self):
        """
        Gets called by init.
        Provides the transformation from source epsg to target epsg (here WGS84 epsg: 4326)
        """
        sourceSR = osr.SpatialReference()
        sourceSR.ImportFromEPSG(int(self.epsg))
        targetSR = osr.SpatialReference()
        targetSR.ImportFromEPSG(4326)
        coordTrans = osr.CoordinateTransformation(sourceSR, targetSR)
        return coordTrans

    def relativePosition(self):
        if len(self.scene.items()) == 0:
            topLeft = QtCore.QPoint(0, 0)
            topRight = QtCore.QPoint(100, 0)
            bottomLeft = QtCore.QPoint(0, 50)
        else:
            for mapItem in self.scene.items():
                if mapItem.type() != 7:
                    pass
                else:
                    sp = mapItem.mapToScene(mapItem.pos())
                    topLeft = self.ui.graphicsView.mapFromScene(sp)
                    topRight = self.ui.graphicsView.mapFromScene(
                        mapItem.sceneBoundingRect().topRight())
                    bottomLeft = self.ui.graphicsView.mapFromScene(
                        mapItem.sceneBoundingRect().bottomLeft())
        return topLeft, topRight, bottomLeft

    def TransformImageCoordsToGeoCoords(self, x, y):
        topLeft, topRight, bottomLeft = self.relativePosition()
        scaleRatioX = self.scene.width() / (topRight.x() - topLeft.x())
        scaleRatioY = self.scene.height() / (bottomLeft.y() - topLeft.y())
        xGeo = self.origin[0] + (x - topLeft.x()) * self.xres * scaleRatioX
        yGeo = self.origin[1] + (y - topLeft.y()) * (self.yres) * scaleRatioX
        return xGeo, yGeo

    def wheelEvent(self, event):
        """
        Gets called when the user scrolls his mouse wheel.
        Zooms in and out.
        """
        if self.imagePixmap:
            cursor = QCursor()
            if event.angleDelta().y() > 0:
                self.ui.graphicsView.scale(zoomFactor, zoomFactor)
            else:
                self.ui.graphicsView.scale(1 / zoomFactor, 1 / zoomFactor)
            self.ui.graphicsView.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.MouseMove and source == self.ui.graphicsView.viewport():
            if event.buttons() == QtCore.Qt.NoButton:
                self.scaleRatioX, self.scaleRatioY = self.getScaleRatio()
                # event position in Coordinaten des Viewports
                x = event.pos().x()
                y = event.pos().y()
                xGeo, yGeo = self.TransformImageCoordsToGeoCoords(x, y)
                self.statusBar().showMessage('%f %f %s' % (xGeo, yGeo, self.georef), 2000)
        return QMainWindow.eventFilter(self, source, event)