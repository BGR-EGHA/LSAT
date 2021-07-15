from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import os
import re
import configparser
import logging
from core.uis.ANN_ui.ann_advset_ui import Ui_ANN_advset


class ann_advset(QMainWindow):
    def __init__(self, parent=None):
        """
        Sets up ui, connects lineedits to validation functions and updates the ui with values from
        ann_config.ini USER_SETTINGS section.
        Defines the following instanace variables:
        self.ini_path = Absolute path to the ini file.
        """
        QMainWindow.__init__(self, parent)
        self.ui = Ui_ANN_advset()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(':/icons/Icons/Settings.png'))
        self.ini_path = os.path.join(os.getcwd(), "core", "widgets", "ANN", "ann_config.ini")
        if not os.path.isfile(self.ini_path):
            # If the .ini file does not exist, we create it.
            self.generateini()
            logging.info(self.tr("ANN .ini not found. New one generated: {}").format(self.ini_path))

        # Most lineedits are different and we need to check them all
        self.ui.hidden_layer_sizesLineEdit.textChanged.connect(self.val_hidden_layer_sizes)
        self.ui.alphaLineEdit.textChanged.connect(self.val_float)
        self.ui.batch_sizeLineEdit.textChanged.connect(self.val_batch_size)
        self.ui.learning_rate_initLineEdit.textChanged.connect(self.val_float)
        self.ui.power_tLineEdit.textChanged.connect(self.val_float)
        self.ui.max_iterLineEdit.textChanged.connect(self.val_int)
        self.ui.random_stateLineEdit.textChanged.connect(self.val_random_state)
        self.ui.tolLineEdit.textChanged.connect(self.val_float)
        self.ui.momentumLineEdit.textChanged.connect(self.val_float)
        self.ui.validation_fractionLineEdit.textChanged.connect(self.val_float)
        self.ui.beta_1LineEdit.textChanged.connect(self.val_float)
        self.ui.beta_2LineEdit.textChanged.connect(self.val_float)
        self.ui.epsilonLineEdit.textChanged.connect(self.val_float)
        self.ui.n_iter_no_changeLineEdit.textChanged.connect(self.val_int)
        self.ui.max_funLineEdit.textChanged.connect(self.val_int)

        # Starts configparser and loads the User settings into the ui
        self.config = configparser.ConfigParser()
        self.loadfromini()

    @pyqtSlot()
    def on_resetpushButton_clicked(self) -> None:
        """
        Resets the values in the USER_SETTINGS to DEFAULT specified in the .ini and updates the ui.
        """
        self.config.read(self.ini_path)
        for key in self.config["DEFAULT"]:
            self.config["USER_SETTINGS"][key] = self.config["DEFAULT"][key]
        with open(self.ini_path, "w") as inifile:
            self.config.write(inifile)
        self.loadfromini()
        self.ui.resetpushButton.setStyleSheet("") # val functions change the buttons look sometimes

    @pyqtSlot()
    def on_cancelPushButton_clicked(self) -> None:
        """
        Closes the Advanced Settings window without writing the changes to the .ini.
        """
        self.close()

    @pyqtSlot()
    def on_applyPushButton_clicked(self) -> None:
        """
        Writes the values from the ui into USER_SETTINGS in the .ini.
        """
        self.config.read(self.ini_path)
        self.config["USER_SETTINGS"]["hidden_layer_sizes"] = self.ui.hidden_layer_sizesLineEdit.text()
        self.config["USER_SETTINGS"]["activation"] = self.ui.activationComboBox.currentText()
        self.config["USER_SETTINGS"]["solver"] = self.ui.solverComboBox.currentText()
        self.config["USER_SETTINGS"]["alpha"] = self.ui.alphaLineEdit.text()
        self.config["USER_SETTINGS"]["batch_size"] = self.ui.batch_sizeLineEdit.text()
        self.config["USER_SETTINGS"]["learning_rate"] = self.ui.learning_rateComboBox.currentText()
        self.config["USER_SETTINGS"]["learning_rate_init"] = self.ui.learning_rate_initLineEdit.text()
        self.config["USER_SETTINGS"]["power_t"] = self.ui.power_tLineEdit.text()
        self.config["USER_SETTINGS"]["max_iter"] = self.ui.max_iterLineEdit.text()
        self.config["USER_SETTINGS"]["shuffle"] = str(bool(self.ui.shuffleCheckBox.checkState()))
        self.config["USER_SETTINGS"]["random_state"] = self.ui.random_stateLineEdit.text()
        self.config["USER_SETTINGS"]["tol"] = self.ui.tolLineEdit.text()
        self.config["USER_SETTINGS"]["verbose"] = str(bool(self.ui.verboseCheckBox.checkState()))
        self.config["USER_SETTINGS"]["warm_start"] = str(
            bool(self.ui.warm_startCheckBox.checkState()))
        self.config["USER_SETTINGS"]["momentum"] = self.ui.momentumLineEdit.text()
        self.config["USER_SETTINGS"]["nesterovs_momentum"] = str(
            bool(self.ui.nesterovs_momentumCheckBox.checkState()))
        self.config["USER_SETTINGS"]["early_stopping"] = str(
            bool(self.ui.early_stoppingCheckBox.checkState()))
        self.config["USER_SETTINGS"]["validation_fraction"] = self.ui.validation_fractionLineEdit.text()
        self.config["USER_SETTINGS"]["beta_1"] = self.ui.beta_1LineEdit.text()
        self.config["USER_SETTINGS"]["beta_2"] = self.ui.beta_2LineEdit.text()
        self.config["USER_SETTINGS"]["epsilon"] = self.ui.epsilonLineEdit.text()
        self.config["USER_SETTINGS"]["n_iter_no_change"] = self.ui.n_iter_no_changeLineEdit.text()
        self.config["USER_SETTINGS"]["max_fun"] = self.ui.max_funLineEdit.text()
        with open(self.ini_path, 'w') as inifile:
            self.config.write(inifile)
        logging.info(self.tr("User Settings in {} updated").format(self.ini_path))
        self.close()

    def val_hidden_layer_sizes(self):
        """
        Checks if hidden_layer_sizes only contains number and spaces
        """
        lineedittocheck = self.sender()
        stringtocheck = lineedittocheck.text()
        if (stringtocheck.startswith(" ") or (bool(re.search(r'  ', stringtocheck)))):
            lineedittocheck.setStyleSheet("background: rgb(255, 0, 0);")
        elif re.match("^ *[0-9][0-9 ]*$", stringtocheck):
            if ((stringtocheck[-1] == " ") or (stringtocheck[0] == " ")):
                lineedittocheck.setStyleSheet("background: yellow")
            else:
                lineedittocheck.setStyleSheet("background: white;")
        else:
            lineedittocheck.setStyleSheet("background: rgb(255, 0, 0);")

    def loadfromini(self):
        """
        Updates the ui with values from USER_SETTINGS in the .ini.
        """
        self.config.read(self.ini_path)
        self.ui.hidden_layer_sizesLineEdit.setText(
            self.config["USER_SETTINGS"]["hidden_layer_sizes"])
        i = self.ui.activationComboBox.findText(self.config["USER_SETTINGS"]["activation"])
        if i != -1:
            self.ui.activationComboBox.setCurrentIndex(i)
        i = self.ui.solverComboBox.findText(self.config["USER_SETTINGS"]["solver"])
        if i != -1:
            self.ui.solverComboBox.setCurrentIndex(i)
        self.ui.alphaLineEdit.setText(self.config["USER_SETTINGS"]["alpha"])
        self.ui.batch_sizeLineEdit.setText(self.config["USER_SETTINGS"]["batch_size"])
        i = self.ui.learning_rateComboBox.findText(self.config["USER_SETTINGS"]["learning_rate"])
        if i != -1:
            self.ui.learning_rateComboBox.setCurrentIndex(i)
        self.ui.learning_rate_initLineEdit.setText(
            self.config["USER_SETTINGS"]["learning_rate_init"])
        self.ui.power_tLineEdit.setText(self.config["USER_SETTINGS"]["power_t"])
        self.ui.max_iterLineEdit.setText(self.config["USER_SETTINGS"]["max_iter"])
        if self.config["USER_SETTINGS"]["shuffle"] == "False":
            self.ui.shuffleCheckBox.setChecked(False)
        else:
            self.ui.shuffleCheckBox.setChecked(True)
        self.ui.random_stateLineEdit.setText(self.config["USER_SETTINGS"]["random_state"])
        self.ui.tolLineEdit.setText(self.config["USER_SETTINGS"]["tol"])
        if self.config["USER_SETTINGS"]["verbose"] == "False":
            self.ui.verboseCheckBox.setChecked(False)
        else:
            self.ui.verboseCheckBox.setChecked(True)
        if self.config["USER_SETTINGS"]["warm_start"] == "False":
            self.ui.warm_startCheckBox.setChecked(False)
        else:
            self.ui.warm_startCheckBox.setChecked(True)
        self.ui.momentumLineEdit.setText(self.config["USER_SETTINGS"]["momentum"])
        if self.config["USER_SETTINGS"]["nesterovs_momentum"] == "False":
            self.ui.nesterovs_momentumCheckBox.setChecked(False)
        else:
            self.ui.nesterovs_momentumCheckBox.setChecked(True)
        if self.config["USER_SETTINGS"]["early_stopping"] == "False":
            self.ui.early_stoppingCheckBox.setChecked(False)
        else:
            self.ui.early_stoppingCheckBox.setChecked(True)
        self.ui.validation_fractionLineEdit.setText(
            self.config["USER_SETTINGS"]["validation_fraction"])
        self.ui.beta_1LineEdit.setText(self.config["USER_SETTINGS"]["beta_1"])
        self.ui.beta_2LineEdit.setText(self.config["USER_SETTINGS"]["beta_2"])
        self.ui.epsilonLineEdit.setText(self.config["USER_SETTINGS"]["epsilon"])
        self.ui.n_iter_no_changeLineEdit.setText(self.config["USER_SETTINGS"]["n_iter_no_change"])
        self.ui.max_funLineEdit.setText(self.config["USER_SETTINGS"]["max_fun"])

    def generateini(self) -> None:
        """
        If init did not find a ini file this function generates a new one based on scipy defaults.
        """
        config = configparser.ConfigParser()
        defaults = {"hidden_layer_sizes": "100",
                    "activation": "relu",
                    "solver": "adam",
                    "alpha": "0.0001",
                    "batch_size": "auto",
                    "learning_rate": "constant",
                    "learning_rate_init": "0.001",
                    "power_t": "0.5",
                    "max_iter": "200",
                    "shuffle": "True",
                    "random_state": "None",
                    "tol": "0.0001",
                    "verbose": "False",
                    "warm_start": "False",
                    "momentum": "0.9",
                    "nesterovs_momentum": "True",
                    "early_stopping": "False",
                    "validation_fraction": "0.1",
                    "beta_1": "0.9",
                    "beta_2": "0.999",
                    "epsilon": "0.00000001",
                    "n_iter_no_change": "10",
                    "max_fun": "1"}
        config["DEFAULT"] = defaults
        config["USER_SETTINGS"] = defaults
        with open(os.path.join(os.getcwd(), "core", "widgets", "ANN", "ann_config.ini"), 'w') as configfile:
            config.write(configfile)

    def val_float(self):
        """
        Checks if alpha, learning_rate_init, power_t, tol, momentum,
        validation_fraction, beta_1, beta_2 and epsilon only contain
        numbers and one dot.
        """
        lineedittocheck = self.sender()
        stringtocheck = lineedittocheck.text()
        if stringtocheck.replace(
                ".", "", 1).isdigit():  # Allows a single point
            lineedittocheck.setStyleSheet("background: white;")
        else:
            lineedittocheck.setStyleSheet("background: rgb(255, 0, 0);")

    def val_batch_size(self):
        """
        Checks if batch_size is either an int or "auto".
        """
        lineedittocheck = self.sender()
        stringtocheck = lineedittocheck.text()
        if ((stringtocheck.isdigit()) or (stringtocheck == "auto")):
            lineedittocheck.setStyleSheet("background: white;")
        elif "auto".startswith(stringtocheck) and stringtocheck != "":
            lineedittocheck.setStyleSheet("background: yellow;")
        else:
            lineedittocheck.setStyleSheet("background: rgb(255, 0, 0);")

    def val_int(self):
        """
        Checks if max_iter, n_iter_no_change and max_fun are int.
        """
        lineedittocheck = self.sender()
        stringtocheck = lineedittocheck.text()
        if stringtocheck.isdigit():
            lineedittocheck.setStyleSheet("background: white;")
        else:
            lineedittocheck.setStyleSheet("background: rgb(255, 0, 0);")

    def val_random_state(self):
        """
        Checks if random_state is "None" or int.
        """
        lineedittocheck = self.sender()
        stringtocheck = lineedittocheck.text()
        if (stringtocheck == "None") or (stringtocheck.isdigit()):
            lineedittocheck.setStyleSheet("background: white;")
        elif "None".startswith(stringtocheck) and stringtocheck != "":
            lineedittocheck.setStyleSheet("background: yellow;")
        else:
            lineedittocheck.setStyleSheet("background: rgb(255, 0, 0);")
