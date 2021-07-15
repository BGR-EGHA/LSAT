# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)

class Ui_Results(object):
    def setupUi(self, ResultsWindow):
        ResultsWindow.setObjectName(_fromUtf8("Results"))
        ResultsWindow.resize(972, 661)
        icon = QIcon()
        icon.addPixmap(QPixmap(_fromUtf8("..\Images\WofE.png")), QIcon.Normal, QIcon.Off)
        ResultsWindow.setWindowIcon(icon)

        self.gridLayoutWidgetResultsWindow = QWidget(ResultsWindow)
        self.gridLayoutWidgetResultsWindow.setGeometry(QRect(2, 3, 968, 648))
        self.gridLayoutWidgetResultsWindow.setObjectName(_fromUtf8("gridLayoutWidgetResultsWindow"))

        self.gridLayoutResultsWindow = QGridLayout(self.gridLayoutWidgetResultsWindow)
        self.gridLayoutResultsWindow.setObjectName(_fromUtf8("gridLayoutResultsWindow "))
        
        self.tabWidget = QTabWidget(self.gridLayoutWidgetResultsWindow)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        
        self.tableTab = QWidget()
        self.tableTab.setObjectName(_fromUtf8("tableTab"))
        
        self.gridLayoutWidgetTableTab = QWidget(self.tableTab)
        
        self.gridLayoutWidgetTableTab.setGeometry(QRect(-1, 2, 961, 620))
        self.gridLayoutWidgetTableTab.setObjectName(_fromUtf8("gridLayoutWidgetTableTab"))
        
        self.gridLayoutTableTab = QGridLayout(self.gridLayoutWidgetTableTab)
        self.gridLayoutTableTab.setObjectName(_fromUtf8("gridLayoutTableTab"))
        
        self.verticalLayoutTableTab = QVBoxLayout()
        self.verticalLayoutTableTab.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.verticalLayoutTableTab.setSpacing(6)
        self.verticalLayoutTableTab.setObjectName(_fromUtf8("verticalLayoutTableTab"))
        


        self.tabWidget.addTab(self.tableTab, _fromUtf8(""))

        self.Graphics = QWidget()
        self.Graphics.setObjectName(_fromUtf8("Graphics"))
        self.gridLayoutWidget_3 = QWidget(self.Graphics)
        self.gridLayoutWidget_3.setGeometry(QtCore.QRect(0, 1, 963, 623))
        self.gridLayoutWidget_3.setObjectName(_fromUtf8("gridLayoutWidget_3"))
        self.gridLayoutGraphics = QGridLayout(self.gridLayoutWidget_3)
        self.gridLayoutGraphics.setObjectName(_fromUtf8("gridLayoutGraphics"))
        self.tabWidgetGraphics = QTabWidget(self.gridLayoutWidget_3)
        self.tabWidgetGraphics.setObjectName(_fromUtf8("tabWidgetGraphics"))
        self.tabHistogramClass = QWidget()
        self.tabHistogramClass.setObjectName(_fromUtf8("tabHistogramClass"))
        self.gridLayoutWidget_4 = QWidget(self.tabHistogramClass)
        self.gridLayoutWidget_4.setGeometry(QtCore.QRect(0, 2, 965, 598))
        self.gridLayoutWidget_4.setObjectName(_fromUtf8("gridLayoutWidget_4"))
        self.gridLayoutHistogramClass = QGridLayout(self.gridLayoutWidget_4)
        self.gridLayoutHistogramClass.setObjectName(_fromUtf8("gridLayoutHistogramClass"))
        self.frameHistogramClass = QFrame(self.gridLayoutWidget_4)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frameHistogramClass.sizePolicy().hasHeightForWidth())

        self.frameHistogramClass.setSizePolicy(sizePolicy)
        self.frameHistogramClass.setFrameShape(QFrame.StyledPanel)
        self.frameHistogramClass.setFrameShadow(QFrame.Raised)
        self.frameHistogramClass.setObjectName(_fromUtf8("frameHistogramClass"))

        self.gridLayoutHistogramClass.addWidget(self.frameHistogramClass, 0, 0, 0, 0)
        self.tabWidgetGraphics.addTab(self.tabHistogramClass, _fromUtf8(""))

        self.tabHistogramLandslides = QWidget()
        self.tabHistogramLandslides.setObjectName(_fromUtf8("tabHistogramLandslides"))
        self.gridLayoutWidget_5 = QWidget(self.tabHistogramLandslides)
        self.gridLayoutWidget_5.setGeometry(QRect(-2, -1, 962, 602))
        self.gridLayoutWidget_5.setObjectName(_fromUtf8("gridLayoutWidget_5"))

        self.gridLayoutHistogramLandslides = QGridLayout(self.gridLayoutWidget_5)
        self.gridLayoutHistogramLandslides.setObjectName(_fromUtf8("gridLayoutHistogramLandslides"))

        self.frameHistogramLandslides = QFrame(self.gridLayoutWidget_5)
        self.frameHistogramLandslides.setFrameShape(QFrame.StyledPanel)
        self.frameHistogramLandslides.setFrameShadow(QFrame.Raised)
        self.frameHistogramLandslides.setObjectName(_fromUtf8("frameHistogramLandslides"))
        self.gridLayoutHistogramLandslides.addWidget(self.frameHistogramLandslides, 0, 0, 0, 0)

        self.tabWidgetGraphics.addTab(self.tabHistogramLandslides, _fromUtf8(""))
        self.tabWeights = QWidget()
        self.tabWeights.setObjectName(_fromUtf8("tabWeights"))
        self.gridLayoutWidget_6 = QWidget(self.tabWeights)
        self.gridLayoutWidget_6.setGeometry(QRect(-1, -1, 960, 604))
        self.gridLayoutWidget_6.setObjectName(_fromUtf8("gridLayoutWidget_6"))

        self.gridLayoutWeights = QGridLayout(self.gridLayoutWidget_6)
        self.gridLayoutWeights.setObjectName(_fromUtf8("gridLayoutWeights"))

        self.frameWeights = QFrame(self.gridLayoutWidget_6)
        self.frameWeights.setFrameShape(QFrame.StyledPanel)
        self.frameWeights.setFrameShadow(QFrame.Raised)
        self.frameWeights.setObjectName(_fromUtf8("frameWeights"))
        self.gridLayoutWeights.addWidget(self.frameWeights, 0, 0, 0, 0)
        self.tabWidgetGraphics.addTab(self.tabWeights, _fromUtf8(""))

        self.tabROCCurve = QWidget()
        self.tabROCCurve.setObjectName(_fromUtf8("tabROCCurve"))

        self.gridLayoutWidget_7 = QWidget(self.tabROCCurve)
        self.gridLayoutWidget_7.setGeometry(QtCore.QRect(-1, 0, 960, 596))
        self.gridLayoutWidget_7.setObjectName(_fromUtf8("gridLayoutWidget_7"))

        self.gridLayoutROCCurve = QGridLayout(self.gridLayoutWidget_7)
        self.gridLayoutROCCurve.setObjectName(_fromUtf8("gridLayoutROCCurve"))

        self.frameROCCurve = QFrame(self.gridLayoutWidget_7)
        self.frameROCCurve.setFrameShape(QFrame.StyledPanel)
        self.frameROCCurve.setFrameShadow(QFrame.Raised)
        self.frameROCCurve.setObjectName(_fromUtf8("frameROCCurve"))

        self.gridLayoutROCCurve.addWidget(self.frameROCCurve, 0, 0, 0, 0)
        self.tabWidgetGraphics.addTab(self.tabROCCurve, _fromUtf8(""))
        self.gridLayoutGraphics.addWidget(self.tabWidgetGraphics, 0, 0, 1, 1)
        self.tabWidget.addTab(self.Graphics, _fromUtf8(""))
        self.gridLayoutResultsWindow.addWidget(self.tabWidget, 0, 0, 1, 1)



        self.tableTab.setLayout(self.gridLayoutTableTab)
        self.Graphics.setLayout(self.gridLayoutGraphics)



        self.toolBar = QToolBar(ResultsWindow)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        ResultsWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

        ResultsWindow.setCentralWidget(self.gridLayoutWidgetResultsWindow)




        self.retranslateUi(ResultsWindow)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidgetGraphics.setCurrentIndex(0)
        QMetaObject.connectSlotsByName(ResultsWindow)

        
        ### Set figures

        ## Histogram class
        self.fig = Figure(facecolor = 'white')
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.frameHistogramClass)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("Class")
        self.ax.set_ylabel("Number of pixels")
        self.gridLayoutHistogramClass.addWidget(self.canvas)
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.frameHistogramClass)
        self.gridLayoutHistogramClass.addWidget(self.mpl_toolbar)
        self.tabHistogramClass.setLayout(self.gridLayoutHistogramClass)
        self.fig.tight_layout()
       
        

        ## Histogram Landslides
        self.fig2 = Figure(facecolor = 'white')
        self.canvas2 = FigureCanvas(self.fig2)
        self.canvas2.setParent(self.frameHistogramLandslides)
        self.ax2 = self.fig2.add_subplot(111)
        self.ax2.set_xlabel("Class")
        self.ax2.set_ylabel("Number of pixels")
        self.gridLayoutHistogramLandslides.addWidget(self.canvas2)
        self.mpl_toolbar2 = NavigationToolbar(self.canvas2, self.frameHistogramLandslides)
        self.gridLayoutHistogramLandslides.addWidget(self.mpl_toolbar2)
        self.tabHistogramLandslides.setLayout(self.gridLayoutHistogramLandslides)
        self.fig2.tight_layout()
        
        ## Weights
        self.fig3 = Figure(facecolor = 'white')
        self.canvas3 = FigureCanvas(self.fig3)
        self.canvas3.setParent(self.frameWeights)
        self.ax3 = self.fig3.add_subplot(111)
        self.ax3.set_xlabel("Class")
        self.ax3.set_ylabel("Total weight")
        self.gridLayoutWeights.addWidget(self.canvas3)
        self.mpl_toolbar3 = NavigationToolbar(self.canvas3, self.frameWeights)
        self.gridLayoutWeights.addWidget(self.mpl_toolbar3)
        self.tabWeights.setLayout(self.gridLayoutWeights)
        self.fig3.tight_layout()

        ## ROC curve
        self.fig4 = Figure(facecolor = 'white')
        self.canvas4 = FigureCanvas(self.fig4)
        self.canvas4.setParent(self.frameROCCurve)
        self.ax4 = self.fig4.add_subplot(111)
        self.ax4.set_xlabel("False Positive Rate (1 - Specificity)")
        self.ax4.set_ylabel("True Positive Rate (Sensitivity)")
        self.gridLayoutROCCurve.addWidget(self.canvas4)
        self.mpl_toolbar4 = NavigationToolbar(self.canvas4, self.frameROCCurve)
        self.gridLayoutROCCurve.addWidget(self.mpl_toolbar4)
        self.tabROCCurve.setLayout(self.gridLayoutROCCurve)
        self.fig4.tight_layout()
        

    def retranslateUi(self, ResultsWindow):
        ResultsWindow.setWindowTitle(_translate("ResultsWindow", "Results Window", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tableTab), _translate("ResultsWindow", "Table", None))
        self.tabWidgetGraphics.setTabText(self.tabWidgetGraphics.indexOf(self.tabHistogramClass), _translate("ResultsWindow", "Histogram class", None))
        self.tabWidgetGraphics.setTabText(self.tabWidgetGraphics.indexOf(self.tabHistogramLandslides), _translate("ResultsWindow", "Histogram landslides", None))
        self.tabWidgetGraphics.setTabText(self.tabWidgetGraphics.indexOf(self.tabWeights), _translate("ResultsWindow", "Weights", None))
        self.tabWidgetGraphics.setTabText(self.tabWidgetGraphics.indexOf(self.tabROCCurve), _translate("ResultsWindow", "ROC curve", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Graphics), _translate("ResultsWindow", "Graphics", None))

