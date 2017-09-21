'''
mainWindow
-------------

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

import sys, webbrowser, random, time
import configparser
from datetime import datetime

from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton,
    QWidget, QAction,QVBoxLayout,QGridLayout,QLabel,QGraphicsView,
    QFileDialog,QStatusBar,QGraphicsScene,QLineEdit,QMessageBox,
    QDialog,QToolBar,QMenuBar)
from PyQt5.QtGui import (QIcon,QImage,QKeySequence,QPixmap,QPainter)
from PyQt5.QtCore import (pyqtSlot,QRectF)

from . import __version__
from . import __author__
from . import logger
from .configuration import *
from .cameraWindow import *
from .resultsWindow import *
from .acquisition import *
from .acquisitionWindow import *
from .powermeterWindow import *
from .sourcemeterWindow import *

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
        self.setGeometry(10,30,340,220)
        self.aboutwid = AboutWidget()
        self.resultswind = ResultsWindow(parent=self)
        self.camerawind = CameraWindow(parent=self)
        self.weblinks = WebLinksWidget()
        self.acquisition = Acquisition(parent=self)
        self.acquisitionwind = AcquisitionWindow(parent=self)
        self.powermeterwind = PowermeterWindow(parent=self)
        self.sourcemeterwind = SourcemeterWindow(parent=self)
        
        self.deviceLabel = QLabel(self)
        self.deviceLabel.setGeometry(QRect(10, 30, 100, 20))
        self.deviceLabel.setText("Name:")
        self.deviceText = QLineEdit(self)
        self.deviceText.setText("")
        self.deviceText.setGeometry(QRect(120, 30, 200, 20))
        
        self.commentsLabel = QLabel(self)
        self.commentsLabel.setGeometry(QRect(10, 60, 100, 20))
        self.commentsLabel.setText("Comments:")
        self.commentsText = QLineEdit(self)
        self.commentsText.setText("")
        self.commentsText.setGeometry(QRect(120, 60, 200, 20))
        
        self.deviceSizeLabel = QLabel(self)
        self.deviceSizeLabel.setGeometry(QRect(10, 90, 100, 20))
        self.deviceSizeLabel.setText("Device size (in):")
        self.deviceSizeText = QLineEdit(self)
        self.deviceSizeText.setText("1")
        self.deviceSizeText.setGeometry(QRect(120, 90, 100, 20))

        # Create menu and toolbar
        self.menuBar = QMenuBar(self)
        self.menuBar.setGeometry(0,0,340,25)
        self.toolBar = QToolBar(self)
        self.toolBar.setGeometry(0,170,340,25)

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
        
        #self.stageMenu = QAction("&Stage", self)
        #self.stageMenu.setShortcut("Ctrl+x")
        #self.stageMenu.setStatusTip('Stage controls')
        #self.stageMenu.triggered.connect(self.stagewind.show)
        self.powermeterMenu = QAction("&Powermeter", self)
        self.powermeterMenu.setShortcut("Ctrl+p")
        self.powermeterMenu.setStatusTip('Powermeter controls')
        self.powermeterMenu.triggered.connect(self.powermeterwind.show)
        self.sourcemeterMenu = QAction("&Sourcemeter", self)
        self.sourcemeterMenu.setShortcut("Ctrl+k")
        self.sourcemeterMenu.setStatusTip('Sourcemeter controls')
        self.sourcemeterMenu.triggered.connect(self.sourcemeterwind.show)
        #self.switchboxMenu = QAction("&Switchbox", self)
        #self.switchboxMenu.setShortcut("Ctrl+b")
        #self.switchboxMenu.setStatusTip('Switchbox controls')
        #self.switchboxMenu.triggered.connect(self.switchboxwind.show)
        self.cameraMenu = QAction("&Camera", self)
        self.cameraMenu.setShortcut("Ctrl+c")
        self.cameraMenu.setStatusTip('Camera controls')
        self.cameraMenu.triggered.connect(self.camerawind.show)

        instrumentsMenu = self.menuBar.addMenu('&Instruments')
        #instrumentsMenu.addAction(self.stageMenu)
        instrumentsMenu.addAction(self.sourcemeterMenu)
        instrumentsMenu.addSeparator()
        instrumentsMenu.addAction(self.powermeterMenu)
        instrumentsMenu.addAction(self.cameraMenu)
        #instrumentsMenu.addAction(self.switchboxMenu)
        
        self.viewWindowMenus(self.menuBar, self)

        self.helpMenu = QAction("&Help", self)
        self.helpMenu.setShortcut("Ctrl+h")
        self.helpMenu.setStatusTip('Help')
        self.helpMenu.triggered.connect(self.weblinks.help)
        self.devBugsMenu = QAction("&Development and Bugs", self)
        self.devBugsMenu.setShortcut("Ctrl+b")
        self.devBugsMenu.setStatusTip('Development and bugs')
        self.devBugsMenu.triggered.connect(self.weblinks.help)
        #self.dataManagMenu = QAction("&Data management", self)
        #self.dataManagMenu.setShortcut("Ctrl+m")
        #self.dataManagMenu.setStatusTip('Data Management')
        #self.dataManagMenu.triggered.connect(self.weblinks.dm)
        self.aboutMenu = QAction("&About", self)
        self.aboutMenu = QAction("&About", self)
        self.aboutMenu.setShortcut("Ctrl+a")
        self.aboutMenu.setStatusTip('About')
        self.aboutMenu.triggered.connect(self.aboutwid.show)
        
        aboutMenu = self.menuBar.addMenu('&Help')
        aboutMenu.addAction(self.helpMenu)
        aboutMenu.addAction(self.devBugsMenu)
        #aboutMenu.addAction(self.dataManagMenu)
        aboutMenu.addSeparator()
        aboutMenu.addAction(self.aboutMenu)
        
        # Toolbar Entries #
        '''
        self.sampleToolbar = QAction("&Substrates", self)
        self.sampleToolbar.setShortcut("Ctrl+s")
        self.sampleToolbar.setStatusTip('Device Configuration')
        self.sampleToolbar.triggered.connect(self.samplewind.show)
        '''
        
        self.acquisitionToolbar = QAction("&Acquisition", self)
        self.acquisitionToolbar.setShortcut("Ctrl+a")
        self.acquisitionToolbar.setStatusTip('Acquisition paramenters')
        self.acquisitionToolbar.triggered.connect(self.acquisitionwind.show)
        
        self.resultsToolbar = QAction("&Results", self)
        self.resultsToolbar.setShortcut("Ctrl+p")
        self.resultsToolbar.setStatusTip('Results Panel')
        self.resultsToolbar.triggered.connect(self.resultswind.show)
        
        #toolBar = self.addToolBar("&Toolbar")
        #self.toolBar.addAction(self.sampleToolbar)
        #self.toolBar.addSeparator()
        self.toolBar.addAction(self.acquisitionToolbar)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.resultsToolbar)
        self.toolBar.addSeparator()
       
        #### Create status bar ####
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBarLabel = QLabel(self)
        self.statusBar.addPermanentWidget(self.statusBarLabel, 1)
        self.statusBarLabel.setText("System: ready")
        #self.statusBar().showMessage("Ready", 5000)
    
        #### Create basic push buttons to run acquisition ####
        self.startAcqButton = QPushButton(self)
        self.startAcqButton.setGeometry(QRect(10, 120, 160, 40))
        self.startAcqButton.setObjectName("Start Acquisition")
        self.startAcqButton.setText("Start Acquisition")
        self.startAcqButton.clicked.connect(self.acquisition.start)
        self.stopAcqButton = QPushButton(self)
        self.stopAcqButton.setGeometry(QRect(170, 120, 160, 40))
        self.stopAcqButton.setObjectName("Stop Acquisition")
        self.stopAcqButton.setText("Stop Acquisition")
        self.stopAcqButton.setEnabled(False)
        self.stopAcqButton.clicked.connect(self.acquisition.stop)
    
    
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
        self.deviceText.setEnabled(flag)
        self.commentsText.setEnabled(flag)
        self.deviceSizeText.setEnabled(flag)

    # Adds Menus to expose other Windows.
    def viewWindowMenus(self, menuObj, obj):
        viewMainWindowMenu = QAction("&Main Window", self)
        viewMainWindowMenu.setShortcut("Ctrl+w")
        viewMainWindowMenu.setStatusTip('Display Main Window')
        viewMainWindowMenu.triggered.connect(lambda: self.displayMainWindow(obj))
        #viewSampleMenu = QAction("&Substrates Window", self)
        #viewSampleMenu.setShortcut("Ctrl+d")
        #viewSampleMenu.setStatusTip('Display Substrates Window')
        #viewSampleMenu.triggered.connect(lambda: self.displayMainWindow(obj.samplewind))
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
        #windowMenu.addAction(viewSampleMenu)
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
            try:
                self.acquisition.acq_thread.stop()
            except:
                pass
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
        webbrowser.open("https://github.com/feranick/SpecAnalyzer")
    def dev(self):
        webbrowser.open("https://github.com/feranick/SpecAnalyzer")
    #def dm(self):
    #    webbrowser.open("http://gridedgedm.mit.edu")

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
        self.setWindowTitle('About SpecAnalyzer-Tracking')
    
        self.gridLayout = QGridLayout()
        self.setLayout(self.gridLayout)
        self.verticalLayout = QVBoxLayout()
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        
        self.logo = QLabel(self)
        self.logo.setGeometry(QRect(30, 30, 311, 61))
        self.logo.setText("GridEdge Solar @ MIT")
        self.logo.setPixmap(QPixmap("gridedgeat/rsrc/logo_about.png"))
        self.logo.setObjectName("logo")

        self.labelTitle = QLabel("<qt><b><big><a href = https://github.com/feranick/SpecAnalyzer>SpecAnalyzer %s</a></b></big></qt>" % __version__, self)
        self.labelBy = QLabel("by: %s" % __author__, self)
        self.labelContact = QLabel("<qt>Contact: <a href = mailto:ferralis@mit.edu> ferralis@mit.edu</a></qt>", self)
        self.labelDetails = QLabel("This is a homebrew project at MIT", self)
        self.labelLicense = QLabel("This software is licensed under the GNU GPL v.2.0 or later", self)
        
        for label in [self.logo, self.labelTitle, self.labelBy,
                self.labelContact, self.labelDetails, self.labelLicense]:
            label.setWordWrap(True)
            label.setOpenExternalLinks(True);
            self.verticalLayout.addWidget(label)
