# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\StartMenu.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_StartOptions(object):
    def setupUi(self, StartOptions):
        StartOptions.setObjectName("StartOptions")
        StartOptions.resize(1000, 750)
        self.centralwidget = QtWidgets.QWidget(StartOptions)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.mainGridLayout = QtWidgets.QGridLayout()
        self.mainGridLayout.setObjectName("mainGridLayout")
        self.startGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.startGroupBox.setObjectName("startGroupBox")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.startGroupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.startGroupBoxGridLayout = QtWidgets.QGridLayout()
        self.startGroupBoxGridLayout.setObjectName("startGroupBoxGridLayout")
        self.openProjectLabel = QtWidgets.QCommandLinkButton(self.startGroupBox)
        self.openProjectLabel.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.openProjectLabel.setObjectName("openProjectLabel")
        self.startGroupBoxGridLayout.addWidget(self.openProjectLabel, 1, 0, 1, 1)
        self.newProjectLabel = QtWidgets.QCommandLinkButton(self.startGroupBox)
        self.newProjectLabel.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.newProjectLabel.setCheckable(False)
        self.newProjectLabel.setObjectName("newProjectLabel")
        self.startGroupBoxGridLayout.addWidget(self.newProjectLabel, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.startGroupBoxGridLayout.addItem(spacerItem, 2, 0, 1, 1)
        self.webViewGroupBox = QtWidgets.QGroupBox(self.startGroupBox)
        self.webViewGroupBox.setTitle("")
        self.webViewGroupBox.setObjectName("webViewGroupBox")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.webViewGroupBox)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.LSATtextBrowser = QtWidgets.QTextBrowser(self.webViewGroupBox)
        self.LSATtextBrowser.setFocusPolicy(QtCore.Qt.NoFocus)
        self.LSATtextBrowser.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.LSATtextBrowser.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.LSATtextBrowser.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.LSATtextBrowser.setAutoFormatting(QtWidgets.QTextEdit.AutoNone)
        self.LSATtextBrowser.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse)
        self.LSATtextBrowser.setOpenExternalLinks(True)
        self.LSATtextBrowser.setObjectName("LSATtextBrowser")
        self.verticalLayout_4.addWidget(self.LSATtextBrowser)
        self.startGroupBoxGridLayout.addWidget(self.webViewGroupBox, 0, 1, 3, 1)
        self.startGroupBoxGridLayout.setColumnStretch(0, 1)
        self.startGroupBoxGridLayout.setColumnStretch(1, 6)
        self.verticalLayout_3.addLayout(self.startGroupBoxGridLayout)
        self.mainGridLayout.addWidget(self.startGroupBox, 0, 0, 1, 1)
        self.recentProjectsGroupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.recentProjectsGroupBox.setObjectName("recentProjectsGroupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.recentProjectsGroupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.recentGroupBoxGridLayout = QtWidgets.QGridLayout()
        self.recentGroupBoxGridLayout.setObjectName("recentGroupBoxGridLayout")
        self.verticalLayout_2.addLayout(self.recentGroupBoxGridLayout)
        self.mainGridLayout.addWidget(self.recentProjectsGroupBox, 1, 0, 1, 1)
        self.mainGridLayout.setRowStretch(0, 3)
        self.mainGridLayout.setRowStretch(1, 2)
        self.verticalLayout.addLayout(self.mainGridLayout)
        StartOptions.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(StartOptions)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1000, 22))
        self.menubar.setObjectName("menubar")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuAbout = QtWidgets.QMenu(self.menubar)
        self.menuAbout.setObjectName("menuAbout")
        self.menuSettings = QtWidgets.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        StartOptions.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(StartOptions)
        self.statusbar.setObjectName("statusbar")
        StartOptions.setStatusBar(self.statusbar)
        self.actionGeneral_settings = QtWidgets.QAction(StartOptions)
        self.actionGeneral_settings.setObjectName("actionGeneral_settings")
        self.actionHelp = QtWidgets.QAction(StartOptions)
        self.actionHelp.setObjectName("actionHelp")
        self.actionAbout_LSAT = QtWidgets.QAction(StartOptions)
        self.actionAbout_LSAT.setObjectName("actionAbout_LSAT")
        self.actionLanguage = QtWidgets.QAction(StartOptions)
        self.actionLanguage.setObjectName("actionLanguage")
        self.actionNetwork = QtWidgets.QAction(StartOptions)
        self.actionNetwork.setObjectName("actionNetwork")
        self.menuHelp.addAction(self.actionHelp)
        self.menuAbout.addAction(self.actionAbout_LSAT)
        self.menuSettings.addAction(self.actionLanguage)
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(StartOptions)
        QtCore.QMetaObject.connectSlotsByName(StartOptions)

    def retranslateUi(self, StartOptions):
        _translate = QtCore.QCoreApplication.translate
        StartOptions.setWindowTitle(_translate("StartOptions", "Landslide Susceptibility Assessment Tools - Project Manager Suite v 1.0.0"))
        self.startGroupBox.setTitle(_translate("StartOptions", "Start Options"))
        self.openProjectLabel.setText(_translate("StartOptions", "Open Project"))
        self.newProjectLabel.setText(_translate("StartOptions", "New Project"))
        self.LSATtextBrowser.setHtml(_translate("StartOptions", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:7.875pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:600;\">LSAT</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Calibri,sans-serif\'; font-size:12pt; font-weight:600;\">Landslide Susceptibility Assessment Tools</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt; font-weight:600;\">Version 1.0.0</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Get the current Version of LSAT from </span><a href=\"https://github.com/BGR-EGHA/LSAT\"><span style=\" font-size:8pt; text-decoration: underline; color:#0000ff;\">our GitHub</span></a></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">View the </span><a href=\"/docs/html/index.html\"><span style=\" font-size:8pt; text-decoration: underline; color:#0000ff;\">Help Content</span></a></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">Visit our website </span><a href=\"https://www.bgr.bund.de/EN/Themen/Erdbeben-Gefaehrdungsanalysen/Massenbewegungen/ingenieurgeologische_gefaehrdungsanalysen_node_en.html\"><span style=\" font-size:8pt; text-decoration: underline; color:#0000ff;\">BGR - Engineering Geological Hazard Assessment</span></a></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">LSAT is licensed under the </span><a href=\"https://www.gnu.org/licenses/gpl-3.0.html\"><span style=\" font-size:8pt; text-decoration: underline; color:#0000ff;\">GNU General Public License</span></a></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p></body></html>"))
        self.recentProjectsGroupBox.setTitle(_translate("StartOptions", "Recent Projects"))
        self.menuHelp.setTitle(_translate("StartOptions", "Help"))
        self.menuAbout.setTitle(_translate("StartOptions", "About"))
        self.menuSettings.setTitle(_translate("StartOptions", "Settings"))
        self.actionGeneral_settings.setText(_translate("StartOptions", "General settings..."))
        self.actionHelp.setText(_translate("StartOptions", "LSAT-Help"))
        self.actionAbout_LSAT.setText(_translate("StartOptions", "About LSAT"))
        self.actionLanguage.setText(_translate("StartOptions", "Language"))
        self.actionNetwork.setText(_translate("StartOptions", "Network"))
