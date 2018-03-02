from setuptools import setup, find_packages

setup(
    name='SpecAnalyzer',
    packages=find_packages(),
    install_requires=['numpy', 'matplotlib', 'pillow', 'PyQt5', 'ThorlabsPM100', 'pyvisa', 'opencv-python', 'pandas'],
    entry_points={'gui_scripts' : ['specanalyzer=SpecAnalyzer.__main__:main']},
    version='0.12.1',
    description='Measurements of Current/Voltage profiles for photovoltaic solar cells',
    long_description= """ Measurements of Current/Voltage profiles for photovoltaic solar cells """,
    author='Nicola Ferralis',
    author_email='ferralis@mit.edu',
    url='https://github.com/feranick/SpecAnalyzer',
    download_url='https://github.com/feranick/SpecAnalyzer/archive/master.zip',
    keywords=['PV', 'devices', 'testing'],
    license='GPLv2',
    platforms='any',
    classifiers=[
     'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
     'Development Status :: 5 - Production/Stable',
     'Programming Language :: Python',
     'Programming Language :: Python :: 3',
     'Programming Language :: Python :: 3.5',
     'Programming Language :: Python :: 3.6',
     'Intended Audience :: Science/Research',
     'Topic :: Scientific/Engineering :: Chemistry',
     'Topic :: Scientific/Engineering :: Physics',
     ],
)
