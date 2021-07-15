# -*- coding: utf-8 -*-

import codecs
import os
import sys
from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import configparser


class Configuration:
    def __init__(self):
        self.configFilePath = "config.ini"
        if os.path.exists(self.configFilePath):
            self.readConfigfile()
            self.validateProjectList()

        else:
            self.createDefaultConfigFile()
            self.readConfigfile()

    def readConfigfile(self):
        self.config = configparser.ConfigParser()
        self.config.read(str(self.configFilePath), encoding="utf-8")

    def validateProjectList(self):
        '''
        Checks if the projects in the list exist and updates the project list
        '''
        projects = self.config["DEFAULT"]["projects"].split(";")
        new_list = []
        for path in projects:
            if os.path.exists(path):
                path = os.path.normpath(path)
                new_list.append(path)
            else:
                pass
        if projects != new_list:
            self.updateProjectList(new_list)

    def getLanguage(self):
        '''
        Returns the project language specified in the config file.
        :return:
        string Language
        '''
        lang = self.config["DEFAULT"]["language"]
        return lang

    def getProjects(self):
        '''
        Returns project paths from config file.
        '''
        path_list = self.config["DEFAULT"]["projects"].split(";")
        return path_list

    def updateProjectList(self, new_list):
        '''
        Updates the existing project list.
        '''
        self.config["DEFAULT"]["projects"] = ";".join(map(str, new_list))
        with codecs.open("config.ini", 'w', "utf-8") as configfile:
            self.config.write(configfile)
        return

    def updateLanguage(self, language):
        """
        Overwrites the language
        :param language: string specified language
        :return: None
        """
        self.config["DEFAULT"]["language"] = str(language)
        with codecs.open("config.ini", 'w', "utf-8") as configfile:
            self.config.write(configfile)
        return

    def createDefaultConfigFile(self):
        """
        Creates a default config file
        """
        config = configparser.ConfigParser()
        config["DEFAULT"] = {"Projects": "",
                             "Language": "English",
                             }
        with codecs.open("config.ini", 'w', "utf-8") as configfile:
            config.write(configfile)
