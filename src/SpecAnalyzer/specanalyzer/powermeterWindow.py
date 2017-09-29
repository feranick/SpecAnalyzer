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
                             QPushButton, QApplication)
from modules.powermeter.powermeter import *

class PowermeterWindow(QMainWindow):
    def __init__(self, parent=None):
        super(PowermeterWindow, self).__init__(parent)
        self.initUI(self)
    
    # Define UI elements
    def initUI(self, PowermeterWindow):
        PowermeterWindow.setWindowTitle("Powermeter Settings")
        self.setGeometry(10, 290, 340, 110)
        self.setFixedSize(self.size())
        self.powerMeterRefreshLabel = QLabel(PowermeterWindow)
        self.powerMeterRefreshLabel.setGeometry(QRect(20, 10, 120, 20))
        self.powerMeterRefreshLabel.setText("Refresh every [s]:")
        self.powerMeterRefreshText = QLineEdit(PowermeterWindow)
        self.powerMeterRefreshText.setGeometry(QRect(140, 10, 50, 20))
        self.powerMeterRefreshText.setText("0.5")

        self.powerMeterLabel = QLabel(PowermeterWindow)
        self.powerMeterLabel.setGeometry(QRect(20, 40, 300, 20))        
        self.powermeterStartButton = QPushButton(PowermeterWindow)
        self.powermeterStartButton.setGeometry(QRect(10, 70, 150, 30))
        self.powermeterStartButton.clicked.connect(self.startPMAcq)
        self.powermeterStartButton.setText("Start")
        self.powermeterStopButton = QPushButton(PowermeterWindow)
        self.powermeterStopButton.setGeometry(QRect(180, 70, 150, 30))
        self.powermeterStopButton.clicked.connect(self.stopPMAcq)
        self.powermeterStopButton.setText("Stop")

        self.powermeterStopButton.setEnabled(False)
        self.powermeterStartButton.setEnabled(True)

    # Logic to stop powermeter acquisition
    def stopPMAcq(self):
        self.powermeterStopButton.setEnabled(False)
        self.powermeterStartButton.setEnabled(True)
        self.powerMeterLabel.setText("")
        try:
            if self.pmThread.isRunning():
                self.pmThread.stop()
        except:
            pass

    # Logic to start powermeter acquisition
    def startPMAcq(self):
        self.powermeterStartButton.setEnabled(False)
        self.powermeterStopButton.setEnabled(True)
        self.powerMeterLabel.setText("Activating powermeter...")
        self.pmThread = powermeterThread(self, self.parent().config.powermeterID)
        self.pmThread.pmResponse.connect(lambda msg, flag: self.printMsg(msg, flag))
        self.pmThread.start()

    # Stop acquisition upon closing the powermeter window
    def closeEvent(self, event):
        self.stopPMAcq()

    def printMsg(self, msg, flag):
        self.powerMeterLabel.setText(msg)
        print(msg)
        if flag is False:
            self.powermeterStartButton.setEnabled(True)
            self.powermeterStopButton.setEnabled(False)
        
# Acquisition takes place in a separate thread
class powermeterThread(QThread):
    pmResponse = pyqtSignal(str, bool)
    def __init__(self, parent_obj, powermeterID):
        QThread.__init__(self)
        self.parent_obj = parent_obj
        self.powermeterID = powermeterID

    def __del__(self):
        self.wait()

    def stop(self):
        self.terminate()

    def run(self):
        try:
            self.pm = PowerMeter(self.powermeterID)
            while True:
                self.pmResponse.emit("Power levels [mW]: {0:0.4f}".\
                                    format(1000*self.pm.get_power().read), True)
                time.sleep(float(self.parent_obj.powerMeterRefreshText.text()))
        except:
            self.pmResponse.emit("Powermeter libraries or connection failed", False)
