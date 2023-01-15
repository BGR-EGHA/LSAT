# -*- coding: utf-8 -*-

from osgeo import gdal, ogr, osr, gdalconst
import sys
import os
import math
import time
import numpy as np
from openpyxl import Workbook
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import logging

from core.libs.GDAL_Libs.Layers import Raster, Feature, RasterLayer
from core.uis.ResultViewer_ui.plotViewer_ui import Ui_GraphicViewer

if os.name == "nt":
    prop = matplotlib.font_manager.FontProperties(fname="C:\\Windows\\Fonts\\Msyh.ttc")
else:  # ubuntu
    prop = matplotlib.font_manager.FontProperties(
        fname="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")


class PlotFunctions(QObject):
    """
    SinglePlot and PlotViewer are similar, this class bundles some of their shared functions
    """
    def getLabels(result):
        """
        This method returns the rasters values to add as label to the Ticks at the X-Axis.
        If it does not detect any it will inform the user and use integers starting at 1.
        """
        raster = Raster(result["source"][0])
        if raster.rat is not None:
            rattable = raster.rat2array()
            labels = rattable.dtype.names
            if "VALUE" in labels:
                labels = rattable["VALUE"].tolist()
                if raster.nodata in labels:
                    labels.remove(raster.nodata)
                # If all are floats with .0 we convert to int to ditch the extra digits
                if (all(isinstance(label, float) for label in labels) and
                        all(label.is_integer() for label in labels)):
                    labels = list(map(int, labels))
                return labels
            else:
                logging.warning(self.tr("RAT of {} lacks 'VALUE'.").format(result['source'][0]))
        else:
            logging.warning(
                self.tr("No Raster Attribute Table found in {}.").format(
                    result['source'][0]))
        # if we can't get the info we just count the values
        labels = list(range(1, len(result["tab"]) + 1))
        return labels

    def addWidgets(self):
        """
        Adds two Comboboxes to the toolbar: One to pick the plot type and one to pick the ROC type.
        """
        label = QLabel(self.tr("Plot type:"))
        self.ui.toolBar.addWidget(label)
        self.plotCombo = QComboBox()
        self.plotCombo.addItems([self.tr("Boxplot"), self.tr("Violinplot")])
        self.ui.toolBar.addWidget(self.plotCombo)
        self.plotCombo.activated.connect(self.updatePlots)

        label = QLabel(self.tr("Show ROC as:"))
        self.ui.toolBar.addWidget(label)
        self.propertyCombo = QComboBox()
        self.propertyCombo.addItems([self.tr("All"), self.tr("range")])
        self.ui.toolBar.addWidget(self.propertyCombo)
        self.propertyCombo.activated.connect(self.updatePlots)


