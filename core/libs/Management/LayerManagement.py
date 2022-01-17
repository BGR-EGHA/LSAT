# -*- coding: utf-8 -*-

import logging


class LayerManagement:
    '''
    Layer management provide some additional properties which improve
    the indexing of the QTreeWidgetItems and QGraphicItems (aka canvas items)
    '''

    def __init__(self):
        self.treeContent = {}
        self.canvasContent = {}
        self.layerCount = 0

    def addCanvasContent(self, item, layerProperties):
        '''
        Adds an object and its attributes to the CanvasContent
        '''
        self.canvasContent[item] = layerProperties
        return self.canvasContent

    def addTreeContent(self, item, layerProperties):
        '''
        Adds an object and its attributes to the TreeContent
        '''
        self.treeContent[item] = layerProperties
        return self.treeContent

    def getPixmapItemByName(self, name):
        '''
        Return the pixmap item object by name
        '''
        for key, values in self.canvasContent.items():
            if values['Name'] == name:
                return key

    def getTreeItemByName(self, name):
        '''
        Return the tree widget item object by name
        '''
        for key, values in self.treeContent.items():
            if values['Name'] == name:
                return key

    def getLayerName(self, item):
        '''
        Returns the layer Name
        '''
        try:
            layerName = self.canvasContent[item]['Name']
        except BaseException:
            layerName = self.treeContent[item]['Name']
        return layerName

    def getLayerSourcePath(self, item):
        '''
        Returns the Layer source path
        '''
        try:
            sourcePath = self.canvasContent[item]['Source']
        except BaseException:
            sourcePath = self.treeContent[item]['Source']
        return sourcePath

    def removeTreeItemByName(self, name: str) -> None:
        '''
        Removes an item from the tree based on its name.
        '''
        key = self.getTreeItemByName(name)
        self.treeContent.pop(key)