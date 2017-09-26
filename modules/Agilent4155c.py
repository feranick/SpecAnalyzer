import visa, time
import numpy as np

class Analyzer(object):

    def __init__(self, visa_string):
        self.manager = visa.ResourceManager().open_resource(visa_string)
        #self.manager = visa.ResourceManager('@py').open_resource(visa_string)
        print(self.ask("*IDN?"))
        self.write("*RST")
        
        self.write(":PAGE:CHAN:MODE SWEEP")
        self.write(":PAGE:CHAN:SMU3:DIS")
        self.write(":PAGE:CHAN:SMU4:DIS")
        self.write(":PAGE:CHAN:VSU1:DIS")
        self.write(":PAGE:CHAN:VSU2:DIS")
        self.write(":PAGE:CHAN:VMU1:DIS")
        self.write(":PAGE:CHAN:VMU2:DIS")
        
        self.write(":PAGE:CHAN:SMU1:VNAME 'VD'")
        self.write(":PAGE:CHAN:SMU2:VNAME 'VS'")
        self.write(":PAGE:CHAN:SMU1:INAME 'ID'")
        self.write(":PAGE:CHAN:SMU2:INAME 'IS'")
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


    def on(self):
        #"Turn Keithley on"
        self.write('OUTP ON')
    def off(self):
        #"Turn Keithley off"
        self.write('OUTP OFF')
        
    def sweep(self, start, end, step):
        self.write('OUTP ON')
        self.write(":PAGE:MEAS:VAR1:START %f" % float(start))
        self.write(":PAGE:MEAS:VAR1:STOP %f" % float(end))
        self.write(":PAGE:MEAS:VAR1:STEP %f" % float(step))
        self.write(":PAGE:MEAS:SSTOP COMP")
        self.write(":PAGE:SCON:SING")
        self.write("*WAI")
        self.write(":FORM:DATA ASC")
        self.write('OUTP OFF')
        I_data = self.manager.query_ascii_values(":DATA? 'ID' ")
        V_data = self.manager.query_ascii_values(":DATA? 'VD' ")
        return V_data, I_data

    def single(self,voltage):
        self.sweep(voltage,voltage,0.1)

### This is only for testing - to be removed ###
if __name__ == '__main__':
    # test
    an = Analyzer('GPIB0::17::INSTR')
    #an.set_output(voltage = 1)
    sweep = an.sweep(0,0,0.1)
    print(sweep[0], sweep[1])
    #current = an.get_current(1)
    #print(current)
    #print("Voltage:",an.read_values()[0]," Current:",an.read_values()[1])
    pass
