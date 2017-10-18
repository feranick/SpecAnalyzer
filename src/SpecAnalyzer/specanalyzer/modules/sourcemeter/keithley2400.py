'''
keithley2400.py
-------------
Class for providing a hardware support for 
for the Keithley 2400 sourcemeter

Version: 20171018

Copyright (C) 2017 Tony Wu <tonyw@mit.edu>
Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''
import visa

class Keithley2400(object):
    '''
    SourceMeter Class
        - Keithley 2400
        - command manual: http://research.physics.illinois.edu/bezryadin/labprotocol/Keithley2400Manual.pdf
    '''
    def __init__(self, visa_string):
        self.manager = visa.ResourceManager().open_resource(visa_string) 
        print(self.ask('*IDN?'))
        # for safety
        self.off()
        self.write('SOUR:CURR 0')
        self.write('SOUR:VOLT 0')
        self.voltage_limit = 100.
        self.current_limit = 1.

        # init mode
        self.set_mode('VOLT')
        self.write('SYSTEM:BEEP:STATE OFF')
        self.write('FORM:ELEM VOLT,CURR')

    def __del__(self):
        try:
            self.off()
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

    ## keithley api
    def get_mode(self, key):
        if key.upper() == 'SOURCE':
            return self.mode
        else:
            return 'CURR' if self.mode == 'VOLT' else 'VOLT'

    def set_mode(self, mode):
        """
        Set source mode, CURRent or VOLTage. 
        """
        abv_mode = mode[0:4].upper()
        if abv_mode in ['VOLT', 'CURR']:
            self.mode = abv_mode
        else:
            raise ValueError('Wrong mode!')

        self.write('SOUR:FUNC {}'.format(self.get_mode('source')))
        self.write('SOUR:{}:MODE FIX'.format(self.get_mode('source')))
        self.write('SOUR:{}:RANG:AUTO ON'.format(self.get_mode('source')))

        self.write('SENS:FUNC "{}"'.format(self.get_mode('measure')))
        self.write('SENS:{}:RANG:AUTO ON'.format(self.get_mode('measure')))

    def set_limit(self, voltage = None, current = None):
        if voltage != None:
            self.write('SENS:VOLT:PROT {}'.format(voltage))
            if voltage == 'MAX':
                self.voltage_limit = 10.
            else:
                self.voltage_limit = voltage
        if current != None:
            self.write('SENS:CURR:PROT {}'.format(current))
            if current == 'MAX':
                self.current_limit = 1.
            else:
                self.current_limit = current

    def set_output(self, voltage = None, current = None):
        """
        Only one output accepted (voltage will override current if both present).
        This functions helps switching modes.
        """
        if voltage != None:
            if self.get_mode('source') != 'VOLT':
                self.set_mode('VOLT')
            # self compliance
            if voltage <= self.voltage_limit:
                self.write('SOUR:VOLT {:f}'.format(voltage))
            else:
                print('Warning: Compliance Reached!!')
                self.write('SOUR:VOLT {:f}'.format(self.voltage_limit))

        elif current != None:
            if self.get_mode('source') != 'CURR':
                self.set_mode('CURR')
            # self compliance
            if current <= self.current_limit:
                self.write('SOUR:CURR {:f}'.format(current))
            else:
                print('Warning: Compliance Reached!!')
                self.write('SOUR:CURR {:f}'.format(self.current_limit))

    def read_values(self, area, pv):
        data = list(map(float, self.ask(':READ?').split(',')))
        if pv == True:
            data = [-1*i/float(area) for i in data]
        else:
            pass
        return data

    def on(self):
        "Turn Keithley on"
        self.write('OUTP ON')
    def off(self):
        "Turn Keithley off"
        self.write('OUTP OFF')


### This is only for testing - to be removed ###
if __name__ == '__main__':
    import time
    # test
    sc = Keithley2400('GPIB0::24::INSTR')
    sc.set_limit(voltage=10, current=0.12)
    sc.on()

    #sc.sweep(np.arange(0, 5, 0.1))

    #while sc.busy:
    #    time.sleep(0.5)
    #print(sc.read_buffer()[-1])
    print("Voltage:",sc.read_values(1,True)[0]," Current:",sc.read_values(1,True)[1])
    pass




