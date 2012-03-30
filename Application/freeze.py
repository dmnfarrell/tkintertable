#!/usr/bin/env python

#bbfreeze setup file for tkintertable sample app distribution on Windows
#Damien Farrell, #Mar 2012

"""
This script can be used to create a standalone executable for
either windows or linux. It must be run on the target platform.
You will need to install bbfreeze, see http://pypi.python.org/pypi/bbfreeze/
"""

from bbfreeze import Freezer
import sys, os, shutil

shutil.rmtree('tkintertableapp', ignore_errors=True)
path=os.path.abspath('../')

version = '1.0.0'

f = Freezer('tkintertableapp', excludes=('wx'))
f.addScript(os.path.join(path, "TablesApp.py"))

m=f.mf
f()    # runs the freezing process

#mpl data
import matplotlib
mpldir = matplotlib.get_data_path()
datadir = 'tkintertableapp/mpl-data'
shutil.copytree(mpldir, datadir)

#add resource files             
shutil.copy('logo.ico', 'tkintertableapp')
shutil.copy('../sample.table', 'tkintertableapp')

#make zip archive
import zipfile
f = zipfile.ZipFile("tkintertableapp-"+version+".zip", "w")
for dirpath, dirnames, filenames in os.walk('tkintertableapp'):
    for fname in filenames:
        fullname = os.path.join(dirpath, fname)        
        f.write(fullname)
f.close()

