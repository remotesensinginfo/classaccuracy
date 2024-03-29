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

from builtins import str
from builtins import range
import os

from qgis.PyQt import QtCore, QtGui
from PyQt5 import QtWidgets as QW
import qgis.utils
import numpy
import csv
from qgis.core import QgsVectorLayerUtils

MESSAGE_TIMEOUT = 20000
FEAT_BUFFER = 0.02


class ClassNamesQComboBox(QW.QComboBox):
    
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
            self.nextFeatSignal.emit()


class ClassAccuracyMainDialog(QW.QDialog):
    
    def __init__(self, parent=None):
        """Constructor."""
        QW.QWidget.__init__(self, parent)
        # Set window size. 
        self.resize(320, 240)

        # Set window title  
        self.setWindowTitle("Accuracy Assessment Tool") 
        
        # Create mainLayout
        self.mainLayout = QW.QVBoxLayout()
        
        self.guiLabelStep1 = QW.QLabel()
        self.guiLabelStep1.setText("1. Select a Vector Layer:")
        self.mainLayout.addWidget(self.guiLabelStep1)
        
        self.availLayersCombo = QW.QComboBox()
        self.availLayersCombo.currentIndexChanged['QString'].connect(self.populateLayerInfo)
        self.mainLayout.addWidget(self.availLayersCombo)
        
        self.guiLabelStep2 = QW.QLabel()
        self.guiLabelStep2.setText("2. Select Columns:")
        self.mainLayout.addWidget(self.guiLabelStep2)
        
        self.classNameComboLabel = QW.QLabel()
        self.classNameComboLabel.setText("Classified Column:")
        self.classNameCombo = QW.QComboBox()
        self.classNameLayout = QW.QHBoxLayout()
        self.classNameLayout.addWidget(self.classNameComboLabel)
        self.classNameLayout.addWidget(self.classNameCombo)
        self.mainLayout.addLayout(self.classNameLayout)
        
        self.classNameOutComboLabel = QW.QLabel()
        self.classNameOutComboLabel.setText("Output Column:")
        self.classNameOutCombo = QW.QComboBox()
        self.classNameOutLayout = QW.QHBoxLayout()
        self.classNameOutLayout.addWidget(self.classNameOutComboLabel)
        self.classNameOutLayout.addWidget(self.classNameOutCombo)
        self.mainLayout.addLayout(self.classNameOutLayout)
        
        self.featProcessedComboLabel = QW.QLabel()
        self.featProcessedComboLabel.setText("Processed Column:")
        self.featProcessedCombo = QW.QComboBox()
        self.featProcessedLayout = QW.QHBoxLayout()
        self.featProcessedLayout.addWidget(self.featProcessedComboLabel)
        self.featProcessedLayout.addWidget(self.featProcessedCombo)
        self.mainLayout.addLayout(self.featProcessedLayout)
        
        self.visitProcessedCheckBox = QW.QCheckBox("Visit Processed Points")
        self.visitProcessedCheckBox.setCheckState(QtCore.Qt.Unchecked)
        self.visitProcessedLayout = QW.QHBoxLayout()
        self.visitProcessedLayout.addWidget(self.visitProcessedCheckBox)
        self.mainLayout.addLayout(self.visitProcessedLayout)
        
        self.guiLabelStep3 = QW.QLabel()
        self.guiLabelStep3.setText("3. Press Start when ready:")
        self.mainLayout.addWidget(self.guiLabelStep3)
        
        # Start and Finish buttons
        self.startButton = QW.QPushButton(self)
        self.startButton.setText("Start")
        self.startButton.setDefault(True)
        #self.connect(self.startButton, QtCore.SIGNAL("clicked()"), self.startProcessing)
        self.startButton.clicked.connect(self.startProcessing)

        self.finishButton = QW.QPushButton(self)
        self.finishButton.setText("Finish")
        #self.connect(self.finishButton, QtCore.SIGNAL("clicked()"), self.finishProcessing)
        #self.connect(self.finishButton, QtCore.SIGNAL("clicked()"), self.reject)
        self.finishButton.clicked.connect(self.finishProcessing)
        self.finishButton.clicked.connect(self.reject)

        self.mainButtonLayout = QW.QHBoxLayout()
        self.mainButtonLayout.addWidget(self.finishButton)
        self.mainButtonLayout.addWidget(self.startButton)
        self.mainLayout.addLayout(self.mainButtonLayout)
        
        self.guiLabelStep4 = QW.QLabel()
        self.guiLabelStep4.setText("4. Go through the features (Press Return for Next):")
        self.mainLayout.addWidget(self.guiLabelStep4)
        
        # next and prev buttons
        self.nextButton = QW.QPushButton(self)
        self.nextButton.setText("Next")
        #self.connect(self.nextButton, QtCore.SIGNAL("clicked()"), self.nextFeat)
        self.nextButton.clicked.connect(self.nextFeat)
        self.nextButton.setDisabled(True)

        self.prevButton = QW.QPushButton(self)
        self.prevButton.setText("Prev")
        #self.connect(self.prevButton, QtCore.SIGNAL("clicked()"), self.prevFeat)
        self.prevButton.clicked.connect(self.prevFeat)
        self.prevButton.setDisabled(True)

        self.ctrlButtonLayout = QW.QHBoxLayout()
        self.ctrlButtonLayout.addWidget(self.prevButton)
        self.ctrlButtonLayout.addWidget(self.nextButton)
        self.mainLayout.addLayout(self.ctrlButtonLayout)
        
        self.assignButton = QW.QPushButton(self)
        self.assignButton.setText("Assign")
        #self.connect(self.assignButton, QtCore.SIGNAL("clicked()"), self.assignFeats)
        self.assignButton.clicked.connect(self.assignFeats)
        self.assignButton.setDisabled(True)
        self.assignButtonLayout = QW.QHBoxLayout()
        self.assignButtonLayout.addWidget(self.assignButton)
        self.mainLayout.addLayout(self.assignButtonLayout)
        
        self.guiLabelStep4b = QW.QLabel()
        self.guiLabelStep4b.setText("4. Or go direct to a feature (index starts at 1):")
        self.mainLayout.addWidget(self.guiLabelStep4b)
        self.goToLabel = QW.QLabel()
        self.goToLabel.setText("Go to Feature (ID):")
        self.goToTextField = QW.QLineEdit()
        self.goToTextField.setDisabled(True)
        self.goToButton = QW.QPushButton(self)
        self.goToButton.setText("Go To")
        #self.connect(self.goToButton, QtCore.SIGNAL("clicked()"), self.goToFeat)
        self.goToButton.clicked.connect(self.goToFeat)
        self.goToButton.setDisabled(True)
        self.goToLayout = QW.QHBoxLayout()
        self.goToLayout.addWidget(self.goToLabel)
        self.goToLayout.addWidget(self.goToTextField)
        self.goToLayout.addWidget(self.goToButton)
        self.mainLayout.addLayout(self.goToLayout)
        
        self.guiLabelStep5 = QW.QLabel()
        self.guiLabelStep5.setText("5. Change class if incorrect:")
        self.mainLayout.addWidget(self.guiLabelStep5)
        
        # classified and correct combo options
        self.fidLabel = QW.QLabel()
        self.fidLabel.setDisabled(True)
        self.classifiedLabel = QW.QLabel()
        self.classifiedLabel.setDisabled(True)
        self.classesCombo = ClassNamesQComboBox()
        self.classesCombo.setDisabled(True)
        self.classesCombo.nextFeatSignal.connect(self.nextFeat) 
        
        self.classesInfoLayout = QW.QHBoxLayout()
        self.classesInfoLayout.addWidget(self.fidLabel)
        self.classesInfoLayout.addWidget(self.classifiedLabel)
        self.classesInfoLayout.addWidget(self.classesCombo)
        self.mainLayout.addLayout(self.classesInfoLayout)

        self.guiLabelStep6 = QW.QLabel()
        self.guiLabelStep6.setText("6. Add extra classes to the list:")
        self.mainLayout.addWidget(self.guiLabelStep6)
        
        self.addClassLabel = QW.QLabel()
        self.addClassLabel.setText("Class Name:")
        self.addClassField = QW.QLineEdit()
        self.addClassField.setDisabled(True)
        self.addClassButton = QW.QPushButton(self)
        self.addClassButton.setText("Add")
        #self.connect(self.addClassButton, QtCore.SIGNAL("clicked()"), self.addClassName)
        self.addClassButton.clicked.connect(self.addClassName)
        self.addClassButton.setDisabled(True)
        self.addClassLayout = QW.QHBoxLayout()
        self.addClassLayout.addWidget(self.addClassLabel)
        self.addClassLayout.addWidget(self.addClassField)
        self.addClassLayout.addWidget(self.addClassButton)
        self.mainLayout.addLayout(self.addClassLayout)

        self.guiLabelStep7 = QW.QLabel()
        self.guiLabelStep7.setText("7. Change scale:")
        self.mainLayout.addWidget(self.guiLabelStep7)
        
        self.cScaleBuffer = FEAT_BUFFER
        
        self.scaleOptionsTextLine = QW.QLineEdit()
        self.scaleOptionsTextLine.setText(str(self.cScaleBuffer))
        self.scaleOptionsTextLine.setDisabled(True)
        self.changeScaleButton = QW.QPushButton(self)
        self.changeScaleButton.setText("Update")
        #self.connect(self.changeScaleButton, QtCore.SIGNAL("clicked()"), self.updateScale)
        self.changeScaleButton.clicked.connect(self.updateScale)
        self.changeScaleButton.setDisabled(True)
        self.scaleLayout = QW.QHBoxLayout()
        self.scaleLayout.addWidget(self.scaleOptionsTextLine)
        self.scaleLayout.addWidget(self.changeScaleButton)
        self.mainLayout.addLayout(self.scaleLayout)
        
        self.guiLabelStep8 = QW.QLabel()
        self.guiLabelStep8.setText("8. Produce Error Matrix:")
        self.mainLayout.addWidget(self.guiLabelStep8)
        
        self.calcErrorMatrixButton = QW.QPushButton(self)
        self.calcErrorMatrixButton.setText("Calc Error Matrix")
        #self.connect(self.calcErrorMatrixButton, QtCore.SIGNAL("clicked()"), self.calcErrMatrix)
        self.calcErrorMatrixButton.clicked.connect(self.calcErrMatrix)
        self.calcErrorMatrixButton.setDisabled(True)
        self.mainLayout.addWidget(self.calcErrorMatrixButton)
        
        self.setLayout(self.mainLayout)
                
        self.started = False
        self.justAssigned = False

    
    def populateLayers(self):
        """ Initialise layers list """
        self.availLayersCombo.clear()
        self.classNameCombo.clear()
        self.classNameOutCombo.clear()
        self.featProcessedCombo.clear()
        
        qgisIface = qgis.utils.iface
        mCanvas = qgisIface.mapCanvas()
        
        allLayers = mCanvas.layers()
        first = True
        for layer in allLayers:
            self.availLayersCombo.addItem(str(layer.name()))
                    
    def populateLayerInfo(self, selectedName):
        """ Populate the layer information from the selected layer """
        self.classNameCombo.clear()
        self.classNameOutCombo.clear()
        self.featProcessedCombo.clear()

        qgisIface = qgis.utils.iface
        mCanvas = qgisIface.mapCanvas()
        
        allLayers = mCanvas.layers()
        found = False
        fieldNames = list()
        for layer in allLayers:
            if layer.name() == selectedName:
                layerFields = layer.fields() #pendingFields
                numFields = layerFields.size()
                for i in range(numFields):
                    field = layerFields.field(i)
                    if field not in fieldNames:
                        self.classNameCombo.addItem(str(field.name()))
                        self.classNameOutCombo.addItem(str(field.name()))
                        self.featProcessedCombo.addItem(str(field.name()))
                        fieldNames.append(field)
                found = True
                break

    def startProcessing(self):
        """ Starting Processing """
        if not self.started:
            
            qgisIface = qgis.utils.iface
                    
            mCanvas = qgisIface.mapCanvas()
            mCanvas.setSelectionColor( QtGui.QColor("yellow") )
            
            selectedIdx = self.availLayersCombo.currentIndex()
            selectedName = self.availLayersCombo.itemText(selectedIdx)
            
            self.selectedClassFieldIdx = self.classNameCombo.currentIndex()
            self.selectedClassFieldName = self.classNameCombo.itemText(self.selectedClassFieldIdx)
            
            self.selectedClassOutFieldIdx = self.classNameOutCombo.currentIndex()
            self.selectedClassOutFieldName = self.classNameOutCombo.itemText(self.selectedClassOutFieldIdx)
            
            self.selectedFeatProcessedFieldIdx = self.featProcessedCombo.currentIndex()
            self.selectedFeatProcessedFieldName = self.featProcessedCombo.itemText(self.selectedFeatProcessedFieldIdx)
            
            allLayers = mCanvas.layers()
            found = False
            for layer in allLayers:
                if layer.name() == selectedName:
                    self.featLayer = layer
                    break
            
            self.selectedClassFieldIdx = self.featLayer.fields().indexFromName(self.selectedClassFieldName)
            self.selectedClassFieldOutIdx = self.featLayer.fields().indexFromName(self.selectedClassOutFieldName)
            self.selectedFeatProcessedFieldIdx = self.featLayer.fields().indexFromName(self.selectedFeatProcessedFieldName)
            
            self.onlyGoToUnProcessedFeats = True
            if self.visitProcessedCheckBox.checkState() == QtCore.Qt.Checked:
                self.onlyGoToUnProcessedFeats = False
            
            self.classNamesTmpList = QgsVectorLayerUtils.getValues(self.featLayer, self.selectedClassFieldName)
            self.classNamesList = list(set(self.classNamesTmpList[0]))
                        
            classOutNamesTmpList = QgsVectorLayerUtils.getValues(self.featLayer, self.selectedClassOutFieldName)
            classOutNamesList = list(set(classOutNamesTmpList[0]))
            
            for classOutName in classOutNamesList:
                if (not classOutName in self.classNamesList) and (not classOutName == 'NULL') and (not classOutName == None):
                    self.classNamesList.append(str(classOutName))
            
            for className in self.classNamesList:
                self.classesCombo.addItem(str(className))
            
            self.numFeats = self.featLayer.featureCount()
            self.cFeatN = 0
            
            self.featLayer.selectByIds([])
            
            self.featIter = self.featLayer.getFeatures()
            self.cFeat = next(self.featIter)
            if self.cFeatN < self.numFeats:
                
                availFeats = True
                if self.onlyGoToUnProcessedFeats:
                    foundUnProcessedFeat = False
                    while not foundUnProcessedFeat:
                        if int(self.cFeat[self.selectedFeatProcessedFieldIdx]) == 0:
                            foundUnProcessedFeat = True
                        else:
                            self.cFeatN = self.cFeatN + 1
                            if self.cFeatN < self.numFeats:
                                self.cFeat = next(self.featIter)
                            else:
                                availFeats = False
                                break
                
                if availFeats:
                    self.featLayer.startEditing()
                    self.featLayer.selectByIds([self.cFeat.id()])
                    
                    cClassName = str(self.cFeat[self.selectedClassFieldIdx])
                    self.classifiedLabel.setText(cClassName)
                    
                    outClassName = str(self.cFeat[self.selectedClassOutFieldIdx])
                    if (outClassName == None) or (outClassName.strip() == "") or (not (outClassName.strip() in self.classNamesList)):
                        self.classesCombo.setCurrentIndex(self.classNamesList.index(cClassName))
                    else:
                        self.classesCombo.setCurrentIndex(self.classNamesList.index(outClassName))               
                    
                    self.fidLabel.setText(str(self.cFeat.id()+1) + " of " + str(self.numFeats))
                    
                    box = self.featLayer.boundingBoxOfSelected()
                    box = box.buffered(self.cScaleBuffer)
                    mCanvas.setExtent(box)
                    mCanvas.refresh()
                    
                    self.nextButton.setEnabled(True)
                    self.nextButton.setDefault(True) 
                    self.prevButton.setEnabled(True)
                    self.assignButton.setEnabled(True)
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
                    self.calcErrorMatrixButton.setEnabled(True)
                    
                    self.startButton.setDisabled(True)
                    self.availLayersCombo.setDisabled(True)
                    self.classNameCombo.setDisabled(True)
                    self.classNameOutCombo.setDisabled(True)
                    self.featProcessedCombo.setDisabled(True)
                    self.visitProcessedCheckBox.setDisabled(True)
                
            else:
                self.featLayer.commitChanges()
                
                self.startButton.setEnabled(True)
                self.startButton.setDefault(True) 
                self.availLayersCombo.setEnabled(True)
                self.classNameCombo.setEnabled(True)
                self.classNameOutCombo.setEnabled(True)
                self.featProcessedCombo.setEnabled(True)
                self.visitProcessedCheckBox.setEnabled(True)
                
                self.nextButton.setDisabled(True)
                self.prevButton.setDisabled(True)
                self.assignButton.setDisabled(True)
                self.classifiedLabel.setDisabled(True)
                self.classesCombo.setDisabled(True)
                self.goToButton.setDisabled(True)
                self.goToTextField.setDisabled(True)
                self.changeScaleButton.setDisabled(True)
                self.scaleOptionsTextLine.setDisabled(True)
                self.addClassButton.setDisabled(True)
                self.addClassField.setDisabled(True)
            
            if availFeats:
                self.started = True  
    
    def nextFeat(self):
        """ Get the next feat """
        if self.started:
            if not self.justAssigned:
                selectedOutClassIdx = self.classesCombo.currentIndex()
                selectedOutClassName = self.classesCombo.itemText(selectedOutClassIdx)
                
                self.featLayer.changeAttributeValue(self.cFeat.id(), self.selectedClassOutFieldIdx, selectedOutClassName)
                self.featLayer.changeAttributeValue(self.cFeat.id(), self.selectedFeatProcessedFieldIdx, 1)
                
                self.featLayer.commitChanges()
                self.featLayer.startEditing()
            
                self.featLayer.selectByIds([])
            self.justAssigned = False
            
            ## Move on to the next feature...
            self.cFeatN = self.cFeatN + 1
            if self.cFeatN < self.numFeats:
                self.cFeat = next(self.featIter)
                
                availFeats = True
                if self.onlyGoToUnProcessedFeats:
                    foundUnProcessedFeat = False
                    while not foundUnProcessedFeat:
                        if self.cFeat[self.selectedFeatProcessedFieldIdx] == 0:
                            foundUnProcessedFeat = True
                        else:
                            self.cFeatN = self.cFeatN + 1
                            if self.cFeatN < self.numFeats:
                                self.cFeat = next(self.featIter)
                            else:
                                availFeats = False
                                break
                
                if availFeats:           
                    self.featLayer.selectByIds([self.cFeat.id()])
                    self.fidLabel.setText(str(self.cFeat.id()+1) + " of " + str(self.numFeats))
                    
                    cClassName = str(self.cFeat[self.selectedClassFieldIdx])
                    self.classifiedLabel.setText(cClassName)
                    
                    outClassName = str(self.cFeat[self.selectedClassOutFieldIdx])
                    if (outClassName == None) or (outClassName.strip() == "") or (not (outClassName.strip() in self.classNamesList)):
                        self.classesCombo.setCurrentIndex(self.classNamesList.index(cClassName))
                    else:
                        self.classesCombo.setCurrentIndex(self.classNamesList.index(outClassName))
                    
                    box = self.featLayer.boundingBoxOfSelected()
                    box = box.buffered(self.cScaleBuffer)
                    qgisIface = qgis.utils.iface        
                    mCanvas = qgisIface.mapCanvas()
                    mCanvas.setExtent(box)
                    mCanvas.refresh()
                else:
                    self.featLayer.commitChanges()
                
                    self.startButton.setEnabled(True)
                    self.startButton.setDefault(True) 
                    self.availLayersCombo.setEnabled(True)
                    self.classNameCombo.setEnabled(True)
                    self.classNameOutCombo.setEnabled(True)
                    self.featProcessedCombo.setEnabled(True)
                    self.visitProcessedCheckBox.setEnabled(True)
                    
                    self.nextButton.setDisabled(True)
                    self.prevButton.setDisabled(True)
                    self.assignButton.setDisabled(True)
                    self.classifiedLabel.setDisabled(True)
                    self.classesCombo.setDisabled(True)
                    self.goToButton.setDisabled(True)
                    self.goToTextField.setDisabled(True)
                    self.changeScaleButton.setDisabled(True)
                    self.scaleOptionsTextLine.setDisabled(True)
                    self.addClassButton.setDisabled(True)
                    self.addClassField.setDisabled(True)
                
            else:
                self.featLayer.commitChanges()
                
                self.startButton.setEnabled(True)
                self.startButton.setDefault(True) 
                self.availLayersCombo.setEnabled(True)
                self.classNameCombo.setEnabled(True)
                self.classNameOutCombo.setEnabled(True)
                self.featProcessedCombo.setEnabled(True)
                self.visitProcessedCheckBox.setEnabled(True)
                
                self.nextButton.setDisabled(True)
                self.prevButton.setDisabled(True)
                self.assignButton.setDisabled(True)
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
            self.featLayer.selectByIds([])
            
            self.featIter = self.featLayer.getFeatures()
            self.cFeat = next(self.featIter)
            numFeats2Process = self.cFeatN - 1
            self.cFeatN = 0
            
            for i in range(numFeats2Process):
                self.cFeat = next(self.featIter)
                self.cFeatN = self.cFeatN + 1
            
            self.featLayer.selectByIds([self.cFeat.id()])
            self.fidLabel.setText(str(self.cFeat.id()+1) + " of " + str(self.numFeats))
            
            cClassName = str(self.cFeat[self.selectedClassFieldIdx])
            self.classifiedLabel.setText(cClassName)
            
            outClassName = str(self.cFeat[self.selectedClassOutFieldIdx])
            if (outClassName == None) or (outClassName.strip() == "") or (not (outClassName.strip() in self.classNamesList)):
                self.classesCombo.setCurrentIndex(self.classNamesList.index(cClassName))
            else:
                self.classesCombo.setCurrentIndex(self.classNamesList.index(outClassName))
            
            box = self.featLayer.boundingBoxOfSelected()
            box = box.buffered(self.cScaleBuffer)
            qgisIface = qgis.utils.iface        
            mCanvas = qgisIface.mapCanvas()
            mCanvas.setExtent(box)
            mCanvas.refresh()
    
    def assignFeats(self):
        if self.started:
            selectedOutClassIdx = self.classesCombo.currentIndex()
            selectedOutClassName = self.classesCombo.itemText(selectedOutClassIdx)
            
            selFeats = self.featLayer.selectedFeatures()
            for selFeat in selFeats:            
                self.featLayer.changeAttributeValue(selFeat.id(), self.selectedClassOutFieldIdx, selectedOutClassName)
                self.featLayer.changeAttributeValue(selFeat.id(), self.selectedFeatProcessedFieldIdx, 1)
            
            self.featLayer.commitChanges()
            self.featLayer.startEditing()
            
            self.featLayer.selectByIds([])
            
            self.cFeatN = 0
            self.featIter = self.featLayer.getFeatures()
            self.cFeat = next(self.featIter)
            
            self.featLayer.selectByIds([self.cFeat.id()])
            self.fidLabel.setText(str(self.cFeat.id()+1) + " of " + str(self.numFeats))
            
            self.justAssigned = True

        

    def goToFeat(self):
        if self.started:
            self.featLayer.selectByIds([])
            
            self.featIter = self.featLayer.getFeatures()
            self.cFeat = next(self.featIter)
            numFeats2Process = int(self.goToTextField.text())-1
            if numFeats2Process < 0:
                numFeats2Process = 0
            elif numFeats2Process >= self.numFeats:
                numFeats2Process = self.numFeats-1
            self.cFeatN = 0
            
            for i in range(numFeats2Process):
                self.cFeat = next(self.featIter)
                self.cFeatN = self.cFeatN + 1
            
            self.featLayer.selectByIds([self.cFeat.id()])
            self.fidLabel.setText(str(self.cFeat.id()+1) + " of " + str(self.numFeats))
            
            cClassName = str(self.cFeat[self.selectedClassFieldIdx])
            self.classifiedLabel.setText(cClassName)
            
            outClassName = str(self.cFeat[self.selectedClassOutFieldIdx])
            if (outClassName == None) or (outClassName.strip() == "") or (not (outClassName.strip() in self.classNamesList)):
                self.classesCombo.setCurrentIndex(self.classNamesList.index(cClassName))
            else:
                self.classesCombo.setCurrentIndex(self.classNamesList.index(outClassName))
            
            box = self.featLayer.boundingBoxOfSelected()
            box = box.buffered(self.cScaleBuffer)
            qgisIface = qgis.utils.iface        
            mCanvas = qgisIface.mapCanvas()
            mCanvas.setExtent(box)
            mCanvas.refresh()
            self.classesCombo.setFocus()
    
    def addClassName(self):
        if self.started:
            classNameTmp = self.addClassField.text()
            if (not classNameTmp == "") or (not classNameTmp == None):
                self.classNamesList.append(classNameTmp)
                self.classesCombo.addItem(classNameTmp)
                self.classesCombo.setCurrentIndex(self.classNamesList.index(classNameTmp))
            self.classesCombo.setFocus()


    def updateScale(self):
        if self.started:
            self.cScaleBuffer = float(self.scaleOptionsTextLine.text())
            
            box = self.featLayer.boundingBoxOfSelected()
            box = box.buffered(self.cScaleBuffer)
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
            self.featProcessedCombo.setEnabled(True)
            self.visitProcessedCheckBox.setEnabled(True)
            
            self.nextButton.setDisabled(True)
            self.prevButton.setDisabled(True)
            self.assignButton.setDisabled(True)
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
    
    def calcErrMatrix(self):
        if self.started:
            self.featLayer.commitChanges()
        
            self.startButton.setEnabled(True)
            self.startButton.setDefault(True) 
            self.availLayersCombo.setEnabled(True)
            self.classNameCombo.setEnabled(True)
            self.classNameOutCombo.setEnabled(True)
            self.featProcessedCombo.setEnabled(True)
            self.visitProcessedCheckBox.setEnabled(True)
            
            self.nextButton.setDisabled(True)
            self.prevButton.setDisabled(True)
            self.assignButton.setDisabled(True)
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
        
        outCSVFilePath = QW.QFileDialog.getSaveFileName(self, 'SaveErrorMatrixCSV', '', 'CSV(*.csv)') #(self, 'Save Error Matrix CSV', '', '*.csv')
        if outCSVFilePath:
            featsClassNamesImgList = QgsVectorLayerUtils.getValues(self.featLayer, self.selectedClassFieldName)[0]
            featsClassNamesGrdList = QgsVectorLayerUtils.getValues(self.featLayer, self.selectedClassOutFieldName)[0]
            numClasses = len(self.classNamesList)
                        
            errMatrix = numpy.zeros((numClasses,numClasses), dtype=float)
            
            for i in range(self.numFeats):
                imgClass = featsClassNamesImgList[i]
                imgClassIdx = self.classNamesList.index(imgClass)
                grdClass = featsClassNamesGrdList[i]
                grdClassIdx = self.classNamesList.index(grdClass)
                errMatrix[imgClassIdx,grdClassIdx] = errMatrix[imgClassIdx,grdClassIdx] + 1

            errMatrixPercent = (errMatrix / numpy.sum(errMatrix)) * 100

            producerAcc = numpy.zeros(numClasses, dtype=float)
            userAcc = numpy.zeros(numClasses, dtype=float)
            producerAccCount = numpy.zeros(numClasses, dtype=float)
            userAccCount = numpy.zeros(numClasses, dtype=float)
            overallCorrCount = 0.0
            
            for i in range(numClasses):
                corVal = float(errMatrix[i,i])
                sumRow = float(numpy.sum(errMatrix[i,]))
                sumCol = float(numpy.sum(errMatrix[...,i]))
                overallCorrCount = overallCorrCount + corVal
                if sumRow == 0:
                    userAcc[i] = 0
                    userAccCount[i] = 0
                else:
                    userAcc[i] = corVal / sumRow
                    userAccCount[i] = sumRow
                if sumCol == 0:
                    producerAcc[i] = 0
                    producerAccCount[i] = 0
                else:
                    producerAcc[i] = corVal / sumCol
                    producerAccCount[i] = sumCol
            
            overallAcc = (overallCorrCount / numpy.sum(errMatrix)) * 100
            producerAcc = producerAcc * 100
            userAcc = userAcc * 100
            
            kappaPartA = overallCorrCount * numpy.sum(producerAccCount)
            kappaPartB = numpy.sum(userAccCount * producerAccCount)
            kappaPartC = numpy.sum(errMatrix) * numpy.sum(errMatrix)

            kappa = float(kappaPartA - kappaPartB) / float(kappaPartC - kappaPartB)
                        
            with open(outCSVFilePath[0], 'w') as csvfile: #(outCSVFilePath, 'wb')
                accWriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                
                accWriter.writerow(['Overall Accuracy (%)', round(overallAcc,2)])
                accWriter.writerow(['kappa', round(kappa,2)])
                
                accWriter.writerow([])
                accWriter.writerow(['Counts:'])
                
                colNames = [' ']
                for i in range(numClasses):
                    colNames.append(self.classNamesList[i])
                colNames.append('User')
                accWriter.writerow(colNames)
                
                for i in range(numClasses):
                    row = []
                    row.append(self.classNamesList[i])
                    for j in range(numClasses):
                        row.append(errMatrix[i,j])
                    row.append(round(userAccCount[i],2))
                    accWriter.writerow(row)
                
                prodRow = ['Producer']
                for i in range(numClasses):
                    prodRow.append(round(producerAccCount[i],2))
                prodRow.append(overallCorrCount)
                accWriter.writerow(prodRow)
                
                accWriter.writerow([])
                accWriter.writerow(['Percentage:'])
                
                colNames = [' ']
                for i in range(numClasses):
                    colNames.append(self.classNamesList[i])
                colNames.append('User (%)')
                accWriter.writerow(colNames)
                
                for i in range(numClasses):
                    row = []
                    row.append(self.classNamesList[i])
                    for j in range(numClasses):
                        row.append(round(errMatrixPercent[i,j],2))
                    row.append(round(userAcc[i],2))
                    accWriter.writerow(row)
                
                prodRow = ['Producer (%)']
                for i in range(numClasses):
                    prodRow.append(round(producerAcc[i],2))
                prodRow.append(round(overallAcc,2))
                accWriter.writerow(prodRow)

