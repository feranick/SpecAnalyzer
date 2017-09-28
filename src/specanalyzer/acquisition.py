'''
acquisition.py
-------------
Class for providing a procedural support for data acquisition

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>
Copyright (C) 2017 Tony Wu <tonyw@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''
import numpy as np
import pandas as pd
import time, random, math
from datetime import datetime
from PyQt5.QtWidgets import (QApplication,QAbstractItemView)
from PyQt5.QtCore import (Qt,QObject, QThread, pyqtSlot, pyqtSignal)
from .acquisitionWindow import *
from .modules.sourcemeter.keithley2400 import *
from .modules.sourcemeter.agilent4155c import *

class Acquisition(QObject):
    def __init__(self, parent=None):
        super(Acquisition, self).__init__(parent)
    
    # Collect acquisition parameters into a DataFrame to be used for storing (as csv or json)
    def getAcqParameters(self):
        self.numRow = self.parent().config.numSubsHolderRow
        self.numCol = self.parent().config.numSubsHolderCol
        pdframe = pd.DataFrame({
                'Acq Min Voltage': [self.parent().acquisitionwind.minVText.text()],
                'Acq Max Voltage': [self.parent().acquisitionwind.maxVText.text()],
                'Acq Start Voltage': [self.parent().acquisitionwind.startVText.text()],
                'Acq Step Voltage': [self.parent().acquisitionwind.stepVText.text()],
                'Acq Gate Voltage': [self.parent().acquisitionwind.gateVText.text()],
                'Acq Num Aver Scans': [int(self.parent().acquisitionwind.numAverScansText.text())],
                'Delay Before Meas': [self.parent().acquisitionwind.delayBeforeMeasText.text()],
                'Num Track Points': [int(self.parent().acquisitionwind.numPointsText.value())],
                'Track Interval': [self.parent().acquisitionwind.IntervalText.text()],
                'Comments': [self.parent().commentsText.text()]})
        return pdframe[['Acq Min Voltage','Acq Max Voltage','Acq Start Voltage',
                'Acq Step Voltage','Acq Gate Voltage','Acq Num Aver Scans','Delay Before Meas',
                'Num Track Points','Track Interval','Comments']]
                
    def start(self):
        # Using ALT with Start Acquisition button:
        # 1. overrides the config settings.
        # 2. Data is saved locally
        self.modifiers = QApplication.keyboardModifiers()
        self.dfAcqParams = self.getAcqParameters()
        if self.parent().deviceText.text()=="":
            print("Please add device name")
            return
        self.parent().acquisitionwind.enableAcqPanel(False)
        self.parent().enableButtonsAcq(False)
        self.parent().resultswind.show()
        self.parent().resultswind.clearPlots(False,False)
        
        self.acq_thread = acqThread(self.dfAcqParams, self)
        self.acq_thread.Msg.connect(self.printMsg)
        self.acq_thread.acqJVComplete.connect(lambda JV,perfData,deviceID: \
                self.JVDeviceProcess(JV,perfData,deviceID,self.dfAcqParams))
        self.acq_thread.tempTracking.connect(lambda JV,perfData,deviceID,setupTable,saveData: \
                self.plotTempTracking(JV,perfData,deviceID,self.dfAcqParams,setupTable,saveData))
        self.acq_thread.maxPowerDev.connect(self.printMsg)
        self.acq_thread.start()

    # Action for stop button
    def stop(self):
        quit_msg = "Are you sure you want to stop the acquisition?"
        print(quit_msg)
        reply = QMessageBox.question(self.parent(), 'Message',
                     quit_msg, QMessageBox.No, QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            msg = "Acquisition stopped: " + self.acq_thread.getDateTimeNow()[0]+ \
                  " at "+self.acq_thread.getDateTimeNow()[1]
            self.acq_thread.stop()
            self.printMsg(msg)
        else:
            pass
    # Show message on log and terminal
    def printMsg(self, msg):
        print(msg)
        logger.info(msg)
        self.parent().statusBarLabel.setText(msg)

    # Process JV Acquisition to result page
    def JVDeviceProcess(self, JV, perfData, deviceID, dfAcqParams):
        self.parent().resultswind.clearPlots(False,False)
        self.parent().resultswind.setupResultTable()
        self.parent().resultswind.processDeviceData(deviceID, dfAcqParams, perfData, JV, True)
        QApplication.processEvents()
        time.sleep(1)
            
    # Plot temporary data from tracking
    def plotTempTracking(self, JV, perfData, deviceID, dfAcqParams, setupTable, saveData):
        self.parent().resultswind.clearPlots(False,False)
        if setupTable is True:
            self.parent().resultswind.setupResultTable()
        self.parent().resultswind.processDeviceData(deviceID, dfAcqParams, perfData, JV, saveData)
        QApplication.processEvents()
        time.sleep(1)

# Main Class for Acquisition
# Everything happens here!
class acqThread(QThread):

    acqJVComplete = pyqtSignal(np.ndarray, np.ndarray, str)
    tempTracking = pyqtSignal(np.ndarray, np.ndarray, str, bool, bool)
    maxPowerDev = pyqtSignal(str)
    Msg = pyqtSignal(str)

    def __init__(self, dfAcqParams, parent=None):
        super(acqThread, self).__init__(parent)
        self.dfAcqParams = dfAcqParams
        self.powerIn = float(self.parent().parent().config.conf['Instruments']['irradiance1Sun']) * \
            float(self.parent().parent().deviceSizeText.text()) * 0.00064516

    def __del__(self):
        self.wait()

    def stop(self):
        self.terminate()
        self.endAcq()
    
    def run(self):

        # Activate sourcemeter
        self.Msg.emit("Activating sourcemeter...")
        try:
            if self.parent().parent().sourcemeterwind.instrumentCBox.currentIndex() == 0:
                self.parent().source_meter = Agilent4155c(self.parent().parent().config.agilent4155cID)
            else:
                self.parent().source_meter = Keithley2400(self.parent().parent().config.keithley2400ID)
            self.parent().source_meter.set_limit(voltage=20., current=1.)
            self.parent().source_meter.on()
        except:
            self.Msg.emit(" Sourcemeter not activated: no acquisition possible")
            self.stop()
            return
        self.Msg.emit(" Sourcemeter activated.")

        ### Setup interface and get parameters before acquisition
        self.Msg.emit("Acquisition started: "+self.getDateTimeNow()[0]+" at " + \
                self.getDateTimeNow()[1])
        
        # If all is OK, start acquiring
                
        # Check if the holder has a substrate in that slot
        if self.parent().parent().deviceText.text() != "":
            self.max_power = []
            #self.devMaxPower = 0
            deviceID = self.parent().parent().deviceText.text()
            # prepare parameters, plots, tables for acquisition
            self.Msg.emit("  Acquiring JV from device: " + deviceID)

            # Acquire forward and backward sweeps
            sweepF, sweepB = self.measure_sweep(self.dfAcqParams)
            # Acquire JV for performance parameters
            JVOKflag, JVF, JVB, perfDataF, perfDataB = self. measure_voc_jsc_mpp(self.dfAcqParams)            
            if JVOKflag:
                self.acqJVComplete.emit(JVF, perfDataF, deviceID+"_JV-forward")
                self.acqJVComplete.emit(JVB, perfDataB, deviceID+"_JV-backward")

                #Right now the voc, jsc and mpp are extracted from the JV in JVDeviceProcess
                #self.acqJVComplete.emit(JVF, perfData, deviceID)

                #self.max_power.append(np.max(JVF[:, 0] * JVF[:, 1]))
                self.Msg.emit('  Device '+deviceID+' acquisition: complete')

                if self.parent().parent().acquisitionwind.enableTrackingBox.isChecked() == True:
                    # Tracking
                    time.sleep(1)

                    # Use this to get the simple JV used for detecting Vpmax
                    perfData, JV = self.tracking(deviceID, self.dfAcqParams, JVF, perfDataF)
                    # Alternatively use this for a complete JV sweep
                    #JV = self.devAcqJV()

                    #self.acqJVComplete.emit(JV, perfData, substrateID+str(self.devMaxPower), i, j)
                    self.Msg.emit(' Device '+deviceID+' tracking: complete')

                self.Msg.emit("Acquisition Completed: "+ self.getDateTimeNow()[0] + \
                    " at "+self.getDateTimeNow()[1])
            self.endAcq()

    def endAcq(self):
        self.parent().parent().acquisitionwind.enableAcqPanel(True)
        self.parent().parent().enableButtonsAcq(True)

        # park the stage close to origin, deactivate.
        try:
            self.parent().source_meter.off()
            del self.parent().source_meter
            self.Msg.emit("Sourcemeter deactivated")
        except:
            pass     
        
        # Re-enable panels and buttons
        self.parent().parent().acquisitionwind.enableAcqPanel(True)
        self.parent().parent().enableButtonsAcq(True)
        QApplication.processEvents()
        self.Msg.emit("System: ready")

    ## measurements: JV
    # dfAcqParams : self.dfAcqParams
    def measure_sweep(self, dfAcqParams):
        deviceID = self.parent().parent().deviceText.text()
        #perfData = np.zeros((0,8))
        
        #self.source_meter.set_mode('VOLT')
        self.parent().source_meter.set_mode('VOLT')
        self.parent().source_meter.on()

        # measurement parameters
        v_min = float(dfAcqParams.get_value(0,'Acq Min Voltage'))
        v_max = float(dfAcqParams.get_value(0,'Acq Max Voltage'))
        v_start = float(dfAcqParams.get_value(0,'Acq Start Voltage'))
        v_step = float(dfAcqParams.get_value(0,'Acq Step Voltage'))
        v_gate = float(dfAcqParams.get_value(0,'Acq Gate Voltage'))
        scans = int(dfAcqParams.get_value(0,'Acq Num Aver Scans'))
        hold_time = float(dfAcqParams.get_value(0,'Delay Before Meas'))
        time.sleep(hold_time)
        
        # enforce
        if v_start < v_min and v_start > v_max and v_min > v_max:
            raise ValueError('Voltage Errors')

        # create list of voltage to measure
        v_list_full = np.arange(v_min-2., v_max + 2., v_step)
        v_list = v_list_full[np.logical_and(v_min-1e-9 <= v_list_full, v_list_full <= v_max+1e-9)]
        start_i = np.argmin(abs(v_start - v_list))

        N = len(v_list)
        #backward sweep
        i_list_back = list(range(0, N))[::-1]
        #forward sweep 1
        i_list_forw1 = list(range(start_i, N))
        #forward sweep 2
        i_list_forw2 = list(range(0, start_i))

        # create data array
        data = np.zeros((N, 3))
        data[:, 0] = v_list
        
        if self.parent().parent().sourcemeterwind.instrumentCBox.currentIndex() == 0:
            self.Msg.emit('  Device '+deviceID+': acquiring forward sweep')
            self.parent().source_meter.set_mode('VOLT')
            self.parent().source_meter.sweep(v_start, v_max, v_step, v_gate)
            data[i_list_forw1, 1] = self.parent().source_meter.read_sweep_values()[1]

            self.Msg.emit('  Device '+deviceID+': acquiring backward sweep')
            self.parent().source_meter.sweep(v_max, v_min, - v_step, v_gate)
            data[:, 2] = np.flipud(self.parent().source_meter.read_sweep_values()[1])
            perfDataB = self.analyseJV(data[:, (0,2)])
            self.acqJVComplete.emit(data[:, (0,2)], perfDataB, deviceID+"_sweep-back")

            self.Msg.emit('  Device '+deviceID+': completing forward sweep')
            self.parent().source_meter.sweep(v_min, v_start-v_step, v_step, v_gate)
            try:
                data[i_list_forw2, 1] = self.parent().source_meter.read_sweep_values()[1]
            except:
                pass
            perfDataF = self.analyseJV(data[:, (0,1)])
            self.acqJVComplete.emit(data[:, (0,1)], perfDataF, deviceID+"_sweep-forw")

        else:
            
            #self.tempTracking.emit(np.array([data[start_i-1, 0:2]]), np.zeros((1,8)),
            #            self.parent().parent().deviceText.text(), True, False)

            self.Msg.emit('  Device '+deviceID+': acquiring forward sweep')
            for i in i_list_forw1:
                self.parent().source_meter.set_output(voltage = v_list[i])
                time.sleep(hold_time)
                data[i,1] = self.parent().source_meter.read_values()[1]
                #print(data[start_i:i, 0:2])
            #self.tempTracking.emit(data[start_i:N, 0:2], np.zeros((1,8)),
            #    self.parent().parent().deviceText.text(), False, False)

            self.Msg.emit('  Device '+deviceID+': acquiring backward sweep')
            for i in i_list_back:
                self.parent().source_meter.set_output(voltage = v_list[i])
                time.sleep(hold_time)
                data[i,2] = self.parent().source_meter.read_values()[1]

            perfDataB = self.analyseJV(data[:, (0,2)])
            self.acqJVComplete.emit(data[:, (0,2)], perfDataB, deviceID+"_sweep-back")
            #self.tempTracking.emit(data[:, (0,2)], np.zeros((1,8)),
            #    self.parent().parent().deviceText.text()+"_back", False, False)

            self.Msg.emit('  Device '+deviceID+': completing forward sweep') 
            for i in i_list_forw2:
                self.parent().source_meter.set_output(voltage = v_list[i])
                time.sleep(hold_time)
                data[i,1] = self.parent().source_meter.read_values()[1]
                #print(data[0:i, 0:2])
            #self.tempTracking.emit(data[:, 0:2], np.zeros((1,8)),
            #    self.parent().parent().deviceText.text()+"_forw", True, False)
            perfDataF = self.analyseJV(data[:, (0,1)])
            self.acqJVComplete.emit(data[:, (0,1)], perfDataF, deviceID+"_sweep-forw")
            print(data)
        return data[:, 0:2], data[:,(0,2)]

    ## measurements: voc, jsc
    def measure_voc_jsc(self):
        # voc
        self.parent().source_meter.set_mode('CURR')
        self.parent().source_meter.on()
        self.parent().source_meter.set_output(current = 0.)
        voc = self.parent().source_meter.read_values()[0]

        # jsc
        self.parent().source_meter.set_mode('VOLT')
        self.parent().source_meter.on()
        self.parent().source_meter.set_output(voltage = 0.)
        jsc = self.parent().source_meter.read_values()[1]
        return voc, jsc

    ## measurements: voc, jsc, mpp
    def measure_voc_jsc_mpp(self, dfAcqParams):
        deviceID = self.parent().parent().deviceText.text()
        #perfData = np.zeros((0,8))

        # measurement parameters
        v_min = float(dfAcqParams.get_value(0,'Acq Min Voltage'))
        v_max = float(dfAcqParams.get_value(0,'Acq Max Voltage'))
        v_start = float(dfAcqParams.get_value(0,'Acq Start Voltage'))
        v_step = float(dfAcqParams.get_value(0,'Acq Step Voltage'))
        v_gate = float(dfAcqParams.get_value(0,'Acq Gate Voltage'))
        scans = int(dfAcqParams.get_value(0,'Acq Num Aver Scans'))
        hold_time = float(dfAcqParams.get_value(0,'Delay Before Meas'))

        # measurements: voc, jsc
        voc, jsc = self.measure_voc_jsc()

        # measurement parameters
        v_min = 0.
        v_max = voc
        #v_max = 2 #for testing only

        if v_max - v_min < v_step:
            self.Msg.emit('  Voc appears to be close to V=0. Aborting') 
            return False, None, None, None, None
        
        # measure
        v_list = np.arange(v_min, v_max+1e-9, v_step)
        
        JV = np.zeros((len(v_list),3))
        JV[:, 0] = v_list
        JVtemp = np.zeros((len(v_list),3))
        JVtemp[:, 0] = v_list
        
        self.Msg.emit('  Device '+deviceID+': acquiring JV forward for analsys')
        
        if self.parent().parent().sourcemeterwind.instrumentCBox.currentIndex() == 0:
            for n in range(scans):
                self.Msg.emit('  Device '+deviceID+': acquiring forward sweep')
                self.parent().source_meter.set_mode('VOLT')
                self.parent().source_meter.sweep(v_min, v_max, v_step, v_gate)
                JVtemp[:, 1] = self.parent().source_meter.read_sweep_values()[1]

                self.Msg.emit('  Device '+deviceID+': acquiring backward sweep')
                self.parent().source_meter.sweep(v_max, v_min, - v_step, v_gate)
                JVtemp[:, 2] = np.flipud(self.parent().source_meter.read_sweep_values()[1])
            
            JV[:,1] = (JVtemp[:,1] + JV[:,1]*n)/(n+1)
            JV[:,2] = (JVtemp[:,2] + JV[:,2]*n)/(n+1)

        else:
            i_list_forw = list(range(0, len(v_list)))
            i_list_back = i_list_forw[::-1]
            for n in range(scans):
                self.Msg.emit('  Device '+deviceID+': acquiring JV forward for analsys, scan: '+str(n)+'/'+str(scans))
                for i in i_list_forw:
                    self.parent().source_meter.set_output(voltage = v_list[i])
                    time.sleep(hold_time)
                    JVtemp[i,1]= self.parent().source_meter.read_values()[1]

                self.Msg.emit('  Device '+deviceID+': acquiring JV backward for analsys, scan: '+str(n)+'/'+str(scans))
                for i in i_list_back:
                    self.parent().source_meter.set_output(voltage = v_list[i])
                    time.sleep(hold_time)
                    JVtemp[i,2]= self.parent().source_meter.read_values()[1]

            JV[:,1] = (JVtemp[:,1] + JV[:,1]*n)/(n+1)
            JV[:,2] = (JVtemp[:,2] + JV[:,2]*n)/(n+1)

        perfDataF = self.analyseJV(JV[:, (0,1)])
        perfDataB = self.analyseJV(JV[:, (0,2)])
        
        return True, JV[:, 0:2], JV[:,(0,2)], perfDataF, perfDataB

    # Tracking (take JV once and track Vpmax)
    # dfAcqParams : self.dfAcqParams
    def tracking(self, deviceID, dfAcqParams, JV, perfData):
        hold_time = float(dfAcqParams.get_value(0,'Delay Before Meas'))
        numPoints = int(dfAcqParams.get_value(0,'Num Track Points'))
        trackTime = float(dfAcqParams.get_value(0,'Track Interval'))
        startTime = time.time()

        self.Msg.emit("Tracking device: "+deviceID+" (time-step: 0)")

        Vpmax = float(perfData[0][5])
        #self.tempTracking.emit(JV, perfData, deviceID, True, False)
        for n in range(1, numPoints):
            time.sleep(trackTime)
            timeStep = time.time()-startTime
            self.Msg.emit("Tracking device: "+deviceID+" (time-step: "+str(n)+"/"+\
                          str(numPoints)+" - {0:0.1f}s)".format(timeStep))
            voc, jsc = self.measure_voc_jsc()
            
            self.parent().source_meter.set_output(voltage = Vpmax)
            time.sleep(hold_time)
            Jpmax = self.parent().source_meter.read_values()[1]
            try:
                FF = Vpmax*Jpmax*100/(voc*jsc)
                effic = Vpmax*Jpmax/self.powerIn
            except:
                FF = 0.
                effic = 0.
            data = np.array([voc, jsc, Vpmax, Vpmax*Jpmax,FF,effic])
            data = np.hstack(([self.getDateTimeNow()[0],
                                   self.getDateTimeNow()[1],timeStep], data))
            perfData = np.vstack((data, perfData))
            #self.tempTracking.emit(JV, perfData, deviceID, False, False)
        self.tempTracking.emit(JV, perfData, deviceID+"_tracking", True, True)
        return perfData, JV

    # Extract parameters from JV
    def analyseJV(self, JV):
        powerIn = float(self.parent().parent().config.conf['Instruments']['irradiance1Sun'])*0.00064516
        PV = np.zeros(JV.shape)
        PV[:,0] = JV[:,0]
        PV[:,1] = JV[:,0]*JV[:,1]
        # measurements: voc, jsc
        Voc, Jsc = self.measure_voc_jsc()
        #Voc = JV[JV.shape[0]-1,0]
        #Jsc = JV[0,1]
        Vpmax = PV[np.where(PV == np.amax(PV)),0][0][0]
        Jpmax = JV[np.where(PV == np.amax(PV)),1][0][0]
        if Voc != 0. and Jsc != 0.:
            FF = Vpmax*Jpmax*100/(Voc*Jsc)
            effic = Vpmax*Jpmax/self.powerIn
        else:
            FF = 0.
            effic = 0.
        data = np.array([Voc, Jsc, Vpmax, Vpmax*Jpmax,FF,effic])
        data = np.hstack((0., data))
        data = np.hstack((self.getDateTimeNow()[1], data))
        data = np.hstack((self.getDateTimeNow()[0], data))
        return np.array([data])

    # Get date/time
    def getDateTimeNow(self):
        return str(datetime.now().strftime('%Y-%m-%d')),\
                    str(datetime.now().strftime('%H-%M-%S'))
