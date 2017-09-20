'''
switchboxWindow
------------------
Class for providing a graphical user interface for 
switchbox

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

from PyQt5.QtCore import (QRect,QObject, QThread, pyqtSlot, pyqtSignal)
from PyQt5.QtWidgets import (QLabel, QLineEdit, QCheckBox,
                             QWidget,QMainWindow,QPushButton)
from .modules.switchbox.switchbox import *

class SwitchboxWindow(QMainWindow):
    def __init__(self, parent=None):
        super(SwitchboxWindow, self).__init__(parent)
        self.initUI(self)
    
    # define UI elements
    def initUI(self, SwitchboxWindow):
        SwitchboxWindow.resize(300, 100)
        self.switchboxLabel = QLabel(SwitchboxWindow)
        self.switchboxLabel.setGeometry(QRect(20, 20, 300, 20))
        SwitchboxWindow.setWindowTitle("Switchbox controls")
        self.switchboxLabel.setText("Ready")
        self.activateSwitchboxButton = QPushButton(SwitchboxWindow)
        self.activateSwitchboxButton.setGeometry(QRect(10, 50, 280, 40))
        self.activateSwitchboxButton.setText("Connect to Switchbox")
        self.activateSwitchboxButton.clicked.connect(self.activateSwitchbox)

    def activateSwitchbox(self):
        self.activateSwitchboxButton.setEnabled(False)
        self.swbThread = switchboxThread(self)
        self.swbThread.swbResponse.connect(self.printMsg)
        self.swbThread.start()

    def printMsg(self, msg):
        self.switchboxLabel.setText(msg)
        print(msg)
        self.activateSwitchboxButton.setEnabled(True)

class switchboxThread(QThread):

    swbResponse = pyqtSignal(str)

    def __init__(self, parent_obj):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def stop(self):
        self.terminate()

    def run(self):
        try:
            sb = SwitchBox()
            sb.connect(1, 2)
            self.swbResponse.emit("Switchbox OK, channels: "+sb.get_connect())
            del sb
        except:
            self.swbResponse.emit("    Cannot connect to switchbox")
            
        
