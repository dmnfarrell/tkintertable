from setuptools import setup
import sys,os
home=os.path.expanduser('~')

setup(
    name = 'tkintertable',
    version = '1.0.3',
    description = 'Extendable table class for Tkinter',
    url='http://code.google.com/p/tkintertable/',
    license='GPL v3',
    author = 'Damien Farrell',
    author_email = 'farrell.damien[at]gmail.com',
    packages = ['tkintertable'],
    dependency_links = [
          "http://download.sourceforge.net/pmw/Pmw.1.3.tar.gz"],
    entry_points = { 'gui_scripts': [
                     'tablesapp = tkintertable.Tablesapp:main']}
)
