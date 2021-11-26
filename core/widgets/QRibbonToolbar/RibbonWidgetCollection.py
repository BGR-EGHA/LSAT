# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from core.widgets.QRibbonToolbar.StyleSheets import get_stylesheet

# Adjusts scales on high DPI Displays from
# https://stackoverflow.com/questions/39247342/pyqt-gui-size-on-high-resolution-screens
if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


def gui_scale():
    return 1


class QRibbonWidget(QToolBar):
    def __init__(self, parent):
        QToolBar.__init__(self, parent)
        self.setStyleSheet(get_stylesheet("Ribbon"))
        self.setObjectName("ribbonWidget")
        self.setWindowTitle("Toolbar")
        self.ribbonWidget = QTabWidget(self)
        self.ribbonWidget.setMaximumHeight(120 * gui_scale())
        self.ribbonWidget.setMinimumHeight(110 * gui_scale())
        self.setMovable(False)
        self.addWidget(self.ribbonWidget)

    def addRibbonTab(self, name):
        """
        Generates a tab with specified name and adds to the ribbon widget.
        :param name: str name of the tab
        :return: QWidget ribbon tab
        """
        ribbonTab = QRibbonTab(self, name)
        ribbonTab.setObjectName("tab_" + str(name))
        self.ribbonWidget.addTab(ribbonTab, name)
        return ribbonTab

    def set_active(self, name):
        """
        Sets the tab active
        :param name: str name of the tab
        :return: None
        """
        self.setCurrentWidget(self.findChild("tab_" + str(name)))


class QRibbonTab(QWidget):
    def __init__(self, parent, name):
        QWidget.__init__(self, parent)
        self.tabLayout = QHBoxLayout()
        self.setLayout(self.tabLayout)
        self.tabLayout.setContentsMargins(0, 0, 0, 0)
        self.tabLayout.setSpacing(0)
        self.tabLayout.setAlignment(Qt.AlignLeft)

    def addRibbonPane(self, name, type="Horizontal"):
        ribbonPane = QRibbonPane(self, name, type)
        self.tabLayout.addWidget(ribbonPane)
        return ribbonPane

    def addSpacer(self):
        self.tabLayout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.MinimumExpanding))
        self.tabLayout.setStretch(self.tabLayout.count() - 1, 1)


class QRibbonButton(QToolButton):
    def __init__(self, button, action, buttonSizeFlag="StandardButton"):
        QToolButton.__init__(self, button)
        self.buttonAction = action
        if buttonSizeFlag == "StandardButton":
            label = QLabel(self.buttonAction.text(), self)
            label.setWordWrap(True)
            label.setAlignment(Qt.AlignCenter)
            layout = QHBoxLayout(self)
            layout.addWidget(label, 0, Qt.AlignCenter | Qt.AlignBottom)
        else:
            self.setText(self.buttonAction.text())
        self.updateButtonStatusFromAction()
        self.clicked.connect(self.buttonAction.trigger)
        self.buttonAction.changed.connect(self.updateButtonStatusFromAction)

        if buttonSizeFlag == "StandardButton":
            self.setMaximumWidth(80 * gui_scale())
            self.setMinimumWidth(80 * gui_scale())
            self.setMinimumHeight(80 * gui_scale())
            self.setMaximumHeight(80 * gui_scale())
            self.setStyleSheet(get_stylesheet("StandardButton"))
            self.setToolButtonStyle(3)
            self.setIconSize(QSize(40 * gui_scale(), 40 * gui_scale()))
        elif buttonSizeFlag == "SmallButton":
            self.setToolButtonStyle(2)
            self.setMaximumWidth(150 * gui_scale())
            self.setIconSize(QSize(20 * gui_scale(), 20 * gui_scale()))
            self.setStyleSheet(get_stylesheet("SmallButton"))

    def updateButtonStatusFromAction(self):
        self.setStatusTip(self.buttonAction.statusTip())
        self.setToolTip(self.buttonAction.toolTip())
        self.setIcon(self.buttonAction.icon())
        self.setEnabled(self.buttonAction.isEnabled())
        self.setCheckable(self.buttonAction.isCheckable())
        self.setChecked(self.buttonAction.isChecked())


class QRibbonPane(QWidget):
    def __init__(self, parent, name, type="Horizontal"):
        QWidget.__init__(self, parent)
        self.type = type
        self.setStyleSheet(get_stylesheet("RibbonPane"))
        horizontal_layout = QHBoxLayout()
        horizontal_layout.setSpacing(5)
        horizontal_layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(horizontal_layout)
        vertical_widget = QWidget(self)
        horizontal_layout.addWidget(vertical_widget)
        horizontal_layout.addWidget(QRibbonSeparator(self))
        vertical_layout = QVBoxLayout()
        vertical_layout.setSpacing(0)
        vertical_layout.setContentsMargins(0, 0, 0, 0)
        vertical_widget.setLayout(vertical_layout)
        label = QLabel(name)
        label.setAlignment(Qt.AlignCenter | Qt.AlignBottom)
        label.setStyleSheet("color:#666;")

        content_widget = QWidget(self)
        vertical_layout.addWidget(content_widget)
        vertical_layout.addWidget(label)
        if self.type == "Horizontal":
            content_layout = QHBoxLayout()
        else:
            content_layout = QGridLayout()
        content_layout.setAlignment(Qt.AlignLeft)
        content_layout.setSpacing(3)
        content_layout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout = content_layout
        content_widget.setLayout(content_layout)

    def addRibbonWidget(self, widget, pos=None):
        if self.type == "Horizontal":
            self.contentLayout.addWidget(widget, 0, Qt.AlignBottom)
        else:
            if pos is not None:
                a, b, c, d = pos
                self.contentLayout.addWidget(widget, a, b, c, d)
                self.contentLayout.setAlignment(Qt.AlignBottom | Qt.AlignLeft)

    def add_grid_widget(self, width):
        widget = QWidget()
        widget.setMaximumWidth(width)
        grid_layout = QGridLayout()
        widget.setLayout(grid_layout)
        grid_layout.setSpacing(4)
        grid_layout.setContentsMargins(4, 4, 4, 4)
        self.contentLayout.addWidget(widget)
        grid_layout.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        return grid_layout


class QRibbonSeparator(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setMinimumHeight(80)
        self.setMaximumHeight(80)
        self.setMinimumWidth(1)
        self.setMaximumWidth(1)
        self.setLayout(QHBoxLayout())

    def paintEvent(self, event):
        paint = QPainter()
        paint.begin(self)
        paint.fillRect(event.rect(), Qt.lightGray)
        paint.end()


class QRibbonCheckBox(QCheckBox):
    def __init__(self, box, label):
        QLineEdit.__init__(self, box)
        self.setText(label)
