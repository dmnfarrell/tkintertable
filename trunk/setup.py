from distutils.core import setup
import sys,os
home=os.path.expanduser('~')
pythonpath=os.path.join(home,'python')

setup(
    name = 'tkintertable',
    version = '1.0.0',
    description = 'Extendable table class for Tkinter',
    url='http://code.google.com/p/tkintertable/',
    license='GPL v3',
    author = 'Damien Farrell',    
    author_email = 'farrell.damien[at]gmail.com',
    #package_dir = {'':'../'},
    packages = ['tkintertable'],
    #py_modules = ['tkintertable'],
    requires=['Tkinter'],
)
