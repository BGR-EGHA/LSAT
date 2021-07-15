from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class TableModel(QAbstractTableModel):
    """
    Used to display raster specific information for ANN and LR.
    """

    def __init__(self, indata, parent=None, *args):
        QAbstractTableModel.__init__(self, parent)
        self.indata = indata
        self.header = indata.dtype.names
        self.dtypes = [self.indata.dtype[i] for i in range(len(self.header))]

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return self.indata.shape[0]

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self.header)

    def data(self, index, int_role=Qt.DisplayRole):
        if int_role == Qt.DisplayRole:
            i = index.row()
            j = index.column()
            if "float" in str(self.dtypes[j]):
                return '{:.5f}'.format(self.indata[i][j])
            else:
                return '{0}'.format(self.indata[i][j])
        else:
            return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)


class shared_resultfunc():
    """
    Bundles function used by both ann_resultviewer and resultViewerLogReg_main.py
    """

    def setTopLevelItem(self, index, info, text, tree, tooltip=None):
        """
        index = Row of the Item (0 = top)
        info = Text to display in first column
        text = Text to display in the second column
        tree = the modelTreeWidget object to append to
        tooltip = Adds a tooltip to the second column, None by default.
        Both info and text can be None -> Empty column
        """
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        tree.addTopLevelItem(QTreeWidgetItem(index))
        item = tree.topLevelItem(index)
        item.setText(0, info)
        item.setText(1, text)
        item.setFont(0, font)
        if tooltip:
            item.setToolTip(1, tooltip)

    def setChildItem(self, index_parent, index_child, info, text, tree, tooltip=None):
        """
        index_parent = Row of the parent Item (0 = top)
        index_child = Row of the child under the parent
        info = Text to display in first column
        text = Text to display in the second column
        tree = the modelTreeWidget object to append to
        tooltip = Adds a tooltip to the second column, None by default.
        Both info and text can be None -> Empty column
        """
        item = tree.topLevelItem(index_parent)
        item.addChild(QTreeWidgetItem(index_child))
        subitem = item.child(index_child)
        subitem.setText(0, info)
        subitem.setText(1, text)
        if tooltip:
            subitem.setToolTip(1, tooltip)

    def addTabToWidget(self, name, tabwidget):
        """
        name = Name of the new tab
        tabwidget = Tabwidget to append to
        Adds a QTableView tab to the tab widget.
        Returns QTableView object
        """
        tab = QWidget()
        tabwidget.addTab(tab, name)
        tabGridLayout = QGridLayout(tab)
        tableView = QTableView()
        tableView.setStyleSheet("QHeaderView::section { background-color:#b7cbeb }")
        tabGridLayout.addWidget(tableView)
        return tableView
