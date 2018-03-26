'''
initialization.py
-----------------

Copyright (C) 2017-2018 Nicola Ferralis <ferralis@mit.edu>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

'''

__version__ = "0.18.0"
__author__ = "<qt><a href = mailto:ferralis@mit.edu> Nicola Ferralis</a></qt>"

from .configuration import *
import os.path

config = Configuration()
if os.path.isfile(config.configFile) is False:
    print("Configuration file does not exist: Creating one.")
    config.createConfig()
config.readConfig(config.configFile)

import logging
logging.basicConfig(filename=config.loggingFilename, level=int(config.loggingLevel))
logger = logging.getLogger()

from . import configuration
from . import mainWindow



