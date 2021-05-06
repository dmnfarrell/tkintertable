#!/usr/bin/env python
"""
    Sample App to illustrate table functionality.
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
import sys, os
try:
    from tkinter import *
    from tkinter.ttk import *
except:
    from Tkinter import *
    from ttk import *
if (sys.version_info > (3, 0)):
    from tkinter import filedialog, messagebox, simpledialog
    from tkinter import font
else:
    import tkFileDialog as filedialog
    import tkSimpleDialog as simpledialog
    import tkMessageBox as messagebox
    import tkFont as font

#import Pmw
import re, os, time, pickle
from collections import OrderedDict
from .Custom import MyTable
from .TableModels import TableModel
from .Tables_IO import TableImporter
from .Prefs import Preferences

class TablesApp(Frame):
    """
    Tables app
    """
    def __init__(self,parent=None,data=None,datafile=None):
        "Initialize the application."
        self.parent=parent

        #If there is data to be loaded, show the dialog first
        if not self.parent:
            Frame.__init__(self)
            self.tablesapp_win=self.master

        else:
            self.tablesapp_win=Toplevel()

        # Get platform into a variable
        import platform
        self.currplatform=platform.system()
        if not hasattr(self,'defaultsavedir'):
            self.defaultsavedir = os.getcwd()

        self.preferences=Preferences('TablesApp',{'check_for_update':1})
        self.loadprefs()
        self.tablesapp_win.title('Tables Application')
        self.tablesapp_win.geometry('+200+200')
        self.x_size=800
        self.y_size=600
        self.createMenuBar()
        self.apptoolBar = ToolBar(self.tablesapp_win, self)
        self.apptoolBar.pack(fill=BOTH, expand=NO)
        #add find bar
        #self.createSearchBar()

        if data != None:
            self.data = data
            self.new_project(data)
        elif datafile != None:
            self.open_project(datafile)
        else:
            self.new_project()

        self.tablesapp_win.protocol('WM_DELETE_WINDOW',self.quit)
        return

    def createMenuBar(self):
        """Create the menu bar for the application. """

        self.menu=Menu(self.tablesapp_win)
        self.proj_menu={'01New':{'cmd':self.new_project},
                        '02Open':{'cmd':self.open_project},
                        '03Close':{'cmd':self.close_project},
                        '04Save':{'cmd':self.save_project},
                        '05Save As':{'cmd':self.save_as_project},
                        '06Preferences..':{'cmd':self.showPrefsDialog},
                        '08Quit':{'cmd':self.quit}}
        if self.parent:
            self.proj_menu['08Return to Database']={'cmd':self.return_data}
        self.proj_menu=self.create_pulldown(self.menu,self.proj_menu)
        self.menu.add_cascade(label='Project',menu=self.proj_menu['var'])

        self.records_menu={'01Add Row':{'cmd':self.add_Row},
                         '02Delete Row':{'cmd':self.delete_Row},
                         '03Add Column':{'cmd':self.add_Column},
                         '04Delete Column':{'cmd':self.delete_Column},
                         '05Auto Add Rows':{'cmd':self.autoAdd_Rows},
                         '06Auto Add Columns':{'cmd':self.autoAdd_Columns},
                         '07Find':{'cmd':self.createSearchBar},
                         }
        self.records_menu=self.create_pulldown(self.menu,self.records_menu)
        self.menu.add_cascade(label='Records',menu=self.records_menu['var'])

        self.sheet_menu={'01Add Sheet':{'cmd':self.add_Sheet},
                         '02Remove Sheet':{'cmd':self.delete_Sheet},
                         '03Copy Sheet':{'cmd':self.copy_Sheet},
                         '04Rename Sheet':{'cmd':self.rename_Sheet},
                         }
        self.sheet_menu=self.create_pulldown(self.menu,self.sheet_menu)
        self.menu.add_cascade(label='Sheet',menu=self.sheet_menu['var'])

        self.IO_menu={'01Import from csv file':{'cmd':self.import_csv},
                      '02Export to csv file':{'cmd':self.export_csv},
                      }

        self.IO_menu=self.create_pulldown(self.menu,self.IO_menu)
        self.menu.add_cascade(label='Import/Export',menu=self.IO_menu['var'])

        # Help menu
        self.help_menu={'01Online Help':{'cmd':self.online_documentation},
                        '02About':{'cmd':self.about_Tables}}
        self.help_menu=self.create_pulldown(self.menu,self.help_menu)
        self.menu.add_cascade(label='Help',menu=self.help_menu['var'])

        self.tablesapp_win.config(menu=self.menu)

        return

    def create_pulldown(self,menu,dict):
        """ Create a pulldown in var from the info in dict  """

        var = Menu(menu,tearoff=0)
        items = dict.keys()
        #items.sort()
        for item in items:
            if item[-3:]=='sep':
                var.add_separator()
            else:
                # Do we have a command?
                command=None
                if 'cmd' in  dict[item]:
                    command=dict[item]['cmd']

                # Put the command in there
                if 'sc' in dict[item]:
                    var.add_command(label='%-25s %9s' %(item[2:],dict[item]['sc']),command=command)
                else:
                    var.add_command(label='%-25s' %(item[2:]),command=command)
        dict['var']=var
        return dict

    def createSearchBar(self, event=None):
        """Add a find entry box"""

        frame = Frame(self.tablesapp_win)
        row=0
        def close():
            frame.destroy()
        self.findtext=StringVar()
        self.findbox=Entry(frame,textvariable=self.findtext,width=30,bg='white')
        self.findbox.grid(row=row,column=1,sticky='news',columnspan=2,padx=2,pady=2)
        self.findbox.bind('<Return>',self.do_find_text)
        Label(frame,text='Find:').grid(row=row,column=0,sticky='ew')
        self.findagainbutton=Button(frame,text='Find Again', command=self.do_find_again)
        self.findagainbutton.grid(row=row,column=3,sticky='news',padx=2,pady=2)
        self.cbutton=Button(frame,text='Close', command=close)
        self.cbutton.grid(row=row,column=4,sticky='news',padx=2,pady=2)
        frame.pack(fill=BOTH, expand=NO)
        return

    def loadprefs(self):
        """Setup default prefs file if any of the keys are not present"""

        defaultprefs = {'textsize':14,
                         'windowwidth': 800 ,'windowheight':600}
        for prop in defaultprefs.keys():
            try:
                self.preferences.get(prop)
            except:
                self.preferences.set(prop, defaultprefs[prop])

        return

    def showPrefsDialog(self):
        self.prefswindow = self.currenttable.showtablePrefs()
        return

    def new_project(self, data=None):
        """Create a new table, with model and add the frame"""

        if hasattr(self,'currenttable'):
            self.notebook.destroy()
            self.currenttable.destroy()

        #Create the sheets dict
        self.sheets = {}
        self.notebook = Notebook(self.tablesapp_win)
        self.notebook.pack(fill='both', expand=1, padx=4, pady=4)
        if data !=None:
            for s in data.keys():
                sdata = data[s]
                try:
                    self.add_Sheet(s ,sdata)
                except:
                    print ('skipping')
        else:
            #do the table adding stuff for the initial sheet
            self.add_Sheet('sheet1')
        #self.notebook.setnaturalsize()
        return

    def open_project(self, filename=None):

        if filename == None:
            filename=filedialog.askopenfilename(defaultextension='.tblprj"',
                                                      initialdir=os.getcwd(),
                                                      filetypes=[("TableApp project","*.tblprj"),
                                                                 ("All files","*.*")],
                                                      parent=self.tablesapp_win)
        if os.path.isfile(filename):
            fd = open(filename, 'rb')
            data = pickle.load(fd)
            fd.close()
        self.new_project(data)
        self.filename=filename
        return

    def save_project(self):

        if not hasattr(self, 'filename'):
            self.save_as_project()
        elif self.filename == None:
            self.save_as_project()
        else:
            self.do_save_project(self.filename)

        return

    def save_as_project(self):
        """Save as a new filename"""

        filename=filedialog.asksaveasfilename(parent=self.tablesapp_win,
                                                defaultextension='.tblprj',
                                                initialdir=self.defaultsavedir,
                                                filetypes=[("TableApp project","*.tblprj"),
                                                           ("All files","*.*")])
        if not filename:
            print ('Returning')
            return
        self.filename=filename
        self.do_save_project(self.filename)
        return

    def do_save_project(self, filename):
        """Get model dicts and write all to pickle file"""

        data={}
        for s in self.sheets.keys():
            currtable = self.sheets[s]
            model = currtable.getModel()
            data[s] = model.getData()

        fd=open(filename,'wb')
        pickle.dump(data,fd)
        fd.close()
        return

    def close_project(self):
        if hasattr(self,'currenttable'):
            #self.notebook.destroy()
            self.currenttable.destroy()
        return

    def import_csv(self):

        importer = TableImporter()
        #just use the dialog to load and import the file
        importdialog = importer.import_Dialog(self.tablesapp_win)
        self.tablesapp_win.wait_window(importdialog)
        model = TableModel()
        model.importDict(importer.data)
        sheetdata = {}
        sheetdata['sheet1'] = model.getData()
        self.new_project(sheetdata)
        return

    def export_csv(self):
        from .Tables_IO import TableExporter
        exporter = TableExporter()
        exporter.ExportTableData(self.currenttable)
        return

    def add_Sheet(self, sheetname=None, sheetdata=None):
        """Add a new sheet - handles all the table creation stuff"""

        def checksheet_name(name):
            if name == '':
                messagebox.showwarning("Whoops", "Name should not be blank.")
                return 0
            if name in self.sheets:
                messagebox.showwarning("Name exists", "Sheet name already exists!")
                return 0
        names = [self.notebook.tab(i, "text") for i in self.notebook.tabs()]
        noshts = len(names)
        if sheetname == None:
            sheetname = simpledialog.askstring("New sheet name?", "Enter sheet name:",
                                                initialvalue='sheet'+str(noshts+1))
        checksheet_name(sheetname)
        page = Frame(self.notebook)
        self.notebook.add(page, text=sheetname)
        #Create the table and model if data present
        if sheetdata != None:
            model = TableModel(sheetdata)
            self.currenttable = MyTable(page, model)
        else:
            self.currenttable = MyTable(page)

        #Load preferences into table
        self.currenttable.loadPrefs(self.preferences)
        #This handles all the canvas and header in the frame passed to constructor
        self.currenttable.createTableFrame()
        #add the table to the sheet dict
        self.sheets[sheetname] = self.currenttable
        self.saved = 0
        return sheetname

    def delete_Sheet(self):
        """Delete a sheet"""

        s = self.notebook.index(self.notebook.select())
        name = self.notebook.tab(s, 'text')
        #self.notebook.delete(s)
        self.notebook.forget(s)
        del self.sheets[s]
        return

    def copy_Sheet(self, newname=None):
        """Copy a sheet"""

        newdata = self.currenttable.getModel().getData().copy()
        if newname==None:
            self.add_Sheet(None, newdata)
        else:
            self.add_Sheet(newname, newdata)
        return

    def rename_Sheet(self):
        """Rename a sheet"""

        #s = self.notebook.getcurselection()
        s = self.notebook.index(self.notebook.select())
        newname = simpledialog.askstring("New sheet name?", "Enter new sheet name:",
                                                initialvalue=s)
        if newname == None:
            return
        self.copy_Sheet(newname)
        self.delete_Sheet()
        return

    def setcurrenttable(self, event):
        """Set the currenttable so that menu items work with visible sheet"""

        try:
            #s = self.notebook.getcurselection()
            s = self.notebook.index(self.notebook.select())
            self.currenttable = self.sheets[s]
        except:
            pass
        return

    def add_Row(self):
        """Add a new row"""
        self.currenttable.addRow()
        self.saved = 0
        return

    def delete_Row(self):
        """Delete currently selected row"""

        self.currenttable.deleteRow()
        self.saved = 0
        return

    def add_Column(self):
        """Add a new column"""

        self.currenttable.addColumn()
        self.saved = 0
        return

    def delete_Column(self):
        """Delete currently selected column in table"""

        self.currenttable.deleteColumn()
        self.saved = 0
        return

    def autoAdd_Rows(self):
        """Auto add x rows"""

        self.currenttable.autoAddRows()
        self.saved = 0
        return

    def autoAdd_Columns(self):
        """Auto add x rows"""

        self.currenttable.autoAddColumns()
        self.saved = 0
        return

    def findValue(self):
        self.currenttable.findValue()
        return

    def do_find_text(self, event=None):
        """Find the text in the table"""

        if not hasattr(self,'currenttable'):
            return
        import string
        if string.strip(self.findtext.get())=='':
            return
        searchstring=self.findtext.get()
        if self.currenttable!=None:
            self.currenttable.findValue(searchstring)
        return

    def do_find_again(self, event=None):
        """Find again"""

        if not hasattr(self,'currenttable'):
            return
        searchstring=self.findtext.get()
        if self.currenttable!=None:
            self.currenttable.findValue(searchstring, findagain=1)
        return

    def plot(self, event=None):
        self.currenttable.plotSelected()
        return

    def plotSetup(self, event=None):
        self.currenttable.plotSetup()
        return

    def about_Tables(self):

        self.ab_win=Toplevel()
        self.ab_win.geometry('+100+350')
        self.ab_win.title('About TablesApp')
        from . import __version__
        from . import Table_images
        logo = Table_images.tableapp_logo()
        label = Label(self.ab_win,image=logo)
        label.image = logo
        label.grid(row=0,column=0,sticky='news',padx=4,pady=4)

        text=['Tables Sample App ','Shows the use of Tablecanvas class for tkinter',
                'Copyright (C) Damien Farrell 2008-', 'This program is free software; you can redistribute it and/or',
                'modify it under the terms of the GNU General Public License',
                'as published by the Free Software Foundation; either version 2',
                'of the License, or (at your option) any later version.',
                'tkintertable version %s' %__version__]
        row=1
        for line in text:
            tmp=Label(self.ab_win,text=line)
            tmp.grid(row=row,column=0,sticky='news',padx=4)
            row=row+1
        return

    def online_documentation(self,event=None):
        """Open the online documentation"""

        import webbrowser
        link='https://github.com/dmnfarrell/tkintertable/wiki'
        webbrowser.open(link,autoraise=1)
        return

    def quit(self):
        self.tablesapp_win.destroy()

        return

class ToolBar(Frame):
    """Uses the parent instance to provide the functions"""

    def __init__(self, parent=None, parentapp=None):
        Frame.__init__(self, parent, width=600, height=40)
        from . import Table_images
        self.parentframe = parent
        self.parentapp = parentapp
        #add buttons
        img = Table_images.new_proj()
        self.add_button('New Project', self.parentapp.new_project, img)
        img = Table_images.open_proj()
        self.add_button('Open Project', self.parentapp.open_project, img)
        img = Table_images.save_proj()
        self.add_button('Save Project', self.parentapp.save_project, img)
        img = Table_images.add_row()
        self.add_button('Add record', self.parentapp.add_Row, img)
        img = Table_images.add_col()
        self.add_button('Add col', self.parentapp.add_Column, img)
        img = Table_images.del_row()
        self.add_button('Delete record', self.parentapp.delete_Row, img)
        img = Table_images.del_col()
        self.add_button('Delete col', self.parentapp.delete_Column, img)
        img = Table_images.plot()
        self.add_button('Plot', self.parentapp.plot, img)
        img = Table_images.plotprefs()
        self.add_button('Plot Prefs', self.parentapp.plotSetup, img)

        return

    def add_button(self, name, callback, img=None):
        if img==None:
            b = Button(self, text=name, command=callback)
        else:
            b = Button(self, text=name, command=callback,
                             image=img)
        b.image = img
        b.pack(side=LEFT, padx=2, pady=2, ipadx=1, ipady=1)

        return

# Main function, run when invoked as a stand-alone Python program.

def main():
    "Run the application"
   
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="tablefile",
                        help="Open a table file", metavar="FILE")
    opts, remainder = parser.parse_args()
    if opts.tablefile != None:
        app=TablesApp(datafile=opts.tablefile)
    else:
        app=TablesApp()
    app.mainloop()
    return

if __name__ == '__main__':
    main()
