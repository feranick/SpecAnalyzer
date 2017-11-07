'''
AcquisitionWindow
------------------
Class for providing a graphical user interface for 
Acqusition Window

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

import sys
from datetime import datetime
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QWidget, QAction,
    QVBoxLayout,QGridLayout,QLabel,QGraphicsView,QFileDialog,QStatusBar,QSpinBox,
    QGraphicsScene,QLineEdit,QMessageBox,QDialog,QDialogButtonBox,QMenuBar,QCheckBox)
from PyQt5.QtGui import (QIcon,QImage,QKeySequence,QPixmap,QPainter,QDoubleValidator)
from PyQt5.QtCore import (pyqtSlot,QRectF,QRect)

from . import logger

'''
   Acquisition Window
'''
class AcquisitionWindow(QMainWindow):
    def __init__(self, parent=None):
        super(AcquisitionWindow, self).__init__(parent)
        self.initUI(self)
    
    # Setup UI elements
    def initUI(self,MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setGeometry(10, 290, 340, 500)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QRect(10, 30, 330, 236))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setObjectName("gridLayout")

        self.steadyStatLabel = QLabel(self.centralwidget)
        self.steadyStatLabel.setGeometry(QRect(10, 10, 111, 16))
        
        self.minVLabel = QLabel(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.minVLabel, 0, 0, 1, 1)
        self.minVText = QLineEdit(self)
        self.gridLayout.addWidget(self.minVText, 0, 1, 1, 1)
        self.minVText.editingFinished.connect(self.validateVoltages)

        self.maxVLabel = QLabel(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.maxVLabel, 1, 0, 1, 1)
        self.maxVText = QLineEdit(self)
        self.gridLayout.addWidget(self.maxVText, 1, 1, 1, 1)
        self.maxVText.editingFinished.connect(self.validateVoltages)
        
        self.startVLabel = QLabel(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.startVLabel, 2, 0, 1, 1)
        self.startVText = QLineEdit(self)
        self.startVText.editingFinished.connect(self.validateVoltages)
        self.gridLayout.addWidget(self.startVText, 2, 1, 1, 1)

        self.stepVLabel = QLabel(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.stepVLabel, 3, 0, 1, 1)
        self.stepVText = QLineEdit(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.stepVText, 3, 1, 1, 1)
        
        self.gateVLabel = QLabel(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.gateVLabel, 4, 0, 1, 1)
        self.gateVText = QLineEdit(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.gateVText, 4, 1, 1, 1)
        
        self.holdTLabel = QLabel(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.holdTLabel, 5, 0, 1, 1)
        self.holdTText = QLineEdit(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.holdTText, 5, 1, 1, 1)
        
        self.numAverScansLabel = QLabel(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.numAverScansLabel, 6, 0, 1, 1)
        self.numAverScansText = QLineEdit(self)
        self.gridLayout.addWidget(self.numAverScansText, 6, 1, 1, 1)

        self.delayBeforeMeasLabel = QLabel(self.gridLayoutWidget)
        self.gridLayout.addWidget(self.delayBeforeMeasLabel, 7, 0, 1, 1)
        self.delayBeforeMeasText = QLineEdit(self)
        self.gridLayout.addWidget(self.delayBeforeMeasText, 7, 1, 1, 1)
        
        self.trackingLabel = QLabel(self.centralwidget)
        self.trackingLabel.setGeometry(QRect(10, 280, 160, 16))
        
        self.enableTrackingBox = QCheckBox(self.centralwidget)
        self.enableTrackingBox.setGeometry(QRect(160, 280, 87, 20))

        self.pvModeLabel = QLabel(self.centralwidget)
        self.pvModeLabel.setGeometry(QRect(10, 300, 160, 16))

        self.pvModeBox = QCheckBox(self.centralwidget)
        self.pvModeBox.setGeometry(QRect(160, 300, 87, 20))
        
        self.gridLayoutWidget_2 = QWidget(self.centralwidget)
        self.gridLayoutWidget_2.setGeometry(QRect(10, 320, 330, 181))
        self.gridLayout_2 = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setHorizontalSpacing(10)

        self.numPointsLabel = QLabel(self.gridLayoutWidget_2)
        self.gridLayout_2.addWidget(self.numPointsLabel, 0, 0, 1, 1)
        self.numPointsText = QSpinBox(self)
        self.gridLayout_2.addWidget(self.numPointsText, 0, 1, 1, 1)
        
        self.intervalLabel = QLabel(self.gridLayoutWidget_2)
        self.gridLayout_2.addWidget(self.intervalLabel, 1, 0, 1, 1)
        self.IntervalText = QLineEdit(self)
        self.gridLayout_2.addWidget(self.IntervalText, 1, 1, 1, 1)

        self.totTimePerDeviceLabel = QLabel(self.gridLayoutWidget_2)
        self.gridLayout_2.addWidget(self.totTimePerDeviceLabel, 2, 0, 1, 1)
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setGeometry(QRect(0, 0, 772, 22))
        self.menuBar.setObjectName("menubar")
        
        self.parent().viewWindowMenus(self.menuBar, self.parent())
        
        MainWindow.setMenuBar(self.menuBar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.statusBar().showMessage("Acquisition: Ready", 5000)
        
        MainWindow.setWindowTitle("Acquisition Window")
        self.steadyStatLabel.setText("<qt><b>Steady State</b></qt>")
        self.minVLabel.setText("Min Voltage [V]")
        self.maxVLabel.setText("Max Voltage [V]")
        self.startVLabel.setText("Start Voltage [V]")
        self.stepVLabel.setText("Step Voltage [V]")
        self.gateVLabel.setText("Gate Voltage - SMU3 [V]")
        self.holdTLabel.setText("Hold time [s]")
        self.numAverScansLabel.setText("Number of averaged scans ")
        self.delayBeforeMeasLabel.setText("Delays before measurements [sec]")
        self.trackingLabel.setText("<qt><b>Track Voc, Jsc, MPP: </b></qt>")
        self.pvModeLabel.setText("<qt><b>PV mode: </b></qt>")
        self.numPointsLabel.setText("Number of points")
        self.intervalLabel.setText("Interval")
        self.totTimePerDeviceLabel.setText("Total time per device")
        
        self.saveButton = QPushButton(self.centralwidget)
        self.saveButton.setGeometry(QRect(250, 390, 80, 60))
        self.saveButton.setText("Save")
        self.saveButton.clicked.connect(self.saveParameters)
        
        self.defaultButton = QPushButton(self.centralwidget)
        self.defaultButton.setGeometry(QRect(160, 390, 80, 60))
        self.defaultButton.setText("Default")
        self.defaultButton.clicked.connect(self.defaultParameters)
        
        self.initParameters()

        self.minVText.editingFinished.connect(self.timePerDevice)
        self.maxVText.editingFinished.connect(self.timePerDevice)
        self.stepVText.editingFinished.connect(self.timePerDevice)
        self.numAverScansText.editingFinished.connect(self.timePerDevice)
        self.delayBeforeMeasText.editingFinished.connect(self.timePerDevice)
        self.holdTText.editingFinished.connect(self.timePerDevice)
        
    # Save acquisition parameters in configuration ini
    def saveParameters(self):
        self.parent().config.conf['Acquisition']['acqMinVoltage'] = str(self.minVText.text())
        self.parent().config.conf['Acquisition']['acqMaxVoltage'] = str(self.maxVText.text())
        self.parent().config.conf['Acquisition']['acqStartVoltage'] = str(self.startVText.text())
        self.parent().config.conf['Acquisition']['acqStepVoltage'] = str(self.stepVText.text())
        self.parent().config.conf['Acquisition']['acqGateVoltage'] = str(self.gateVText.text())
        self.parent().config.conf['Acquisition']['acqHoldTime'] = str(self.holdTText.text())
        self.parent().config.conf['Acquisition']['acqNumAvScans'] = str(self.numAverScansText.text())
        self.parent().config.conf['Acquisition']['acqDelBeforeMeas'] = str(self.delayBeforeMeasText.text())
        self.parent().config.conf['Acquisition']['acqTrackNumPoints'] = str(self.numPointsText.value())
        self.parent().config.conf['Acquisition']['acqTrackInterval'] = str(self.IntervalText.text())
        self.parent().config.conf['Acquisition']['acqPVmode'] = str(self.pvModeBox.isChecked())

        self.parent().config.saveConfig(self.parent().config.configFile)
        self.parent().config.readConfig(self.parent().config.configFile)
        print("Acquisition parameters saved as default")
        logger.info("Acquisition parameters saved as default")
        self.timePerDevice()
    
    # Set default acquisition parameters from configuration ini
    def defaultParameters(self):
        self.parent().config.createConfig()
        self.parent().config.readConfig(self.parent().config.configFile)
        self.initParameters()
        print("Default acquisition parameters restored")
        logger.info("Default acquisition parameters restored")
        self.timePerDevice()

    # Populate acquisition panel with values from config
    def initParameters(self):
        self.minVText.setText(str(self.parent().config.acqMinVoltage))
        self.maxVText.setText(str(self.parent().config.acqMaxVoltage))
        self.startVText.setText(str(self.parent().config.acqStartVoltage))
        self.stepVText.setText(str(self.parent().config.acqStepVoltage))
        self.gateVText.setText(str(self.parent().config.acqGateVoltage))
        self.holdTText.setText(str(self.parent().config.acqHoldTime))
        self.numAverScansText.setText(str(self.parent().config.acqNumAvScans))
        self.delayBeforeMeasText.setText(str(self.parent().config.acqDelBeforeMeas))
        self.numPointsText.setValue(int(self.parent().config.acqTrackNumPoints))
        self.IntervalText.setText(str(self.parent().config.acqTrackInterval))
        self.pvModeBox.setChecked(eval(self.parent().config.conf['Acquisition']['acqPVmode']))
        self.timePerDevice()

    # Field validator for VStart
    def validateVoltages(self):
        maxV = 100
        minV = -100
        try:
            validateStartVoltage = QDoubleValidator(float(self.minVText.text()),
                                    float(self.maxVText.text()),1,self.startVText)
            validateMaxVoltage = QDoubleValidator(float(self.minVText.text()),
                                    maxV,1,self.maxVText)
            validateMinVoltage = QDoubleValidator(minV,
                                    float(self.maxVText.text()),1,self.minVText)
        except:
            pass
                                    
        if validateStartVoltage.validate(self.startVText.text(),1)[0] != 2 or \
            validateMaxVoltage.validate(self.maxVText.text(),1)[0] != 2 or \
            validateMinVoltage.validate(self.minVText.text(),1)[0] != 2:
            msg = "Sweep voltages (including Start) need to be \n between Vmin and Vmax"+\
                "\n\nPlease change Voltages in the Acquisition panel"
            reply = QMessageBox.question(self, 'Critical', msg, QMessageBox.Ok)
            self.show()

    # Calculate the measurement time per device
    def timePerDevice(self):
        try:
            timePerDevice = (len(np.arange(float(self.minVText.text())-1e-9,
                                      float(self.maxVText.text())+1e-9,
                                      float(self.stepVText.text()))) * \
                                      float(self.holdTText.text()) + \
                                      float(self.delayBeforeMeasText.text())) * \
                                      float(self.numAverScansText.text())
        except:
            timePerDevice = 0
        self.totTimePerDeviceLabel.setText(\
                "Total time per device: <qt><b>{0:0.1f}s</b></qt>".format(timePerDevice))
        
    # Enable and disable fields (flag is either True or False) during acquisition.
    def enableAcqPanel(self, flag):
        self.minVText.setEnabled(flag)
        self.maxVText.setEnabled(flag)
        self.startVText.setEnabled(flag)
        self.stepVText.setEnabled(flag)
        self.gateVText.setEnabled(flag)
        self.holdTText.setEnabled(flag)
        self.numAverScansText.setEnabled(flag)
        self.delayBeforeMeasText.setEnabled(flag)
        self.numPointsText.setEnabled(flag)
        self.IntervalText.setEnabled(flag)
        self.saveButton.setEnabled(flag)
        self.defaultButton.setEnabled(flag)
        self.enableTrackingBox.setEnabled(flag)
