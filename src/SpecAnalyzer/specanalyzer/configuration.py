'''
configuration
------------------
Class for handling configuration

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''
import configparser, logging, os
from pathlib import Path
from . import __version__

class Configuration():
    def __init__(self):
        self.home = str(Path.home())+"/"
        self.configFile = str(self.home+"SpecAnalyzer.ini")
        self.generalFolder = str(self.home+"SpecAnalyzer/")
        Path(self.generalFolder).mkdir(parents=True, exist_ok=True)
        self.logFile = str(self.generalFolder+"SpecAnalyzer.log")
        self.dataFolder = str(self.generalFolder + 'data/')
        Path(self.dataFolder).mkdir(parents=True, exist_ok=True)
        self.imagesFolder = str(self.generalFolder + 'images/')
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
            'numSubsHolderRow' : 4,
            'numSubsHolderCol' : 4,
            }
    def defineConfAcq(self):
        self.conf['Acquisition'] = {
            'acqMinVoltage' : 0,
            'acqMaxVoltage' : 1,
            'acqStartVoltage' : 0,
            'acqStepVoltage' : 0.5,
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
            'irradiance1Sun' : 3682,
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
        if str(self.appVersion).rsplit('.',1)[0] != __version__.rsplit('.',1)[0] :
            print("Configuration file is for an earlier major version of the software")
            oldConfigFile = str(os.path.splitext(configFile)[0]+"_"+str(self.appVersion)+".ini")
            print("Old config file backup: ",oldConfigFile)
            os.rename(configFile, oldConfigFile )
            print("Creating a new config file.")
            self.createConfig()
        
        self.devConfig = self.conf['Devices']
        self.acqConfig = self.conf['Acquisition']
        self.instrConfig = self.conf['Instruments']
        self.sysConfig = self.conf['System']

        self.numSubsHolderRow = eval(self.devConfig['numSubsHolderRow'])
        self.numSubsHolderCol = eval(self.devConfig['numSubsHolderCol'])
        
        self.acqMinVoltage = eval(self.acqConfig['acqMinVoltage'])
        self.acqMaxVoltage = eval(self.acqConfig['acqMaxVoltage'])
        self.acqStartVoltage = eval(self.acqConfig['acqStartVoltage'])
        self.acqStepVoltage = eval(self.acqConfig['acqStepVoltage'])
        self.acqGateVoltage = eval(self.acqConfig['acqGateVoltage'])
        self.acqHoldTime = eval(self.acqConfig['acqHoldTime'])
        self.acqNumAvScans = eval(self.acqConfig['acqNumAvScans'])
        self.acqDelBeforeMeas = eval(self.acqConfig['acqDelBeforeMeas'])
        self.acqTrackNumPoints = eval(self.acqConfig['acqTrackNumPoints'])
        self.acqTrackInterval = eval(self.acqConfig['acqTrackInterval'])
        self.acqPVmode = eval(self.acqConfig['acqPVmode'])

        self.alignmentIntThreshold = eval(self.instrConfig['alignmentIntThreshold'])
        self.alignmentContrastDefault = eval(self.instrConfig['alignmentContrastDefault'])
        self.alignmentIntMax = eval(self.instrConfig['alignmentIntMax'])
        self.powermeterID = self.instrConfig['powermeterID']
        self.irradiance1Sun = eval(self.instrConfig['irradiance1Sun'])
        self.keithley2400ID = self.instrConfig['keithley2400ID']
        self.agilent4155cID = self.instrConfig['agilent4155cID']

        self.appVersion = self.sysConfig['appVersion']
        self.loggingLevel = self.sysConfig['loggingLevel']
        self.loggingFilename = self.sysConfig['loggingFilename']
        self.csvSavingFolder = self.sysConfig['csvSavingFolder']
        self.saveLocalCsv = eval(self.sysConfig['saveLocalCsv'])

    # Save current parameters in configuration file
    def saveConfig(self, configFile):
        try:
            with open(configFile, 'w') as configfile:
                self.conf.write(configfile)
        except:
            print("Error in saving parameters")
