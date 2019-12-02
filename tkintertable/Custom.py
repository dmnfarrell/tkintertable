#!/usr/bin/env python
"""
    Custom Table sub-class illustrate table functionality.
    Created January 2008
    Copyright (C) Damien Farrell

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 2
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

from __future__ import absolute_import, division, print_function
try:
    from tkinter import *
    from tkinter.ttk import *
    from tkinter import filedialog, messagebox, simpledialog
    from tkinter import font
except:
    from Tkinter import *
    from ttk import *
    import tkFileDialog as filedialog
    import tkSimpleDialog as simpledialog
    import tkMessageBox as messagebox
    import TkFont as font

from .Tables import TableCanvas, ColumnHeader

class MyTable(TableCanvas):
     """Sub-class of Tablecanvas, with some changes in behaviour to make
        a customised table - just an example"""
     def __init__(self, parent=None, model=None):
         TableCanvas.__init__(self, parent, model)
         self.bgcolor = '#FFFAF1'
         self.fgcolor = 'black'
         self.entrybackgr = 'white'

         self.selectedcolor = 'yellow'
         self.rowselectedcolor = '#B0E0E6'
         self.multipleselectioncolor = '#ECD672'

         return
