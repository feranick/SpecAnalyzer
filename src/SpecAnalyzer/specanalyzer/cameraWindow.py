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
import sys, time
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QAction,
    QVBoxLayout,QLabel,QGraphicsView,QFileDialog,QStatusBar,
    QGraphicsScene, QLineEdit,QMessageBox,QWidget,QApplication,
    QGraphicsRectItem,QGraphicsItem,QToolBar)
from PyQt5.QtGui import (QIcon,QImage,QKeySequence,QPixmap,QPainter,
    QBrush,QColor,QTransform,QPen,QFont)
from PyQt5.QtCore import (pyqtSlot,pyqtSignal,QRectF,QPoint,QRect,
    Qt,QPointF)

from .modules.camera.camera import *
from . import logger
from .configuration import *

'''
   Camera Window
'''
class CameraWindow(QMainWindow):
    def __init__(self, parent=None):
        super(CameraWindow, self).__init__(parent)
        self.initUI()
        self.config = Configuration()
        self.config.readConfig(self.config.configFile)
    
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
        #self.setCentralWidget(self.imageLabel)
        self.setCentralWidget(self.view)
        
        self.begin = QPoint()
        self.end = QPoint()
        self.firstTimeRunning = True
        
        # Set up ToolBar
        tb = self.addToolBar("Camera")
        self.updateBtn = QAction(QIcon(QPixmap()),"Get Camera Image",self)
        self.updateBtn.setShortcut('Ctrl+c')
        self.updateBtn.setStatusTip('Get camera feed, set integration window')
        tb.addAction(self.updateBtn)
        tb.addSeparator()
        
        self.liveFeedBtn = QAction(QIcon(QPixmap()),
                                     "Live Feed",self)
        self.liveFeedBtn.setShortcut('Ctrl+d')
        self.liveFeedBtn.setStatusTip('Set Default Alignment')
        self.liveFeedBtn.setEnabled(True)
        tb.addAction(self.liveFeedBtn)
        tb.addSeparator()
        
        self.autoAlignBtn = QAction(QIcon(QPixmap()),"Run Alignment",self)
        self.autoAlignBtn.setEnabled(False)
        self.autoAlignBtn.setShortcut('Ctrl+r')
        self.autoAlignBtn.setStatusTip('Run Alignment routine')
        tb.addAction(self.autoAlignBtn)
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
        
        self.autoAlignBtn.triggered.connect(self.autoAlign)
        self.updateBtn.triggered.connect(lambda: self.cameraFeed(False))
        self.setDefaultBtn.triggered.connect(self.setDefault)
        self.liveFeedBtn.triggered.connect(lambda: self.cameraFeed(True))

    # Define behavior of push buttons
    # Handle the actual alignment substrate by substrate
    def autoAlign(self):
        pass

    # Get image from feed
    def cameraFeed(self, live):
        self.cam = CameraFeed()
        self.setDefaultBtn.setEnabled(True)
        try:
            self.checkAlignText.setStyleSheet("color: rgb(0, 0, 0);")
            if live:
                self.liveFeedBtn.setText("Set integration window")
                self.updateBtn.setEnabled(False)
                QApplication.processEvents()
                self.img = self.cam.grab_image_live()
            else:
                self.updateBtn.setText("Set integration window")
                self.liveFeedBtn.setEnabled(False)
                QApplication.processEvents()
                self.img = self.cam.grab_image()
            self.image, self.image_data, temp = self.cam.get_image(False,0,0,0,0)
            
            pixMap = QPixmap.fromImage(self.image)
            self.scene.addPixmap(pixMap)
            #self.imageLabel.setPixmap(QPixmap.fromImage(self.image))
            self.view.fitInView(self.view.sceneRect(), Qt.KeepAspectRatio)

            self.statusBar().showMessage('Camera-feed' + \
                 str(datetime.now().strftime(' (%Y-%m-%d %H-%M-%S)')), 5000)
            self.statusBar().showMessage(' Drag Mouse to select area for alignment', 5000)
            self.liveFeedBtn.setEnabled(True)
            self.updateBtn.setEnabled(True)
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

    # Close camera feed upon closing window.
    def closeEvent(self, event):
        if hasattr(self,"cam"):
            self.cam.closeLiveFeed = True
            #self.firstTimeRunning = True
            del self.cam
        self.scene.cleanup()

    # Extract pixel intensity from cursor position
    def getPixelIntensity(self):
        if hasattr(self,"cam"):
            img_y, img_x, c = self.cam.img.shape
            x = int(self.end.x())
            y = int(self.end.y())
            if x > 0 and y > 0 and x < img_x and y < img_y:
                intensity = cv2.cvtColor(self.cam.img, cv2.COLOR_RGB2GRAY)[y,x]
                msg = " Intensity pixel at ["+str(x)+", "+str(y)+"]: "+str(intensity)
                #self.printMsg(msg)
                self.statusBar().showMessage(msg)

