# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ClassAccuracyMainDialog
                                 A QGIS plugin
 Manually review the accuracy of a classification
                             -------------------
        begin                : 2015-08-15
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Pete Bunting
        email                : pfb@aber.ac.uk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtCore, QtGui
import qgis.utils

MESSAGE_TIMEOUT = 20000
FEAT_BUFFER = 100

class ClassAccuracyMainDialog(QtGui.QDialog):
    
    def __init__(self, parent=None):
        """Constructor."""
        QtGui.QWidget.__init__(self, parent)
        # Set window size. 
        self.resize(320, 240)

        # Set window title  
        self.setWindowTitle("Accuracy Assessment Tool") 
        
        # Create mainLayout
        self.mainLayout = QtGui.QVBoxLayout()
        
        self.availLayersCombo = QtGui.QComboBox()
        self.availLayersCombo.currentIndexChanged['QString'].connect(self.populateLayerInfo)
        self.mainLayout.addWidget(self.availLayersCombo)
                
        self.classNameCombo = QtGui.QComboBox()
        self.mainLayout.addWidget(self.classNameCombo)
        
        self.classNameOutCombo = QtGui.QComboBox()
        self.mainLayout.addWidget(self.classNameOutCombo)
        
        # ok and cancel buttons
        self.startButton = QtGui.QPushButton(self)
        self.startButton.setText("Start")
        self.startButton.setDefault(True)
        self.connect(self.startButton, QtCore.SIGNAL("clicked()"), self.startProcessing)

        self.finishButton = QtGui.QPushButton(self)
        self.finishButton.setText("Finish")
        self.connect(self.finishButton, QtCore.SIGNAL("clicked()"), self.finishProcessing)
        self.connect(self.finishButton, QtCore.SIGNAL("clicked()"), self.reject)

        self.mainButtonLayout = QtGui.QHBoxLayout()
        self.mainButtonLayout.addWidget(self.finishButton)
        self.mainButtonLayout.addWidget(self.startButton)
        self.mainLayout.addLayout(self.mainButtonLayout)
        
        
        # next and prev buttons
        self.nextButton = QtGui.QPushButton(self)
        self.nextButton.setText("Next")
        self.connect(self.nextButton, QtCore.SIGNAL("clicked()"), self.nextFeat)
        self.nextButton.setDisabled(True)

        self.prevButton = QtGui.QPushButton(self)
        self.prevButton.setText("Prev")
        self.connect(self.prevButton, QtCore.SIGNAL("clicked()"), self.prevFeat)
        self.prevButton.setDisabled(True)

        self.ctrlButtonLayout = QtGui.QHBoxLayout()
        self.ctrlButtonLayout.addWidget(self.prevButton)
        self.ctrlButtonLayout.addWidget(self.nextButton)
        self.mainLayout.addLayout(self.ctrlButtonLayout)
        
        
        # classified and correct combo options
        self.fidLabel = QtGui.QLabel()
        self.fidLabel.setDisabled(True)
        self.classifiedLabel = QtGui.QLabel()
        self.classifiedLabel.setDisabled(True)
        self.classesCombo = QtGui.QComboBox()
        self.classesCombo.setDisabled(True)
        
        self.classesInfoLayout = QtGui.QHBoxLayout()
        self.classesInfoLayout.addWidget(self.fidLabel)
        self.classesInfoLayout.addWidget(self.classifiedLabel)
        self.classesInfoLayout.addWidget(self.classesCombo)
        self.mainLayout.addLayout(self.classesInfoLayout)

        self.setLayout(self.mainLayout)
                
        self.started = False

    
    def populateLayers(self):
        """ dsfsd """
        self.availLayersCombo.clear()
        self.classNameCombo.clear()
        self.classNameOutCombo.clear()
        
        qgisIface = qgis.utils.iface
        
        mCanvas = qgisIface.mapCanvas()
        
        allLayers = mCanvas.layers()
        first = True
        for layer in allLayers:
            self.availLayersCombo.addItem(layer.name())
            if first:
                first = False
                layerFields = layer.pendingFields()
                numFields = layerFields.size()
                for i in range(numFields):
                    field = layerFields.field(i)
                    self.classNameCombo.addItem(field.name())
                    self.classNameOutCombo.addItem(field.name())
                    
    def populateLayerInfo(self, selectedName):
        """ jklsjfsdlk """
        #print(selectedName)
        self.classNameCombo.clear()
        self.classNameOutCombo.clear()

        qgisIface = qgis.utils.iface
        
        mCanvas = qgisIface.mapCanvas()
        
        allLayers = mCanvas.layers()
        found = False
        for layer in allLayers:
            if layer.name() == selectedName:
                layerFields = layer.pendingFields()
                numFields = layerFields.size()
                for i in range(numFields):
                    field = layerFields.field(i)
                    self.classNameCombo.addItem(field.name())
                    self.classNameOutCombo.addItem(field.name())
                found = True
                break

    def startProcessing(self):
        """ Starting Processing """
        if not self.started:
            print("Starting processing...")
            
            qgisIface = qgis.utils.iface
                    
            mCanvas = qgisIface.mapCanvas()
            mCanvas.setSelectionColor( QtGui.QColor("red") )
            
            selectedIdx = self.availLayersCombo.currentIndex()
            selectedName = self.availLayersCombo.itemText(selectedIdx)
            print(selectedName)
            
            self.selectedClassFieldIdx = self.classNameCombo.currentIndex()
            self.selectedClassFieldName = self.classNameCombo.itemText(self.selectedClassFieldIdx)
            print(self.selectedClassFieldName)
            
            self.selectedClassOutFieldIdx = self.classNameOutCombo.currentIndex()
            self.selectedClassOutFieldName = self.classNameOutCombo.itemText(self.selectedClassOutFieldIdx)
            print(self.selectedClassOutFieldName)        
                    
            allLayers = mCanvas.layers()
            found = False
            for layer in allLayers:
                if layer.name() == selectedName:
                    self.featLayer = layer
                    break
            
            self.selectedClassFieldIdx = self.featLayer.fieldNameIndex(self.selectedClassFieldName)
            self.selectedClassFieldOutIdx = self.featLayer.fieldNameIndex(self.selectedClassOutFieldName)
            
            classNamesTmpList = self.featLayer.getValues(self.selectedClassFieldName)
            
            self.classNamesList = list(set(classNamesTmpList[0]))
            print(self.classNamesList)
            for className in self.classNamesList:
                self.classesCombo.addItem(className)
            
            self.numFeats = self.featLayer.featureCount()
            self.cFeatN = 0
            
            self.featLayer.setSelectedFeatures([])
            
            self.featIter = self.featLayer.getFeatures()
            self.cFeat = self.featIter.next()
            if self.cFeatN < self.numFeats:
                self.featLayer.startEditing()
                
                self.featLayer.setSelectedFeatures([self.cFeat.id()])
                
                cClassName = str(self.cFeat[self.selectedClassFieldIdx])
                print("cClassName: ", cClassName)
                self.classifiedLabel.setText(cClassName)
                
                outClassName = str(self.cFeat[self.selectedClassOutFieldIdx])
                print("outClassName: ", outClassName)
                if (outClassName == None) or (outClassName.strip() == "") or (not (outClassName.strip() in self.classNamesList)):
                    self.classesCombo.setCurrentIndex(self.classNamesList.index(cClassName))
                else:
                    self.classesCombo.setCurrentIndex(self.classNamesList.index(outClassName))
                
                #self.cFeat[self.selectedClassFieldIdx]
                
                
                print("Feature ID : ", self.cFeat.id())
                self.fidLabel.setText(str(self.cFeat.id()+1) + " of " + str(self.numFeats))
                
                box = self.featLayer.boundingBoxOfSelected()
                box = box.buffer(FEAT_BUFFER)
                mCanvas.setExtent(box)
                mCanvas.refresh()
                
                self.nextButton.setEnabled(True)
                self.nextButton.setDefault(True) 
                self.prevButton.setEnabled(True)
                self.classifiedLabel.setEnabled(True)
                self.fidLabel.setEnabled(True)
                self.classesCombo.setEnabled(True)
                
                self.startButton.setDisabled(True)
                self.availLayersCombo.setDisabled(True)
                self.classNameCombo.setDisabled(True)
                self.classNameOutCombo.setDisabled(True)
                
            else:
                print("Processed all features...")
    
            self.started = True  
    
    def nextFeat(self):
        print("Next Feature")
        if self.started:
            ## Update the input layer
            selectedOutClassIdx = self.classesCombo.currentIndex()
            selectedOutClassName = self.classesCombo.itemText(selectedOutClassIdx)
            
            self.featLayer.changeAttributeValue(self.cFeat.id(), self.selectedClassOutFieldIdx, selectedOutClassName, "")
            
            self.featLayer.commitChanges()
            self.featLayer.startEditing()
            
            ## Move on to the next feature...
            self.featLayer.setSelectedFeatures([])
            self.cFeatN = self.cFeatN + 1
            if self.cFeatN < self.numFeats:
                self.cFeat = self.featIter.next()
                self.featLayer.setSelectedFeatures([self.cFeat.id()])
                print("Feature ID : ", self.cFeat.id())
                self.fidLabel.setText(str(self.cFeat.id()+1) + " of " + str(self.numFeats))
                
                cClassName = str(self.cFeat[self.selectedClassFieldIdx])
                print("cClassName: ", cClassName)
                self.classifiedLabel.setText(cClassName)
                
                outClassName = str(self.cFeat[self.selectedClassOutFieldIdx])
                print("outClassName: ", outClassName)
                if (outClassName == None) or (outClassName.strip() == "") or (not (outClassName.strip() in self.classNamesList)):
                    self.classesCombo.setCurrentIndex(self.classNamesList.index(cClassName))
                else:
                    self.classesCombo.setCurrentIndex(self.classNamesList.index(outClassName))
                
                box = self.featLayer.boundingBoxOfSelected()
                box = box.buffer(FEAT_BUFFER)
                qgisIface = qgis.utils.iface        
                mCanvas = qgisIface.mapCanvas()
                mCanvas.setExtent(box)
                mCanvas.refresh() 
            else:
                print("Processed all features...")
                self.featLayer.commitChanges()
                
                self.startButton.setEnabled(True)
                self.startButton.setDefault(True) 
                self.availLayersCombo.setEnabled(True)
                self.classNameCombo.setEnabled(True)
                self.classNameOutCombo.setEnabled(True)
                
                self.nextButton.setDisabled(True)
                self.prevButton.setDisabled(True)
                self.classifiedLabel.setDisabled(True)
                self.classesCombo.setDisabled(True)
        
        
    def prevFeat(self):
        if self.started:
            print("Prev Feature")
            self.featLayer.setSelectedFeatures([])
            
            self.featIter = self.featLayer.getFeatures()
            self.cFeat = self.featIter.next()
            numFeats2Process = self.cFeatN - 1
            self.cFeatN = 0
            
            for i in range(numFeats2Process):
                self.cFeat = self.featIter.next()
                self.cFeatN = self.cFeatN + 1
            
            self.featLayer.setSelectedFeatures([self.cFeat.id()])
            print("Feature ID : ", self.cFeat.id())
            self.fidLabel.setText(str(self.cFeat.id()+1) + " of " + str(self.numFeats))
            
            cClassName = str(self.cFeat[self.selectedClassFieldIdx])
            print("cClassName: ", cClassName)
            self.classifiedLabel.setText(cClassName)
            
            outClassName = str(self.cFeat[self.selectedClassOutFieldIdx])
            print("outClassName: ", outClassName)
            if (outClassName == None) or (outClassName.strip() == "") or (not (outClassName.strip() in self.classNamesList)):
                self.classesCombo.setCurrentIndex(self.classNamesList.index(cClassName))
            else:
                self.classesCombo.setCurrentIndex(self.classNamesList.index(outClassName))
            
            box = self.featLayer.boundingBoxOfSelected()
            box = box.buffer(FEAT_BUFFER)
            qgisIface = qgis.utils.iface        
            mCanvas = qgisIface.mapCanvas()
            mCanvas.setExtent(box)
            mCanvas.refresh()



    def finishProcessing(self):
        if self.started:
            self.featLayer.commitChanges()
        
            self.startButton.setEnabled(True)
            self.startButton.setDefault(True) 
            self.availLayersCombo.setEnabled(True)
            self.classNameCombo.setEnabled(True)
            self.classNameOutCombo.setEnabled(True)
            
            self.nextButton.setDisabled(True)
            self.prevButton.setDisabled(True)
            self.classifiedLabel.setDisabled(True)
            self.fidLabel.setDisabled(True)
            self.classesCombo.setDisabled(True)
        self.started = False        


