simport visa, time
import numpy as np

class Analyzer(object):

    def __init(self, visa_string):
        self.manager = visa.ResourceManager().open_resource(visa_string)
        #self.manager = visa.ResourceManager('@py').open_resource(visa_string)
        print(self.ask("*IDN?"))
        self.ask.("*RST")
        self.write(":PAGE:CHAN:MODE SAMP")
        self.write(":PAGE:CHAN:SMU3:DIS")
        self.write(":PAGE:CHAN:SMU4:DIS")
        self.write(":PAGE:CHAN:VSU1:DIS")
        self.write(":PAGE:CHAN:VSU2:DIS")
        self.write(":PAGE:CHAN:VMU1:DIS")
        self.write(":PAGE:CHAN:VMU2:DIS")
        self.write(":PAGE:CHAN:SMU1:VNAME ‘VD’")
        self.write(":PAGE:CHAN:SMU2:VNAME ‘VS’")
        self.write(":PAGE:CHAN:SMU1:INAME ‘ID’")
        self.write(":PAGE:CHAN:SMU2:INAME ‘IS’")
        self.write(":PAGE:CHAN:SMU1:MODE V")
        self.write(":PAGE:CHAN:SMU1:FUNC VAR1")
        self.write(":PAGE:CHAN:SMU2:MODE COMM")
        self.write(":PAGE:CHAN:SMU2:FUNC CONS")

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
    
        
    def set_output(self, voltage=None, current=None):

        self.write(":PAGE:MEAS:SAMP:SMU1 %f" % float(voltage))
        #self.write(":PAGE:MEAS:VAR1:STOP %f" % float(stop1))
        #self.write(":PAGE:MEAS:VAR1:STEP %f" % float(step1))
        #self.write(":PAGE:MEAS:VAR1:COMP %f" % float(comp1))

        #self.write(":PAGE:MEAS:VAR1:POINTS %f" % float(point1))
        instr.write(":FORM:DATA ASC")
        
    def read_values(self):
        I_data = instr.query_ascii_values(":DATA? ‘ID’ ")
        V_data = instr.query_ascii_values(":DATA? ‘VD’ ")
        return list(V_data, I_data)

    '''
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
                self.voltage_limit = 210.
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

    def read_values(self):
        return list(map(float, self.ask(':READ?').split(',')))

    def on(self):
        "Turn Keithley on"
        self.write('OUTP ON')
    def off(self):
        "Turn Keithley off"
        self.write('OUTP OFF')

    '''


'''
inst

inst.write(':ROUT: REAR')
print(inst.query(':ROUT?'))
inst.write(':SENS:FUNC:CONC OFF')
inst.write(':SOUR:FUNC CURR')
inst.write(':SENS:FUNC VOLT:DC')
inst.write(':SENS:VOLT:PROT 10')
inst.write(':SOUR:CURR:START 1E-3')
inst.write(':SOUR:CURR:STOP 10E-3')
inst.write(':SOUR:CURR:STEP 1E-3')
inst.write(':SOUR:CURR:MODE SWE')
inst.write(':SOUR:SWE:RANG AUTO')
inst.write(':SOUR:SWE:SPAC LIN')
inst.write(':TRIG:COUN 10')
inst.write(':SOUR:DEL 0.1')
inst.write(':OUTP ON')
values = np.array(inst.query_ascii_values(':READ?'))
inst.write(':OUTP OFF')
'''

### This is only for testing - to be removed ###
if __name__ == '__main__':
    # test
    an = analyzer('GPIB0::17::INSTR')
    an.set_output(voltage = 1)
    print("Voltage:",an.read_values()[0]," Current:",an.read_values()[1])
    pass
