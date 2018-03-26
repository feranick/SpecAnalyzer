'''
cameraWindow.py
---------------
Class for providing a graphical user interface
for the cameraWindow

Copyright (C) 2017-2018 Nicola Ferralis <ferralis@mit.edu>

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
    QGraphicsRectItem,QGraphicsItem,QToolBar,QMenuBar)
from PyQt5.QtGui import (QIcon,QImage,QKeySequence,QPixmap,QPainter,
                         QBrush,QColor,QTransform,QPen,QFont)
from PyQt5.QtCore import (pyqtSlot,QRectF,QPoint,QRect,Qt,QPointF)

from .modules.camera.camera import *
from .configuration import *
from .acquisition import *
#from .modules.xystage.xystage import *
#from .modules.shutter.shutter import *
#from . import logger

'''
   Camera Window
'''
class CameraWindow(QMainWindow):
    def __init__(self, parent=None):
        super(CameraWindow, self).__init__(parent)
        self.initUI()
        self.config = Configuration()
        self.config.readConfig(self.config.configFile)
        #self.numRow = self.config.numSubsHolderRow
        #self.numCol = self.config.numSubsHolderCol
    
    def initUI(self):
        # Set up Window geometry and shape
        self.setGeometry(550, 300, 800, 630)
        self.setWindowTitle('Camera Alignment Panel')
        # Set up status bar
        self.statusBar().showMessage("Camera: Ready", 5000)
        
        # Set up Graphic Scene and View
        self.scene = GraphicsScene(self)
        self.view = GraphicsView()
        self.view.setScene(self.scene)
        self.view.setMinimumSize(660, 480)
        self.imageLabel = QLabel()
        self.setCentralWidget(self.view)
        self.image_data = None
        
        self.begin = QPoint()
        self.end = QPoint()
        self.firstTimeRunning = True
        self.alignOn = False
        
        # Set up ToolBar
        tb = QToolBar()
        self.addToolBar(Qt.BottomToolBarArea, tb)
        
        #self.autoAlignBtn = QAction(QIcon(QPixmap()),"Run Automated Alignment",self)
        #self.autoAlignBtn.setEnabled(True)
        #self.autoAlignBtn.setShortcut('Ctrl+r')
        #self.autoAlignBtn.setStatusTip('Run Automated Alignment Routine')
        
        self.manualAlignBtn = QAction(QIcon(QPixmap()),"Get Image",self)
        self.manualAlignBtn.setEnabled(True)
        self.manualAlignBtn.setShortcut('Ctrl+m')
        self.manualAlignBtn.setStatusTip('Get Image - Run Manual Alignment')
        
        self.liveAlignBtn = QAction(QIcon(QPixmap()),"Live",self)
        self.liveAlignBtn.setEnabled(True)
        self.liveAlignBtn.setShortcut('Ctrl+l')
        self.liveAlignBtn.setStatusTip('Live Image - Run Manual Alignment')
        
        self.saveImageBtn = QAction(QIcon(QPixmap()),"Save Image",self)
        self.saveImageBtn.setEnabled(False)
        self.saveImageBtn.setShortcut('Ctrl+s')
        self.saveImageBtn.setStatusTip('Save Image')
        
        contrastAlignLabel = QLabel()
        font = QFont()
        font.setFamily(font.defaultFamily())
        contrastAlignLabel.setFont(font)
        contrastAlignLabel.setText("Alignment Threshold [%]: ")
        self.checkAlignText = QLineEdit()
        self.checkAlignText.setMaximumSize(40, 25)
        self.checkAlignText.setReadOnly(True)
        
        self.setDefaultBtn = QAction(QIcon(QPixmap()),
                                     "Set Alignment as Default",self)
        self.setDefaultBtn.setShortcut('Ctrl+d')
        self.setDefaultBtn.setStatusTip('Set Default Alignment')
        self.setDefaultBtn.setEnabled(False)
        
        self.resetBtn = QAction(QIcon(QPixmap()),
                                     "Reset",self)
        self.resetBtn.setShortcut('Ctrl+r')
        self.resetBtn.setStatusTip('Reset Camera Live Interface')
        self.resetBtn.setEnabled(False)
        
        self.intensityLabel = QLabel()
        font = QFont()
        font.setFamily(font.defaultFamily())
        self.intensityLabel.setFont(font)
        self.intensityLabel.setText("")

        #tb.addAction(self.autoAlignBtn)
        tb.addAction(self.manualAlignBtn)
        tb.addSeparator()
        tb.addAction(self.liveAlignBtn)
        tb.addSeparator()
        tb.addAction(self.saveImageBtn)
        tb.addSeparator()
        tb.addWidget(contrastAlignLabel)
        tb.addWidget(self.checkAlignText)
        self.checkAlignText.show()
        tb.addSeparator()
        tb.addAction(self.setDefaultBtn)
        tb.addSeparator()
        tb.addAction(self.resetBtn)
        tb.addSeparator()
        tb.addWidget(self.intensityLabel)
        
        #self.autoAlignBtn.triggered.connect(self.autoAlign)
        self.manualAlignBtn.triggered.connect(lambda: self.manualAlign(False))
        self.liveAlignBtn.triggered.connect(lambda: self.manualAlign(True))
        self.saveImageBtn.triggered.connect(self.saveImage)
        self.setDefaultBtn.triggered.connect(self.setDefault)
        self.resetBtn.triggered.connect(lambda: self.setAlignOn(False))

        # Make Menu for plot related calls
        self.menuBar = QMenuBar(self)
        self.menuBar.setGeometry(0,0,1150,25)

        #self.autoAlignmentMenu = QAction("&Autoalignment", self)
        #self.autoAlignmentMenu.setShortcut("Ctrl+k")
        #self.autoAlignmentMenu.setStatusTip('Run Autoalignment')
        #self.autoAlignmentMenu.triggered.connect(self.autoAlign)

        self.manualAlignmentMenu = QAction("&Manual alignment", self)
        self.manualAlignmentMenu.setShortcut("Ctrl+m")
        self.manualAlignmentMenu.setStatusTip('Run manual alignment')
        self.manualAlignmentMenu.triggered.connect(lambda: self.manualAlign(False))

        self.liveAlignmentMenu = QAction("&Manual alignment - Live", self)
        self.liveAlignmentMenu.setShortcut("Ctrl+l")
        self.liveAlignmentMenu.setStatusTip('Run manual alignment from live mode')
        self.liveAlignmentMenu.triggered.connect(lambda: self.manualAlign(True))

        self.saveImageMenu = QAction("&Save Image", self)
        self.saveImageMenu.setShortcut("Ctrl+s")
        self.saveImageMenu.setStatusTip('Save image to png file')
        self.saveImageMenu.triggered.connect(self.saveImage)
        self.saveImageMenu.setEnabled(False)
        
        alignmentMenu = self.menuBar.addMenu('&Alignment')
        #alignmentMenu.addAction(self.autoAlignmentMenu)
        alignmentMenu.addAction(self.manualAlignmentMenu)
        alignmentMenu.addAction(self.liveAlignmentMenu)
        imageMenu = self.menuBar.addMenu('&Image')
        imageMenu.addAction(self.saveImageMenu)

        self.parent().viewWindowMenus(self.menuBar, self.parent())
     
    '''
    # Handle the actual alignment substrate by substrate
    def autoAlign(self):
        performAlignment = False
        for j in range(self.numCol):
            for i in range(self.numRow):
                if self.parent().samplewind.tableWidget.item(i,j).text() != "":
                    performAlignment = True
        if performAlignment == False:
            self.noSubstratesMessageBox()
            return
        self.isAutoAlign = True
        self.autoAlignBtn.setEnabled(False)
        
        self.printMsg("Activating XY stage for automated alignment...")
        # If stage is open in stage window, close.
        if self.parent().stagewind.activeStage:
            self.parent().stagewind.activateStage()
        self.xystage = XYstage(self.parent().config.xDefStageOrigin,
                            self.parent().config.yDefStageOrigin)
        if self.xystage.xystageInit == False:
            self.printMsg(" Stage not activated: automated acquisition not possible. Aborting.")
            self.autoAlignBtn.setEnabled(True)
            return
        self.printMsg(" Stage activated.")
        
        ##########################
        self.moveToReferenceCell()
        ##########################
        
        #self.openShutter()
        
        self.firstRun = True
        for j in range(self.numCol):
            for i in range(self.numRow):
                # Convert to correct substrate number in holder
                substrateNum = Acquisition().getSubstrateNumber(i,j)
                
                # Check if the holder has a substrate in that slot
                if self.parent().samplewind.tableWidget.item(i,j).text() != ""  and \
                        self.parent().samplewind.activeSubs[i,j] == True:
                    self.parent().samplewind.colorCellAcq(i,j,"yellow")
                                        
                    # Move stage to desired substrate
                    if self.xystage.xystageInit is True:
                        self.printMsg("\nMoving stage to substrate #"+ \
                                        str(substrateNum) + \
                                        ": ("+str(4-i)+", "+str(4-j)+")")
                        self.xystage.move_to_substrate_4x4(substrateNum)
                        time.sleep(0.1)

                        # Perform alignment analysis 
                        self.cam = CameraFeed()
                        self.setWindowTitle('Camera Alignment Panel - Substrate #'+\
                                    str(substrateNum)+" ("+\
                                    self.parent().samplewind.tableWidget.item(i,j).text()+")")
                        self.setSelWindow(False)
                        if hasattr(self,"cam"):
                            alignFlag, alignPerc, iMax = self.alignment()
                        else:
                            self.deactivateStage()
                            return
                        if alignFlag == 0:
                            self.parent().samplewind.colorCellAcq(i,j,"white")
                            self.printMsg(" Substrate #"+str(substrateNum)+" aligned (alignPerc = "+ str(alignPerc)+")")
                        else:
                            self.parent().samplewind.colorCellAcq(i,j,"grey")
                            if alignFlag == 1:
                                self.printMsg(" Substrate #"+str(substrateNum)+" Empty! (alignPerc = "+ str(alignPerc)+")")
                            if alignFlag == 2:
                                self.printMsg(" Substrate #"+str(substrateNum)+" not aligned! (alignPerc = "+ str(alignPerc)+")")
                        self.delCam()
        self.printMsg("\nAuto-alignment completed")
        #self.deactivateStage()
        #self.closeShutter()
        
        self.enableButtons(True)
        self.setWindowTitle('Camera Alignment Panel')
    '''

    # Perform manual alignment
    def manualAlign(self, live):
        self.delCam()
        #self.openShutter()
        self.cam = CameraFeed()
        self.resetBtn.setEnabled(True)
        self.saveImageMenu.setEnabled(True)
        self.saveImageBtn.setEnabled(True)
        self.isAutoAlign = False
        self.firstRun = True
        if self.alignOn == False:
            self.scene.selectionDef.connect(self.checkManualAlign)
        self.alignOn = True
        self.setSelWindow(live)
        self.resetBtn.setEnabled(True)
        QApplication.processEvents()
        while self.alignOn:
            time.sleep(0.1)
            QApplication.processEvents()
        try:
            self.scene.selectionDef.disconnect()
        except:
            pass
        self.scene.cleanup()
        self.delCam()
        self.enableButtons(True)
        self.saveImageMenu.setEnabled(False)
        self.saveImageBtn.setEnabled(False)
        #self.closeShutter()
        
    # Routine for manual alignment check
    def checkManualAlign(self):
        self.alignFlag, self.alignPerc, self.iMax = self.alignment()
        if self.alignFlag == 0:
            self.inAlignmentMessageBox()
            self.printMsg(" Devices and masks appear to be correctly aligned (alignPerc = "+ str(self.alignPerc)+")")
        else:
            self.outAlignmentMessageBox(self.alignFlag)

    # Define selection window 
    def setSelWindow(self, live):
        self.cameraFeed(live)
        if self.firstRun:
            self.printMsg(" Use Mouse to set the integration window")
        while self.firstRun:
            time.sleep(0.05)
            QApplication.processEvents()
            pass
        self.firstRun = False
            
    # Alignment routine
    def alignment(self):
        image, image_data, image_orig = self.cam.get_image(True,
                             int(self.initial.x()),
                             int(self.final.x()),
                             int(self.initial.y()),
                             int(self.final.y()))
                
        alignPerc, iMax = self.cam.check_alignment( \
                image_data,
                self.config.alignmentIntThreshold)
        print(" DEBUG: alignPerc: ",alignPerc,"; iMax: ",iMax)

        self.checkAlignText.setText(str(alignPerc))
        if float(alignPerc) > self.config.alignmentContrastDefault:
            self.checkAlignText.setStyleSheet("color: rgb(255, 0, 255);")
            alignFlag = 1
        else:
            if float(iMax) > self.config.alignmentIntMax:
                self.checkAlignText.setStyleSheet("color: rgb(255, 0, 255);")
                alignFlag = 2
            else:
                alignFlag = 0
        return alignFlag, alignPerc, iMax
    
    '''
    # Old Alignment routine
    def alignment(self):
        image, image_data, image_orig = self.cam.get_image(True,
                             int(self.initial.x()),
                             int(self.final.x()),
                             int(self.initial.y()),
                             int(self.final.y()))
                
        alignPerc, iMax = self.cam.check_alignment( \
                image_data,
                self.config.alignmentIntThreshold)
        print(" DEBUG: alignPerc: ",alignPerc,"; iMax: ",iMax)

        self.checkAlignText.setText(str(alignPerc))
        if float(alignPerc) > self.config.alignmentContrastDefault \
                and float(iMax) > self.config.alignmentIntMax:
            self.checkAlignText.setStyleSheet("color: rgb(255, 0, 255);")
            return 1, alignPerc, iMax
        else:
            return 0, alignPerc, iMax
    '''

    # Get image from feed
    def cameraFeed(self, live):
        self.scene.cleanup()
        self.setDefaultBtn.setEnabled(True)
        try:
            self.checkAlignText.setStyleSheet("color: rgb(0, 0, 0);")
            self.enableButtons(False)
            if live:
                #self.parent().stagewind.setGeometry(700, 60, 310, 400)
                #self.parent().stagewind.show()
                QApplication.processEvents()
                self.img = self.cam.grab_image_live()
            else:
                QApplication.processEvents()
                self.img = self.cam.grab_image()
            if hasattr(self,"cam"):
                self.image, self.image_data, temp = self.cam.get_image(False,0,0,0,0)
            
                pixMap = QPixmap.fromImage(self.image)
                self.scene.addPixmap(pixMap)
            self.view.fitInView(self.view.sceneRect(), Qt.KeepAspectRatio)

            self.statusBar().showMessage('Camera-feed' + \
                 str(datetime.now().strftime(' (%Y-%m-%d %H-%M-%S)')), 5000)
            self.statusBar().showMessage(' Drag Mouse to select area for alignment', 5000)
        except:
            self.statusBar().showMessage(' Camera not connected', 5000)

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
            self.parent().config.conf['Instruments']['alignmentContrastDefault'] = str(self.alignPerc)
            self.parent().config.conf['Instruments']['alignmentIntMax'] = str(self.iMax)
            with open(self.parent().config.configFile, 'w') as configfile:
                self.parent().config.conf.write(configfile)
            self.parent().config.readConfig(self.parent().config.configFile)
            self.printMsg(" New alignment settings saved as default.")
            self.saveImage()
            return True
        else:
            self.printMsg( " Alignment settings not saved as default")
            return False

    # Warning box for misalignment
    def outAlignmentMessageBox(self, flag):
        msgBox = QMessageBox( self )
        msgBox.setIcon( QMessageBox.Warning )
        if flag == 1:
            msgBox.setText( "WARNING:\nNo substrate appears to be loaded " )
            msgBox.setInformativeText( "Please check and retry...\nClose this box and press ENTER to close" )
            self.printMsg(" No substrates appear to be loaded (alignPerc = "+ str(self.alignPerc)+")")
        if flag == 2:
            msgBox.setText( "WARNING:\nDevices and mask may be misaligned " )
            msgBox.setInformativeText( "Please realign and retry...\nClose this box and press ENTER to close" )
            self.printMsg(" Devices and masks are not aligned! (alignPerc = "+ str(self.alignPerc)+")")
        msgBox.exec_()
    
    # Warning box for misalignment
    def inAlignmentMessageBox(self):
        msgBox = QMessageBox( self )
        msgBox.setIcon( QMessageBox.Information )
        msgBox.setText( "GOOD!\nDevices and mask are correctly aligned " )
        msgBox.setInformativeText( " Close this box and press ENTER to close" )
        msgBox.exec_()

    # No substrate selected box
    def noSubstratesMessageBox(self):
        msgBox = QMessageBox( self )
        msgBox.setIcon( QMessageBox.Information )
        msgBox.setText( "WARNING:\nNo substrates selected " )
        msgBox.setInformativeText( "Please add the substrates in the substrate window" )
        msgBox.exec_()
    
    '''
    # Action for stop button
    def moveToReferenceCell(self):
        msg = "Moving to the Reference cell first?"
        self.printMsg(msg)
        reply = QMessageBox.question(self.parent(), 'Message',
                     msg, QMessageBox.No, QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            self.printMsg("Moving stage to reference cell...")
            QApplication.processEvents()
            self.xystage.move_abs(float(self.config.xPosRefCell),
                              float(self.config.yPosRefCell))
            self.printMsg(msg)
            msgBox = QMessageBox( self )
            msgBox.setIcon( QMessageBox.Information )
            msgBox.setText( "Push OK to continue..." )
            msgBox.setInformativeText( "... once you're done with the reference cell" )
            msgBox.exec_()
        else:
            pass
    '''
    # Show message on log and terminal
    def printMsg(self, msg):
        print(msg)
        self.statusBar().showMessage(msg)
        logger.info(msg)
    
    # Save Image to file
    def saveImage(self):
        filename = "calib"+str(datetime.now().strftime('_%Y%m%d_%H-%M-%S.png'))
        self.printMsg(" Image saved in: "+filename)
        self.cam.save_image(self.parent().config.imagesFolder+filename)

    # Delete camera feed
    def delCam(self):
        if hasattr(self,"cam"):
            self.cam.closeLiveFeed = True
            del self.cam

    # Close camera feed upon closing window.
    def closeEvent(self, event):
        #self.parent().stagewind.close()
        self.firstRun = False
        self.enableButtons(True)
        self.delCam()
        self.scene.cleanup()
        try:
            self.alignOn = False
            self.scene.selectionDef.disconnect()
        except:
            pass
        self.statusBar().showMessage("Camera: Ready")
        self.intensityLabel.setText("")

    '''
    # Deactivate stage after alignment
    def deactivateStage(self):
        self.printMsg(" Moving stage to parking position")
        self.xystage.move_abs(5,5)
        self.printMsg("Deactivating Stage...")
        self.xystage.end_stage_control()
        del self.xystage
        self.printMsg("Stage deactivated")

    # Activate shutter
    def openShutter(self):
        self.printMsg("Activating shutter...")
        try:
            self.shutter = Shutter()
            self.shutter.open()
            self.printMsg(" Shutter activated and open.")
        except:
            self.printMsg(" Shutter not activated: no acquisition possible")
            return

    # Deactivate shutter
    def closeShutter(self):
        if hasattr(self,"shutter"):
            try:
                self.shutter.closed()
                del self.shutter
                self.printMsg("Shutter deactivated")
            except:
                pass
    '''
    # Enable/Disable Buttons
    def enableButtons(self, flag):
        pass
        #self.autoAlignBtn.setEnabled(flag)
        #self.manualAlignBtn.setEnabled(flag)
        #self.liveAlignBtn.setEnabled(flag)
        #self.manualAlignmentMenu.setEnabled(flag)
        #self.autoAlignmentMenu.setEnabled(flag)
        #self.liveAlignmentMenu.setEnabled(flag)

    # Set alignOn variable as False
    def setAlignOn(self, flag):
        self.alignOn = flag
        self.firstRun = flag
        self.resetBtn.setEnabled(flag)

    # Extract pixel intensity from cursor position
    def getPixelIntensity(self):
        if hasattr(self,"cam"):
            try:
                img_y, img_x, c = self.cam.img.shape
            except:
                img_y, img_x, c = 0,0,1
            x = int(self.end.x())
            y = int(self.end.y())
            if x > 0 and y > 0 and x < img_x and y < img_y:
                intensity = cv2.cvtColor(self.cam.img, cv2.COLOR_RGB2GRAY)[y,x]
                #msg = " Intensity pixel at ["+str(x)+", "+str(y)+"]: "+str(intensity)
                msg = " Int: <b>"+str(intensity)+"</b> - ["+str(x)+", "+str(y)+"] "
                #self.printMsg(msg)
                #self.statusBar().showMessage(msg)
                self.intensityLabel.setText(msg)

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
                self.parent().firstRun = False
                self.selectionDef.emit(True)
            if event.key() == Qt.Key_Return:
                self.parent().alignOn=False
    
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



