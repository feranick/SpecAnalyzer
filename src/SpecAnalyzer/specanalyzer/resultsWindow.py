'''
ResultsWindow.py
-------------
Classes for providing a graphical user interface
for the resultsWindow

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''
import sys, random, math, json
#import requests, webbrowser
import numpy as np
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow,QPushButton,QVBoxLayout,QFileDialog,QWidget,
                             QGridLayout,QGraphicsView,QLabel,QComboBox,QLineEdit,
                             QMenuBar,QStatusBar, QApplication,QTableWidget,
                             QTableWidgetItem,QAction,QHeaderView,QMenu,QCheckBox,
                             QHBoxLayout)
from PyQt5.QtCore import (QSize,QRect,pyqtSlot,Qt)
from PyQt5.QtGui import (QColor,QCursor)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from . import logger

'''
   Results Window
'''
class ResultsWindow(QMainWindow):
    def __init__(self, parent=None):
        super(ResultsWindow, self).__init__(parent)
        self.deviceID = np.zeros((0,1))
        self.perfData = np.zeros((0,9))
        self.JV = np.array([])
        self.setupDataFrame()
        self.csvFolder = self.parent().config.csvSavingFolder
        self.initUI()
        self.initPlots(self.perfData)
        self.initJVPlot()
        self.show()
    
    # Define UI elements
    def initUI(self):
        self.setGeometry(380, 30, 1150, 950)
        self.setWindowTitle('Results Panel')
        self.setFixedSize(self.size())
        
        # A figure instance to plot on
        self.figureTJsc = plt.figure()
        self.figureTVoc = plt.figure()
        self.figureMPP = plt.figure()
        self.figureJVresp = plt.figure()
        self.figurePVresp = plt.figure()
        self.figureJVresp.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.15)
        self.figurePVresp.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.15)

        self.figureTJsc.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.21)
        self.figureTVoc.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.21)
        self.figureMPP.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.21)

        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        
        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QRect(20, 30, 1100, 710))

        self.HLayout = QHBoxLayout(self.gridLayoutWidget)
        self.jvVLayout = QVBoxLayout()
        
        self.canvasJVresp = FigureCanvas(self.figureJVresp)
        self.toolbarJVresp = NavigationToolbar(self.canvasJVresp, self)
        self.toolbarJVresp.setMaximumHeight(30)
        self.toolbarJVresp.setStyleSheet("QToolBar { border: 0px }")

        self.canvasPVresp = FigureCanvas(self.figurePVresp)
        self.toolbarPVresp = NavigationToolbar(self.canvasPVresp, self)
        self.toolbarPVresp.setMaximumHeight(30)
        self.toolbarPVresp.setStyleSheet("QToolBar { border: 0px }")

        self.jvVLayout.addWidget(self.toolbarJVresp)
        self.jvVLayout.addWidget(self.canvasJVresp)
        self.jvVLayout.addWidget(self.toolbarPVresp)
        self.jvVLayout.addWidget(self.canvasPVresp)
        self.HLayout.addLayout(self.jvVLayout)

        self.VLayout = QVBoxLayout()

        self.canvasTJsc = FigureCanvas(self.figureTJsc)
        self.toolbarTJsc = NavigationToolbar(self.canvasTJsc, self)
        self.toolbarTJsc.setMaximumHeight(30)
        self.toolbarTJsc.setStyleSheet("QToolBar { border: 0px }")

        self.VLayout.addWidget(self.toolbarTJsc)
        self.VLayout.addWidget(self.canvasTJsc)
        self.canvasTVoc = FigureCanvas(self.figureTVoc)
        self.toolbarTVoc = NavigationToolbar(self.canvasTVoc, self)
        self.toolbarTVoc.setMaximumHeight(30)
        self.toolbarTVoc.setStyleSheet("QToolBar { border: 0px }")

        self.VLayout.addWidget(self.toolbarTVoc)
        self.VLayout.addWidget(self.canvasTVoc)
        self.canvasMPP = FigureCanvas(self.figureMPP)
        self.toolbarMPP = NavigationToolbar(self.canvasMPP, self)
        self.toolbarMPP.setMaximumHeight(30)
        self.toolbarMPP.setStyleSheet("QToolBar { border: 0px }")

        self.VLayout.addWidget(self.toolbarMPP)
        self.VLayout.addWidget(self.canvasMPP)
        self.HLayout.addLayout(self.VLayout)

        self.resTableW = 1100
        self.resTableH = 145
        self.resTableWidget = QTableWidget(self.centralwidget)
        self.resTableWidget.setGeometry(QRect(20, 770, self.resTableW, self.resTableH))
        self.resTableWidget.setColumnCount(10)
        self.resTableWidget.setRowCount(0)
        self.resTableWidget.setItem(0,0, QTableWidgetItem(""))
        self.resTableWidget.setHorizontalHeaderItem(0,QTableWidgetItem("Device ID"))
        self.resTableWidget.setHorizontalHeaderItem(1,QTableWidgetItem("Av Voc [V]"))
        self.resTableWidget.setHorizontalHeaderItem(2,QTableWidgetItem(u"Av Jsc [mA/cm\u00B2]"))
        self.resTableWidget.setHorizontalHeaderItem(3,QTableWidgetItem(u"VPP [V]"))
        self.resTableWidget.setHorizontalHeaderItem(4,QTableWidgetItem(u"MPP [mW/cm\u00B2]"))
        self.resTableWidget.setHorizontalHeaderItem(5,QTableWidgetItem("Av FF"))
        self.resTableWidget.setHorizontalHeaderItem(6,QTableWidgetItem("Av PCE"))
        self.resTableWidget.setHorizontalHeaderItem(7,QTableWidgetItem("Tracking time [s]"))
        self.resTableWidget.setHorizontalHeaderItem(8,QTableWidgetItem("Acq Date"))
        self.resTableWidget.setHorizontalHeaderItem(9,QTableWidgetItem("Acq Time"))
        self.resTableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.resTableWidget.itemClicked.connect(self.onCellClick)
        self.setCentralWidget(self.centralwidget)

        # Make Menu for plot related calls
        self.menuBar = QMenuBar(self)
        self.menuBar.setGeometry(0,0,1150,25)

        self.loadMenu = QAction("&Load Data", self)
        self.loadMenu.setShortcut("Ctrl+o")
        self.loadMenu.setStatusTip('Load csv data from saved file')
        self.loadMenu.triggered.connect(self.read_csv)
        self.directoryMenu = QAction("&Set saving directory", self)
        self.directoryMenu.setShortcut("Ctrl+s")
        self.directoryMenu.setStatusTip('Set directory for saved files')
        self.directoryMenu.triggered.connect(self.set_dir_saved)
        
        self.clearMenu = QAction("&Clear Plots", self)
        self.clearMenu.setShortcut("Ctrl+x")
        self.clearMenu.setStatusTip('Clear plots')
        self.clearMenu.triggered.connect(lambda: self.clearPlots(True,True))
        
        fileMenu = self.menuBar.addMenu('&File')
        fileMenu.addAction(self.loadMenu)
        fileMenu.addAction(self.directoryMenu)
        plotMenu = self.menuBar.addMenu('&Plot')
        plotMenu.addAction(self.clearMenu)
        
        self.parent().viewWindowMenus(self.menuBar, self.parent())
        
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

    # Set directory for saved data
    def set_dir_saved(self):
        self.csvFolder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.parent().config.conf['System']['csvSavingFolder'] = str(self.csvFolder)
        self.parent().config.saveConfig(self.parent().config.configFile)
        self.parent().config.readConfig(self.parent().config.configFile)
        msg = "CSV Files will be saved in: "+self.csvFolder
        print(msg)
        logger.info(msg)
    
    # Define axis parametrs for plots
    def plotSettings(self, ax):
        ax.tick_params(axis='both', which='major', labelsize=8)
        ax.tick_params(axis='both', which='minor', labelsize=8)
    
    # Initialize Time-based plots
    def initPlots(self, data):
        self.figureTJsc.clf()
        self.axTJsc = self.figureTJsc.add_subplot(111)
        self.plotSettings(self.axTJsc)
        self.axTJsc.set_xlabel('Time [s]$',fontsize=8)
        self.axTJsc.set_ylabel('Jsc [mA/cm$^2$]',fontsize=8)
        self.axTJsc.set_autoscale_on(True)
        self.axTJsc.autoscale_view(True,True,True)
        self.canvasTJsc.draw()
        self.lineTJsc, = self.axTJsc.plot(data[:,0],data[:,2], '.-',linewidth=0.5)
        
        self.figureTVoc.clf()
        self.axTVoc = self.figureTVoc.add_subplot(111)
        self.plotSettings(self.axTVoc)
        self.axTVoc.set_xlabel('Time [s]',fontsize=8)
        self.axTVoc.set_ylabel('Voc [V]',fontsize=8)
        self.axTVoc.set_autoscale_on(True)
        self.axTVoc.autoscale_view(True,True,True)
        self.canvasTVoc.draw()
        self.lineTVoc, = self.axTVoc.plot(data[:,0],data[:,1], '.-',linewidth=0.5)
        
        self.figureMPP.clf()
        self.axMPP = self.figureMPP.add_subplot(111)
        self.plotSettings(self.axMPP)
        self.axMPP.set_xlabel('Time [s]',fontsize=8)
        self.axMPP.set_ylabel('Max power point [mW]',fontsize=8)
        self.axMPP.set_autoscale_on(True)
        self.axMPP.autoscale_view(True,True,True)
        self.canvasMPP.draw()
        self.lineMPP, = self.axMPP.plot(data[:,0],data[:,4], '.-',linewidth=0.5)
    
    # Initialize JV and PV plots
    def initJVPlot(self):
        self.axJVresp = self.figureJVresp.add_subplot(111)
        self.plotSettings(self.axJVresp)
        self.axJVresp.set_xlabel('Voltage [V]',fontsize=8)
        self.axJVresp.set_ylabel('Current density [mA/cm$^2$]',fontsize=8)
        self.axJVresp.axvline(x=0, linewidth=0.5)
        self.axJVresp.axhline(y=0, linewidth=0.5)
        
        self.axPVresp = self.figurePVresp.add_subplot(111)
        self.plotSettings(self.axPVresp)
        self.axPVresp.set_xlabel('Voltage [V]',fontsize=8)
        self.axPVresp.set_ylabel('Power density [mW/cm$^2$]',fontsize=8)
        self.axPVresp.axvline(x=0, linewidth=0.5)
        self.axPVresp.axhline(y=0, linewidth=0.5)
        self.canvasJVresp.draw()
        self.canvasPVresp.draw()

    # Plot Transient Jsc
    def plotTJsc(self, data):
        self.lineTJsc.set_data(data[:,2].astype(float), data[:,4].astype(float))
        self.axTJsc.relim()
        self.axTJsc.autoscale_view(True,True,True)
        self.canvasTJsc.draw()
    
    # Plot Transient Voc
    def plotTVoc(self, data):
        self.lineTVoc.set_data(data[:,2].astype(float), data[:,3].astype(float))
        self.axTVoc.relim()
        self.axTVoc.autoscale_view(True,True,True)
        self.canvasTVoc.draw()

    # Plot MPP with tracking
    def plotMPP(self, data):
        self.lineMPP.set_data(data[:,2].astype(float), data[:,5].astype(float))
        self.axMPP.relim()
        self.axMPP.autoscale_view(True,True,True)
        self.canvasMPP.draw()
    
    # Plot JV response
    def plotJVresp(self, JV,init):
        if init is True:
            self.initJVPlot()
        self.axJVresp.plot(JV[:,0],JV[:,1], '-',linewidth=1)
        self.axPVresp.plot(JV[:,0],JV[:,0]*JV[:,1], '-',linewidth=1,
            color='orange')
        self.figureJVresp.tight_layout()
        self.figurePVresp.tight_layout()
        self.canvasJVresp.draw()
        self.canvasPVresp.draw()

    # Clear all plots and fields
    def clearPlots(self, includeTable,includeJVplot):
        self.deviceID = np.zeros((0,1))
        self.perfData = np.zeros((0,8))
        self.JV = np.array([])
        if includeJVplot is True:
            self.figureJVresp.clf()
            self.figurePVresp.clf()
            self.canvasJVresp.draw()
            self.canvasPVresp.draw()
            self.initJVPlot()
        self.initPlots(self.perfData)
        if includeTable is True:
            self.resTableWidget.setRowCount(0)
            self.setupDataFrame()
        QApplication.processEvents()
    
    # Action upon selecting a row in the table.
    @pyqtSlot()
    def onCellClick(self):
        row = self.resTableWidget.selectedItems()[0].row()
        for j in range(self.resTableWidget.columnCount()):
            for i in range(self.resTableWidget.rowCount()):
                self.resTableWidget.item(i,j).setBackground(QColor(255,255,255))
        for j in range(self.resTableWidget.columnCount()):
            self.resTableWidget.item(row,j).setBackground(QColor(0,255,0))

        for line in self.axJVresp.get_lines():
            line.set_linewidth(0.5)
        for line in self.axPVresp.get_lines():
            line.set_linewidth(0.5)
        self.axJVresp.get_lines()[row+2].set_linewidth(2)
        self.axPVresp.get_lines()[row+2].set_linewidth(2)
        self.canvasJVresp.draw()
        self.canvasPVresp.draw()

    # Enable right click on substrates for saving locally
    def contextMenuEvent(self, event):
        self.menu = QMenu(self)
        rPos = self.resTableWidget.mapFromGlobal(QCursor.pos())
        if rPos.x()>0 and rPos.x()<self.resTableW and \
                rPos.y()>0 and rPos.y()<self.resTableH and \
                self.resTableWidget.rowCount() > 0 :
        
            selectCellSaveAction = QAction('Save as...', self)
            selectCellRemoveAction = QAction('Remove...', self)
            selectRemoveAllAction = QAction('Remove All...', self)
            self.menu.addAction(selectCellRemoveAction)
            self.menu.addAction(selectRemoveAllAction)
            self.menu.addAction(selectCellSaveAction)
            self.menu.popup(QCursor.pos())
            QApplication.processEvents()
        for currentQTableWidgetItem in self.resTableWidget.selectedItems():
            row = self.resTableWidget.currentRow()
            selectCellSaveAction.triggered.connect(lambda: self.selectDeviceSaveLocally(row))
            selectCellRemoveAction.triggered.connect(lambda: self.selectDeviceRemove(row))
            selectRemoveAllAction.triggered.connect(lambda: self.clearPlots(True,True))

    # Logic to save locally devices selected from results table
    def selectDeviceSaveLocally(self, row):
        folder = str(QFileDialog.getExistingDirectory(self, "Select directory where to save " +\
                                  self.dfTotDeviceID.iat[0,row][0][0]))
        self.save_csv(self.dfTotDeviceID.iat[0,row][0][0],
            self.dfTotAcqParams.iloc[[row]],
            self.dfTotPerfData.iat[0,row],
            self.dfTotJV.iat[0,row], folder)

    # Logic to remove data from devices selected from results table
    def selectDeviceRemove(self, row):
        self.dfTotDeviceID.drop(self.dfTotDeviceID.columns[row], axis=1)
        self.dfTotPerfData.drop(self.dfTotPerfData.columns[row], axis=1)
        self.dfTotJV.drop(self.dfTotJV.columns[row], axis=1)
        try:
            self.axPVresp.get_lines()[row+2].remove()
            self.axJVresp.get_lines()[row+2].remove()
        except:
            print("Removing spectra failed")
        self.canvasJVresp.draw()
        self.canvasPVresp.draw()
        self.resTableWidget.removeRow(row)

    # Add row and initialize it within the table
    def setupResultTable(self):
        self.resTableWidget.insertRow(self.resTableWidget.rowCount())
        self.resTableWidget.setItem(self.resTableWidget.rowCount()-1,0,
                                        QTableWidgetItem())
        for j in range(self.resTableWidget.columnCount()):
            self.resTableWidget.setItem(self.resTableWidget.rowCount(),j,
                                        QTableWidgetItem())
        self.lastRowInd = self.resTableWidget.rowCount()-1
        for f in range(9):
            self.resTableWidget.setItem(self.lastRowInd, 0,QTableWidgetItem())

    # Create internal dataframe with all the data. This is needed for plotting data after acquisition
    def setupDataFrame(self):
        self.dfTotDeviceID = pd.DataFrame()
        self.dfTotPerfData = pd.DataFrame()
        self.dfTotAcqParams = pd.DataFrame()
        self.dfTotJV = pd.DataFrame()
    
    # Process data from devices
    def processDeviceData(self, deviceID, dfAcqParams, perfData, JV, flag):
        
        # create numpy arrays for all devices as well as dataframes for csv and jsons
        self.deviceID = np.vstack((self.deviceID, np.array([deviceID])))
        self.perfData = perfData
        self.JV = JV

        # Populate table.
        self.fillTableData(deviceID, self.perfData)
        QApplication.processEvents()
        # Plot results
        self.plotData(self.deviceID,self.perfData, JV, False)
        QApplication.processEvents()

        if flag is True:
            # Save to internal dataFrame
            self.makeInternalDataFrames(self.lastRowInd,
                self.deviceID,self.perfData, dfAcqParams, self.JV)

            # Enable/disable saving to file
            # Using ALT with Start Acquisition button overrides the config settings.
            if self.parent().config.saveLocalCsv == True or \
                    self.parent().acquisition.modifiers == Qt.AltModifier:
                self.save_csv(deviceID, dfAcqParams, self.perfData, self.JV,self.csvFolder)

    # Plot data from devices
    def plotData(self, deviceID, perfData, JV, init):
        self.plotJVresp(JV, init)
        self.plotTVoc(perfData)
        self.plotMPP(perfData)
        self.plotTJsc(perfData)
        self.show()
    
    # Create internal dataframe with all the data. This is needed for plotting data after acquisition
    def makeInternalDataFrames(self, index,deviceID,perfData,dfAcqParams,JV):
        self.dfTotDeviceID[index] = [deviceID]
        self.dfTotPerfData[index] = [perfData]
        self.dfTotAcqParams = self.dfTotAcqParams.append(dfAcqParams)
        self.dfTotJV[index] = [JV]
    
    # Create DataFrames for saving csv and jsons
    def makeDFPerfData(self,perfData):
        dfPerfData = pd.DataFrame({'Time step': perfData[:,2], 'Voc': perfData[:,3],
                        'Jsc': perfData[:,4], 'VPP': perfData[:,5],'MPP': perfData[:,6],
                        'FF': perfData[:,7], 'effic': perfData[:,8],
                        'Acq Date': perfData[:,0], 'Acq Time': perfData[:,1]})
        dfPerfData = dfPerfData[['Acq Date','Acq Time','Time step', 'Voc',
                                     'Jsc', 'VPP','MPP','FF','effic']]
        return dfPerfData
    
    def makeDFJV(self,JV):
        dfJV = pd.DataFrame({'V':JV[:,0], 'J':JV[:,1]})
        dfJV = dfJV[['V', 'J']]
        return dfJV
    
    ### Save device acquisition as csv
    def save_csv(self,deviceID, dfAcqParams, perfData, JV, folder):
        dfPerfData = self.makeDFPerfData(perfData)
        dfJV = self.makeDFJV(JV)
    
        dfDeviceID = pd.DataFrame({'Device':[deviceID]})
        dfTot = pd.concat([dfDeviceID, dfPerfData], axis = 1)
        dfTot = pd.concat([dfTot,dfJV], axis = 1)
        dfTot = pd.concat([dfTot,dfAcqParams], axis = 1)
        
        dateTimeTag = str(datetime.now().strftime('%Y%m%d-%H%M%S_'))
        
        if dfPerfData['MPP'].count() < 2:
            csvFilename = dateTimeTag+str(dfDeviceID.at[0,'Device'])+".csv"
        else:
            csvFilename = dateTimeTag+str(dfDeviceID.at[0,'Device'])+"_tracking.csv"
        try:
            dfTot.to_csv(folder+"/"+csvFilename, sep=',', index=False)
        except:
            self.set_dir_saved()
            dfTot.to_csv(folder+"/"+csvFilename, sep=',', index=False)
        msg=" Device data saved on: "+folder+"/"+csvFilename
        print(msg)
        logger.info(msg)

    ### Load data from saved CSV
    def read_csv(self):
        filenames = QFileDialog.getOpenFileNames(self,
                        "Open csv data", "","*.csv")
        try:
            for filename in filenames[0]:
                print("Open saved device data from: ", filename)
                dftot = pd.read_csv(filename, na_filter=False)
                deviceID = dftot.at[0,'Device']
                perfData = dftot.as_matrix()[range(0,np.count_nonzero(dftot['Acq Date']))][:,range(1,10)]
                JV = dftot.as_matrix()[range(0,np.count_nonzero(dftot['V']))][:,np.arange(10,12)].astype(float)
                dfAcqParams = dftot.loc[0:1, 'Acq Min Voltage':'Comments']
                self.plotData(deviceID, perfData, JV, False)
                self.setupResultTable()
                self.fillTableData(deviceID, perfData)
                self.makeInternalDataFrames(self.lastRowInd, deviceID, perfData, dfAcqParams, np.array([JV]))
        except:
            print("Loading files failed")

    # Populate result table.
    def fillTableData(self, deviceID, obj):
        self.resTableWidget.setItem(self.lastRowInd, 0,QTableWidgetItem(deviceID))
        self.resTableWidget.setItem(self.lastRowInd, 1,QTableWidgetItem("{0:0.3f}".format(np.mean(obj[:,3].astype(float)))))
        self.resTableWidget.setItem(self.lastRowInd, 2,QTableWidgetItem("{0:0.3f}".format(np.mean(obj[:,4].astype(float)))))
        self.resTableWidget.setItem(self.lastRowInd, 3,QTableWidgetItem("{0:0.3f}".format(np.mean(obj[:,5].astype(float)))))
        self.resTableWidget.setItem(self.lastRowInd, 4,QTableWidgetItem("{0:0.3f}".format(np.mean(obj[:,6].astype(float)))))
        self.resTableWidget.setItem(self.lastRowInd, 5,QTableWidgetItem("{0:0.3f}".format(np.mean(obj[:,7].astype(float)))))
        self.resTableWidget.setItem(self.lastRowInd, 6,QTableWidgetItem("{0:0.3f}".format(np.mean(obj[:,8].astype(float)))))
        #self.resTableWidget.setItem(self.lastRowInd, 7,QTableWidgetItem("{0:0.3f}".format(np.mean(obj[:,2].astype(float)))))
        self.resTableWidget.setItem(self.lastRowInd, 8,QTableWidgetItem(obj[0,0]))
        self.resTableWidget.setItem(self.lastRowInd, 9,QTableWidgetItem(obj[0,1]))
        if float(obj[0,2]) == 0.:
            self.resTableWidget.setItem(self.lastRowInd, 7,QTableWidgetItem("None")) #track_time
        else:
            self.resTableWidget.setItem(self.lastRowInd, 7,QTableWidgetItem("{0:0.3f}".format(float(obj[0,2])))) #track_time

