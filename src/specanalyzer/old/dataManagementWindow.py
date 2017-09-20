'''
Data Management Window
------------------
Class for providing a graphical user interface for 
Data Management Window

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton,
    QWidget, QAction,QAbstractItemView,QTableWidgetItem,QFrame,
    QVBoxLayout,QGridLayout,QLabel,QGraphicsView,QFileDialog,
    QStatusBar,QTableWidget,QGraphicsScene,QLineEdit,QMessageBox,
    QDialog,QComboBox,QMenuBar,QDialogButtonBox,)
from PyQt5.QtGui import (QIcon,QImage,QKeySequence,QPixmap,QPainter,QColor)
from PyQt5.QtCore import (pyqtSlot,QRectF,QRect,QCoreApplication,QSize)

from .dataManagement import *
from . import logger

'''
   DBConnection Widget
   Definition of Database connection Widget
'''
class DataManagementWindow(QMainWindow):
    def __init__(self, parent=None):
        super(DataManagementWindow, self).__init__(parent)
        self.initUI(self)
    
    # Setup UI elements
    def initUI(self,Panel):
        self.setGeometry(10, 200, 300, 390)
        self.setWindowTitle('Data-management Settings')
        self.gridLayoutWidget = QWidget(Panel)
        self.gridLayoutWidget.setGeometry(QRect(10, 9, 270, 221))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(10, 0, 10, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.dbHostnameLabel = QLabel(self.gridLayoutWidget)
        self.dbHostnameLabel.setObjectName("dbHostnameLabel")
        self.gridLayout.addWidget(self.dbHostnameLabel, 0, 0, 1, 1)
        self.dbHostnameText = QLineEdit(self.gridLayoutWidget)
        self.dbHostnameText.setObjectName("dbHostnameText")
        self.gridLayout.addWidget(self.dbHostnameText, 0, 1, 1, 1)
        self.dbUsernameText = QLineEdit(self.gridLayoutWidget)
        self.dbUsernameText.setObjectName("dbUsernameText")
        self.gridLayout.addWidget(self.dbUsernameText, 3, 1, 1, 1)
        self.dbNameText = QLineEdit(self.gridLayoutWidget)
        self.dbNameText.setObjectName("dbNameText")
        self.gridLayout.addWidget(self.dbNameText, 2, 1, 1, 1)
        self.dbPortNumText = QLineEdit(self.gridLayoutWidget)
        self.dbPortNumText.setObjectName("dbPortNumText")
        self.gridLayout.addWidget(self.dbPortNumText, 1, 1, 1, 1)
        self.dbPasswordText = QLineEdit(self.gridLayoutWidget)
        self.dbPasswordText.setObjectName("dbPasswordText")
        self.gridLayout.addWidget(self.dbPasswordText, 4, 1, 1, 1)
        self.dbPortNumLabel = QLabel(self.gridLayoutWidget)
        self.dbPortNumLabel.setObjectName("dbPortNumLabel")
        self.gridLayout.addWidget(self.dbPortNumLabel, 1, 0, 1, 1)
        self.dbNameLabel = QLabel(self.gridLayoutWidget)
        self.dbNameLabel.setObjectName("dbNameLabel")
        self.gridLayout.addWidget(self.dbNameLabel, 2, 0, 1, 1)
        self.dbUsernameLabel = QLabel(self.gridLayoutWidget)
        self.dbUsernameLabel.setObjectName("dbUsernameLabel")
        self.gridLayout.addWidget(self.dbUsernameLabel, 3, 0, 1, 1)
        self.dbPasswordLabel = QLabel(self.gridLayoutWidget)
        self.dbPasswordLabel.setObjectName("dbPasswordLabel")
        self.gridLayout.addWidget(self.dbPasswordLabel, 4, 0, 1, 1)
        
        self.gridLayout.addWidget(QHLine(), 5, 0, 1, 1)
        self.gridLayout.addWidget(QHLine(), 5, 1, 1, 1)
        self.dbHttpPortNumLabel = QLabel(self.gridLayoutWidget)
        self.dbHttpPortNumLabel.setObjectName("dbHttpPortNumLabel")
        self.gridLayout.addWidget(self.dbHttpPortNumLabel, 6, 0, 1, 1)
        self.dbHttpPortNumText = QLineEdit(self.gridLayoutWidget)
        self.dbHttpPortNumText.setObjectName("dbHttpPortNumText")
        self.gridLayout.addWidget(self.dbHttpPortNumText, 6, 1, 1, 1)
        self.dbHttpPathText = QLineEdit(self.gridLayoutWidget)
        self.dbHttpPathText.setObjectName("dbHttpPathText")
        self.gridLayout.addWidget(self.dbHttpPathText, 7, 1, 1, 1)
        self.dbHttpPathLabel = QLabel(self.gridLayoutWidget)
        self.dbHttpPathLabel.setObjectName("dbHttpPathLabel")
        self.gridLayout.addWidget(self.dbHttpPathLabel, 7, 0, 1, 1)
        self.gridLayout.addWidget(QHLine(), 8, 0, 1, 1)
        self.gridLayout.addWidget(QHLine(), 8, 1, 1, 1)

        self.dbTestConnectButton = QPushButton(Panel)
        self.dbTestConnectButton.setGeometry(QRect(10, 260, 270, 40))
        self.dbTestConnectButton.setObjectName("dbTestConnectButton")
        self.dbSetDefaultButton = QPushButton(Panel)
        self.dbSetDefaultButton.setGeometry(QRect(10, 300, 270, 40))
        self.dbSetDefaultButton.setObjectName("dbSetDefaultButton")
        self.dbRestoreDefaultButton = QPushButton(Panel)
        self.dbRestoreDefaultButton.setGeometry(QRect(10, 340, 270, 40))
        self.dbRestoreDefaultButton.setObjectName("dbRestoreDefaultButton")
        
        self.dbConnectResultLabel = QLabel(Panel)
        self.dbConnectResultLabel.setGeometry(QRect(20, 235, 321, 20))
        self.dbConnectResultLabel.setObjectName("dbConnectResultLabel")

        self.dbHostnameLabel.setText("DB hostname IP")
        self.dbPortNumLabel.setText("DB port number")
        self.dbNameLabel.setText("DB name")
        self.dbUsernameLabel.setText("DB Username")
        self.dbPasswordLabel.setText("DB Password")
        self.dbHttpPortNumLabel.setText("HTTP port number")
        self.dbHttpPathLabel.setText("HTTP path")

        self.dbTestConnectButton.setText("Test Connectivity")
        self.dbSetDefaultButton.setText("Save settings")
        self.dbRestoreDefaultButton.setText("Restore default settings")
        self.dbConnectResultLabel.setText("Idle")
        
        self.initParams()
        
        self.dbTestConnectButton.clicked.connect(self.dbCheckConnect)
        self.dbSetDefaultButton.clicked.connect(self.dbSetDefault)
        self.dbRestoreDefaultButton.clicked.connect(self.dbRestoreDefault)

    # Populate UI elements from configuration file
    def initParams(self):
        self.dbHostnameText.setText(self.parent().config.DbHostname)
        self.dbPortNumText.setText(self.parent().config.DbPortNumber)
        self.dbNameText.setText(self.parent().config.DbName)
        self.dbUsernameText.setText(self.parent().config.DbUsername)
        self.dbPasswordText.setText(self.parent().config.DbPassword)
        self.dbHttpPortNumText.setText(self.parent().config.DbHttpPortNumber)
        self.dbHttpPathText.setText(self.parent().config.DbHttpPath)

    # Get initialization paramters from UI elements
    def getDbConnectionInfo(self):
        return [self.dbHostnameText.text(),
                    self.dbPortNumText.text(),
                    self.dbNameText.text(),
                    self.dbUsernameText.text(),
                    self.dbPasswordText.text(),
                    self.dbHttpPortNumText.text(),
                    self.dbHttpPathText.text()]

    # Logic for checking connection via pyMongo
    def dbCheckConnect(self):
        self.dbConnect = DataManagement(self.getDbConnectionInfo())
        try:
            if self.dbConnect.connectDB()[1] is True:
                self.dbConnectResultLabel.setText("Connection successful")
                print("Connection to Data-Management successful")
        except:
            self.dbConnectResultLabel.setText("Connection failed")
            print("Connection to Data-Management failed")

    # Set connection parameters as default values.
    def dbSetDefault(self):
        self.parent().config.conf['DM']['DbHostname'] = str(self.dbHostnameText.text())
        self.parent().config.conf['DM']['DbPortNumber'] = str(self.dbPortNumText.text())
        self.parent().config.conf['DM']['DbName'] = str(self.dbNameText.text())
        self.parent().config.conf['DM']['DbUsername'] = str(self.dbUsernameText.text())
        self.parent().config.conf['DM']['DbPassword'] = str(self.dbPasswordText.text())
        self.parent().config.conf['DM']['DbHttpPortNumber'] = str(self.dbHttpPortNumText.text())
        self.parent().config.conf['DM']['DbHttpPath'] = str(self.dbHttpPathText.text())
        self.parent().config.saveConfig(self.parent().config.configFile)
        self.parent().config.readConfig(self.parent().config.configFile)
        print("New Data-Management settings saved as default")
        logger.info("New Data-Management settings saved as default")

    # Restore connection parameters from default values.
    def dbRestoreDefault(self):
        self.parent().config.defineConfDM()
        self.parent().config.saveConfig(self.parent().config.configFile)
        self.parent().config.readConfig(self.parent().config.configFile)
        print("Restored default Data-Management settings")
        logger.info("Restored default Data-Management settings")
        self.initParams()

# Classes to make horizontal lines
class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
