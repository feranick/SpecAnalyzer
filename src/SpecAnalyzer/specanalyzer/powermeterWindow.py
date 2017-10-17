'''
powermeterWindow
------------------
Class for providing a graphical user interface for 
powermeter panel

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

from PyQt5.QtCore import (QRect,QThread, pyqtSlot, pyqtSignal)
from PyQt5.QtWidgets import (QLabel, QLineEdit, QWidget, QMainWindow,
            QPushButton, QApplication,QMessageBox)
from .modules.powermeter.powermeter import *
from . import logger

class PowermeterWindow(QMainWindow):
    def __init__(self, parent=None):
        super(PowermeterWindow, self).__init__(parent)
        self.initUI(self)
    
    # Define UI elements
    def initUI(self, PowermeterWindow):
        PowermeterWindow.setWindowTitle("Powermeter Settings")
        self.setGeometry(10, 290, 340, 240)
        self.setFixedSize(self.size())
        self.powerMeterRefreshLabel = QLabel(PowermeterWindow)
        self.powerMeterRefreshLabel.setGeometry(QRect(20, 10, 120, 20))
        self.powerMeterRefreshLabel.setText("Refresh every [s]:")
        self.powerMeterRefreshText = QLineEdit(PowermeterWindow)
        self.powerMeterRefreshText.setGeometry(QRect(140, 10, 50, 20))
        self.powerMeterRefreshText.setText("0.5")

        self.powerMeterDefaultLabel = QLabel(PowermeterWindow)
        self.powerMeterDefaultLabel.setGeometry(QRect(20, 40, 140, 20))
        self.powerMeterDefaultLabel.setText("Default irradiance [mW/cm\u00B2]: ")
        self.powerMeterDefaultText = QLineEdit(PowermeterWindow)
        self.powerMeterDefaultText.setGeometry(QRect(190, 40, 50, 20))
        self.powerMeterDefaultText.setText(str(self.parent().config.irradiance1Sun))
        self.powerMeterSensorAreaLabel = QLabel(PowermeterWindow)
        self.powerMeterSensorAreaLabel.setGeometry(QRect(20, 70, 170, 20))
        self.powerMeterSensorAreaLabel.setText("Area power meter sensor [cm\u00B2]: ")
        self.powerMeterSensorAreaText = QLineEdit(PowermeterWindow)
        self.powerMeterSensorAreaText.setGeometry(QRect(190, 70, 50, 20))
        self.powerMeterSensorAreaText.setText(str(self.parent().config.irradianceSensorArea))

        self.powerMeterLabel = QLabel(PowermeterWindow)
        self.powerMeterLabel.setGeometry(QRect(20, 100, 300, 20))
        self.powerMeterLabel2 = QLabel(PowermeterWindow)
        self.powerMeterLabel2.setGeometry(QRect(20, 130, 300, 20))
        
        self.powermeterStartButton = QPushButton(PowermeterWindow)
        self.powermeterStartButton.setGeometry(QRect(10, 160, 150, 30))
        self.powermeterStartButton.clicked.connect(self.startPMAcq)
        self.powermeterStartButton.setText("Start")
        self.powermeterStopButton = QPushButton(PowermeterWindow)
        self.powermeterStopButton.setGeometry(QRect(180, 160, 150, 30))
        self.powermeterStopButton.clicked.connect(self.stopPMAcq)
        self.powermeterStopButton.setText("Stop")
      
        self.powermeterSaveButton = QPushButton(PowermeterWindow)
        self.powermeterSaveButton.setGeometry(QRect(10, 200, 320, 30))
        self.powermeterSaveButton.clicked.connect(self.setIrradianceMessageBox)
        self.powermeterSaveButton.setText("Save to Config")

        self.powermeterStopButton.setEnabled(False)
        self.powermeterStartButton.setEnabled(True)
        self.powermeterSaveButton.setEnabled(False)

        self.irradiance = self.parent().config.irradiance1Sun

    # Logic to stop powermeter acquisition
    def stopPMAcq(self):
        self.powermeterStopButton.setEnabled(False)
        self.powermeterStartButton.setEnabled(True)
        self.powermeterSaveButton.setEnabled(True)
        try:
            if self.pmThread.isRunning():
                self.pmThread.stop()
        except:
            pass

    # Logic to start powermeter acquisition
    def startPMAcq(self):
        self.powermeterStartButton.setEnabled(False)
        self.powermeterStopButton.setEnabled(True)
        self.powermeterSaveButton.setEnabled(False)
        self.powerMeterLabel.setText("Activating powermeter...")
        self.powerMeterLabel2.setText("")
        self.pmThread = powermeterThread(self, self.parent().config.powermeterID)
        self.pmThread.pmResponse.connect(lambda curr, av, flag: self.printMsg(curr, av, flag))
        self.pmThread.start()

    # Stop acquisition upon closing the powermeter window
    def closeEvent(self, event):
        self.stopPMAcq()

    def printMsg(self, curr, av, flag):
        self.irradiance = av/float(self.powerMeterSensorAreaText.text())
        msg1 = "Power levels [mW]: {0:0.4f}".format(curr)
        msg2 = "Average irradiance [mW/cm\u00B2]: {0:0.4f}".format(self.irradiance)
        self.powerMeterLabel.setText(msg1)
        self.powerMeterLabel2.setText(msg2)
        print(msg1+" - "+msg2)
        if flag is False:
            self.powermeterStartButton.setEnabled(True)
            self.powermeterStopButton.setEnabled(False)

    # Dialog box and logic to set new alignment parameters.
    def setIrradianceMessageBox(self):
        msgBox = QMessageBox( self )
        msgBox.setIcon( QMessageBox.Information )
        msgBox.setText( "By changing the irradiance default value, you will erase the previous value" )

        msgBox.setInformativeText( "Would you like to set {0:0.4f}".format(self.irradiance) +  " as default irradiance?" )
        msgBox.addButton( QMessageBox.Yes )
        msgBox.addButton( QMessageBox.No )

        msgBox.setDefaultButton( QMessageBox.No )
        ret = msgBox.exec_()

        if ret == QMessageBox.Yes:
            self.parent().config.conf['Instruments']['irradiance1Sun'] = "{0:0.4f}".format(self.irradiance)
            self.parent().config.conf['Instruments']['irradianceSensorArea'] = self.powerMeterSensorAreaText.text()
            with open(self.parent().config.configFile, 'w') as configfile:
                self.parent().config.conf.write(configfile)
            self.parent().config.readConfig(self.parent().config.configFile)
            self.powerMeterDefaultText.setText("{0:0.4f}".format(self.irradiance))
            print(" New irradiance settings saved as default.")
            logger.info(" New irradiance settings saved as default.")
            return True
        else:
            print( " Irradiance settings not saved as default" )
            return False
        
# Acquisition takes place in a separate thread
class powermeterThread(QThread):
    pmResponse = pyqtSignal(float, float, bool)
    
    def __init__(self, parent_obj, powermeterID):
        QThread.__init__(self)
        self.parent_obj = parent_obj
        self.powermeterID = powermeterID
        self.avPower = 1

    def __del__(self):
        self.wait()

    def stop(self):
        self.terminate()

    def run(self):
        try:
            self.pm = PowerMeter(self.powermeterID)
            self.avPower = 1000*self.pm.get_power().read
            numAver = 1
            while True:
                curPower = 1000*self.pm.get_power().read
                self.avPower = (self.avPower*numAver + curPower)/(numAver+1)
                self.pmResponse.emit(curPower,self.avPower,True)
                numAver += 1
                time.sleep(float(self.parent_obj.powerMeterRefreshText.text()))
        except:
            self.pmResponse.emit("Powermeter libraries or connection failed", False)

