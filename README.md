# SpecAnalyzer
SpecAnalyzer connects to sourcemeters (supported keythley 2400) and/or parameter analyzers (supported Agilent 4155c) for collection of current-voltage profiles. It is specifically tailored for testing photovoltaic devices.

## Installation:
The software can be run "offline", meaning without being connected to the hardware, for example to load data, etc. The dependencies needed for running the "online" version (i.e. to be able to control the acquisition hardware) are listed as such below. These are not needed for running the "offline" version. If you are planning to use this software for "offline" use on your computer, do not install the "online" dependencies. The software automatically recognizes the presence (or lack thereof) of the required dependencies for online/offline use.

### Dependencies
SpecAnalyzer is written in [Python 3.x](<http://www.python.org/>) and relies on the following libraries:
- [Python v.3.5/3.6](<http://www.python.org/>)
- [Qt5](<http://qt.io>)
- [PyQt version 5](<http://www.riverbankcomputing.co.uk/>)
- [Numpy >1.5](http://www.numpy.org/)
- [Scipy >0.9](<http://www.scipy.org/>)
- [Matplotlib >0.9](<http://matplotlib.org/>) 
- [OpenCV >3.2](<http://opencv.org/>)
- [Pillow (for .tif, .png, .jpg)](https://python-pillow.github.io/>)
- [PyVisa](<https://pyvisa.readthedocs.io/en/stable/index.html>)
- [ThorlabsPM100-Pypi](<https://pypi.python.org/pypi/ThorlabsPM100>) - [Official ThorlabsPM100](<https://www.thorlabs.com/software_pages/viewsoftwarepage.cfm?code=PM100x>) The drivers for Windows as well as the Python library are needed 

### Installing dependencies on Mac OSX
All required packages can be obtained through [MacPorts](<http://www.macports.org/>). After installing macports, individual libraries are installed with the following:

    sudo port install python3.6 +readline
    sudo port install py36-numpy, py36-scipy, py36-matplotlib, py36-pillow, py36-pandas
    sudo port install opencv
    sudo port install qt5 py3.6-pyqt5
    (optional) sudo port install qt5-qtcreator
        
### Installing dependencies on Ubuntu Linux
    sudo apt-get update; sudo apt-get upgrade
    sudo apt-get install python3 python3-numpy python3-scipy
    sudo apt-get install python3-matplotlib python3-pil python3-pandas
    sudo apt-get install qt5-default python3-pyqt5
    sudo apt-get install qtcreator
    (optional) sudo apt-get install opencv-data
    
### Installing dependencies on Microsoft Windows
The simplest way to get all the required python packages at once is to install the Python 3 distribution from [python.org](<http://www.python.org/>) (recommended) or from [Anaconda](<https://www.continuum.io/downloads/>). You will use ```pip``` for installing most of the dependencies.

    pip install numpy scipy matplotlib pillow pandas
    pip install QtPy5 opencv-python

Install Qt5 from the [qt.io](https://www.qt.io/download/) directly.

### "Online" dependencies for hardware control:
    pip install pyvisa ThorlabsPM100 requests
    
### Creating a wheel package for redistribution
In order to satisfy all dependency and at the same time have a seamless experience, assuming ```python 3```, ```pip``` and ```wheel``` are installed, one can create a wheel package that can be used for seamless installation. To create the wheel package:

    cd /UI
    python3 setup.py bdist_wheel
    
A wheel package is created inside a new folder ```dist```. On UNIX-systems the package can be installed simply as user by:

    pip install --user <package.whl>
    
or system-wide:

    sudo pip install <package.whl>
    
On MS Windows:

    pip install <package.whl>
    
## Run
After downloading the zip-file extract its content to a directory. If you have already installed the dependencies, you are ready to go.

### Linux/Mac OSX
From the terminal, run: ```python specanalyzer```
    
### Windows
Launch by double clicking the file ```specanalyzer-windows.bat```

