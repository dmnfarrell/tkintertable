#!/usr/bin/env python
"""
    Table Dialog classes.
    Created Oct 2008
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
import sys
try:
    from tkinter import *
    from tkinter.ttk import *
except:
    from Tkinter import *
    from ttk import *
if (sys.version_info > (3, 0)):
    from tkinter import filedialog, messagebox, simpledialog
    from tkinter.simpledialog import Dialog
    from tkinter import font
else:
    import tkFileDialog as filedialog
    import tkSimpleDialog as simpledialog
    import tkMessageBox as messagebox
    from tkSimpleDialog import Dialog
    import tkFont as font

class RecordViewDialog(Dialog):
    """Dialog for viewing and editing table records"""

    def __init__(self, parent, title=None, table=None, row=None):
        if table != None:
            self.table = table
            self.model = table.getModel()
            self.row = row
            self.recdata = self.model.getRecordAtRow(row)
            self.recname = self.model.getRecName(row)
        else:
            return
        simpledialog.Dialog.__init__(self, parent, title)
        return

    def body(self, master):
        """Show all record fields in entry fields or labels"""

        model = self.model
        cols = self.recdata.keys()
        self.editable = []
        self.fieldnames = {}
        self.fieldvars = {}
        self.fieldvars['Name'] = StringVar()
        self.fieldvars['Name'].set(self.recname)
        Label(master, text='Rec Name:').grid(row=0,column=0,padx=2,pady=2,sticky='news')
        Entry(master, textvariable=self.fieldvars['Name']).grid(row=0,column=1,padx=2,pady=2,sticky='news')
        i=1
        for col in cols:
            self.fieldvars[col] = StringVar()
            if col in self.recdata:
                val = self.recdata[col]
                self.fieldvars[col].set(val)
            self.fieldnames[col] = Label(master, text=col).grid(row=i,column=0,padx=2,pady=2,sticky='news')
            ent = Entry(master, textvariable=self.fieldvars[col])
            ent.grid(row=i,column=1,padx=2,pady=2,sticky='news')
            if not type(self.recdata[col]) is str:
                ent.config(state=DISABLED)
            else:
                self.editable.append(col)
            i+=1
        top=self.winfo_toplevel()
        top.columnconfigure(1,weight=1)
        return

    def apply(self):
        """apply"""
        cols = self.table.cols
        model = self.model
        absrow = self.table.get_AbsoluteRow(self.row)
        newname = self.fieldvars['Name'].get()
        if newname != self.recname:
            model.setRecName(newname, absrow)

        for col in range(cols):
            colname = model.getColumnName(col)
            if not colname in self.editable:
                continue
            if not colname in self.fieldvars:
                continue
            val = self.fieldvars[colname].get()
            model.setValueAt(val, absrow, col)
            #print 'changed field', colname

        self.table.redrawTable()
        return

class MultipleValDialog(simpledialog.Dialog):
    """Simple dialog to get multiple values"""

    def __init__(self, parent, title=None, initialvalues=None, labels=None, types=None):
        if labels != None:
            self.initialvalues = initialvalues
            self.labels = labels
            self.types = types
        simpledialog.Dialog.__init__(self, parent, title)

    def body(self, master):

        r=0
        self.vrs=[];self.entries=[]
        for i in range(len(self.labels)):
            Label(master, text=self.labels[i]).grid(row=r, column=0,sticky='news')
            if self.types[i] == 'int':
                self.vrs.append(IntVar())
            else:
                self.vrs.append(StringVar())
            if self.types[i] == 'password':
                s='*'
            else:
                s=None

            if self.types[i] == 'list':
                button=Menubutton(master, textvariable=self.vrs[i])
                menu=Menu(button,tearoff=0)
                button['menu']=menu
                choices=self.initialvalues[i]
                for c in choices:
                    menu.add_radiobutton(label=c,
                                        variable=self.vrs[i],
                                        value=c,
                                        indicatoron=1)
                self.entries.append(button)
                self.vrs[i].set(self.initialvalues[i][0])
            else:
                self.vrs[i].set(self.initialvalues[i])
                self.entries.append(Entry(master, textvariable=self.vrs[i], show=s))
            self.entries[i].grid(row=r, column=1,padx=2,pady=2,sticky='news')
            r+=1

        return self.entries[0] # initial focus

    def apply(self):
        self.result = True
        self.results = []
        for i in range(len(self.labels)):
            self.results.append(self.vrs[i].get())
        return
