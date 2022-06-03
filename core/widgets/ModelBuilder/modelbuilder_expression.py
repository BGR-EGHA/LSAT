#-*- coding: utf-8 -*-

from osgeo import gdal, ogr, osr, gdalconst
import os, sys, math, time
import numpy as np
import logging 
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from core.uis.ModelBuilder_ui.ExpressionBuilder_ui import Ui_ExpressionBuilder
from core.libs.GDAL_Libs.Layers import Raster

class ExpressionBuilder(QMainWindow):

    expressionSignal = pyqtSignal(str)
    def __init__(self, expression, layers, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_ExpressionBuilder()
        self.ui.setupUi(self)
        self.setWindowTitle(self.tr("Build Expression"))
        self.ui.operatorsComboBox.activated.connect(self.updateOperatorsList)

        self.layers = layers
        self.ui.expressionTextEdit.setText(expression)
        self.layersListModel = ListModel(self.layers)
        self.ui.layersListView.setModel(self.layersListModel)
               
        self.operators = {"Trigonometric" : ["np.sin()", "np.cos()", "np.tan()",
                                      "np.arcsin()", "np.arccos()", "np.arctan()",
                                      "np.arctan2()", "np.degrees()", "np.radians()",
                                      "np.deg2grad()", "np.rad2deg()"],
                     "Hyperbolic" : ["np.sinh()", "np.cosh()", "np.tanh()",
                                     "np.arcsinh()", "np.arccosh()", "np.arctanh()"],
                          "Rounding" : ["np.around()", "np.round_()", "np.rint()",
                                        "np.fix()", "np.floor()", "np.ceil()", "np.trunc()"],
                          "Sums, products, differences" : ["np.prod()", "np.sum()", "np.nanprod()",
                                                           "np.nansum()", "np.cumsum()", "np.cumprod()",
                                                           "np.nancumsum()", "np.nancumprod()", "np.diff()",
                                                           "np.ediff1d()", "np.gradient()", "np.cross()",
                                                           "np.trapz()"],
                          "Exponents and logarithms" : ["np.exp()", "np.expm1()", "np.exp2()",
                                                       "np.log()", "np.log10()", "np.log2()",
                                                       "np.log1p()", "np.logaddexp()", "np.logaddexp2()"],
                          "Arithmetic" : ["np.add()", "np.reciprocal()", "np.positive()", "np.negative()",
                                          "np.multiply()", "np.divide()", "np.power()", "np.substract()",
                                          "np.true_divide()", "np.floor_divide()", "np.float_power()"] }

        self.updateOperatorsList()


   
    def updateOperatorsList(self):
        """
        Updates the operators list based on the selection
        in the combo box anytime the combo box was activated.
        """
        keys = self.operators.keys()
        if self.ui.operatorsComboBox.currentText() in keys:
            operators = []
            for value in self.operators[str(self.ui.operatorsComboBox.currentText())]:
                operators.append(value)
            self.operatorsListModel = ListModel(operators)
            self.ui.operatorsListView.setModel(self.operatorsListModel)
        else:
            operators = []
            for key in keys:
                for value in self.operators[key]:
                    operators.append(value)
                    self.operatorsListModel = ListModel(operators)
                    self.ui.operatorsListView.setModel(self.operatorsListModel)

    @pyqtSlot(QModelIndex)
    def on_operatorsListView_doubleClicked(self, index):
        self.addStringtoTextEdit(str(index.data()))

    @pyqtSlot(QModelIndex)
    def on_layersListView_doubleClicked(self, index):
        self.addStringtoTextEdit(str(index.data()).replace(".", "").replace(" ",""))

    def addStringtoTextEdit(self, str2add: str):
        """
        Gets called by toolButtons and clicking on values in tables.
        Adds the corresponding text to the textEdit at the cursor position.
        Updates to the cursor position.
        """
        cursor = self.ui.expressionTextEdit.textCursor()
        pos = cursor.position()
        text = self.ui.expressionTextEdit.toPlainText()
        newText = text[:pos] + str2add + text[pos:]
        self.ui.expressionTextEdit.setPlainText(newText)
        cursor.setPosition(pos + len(str2add))
        self.ui.expressionTextEdit.setTextCursor(cursor)

    @pyqtSlot()
    def on_applyPushButton_clicked(self):
        self.calculate()

    @pyqtSlot()
    def on_cancelPushButton_clicked(self):
        self.close()
        return
    

    def calculate(self):
        expression = self.ui.expressionTextEdit.toPlainText()
        self.expressionSignal.emit(str(expression))
        self.close()



class ListModel(QAbstractListModel):
    def __init__(self, datain, parent=None, *args):
        """
         datain: a list of lists
        """
        QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = datain

    def rowCount(self, parent):
        return len(self.arraydata)

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        if role != Qt.DisplayRole:
            return QVariant()

        return QVariant(self.arraydata[index.row()])
                  


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myapp = Calculator()
    myapp.show()
    sys.exit(app.exec_())



