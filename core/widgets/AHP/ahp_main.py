from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import logging
import numpy as np
import os
from core.uis.AHP_ui.ahp_ui import Ui_AHP
from core.libs.Analysis.ahp_calc import ahp_calc
from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog
from core.libs.GDAL_Libs.Layers import Raster
from core.widgets.ParameterSelection.ParameterSelection_main import ParameterSelection


class ahp(QMainWindow):
    """
    The part of the AHP the user can interact with.
    """

    def __init__(self, project_path: str, parent=None):
        """
        Sets up the ui.
        Defines:
        self.project_path = Absolute path to the project
        self.pathNames = Dictionary connecting file name to path
        """
        super().__init__()
        self.ui = Ui_AHP()
        self.ui.setupUi(self)
        self.dialog = CustomFileDialog()
        self.project_path = project_path
        self.setWindowIcon(QIcon(":/icons/Icons/ahp.png"))
        self.pathNames = dict()
        # Sets the Header color
        self.ui.inputTableWidget.setStyleSheet("QHeaderView::section{background-color:#b7cbeb}")
        self.ui.rastertableWidget.setStyleSheet("QHeaderView::section{background-color:#b7cbeb}")

        # Tell inputTable and rasertableWidget to cut of the left side of the text "..." and
        # stretch it to fill the ui. We also limit rastertablewidget verticalheadersize.
        self.ui.inputTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.inputTableWidget.setTextElideMode(Qt.ElideLeft)
        self.ui.inputTableWidget.setWordWrap(False)
        self.ui.rastertableWidget.horizontalHeader().setTextElideMode(Qt.ElideLeft)
        self.ui.rastertableWidget.verticalHeader().setTextElideMode(Qt.ElideLeft)
        self.ui.rastertableWidget.verticalHeader().setDefaultAlignment(Qt.AlignRight)
        self.ui.rastertableWidget.verticalHeader().setMaximumWidth(500)
        self.ui.rastertableWidget.setWordWrap(False)

        # Add icons to buttons
        self.ui.addrasterPushButton.setIcon(QIcon(":icons/Icons/plus.png"))
        self.ui.removerasterPushButton.setIcon(QIcon(":icons/Icons/minus.png"))

        # Connect functions when changing TableWidgets
        self.ui.rastertableWidget.itemChanged.connect(self.on_tablecell_changed)

        # Fill outputLineEdit with default
        self.filloutputlineedit(project_path)

    def filloutputlineedit(self, project_path: str) -> None:
        """
        Gets called by init to set a default output name. Default is "AHP", but if either
        \tables\\AHP_tab.npz or \rasters\\AHP_ahp.tif exists it changes to AHP1, AHP2
        and so on.
        """
        name = "AHP"
        raster = os.path.join(project_path, "results", "AHP", "rasters", name + "_ahp.tif")
        npz = os.path.join(project_path, "results", "AHP", "tables", name + "_tab.npz")
        nr = 0
        # If AHP.tif or AHP.docx already exists we need to change the output name
        while os.path.isfile(raster) or os.path.isfile(npz):
            raster = os.path.join(project_path, "results", "AHP", "rasters",
                                  "".join([name, str(nr + 1), "_ahp.tif"]))
            npz = os.path.join(project_path, "results", "AHP", "tables",
                               "".join([name, str(nr + 1), "_tab.npz"]))
            nr += 1
        # If no file exists we do not need a number, else we append it at the end
        if nr == 0:
            self.ui.outputLineEdit.setText(name)
        else:
            self.ui.outputLineEdit.setText(name + str(nr))

    @pyqtSlot()
    def on_addrasterPushButton_clicked(self) -> None:
        """
        Opens a dialog to let the user select rasters to add.
        Calls addRasterList.
        """
        self.dialog.openRasterFiles(self.project_path)
        if self.dialog.exec_() == 1 and self.dialog.selectedFiles():  # Only if atleast 1 Raster
            self.addRasterList(self.dialog.selectedFiles())

    def selectParameter(self) -> None:
        """
        Gets called from MainFrame_main when the user starts AHP. First starts Paramter Selection
        allowing the user to pick whichever Rasters he wants to use in the calculation before
        starting the main ANN Widget after recieving a signal from Parameter Selection.
        """
        self.hide()
        self.paramSelection = ParameterSelection(self.project_path)
        self.paramSelection.show()
        self.paramSelection.apply_clicked.connect(self.addRasterList)

    def addRasterList(self, rasterlist: list) -> None:
        """
        Gets called by selectParameter and on_addrasterPushButton_clicked.
        Adds new rasters to the mainTable in a new row with three columns:
        1. Parameter name 2. Number of unique values 3. 1D Array of Values if len() < 10
        If the raster has > 10 values LSAT will let the user know, that this is not ideal.
        """
        for rasterPath in rasterlist:
            # Check if the raster already exists in the dictionary, let the user know and skip it.
            rasterFileName = os.path.splitext(os.path.basename(rasterPath))[0]
            if rasterFileName in self.pathNames:
                logging.info(
                    self.tr("{} is already part of the calculation").format(rasterFileName))
                continue
            # adds rasterFileName (key) with rasterPath (value) to self.pathNames
            self.pathNames[rasterFileName] = rasterPath
            # gets the number of rows present and inserts a new one at the end
            rowposition = self.ui.inputTableWidget.rowCount()
            self.ui.inputTableWidget.insertRow(rowposition)
            # writes the name of the raster in the first column
            qraster = QTableWidgetItem(rasterFileName)
            self.ui.inputTableWidget.setItem(rowposition, 0, qraster)
            # We get the amount of unique raster values and write it in the second column
            rasterHandle = Raster(rasterPath)
            uniquevaluescount = rasterHandle.uniqueValuesCount
            quniquevaluescount = QTableWidgetItem(str(uniquevaluescount))
            self.ui.inputTableWidget.setItem(rowposition, 1, quniquevaluescount)
            # We write the unique raster values in the third column if there are > 10 else we
            # write "many" with a red background
            if uniquevaluescount > 10:
                quniquevalues = QTableWidgetItem(self.tr("many (> 10). Wrong raster?"))
                quniquevalues.setBackground(Qt.red)
            else:
                uniquevalues = rasterHandle.uniqueValues
                quniquevalues = QTableWidgetItem(str(uniquevalues))
            self.ui.inputTableWidget.setItem(rowposition, 2, quniquevalues)
        # Resizes table to fit given data after adding them
        self.ui.inputTableWidget.horizontalHeader().setSectionResizeMode(1,
                                                                         QHeaderView.ResizeToContents)
        self.ui.inputTableWidget.horizontalHeader().setSectionResizeMode(2,
                                                                         QHeaderView.ResizeToContents)
        # Update rasterTable
        self.updaterastertable()
        self.updaterastertabs()
        if self.isHidden():  # We show AHP if started from Parameter Selection.
            self.show()

    @pyqtSlot()
    def on_removerasterPushButton_clicked(self):
        """
        Removes the selected Raster from inputTable and self.pathNames dictionary.
        If none is selected it removes starting from the last selected position.
        """
        selectedRow = self.ui.inputTableWidget.currentRow()
        del self.pathNames[self.ui.inputTableWidget.item(selectedRow, 0).text()]
        self.ui.inputTableWidget.removeRow(selectedRow)
        # Update rasterTable and rastertabs
        self.updaterastertable()
        self.updaterastertabs()

    def updaterastertable(self):
        """
        Gets called by on_addrasterPushButton_clicked and on_removerasterPushButton_clicked.
        If we add/remove a raster from the calculation/inputTableWidget we recreate the complete
        raster comparison table.
        """
        # Disable signals during creation
        self.ui.rastertableWidget.blockSignals(True)
        self.ui.rastertableWidget.setRowCount(0)
        self.ui.rastertableWidget.setColumnCount(0)
        inputrows = self.ui.inputTableWidget.rowCount()
        rasternames = [self.ui.inputTableWidget.item(i, 0).text() for i in range(inputrows)]
        for raster in rasternames:
            self.ui.rastertableWidget.insertRow(0)
            self.ui.rastertableWidget.insertColumn(0)
        self.ui.rastertableWidget.setHorizontalHeaderLabels(rasternames)
        self.ui.rastertableWidget.setVerticalHeaderLabels(rasternames)
        # Pre fills the table and makes only the upper right editable and selectable
        self._filltable(self.ui.rastertableWidget)
        self.ui.rastertableWidget.blockSignals(False)

    def updaterastertabs(self) -> None:
        """
        Gets called by on_addrasterPushButton_clicked and on_removerasterPushButton_clicked.
        For every raster in inputTableWidget we create a new Tab where the user can prioritise its
        unique values. We only create new ones and delete old ones.
        """
        rows = self.ui.inputTableWidget.rowCount()
        tabs = self.ui.tabWidget.count()
        rasternames = [self.ui.inputTableWidget.item(i, 0).text() for i in range(rows)]
        tabnames = [self.ui.tabWidget.widget(i).objectName() for i in range(tabs)]
        # We remove the first and last item in tabnames because these are always input and raster
        # comparison
        tabnames.pop()
        tabnames.pop(0)
        rastertabstoadd = []
        rastertabstodel = []
        for tab in tabnames:
            if tab not in rasternames:
                rastertabstodel.append(tab)
        for raster in rasternames:
            if raster not in tabnames:
                rastertabstoadd.append(raster)
        self._addrastertabs(rastertabstoadd)
        self._delrastertabs(rastertabstodel)

    def _addrastertabs(self, rastertabstoadd: list) -> None:
        """
        Gets called by updaterastertabs.
        Adds new Tabs to tabWidget if they are in the input TableWidget. Also fills the new
        TableWidget.
        """
        for raster in rastertabstoadd:
            # Add and configure PyQt structure for the tab
            tabcount = self.ui.tabWidget.count()
            rasterwidget = QWidget()
            rasterwidget.setObjectName(raster)
            horizontalLayout = QHBoxLayout(rasterwidget)
            rastervalueTableWidget = QTableWidget(rasterwidget)
            rastervalueTableWidget.setAlternatingRowColors(True)
            rastervalueTableWidget.setTextElideMode(Qt.ElideLeft)
            rastervalueTableWidget.setWordWrap(False)
            rastervalueTableWidget.setObjectName(f"table_{self.pathNames[raster]}")
            rastervalueTableWidget.setStyleSheet("QHeaderView::section{background-color:#b7cbeb}")
            horizontalLayout.addWidget(rastervalueTableWidget)
            # second to last because raster comparison is always the last tab
            self.ui.tabWidget.insertTab(tabcount - 1, rasterwidget, raster)
            # Fill the tablewidget
            memoryraster = Raster(self.pathNames[raster])
            uniquevaluescount = memoryraster.uniqueValuesCount
            if uniquevaluescount > 100:
                rastervalueTableWidget.insertRow(0)
                rastervalueTableWidget.insertColumn(0)
                a_lot = QTableWidgetItem(self.tr("> 100 Values! Not viable."))
                a_lot.setFlags(a_lot.flags() ^ Qt.ItemIsEditable)
                rastervalueTableWidget.setItem(0, 0, a_lot)
                continue
            uniquevalues = [str(x) for x in memoryraster.uniqueValues.tolist()]
            for values in range(uniquevaluescount):
                rastervalueTableWidget.insertRow(0)
                rastervalueTableWidget.insertColumn(0)
            rastervalueTableWidget.setHorizontalHeaderLabels(uniquevalues)
            rastervalueTableWidget.setVerticalHeaderLabels(uniquevalues)
            self._filltable(rastervalueTableWidget)
            # Connect function to automatically calculate lower left part
            rastervalueTableWidget.itemChanged.connect(self.on_tablecell_changed)

    def _filltable(self, table) -> None:
        """
        Gets called by updaterastertable and _addrastertabs.
        Prefills and configures table for later use.
        Line from top left to bottom right gets filled by "1" and disabled
        Bellow that we disable editing and disable the cells because it gets autofilled when we
        change the upper right part.
        """
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                if row == col:
                    fill = QTableWidgetItem("1")
                    fill.setFlags(fill.flags() ^ Qt.ItemIsEditable ^ Qt.ItemIsEnabled)
                # lower left side
                elif row > col:
                    fill = QTableWidgetItem("")
                    fill.setFlags(fill.flags() ^ Qt.ItemIsEditable ^ Qt.ItemIsEnabled)
                # upper right side
                elif row < col:
                    fill = QTableWidgetItem("")
                table.setItem(row, col, fill)  # filler

    def _delrastertabs(self, rastertabstodelete: list):
        """
        Gets called by updaterastertabs.
        Removes raster specific tabs from tabWidget if they are no longer in the input TableWidget
        and explicitly tells Qt to delete the table when the tab gets deleted.
        """
        for raster in rastertabstodelete:
            # We named the tab after the raster path
            tab = self.ui.tabWidget.findChild(QWidget, raster)
            tables = tab.findChildren(QTableWidget)
            for table in tables:
                table.deleteLater()
            index = self.ui.tabWidget.indexOf(tab)
            self.ui.tabWidget.removeTab(index)

    @pyqtSlot()
    def on_nextPushButton_clicked(self):
        """
        Goes to the next tab.
        Input -> *specific raster tabs* -> Raster
        Can also loop back to the start.
        """
        n = self.ui.tabWidget.currentIndex()
        tabcount = self.ui.tabWidget.count()
        if n + 1 == tabcount:
            self.ui.tabWidget.setCurrentIndex(0)
        else:
            self.ui.tabWidget.setCurrentIndex(n + 1)

    @pyqtSlot()
    def on_backPushButton_clicked(self):
        """
        Goes to the last tab.
        Raster -> *Specific raster tabs* -> Input
        Loops the tabs.
        """
        n = self.ui.tabWidget.currentIndex()
        tabcount = self.ui.tabWidget.count()
        if n == 0:
            self.ui.tabWidget.setCurrentIndex(tabcount - 1)
        else:
            self.ui.tabWidget.setCurrentIndex(n - 1)

    @pyqtSlot()
    def on_applyPushButton_clicked(self):
        """
        Calls functions to check the inputs and to gather information for calculation and then
        starts it.
        """
        if self._checkinputs():
            # Disables apply button and animates the progressbar to show the user that something is
            # happening in the background
            self.ui.applyPushButton.setEnabled(False)
            self.ui.mainprogressBar.setMaximum(0)
            scale, prioritymethod, rastervaluescomp, rastercomp, outputname = self._getinputs()
            ahpc = ahp_calc(
                scale,
                prioritymethod,
                rastervaluescomp,
                rastercomp,
                outputname,
                self.project_path)
            self.threadpool = QThreadPool()
            worker = WorkThread(ahpc.run)
            worker.signals.finished.connect(lambda: self.updateui(outputname))
            self.threadpool.start(worker)

    def _checkinputs(self) -> bool:
        """
        Gets called by on_applyPushButton_clicked.
        Checks if the user provided enough information for the calculation to start.
        """
        # We check if the user filled out every TableWidget.
        tables = self.ui.tabWidget.findChildren(QTableWidget)
        for table in tables:
            for row in range(table.rowCount()):
                for col in range(table.columnCount()):
                    text = table.item(row, col).text()
                    if text in ("?", ""):
                        logging.info(
                            self.tr("Information missing from {}.").format(
                                table.objectName()))
                        return False
        # If there are atleast 3 Tabs the user added atleast 1 rasters.
        tabcount = self.ui.tabWidget.count()
        if tabcount < 3:
            logging.info(self.tr("Please add atleast one raster."))
            self.ui.addrasterPushButton.setStyleSheet("background-color: rgb(255, 0, 0)")
            QTimer.singleShot(500, lambda: self.ui.addrasterPushButton.setStyleSheet(""))
            return False
        # We need an outputname
        outputname = self.ui.outputLineEdit.text()
        if not outputname:
            logging.info(self.tr("Please provide an output name."))
            self.ui.outputLineEdit.setStyleSheet("background-color: rgb(255, 0, 0)")
            QTimer.singleShot(500, lambda: self.ui.outputLineEdit.setStyleSheet(""))
            return False
        return True

    def _getinputs(self) -> tuple:
        """
        Gets called by on_applyPushButton_clicked.
        We gather the user input for the calculation. For the arrays we call _tables2array.
        """
        scale = 0 # used to read a combo box value but for initial release we only use linear
        prioritymethod = self.ui.methodpriorityComboBox.currentIndex()
        tables = self.ui.tabWidget.findChildren(QTableWidget)
        rastervaluescomp, rastercomp = self._tables2array(tables)
        outputname = self.ui.outputLineEdit.text()
        return (scale, prioritymethod, rastervaluescomp, rastercomp, outputname)

    def _tables2array(self, tables) -> tuple:
        """
        Gets called by _getinputs. We transform the Tablewidgets into arrays for use in the
        calculation. We also append the paths so we can keep track in the calculation.
        Returns two lists:
        1. [[Array of values of raster 1, Path to raster 1], ..., [Array of values of raster n,
           Path to raster n]]
        2. [Array of values of raster comparison, [path to raster 1, ... path to raster n]]
        """
        rastervaluescomp = []
        for table in tables:
            # We can skip the input Table
            if table.objectName() == "inputTableWidget":
                continue
            rows = table.rowCount()
            cols = table.columnCount()
            array = np.zeros([rows, cols])
            for row in range(rows):
                for col in range(cols):
                    array[row][col] = float(table.item(row, col).text())
            # These are raster value comparisons
            if table.objectName().startswith("table_"):
                # Removes table_ from the start of the ObjectName
                rastervaluescomp.append([array, table.objectName()[len("table_"):]])
            # This is the raster comparison
            else:
                # We append a list of used rasters as the second element
                rasterpaths = []
                for c in range(cols):
                    path = self.pathNames[table.horizontalHeaderItem(c).text()]
                    rasterpaths.append(path)
                rastercomp = [array, rasterpaths]
        return (rastervaluescomp, rastercomp)

    @pyqtSlot()
    def updateui(self, outputname: str) -> None:
        """
        Gets called once the calculation thread finishes. Updates the Ui Elements and tells the
        user where the results were saved.
        """
        # We set the Maximum to 1 to stop the animation in the progressbar.
        self.ui.mainprogressBar.setMaximum(1)
        self.ui.applyPushButton.setEnabled(True)
        npzpath = os.path.join(
            self.project_path,
            "results",
            "AHP",
            "tables",
            outputname +
            "_tab.npz")
        rasterpath = os.path.join(
            self.project_path,
            "results",
            "AHP",
            "rasters",
            outputname +
            "_ahp.tif")
        logging.info(self.tr("Results saved in {}").format(npzpath))
        logging.info(self.tr("Raster with Results saved in {}").format(rasterpath))
        logging.info(self.tr("AHP Calculation completed."))

    def on_tablecell_changed(self, item):
        """
        Functions gets called when the user edits any raster or rastervalue TableWidget. As he/she
        can only edit the upper right part we only need to update the lower left and can ignore the
        rest as these changes are done automatically.
        """
        full_dic = { # used to fill the lower left side after entering the top right part
        1.0: "1",
        0.5: "2",
        0.333333333: "3",
        0.25: "4",
        0.2: "5",
        0.166666667: "6",
        0.142857142: "7",
        0.125: "8",
        0.111111111: "9"}
        fraction_dic = {
        "1/0": "?",
        "1/1": "1",
        "1/2": "0.5",
        "1/3": "0.333333333",
        "1/4": "0.25",
        "1/5": "0.2",
        "1/6": "0.166666667",
        "1/7": "0.142857142",
        "1/8": "0.125",
        "1/9": "0.111111111"}
        parent = self.sender()
        # We do not want to infinitly loop the function
        parent.blockSignals(True)
        row = item.row()
        col = item.column()
        edited = item.text()
        # If the user entered a fraction we calculate it for him/her
        if (len(edited) == 3 and edited[0] == "1" and edited[1] == "/" and edited[2].isdigit()):
            edited = fraction_dic[edited]
            item.setText(edited)
        try:
            edited = float(edited)
        except ValueError:
            new = QTableWidgetItem("?")
            new.setFlags(new.flags() ^ Qt.ItemIsEditable ^ Qt.ItemIsEnabled)
            parent.setItem(col, row, new)
            parent.blockSignals(False)
            return
        if float(edited):  # 0.0 equals False
            if float(edited) <= 1:
                try:
                    new = QTableWidgetItem(full_dic[edited])
                except KeyError:
                    new = QTableWidgetItem(str(round(1/edited, 9)))
            else:
                try:
                    new = QTableWidgetItem(fraction_dic["1/"+str(int(edited))])
                except KeyError:
                    new = QTableWidgetItem(str(round(1/edited, 9)))
        else:
            new = QTableWidgetItem("?")
        new.setFlags(new.flags() ^ Qt.ItemIsEditable ^ Qt.ItemIsEnabled)
        # col and row flipped
        parent.setItem(col, row, new)
        parent.blockSignals(False)

# WorkThreadSignals and WorkThread are used to start the calculation (ahp_calc) in its own Thread
# using QRunnable


class WorkThreadSignals(QObject):
    finished = pyqtSignal()


class WorkThread(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(WorkThread, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkThreadSignals()

    @pyqtSlot()
    def run(self):
        self.fn(*self.args, **self.kwargs)
        self.signals.finished.emit()
