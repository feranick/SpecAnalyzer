from setuptools import setup, find_packages

setup(
    name='SpecAnalyzer',
    packages=find_packages(),
    install_requires=['numpy', 'matplotlib', 'pillow', 'PyQt5', 'pyvisa', 'opencv-python', 'pandas',
        'ThorlabsPM100;platform_system=="Windows"',],
    entry_points={'gui_scripts' : ['specanalyzer=SpecAnalyzer.__main__:main']},
    version='0.15.0',
    description='Automated measurements of Current/Voltage profiles for photovoltaic solar cells',
    long_description= """ Control software for automated measurements of Current/Voltage profiles, device tracking for photovoltaic solar cells """,
    author_email='ferralis@mit.edu',
    url='https://github.com/feranick/SpecAnalyzer',
    download_url='https://github.com/feranick/SpecAnalyzer/archive/master.zip',
    keywords=['Photovoltaics', 'devices', 'JV', 'tracking', 'testing'],
    license='GPLv3',
    platforms='any',
    classifiers=[
     'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
     'Development Status :: 4 - Beta',
     'Programming Language :: Python :: Only',
     'Programming Language :: Python :: 3',
     'Programming Language :: Python :: 3.5',
     'Programming Language :: Python :: 3.6',
     'Intended Audience :: Science/Research',
     'Topic :: Scientific/Engineering :: Chemistry',
     'Topic :: Scientific/Engineering :: Physics',
     ],
)
