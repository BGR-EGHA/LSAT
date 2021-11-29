import logging
import matplotlib
import numpy as np
import os
import traceback
from osgeo import gdal
from osgeo import osr
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog
from core.libs.GDAL_Libs.Layers import Raster, RasterLayer
from core.libs.Management.LayerManagement import LayerManagement
from core.uis.ModelBuilder_ui.ModelBuilder_ui import Ui_ModelBuilder
from core.widgets.ModelBuilder.modelbuilder_calc import ModelBuilder_calc
from core.widgets.ModelInfo.modelinfo_main import ModelInfo
from core.widgets.ModelBuilder.modelbuilder_expression import ExpressionBuilder
from core.widgets.WofE.advancedSettings_main import AdvancedSettings
from core.widgets.Zoning.Zoning_main import Zoning


class ModelBuilder(QMainWindow):
    def __init__(self, projectpath: str, parent=None):
        super().__init__()
        self.projectpath = projectpath
        self.dialog = CustomFileDialog()
        self.mask = Raster(os.path.join(projectpath, "region.tif"))
        self.modelsmanager = LayerManagement()
        self.advanced = AdvancedSettings(projectpath)
        self.spatref = osr.SpatialReference()
        self.spatref.ImportFromEPSG(int(self.mask.epsg))
        # ui
        self.ui = Ui_ModelBuilder()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(":/icons/Icons/model_builder.png"))
        self.ui.actionAdvanced_Settings.setIcon(QIcon(":/icons/Icons/Settings.png"))
        self.ui.expressionToolButton.setIcon(QIcon(":/icons/Icons/File_Table.png"))
        # connect signals
        self.ui.modelsTreeWidget.itemChanged.connect(self.redrawplot)
        self.ui.modelsTreeWidget.itemSelectionChanged.connect(self.modelselectionchanged)
        self.ui.modelsTreeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.modelsTreeWidget.customContextMenuRequested.connect(self.modelcontextmenuevent)
        self.ui.woeLayerTreeWidget.setContextMenuPolicy(
            Qt.CustomContextMenu)  # right click to move to model
        self.ui.woeLayerTreeWidget.customContextMenuRequested.connect(
            self.on_addtoModelLayerToolButton_clicked)
        self.ui.modelLayerTreeWidget.setContextMenuPolicy(
            Qt.CustomContextMenu)  # right click to remove from model
        self.ui.modelLayerTreeWidget.customContextMenuRequested.connect(
            self.on_removefromModelLayerToolButton_clicked)
        self.ui.actionAdvanced_Settings.triggered.connect(self.openadvanced)
        # set up ROC (matplotlib)
        self.setupROC()
        # Search for and load Features, weighted Layers and existing models from project
        self.loadfeaturefiles(projectpath)
        self.loadrastersinit(projectpath)
        self.loadmodelsinit(projectpath)

    @pyqtSlot()
    def on_expressionToolButton_clicked(self):
        """
        Calls the Expression Builder.
        :return: None
        """
        if self.ui.modelLayerTreeWidget.invisibleRootItem().childCount() == 0:  # Check rasters
            logging.error(self.tr("No layers selected."))
            self.ui.modelLayerTreeWidget.setStyleSheet("background-color: rgb(255, 0, 0)")
            QTimer.singleShot(500, lambda: self.ui.modelLayerTreeWidget.setStyleSheet(""))
        else:
            try:
                itemcount = self.ui.modelLayerTreeWidget.invisibleRootItem().childCount()
                layers = []
                for i in range(itemcount):
                    item = self.ui.modelLayerTreeWidget.topLevelItem(i)
                    name = self.modelsmanager.treeContent[hash(str(item))]['Name']
                    layers.append(name)
                expression = self.ui.expressionTextEdit.toPlainText()
                self.expBuilder = ExpressionBuilder(expression, layers, parent = self)
                self.expBuilder.expressionSignal.connect(self.getExpression)
                self.expBuilder.show()
            except BaseException:
                tb = traceback.format_exc()
                logging.error(tb)
        return

    def getExpression(self, expression):
        """
        Set the expression received from Expression Builder
        :param expression:
        :return:
        """
        try:
            self.ui.expressionTextEdit.clear()
            self.ui.expressionTextEdit.setText(expression)
        except BaseException:
            tb = traceback.format_exc()
            logging.error(tb)

    def setDefaultExpression(self):
        """
        Set default liniar data generation model based on model layer list
        :return: None
        """
        expression = ""
        itemcount = self.ui.modelLayerTreeWidget.invisibleRootItem().childCount()
        for i in range(itemcount):
            item = self.ui.modelLayerTreeWidget.topLevelItem(i)
            name = self.modelsmanager.treeContent[hash(str(item))]['Name'].replace(" ", "")
            if i < (itemcount - 1):
                expression += str(name) + " + "
            else:
                expression += str(name)
        self.ui.expressionTextEdit.setPlainText(expression)

    def redrawplot(self, item):
        """
        Gets called when when an item changes in modelsTreeWidget.
        """
        label = item.text(0)  # file name without extension
        lineLabels, polyLabels = self._get_PolyandLineLabels()
        if item.checkState(4) == 0 and label in polyLabels:  # User unchecked show range
            self._removePoly(label)
        elif item.checkState(4) == 2 and label not in polyLabels:  # User checked show range
            self._showPoly(label)
        if item.checkState(0) == 0 and label in lineLabels:  # User unchecked the model
            self._removeModelPlot(label, item)
        elif item.checkState(0) == 2 and label not in lineLabels:  # User checked the model
            self._showModelPlot(label)
        if item.isSelected():  # Highlight selected line
            self._highlightLine(label)
        self.canvas_roc.draw()

    def _get_PolyandLineLabels(self):
        """
        Gets called by redrawplot.
        Returns two lists: lineLabels (labels of lines currently displayed in the ROC plot)
        and polyLabels (labels of polys (areas) currently displayed in the ROC plot)
        """
        lineLabels = [line.get_label() for line in self.axes_roc.lines]
        polyLabels = [poly.get_label() for poly in self.axes_roc.collections]
        return lineLabels, polyLabels

    def _removePoly(self, label):
        """
        Gets called by redrawplot.
        Removes Poly from ROC Plot based on label
        """
        for poly in self.axes_roc.collections:
            if poly.get_label() == label:
                poly.remove()

    def _showPoly(self, label):
        """
        Gets called by redrawplot.
        Draws a polygon indicating the range of the ROC, as there are multiple subsamples.
        """
        model = np.load(
            os.path.join(
                self.projectpath,
                "results",
                "susceptibility_maps",
                label + ".npz"),
            allow_pickle=True)
        # We saved the path during import
        if len(model["roc_x"]) > 300:  # Over 300 ROC Curves in collection
            slice_interval = len(model["roc_x"]) // 300
        else:
            slice_interval = 1
        self.axes_roc.fill_between(model["roc_x"][::slice_interval],
                                   model["roc_ymin"][::slice_interval],
                                   model["roc_ymax"][::slice_interval], color="grey",
                                   linestyle="--", alpha=0.5,
                                   label=model['name'], zorder=1)

    def _removeModelPlot(self, label, item):
        """
        Gets called by redrawplot and on_DeleteModeltoolButton_clicked.
        Removes poly and line from ROC Plot based on label.
        We use item and label here because we uncheck poly if necessary
        """
        for line in self.axes_roc.lines:
            if line.get_label() == label:
                line.remove()
        for poly in self.axes_roc.collections:
            if poly.get_label() == label:
                poly.remove()
                item.setCheckState(4, Qt.Unchecked)

    def _showModelPlot(self, label):
        """
        Gets called by redrawplot.
        We draw the ROC Curve of the model.
        """
        model = np.load(
            os.path.join(
                self.projectpath,
                "results",
                "susceptibility_maps",
                label + ".npz"))
        if len(model["roc_x"]) > 300:  # Over 300 data points
            slice_interval = int(len(model["roc_x"]) / 300)
        else:
            slice_interval = 1
        self.axes_roc.plot(model['roc_x'][::slice_interval],
                           model['roc_ymean'][::slice_interval],
                           label=model['name'])

    def _highlightLine(self, label):
        """
        Gets called by redrawplot and modelselectionchanged.
        Highlights the selected line.
        """
        for line in self.axes_roc.lines:
            if line.get_label() == label:
                line.set_linewidth(3)
            else:
                line.set_linewidth(1)

    def modelselectionchanged(self):
        """
        Gets called when the user select a different item in modelsTreeWidget.
        """
        try:
            items = self.ui.modelsTreeWidget.selectedItems()
            if len(items) > 0:
                for item in items:
                    index = self.ui.modelsTreeWidget.currentIndex().row()
                    label = self.ui.modelsTreeWidget.topLevelItem(index).text(0)
                    self._highlightLine(label)
                self.canvas_roc.draw()
        except AttributeError:  # If we click on weird places LSAT sometimes can't find stuff
            pass

    def modelcontextmenuevent(self, event):
        """
        This function adds a contextmenu for modelsTreeWidget.
        It replicates the features from the toolbuttons at the top.
        """
        menu = QMenu()
        actionModel2raster = QAction(
            QIcon(":/icons/Icons/WriteRaster.png"),
            self.tr("Model to Raster"),
            None)
        menu.addAction(actionModel2raster)
        actionModel2raster.triggered.connect(self.on_WriteRastertoolButton_clicked)
        actionModelinfo = QAction(
            QIcon(":/icons/Icons/model_info.png"),
            self.tr("Model Info"),
            None)
        menu.addAction(actionModelinfo)
        actionModelinfo.triggered.connect(self.on_ModelInfotoolButton_clicked)
        actionDelete = QAction(QIcon(":/icons/Icons/Trashbox.png"), self.tr("Delete Model"), None)
        menu.addAction(actionDelete)
        actionDelete.triggered.connect(self.on_DeleteModeltoolButton_clicked)
        actionZonation = QAction(QIcon(":/icons/Icons/zoning.png"), self.tr("Zonation"), None)
        menu.addAction(actionZonation)
        actionZonation.triggered.connect(self.on_ZoningtoolButton_clicked)
        menu.exec_(QCursor.pos())

    def openadvanced(self):
        self.advanced.show()

    def setupROC(self):
        """
        Gets called by __init__.
        Sets up the matplotlib plot of the ROC.
        Defines:
        self.fig_roc
        self.axes_roc
        self.canvas_roc
        """
        prop = self._fontpicker(os.name)
        self.fig_roc = matplotlib.figure.Figure()
        self.canvas_roc = matplotlib.backends.backend_qt5agg.FigureCanvasQTAgg(self.fig_roc)
        self.canvas_roc.setParent(self.ui.rocGroupBox)
        self.axes_roc = self.fig_roc.add_subplot(111)
        self.ui.rocGroupBoxGridLayout.addWidget(self.canvas_roc)
        self.axes_roc.set_xlabel(
            self.tr('False Positive Rate (1-Specificity)'),
            fontproperties=prop)
        self.axes_roc.set_ylabel(self.tr('True Positive Rate (Sensitivity)'), fontproperties=prop)
        self.axes_roc.set_xlim([0.0, 1.0])
        self.axes_roc.set_ylim([0.0, 1.0])
        self.fig_roc.tight_layout()
        mpl_toolbar_roc = matplotlib.backends.backend_qt5.NavigationToolbar2QT(
            self.canvas_roc, self.ui.rocGroupBox)
        self.ui.rocGroupBoxGridLayout.addWidget(mpl_toolbar_roc)

    def _fontpicker(self, osname: str):
        """
        Gets called by setupROC.
        Returns a matplotlib fontproperties object based on the detected OS.
        """
        if osname == "nt":  # Windows
            prop = matplotlib.font_manager.FontProperties(fname="C:\\Windows\\Fonts\\Msyh.ttc")
        else:  # ubuntu
            prop = matplotlib.font_manager.FontProperties(
                fname="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
        return prop

    def loadfeaturefiles(self, projectpath):
        """
        Gets called by __init__.
        Looks for feature files in the project structure and adds them to the ui.
        """
        for folder in ["training", "test"]:
            path = os.path.join(projectpath, "data", "inventory", folder)
            for file in os.listdir(path):
                file_ext = os.path.splitext(file)[1]
                if file_ext in [".shp", ".kml", ".geojson"]:
                    self.ui.landslideFeatureComboBox.insertItem(0, os.path.join(path, file))

    def loadrastersinit(self, projectpath):
        """
        Gets called by __init__.
        Adds raster from the rasters folders to the ui.
        """
        extension_list = ("_ann", "_lr", "_ahp", "_woe")
        for folder in ["AHP", "ANN", "LR", "WoE"]:
            path = os.path.join(projectpath, "results", folder, "rasters")
            for file in os.listdir(path):
                if file.endswith(".tif") and os.path.splitext(file)[0].endswith(extension_list):
                    npz = self._checkfornpz(projectpath, folder, file)
                    self._loadweighted_layer(file, path, npz)

    def _loadweighted_layer(self, file, path, npz):
        """
        Gets called by loadrastersinit and on_addWeightedLayerToolButton_clicked.
        Adds rasters to the ui.
        """
        item = QTreeWidgetItem()
        if npz:  # npz found
            item.setIcon(0, QIcon(":/icons/Icons/check.png"))
            result = np.load(npz)
            if "auc" in result:
                if result["auc"].shape == ():
                    auc = result["auc"]
                else:
                    auc = result["auc"].mean()
                item.setText(1, str(np.round(auc, 2)))
        else:  # npz not found
            item.setIcon(0, QIcon(":/icons/Icons/Warning.png"))
        layer = RasterLayer(os.path.join(path, file))
        item.setText(0, layer.name)
        self.ui.woeLayerTreeWidget.addTopLevelItem(item)
        self.modelsmanager.addTreeContent(hash(str(item)), layer.properties)
        self.ui.woeLayerTreeWidget.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.woeLayerTreeWidget.header().setStretchLastSection(False)
        self.ui.woeLayerTreeWidget.sortItems(1, Qt.DescendingOrder)

    def _checkfornpz(self, projectpath, folder, file) -> str:
        """
        Gets called by loadrastersinit.
        Checks if a corresponding npz exists in the project for file (the raster).
        The npz are either stored with the same name or with "_tab" appended.
        Returns a string to the npz or an empty string if it does not exist.
        """
        name = os.path.splitext(file)[0]
        extension_list = ("_ann", "_lr", "_ahp", "_woe")
        for ext in extension_list:
            if name.endswith(ext):
                name = name[:-len(ext)]
        if os.path.isfile(
            os.path.join(
                projectpath,
                "results",
                folder,
                "tables",
                name +
                "_tab.npz")):
            return os.path.join(projectpath, "results", folder, "tables", name + "_tab.npz")
        elif os.path.isfile(os.path.join(projectpath, "results", folder, "tables", name + ".npz")):
            return os.path.join(projectpath, "results", folder, "tables", name + ".npz")
        else:
            return ""

    def loadmodelsinit(self, projectpath):
        """
        Gets called by __init__.
        Loads existing models from the project into the ui.
        """
        self.ui.modelsTreeWidget.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        modelpath = os.path.join(projectpath, "results", "susceptibility_maps")
        for file in os.listdir(modelpath):
            if os.path.splitext(file)[1] == ".npz":
                self._loadmodels(file, modelpath, Qt.Unchecked)

    def _loadmodels(self, file, path, initialcheck):
        """
        Gets called by loadmodelsinit, populateSusModelTree.
        initialcheck sets the CheckState for drawing
        """
        item = QTreeWidgetItem()
        model = np.load(os.path.join(path, file), allow_pickle=True)
        item.setText(0, os.path.splitext(file)[0])
        try:
            item.setText(1, str(np.round(sum(model['auc']), 2)))
        except TypeError:
            item.setText(1, str(np.round(model['auc'], 2)))
        item.setText(2, str(len(model['params'])))
        item.setText(3, str(len(model['unique_values'])))
        item.setCheckState(0, initialcheck)
        if model["samplecount"] > 1:  # Model has a range
            item.setCheckState(4, initialcheck)
            item.setIcon(0, QIcon(":/icons/Icons/Modeler.png"))
        else:  # Model was calculated with only one sample
            item.setIcon(0, QIcon(":/icons/Icons/Modeler_grey.png"))
        self.ui.modelsTreeWidget.addTopLevelItem(item)
        if initialcheck == Qt.Checked:
            self.redrawplot(item)

    @pyqtSlot()
    def on_WriteRastertoolButton_clicked(self):
        """
        Creates a raster based on the selected model in its current folder.
        """
        if len(self.ui.modelsTreeWidget.selectedItems()) > 0:
            index = self.ui.modelsTreeWidget.currentIndex().row()
            label = self.ui.modelsTreeWidget.topLevelItem(index).text(0)
            npzpath = os.path.join(
                self.projectpath,
                "results",
                "susceptibility_maps",
                label + ".npz")
            rasterpath = os.path.splitext(npzpath)[0] + ".tif"
            self._npz2raster(npzpath, "data", rasterpath, self.mask, [np.isnan])
            logging.info(self.tr("Output raster {} created.").format(rasterpath))
        else:
            logging.info(self.tr("No model selected."))

    def _npz2raster(
            self,
            npzpath,
            arraykeyword,
            rasterpath,
            maskhandle,
            values2replace: list) -> str:
        """
        Gets called by on_WriteRastertoolButton_clicked.
        Creates a raster from an array stored in a npz file, while replacing a list of values with
        NoData (-9999)
        """
        driver = gdal.GetDriverByName("GTiff")
        outraster = driver.Create(rasterpath, maskhandle.cols, maskhandle.rows, 1, gdal.GDT_Float32)
        outraster.SetProjection(maskhandle.proj)
        outraster.SetGeoTransform(maskhandle.geoTrans)
        band = outraster.GetRasterBand(1)
        band.SetNoDataValue(-9999)
        model = np.load(npzpath)
        array = model[arraykeyword]
        for value in values2replace:
            array[array == value] = -9999
        band.WriteArray(array)
        band.ComputeStatistics(False)
        outraster = None
        return rasterpath

    @pyqtSlot()
    def on_ModelInfotoolButton_clicked(self):
        """
        Opens the Model Info for the selected model.
        """
        if len(self.ui.modelsTreeWidget.selectedItems()) > 0:
            index = self.ui.modelsTreeWidget.currentIndex().row()
            label = self.ui.modelsTreeWidget.topLevelItem(index).text(0)
            npzpath = os.path.join(
                self.projectpath,
                "results",
                "susceptibility_maps",
                label + ".npz")
            self.modelinfo = ModelInfo(npzpath)
            self.modelinfo.show()
        else:
            logging.info(self.tr("No model selected."))

    @pyqtSlot()
    def on_DeleteModeltoolButton_clicked(self):
        """
        Deletes the selected model, removes it from the plot and updates the plot.
        """
        items = self.ui.modelsTreeWidget.selectedItems()
        if len(items) > 0:
            for item in items:
                index = self.ui.modelsTreeWidget.currentIndex().row()
                delitem = self.ui.modelsTreeWidget.topLevelItem(index)
                label = delitem.text(0)
            root = self.ui.modelsTreeWidget.invisibleRootItem()
            modelpath = os.path.join(
                self.projectpath,
                "results",
                "susceptibility_maps",
                label + ".npz")
            really = QMessageBox.question(self, self.tr("Delete {}?").format(label), self.tr(
                "This will delete {} Continue?").format(modelpath), QMessageBox.Yes | QMessageBox.No)
            if really == QMessageBox.Yes:
                self._removeModelPlot(label, delitem)
                os.remove(modelpath)
                root.removeChild(delitem)
                logging.info(self.tr("Model {} deleted.").format(modelpath))
                self.canvas_roc.draw()
        else:
            logging.info(self.tr("No model selected."))

    @pyqtSlot()
    def on_ZoningtoolButton_clicked(self):
        """
        Opens the Zoning widget with the selected model
        """
        items = self.ui.modelsTreeWidget.selectedItems()
        if len(items) > 0:
            for item in items:
                index = self.ui.modelsTreeWidget.currentIndex().row()
                label = self.ui.modelsTreeWidget.topLevelItem(index).text(0)
            self.zon = Zoning(
                modelPath=os.path.join(
                    self.projectpath,
                    "results",
                    "susceptibility_maps",
                    label + ".npz"),
                projectLocation=self.projectpath)
            self.zon.loadData()
            self.zon.show()
        else:
            logging.info(self.tr("No model selected."))

    @pyqtSlot()
    def on_addtoModelLayerToolButton_clicked(self):
        """
        Moves selected weighted layers to the new model layer list.
        """
        for item in self.ui.woeLayerTreeWidget.selectedItems():
            index = self.ui.woeLayerTreeWidget.currentIndex().row()
            treeItem = self.ui.woeLayerTreeWidget.topLevelItem(index)
            self.ui.woeLayerTreeWidget.invisibleRootItem().removeChild(treeItem)
            self.ui.modelLayerTreeWidget.addTopLevelItem(treeItem)
            self.ui.modelLayerTreeWidget.sortItems(1, Qt.DescendingOrder)
            self.setDefaultExpression()

    @pyqtSlot()
    def on_removefromModelLayerToolButton_clicked(self):
        """
        Passes selected model layer back to the weighted layers list.
        """
        for item in self.ui.modelLayerTreeWidget.selectedItems():
            index = self.ui.modelLayerTreeWidget.currentIndex().row()
            treeItem = self.ui.modelLayerTreeWidget.topLevelItem(index)
            self.ui.modelLayerTreeWidget.invisibleRootItem().removeChild(treeItem)
            self.ui.woeLayerTreeWidget.addTopLevelItem(treeItem)
            self.ui.woeLayerTreeWidget.sortItems(1, Qt.DescendingOrder)
            self.setDefaultExpression()

    @pyqtSlot()
    def on_removeLayerToolButton_clicked(self):
        """
        Removes selected layer from the weighted layers list.
        """
        for item in self.ui.woeLayerTreeWidget.selectedItems():
            index = self.ui.woeLayerTreeWidget.currentIndex().row()
            treeItem = self.ui.woeLayerTreeWidget.topLevelItem(index)
            self.ui.woeLayerTreeWidget.invisibleRootItem().removeChild(treeItem)

    @pyqtSlot()
    def on_addWeightedLayerToolButton_clicked(self):
        """
        Adds a raster to the weighted layers list.
        Looks for a coressponding npz in the raster folder.
        Calls _loadweighted_layer
        """
        self.dialog.openRasterFile(self.projectpath)
        if self.dialog.exec_() == 1 and self.dialog.selectedFiles():
            path, file = os.path.split(self.dialog.selectedFiles()[0])
            # We look for a .npz with the same or _tab name in the directory.
            if os.path.isfile(os.path.join(path, os.path.splitext(file)[0] + ".npz")):
                npz = os.path.join(path, os.path.splitext(file)[0] + ".npz")
            elif os.path.isfile(os.path.join(path, os.path.splitext(file)[0] + "_tab.npz")):
                npz = os.path.join(path, os.path.splitext(file)[0] + "_tab.npz")
            else:
                npz = ""
            self._loadweighted_layer(file, path, npz)

    @pyqtSlot()
    def on_addFeatureToolButton_clicked(self):
        """
        Adds a new Landslide feature to the landslideFeatureComboBox.
        """
        self.dialog.openFeatureFile(self.projectpath)
        if self.dialog.exec_() == 1 and self.dialog.selectedFiles():
            file = os.path.normpath(self.dialog.selectedFiles()[0])
            items = [self.ui.landslideFeatureComboBox.itemText(
                i) for i in range(self.ui.landslideFeatureComboBox.count())]
            if file and file not in items:
                self.ui.landslideFeatureComboBox.insertItem(0, file)
                self.ui.landslideFeatureComboBox.setCurrentIndex(0)

    @pyqtSlot()
    def on_updatePushButton_clicked(self):
        """
        Checks inputs, sets up the thread for analysis and then starts it.
        """
        if self._validateinputs():
            inputs = self._getinputs()
            self.thread = QThread()
            self.worker = ModelBuilder_calc(
                self.projectpath,
                inputs,
                self.spatref,
                self.axes_roc,
                self.canvas_roc)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.progressSignal.connect(self.updateProgressBar)
            self.worker.dataSignal.connect(self.updateuiwithresults)
            self.worker.finishSignal.connect(self.done)
            self.worker.expressionErrorSignal.connect(self.doneOnError)
            self.thread.start()
            self.ui.progressBar.setValue(0)
            self.ui.updatePushButton.setEnabled(False)

    def _validateinputs(self):
        """
        Gets called by on_updatePushButton_clicked.
        Checks if the inputs are sufficient to start the calculation.
        Lets the user know what is wrong.
        """
        validation = True
        if not os.path.isfile(self.ui.landslideFeatureComboBox.currentText()):  # Check inventory
            logging.error(self.tr("Landslide Inventory missing."))
            self.ui.addFeatureToolButton.setStyleSheet("background-color: rgb(255, 0, 0)")
            QTimer.singleShot(500, lambda: self.ui.addFeatureToolButton.setStyleSheet(""))
            validation = False
        existingmodelnames = []  # Check model name
        for i in range(self.ui.modelsTreeWidget.topLevelItemCount()):
            existingmodelnames.append(self.ui.modelsTreeWidget.topLevelItem(i).text(0))
        if (self.ui.modelNameLineEdit.text() == "" or
                self.ui.modelNameLineEdit.text() in existingmodelnames):
            logging.error(self.tr("Model Name already in use or invalid."))
            self.ui.modelNameLineEdit.setStyleSheet("background-color: rgb(255, 0, 0)")
            QTimer.singleShot(500, lambda: self.ui.modelNameLineEdit.setStyleSheet(""))
            validation = False
        if self.ui.modelLayerTreeWidget.invisibleRootItem().childCount() == 0:  # Check rasters
            logging.error(self.tr("No layers selected."))
            self.ui.addtoModelLayerToolButton.setStyleSheet("background-color: rgb(255, 0, 0)")
            QTimer.singleShot(500, lambda: self.ui.addtoModelLayerToolButton.setStyleSheet(""))
            validation = False
        if (self.advanced.ui.predefinedSubsamplingCheckBox.isChecked() and  # Check subsamples
                not os.path.isdir(self.advanced.ui.subsamplesLocationLineEdit.text())):
            logging.error(self.tr("No Predefined Subsamples selected."))
            self.advanced.ui.subsamplesLocationLineEdit.setStyleSheet(
                "background-color: rgb(255, 0, 0)")
            QTimer.singleShot(
                500, lambda: self.advanced.ui.subsamplesLocationLineEdit.setStyleSheet(""))
            validation = False
        return validation

    def _getinputs(self):
        """
        Gets called by on_updatePushButton_clicked.
        Gathers information from the ui to start the calculation
        """
        if self.advanced.ui.onTheFlySubsamplingCheckBox.isChecked():  # On-the-fly
            analysistype = 1
            subsamplelocation = ""
            samplesize = int(self.advanced.ui.sampleSizeLineEdit.text())
            samplecount = self.advanced.ui.numberResamplesSpinBox.value()
        elif self.advanced.ui.predefinedSubsamplingCheckBox.isChecked():  # Predefined Samples
            analysistype = 2
            subsamplelocation = self.advanced.ui.subsamplesLocationLineEdit.text()
            samplecount = 0
            for file in os.listdir(subsamplelocation):
                if file.endswith((".shp", ".kml", ".geojson")):
                    samplecount+=1
            samplesize = 100

        else:  # Single sample
            analysistype = 3
            subsamplelocation = ""
            samplesize = 100
            samplecount = 1
            self.ui.progressBar.setRange(0,0)
        featurepath = self.ui.landslideFeatureComboBox.currentText()
        modelname = self.ui.modelNameLineEdit.text()
        params_list = []
        expression = self.ui.expressionTextEdit.toPlainText()
        itemcount = self.ui.modelLayerTreeWidget.invisibleRootItem().childCount()
        for i in range(itemcount):
            item = self.ui.modelLayerTreeWidget.topLevelItem(i)
            path = self.modelsmanager.treeContent[hash(str(item))]['Source']
            params_list.append(path)
        inputs = (params_list, featurepath, samplecount, samplesize,
                  subsamplelocation, analysistype, modelname, expression)
        return inputs

    def updateProgressBar(self, progress: int):
        """
        Gets called from the calc Thread and updates the progressbar
        """
        self.ui.progressBar.setValue(progress)

    def updateuiwithresults(self, fullpath):
        """
        Gets called when the calc Thread finishes.
        Calls _loadmodels with the new models results and
        """
        path, file = os.path.split(fullpath)
        self._loadmodels(file, path, Qt.Checked)
        logging.info(self.tr("Model {} created.").format(fullpath))

    def done(self):
        """
        Gets called when the calc Thread finishes.
        Quits thread and updates progressbar to 100 to tell user that we are done.
        """
        self.thread.quit()
        self.ui.updatePushButton.setEnabled(True)
        self.ui.progressBar.setRange(0, 100)
        self.ui.progressBar.setValue(100)

    def doneOnError(self):
        """
        Gets called when the calc Thread emit an expressionErrorSignal.
        Quits thread and updates progressbar to 100 and tells the user something went wrong.
        """
        self.thread.quit()
        self.ui.updatePushButton.setEnabled(True)
        self.ui.progressBar.setRange(0, 100)
        self.ui.progressBar.setValue(0)
        QMessageBox.warning(self, "Expression Error!", "Invalid expression encountered!")

