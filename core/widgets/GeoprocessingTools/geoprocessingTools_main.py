# -*- coding: utf-8 -*-

from core.libs.CustomFileDialog.CustomFileDialog import CustomFileDialog
from core.libs.LSAT_Messages.messages_main import Messenger
from core.uis.GeoprocessingTools_ui.GeoprocessingTools_ui import Ui_GeoprocessingTools
from core.widgets.GeoprocessingTools.geoprocessingTools_calc import GeoprocessingToolsWorker
import os
import logging
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class GeoprocessingTools(QMainWindow):
    """
    This class is the main platform of the LSAT application.
    """

    def __init__(self, projectLocation=os.getcwd(), parent=None):
        """
        Initializes the application.
        :param parent: None
        """
        QWidget.__init__(self, parent)
        self.ui = Ui_GeoprocessingTools()
        self.ui.setupUi(self)
        self.progress = QProgressBar()
        self.statusBar().addPermanentWidget(self.progress)
        # Set the window icon
        self.setWindowIcon(QIcon(':/icons/Icons/GeoprocessingTools.png'))

        self.fileDialog = CustomFileDialog()
        self.projectLocation = projectLocation
        self.message = Messenger()
        self.thread_status = False

    @pyqtSlot()
    def on_featureToolButton_clicked(self):
        self.fileDialog.openFeatureFile(self.projectLocation)
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
            self.ui.featureLineEdit.setText(os.path.normpath(self.fileDialog.selectedFiles()[0]))

    @pyqtSlot()
    def on_methodLayerToolButton_clicked(self):
        self.fileDialog.openFeatureFile(self.projectLocation)
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
            self.ui.methodLayerLineEdit.setText(
                os.path.normpath(self.fileDialog.selectedFiles()[0]))

    @pyqtSlot()
    def on_outFeatureToolButton_clicked(self):
        self.fileDialog.openFeatureFile(self.projectLocation)
        if self.fileDialog.exec_() == 1 and self.fileDialog.selectedFiles():
            file = self.fileDialog.selectedFiles()[0]
            if file.lower().endswith(".shp"):
                self.ui.outFeatureLineEdit.setText(os.path.normpath(file))
            else:
                self.ui.outFeatureLineEdit.setText(os.path.normpath(file+".shp"))

    @pyqtSlot()
    def on_cancelPushButton_clicked(self):
        """
        Cancels the procedure and closes the application.
        :return: None
        """
        try:
            if self.thread_status:
                self.thread.terminate()
            self.close()
        except Exception as e:
            logging.ERROR(str(e))
            self.close()

    @pyqtSlot()
    def on_applyPushButton_clicked(self):
        try:
            if (not self.ui.featureLineEdit.text() or not self.ui.methodLayerLineEdit.text() or 
                not self.ui.outFeatureLineEdit.text()):
                self.message.WarningMissingInput()
                return

            self.thread_status = True
            self.progress.setRange(0, 0)
            self.ui.applyPushButton.setEnabled(False)

            inDataPath = self.ui.featureLineEdit.text()
            methodLayerPath = self.ui.methodLayerLineEdit.text()
            outDataPath = self.ui.outFeatureLineEdit.text()
            processingType = self.ui.processingComboBox.currentIndex()
            # 0 - Clip, 1 - Erase,  2 - Intersect, 3 - Symmetrical Difference, 4 - Union
            srBox = self.ui.srCheckBox.isChecked()

            options = []
            if self.ui.skipFailuresCheckBox.isChecked():
                options.append("SKIP_FAILURES=YES")
            else:
                options.append("SKIP_FAILURES=NO")
            if self.ui.promoteToMultiCheckBox.isChecked():
                options.append("PROMOTE_TO_MULTI=YES")
            else:
                options.append("PROMOTE_TO_MULTI=NO")

            # Start the Analysis as Thread
            kwargs = (processingType, options, srBox)
            self.thread = QThread()
            self.worker = GeoprocessingToolsWorker(
                inDataPath, methodLayerPath, outDataPath, kwargs)
            self.worker.moveToThread(self.thread)

            self.worker.loggingInfoSignal.connect(self.updateLogger)
            self.thread.started.connect(self.worker.run)
            self.worker.finishSignal.connect(self.done)
            self.thread.start()

        except Exception as e:
            logging.ERROR(str(e.message))

    def done(self):
        """
        Defines actions after the thread emits the signal "finished()".
        :return: None
        """
        self.thread.quit()
        self.thread_status = False
        self.message.getLoggingInfoOnAnalysisCompleted()
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.ui.applyPushButton.setEnabled(True)

    def updateLogger(self, message):
        logging.info(str(message))