'''
   QGraphicsSelectionItem
   Definition of the class to generate the rectangular selection
'''
class QGraphicsSelectionItem(QGraphicsRectItem):
    
    # Class defining Rectangular Selection
    def __init__(self, initPos, finalPos, parent=None):
        super(QGraphicsSelectionItem, self).__init__(parent)
        self.setRect(QRectF(initPos, finalPos))
        self.setPen(QPen(Qt.blue))
        self.setFlags(self.flags() |
                      QGraphicsItem.ItemIsSelectable|
                      QGraphicsItem.ItemIsFocusable)
'''
   GraphicsView
   Custom GraphicsView to display the scene
'''
class GraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super(GraphicsView, self).__init__(parent)
        self.setRenderHints(QPainter.Antialiasing)
        self.setMouseTracking(True)
        
    # Resize image when resizing cameraWindow
    def resizeEvent(self, event):
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
    
    def drawBackground(self, painter, rect):
        painter.fillRect(rect, QBrush(Qt.lightGray))
        self.scene().drawBackground(painter, rect)

'''
   GraphicsScene
   Custom GraphicScene having all the main content.
'''
class GraphicsScene(QGraphicsScene):
    
    selectionDef = pyqtSignal(bool)
    def __init__(self, parent=None):
        super(GraphicsScene, self).__init__(parent)
        self.btnPressed = False

    # Create rectangular selection
    def addRect(self):
        self.removeRectangles()
        item = QGraphicsSelectionItem(self.parent().begin,self.parent().end)
        self.clearSelection()
        self.addItem(item)
        item.setSelected(True)
        self.setFocusItem(item)
        self.update()

    # Mouse events routines for generating rectangular selections
    def mousePressEvent(self, event):
        if len(self.items()) !=0:
            self.removeRectangles()
        if event.button() == Qt.LeftButton:
            self.parent().begin = event.scenePos()
            self.parent().initial = event.scenePos()
            self.update()
            self.btnPressed = True

    def mouseMoveEvent(self, event):
        self.parent().end = event.scenePos()
        self.parent().getPixelIntensity()
        #print(len(self.items()))
        #if len(self.items()) >0:
        if self.btnPressed == True and hasattr(self.parent(),"cam"):
            self.addRect()
    
    # Rectangular selection is defined at mouse release
    def mouseReleaseEvent(self, event):
        self.btnPressed = False
        self.parent().end = event.scenePos()
        self.parent().final = event.scenePos()
        self.parent().update()
        try:
            if len(self.items()) ==2:
                self.addRect()
                self.parent().manualAlignBtn.setEnabled(True)
                if self.parent().isAutoAlign:
                    msg = " Press SPACE to set integration window for alignment check"
                else:
                    msg = " Press SPACE to set Check Alignment; ENTER to Close"
                self.parent().printMsg(msg)
                self.parent().view.setToolTip(msg)
        except:
            pass

    # keyboard event driven routines for fixing the selection for analysis and closing image
    def keyPressEvent(self, event):
        if len(self.items())>1:
            if event.key() == Qt.Key_Space:
                self.parent().updateBtn.setText("Get Camera Image")
                self.parent().liveFeedBtn.setText("Live Feed")
                self.image, self.image_data, self.image_orig = self.parent().cam.get_image(True,
                             int(self.parent().initial.x()),
                             int(self.parent().final.x()),
                             int(self.parent().initial.y()),
                             int(self.parent().final.y()))
                
                self.alignPerc, self.iMax = self.parent().cam.check_alignment( \
                self.image_data,
                self.parent().config.alignmentIntThreshold)

                self.parent().checkAlignText.setText(str(self.alignPerc))
                if float(self.alignPerc) > self.parent().config.alignmentContrastDefault \
                    and float(self.iMax) > self.parent().config.alignmentIntMax:
                    self.parent().checkAlignText.setStyleSheet("color: rgb(255, 0, 255);")
                    self.parent().outAlignmentMessageBox()
                else:
                    self.parent().statusBar().showMessage(' Devices and masks appear to be correct', 5000)
    
    # Remove rectangular selections upon redrawing, leave image
    def removeRectangles(self):
        if len(self.items()) == 1 :
            self.image_item = self.items()[0]
        for item in self.items():
            self.removeItem(item)
        if hasattr(self,"image_item"):
            self.addItem(self.image_item)
        self.update

    # cleaup scene and view
    def cleanup(self):
        try:
            for item in self.items():
                self.removeItem(item)
            self.update
            del self.image
            del self.image_data
            del self.image_orig
        except:
            pass




