#
# This file is part Protein Engineering Analysis Tool (PEAT)
# (C) Copyright Jens Erik Nielsen, University College Dublin 2003-
# All rights reserved
#
#
# Written by D Farrell, April 2008
#

from Tkinter import *
import Pmw
import os, csv
import tkFileDialog

class TableImporter:
    """Provides import utility methods for the Table and Table Model classes"""

    def __init__(self):
        """Setup globals"""
        #self.separator = ','
        self.separator_list = {',':',',' ':'space','\t':'tab','blank':' ',':':':'}
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
        rootx=top.winfo_rootx()
        rooty=top.winfo_rooty()

        self.sep_choice = Pmw.OptionMenu(
            parent = self.master,labelpos = 'w',
            label_text = 'Record separator:',
            menubutton_textvariable = self.var_sep,
            items = self.separator_list.keys(),
            initialitem = ',',
            menubutton_width = 4,
            command= self.update_display)

        self.sep_choice.grid(row=0,column=0,sticky='nw',padx=2,pady=2)
        #place for text preview frame

        self.textframe=Pmw.ScrolledFrame(self.master,
                    labelpos = 'n', label_text = 'Preview',
                    usehullsize = 1,
                    hull_width = 450,
                    hull_height = 300)
        self.textframe.grid(row=1,column=0,columnspan=5,sticky='news',padx=2,pady=2)
        self.previewarea = Text(self.textframe.interior(), bg='white', width=400, height=500)
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
        filename=tkFileDialog.askopenfile(defaultextension='.csv',
                                                initialdir=savedir,
                                                initialfile='',
                                                filetypes=[("Data file","*.csv"),
                                                           ("All files","*.*")],
                                                title='Choose data from a .csv file saved as excel spreadsheet in .csv format (comma separated list)',
                                                parent=parent)
        if filename and os.path.exists(filename.name) and os.path.isfile(filename.name):
            datafile = filename.name
        return datafile

    def update_display(self,evt=None):
        """Preview loaded file"""
        sep = self.var_sep.get()
        self.previewarea.delete(1.0, END)
        reader = csv.reader(open(self.datafile, "rb"), delimiter=sep)
        for row in reader:
            self.previewarea.insert(END,row)
            self.previewarea.insert(END,'\n')
        return

    def do_ModelImport(self):
        """imports and places the result in self.modeldata"""
        self.data = self.ImportTableModel(self.datafile)
        self.close()
        return

    def ImportTableModel(self,filename):
        """Import table data from a comma separated file and create data for a model
           This is reusable outside the GUI dialog also."""

        if not os.path.isfile(filename):
            return None
        try:
            sep = self.var_sep.get()
        except:
            sep = ','
        #takes first row as field names
        dictreader = csv.DictReader(open(filename, "rb"), delimiter=sep)
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
        import tkFileDialog
        filename = tkFileDialog.asksaveasfilename(parent=parent,defaultextension='.csv',
                                                  filetypes=[("CSV files","*.csv")]
                                                  )
        if not filename:
            return
        if sep == None:
            sep = ','
        writer = csv.writer(file(filename, "w"), delimiter=sep)
        #writer = csv.writer(sys.stdout, delimiter=sep)
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

