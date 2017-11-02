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
    QGraphicsScene, QLineEdit,QMessageBox,QWidget)
from PyQt5.QtGui import (QIcon,QImage,QKeySequence,QPixmap,QPainter,
                         QBrush,QColor)
from PyQt5.QtCore import (pyqtSlot,QRectF,QPoint,QRect)

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
        
        self.begin = QPoint()
        self.end = QPoint()
        self.firstTimeRunning = True
        
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
        
        #self.cam = CameraFeed()
        tb.actionTriggered[QAction].connect(self.toolbtnpressed)
    
    # Define behavior of push buttons
    def toolbtnpressed(self,a):
        if a.text() == "Update Camera Feed":
            self.cam = CameraFeed()
            self.cameraFeed()
        if a.text() == "Set Default Alignment":
            self.setDefault()

    # Get image from feed
    def cameraFeed(self):
        self.setDefaultBtn.setEnabled(True)
        try:
            if self.firstTimeRunning == True:
                self.infoMessageBox()
                self.firstTimeRunning = False

            self.checkAlignText.setStyleSheet("color: rgb(0, 0, 0);")
            self.img = self.cam.grab_image()
            self.image, self.image_data, temp = self.cam.get_image(False,0,0,0,0)
            self.imageLabel.setPixmap(QPixmap.fromImage(self.image))
        
            self.statusBar().showMessage('Camera-feed' + \
                 str(datetime.now().strftime(' (%Y-%m-%d %H-%M-%S)')), 5000)
            self.statusBar().showMessage(' Drag Mouse to select area for alignment', 5000)
        except:
            self.statusBar().showMessage(' USB camera not connected', 5000)
            
    # Event driven routines for cropping image with mouse
    def paintEvent(self, event):
        qp = QPainter(self)
        br = QBrush(QColor(100, 10, 10, 40))
        qp.setBrush(br)
        qp.drawRect(QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.initial = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    # Event driven routines for cropping image with mouse
    # Main method for evaluating alignemnt from cropped selection
    def mouseReleaseEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.final = event.pos()
        self.update()
        #print(self.initial.x(), self.initial.y(), self.final.x(), self.final.y())
        try:
            self.image, self.image_data, self.image_orig = self.cam.get_image(True,
                             self.initial.x(),
                             self.final.x(),
                             self.initial.y(),
                             self.final.y())
            
            self.imageLabel.setPixmap(QPixmap.fromImage(self.image_orig))
            
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
            pass

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
    
    # Info procedure panel
    def infoMessageBox(self):
        msgBox = QMessageBox( self )
        msgBox.setIcon( QMessageBox.Information )
        msgBox.setText( "INFO: Please follow the alignment procedure:" )
        msgBox.setInformativeText( "1. Press \"Update camera Feed\" to start the live feed\n"+\
                                   "2. Press \"q\" to stop the live feed and grab image\n"+\
                                   "3. Select with the mouse the area for alignemnt " )
        msgBox.exec_()
    
    # Close camera feed upon closing window.
    def closeEvent(self, event):
        self.cam.closeLiveFeed = True
        self.firstTimeRunning = True
        try:
            del self.cam
        except:
            pass

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

