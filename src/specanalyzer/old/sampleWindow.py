'''
SampleWindow
------------------
Class for providing a graphical user interface for 
Sample Window

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

import sys
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton,
    QWidget, QAction,QVBoxLayout,QGridLayout,QLabel,QGraphicsView,
    QFileDialog,QStatusBar,QTableWidget,QGraphicsScene,QLineEdit,
    QMessageBox,QDialog,QComboBox,QMenuBar,QDialogButtonBox,
    QAbstractItemView,QTableWidgetItem,QMenu)
from PyQt5.QtGui import (QIcon,QImage,QKeySequence,QPixmap,QPainter,QColor,
    QCursor,)
from PyQt5.QtCore import (Qt,pyqtSlot,QRectF,QRect,QCoreApplication,QSize)

from . import logger

'''
   Sample Window
'''
class SampleWindow(QMainWindow):
    def __init__(self, parent=None):
        super(SampleWindow, self).__init__(parent)
        self.initUI(self)
        self.activeSubs = np.ones((4,4), dtype=bool)
    
    # Define UI elements
    def initUI(self,MainWindow):
        self.setGeometry(10, 300, 440, 370)
        MainWindow.setWindowTitle("Substrates configuration")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QRect(10, 0, 275, 150))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.windowGridLayout = QGridLayout(self.gridLayoutWidget)
        self.windowGridLayout.setContentsMargins(0, 0, 0, 0)
        self.windowGridLayout.setSpacing(1)
        self.windowGridLayout.setObjectName("windowGridLayout")
        self.holderTypeCBox = QComboBox(self.gridLayoutWidget)
        self.holderTypeCBox.setObjectName("holderTypeCBox")
        self.windowGridLayout.addWidget(self.holderTypeCBox, 1, 1, 1, 1)
        self.sizeSubsLabel = QLabel(self.gridLayoutWidget)
        self.sizeSubsLabel.setObjectName("sizeSubsLabel")
        self.windowGridLayout.addWidget(self.sizeSubsLabel, 2, 0, 1, 1)
        self.holderTypeLabel = QLabel(self.gridLayoutWidget)
        self.holderTypeLabel.setObjectName("holderTypeLabel")
        self.windowGridLayout.addWidget(self.holderTypeLabel, 1, 0, 1, 1)
        self.operatorLabel = QLabel(self.gridLayoutWidget)
        self.operatorLabel.setObjectName("operatorLabel")
        self.windowGridLayout.addWidget(self.operatorLabel, 0, 0, 1, 1)
        self.operatorText = QLineEdit(self.gridLayoutWidget)
        self.operatorText.setText("")
        self.operatorText.setObjectName("operatorText")
        self.windowGridLayout.addWidget(self.operatorText, 0, 1, 1, 1)
        self.sizeSubsCBox = QComboBox(self.gridLayoutWidget)
        self.sizeSubsCBox.setObjectName("sizeSubsCBox")
        self.windowGridLayout.addWidget(self.sizeSubsCBox, 2, 1, 1, 1)
       
        self.sizeSubsCBox.addItem("1")
        self.sizeSubsCBox.setEnabled(False)
        self.holderTypeCBox.addItem(str(self.parent().config.numSubsHolderRow)+\
                                    "x"+str(self.parent().config.numSubsHolderRow))
        self.holderTypeCBox.setEnabled(False)
        
        self.commentsLabel = QLabel(self.centralwidget)
        self.commentsLabel.setObjectName("commentsLabel")
        self.commentsLabel.setGeometry(QRect(10, 150, 80, 20))
        #self.windowGridLayout.addWidget(self.commentsLabel, 3, 0, 1, 1)
        self.commentsText = QLineEdit(self.centralwidget)
        self.commentsText.setText("")
        self.commentsText.setGeometry(QRect(90, 150, 330, 20))
        self.commentsText.setObjectName("commentsText")
        #self.windowGridLayout.addWidget(self.commentsText, 3, 1, 1, 1)
       
        self.tableWidget = QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QRect(10, 190, 420, 145))
        self.tableWidget.setColumnCount(self.parent().config.numSubsHolderRow)
        self.tableWidget.setRowCount(self.parent().config.numSubsHolderCol)
        
        # This allows for background coloring of a cell
        for i in range(self.parent().config.numSubsHolderCol):
            for j in range(self.parent().config.numSubsHolderRow):
                self.tableWidget.setItem(i,j,QTableWidgetItem())
        #self.tableWidget.item(0, 0).setText("test-sample")

        self.tableWidget.itemClicked.connect(self.onCellClick)
        self.tableWidget.itemDoubleClicked.connect(self.onCellDoubleClick)
        
        # This disable editing
        #self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # This enables editing by Double Click
        self.tableWidget.setEditTriggers(QAbstractItemView.DoubleClicked)

        self.loadButton = QPushButton(self.centralwidget)
        self.loadButton.setGeometry(QRect(310, 30, 100, 40))
        self.loadButton.setObjectName("loadButton")
        self.loadButton.clicked.connect(self.loadCsvSubstrates)
        self.saveButton = QPushButton(self.centralwidget)
        self.saveButton.setGeometry(QRect(310, 80, 100, 40))
        self.saveButton.setObjectName("saveButton")
        self.saveButton.clicked.connect(self.saveCsvSubstrates)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setGeometry(QRect(0, 0, 774, 22))
        self.menuBar.setObjectName("menubar")
        
        self.loadMenu = QAction("&Load Substrates", self)
        self.loadMenu.setShortcut("Ctrl+o")
        self.loadMenu.setStatusTip('Load substrate names from csv')
        self.loadMenu.triggered.connect(self.loadCsvSubstrates)
        self.saveMenu = QAction("&Save Substrates", self)
        self.saveMenu.setShortcut("Ctrl+s")
        self.saveMenu.setStatusTip('Save substrate names to csv')
        self.saveMenu.triggered.connect(self.saveCsvSubstrates)
        self.clearMenu = QAction("&Clear Substrates", self)
        self.clearMenu.setShortcut("Ctrl+x")
        self.clearMenu.setStatusTip('Clear substrate from table')
        self.clearMenu.triggered.connect(self.clearCells)

        fileMenu = self.menuBar.addMenu('&File')
        fileMenu.addAction(self.loadMenu)
        fileMenu.addAction(self.saveMenu)
        fileMenu.addSeparator()
        fileMenu.addAction(self.clearMenu)

        self.parent().viewWindowMenus(self.menuBar, self.parent())

        MainWindow.setMenuBar(self.menuBar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.sizeSubsLabel.setText("Substrate size [sq in]  ")
        self.operatorLabel.setText("Operator")
        self.holderTypeLabel.setText("Holder type")
        self.commentsLabel.setText("Comments")
        self.loadButton.setText("Load")
        self.saveButton.setText("Save")
    
    # Enable right click on substrates for disabling/enabling during acquisition.
    def contextMenuEvent(self, event):
        self.menu = QMenu(self)
        #for currentQTableWidgetItem in self.tableWidget.selectedItems():
        row = self.tableWidget.currentRow()
        col = self.tableWidget.currentColumn()
        try:
            if self.tableWidget.item(row,col).text() != "":
                if self.activeSubs[row,col] == True:
                    selectCellAction = QAction('Disable substrate', self)
                else:
                    selectCellAction = QAction('Enable substrate', self)
                self.menu.addAction(selectCellAction)
                self.menu.popup(QCursor.pos())
                selectCellAction.triggered.connect(lambda: self.selectCell(row,col))
        except:
            pass

    # Logic to set substrate status for acquisition
    def selectCell(self, row,col):
        if self.activeSubs[row,col] == True:
            self.colorCellAcq(row,col,"red")
            self.activeSubs[row,col] = False
        else:
            self.colorCellAcq(row,col,"white")
            self.activeSubs[row,col] = True
    
    # Logic to set substrate name and color in table
    @pyqtSlot()
    def onCellClick(self):
        modifiers = QApplication.keyboardModifiers()
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            if modifiers == Qt.AltModifier and \
                        currentQTableWidgetItem.text() != "":
                self.parent().resultswind.redirectToDM(currentQTableWidgetItem.text())
            print(" Selected cell: (",str(self.tableWidget.row(currentQTableWidgetItem)+1),
                ", ",str(self.tableWidget.column(currentQTableWidgetItem)+1),")")

    @pyqtSlot()
    def onCellDoubleClick(self):
        self.resetCellAcq()

    # Enable and disable fields (flag is either True or False) during acquisition.
    def enableSamplePanel(self, flag):
        self.holderTypeCBox.setEnabled(flag)
        self.operatorText.setEnabled(flag)
        self.sizeSubsCBox.setEnabled(flag)
        self.commentsText.setEnabled(flag)
        self.loadButton.setEnabled(flag)
        self.saveButton.setEnabled(flag)
        self.tableWidget.setEnabled(flag)
        self.tableWidget.clearSelection()
        if flag is False:
            self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        else:
            self.tableWidget.setEditTriggers(QAbstractItemView.DoubleClicked)

    # Change color in sample cells depending on the acqusition status
    def colorCellAcq(self,row,column,color):
        if color == "red":
            self.tableWidget.item(row, column).setBackground(QColor(255,0,0))
        if color == "white":
            self.tableWidget.item(row, column).setBackground(QColor(255,255,255))
        if color == "green":
            self.tableWidget.item(row, column).setBackground(QColor(0,255,0))
        if color == "yellow":
            self.tableWidget.item(row, column).setBackground(QColor(255,255,0))

    # Reset color in sample cells
    def resetCellAcq(self):
        for i in range(self.parent().config.numSubsHolderCol):
            for j in range(self.parent().config.numSubsHolderRow):
                self.tableWidget.item(i, j).setBackground(QColor(255,255,255))

    # Clear names in cells
    def clearCells(self):
        for i in range(self.parent().config.numSubsHolderCol):
            for j in range(self.parent().config.numSubsHolderRow):
                self.tableWidget.item(i, j).setText('')
                self.tableWidget.item(i, j).setBackground(QColor(255,255,255))
        self.activeSubs = np.ones((4,4), dtype=bool)

    # Check if table is filled or empty
    def checkTableEmpty(self, numRow, numCol):
        for i in range(numRow):
            for j in range(numCol):
                if self.tableWidget.item(i,j).text() != "":
                    return False
        return True

    # Load device names and configuration
    def loadCsvSubstrates(self):
        import csv
        try:
            filename = QFileDialog.getOpenFileName(self,
                        "Open CSV substrates file", "","*.csv")
            with open(filename[0], 'rU') as inputFile:
                input = csv.reader(inputFile)
                devConf=[]
                for row in input:
                    devConf.append(row)
            for i in range(self.parent().config.numSubsHolderRow):
                for j in range(self.parent().config.numSubsHolderCol):
                    try:
                        self.tableWidget.item(i,j).setText(devConf[i][j])
                    except:
                        pass
            print("Substrates configuration loaded from:",filename[0])
            logger.info("Substrates configuration loaded from:"+filename[0])
        except:
            print("Error in loading Substrates configuration")
            logger.info("Error in loading Substrates configuration")

    # Save device names and configuration
    def saveCsvSubstrates(self):
        import csv
        devConf=[['']*4 for i in range(4)]
        for i in range(self.parent().config.numSubsHolderRow):
            for j in range(self.parent().config.numSubsHolderCol):
                devConf[i][j] = self.tableWidget.item(i,j).text()
        try:
            filename = QFileDialog.getSaveFileName(self,
                    "Save CSV substrates file", "","*.csv")
            with open(filename[0], 'w', newline='') as inputFile:
                csvwrite = csv.writer(inputFile)
                for i in range(self.parent().config.numSubsHolderRow):
                    csvwrite.writerow(devConf[i])
            print("Substrate configuration saved to:",filename[0])
            logger.info("Substrate configuration saved to:"+filename[0])
        except:
            print("Error in saving substrate configuration")
            logger.info("Error in saving substrate configuration")
