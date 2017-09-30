'''
agilent4155c.py
-------------
Class for providing a hardware support for 
for the Agilent 4155C

Version: 20170927

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

import visa, time
import numpy as np

class Agilent4155c(object):
    '''
    SourceMeter Class
        - Agilent 4155C Semiconductor Parameter Analyzer
    '''
    def __init__(self, visa_string):
        self.manager = visa.ResourceManager().open_resource(visa_string)
        #self.manager = visa.ResourceManager('@py').open_resource(visa_string)
        print(self.ask("*IDN?"))
        del self.manager.timeout
        self.write("*RST")
        self.write(":SYST:SSAV 0")
        self.write(":PAGE:CHAN:MODE SWEEP")
        self.write(":PAGE:CHAN:SMU4:DIS")
        self.write(":PAGE:CHAN:VSU1:DIS")
        self.write(":PAGE:CHAN:VSU2:DIS")
        self.write(":PAGE:CHAN:VMU1:DIS")
        self.write(":PAGE:CHAN:VMU2:DIS")
        
        self.write(":PAGE:CHAN:SMU1:VNAME 'VD'")
        self.write(":PAGE:CHAN:SMU2:VNAME 'VS'")
        self.write(":PAGE:CHAN:SMU3:VNAME 'VG'")
        self.write(":PAGE:CHAN:SMU1:INAME 'ID'")
        self.write(":PAGE:CHAN:SMU2:INAME 'IS'")
        self.write(":PAGE:CHAN:SMU3:INAME 'IG'")
        self.write(":PAGE:CHAN:SMU1:MODE V")
        self.write(":PAGE:CHAN:SMU1:FUNC VAR1")
        self.write(":PAGE:CHAN:SMU2:MODE COMM")
        self.write(":PAGE:CHAN:SMU2:FUNC CONS")
        self.write(":PAGE:CHAN:SMU3:MODE V")
        self.write(":PAGE:CHAN:SMU3:FUNC CONS")
        time.sleep(0.5)
        self.voltage_limit = 100.
        self.current_limit = 1.

    def __del__(self):
        try:
            self.write(":SYST:SSAV 5")
            self.manager.close()
        except:
            pass

    ## common visa api wrappers
    # write: send command with out expecting return
    # read: instrument response
    # ask: write + read
    def write(self, command):
        self.manager.write(command)
    def read(self):
        return self.manager.read()
    def ask(self, command):
        return self.manager.query(command)
        
    def sweep(self, start, end, step, gate):
        self.write("*CLS")
        self.write(":PAGE:MEAS:VAR1:START %f" % float(start))
        self.write(":PAGE:MEAS:VAR1:STOP %f" % float(end))
        self.write(":PAGE:MEAS:VAR1:STEP %f" % float(step))
        self.write(":PAGE:MEAS:VAR1:STEP %f" % float(step))
        self.write(":PAGE:MEAS:CONS:SMU3 %f" % float(gate))
        self.write(":PAGE:MEAS:SSTOP COMP")
        self.write("*OPC")
        #print(" Acquisition in progress...")
        self.write(":PAGE:SCON:SING")
        self.write("*WAI")

    def read_sweep_values(self):
        self.write(":FORM:DATA ASC")
        self.write(":PAGE:GLIS")
        self.write(":PAGE:GLIS:SCAL:AUTO ONCE")
        I_data = self.manager.query_ascii_values(":DATA? 'ID' ")
        V_data = self.manager.query_ascii_values(":DATA? 'VD' ")
        return V_data, I_data

    ### These are wrappers for common use with Keithley 2400
    def get_mode(self, key):
        pass

    def set_mode(self, mode):
        if mode == 'VOLT':
            self.write(":PAGE:CHAN:SMU1:MODE V")
        elif mode == 'CURR':
            self.write(":PAGE:CHAN:SMU1:MODE I")

    def set_limit(self, voltage = None, current = None):
        if voltage != None:
            if voltage == 'MAX':
                pass
            else:
                self.voltage_limit = voltage
                
        if current != None:
            if current == 'MAX':
                pass
            else:
                self.current_limit = current
        
    def set_output(self, voltage = None, current = None):
        if voltage != None:
            self.set_mode('VOLT')
            if voltage <= self.voltage_limit:
                self.sweep(voltage,voltage,0,0)
            else:
                self.sweep(self.voltage_limit,self.voltage_limit,0,0)
        elif current != None:
            self.set_mode('CURR')
            if current <= self.current_limit:
                self.sweep(current,current,0,0)
            else:
                self.sweep(self.current_limit,self.current_limit,0,0)
    
    def read_values(self):
        data = self.read_sweep_values()
        return data[0][0], data[1][0]

    def on(self):
        pass
    
    def off(self):
        self.write("*OPC")
        self.write("*WAI")
        pass

### This is only for testing - to be removed ###
if __name__ == '__main__':
    # test
    an = Agilent4155c('GPIB0::17::INSTR')
    an.set_output(voltage = 1)
    print("Voltage:",an.read_values()[0]," Current:",an.read_values()[1])
    an.set_output(current = 0)
    print("Voltage:",an.read_values()[0]," Current:",an.read_values()[1])

    an.set_mode('VOLT')
    sweep = an.sweep(-5,5,0.01,0)
    print(an.read_sweep_values()[0], an.read_sweep_values()[1])    
    pass
