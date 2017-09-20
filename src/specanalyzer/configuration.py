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
import configparser, logging

class Configuration():
    def __init__(self):
        self.configFile = "SpecAnalyzer.ini"
        self.conf = configparser.ConfigParser()
    
    # Create configuration file
    def createConfig(self):
        try:
            self.defineConfAcq()
            self.defineConfInstr()
            self.defineConfSystem()
            with open(self.configFile, 'w') as configfile:
                self.conf.write(configfile)
        except:
            print("Error in creating configuration file")

    # Hadrcoded default definitions for the configuration file
    def defineConfAcq(self):
        self.conf['Acquisition'] = {
            'acqMinVoltage' : 0,
            'acqMaxVoltage' : 1,
            'acqStartVoltage' : 0,
            'acqStepVoltage' : 0.02,
            'acqNumAvScans' : 5,
            'acqDelBeforeMeas' : 1,
            }
    def defineConfInstr(self):
        self.conf['Instruments'] = {
            'alignmentIntThreshold' : 0.6,
            'alignmentContrastDefault' : 1,
            'alignmentIntMax' : 10,
            'powermeterID' : "USB0::0x1313::0x8072::P2008173::INSTR",
            'irradiance1Sun' : 3682,
            'switchboxID' : "GPIB0::16::INSTR",
            'sourcemeterID' : "GPIB0::24::INSTR",
            }
    def defineConfSystem(self):
        self.conf['System'] = {
            'loggingLevel' : logging.INFO,
            'loggingFilename' : "SpecAnalyzer.log",
            'csvSavingFolder' : "./data",
            'saveLocalCsv' : False,
            }

    # Read configuration file into usable variables
    def readConfig(self, configFile):
        self.conf.read(configFile)
        self.acqConfig = self.conf['Acquisition']
        self.instrConfig = self.conf['Instruments']
        self.sysConfig = self.conf['System']
        
        self.acqMinVoltage = eval(self.acqConfig['acqMinVoltage'])
        self.acqMaxVoltage = eval(self.acqConfig['acqMaxVoltage'])
        self.acqStartVoltage = eval(self.acqConfig['acqStartVoltage'])
        self.acqStepVoltage = eval(self.acqConfig['acqStepVoltage'])
        self.acqNumAvScans = eval(self.acqConfig['acqNumAvScans'])
        self.acqDelBeforeMeas = eval(self.acqConfig['acqDelBeforeMeas'])

        self.alignmentIntThreshold = eval(self.instrConfig['alignmentIntThreshold'])
        self.alignmentContrastDefault = eval(self.instrConfig['alignmentContrastDefault'])
        self.alignmentIntMax = eval(self.instrConfig['alignmentIntMax'])
        self.powermeterID = self.instrConfig['powermeterID']
        self.irradiance1Sun = eval(self.instrConfig['irradiance1Sun'])
        self.switchboxID = self.instrConfig['switchboxID']
        self.sourcemeterID = self.instrConfig['sourcemeterID']

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
