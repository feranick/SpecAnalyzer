'''
mainWindow
-------------
Various classes for providing a graphical user interface

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''
import sys, webbrowser, random, time
import configparser
from datetime import datetime
import numpy as np
import pandas as pd

from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton,
    QWidget, QAction,QVBoxLayout,QGridLayout,QLabel,QGraphicsView,
    QFileDialog,QStatusBar,QGraphicsScene,QLineEdit,QMessageBox,
    QDialog,QToolBar,QMenuBar,QHeaderView,QMenu)
from PyQt5.QtGui import (QIcon,QImage,QKeySequence,QPixmap,QPainter)
from PyQt5.QtCore import (pyqtSlot,QRectF)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from . import __version__
from . import __author__
from . import logger

from .configuration import *
from .acquisition import *
from .sourcemeterWindow import *
from .results import *

'''
   Main Window
   Definition of Main Panel
'''
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__(None)
        self.config = Configuration()
        self.config.readConfig(self.config.configFile)
        self.initUI()
    
    # Define UI elements
    def initUI(self):
        logger.info("SpecAnalyzer v."+__version__)
        self.setWindowTitle("SpecAnalyzer %s" % __version__)
        self.setGeometry(10,30,1000,700)
        self.aboutwid = AboutWidget()
        self.acquisition = Acquisition(parent=self)
        self.results = Results(parent=self)
        self.sourcemeterwind = SourcemeterWindow(parent=self)
        self.weblinks = WebLinksWidget()

        self.centralwidget = QWidget(self)

        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QRect(10, 40, 950, 480))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.mainGridLayout = QGridLayout(self.gridLayoutWidget)
        self.mainGridLayout.setContentsMargins(0, 0, 0, 0)
        self.mainGridLayout.setObjectName("mainGridLayout")

        self.plotVLayout = QGridLayout()
        self.canvasJV = FigureCanvas(self.results.figureJV)
        self.toolbarJV = NavigationToolbar(self.canvasJV, self)
        self.plotVLayout.addWidget(self.toolbarJV)
        self.plotVLayout.addWidget(self.canvasJV)
        self.mainGridLayout.addLayout(self.plotVLayout, 0, 1, 1, 1)
        self.canvasJV.draw()

        self.gridLayout = QGridLayout()
        self.gridLayout.setContentsMargins(10, 1, 10, 1)
        self.gridLayout.setHorizontalSpacing(10)
        self.gridLayout.setObjectName("gridLayout")
        self.delayBeforeMeasText = QLineEdit(self.gridLayoutWidget)
        self.delayBeforeMeasText.setObjectName("delayBeforeMeasText")
        self.gridLayout.addWidget(self.delayBeforeMeasText, 5, 1, 1, 1)
        self.minVLabel = QLabel(self.gridLayoutWidget)
        self.minVLabel.setObjectName("minVLabel")
        self.gridLayout.addWidget(self.minVLabel, 0, 0, 1, 1)
        self.minVText = QLineEdit(self.gridLayoutWidget)
        self.minVText.setObjectName("minVText")
        self.gridLayout.addWidget(self.minVText, 0, 1, 1, 1)
        self.numAverScansText = QLineEdit(self.gridLayoutWidget)
        self.numAverScansText.setObjectName("numAverScansText")
        self.gridLayout.addWidget(self.numAverScansText, 4, 1, 1, 1)
        self.numAverScansLabel = QLabel(self.gridLayoutWidget)
        self.numAverScansLabel.setObjectName("numAverScansLabel")
        self.gridLayout.addWidget(self.numAverScansLabel, 4, 0, 1, 1)
        self.startVLabel = QLabel(self.gridLayoutWidget)
        self.startVLabel.setObjectName("startVLabel")
        self.gridLayout.addWidget(self.startVLabel, 2, 0, 1, 1)
        self.startVText = QLineEdit(self.gridLayoutWidget)
        self.startVText.setObjectName("startVText")
        self.gridLayout.addWidget(self.startVText, 2, 1, 1, 1)
        self.stepVLabel = QLabel(self.gridLayoutWidget)
        self.stepVLabel.setObjectName("stepVLabel")
        self.gridLayout.addWidget(self.stepVLabel, 3, 0, 1, 1)
        self.maxVText = QLineEdit(self.gridLayoutWidget)
        self.maxVText.setObjectName("maxVText")
        self.gridLayout.addWidget(self.maxVText, 1, 1, 1, 1)
        self.maxVLabel = QLabel(self.gridLayoutWidget)
        self.maxVLabel.setObjectName("maxVLabel")
        self.gridLayout.addWidget(self.maxVLabel, 1, 0, 1, 1)
        self.delayBeforeMeasLabel = QLabel(self.gridLayoutWidget)
        self.delayBeforeMeasLabel.setObjectName("delayBeforeMeasLabel")
        self.gridLayout.addWidget(self.delayBeforeMeasLabel, 5, 0, 1, 1)
        self.stepVText = QLineEdit(self.gridLayoutWidget)
        self.stepVText.setObjectName("stepVText")
        self.gridLayout.addWidget(self.stepVText, 3, 1, 1, 1)
        self.mainGridLayout.addLayout(self.gridLayout, 0, 0, 1, 1)
        
        self.minVLabel.setText("Min Voltage [V]")
        self.numAverScansLabel.setText("# averaged scans ")
        self.startVLabel.setText("Start Voltage [V]")
        self.stepVLabel.setText("Step Voltage [V]")
        self.maxVLabel.setText("Max Voltage [V]")
        self.delayBeforeMeasLabel.setText("Delays before measurements [sec]")
        
        ### Create basic push buttons to run acquisition ####
        self.startAcqButton = QPushButton(self)
        self.startAcqButton.setGeometry(QRect(10, 110, 160, 50))
        self.gridLayout.addWidget(self.startAcqButton, 6, 0, 1, 1)

        self.startAcqButton.setObjectName("Start Acquisition")
        self.startAcqButton.setText("Start Acquisition")
        self.startAcqButton.clicked.connect(lambda: self.acquisition.start(self))
        self.stopAcqButton = QPushButton(self)
        self.stopAcqButton.setGeometry(QRect(170, 110, 160, 50))
        self.gridLayout.addWidget(self.stopAcqButton, 6, 1, 1, 1)

        self.stopAcqButton.setObjectName("Stop Acquisition")
        self.stopAcqButton.setText("Stop Acquisition")
        self.stopAcqButton.setEnabled(False)
        self.stopAcqButton.clicked.connect(lambda: self.acquisition.stop(self))
        
        self.results.resTableWidget
        
        self.setCentralWidget(self.centralwidget)

        self.initParameters()
        self.results.initJVPlot()

        
        # Create menu and toolbar
        self.menuBar = QMenuBar(self)
        self.menuBar.setGeometry(0,0,340,25)
        #self.toolBar = QToolBar(self)
        #self.toolBar.setGeometry(0,450,340,100)

        # Menu entries
        self.loadConfigMenu = QAction("&Load Configuration", self)
        self.loadConfigMenu.setShortcut("Ctrl+l")
        self.loadConfigMenu.setStatusTip('Quit')
        self.loadConfigMenu.triggered.connect(self.loadConfig)
        
        self.saveConfigMenu = QAction("&Save Configuration", self)
        self.saveConfigMenu.setShortcut("Ctrl+s")
        self.saveConfigMenu.setStatusTip('Quit')
        self.saveConfigMenu.triggered.connect(self.saveConfig)
        
        self.quitMenu = QAction("&Quit", self)
        self.quitMenu.setShortcut("Ctrl+q")
        self.quitMenu.setStatusTip('Quit')
        self.quitMenu.triggered.connect(self.fileQuit)
        
        fileMenu = self.menuBar.addMenu('&File')
        fileMenu.addAction(self.quitMenu)
        fileMenu.addSeparator()
        fileMenu.addAction(self.loadConfigMenu)
        fileMenu.addAction(self.saveConfigMenu)
        
        self.sourcemeterMenu = QAction("&Sourcemeter", self)
        self.sourcemeterMenu.setShortcut("Ctrl+k")
        self.sourcemeterMenu.setStatusTip('Sourcemeter controls')
        self.sourcemeterMenu.triggered.connect(self.sourcemeterwind.show)
        instrumentsMenu = self.menuBar.addMenu('&Instruments')
        instrumentsMenu.addAction(self.sourcemeterMenu)
        self.viewWindowMenus(self.menuBar, self)

        self.helpMenu = QAction("&Help", self)
        self.helpMenu.setShortcut("Ctrl+h")
        self.helpMenu.setStatusTip('Help')
        self.helpMenu.triggered.connect(self.weblinks.help)
        self.devBugsMenu = QAction("&Development and Bugs", self)
        self.devBugsMenu.setShortcut("Ctrl+b")
        self.devBugsMenu.setStatusTip('Development and bugs')
        self.devBugsMenu.triggered.connect(self.weblinks.help)
        self.dataManagMenu = QAction("&Data management", self)
        self.dataManagMenu.setShortcut("Ctrl+m")
        self.dataManagMenu.setStatusTip('Data Management')
        self.dataManagMenu.triggered.connect(self.weblinks.dm)
        self.aboutMenu = QAction("&About", self)
        self.aboutMenu = QAction("&About", self)
        self.aboutMenu.setShortcut("Ctrl+a")
        self.aboutMenu.setStatusTip('About')
        self.aboutMenu.triggered.connect(self.aboutwid.show)
        
        aboutMenu = self.menuBar.addMenu('&Help')
        aboutMenu.addAction(self.helpMenu)
        aboutMenu.addAction(self.devBugsMenu)
        aboutMenu.addAction(self.dataManagMenu)
        aboutMenu.addSeparator()
        aboutMenu.addAction(self.aboutMenu)
        
        '''
        # Toolbar Entries #
        self.sampleToolbar = QAction("&Substrates", self)
        self.sampleToolbar.setShortcut("Ctrl+s")
        self.sampleToolbar.setStatusTip('Device Configuration')
        self.sampleToolbar.triggered.connect(self.samplewind.show)
        
        self.acquisitionToolbar = QAction("&Acquisition", self)
        self.acquisitionToolbar.setShortcut("Ctrl+a")
        self.acquisitionToolbar.setStatusTip('Acquisition paramenters')
        self.acquisitionToolbar.triggered.connect(self.acquisitionwind.show)
        
        self.resultsToolbar = QAction("&Results", self)
        self.resultsToolbar.setShortcut("Ctrl+p")
        self.resultsToolbar.setStatusTip('Results Panel')
        self.resultsToolbar.triggered.connect(self.resultswind.show)
        
        #toolBar = self.addToolBar("&Toolbar")
        self.toolBar.addAction(self.sampleToolbar)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.acquisitionToolbar)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.resultsToolbar)
        self.toolBar.addSeparator()
        '''
        #### Create status bar ####
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBarLabel = QLabel(self)
        self.statusBar.addPermanentWidget(self.statusBarLabel, 1)
        self.statusBarLabel.setText("System: ready")
        #self.statusBar().showMessage("Ready", 5000)
        
    
    # Save acquisition parameters in configuration ini
    def saveParameters(self):
        self.config.conf['Acquisition']['acqMinVoltage'] = str(self.minVText.text())
        self.config.conf['Acquisition']['acqMaxVoltage'] = str(self.maxVText.text())
        self.config.conf['Acquisition']['acqStartVoltage'] = str(self.startVText.text())
        self.config.conf['Acquisition']['acqStepVoltage'] = str(self.stepVText.text())
        self.config.conf['Acquisition']['acqNumAvScans'] = str(self.numAverScansText.text())
        self.config.conf['Acquisition']['acqDelBeforeMeas'] = str(self.delayBeforeMeasText.text())

        self.config.saveConfig(self.parent().config.configFile)
        self.config.readConfig(self.parent().config.configFile)
        print("Acquisition parameters saved as default")
        logger.info("Acquisition parameters saved as default")
    
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
        self.minVText.setText(str(self.config.acqMinVoltage))
        self.maxVText.setText(str(self.config.acqMaxVoltage))
        self.startVText.setText(str(self.config.acqStartVoltage))
        self.stepVText.setText(str(self.config.acqStepVoltage))
        self.numAverScansText.setText(str(self.config.acqNumAvScans))
        self.delayBeforeMeasText.setText(str(self.config.acqDelBeforeMeas))

    # Enable and disable fields (flag is either True or False) during acquisition.
    def enableAcqPanel(self, flag):
        self.minVText.setEnabled(flag)
        self.maxVText.setEnabled(flag)
        self.startVText.setEnabled(flag)
        self.stepVText.setEnabled(flag)
        self.numAverScansText.setEnabled(flag)
        self.delayBeforeMeasText.setEnabled(flag)
        self.numPointsText.setEnabled(flag)
        self.IntervalText.setEnabled(flag)
        self.saveButton.setEnabled(flag)
        self.defaultButton.setEnabled(flag)
    
    # Logic for loading parameters from a configuration file
    def loadConfig(self):
        filename = QFileDialog.getOpenFileName(self,
                        "Open INI config file", "","*.ini")
        self.config.readConfig(filename)
        print("Confguration parameters loaded from:",filename[0])
        logger.info("Confguration parameters loaded from:"+filename[0])
    
    # Logic for saving parameters to a configuration file
    def saveConfig(self):
        filename = QFileDialog.getSaveFileName(self,
                        "Save INI config file", "","*.ini")
        self.config.saveConfig(filename[0])
        print("Confguration parameters saved to:",filename[0])
        logger.info("Confguration parameters saved to:"+filename[0])

    # When closing the MainWindow, all windows need to close as we..
    def fileQuit(self):
        QApplication.closeAllWindows()
    
    # Enable/disable buttons
    def enableButtonsAcq(self,flag):
        if flag is False:
            self.startAcqButton.setText("Acquisition Running...")
        else:
            self.startAcqButton.setText("Start Acquisition")
        self.startAcqButton.setEnabled(flag)
        self.stopAcqButton.setEnabled(not flag)

    # Adds Menus to expose other Windows.
    def viewWindowMenus(self, menuObj, obj):
        viewMainWindowMenu = QAction("&Main Window", self)
        viewMainWindowMenu.setShortcut("Ctrl+w")
        viewMainWindowMenu.setStatusTip('Display Main Window')
        viewMainWindowMenu.triggered.connect(lambda: self.displayMainWindow(obj))
        viewSampleMenu = QAction("&Substrates Window", self)
        viewSampleMenu.setShortcut("Ctrl+d")
        viewSampleMenu.setStatusTip('Display Substrates Window')
        viewSampleMenu.triggered.connect(lambda: self.displayMainWindow(obj.samplewind))
        viewAcquisitionMenu = QAction("&Acquisition Window", self)
        viewAcquisitionMenu.setShortcut("Ctrl+a")
        viewAcquisitionMenu.setStatusTip('Display Acquisition Window')
        viewAcquisitionMenu.triggered.connect(lambda: self.displayMainWindow(obj.acquisitionwind))
        viewResultsMenu = QAction("&Results Window", self)
        viewResultsMenu.setShortcut("Ctrl+r")
        viewResultsMenu.setStatusTip('Display Results Window')
        viewResultsMenu.triggered.connect(lambda: self.displayMainWindow(obj.resultswind))

        windowMenu = menuObj.addMenu('&Window')
        windowMenu.addAction(viewMainWindowMenu)
        windowMenu.addAction(viewSampleMenu)
        windowMenu.addAction(viewAcquisitionMenu)
        windowMenu.addAction(viewResultsMenu)

    # Display main window
    def displayMainWindow(self, obj):
        obj.show()
        obj.setWindowState(obj.windowState() & Qt.WindowMinimized | Qt.WindowActive)
        obj.raise_()
        obj.activateWindow()

    # Logic to run when quitting the program
    # Dialog box for confirmation
    def closeEvent(self, event):
        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(self, 'Message',
                     quit_msg, QMessageBox.No, QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            #if self.stagewind.activeStage == True:
            #    self.stagewind.activateStage()
            #try:
            #    self.acquisition.acq_thread.stop()
            #except:
            #    pass
            self.close()
        else:
            event.ignore()

'''
   WebLinks Widget
   Definition of Web links