class SinglePlot(QMainWindow):
    def __init__(self, plot, result, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_GraphicViewer()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(':/icons/Icons/Chart_Bar_Big.png'))

        self.plot = plot
        self.result = result
        labels = PlotFunctions.getLabels(result)
        PlotFunctions.addWidgets(self)
        self.labels = labels  # For use in signal connected functions
        self.resultTable = result["tab"]
        self.keylist = []
        for key in result:
            self.keylist.append(key)

        if len(self.keylist) <= 6:
            # Only one sample
            self.multiplesamples = False
            self.propertyCombo.setEnabled(False)
            self.plotCombo.setEnabled(False)
        else:
            self.multiplesamples = True
            if self.plot == 0:
                self.propertyCombo.setEnabled(False)
                self.plotCombo.setEnabled(False)
            elif self.plot == 1 or self.plot == 2:
                self.propertyCombo.setEnabled(False)
                self.plotCombo.setEnabled(True)
            elif self.plot == 3:
                self.propertyCombo.setEnabled(True)
                self.plotCombo.setEnabled(False)

        if self.plot == 0:
            self.setWindowTitle(self.tr("Plot 1: Class pixel distribution"))
        elif self.plot == 1:
            self.setWindowTitle(self.tr("Plot 2: Landslide pixel distribution in classes"))
        elif self.plot == 2:
            self.setWindowTitle(self.tr("Plot 3: Weight distribution"))
        elif self.plot == 3:
            self.setWindowTitle(self.tr("Plot 4: Receiver Operating Characteristics (ROC) curve"))

        self.fig = Figure(facecolor='white')
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
        self.ui.mainGridLayout.addWidget(self.canvas)
        self.mpl_toolbar = NavigationToolbar(self.canvas, self)
        self.ui.mainGridLayout.addWidget(self.mpl_toolbar)

        if self.plot == 0:
            self.plot1(labels)
        elif self.plot == 1:
            self.plot2(labels)
        elif self.plot == 2:
            self.plot3(labels)
        elif self.plot == 3:
            self.plot4()

    def updatePlots(self):
        if self.plot == 1:
            self.plot2(self.labels)
        elif self.plot == 2:
            self.plot3(self.labels)
        elif self.plot == 3:
            self.plot4()

    def plot1(self, labels):
        """
        Plots the plot No. 1 - Class pixel distribution
        """
        self.ax.clear()
        self.ax.set_xlabel(self.tr('Classes'), fontproperties=prop)
        self.ax.set_ylabel(self.tr('Class pixel count'), fontproperties=prop)
        self.ax.set_ylim(0, self.resultTable['Class'].max() * 1.1)
        self.ax.set_xlim(0, len(self.resultTable) + 1)
        y = []
        x = []
        for i in range(len(self.resultTable)):
            y.append(self.resultTable['Class'][i])
            x.append(i + 1)
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(labels)
        self.ax.bar(x, y, align='center')
        self.canvas.draw()
        self.canvas.flush_events()
        self.fig.tight_layout()

    def plot2(self, labels):
        """
        Plots the plot No. 2 - Landslide pixel distribution in classes
        """
        self.ax.clear()
        self.ax.set_xlabel(self.tr('Classes'), fontproperties=prop)
        self.ax.set_ylabel(self.tr('Landslide pixel count'), fontproperties=prop)
        self.ax.set_xlim(0, len(self.resultTable) + 1)
        if not self.multiplesamples:
            self.ax.set_ylim(0, self.resultTable['Landslides'].max() * 1.1)
            y = []
            x = []
            for i in range(len(self.resultTable)):
                y.append(self.resultTable['Landslides'][i])
                x.append(i + 1)
            self.ax.set_xticks(x)
            self.ax.set_xticklabels(labels)
            self.ax.bar(x, y, align='center')
        else:
            data = []
            for i in range(len(self.resultTable)):
                data.append(self.result['landslides'][i])
            if self.plotCombo.currentText() == self.tr("Boxplot"):
                box = self.ax.boxplot(data, notch=False, patch_artist=True)
            elif self.plotCombo.currentText() == self.tr("Violinplot"):
                violin = self.ax.violinplot(data, showmeans=False, showmedians=True)
            self.ax.set_xticks(range(1, len(self.resultTable) + 1))
            self.ax.set_xticklabels(labels)
        self.canvas.draw()
        self.canvas.flush_events()
        self.fig.tight_layout()

    def plot3(self, labels):
        """
        Plot the plot No. 3 - Weight distribution and their standard deviations
        """
        self.ax.clear()
        self.ax.set_xlabel(self.tr('Classes'), fontproperties=prop)
        self.ax.set_ylabel(self.tr('Total weight'), fontproperties=prop)
        self.ax.set_xlim(0, len(self.resultTable) + 1)
        if not self.multiplesamples:
            y = []
            x = []
            Std = []
            colour = []
            for i in range(len(self.resultTable)):
                y.append(self.resultTable['Weight'][i])
                x.append(i + 1)
                Std.append(math.sqrt(self.resultTable['Variance'][i]))
                if self.resultTable['Weight'][i] <= 0.0 and self.resultTable['Weight'][i] >= -1.0:
                    a = 'y'
                elif self.resultTable['Weight'][i] > 0.0 and self.resultTable['Weight'][i] <= 1.0:
                    a = 'y'
                elif self.resultTable['Weight'][i] < -1.0:
                    a = 'r'
                else:
                    a = 'g'
                colour.append(a)
            self.ax.set_xticks(x)
            self.ax.set_xticklabels(labels)
            self.ax.bar(x, y, color=colour, yerr=Std, align='center')
        else:
            data = []
            colors = []
            for i in range(len(self.resultTable)):
                data.append(self.result['weight'][i])
                if self.resultTable['Weight'][i] <= 0.0 and self.resultTable['Weight'][i] >= -1.0:
                    a = 'y'
                elif self.resultTable['Weight'][i] > 0.0 and self.resultTable['Weight'][i] <= 1.0:
                    a = 'y'
                elif self.resultTable['Weight'][i] < -1.0:
                    a = 'r'
                else:
                    a = 'g'
                colors.append(a)
            if self.plotCombo.currentText() == self.tr("Boxplot"):
                box = self.ax.boxplot(data, notch=False, patch_artist=True)
                for patch, color in zip(box['boxes'], colors):
                    patch.set_facecolor(color)
            elif self.plotCombo.currentText() == self.tr("Violinplot"):
                violin = self.ax.violinplot(data, showmeans=False, showmedians=True)
                for patch, color in zip(violin['bodies'], colors):
                    patch.set_facecolor(color)
            self.ax.set_xticks(range(1, len(self.resultTable) + 1))
            self.ax.set_xticklabels(labels)
        self.canvas.draw()
        self.canvas.flush_events()
        self.fig.tight_layout()

    def plot4(self):
        """
        Plot the plot No. 4 - ROC curve(s) of the model compared to average model with AUC = 0.5
        """
        self.ax.clear()
        self.ax.set_xlabel(self.tr('False Positive Rate (1-Specificity)'),
                           fontproperties=prop)
        self.ax.set_ylabel(self.tr('True Positive Rate (Sensitivity)'),
                           fontproperties=prop)
        x0 = [0.0, 1.0]
        y0 = [0.0, 1.0]
        self.ax.set_ylim(0, 1.0)
        self.ax.set_xlim(0, 1.0)
        if not self.multiplesamples:
            x = self.result['roc_x']
            y = self.result['roc_y']
            auc = self.result['auc']
            self.ax.plot(x, y, label=self.tr("AUC: %.2f") % (float(auc)), color="red", linewidth=2)
        else:
            sortTable = np.sort(self.resultTable, order=['Weight'])[::-1]
            x = [0.0]
            y = [0.0]
            for i in range(len(self.resultTable)):
                x.append(x[i] + float(sortTable['Class'][i]) / float(sortTable['Class'].sum()))
                y.append(y[i] + float(sortTable['Landslides'][i]) /
                         float(sortTable['Landslides'].sum()))
            unique = np.unique(self.result["roc_x"].ravel())
            y_all = []
            for i in range(len(self.result["roc_x"])):
                new_y = np.interp(unique, self.result["roc_x"][i], self.result["roc_y"][i])
                y_all.append(new_y)
            max_y = []
            min_y = []
            mean_y = []
            median_y = []
            for i in np.transpose(y_all):
                min_y.append(min(i))
                max_y.append(max(i))
                mean_y.append(np.mean(i))
                median_y.append(np.median(i))
            auc = []
            for i in range(len(unique) - 1):
                auc.append((unique[i + 1] - unique[i]) * mean_y[i + 1] - (
                    (unique[i + 1] - unique[i]) * (mean_y[i + 1] - mean_y[i]) / 2))
            if self.propertyCombo.currentText() == "All":
                for i in range(len(self.result['roc_x'])):
                    self.ax.plot(
                        self.result['roc_x'][i],
                        self.result['roc_y'][i],
                        color="black",
                        linewidth=0.5)
                self.ax.plot(
                    unique,
                    mean_y,
                    color="red",
                    linewidth=2,
                    label=self.tr("mean: %.2f") %
                    (sum(auc)))
            else:
                self.ax.fill_between(unique, min_y, max_y, color="grey", linestyle="--", alpha=0.5,
                                     label=self.tr("range: %.2f - %.2f") % (
                                         self.result['auc'].max(), self.result['auc'].min()))
                self.ax.plot(unique, mean_y, color="red", linewidth=2,
                             label=self.tr("mean: %.2f") % (sum(auc)))
        self.ax.plot(x0, y0, label=self.tr("prior: 0.5"), color="blue")
        self.ax.legend(loc="lower right")
        self.canvas.draw()
        self.canvas.flush_events()
        self.fig.tight_layout()


