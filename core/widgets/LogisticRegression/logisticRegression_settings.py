import configparser
import logging
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from core.uis.LogisticRegression_ui.AdvancedSettingsLogReg_ui import Ui_AdvancedSettingsLogReg


class Settings(QWidget):
    """
    This class handles the Advanced Settings Window.
    """

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_AdvancedSettingsLogReg()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.configFilePath = os.path.join(
            "core", "Widgets", "LogisticRegression", "configLogReg.ini")
        if not os.path.isfile(self.configFilePath):
            # If the .ini file does not exist, we create it.
            self.generateini()
            logging.info(
                self.tr("LR .ini not found. Generating new one: {}").format(
                    os.path.join(
                        os.getcwd(),
                        self.configFilePath)))
        self.setWindowIcon(QIcon(':/icons/Icons/Settings.png'))
        self.setWindowTitle(self.tr("Advanced Settings"))
        self.readConfigfile(self.configFilePath)
        self.loadFromConfigFile()
        self.validate()

    def generateini(self) -> None:
        """
        If init did not find a ini file this function generates a new one based on scipy defaults.
        """
        config = configparser.ConfigParser()
        defaults = {"penalty": "l2",
                    "dual": "False",
                    "tol": "0.0001",
                    "c": "1.0",
                    "fit_intercept": "True",
                    "intercept_scaling": "1",
                    "class_weight": "None",
                    "random_state": "None",
                    "solver": "lbfgs",
                    "max_iter": "100",
                    "multi_class": "auto",
                    "verbose": "0",
                    "warm_start": "False",
                    "n_jobs": "None",
                    "l1_ratio": "None"}
        config["DEFAULT"] = defaults
        config["USER_SETTINGS"] = defaults
        with open(os.path.join(os.getcwd(), self.configFilePath), 'w') as configfile:
            config.write(configfile)

    def readConfigfile(self, configfile):
        self.config = configparser.ConfigParser()
        self.config.read(configfile)

    @pyqtSlot()
    def on_resetToDefaultPushButton_clicked(self):
        """
        Resets the USER_SETTING in the confifile to DEFAULT settings.
        Updates the GUI with default values.
        :return: None
        """
        self.readConfigfile(self.configFilePath)
        for key in self.config["DEFAULT"]:
            self.config["USER_SETTINGS"][key] = self.config["DEFAULT"][key]
        with open(str(self.configFilePath), "w") as configfile:
            self.config.write(configfile)
        self.readConfigfile(self.configFilePath)
        self.loadFromConfigFile()
        self.validate()

    @pyqtSlot(int)
    def on_nJobsComboBox_activated(self):
        self.validate()

    @pyqtSlot(int)
    def on_randomStateComboBox_activated(self):
        self.validate()

    @pyqtSlot(int)
    def on_l1RatioComboBox_activated(self):
        self.validate()

    def validate(self):
        """
        Validates the input settings and updates the visibility of the GUI elements.
        :return: None
        """
        if self.ui.l1RatioComboBox.currentText() == "None":
            self.ui.l1RatioLineEdit.clear()
            self.ui.l1RatioLineEdit.setEnabled(0)
        else:
            if self.config["USER_SETTINGS"]["l1_ratio"] == "None" or self.config["USER_SETTINGS"]["l1_ratio"] == "":
                value = "1"
            else:
                value = self.config["USER_SETTINGS"]["l1_ratio"]
            self.ui.l1RatioLineEdit.setEnabled(1)
            self.ui.l1RatioLineEdit.setText(value)

        if self.ui.randomStateComboBox.currentIndex() == 0:
            self.ui.randomStateLineEdit.setEnabled(1)
            if self.config["USER_SETTINGS"]["random_state"] == "" or self.config["USER_SETTINGS"]["random_state"] == "None":
                value = "1"
            else:
                value = self.config["USER_SETTINGS"]["random_state"]
            self.ui.randomStateLineEdit.setText(value)
        else:
            self.ui.randomStateLineEdit.clear()
            self.ui.randomStateLineEdit.setEnabled(0)

        if self.ui.nJobsComboBox.currentIndex() == 0:
            self.ui.n_jobsLineEdit.clear()
            self.ui.n_jobsLineEdit.setEnabled(0)
        else:
            if self.config["USER_SETTINGS"]["n_jobs"] == "None":
                value = "1"
            else:
                value = self.config["USER_SETTINGS"]["n_jobs"]
            self.ui.n_jobsLineEdit.setText(value)
            self.ui.n_jobsLineEdit.setEnabled(1)

    def loadFromConfigFile(self):
        """
        Reads out the user settings from ini-configfile and populates GUI
        with values.
        :return: None
        """
        solverCombo = self.ui.solverComboBox
        idx = solverCombo.findText(self.config["USER_SETTINGS"]["solver"])
        solverCombo.setCurrentIndex(idx)
        penaltyCombo = self.ui.penaltyComboBox
        idx = penaltyCombo.findText(self.config["USER_SETTINGS"]["penalty"])
        penaltyCombo.setCurrentIndex(idx)

        l1_ratioCombo = self.ui.l1RatioComboBox
        if self.config["USER_SETTINGS"]["l1_ratio"] == "None":
            idx = 0
        else:
            idx = 1
        l1_ratioCombo.setCurrentIndex(idx)

        dualCombo = self.ui.dualComboBox
        if self.config["USER_SETTINGS"]["dual"] == "True":
            idx = 0
        else:
            idx = 1
        dualCombo.setCurrentIndex(idx)

        tolValue = self.ui.toleranceLineEdit
        tolValue.setText(self.config["USER_SETTINGS"]["tol"])

        invRegValue = self.ui.inverseRegLineEdit
        invRegValue.setText(self.config["USER_SETTINGS"]["c"])

        interceptCombo = self.ui.interceptComboBox
        idx = interceptCombo.findText(str(self.config["USER_SETTINGS"]["fit_intercept"]))
        interceptCombo.setCurrentIndex(idx)

        interceptScale = self.ui.interceptScaleLineEdit
        interceptScale.setText(self.config["USER_SETTINGS"]["intercept_scaling"])

        classWeightCombo = self.ui.classWeightComboBox
        idx = classWeightCombo.findText(self.config["USER_SETTINGS"]["class_weight"])
        classWeightCombo.setCurrentIndex(idx)

        randCombo = self.ui.randomStateComboBox
        set_list = ["Integer", "Random state instance", "None"]
        if self.config["USER_SETTINGS"]["random_state"] not in set_list:
            idx = 0
            self.ui.randomStateLineEdit.setText(self.config["USER_SETTINGS"]["random_state"])
        else:
            idx = randCombo.findText(self.config["USER_SETTINGS"]["random_state"])
        randCombo.setCurrentIndex(idx)

        max_iter = self.ui.max_iterLineEdit
        max_iter.setText(self.config["USER_SETTINGS"]["max_iter"])

        multiclassCombo = self.ui.multi_classComboBox
        idx = multiclassCombo.findText(self.config["USER_SETTINGS"]["multi_class"])
        multiclassCombo.setCurrentIndex(idx)

        verbose = self.ui.verboseLineEdit
        verbose.setText(self.config["USER_SETTINGS"]["verbose"])

        warmStartCombo = self.ui.warmStartComboBox
        idx = warmStartCombo.findText(self.config["USER_SETTINGS"]["warm_start"])
        warmStartCombo.setCurrentIndex(idx)

        n_jobsCombo = self.ui.nJobsComboBox
        if self.config["USER_SETTINGS"]["n_jobs"] == "None":
            idx = 0
        else:
            idx = 1
        n_jobsCombo.setCurrentIndex(idx)

    @pyqtSlot()
    def on_cancelPushButton_clicked(self):
        self.close()

    @pyqtSlot()
    def on_applyPushButton_clicked(self):
        solver = str(self.ui.solverComboBox.currentText())
        self.config["USER_SETTINGS"]["solver"] = str(solver)
        penalty = str(self.ui.penaltyComboBox.currentText())
        if penalty == "None":
            penalty = 'None'
        self.config["USER_SETTINGS"]["penalty"] = str(penalty)

        if self.ui.l1RatioComboBox.currentText() == "Float":
            l1_ratio = str(self.ui.l1RatioLineEdit.text())
        else:
            l1_ratio = 'None'
        self.config["USER_SETTINGS"]["l1_ratio"] = str(l1_ratio)

        if self.ui.dualComboBox.currentText() == "dual":
            dual = 'True'
        else:
            dual = 'False'
        self.config["USER_SETTINGS"]["dual"] = str(dual)
        tol = self.ui.toleranceLineEdit.text()
        self.config["USER_SETTINGS"]["tol"] = str(tol)
        C = self.ui.inverseRegLineEdit.text()
        self.config["USER_SETTINGS"]["C"] = str(C)

        if str(self.ui.interceptComboBox.currentText()) == "True":
            fit_intercept = 'True'
        else:
            fit_intercept = 'False'
        self.config["USER_SETTINGS"]["fit_intercept"] = str(fit_intercept)

        intercept_scaling = str(self.ui.interceptScaleLineEdit.text())
        self.config["USER_SETTINGS"]["intercept_scaling"] = str(intercept_scaling)

        class_weight = str(self.ui.classWeightComboBox.currentText())
        self.config["USER_SETTINGS"]["class_weight"] = str(class_weight)

        random_state = str(self.ui.randomStateComboBox.currentText())
        if random_state == "Integer":
            self.config["USER_SETTINGS"]["random_state"] = str(self.ui.randomStateLineEdit.text())
        else:
            self.config["USER_SETTINGS"]["random_state"] = str(
                self.ui.randomStateComboBox.currentText())

        max_iter = str(self.ui.max_iterLineEdit.text())
        self.config["USER_SETTINGS"]["max_iter"] = str(max_iter)

        multi_class = str(self.ui.multi_classComboBox.currentText())
        self.config["USER_SETTINGS"]["multi_class"] = str(multi_class)

        verbose = str(self.ui.verboseLineEdit.text())
        self.config["USER_SETTINGS"]["verbose"] = str(verbose)

        warm_start = str(self.ui.warmStartComboBox.currentText())
        self.config["USER_SETTINGS"]["warm_start"] = str(warm_start)

        n_jobs = str(self.ui.nJobsComboBox.currentText())
        if n_jobs == "Integer":
            self.config["USER_SETTINGS"]["n_jobs"] = str(self.ui.n_jobsLineEdit.text())
        else:
            self.config["USER_SETTINGS"]["n_jobs"] = str(n_jobs)

        with open(self.configFilePath, 'w') as configfile:
            self.config.write(configfile)

        logging.info(self.tr("Settings successfully applied."))
        self.close()