'''
class WebLinksWidget():
    def __init__(self):
        super(WebLinksWidget, self).__init__()

    def help(self):
        webbrowser.open("https://sites.google.com/site/gridedgesolar/")
    def dev(self):
        webbrowser.open("https://github.mit.edu/GridEdgeSolar/Autotesting")
    def dm(self):
        webbrowser.open("http://gridedgedm.mit.edu")

'''
   About Widget
   Definition of About Panel
'''
class AboutWidget(QWidget):
    """ PyQt widget for About Box Panel """
    
    def __init__(self):
        super(AboutWidget, self).__init__()
        self.initUI()
    
    # Define UI elements
    def initUI(self):
        self.setGeometry(100, 200, 400, 300)
        self.setWindowTitle('About GridEdge AutoTesting')
    
        self.gridLayout = QGridLayout()
        self.setLayout(self.gridLayout)
        self.verticalLayout = QVBoxLayout()
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        
        self.logo = QLabel(self)
        self.logo.setGeometry(QRect(30, 30, 311, 61))
        self.logo.setText("GridEdge Solar @ MIT")
        self.logo.setPixmap(QPixmap("gridedgeat/rsrc/logo_about.png"))
        self.logo.setObjectName("logo")

        self.labelTitle = QLabel("<qt><b><big><a href = http://gridedgesolar.com>Autotesting %s</a></b></big></qt>" % __version__, self)
        self.labelBy = QLabel("by: %s" % __author__, self)
        self.labelContact = QLabel("<qt>Contact: <a href = mailto:mitgridedge@gmail.com> mitgridedge@gmail.com</a></qt>", self)
        self.labelDetails = QLabel("GridEdgeSolar is a Solar PV project at MIT", self)
        self.labelLicense = QLabel("This software is licensed under the GNU GPL v.2.0 or later", self)
        
        for label in [self.logo, self.labelTitle, self.labelBy,
                self.labelContact, self.labelDetails, self.labelLicense]:
            label.setWordWrap(True)
            label.setOpenExternalLinks(True);
            self.verticalLayout.addWidget(label)