class PlotViewer(QMainWindow):
    def __init__(self, layerName, result, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_GraphicViewer()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(':/icons/Icons/Chart_Bar_Big.png'))

        self.result = result
        labels = PlotFunctions.getLabels(result)
        self.labels = labels  # For use in updatePlots
        PlotFunctions.addWidgets(self)
        self.resultTable = result['tab']
        self.keylist = []
        for key in result:
            self.keylist.append(key)

        if len(self.keylist) <= 6:
            # only one feature dataset
            self.plotCombo.setEnabled(False)
            self.propertyCombo.setEnabled(False)
            self.multiplesamples = False
        else:
            self.multiplesamples = True

        # Set figures

        # Histogram class
        self.fig = Figure(facecolor='white')
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(221)
        self.ui.mainGridLayout.addWidget(self.canvas)
        self.ax.set_xlabel(self.tr("Class"))
        self.ax.set_ylabel(self.tr("Class pixel count"))
        self.mpl_toolbar = NavigationToolbar(self.canvas, self)
        self.ui.mainGridLayout.addWidget(self.mpl_toolbar)

        # Histogram Landslides
        self.ax2 = self.fig.add_subplot(222)
        self.ax2.set_xlabel(self.tr("Class"))
        self.ax2.set_ylabel(self.tr("Landslide pixel count"))

        # Weights
        self.ax3 = self.fig.add_subplot(223)
        self.ax3.set_xlabel(self.tr("Class"))
        self.ax3.set_ylabel(self.tr("Weight"))

        # ROC curve
        self.ax4 = self.fig.add_subplot(224)
        self.ax4.set_xlabel(self.tr("FPR (1 - Specificity)"))
        self.ax4.set_ylabel(self.tr("TPR (Sensitivity)"))

        cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.fig.tight_layout()

        self.plot1(labels)
        self.plot2(labels)
        self.plot3(labels)
        self.plot4()

    def updatePlots(self):
        self.plot2(self.labels)
        self.plot3(self.labels)
        self.plot4()

    def onclick(self, event):
        for i, plot in enumerate([self.ax, self.ax2, self.ax3, self.ax4, ]):
            if plot == event.inaxes and event.dblclick:
                self.singlePlot = SinglePlot(i, self.result)
                self.singlePlot.show()

    def plot1(self, labels):
        """
        Plots the plot No. 1 illustating the class diunicodeibution
        """
        self.ax.clear()
        self.ax.set_xlabel(self.tr('Classes'), fontproperties=prop)
        self.ax.set_ylabel(self.tr('Class pixel count'), fontproperties=prop)
        self.ax.set_ylim(0, self.resultTable['Class'].max() + self.resultTable['Class'].max() / 10)
        self.ax.set_xlim(0, len(self.resultTable) + 1)
        y = []
        x = []
        for i in range(len(self.resultTable)):
            y.append(self.resultTable['Class'][i])
            x.append(i + 1)
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(labels)
        self.ax.bar(x, y, align='center')
        self.canvas.draw()
        self.canvas.flush_events()
        self.fig.tight_layout()

    def plot2(self, labels):
        """
        Plots the plot No. 2 - landslide pixel distribution in classes
        """
        self.ax2.clear()
        self.ax2.set_xlabel(self.tr('Classes'), fontproperties=prop)
        self.ax2.set_ylabel(self.tr('Landslide pixel count'), fontproperties=prop)
        self.ax2.set_xlim(0, len(self.resultTable) + 1)
        if not self.multiplesamples:
            # One feature dataset
            self.ax2.set_ylim(0, self.resultTable['Landslides'].max(
            ) + int(self.resultTable['Landslides'].max() / 10))
            y = []
            x = []
            for i in range(len(self.resultTable)):
                y.append(self.resultTable['Landslides'][i])
                x.append(i + 1)
            self.ax2.set_xticks(x)
            self.ax2.set_xticklabels(labels)
            self.ax2.bar(x, y, align='center')
        else:
            data = []
            for i in range(len(self.resultTable)):
                data.append(self.result['landslides'][i])
            if self.plotCombo.currentText() == self.tr("Boxplot"):
                box = self.ax2.boxplot(data, notch=False, patch_artist=True)
            elif self.plotCombo.currentText() == self.tr("Violinplot"):
                violin = self.ax2.violinplot(data, showmedians=True)
            self.ax2.set_xticks(range(1, len(self.resultTable) + 1))
            self.ax2.set_xticklabels(labels)
        self.canvas.draw()
        self.canvas.flush_events()
        self.fig.tight_layout()

    def plot3(self, labels):
        """
        Plot the plot No. 3 illustaring the weights and their standard deviations
        """
        self.ax3.clear()
        self.ax3.set_xlabel(self.tr('Classes'), fontproperties=prop)
        self.ax3.set_ylabel(self.tr('Total weight'), fontproperties=prop)
        if not self.multiplesamples:
            self.ax3.set_xlim(0, len(self.resultTable) + 1)
            y = []
            x = []
            Std = []
            colour = []
            for i in range(len(self.resultTable)):
                y.append(self.resultTable['Weight'][i])
                x.append(i + 1)
                Std.append(math.sqrt(self.resultTable['Variance'][i]))
                if self.resultTable['Weight'][i] <= 0.0 and self.resultTable['Weight'][i] >= -1.0:
                    a = 'y'
                elif self.resultTable['Weight'][i] > 0.0 and self.resultTable['Weight'][i] <= 1.0:
                    a = 'y'
                elif self.resultTable['Weight'][i] < -1.0:
                    a = 'r'
                else:
                    a = 'g'
                colour.append(a)
            self.ax3.set_xticks(x)
            self.ax3.set_xticklabels(labels)
            self.ax3.bar(x, y, color=colour, yerr=Std, align='center')
        else:
            self.ax3.set_xlim(0, len(self.resultTable) + 1)
            data = []
            colors = []
            for i in range(len(self.resultTable)):
                data.append(self.result['weight'][i])

                if self.resultTable['Weight'][i] <= 0.0 and self.resultTable['Weight'][i] >= -1.0:
                    a = 'y'
                elif self.resultTable['Weight'][i] > 0.0 and self.resultTable['Weight'][i] <= 1.0:
                    a = 'y'
                elif self.resultTable['Weight'][i] < -1.0:
                    a = 'r'
                else:
                    a = 'g'
                colors.append(a)
            if self.plotCombo.currentText() == self.tr("Boxplot"):
                box = self.ax3.boxplot(data, notch=False, patch_artist=True)
                for patch, color in zip(box['boxes'], colors):
                    patch.set_facecolor(color)
            elif self.plotCombo.currentText() == self.tr("Violinplot"):
                violin = self.ax3.violinplot(data, showmeans=False, showmedians=True)
                for patch, color in zip(violin['bodies'], colors):
                    patch.set_facecolor(color)
            self.ax3.set_xticks(range(1, len(self.resultTable) + 1))
            self.ax3.set_xticklabels(labels)
        self.canvas.draw()
        self.canvas.flush_events()
        self.fig.tight_layout()

    def plot4(self):
        """
        Plots the ROC curve(s) of the model realisation(s) compared to average model with AUC = 0.5
        """
        self.ax4.clear()
        self.ax4.set_xlabel(self.tr('False Positive Rate (1-Specificity)'),
                            fontproperties=prop)
        self.ax4.set_ylabel(self.tr('True Positive Rate (Sensitivity)'),
                            fontproperties=prop)
        x0 = [0.0, 1.0]
        y0 = [0.0, 1.0]
        self.ax4.set_ylim(0, 1.0)
        self.ax4.set_xlim(0, 1.0)
        if not self.multiplesamples:
            x = self.result['roc_x']
            y = self.result['roc_y']
            auc = self.result['auc']
            self.ax4.plot(x, y, label=self.tr("AUC: %.2f") % (float(auc)), color="red", linewidth=2)
        else:
            sortTable = np.sort(self.resultTable, order=['Weight'])[::-1]
            x = [0.0]
            y = [0.0]
            for i in range(len(self.resultTable)):
                x.append(x[i] + float(sortTable['Class'][i]) / float(sortTable['Class'].sum()))
                y.append(y[i] + float(sortTable['Landslides'][i]) /
                         float(sortTable['Landslides'].sum()))

            unique = np.unique(self.result["roc_x"].ravel())
            y_all = []
            for i in range(len(self.result["roc_x"])):
                new_y = np.interp(unique, self.result["roc_x"][i], self.result["roc_y"][i])
                y_all.append(new_y)
            max_y = []
            min_y = []
            mean_y = []
            median_y = []
            for i in np.transpose(y_all):
                min_y.append(min(i))
                max_y.append(max(i))
                mean_y.append(np.mean(i))
                median_y.append(np.median(i))
            auc = []
            for i in range(len(unique) - 1):
                auc.append((unique[i + 1] - unique[i]) * mean_y[i + 1] - (
                    (unique[i + 1] - unique[i]) * (mean_y[i + 1] - mean_y[i]) / 2))

            if self.propertyCombo.currentText() == "All":
                for i in range(len(self.result['roc_x'])):
                    self.ax4.plot(
                        self.result['roc_x'][i],
                        self.result['roc_y'][i],
                        color="black",
                        linewidth=0.5)
                self.ax4.plot(
                    unique,
                    mean_y,
                    color="red",
                    linewidth=2,
                    label=self.tr("mean: %.2f") %
                    (sum(auc)))
            else:
                self.ax4.fill_between(unique, min_y, max_y, color="grey", linestyle="--", alpha=0.5,
                                      label=self.tr("range: %.2f - %.2f") % (
                                          self.result['auc'].max(), self.result['auc'].min()))
                self.ax4.plot(unique, mean_y, color="red", linewidth=2,
                              label=self.tr("mean: %.2f") % (sum(auc)))
        self.ax4.plot(x0, y0, label=self.tr("prior: 0.5"), color="blue")
        self.ax4.legend(loc="lower right")
        self.canvas.draw()
        self.canvas.flush_events()
        self.fig.tight_layout()
