'''
configuration
------------------
Class for handling configuration

Copyright (C) 2017-2018 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''
import configparser, logging, os
from pathlib import Path
from datetime import datetime
from . import __version__

class Configuration():
    def __init__(self):
        self.home = str(Path.home())+"/"
        self.configFile = self.home+"SpecAnalyzer.ini"
        self.generalFolder = self.home+"SpecAnalyzer/"
        Path(self.generalFolder).mkdir(parents=True, exist_ok=True)
        self.logFile = self.generalFolder+"SpecAnalyzer.log"
        self.dataFolder = self.generalFolder + 'data/'
        Path(self.dataFolder).mkdir(parents=True, exist_ok=True)
        self.imagesFolder = self.generalFolder + 'images/'
        Path(self.imagesFolder).mkdir(parents=True, exist_ok=True)
        self.conf = configparser.ConfigParser()
        self.conf.optionxform = str
    
    # Create configuration file
    def createConfig(self):
        try:
            self.defineConfDevices()
            self.defineConfAcq()
            self.defineConfInstr()
            self.defineConfSystem()
            with open(self.configFile, 'w') as configfile:
                self.conf.write(configfile)
        except:
            print("Error in creating configuration file")

    # Hadrcoded default definitions for the confoguration file
    def defineConfDevices(self):
        self.conf['Devices'] = {
            'deviceArea' : 1,
            }
    def defineConfAcq(self):
        self.conf['Acquisition'] = {
            'acqMinVoltage' : -5,
            'acqMaxVoltage' : 5,
            'acqStartVoltage' : 0,
            'acqStepVoltage' : 0.1,
            'acqGateVoltage' : 0,
            'acqHoldTime' : 0.1,
            'acqNumAvScans' : 1,
            'acqDelBeforeMeas' : 1,
            'acqTrackNumPoints' : 5,
            'acqTrackInterval' : 2,
            'acqPVmode' : True,
            }
    def defineConfInstr(self):
        self.conf['Instruments'] = {
            'alignmentIntThreshold' : 0.6,
            'alignmentContrastDefault' : 1,
            'alignmentIntMax' : 10,
            'powermeterID' : "USB0::0x1313::0x8072::P2008173::INSTR",
            'irradiance1Sun' : 4.5044,
            'irradianceSensorArea' : 3.24,
            'keithley2400ID' : "GPIB0::24::INSTR",
            'agilent4155cID' : "GPIB0::17::INSTR",
            }
    def defineConfSystem(self):
        self.conf['System'] = {
            'appVersion' : __version__,
            'loggingLevel' : logging.INFO,
            'loggingFilename' : self.logFile,
            'csvSavingFolder' : self.dataFolder,
            'saveLocalCsv' : True,
            }

    # Read configuration file into usable variables
    def readConfig(self, configFile):
        self.conf.read(configFile)
        self.sysConfig = self.conf['System']
        self.appVersion = self.sysConfig['appVersion']
        try:
            self.devConfig = self.conf['Devices']
            self.acqConfig = self.conf['Acquisition']
            self.instrConfig = self.conf['Instruments']
            self.sysConfig = self.conf['System']

            self.deviceArea = self.conf.getfloat('Devices','deviceArea')
        
            self.acqMinVoltage = self.conf.getfloat('Acquisition','acqMinVoltage')
            self.acqMaxVoltage = self.conf.getfloat('Acquisition','acqMaxVoltage')
            self.acqStartVoltage = self.conf.getfloat('Acquisition','acqStartVoltage')
            self.acqStepVoltage = self.conf.getfloat('Acquisition','acqStepVoltage')
            self.acqGateVoltage = self.conf.getfloat('Acquisition','acqGateVoltage')
            self.acqHoldTime = self.conf.getfloat('Acquisition','acqHoldTime')
            self.acqNumAvScans = self.conf.getint('Acquisition','acqNumAvScans')
            self.acqDelBeforeMeas = self.conf.getfloat('Acquisition','acqDelBeforeMeas')
            self.acqTrackNumPoints = self.conf.getint('Acquisition','acqTrackNumPoints')
            self.acqTrackInterval = self.conf.getfloat('Acquisition','acqTrackInterval')
            self.acqPVmode = self.conf.getboolean('Acquisition','acqPVmode')

            self.alignmentIntThreshold = self.conf.getfloat('Instruments','alignmentIntThreshold')
            self.alignmentContrastDefault = self.conf.getfloat('Instruments','alignmentContrastDefault')
            self.alignmentIntMax = self.conf.getfloat('Instruments','alignmentIntMax')
            self.powermeterID = self.instrConfig['powermeterID']
            self.irradiance1Sun = self.conf.getfloat('Instruments','irradiance1Sun')
            self.irradianceSensorArea = self.conf.getfloat('Instruments','irradianceSensorArea')
            self.keithley2400ID = self.instrConfig['keithley2400ID']
            self.agilent4155cID = self.instrConfig['agilent4155cID']

            self.appVersion = self.sysConfig['appVersion']
            self.loggingLevel = self.sysConfig['loggingLevel']
            self.loggingFilename = self.sysConfig['loggingFilename']
            self.csvSavingFolder = self.sysConfig['csvSavingFolder']
            self.saveLocalCsv = self.conf.getboolean('System','saveLocalCsv')

        except:
            print("Configuration file is for an earlier version of the software")
            oldConfigFile = str(os.path.splitext(configFile)[0] + "_" +\
                    str(datetime.now().strftime('%Y%m%d-%H%M%S'))+".ini")
            print("Old config file backup: ",oldConfigFile)
            os.rename(configFile, oldConfigFile )
            print("Creating a new config file.")
            self.createConfig()
            self.readConfig(configFile)

    # Save current parameters in configuration file
    def saveConfig(self, configFile):
        try:
            with open(configFile, 'w') as configfile:
                self.conf.write(configfile)
        except:
            print("Error in saving parameters")
