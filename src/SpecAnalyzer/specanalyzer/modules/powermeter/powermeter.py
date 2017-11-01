'''
powermeter.py
-------------
Class for providing a hardware support for 
for the powermeter Thorlabs PM100

Copyright (C) 2017 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

import time
#from specanalyzer import configuration
try:
    from ThorlabsPM100 import ThorlabsPM100
    import visa
except ImportError:
    pass

class PowerMeter():
    # Define connection to powermeter
    def __init__(self, powermeterID):
        self.powermeterID = powermeterID
        try:
            self.rm = visa.ResourceManager()
            self.PM100Init = True
        except:
            self.PM100Init = False
        time.sleep(1)
    
    # Get power reading from powermeter
    def get_power(self):
        inst = self.rm.open_resource(self.powermeterID, timeout=1)
        power_meter = ThorlabsPM100(inst=inst)
        return power_meter.read

    # Performs zero adjustment routine
    def zero(self):
        inst = self.rm.open_resource(self.powermeterID, timeout=1)
        power_meter = ThorlabsPM100(inst=inst)
        power_meter.sense.correction.collect.zero.initiate()
        time.sleep(1)

    
