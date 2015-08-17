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


class ClassNamesQComboBox(QtGui.QComboBox):
    
    nextFeatSignal = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super(ClassNamesQComboBox, self).__init__(parent)
        self.setEditable(False)

    def keyPressEvent(self, event):
        if (event.type() == QtCore.QEvent.KeyPress) and (event.key() == QtCore.Qt.Key_1):
            if self.count() > 0:
                self.setCurrentIndex(0)
        elif (event.type() == QtCore.QEvent.KeyPress) and (event.key() == QtCore.Qt.Key_2):
            if self.count() > 1:
                self.setCurrentIndex(1)
        elif (event.type() == QtCore.QEvent.KeyPress) and (event.key() == QtCore.Qt.Key_3):
            if self.count() > 2:
                self.setCurrentIndex(2)
        elif (event.type() == QtCore.QEvent.KeyPress) and (event.key() == QtCore.Qt.Key_4):
            if self.count() > 3:
                self.setCurrentIndex(3)
        elif (event.type() == QtCore.QEvent.KeyPress) and (event.key() == QtCore.Qt.Key_5):
            if self.count() > 4:
                self.setCurrentIndex(4)
        elif (event.type() == QtCore.QEvent.KeyPress) and (event.key() == QtCore.Qt.Key_6):
            if self.count() > 5:
                self.setCurrentIndex(5)
        elif (event.type() == QtCore.QEvent.KeyPress) and (event.key() == QtCore.Qt.Key_7):
            if self.count() > 6:
                self.setCurrentIndex(6)
        elif (event.type() == QtCore.QEvent.KeyPress) and (event.key() == QtCore.Qt.Key_8):
            if self.count() > 7:
                self.setCurrentIndex(7)
        elif (event.type() == QtCore.QEvent.KeyPress) and (event.key() == QtCore.Qt.Key_9):
            if self.count() > 8:
                self.setCurrentIndex(8)
        elif (event.type() == QtCore.QEvent.KeyPress) and (event.key() == QtCore.Qt.Key_0):
            if self.count() > 9:
                self.setCurrentIndex(9)
        elif (event.type() == QtCore.QEvent.KeyPress) and ((event.key() == QtCore.Qt.Key_Return) or (event.key() == QtCore.Qt.Key_Enter)):
            print("Go to Next - how to do that!?!")
            self.nextFeatSignal.emit()


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
        
        self.guiLabelStep1 = QtGui.QLabel()
        self.guiLabelStep1.setText("1. Select a Vector Layer:")
        self.mainLayout.addWidget(self.guiLabelStep1)
        
        self.availLayersCombo = QtGui.QComboBox()
        self.availLayersCombo.currentIndexChanged['QString'].connect(self.populateLayerInfo)
        self.mainLayout.addWidget(self.availLayersCombo)
        
        self.guiLabelStep2 = QtGui.QLabel()
        self.guiLabelStep2.setText("2. Select Columns:")
        self.mainLayout.addWidget(self.guiLabelStep2)
        
        self.classNameComboLabel = QtGui.QLabel()
        self.classNameComboLabel.setText("Classified Column:")
        self.classNameCombo = QtGui.QComboBox()
        self.classNameLayout = QtGui.QHBoxLayout()
        self.classNameLayout.addWidget(self.classNameComboLabel)
        self.classNameLayout.addWidget(self.classNameCombo)
        self.mainLayout.addLayout(self.classNameLayout)
        
        self.classNameOutComboLabel = QtGui.QLabel()
        self.classNameOutComboLabel.setText("Output Column:")
        self.classNameOutCombo = QtGui.QComboBox()
        self.classNameOutLayout = QtGui.QHBoxLayout()
        self.classNameOutLayout.addWidget(self.classNameOutComboLabel)
        self.classNameOutLayout.addWidget(self.classNameOutCombo)
        self.mainLayout.addLayout(self.classNameOutLayout)
        
        self.guiLabelStep3 = QtGui.QLabel()
        self.guiLabelStep3.setText("3. Press Start when ready:")
        self.mainLayout.addWidget(self.guiLabelStep3)
        
        # Start and Finish buttons
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
        
        self.guiLabelStep4 = QtGui.QLabel()
        self.guiLabelStep4.setText("4. Go through the features (Press Return for Next):")
        self.mainLayout.addWidget(self.guiLabelStep4)
        
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
        
        self.guiLabelStep4b = QtGui.QLabel()
        self.guiLabelStep4b.setText("4. Or go direct to a feature (index starts at 1):")
        self.mainLayout.addWidget(self.guiLabelStep4b)
        self.goToLabel = QtGui.QLabel()
        self.goToLabel.setText("Go to Feature (ID):")
        self.goToTextField = QtGui.QLineEdit()
        self.goToTextField.setDisabled(True)
        self.goToButton = QtGui.QPushButton(self)
        self.goToButton.setText("Go To")
        self.connect(self.goToButton, QtCore.SIGNAL("clicked()"), self.goToFeat)
        self.goToButton.setDisabled(True)
        self.goToLayout = QtGui.QHBoxLayout()
        self.goToLayout.addWidget(self.goToLabel)
        self.goToLayout.addWidget(self.goToTextField)
        self.goToLayout.addWidget(self.goToButton)
        self.mainLayout.addLayout(self.goToLayout)
        
        self.guiLabelStep5 = QtGui.QLabel()
        self.guiLabelStep5.setText("5. Change class if incorrect:")
        self.mainLayout.addWidget(self.guiLabelStep5)
        
        # classified and correct combo options
        self.fidLabel = QtGui.QLabel()
        self.fidLabel.setDisabled(True)
        self.classifiedLabel = QtGui.QLabel()
        self.classifiedLabel.setDisabled(True)
        self.classesCombo = ClassNamesQComboBox()
        self.classesCombo.setDisabled(True)
        self.classesCombo.nextFeatSignal.connect(self.nextFeat) 
        
        self.classesInfoLayout = QtGui.QHBoxLayout()
        self.classesInfoLayout.addWidget(self.fidLabel)
        self.classesInfoLayout.addWidget(self.classifiedLabel)
        self.classesInfoLayout.addWidget(self.classesCombo)
        self.mainLayout.addLayout(self.classesInfoLayout)

        self.guiLabelStep6 = QtGui.QLabel()
        self.guiLabelStep6.setText("6. Add extra classes to the list:")
        self.mainLayout.addWidget(self.guiLabelStep6)
        
        self.addClassLabel = QtGui.QLabel()
        self.addClassLabel.setText("Class Name:")
        self.addClassField = QtGui.QLineEdit()
        self.addClassField.setDisabled(True)
        self.addClassButton = QtGui.QPushButton(self)
        self.addClassButton.setText("Add")
        self.connect(self.addClassButton, QtCore.SIGNAL("clicked()"), self.addClassName)
        self.addClassButton.setDisabled(True)
        self.addClassLayout = QtGui.QHBoxLayout()
        self.addClassLayout.addWidget(self.addClassLabel)
        self.addClassLayout.addWidget(self.addClassField)
        self.addClassLayout.addWidget(self.addClassButton)
        self.mainLayout.addLayout(self.addClassLayout)

        self.guiLabelStep7 = QtGui.QLabel()
        self.guiLabelStep7.setText("7. Change scale:")
        self.mainLayout.addWidget(self.guiLabelStep7)
        
        self.cScaleBuffer = FEAT_BUFFER
        
        self.scaleOptionsTextLine = QtGui.QLineEdit()
        self.scaleOptionsTextLine.setText(str(self.cScaleBuffer))
        self.scaleOptionsTextLine.setDisabled(True)
        self.changeScaleButton = QtGui.QPushButton(self)
        self.changeScaleButton.setText("Update")
        self.connect(self.changeScaleButton, QtCore.SIGNAL("clicked()"), self.updateScale)
        self.changeScaleButton.setDisabled(True)
        self.scaleLayout = QtGui.QHBoxLayout()
        self.scaleLayout.addWidget(self.scaleOptionsTextLine)
        self.scaleLayout.addWidget(self.changeScaleButton)
        self.mainLayout.addLayout(self.scaleLayout)
        

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
            #print("Starting processing...")
            
            qgisIface = qgis.utils.iface
                    
            mCanvas = qgisIface.mapCanvas()
            mCanvas.setSelectionColor( QtGui.QColor("red") )
            
            selectedIdx = self.availLayersCombo.currentIndex()
            selectedName = self.availLayersCombo.itemText(selectedIdx)
            #print(selectedName)
            
            self.selectedClassFieldIdx = self.classNameCombo.currentIndex()
            self.selectedClassFieldName = self.classNameCombo.itemText(self.selectedClassFieldIdx)
            #print(self.selectedClassFieldName)
            
            self.selectedClassOutFieldIdx = self.classNameOutCombo.currentIndex()
            self.selectedClassOutFieldName = self.classNameOutCombo.itemText(self.selectedClassOutFieldIdx)
            #print(self.selectedClassOutFieldName)        
                    
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
            #print(self.classNamesList)            
            
            classOutNamesTmpList = self.featLayer.getValues(self.selectedClassOutFieldName)
            classOutNamesList = list(set(classOutNamesTmpList[0]))
            #print(classOutNamesList)
            for classOutName in classOutNamesList:
                if (not classOutName in self.classNamesList) and (not classOutName == 'NULL') and (not classOutName == None):
                    self.classNamesList.append(classOutName)
            
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
                #print("cClassName: ", cClassName)
                self.classifiedLabel.setText(cClassName)
                
                outClassName = str(self.cFeat[self.selectedClassOutFieldIdx])
                #print("outClassName: ", outClassName)
                if (outClassName == None) or (outClassName.strip() == "") or (not (outClassName.strip() in self.classNamesList)):
                    self.classesCombo.setCurrentIndex(self.classNamesList.index(cClassName))
                else:
                    self.classesCombo.setCurrentIndex(self.classNamesList.index(outClassName))               
                
                #print("Feature ID : ", self.cFeat.id())
                self.fidLabel.setText(str(self.cFeat.id()+1) + " of " + str(self.numFeats))
                
                box = self.featLayer.boundingBoxOfSelected()
                box = box.buffer(self.cScaleBuffer)
                mCanvas.setExtent(box)
                mCanvas.refresh()
                
                self.nextButton.setEnabled(True)
                self.nextButton.setDefault(True) 
                self.prevButton.setEnabled(True)
                self.classifiedLabel.setEnabled(True)
                self.fidLabel.setEnabled(True)
                self.classesCombo.setEnabled(True)
                self.goToButton.setEnabled(True)
                self.goToTextField.setEnabled(True)
                self.classesCombo.setFocus()
                self.changeScaleButton.setEnabled(True)
                self.scaleOptionsTextLine.setEnabled(True)
                self.addClassButton.setEnabled(True)
                self.addClassField.setEnabled(True)
                
                self.startButton.setDisabled(True)
                self.availLayersCombo.setDisabled(True)
                self.classNameCombo.setDisabled(True)
                self.classNameOutCombo.setDisabled(True)
                
            else:
                #print("Processed all features...")
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
                self.goToButton.setDisabled(True)
                self.goToTextField.setDisabled(True)
                self.changeScaleButton.setDisabled(True)
                self.scaleOptionsTextLine.setDisabled(True)
                self.addClassButton.setDisabled(True)
                self.addClassField.setDisabled(True)
            self.started = True  
    
    def nextFeat(self):
        #print("Next Feature")
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
                #print("Feature ID : ", self.cFeat.id())
                self.fidLabel.setText(str(self.cFeat.id()+1) + " of " + str(self.numFeats))
                
                cClassName = str(self.cFeat[self.selectedClassFieldIdx])
                #print("cClassName: ", cClassName)
                self.classifiedLabel.setText(cClassName)
                
                outClassName = str(self.cFeat[self.selectedClassOutFieldIdx])
                #print("outClassName: ", outClassName)
                if (outClassName == None) or (outClassName.strip() == "") or (not (outClassName.strip() in self.classNamesList)):
                    self.classesCombo.setCurrentIndex(self.classNamesList.index(cClassName))
                else:
                    self.classesCombo.setCurrentIndex(self.classNamesList.index(outClassName))
                
                box = self.featLayer.boundingBoxOfSelected()
                box = box.buffer(self.cScaleBuffer)
                qgisIface = qgis.utils.iface        
                mCanvas = qgisIface.mapCanvas()
                mCanvas.setExtent(box)
                mCanvas.refresh() 
            else:
                #print("Processed all features...")
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
                self.goToButton.setDisabled(True)
                self.goToTextField.setDisabled(True)
                self.changeScaleButton.setDisabled(True)
                self.scaleOptionsTextLine.setDisabled(True)
                self.addClassButton.setDisabled(True)
                self.addClassField.setDisabled(True)
        
        
    def prevFeat(self):
        if self.started:
            #print("Prev Feature")
            self.featLayer.setSelectedFeatures([])
            
            self.featIter = self.featLayer.getFeatures()
            self.cFeat = self.featIter.next()
            numFeats2Process = self.cFeatN - 1
            self.cFeatN = 0
            
            for i in range(numFeats2Process):
                self.cFeat = self.featIter.next()
                self.cFeatN = self.cFeatN + 1
            
            self.featLayer.setSelectedFeatures([self.cFeat.id()])
            #print("Feature ID : ", self.cFeat.id())
            self.fidLabel.setText(str(self.cFeat.id()+1) + " of " + str(self.numFeats))
            
            cClassName = str(self.cFeat[self.selectedClassFieldIdx])
            #print("cClassName: ", cClassName)
            self.classifiedLabel.setText(cClassName)
            
            outClassName = str(self.cFeat[self.selectedClassOutFieldIdx])
            #print("outClassName: ", outClassName)
            if (outClassName == None) or (outClassName.strip() == "") or (not (outClassName.strip() in self.classNamesList)):
                self.classesCombo.setCurrentIndex(self.classNamesList.index(cClassName))
            else:
                self.classesCombo.setCurrentIndex(self.classNamesList.index(outClassName))
            
            box = self.featLayer.boundingBoxOfSelected()
            box = box.buffer(self.cScaleBuffer)
            qgisIface = qgis.utils.iface        
            mCanvas = qgisIface.mapCanvas()
            mCanvas.setExtent(box)
            mCanvas.refresh()

    def goToFeat(self):
        if self.started:
            #print("Go To Feature")
            self.featLayer.setSelectedFeatures([])
            
            self.featIter = self.featLayer.getFeatures()
            self.cFeat = self.featIter.next()
            numFeats2Process = int(self.goToTextField.text())-1
            if numFeats2Process < 0:
                numFeats2Process = 0
            elif numFeats2Process >= self.numFeats:
                numFeats2Process = self.numFeats-1
            self.cFeatN = 0
            
            for i in range(numFeats2Process):
                self.cFeat = self.featIter.next()
                self.cFeatN = self.cFeatN + 1
            
            self.featLayer.setSelectedFeatures([self.cFeat.id()])
            #print("Feature ID : ", self.cFeat.id())
            self.fidLabel.setText(str(self.cFeat.id()+1) + " of " + str(self.numFeats))
            
            cClassName = str(self.cFeat[self.selectedClassFieldIdx])
            #print("cClassName: ", cClassName)
            self.classifiedLabel.setText(cClassName)
            
            outClassName = str(self.cFeat[self.selectedClassOutFieldIdx])
            #print("outClassName: ", outClassName)
            if (outClassName == None) or (outClassName.strip() == "") or (not (outClassName.strip() in self.classNamesList)):
                self.classesCombo.setCurrentIndex(self.classNamesList.index(cClassName))
            else:
                self.classesCombo.setCurrentIndex(self.classNamesList.index(outClassName))
            
            box = self.featLayer.boundingBoxOfSelected()
            box = box.buffer(self.cScaleBuffer)
            qgisIface = qgis.utils.iface        
            mCanvas = qgisIface.mapCanvas()
            mCanvas.setExtent(box)
            mCanvas.refresh()
            self.classesCombo.setFocus()
    
    def addClassName(self):
        if self.started:
            #print("Add Class Name")
            classNameTmp = self.addClassField.text()
            if (not classNameTmp == "") or (not classNameTmp == None):
                self.classNamesList.append(classNameTmp)
                self.classesCombo.addItem(classNameTmp)
                self.classesCombo.setCurrentIndex(self.classNamesList.index(classNameTmp))
            self.classesCombo.setFocus()


    def updateScale(self):
        if self.started:
            self.cScaleBuffer = int(self.scaleOptionsTextLine.text())
            #print(self.cScaleBuffer)
            
            box = self.featLayer.boundingBoxOfSelected()
            box = box.buffer(self.cScaleBuffer)
            qgisIface = qgis.utils.iface        
            mCanvas = qgisIface.mapCanvas()
            mCanvas.setExtent(box)
            mCanvas.refresh()
            self.classesCombo.setFocus()
       
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
            self.goToButton.setDisabled(True)
            self.goToTextField.setDisabled(True)
            self.changeScaleButton.setDisabled(True)
            self.scaleOptionsTextLine.setDisabled(True)
            self.addClassButton.setDisabled(True)
            self.addClassField.setDisabled(True)
        self.started = False        


