# -*- coding: cp1252 -*-

import codecs
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtNetwork import *
from core.uis.Settings_ui.LanguageSettings_ui import Ui_LanguageSettings
from core.libs.Management import Project_configuration as configuration


class LanguageSettings(QMainWindow):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_LanguageSettings()
        self.ui.setupUi(self)
        self.setWindowTitle(self.tr("Language Settings"))
        self.setWindowIcon(QIcon(':/icons/Icons/language.png'))
        self.config = configuration.Configuration()
        language = self.config.getLanguage()
        idx = self.ui.comboBox.findText(str(language))
        self.ui.comboBox.setCurrentIndex(idx)

    @pyqtSlot()
    def on_applyPushButton_clicked(self):
        self.config.config["DEFAULT"]["language"] = str(self.ui.comboBox.currentText())
        with codecs.open("config.ini", 'w', "utf-8") as configfile:
            self.config.config.write(configfile)
        self.close()
        QMessageBox.information(self, self.tr("Restart Application"), self.tr(
            "The changes become active after restart of the application!"))

    @pyqtSlot()
    def on_cancelPushButton_clicked(self):
        self.close()
