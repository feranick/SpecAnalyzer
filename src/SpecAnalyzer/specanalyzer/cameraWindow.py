'''
cameraWindow.py
---------------
Class for providing a graphical user interface
for the cameraWindow

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''
import sys
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QAction,
    QVBoxLayout,QLabel,QGraphicsView,QFileDialog,QStatusBar,
    QGraphicsScene, QLineEdit,QMessageBox)
from PyQt5.QtGui import (QIcon,QImage,QKeySequence,QPixmap,QPainter)
from PyQt5.QtCore import (pyqtSlot,QRectF)

from .modules.camera.camera import *
from . import logger

'''
   Camera Window
'''
class CameraWindow(QMainWindow):
    def __init__(self, parent=None):
        super(CameraWindow, self).__init__(parent)
        self.initUI()
    
    def initUI(self):
        # Set up Window geometry and shape
        self.setGeometry(100, 500, 660, 480)
        self.setWindowTitle('Camera Panel')
        # Set up status bar
        self.statusBar().showMessage("Camera: Ready", 5000)
        
        # Set up Graphic Scene and View
        self.scene = GraphicsScene(self)
        self.view = GraphicsView()
        self.view.setScene(self.scene)
        self.view.setMinimumSize(660, 480)
        self.imageLabel = QLabel()
        self.setCentralWidget(self.imageLabel)
        
        # Set up ToolBar
        tb = self.addToolBar("Camera")
        updateBtn = QAction(QIcon(QPixmap()),"Update Camera Feed",self)
        updateBtn.setShortcut('Ctrl+c')
        updateBtn.setStatusTip('Get Camera Feed')
        tb.addAction(updateBtn)
        tb.addSeparator()
        contrastAlignLabel = QLabel()
        contrastAlignLabel.setText("Check alignment [%]: ")
        tb.addWidget(contrastAlignLabel)
        self.checkAlignText = QLineEdit()
        self.checkAlignText.setMaximumSize(50, 25)
        self.checkAlignText.setReadOnly(True)
        tb.addWidget(self.checkAlignText)
        self.checkAlignText.show()
        tb.addSeparator()
        self.setDefaultBtn = QAction(QIcon(QPixmap()),
                                     "Set Default Alignment",self)
        self.setDefaultBtn.setShortcut('Ctrl+d')
        self.setDefaultBtn.setStatusTip('Set Default Alignment')
        self.setDefaultBtn.setEnabled(False)
        tb.addAction(self.setDefaultBtn)
        tb.addSeparator()
        
        self.cam = CameraFeed()
        tb.actionTriggered[QAction].connect(self.toolbtnpressed)
    
    # Define behavior of push buttons
    def toolbtnpressed(self,a):
        if a.text() == "Update Camera Feed":
            self.cameraFeed()
        if a.text() == "Set Default Alignment":
            self.setDefault()

    # Get and preprocess image
    def cameraFeed(self):
        self.setDefaultBtn.setEnabled(True)
        try:
            self.checkAlignText.setStyleSheet("color: rgb(0, 0, 0);")
            self.cam.grab_image()
            self.image, self.image_data = self.cam.get_image()
            self.imageLabel.setPixmap(QPixmap.fromImage(self.image))
            self.statusBar().showMessage('Camera-feed' + \
                str(datetime.now().strftime(' (%Y-%m-%d %H-%M-%S)')), 5000)
            self.alignPerc, self.iMax = self.cam.check_alignment( \
                self.image_data,
                self.parent().config.alignmentIntThreshold)

            self.checkAlignText.setText(str(self.alignPerc))
            if float(self.alignPerc) > self.parent().config.alignmentContrastDefault \
                    and float(self.iMax) > self.parent().config.alignmentIntMax:
                self.checkAlignText.setStyleSheet("color: rgb(255, 0, 255);")
                self.outAlignmentMessageBox()
            else:
                self.statusBar().showMessage(' Devices and masks appear to be correct', 5000)
        except:
            self.statusBar().showMessage(' USB camera not connected', 5000)

    # Set default values for alignment parameters
    def setDefault(self):
        try:
            self.setDefaultMessageBox(self.alignPerc)
            self.statusBar().showMessage(' Set default:' + self.alignPerc, 5000)
        except:
            self.statusBar().showMessage(' Acquire image first', 5000)

    # Dialog box and logic to set new alignment parameters.
    def setDefaultMessageBox(self, value):
        msgBox = QMessageBox( self )
        msgBox.setIcon( QMessageBox.Information )
        msgBox.setText( "By changing the default value, you will erase the previous value" )

        msgBox.setInformativeText( "Would you like to set " + value +  " as default?" )
        msgBox.addButton( QMessageBox.Yes )
        msgBox.addButton( QMessageBox.No )

        msgBox.setDefaultButton( QMessageBox.No )
        ret = msgBox.exec_()

        if ret == QMessageBox.Yes:
            self.filename = "calib"+str(datetime.now().strftime('_%Y%m%d_%H-%M-%S.png'))
            self.parent().config.conf['Instruments']['alignmentContrastDefault'] = str(self.alignPerc)
            self.parent().config.conf['Instruments']['alignmentIntMax'] = str(self.iMax)
            with open(self.parent().config.configFile, 'w') as configfile:
                self.parent().config.conf.write(configfile)
            self.parent().config.readConfig(self.parent().config.configFile)
            print(" New alignment settings saved as default. Image saved in: ", self.filename)
            logger.info(" New camera alignment settings saved as default. Image saved in: "+self.filename)
            self.cam.save_image(self.parent().config.imagesFolder+self.filename)
            return True
        else:
            print( " Alignment settings not saved as default" )
            return False

    # Warning box for misalignment
    def outAlignmentMessageBox(self):
        msgBox = QMessageBox( self )
        msgBox.setIcon( QMessageBox.Information )
        msgBox.setText( "WARNING: devices and mask might be misaligned " )
        msgBox.setInformativeText( "Please realign and retry" )
        msgBox.exec_()

'''
   GraphicsView
   Definition of the View for Camera
'''
class GraphicsView(QGraphicsView):
    """ Custom GraphicsView to display the scene. """
    def __init__(self, parent=None):
        super(GraphicsView, self).__init__(parent)
        self.setRenderHints(QPainter.Antialiasing)
    
    def resizeEvent(self, event):
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
    
    def drawBackground(self, painter, rect):
        painter.fillRect(rect, QBrush(Qt.lightGray))
        self.scene().drawBackground(painter, rect)

'''
   GraphicsScene
   Definition of the Scene for Camera
'''
class GraphicsScene(QGraphicsScene):
    """ Custom GraphicScene having all the main content."""

    def __init__(self, parent=None):
        super(GraphicsScene, self).__init__(parent)
    
    def drawBackground(self, painter, rect):
        """ Draws image in background if it exists. """
        if hasattr(self, "image"):
            painter.drawImage(QPoint(0, 0), self.image)

    def setBackground(self, image, labeltext):
        """ Sets the background image. """
        if not hasattr(self, 'imlabel'):
            self.imlabel = QGraphicsSimpleTextItem(labeltext)
            self.imlabel.setBrush(QBrush(Qt.white))
            self.imlabel.setPos(5, 5)
        if not hasattr(self,"image") or len(self.items()) < 1:
            self.addItem(self.imlabel)
        self.imlabel.setText(labeltext)
        self.image = image
        self.update()
