#!/usr/bin/env python
"""
    Import and export classes.
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
try:
    from tkinter import *
    from tkinter.ttk import *
    from tkinter import filedialog, messagebox, simpledialog
except:
    from Tkinter import *
    from ttk import *
    import tkFileDialog as filedialog
    import tkSimpleDialog as simpledialog
    import tkMessageBox as messagebox

import os, csv

class TableImporter:
    """Provides import utility methods for the Table and Table Model classes"""

    def __init__(self):
        """Setup globals"""
        #self.separator = ','
        self.separator_list = [',',' ','\t',':']
        self.var_sep = StringVar()
        self.var_sep.set(',')
        return

    def import_Dialog(self, parent):
        """Allows user to set some import options"""

        self.parent=parent
        self.master=Toplevel()
        self.master.title("Import Data")
        self.xsize = 450
        self.ysize = 370
        top=self.master.winfo_toplevel()
        self.master.geometry('400x400+200+200')

        self.sep_choice = Combobox(self.master,
                            text = 'Record separator:',
                            textvariable = self.var_sep,
                            values = self.separator_list,
                            width = 4)
        self.var_sep.trace('w', self.update_display)
        Label(self.master,text='separator:').grid(row=0,column=0,sticky='nw',padx=2,pady=2)
        self.sep_choice.grid(row=0,column=1,sticky='nw',padx=2,pady=2)
        #place for text preview frame
        self.textframe = Frame(self.master)
        self.textframe.grid(row=1,column=0,columnspan=5,sticky='news',padx=2,pady=2)
        self.previewarea = Text(self.textframe, bg='white', width=400, height=500)
        self.previewarea.pack(fill=BOTH, expand=1)
        #buttons
        self.openButton = Button(self.master, text = 'Open File',
                command = self.do_openFile )
        self.openButton.grid(row=3,column=0,sticky='news',padx=2,pady=2)
        self.importButton = Button(self.master, text = 'Do Import',
                command = self.do_ModelImport )
        self.importButton.grid(row=3,column=1,sticky='news',padx=2,pady=2)
        self.CancelButton = Button(self.master, text = 'Cancel',
                command = self.close )
        self.CancelButton.grid(row=3,column=2,sticky='news',padx=2,pady=2)
        self.master.columnconfigure(0,weight=1)
        self.master.rowconfigure(1,weight=1)
        return self.master

    def do_openFile(self):

        self.datafile = self.open_File(self.parent)
        self.update_display()
        return

    def open_File(self, parent):

        savedir = os.getcwd()
        filename=filedialog.askopenfile(defaultextension='.csv',
                                                initialdir=savedir,
                                                initialfile='',
                                                filetypes=[("Data file","*.csv"),
                                                           ("All files","*.*")],
                                                title='Choose data from a .csv file saved as excel spreadsheet in .csv format (comma separated list)',
                                                parent=parent)
        if filename and os.path.exists(filename.name) and os.path.isfile(filename.name):
            datafile = filename.name
        return datafile

    def update_display(self, *args):
        """Preview loaded file"""

        sep = self.var_sep.get()
        self.previewarea.delete(1.0, END)
        reader = csv.reader(open(self.datafile, "r"), delimiter=sep)
        for row in reader:
            self.previewarea.insert(END,row)
            self.previewarea.insert(END,'\n')
        return

    def do_ModelImport(self):
        """imports and places the result in self.modeldata"""

        self.data = self.ImportTableModel(self.datafile)
        self.close()
        return

    def ImportTableModel(self, filename):
        """Import table data from a comma separated file and create data for a model."""

        if not os.path.isfile(filename):
            return None
        try:
            sep = self.var_sep.get()
        except:
            sep = ','
        #takes first row as field names
        dictreader = csv.DictReader(open(filename, "r"), delimiter=sep)
        dictdata = {}
        count=0
        for rec in dictreader:
            dictdata[count]=rec
            count=count+1
        return dictdata

    def close(self):
        self.master.destroy()
        return

class TableExporter:
    def __init__(self):
        """Provides export utility methods for the Table and Table Model classes"""

        return

    def ExportTableData(self, table, sep=None):
        """Export table data to a comma separated file"""

        parent=table.parentframe
        filename = filedialog.asksaveasfilename(parent=parent,defaultextension='.csv',
                                                  filetypes=[("CSV files","*.csv")] )
        if not filename:
            return
        if sep == None:
            sep = ','
        writer = csv.writer(open(filename, "w"), delimiter=sep)
        model=table.getModel()
        recs = model.getAllCells()
        #take column labels as field names
        colnames = model.columnNames
        collabels = model.columnlabels
        row=[]
        for c in colnames:
            row.append(collabels[c])
        writer.writerow(row)
        for row in recs.keys():
            writer.writerow(recs[row])
        return
