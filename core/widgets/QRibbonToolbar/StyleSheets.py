import sys
import os
import inspect
stylesheet_instance = None


def get_stylesheet(name):
    global stylesheet_instance
    if not stylesheet_instance:
        stylesheet_instance = Stylesheets()
    return stylesheet_instance.get_stylesheet(name)


class Stylesheets(object):
    def __init__(self):
        self._stylesheets = {}
        self.fullpath = os.path.dirname(os.path.abspath(inspect.getfile(self.make_stylesheet)))
        self.make_stylesheet("main", "main.css")
        self.make_stylesheet("Ribbon", "Ribbon.css")
        self.make_stylesheet("RibbonPane", "RibbonPane.css")
        self.make_stylesheet("StandardButton", "StandardButton.css")
        self.make_stylesheet("SmallButton", "SmallButton.css")

    def make_stylesheet(self, name, path):
        style_path = os.path.join(self.fullpath,
            path)
        with open(style_path) as data_file:
            stylesheet = data_file.read()

        self._stylesheets[name] = stylesheet

    def get_stylesheet(self, name):
        stylesheet = ""
        try:
            stylesheet = self._stylesheets[name]
        except KeyError:
            print("stylesheet " + name + " not found")
        return stylesheet
