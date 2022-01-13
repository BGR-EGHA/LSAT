# -*- coding: utf-8 -*-

from osgeo import gdal
import time
from PyQt5 import QtGui, QtCore, QtWidgets, QtNetwork
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import os
from core.libs.Management import Project_configuration as config
from core.libs.CustomFileDialog import CustomFileDialog
from core.widgets.LSAT_main.MainFrame_main import MainFrame
import core.resources.icons_rc
import configparser
import webbrowser

from core.uis.StartMenu_ui.StartMenu_ui import Ui_StartOptions


class MainForm(QMainWindow):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.ui = Ui_StartOptions()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon(':/icons/Icons/LSATLogo.png'))
        self.config = config.Configuration()
        # Set actions on mouse press event for Labels
        self.ui.openProjectLabel.mousePressEvent = self.openProjectLabel_clicked
        self.ui.newProjectLabel.mousePressEvent = self.newProjectLabel_clicked
        # Connects Menubar buttons to functions
        self.ui.actionLanguage.setIcon(QIcon(':/icons/Icons/language.png'))
        self.ui.actionHelp.setIcon(QIcon(':/icons/Icons/Help.png'))
        self.ui.actionAbout_LSAT.setIcon(QIcon(':/icons/Icons/Info.png'))
        self.ui.newProjectLabel.setIcon(QIcon(':/icons/Icons/new_project.png'))
        self.ui.newProjectLabel.setIconSize(QSize(100, 100))
        self.ui.openProjectLabel.setIcon(QIcon(':/icons/Icons/open_project.png'))
        self.ui.openProjectLabel.setIconSize(QSize(100, 100))
        self.ui.actionAbout_LSAT.triggered.connect(self.on_actionAbout_LSAT_clicked)
        self.ui.actionHelp.triggered.connect(self.on_actionHelp_clicked)
        self.ui.actionLanguage.triggered.connect(self.on_actionLanguage_clicked)
        self.mainFrame = MainFrame()
        # Read the config file to get projects
        self.listProjects = self.config.getProjects()
        i = 0

        # Create shortcuts for the listed projects
        for project in self.listProjects:
            if project:
                if i < 3:
                    self.comLinkButton = QCommandLinkButton(str(project))
                    icon = QIcon()
                    if os.path.exists(os.path.join(project, 'thumb.png')):
                        icon_path = os.path.join(project, 'thumb.png')
                    else:
                        icon_path = ":/icons/Icons/project_icon.png"
                    pixmap = QPixmap(icon_path)
                    icon.addPixmap(pixmap, QIcon.Normal, QtGui.QIcon.Off)
                    self.comLinkButton.setIcon(icon)
                    self.comLinkButton.setIconSize(QSize(100, 100))
                    self.comLinkButton.clicked.connect(self.Button_clicked)
                    self.ui.recentGroupBoxGridLayout.addWidget(self.comLinkButton, 5 + i, 1, 1, 4)
                    i += 1
                    project = None
        self.listProjects = None

    def Button_clicked(self):
        """
        Opens the selected project from the recent project list
        :return: None
        """
        button = self.sender()
        self.mainFrame.openProjectFromShortcut(str(button.text()))
        self.mainFrame.showMaximized()
        self.close()

    def openProjectLabel_clicked(self, event):
        """
        Launch the FileDialog to open a project
        :param event: mouse click event
        :return: None
        """
        project = self.mainFrame.on_open_project()
        if not project:
            return
        else:
            self.mainFrame.showMaximized()
            self.close()

    def newProjectLabel_clicked(self, event):
        """
        Opens the dialog to create a new project
        :param event: mouse click event
        :return:
        """
        new_project = self.mainFrame.createNewProject()
        if not new_project:
            return
        else:
            self.mainFrame.showMaximized()
            self.close()

    def on_actionLanguage_clicked(self):
        """
        Displays the Language settings.
        """
        self.mainFrame.on_languageSettings()

    def on_actionHelp_clicked(self):
        """
        Displays Documentation in a new browser tab.
        """
        path = os.path.abspath(os.path.join('docs', 'html', 'index.html'))
        webbrowser.open("file://" + path, new=2)

    def on_actionAbout_LSAT_clicked(self):
        """
        Shows information about LSAT its creation, purpose and how to contribute.
        """
        aboutLSAT = QMessageBox()
        aboutLSAT.setWindowTitle("About LSAT")
        aboutLSAT.setWindowIcon(QIcon(':/icons/Icons/Info.png'))
        aboutLSAT.setText(
            """<h2>Landslide Susceptibility Assessment Tools - Project Manager Suite v 1.0.0</h2>
        LSAT was primarily developed to conduct landslide susceptibility analyses, it is not
        limited to this issue and applies to any other research dealing with supervised spatial 
        binary classification.<br>
        The software is a product developed at Federal Institute for Geosciences and Natural
        Resources (BGR) <a href="www.bgr.bund.de/EN/">www.bgr.bund.de/EN/</a>.<br>
        The software is distributed on GitHub and BGR's homepage. If you encounter any problems
        while using LSAT PM, please use GitHub Issues to report it.<br>
        LSAT is released under the <a href="http://www.gnu.org/licenses/#GPL">GNU General Public License version 3</a><br>
        """)
        aboutLSAT.exec()


class Thread(QThread):
    """
    Thread instance, called whenever a new process is started.
    """
    barValueSignal = QtCore.pyqtSignal(int)
    finishSignal = QtCore.pyqtSignal()

    def __init__(self, function, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __del__(self):
        self.wait()

    def run(self):
        """
        Runs the received function in the thread. Emits a done
        signal when ready.
        :return: None
        """
        self.function(*self.args, **self.kwargs)
        self.finishSignal.emit()
        return

def start():
    """
    Gets called when LSAT starts.
    Pynsist (the installer for windows) needs an entryfunction to create a usable installer.
    """
    gdal.AllRegister()
    app = QApplication(sys.argv)
    splash_pix = QPixmap(':/icons/Icons/SplashScreen.png')
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    configuration = config.Configuration()
    translator = QTranslator()
    language = configuration.getLanguage()
    if language == "English":
        pass
    elif language == "中国":
        translator.load(os.path.join("core", "resources", "qt_cn.qm"))
    elif language == "Deutsch":
        translator.load(os.path.join("core", "resources", "qt_de.qm"))
    elif language == "Русский":
        translator.load(os.path.join("core", "resources", "qt_ru.qm"))

    app.installTranslator(translator)
    myapp = MainForm()
    app.installEventFilter(myapp)
    myapp.showMaximized()
    splash.finish(myapp)
    sys.exit(app.exec_())

if __name__ == "__main__":
    start()
