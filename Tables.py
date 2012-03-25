#!/usr/bin/env python
#
# Protein Engineering Analysis Tool DataBase (PEATDB)
# Copyright (C) 2010 Damien Farrell & Jens Erik Nielsen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact information:
# Email: Jens.Nielsen_at_gmail.com 
# Normal mail:
# Jens Nielsen
# SBBS, Conway Institute
# University College Dublin
# Dublin 4, Ireland
#

from Tkinter import *
from TableModels import TableModel
from TableFormula import Formula
from Prefs import Preferences
import tkFileDialog, tkMessageBox, tkSimpleDialog
import tkFont
import math
from types import *

class TableCanvas(Canvas):
    """A tkinter class for providing table functionality"""

    def __init__(self, parent=None, model=None, newdict=None, width=None, height=None, **kwargs):
        Canvas.__init__(self, parent, bg='white',
                         width=width, height=height,
                         relief=GROOVE,
                         scrollregion=(0,0,300,200))
        self.parentframe = parent
        #get platform into a variable
        self.ostyp = self.checkOSType()
        import platform
        self.platform=platform.system()
        self.width=width
        self.height=height

        self.set_defaults()
        self.currentpage = None
        self.navFrame = None
        self.currentrow = 0
        self.currentcol = 0
        self.reverseorder = 0
        #for multiple selections
        self.startrow = self.endrow = None
        self.startcol = self.endcol = None
        self.allrows = False   #for selected all rows without setting multiplerowlist
        self.multiplerowlist=[]
        self.multiplecollist=[]
        self.col_positions=[]       #record current column grid positions
        self.mode = 'normal'
        self.editable = True
        self.filtered = False

        self.loadPrefs()        
        #set any options passed in kwargs to overwrite defaults/prefs
        for key in kwargs:
            self.__dict__[key] = kwargs[key]

        if model == None:
            self.model = TableModel(rows=10,columns=5)
        else:
            self.model = model
        if newdict != None:
            self.createfromDict(newdict)

        self.rows=self.model.getRowCount()
        self.cols=self.model.getColumnCount()
        self.tablewidth=(self.cellwidth)*self.cols
        self.tablecolheader = ColumnHeader(self.parentframe, self)
        self.tablerowheader = RowHeader(self.parentframe, self)
        self.do_bindings()

        #column specific actions, define for every column type in the model
        #when you add a column type you should edit this dict
        self.columnactions = {'text' : {"Edit":  'draw_cellentry' },
                              'number' : {"Edit": 'draw_cellentry' }}
        #self.savePrefs()    
        return

    def set_defaults(self):
        self.cellwidth=150
        self.maxcellwidth=400
        self.rowheight=20
        self.horizlines=1
        self.vertlines=1
        self.alternaterows=0
        self.autoresizecols = 0
        self.paging = 0
        self.rowsperpage = 50
        self.inset=2
        self.x_start=0
        self.y_start=1
        self.linewidth=1.0
        self.thefont = "Arial 11"
        self.cellbackgr = '#F7F7FA'
        self.entrybackgr = 'white'
        self.grid_color = '#ABB1AD'
        self.selectedcolor = 'yellow'
        self.rowselectedcolor = '#CCCCFF'
        self.multipleselectioncolor = '#ECD672'
        return

    def mouse_wheel(self, event):
        """Handle mouse wheel scroll for windows"""
        if event.num == 5 or event.delta == -120:
            event.widget.yview_scroll(1, UNITS)
            self.tablerowheader.yview_scroll(1, UNITS)
        if event.num == 4 or event.delta == 120:
            event.widget.yview_scroll(-1, UNITS)
            self.tablerowheader.yview_scroll(-1, UNITS)
        return

    def do_bindings(self):
        """Bind keys and mouse clicks, this can be overriden"""
        self.bind("<Button-1>",self.handle_left_click)
        self.bind("<Double-Button-1>",self.handle_double_click)
        self.bind("<Control-Button-1>", self.handle_left_ctrl_click)
        self.bind("<Shift-Button-1>", self.handle_left_shift_click)

        self.bind("<ButtonRelease-1>", self.handle_left_release)
        if self.ostyp=='mac':
            #For mac we bind Shift, left-click to right click
            self.bind("<Button-2>", self.handle_right_click)
            self.bind('<Shift-Button-1>',self.handle_right_click)
        else:
            self.bind("<Button-3>", self.handle_right_click)

        self.bind('<B1-Motion>', self.handle_mouse_drag)
        self.bind('<Motion>', self.handle_motion)

        self.bind_all("<Control-x>", self.delete_Row)
        self.bind_all("<Control-n>", self.add_Row)
        self.bind_all("<Delete>", self.delete_Cells)
        self.bind_all("<Control-v>", self.paste)

        #if not hasattr(self,'parentapp'):
        #    self.parentapp = self.parentframe

        self.parentframe.master.bind_all("<Right>", self.handle_arrow_keys)
        self.parentframe.master.bind_all("<Left>", self.handle_arrow_keys)
        self.parentframe.master.bind_all("<Up>", self.handle_arrow_keys)
        self.parentframe.master.bind_all("<Down>", self.handle_arrow_keys)
        self.parentframe.master.bind_all("<KP_8>", self.handle_arrow_keys)
        self.parentframe.master.bind_all("<Return>", self.handle_arrow_keys)
        self.parentframe.master.bind_all("<Tab>", self.handle_arrow_keys)
        if 'windows' in self.platform:
            self.bind("<MouseWheel>", self.mouse_wheel)
        self.bind('<Button-4>', self.mouse_wheel)
        self.bind('<Button-5>', self.mouse_wheel)
        return

    def getModel(self):
        """Get the current table model"""
        return self.model

    def setModel(self,model):
        self.model = model
        return

    def createfromDict(self, data):
        """Attempt to create a new model/table from a dict"""
        try:
            namefield=self.namefield
        except:
            namefield=data.keys()[0]
        self.model = TableModel()
        self.model.importDict(data, namefield=namefield)
        self.model.setSortOrder(0,reverse=self.reverseorder)
        return

    def createTableFrame(self, callback=None):
        """Adds column header and scrollbars and combines them with
           the current table adding all to the master frame provided in constructor.
           Table is then redrawn."""

        #Add the table and header to the frame
        self.Yscrollbar = AutoScrollbar(self.parentframe,orient=VERTICAL,command=self.set_yviews)
        self.Yscrollbar.grid(row=1,column=2,rowspan=1,sticky='news',pady=0,ipady=0)
        self.Xscrollbar = AutoScrollbar(self.parentframe,orient=HORIZONTAL,command=self.set_xviews)
        self.Xscrollbar.grid(row=2,column=1,columnspan=1,sticky='news')
        self['xscrollcommand'] = self.Xscrollbar.set
        self['yscrollcommand'] = self.Yscrollbar.set
        self.tablecolheader['xscrollcommand']=self.Xscrollbar.set
        self.tablerowheader['yscrollcommand']=self.Yscrollbar.set
        self.parentframe.rowconfigure(1,weight=1)
        self.parentframe.columnconfigure(1,weight=1)

        self.tablecolheader.grid(row=0,column=1,rowspan=1,sticky='news',pady=0,ipady=0)
        self.tablerowheader.grid(row=1,column=0,rowspan=1,sticky='news',pady=0,ipady=0)
        self.grid(row=1,column=1,rowspan=1,sticky='news',pady=0,ipady=0)
        if self.model.getRowCount()<500:
            self.adjust_colWidths()
        self.redrawTable(callback=callback)
        self.parentframe.bind("<Configure>", self.resizeTable)
        self.tablecolheader.xview("moveto", 0)
        self.xview("moveto", 0)
        #self.table.yview("moveto", 0)

        return

    def redrawTable(self, event=None, callback=None):
        """Draw the table from scratch based on it's model data"""
        import time
        model = self.model
        self.rows=self.model.getRowCount()
        self.cols=self.model.getColumnCount()
        self.tablewidth=(self.cellwidth)*self.cols
        self.configure(bg=self.cellbackgr)
        #determine col positions for first time
        self.set_colPositions()
        
        #are we drawing a filtered subset of the recs?
        if self.filtered == True and self.model.filteredrecs != None:            
            self.rows = len(self.model.filteredrecs)
            self.delete('colrect')
            
        #check if large no. of records and switch to paging view
        if self.paging == 0 and self.rows >= 500:
            self.paging = 1
        #if using paging, we only want to display the current page..
        if self.paging == 1:
            self.numpages = int(math.ceil(float(self.rows)/self.rowsperpage))
          
            if self.currentpage == None:
                self.currentpage = 0
            self.drawNavFrame()
        else:
            try:
                self.navFrame.destroy()
                self.navFrame.forget()
            except:
                pass
        #determine current range of rows to draw if paging
        if self.paging == 1 and self.rows>self.rowsperpage:
            lower=self.currentpage*self.rowsperpage
            upper=lower+self.rowsperpage
            if upper>=self.rows:
                upper=self.rows
            self.rowrange=range(lower,upper)
            self.configure(scrollregion=(0,0, self.tablewidth+self.x_start, self.rowheight*self.rowsperpage+10))
        else:
            self.rowrange = range(0,self.rows)
            self.configure(scrollregion=(0,0, self.tablewidth+self.x_start, self.rowheight*self.rows+10))
            
        self.draw_grid()
        self.update_idletasks()
        self.tablecolheader.redraw()
        self.tablerowheader.redraw(paging=self.paging)
        align=None
        self.delete('fillrect')
     
        if self.cols == 0 or self.rows == 0:
            self.delete('entry')
            self.delete('rowrect')
            self.delete('currentrect')
            return

        #now draw model data in cells
        rowpos=0
        if self.model!=None:
            for row in self.rowrange:
                if callback != None:
                    callback()                   
                for col in range(self.cols):
                    colname = model.getColumnName(col)
                    if colname == 'name' or colname == 'Name':
                        align='w'
                    else:
                        align=None
                    bgcolor = self.model.getColorAt(row,col, 'bg')
                    fgcolor = self.model.getColorAt(row,col, 'fg')
                    text = self.model.getValueAt(row,col)
                    self.draw_Text(rowpos, col, text, fgcolor, align)
                    if bgcolor != None:
                        self.draw_rect(rowpos,col, color=bgcolor)
                rowpos+=1
        self.setSelectedRow(0)
        self.drawSelectedRow()
        self.draw_selected_rect(self.currentrow, self.currentcol)
        if len(self.multiplerowlist)>1:
            self.drawMultipleRows(self.multiplerowlist)

        return

    def redrawCell(self, row=None, col=None, recname=None, colname=None):
        """Redraw a specific cell only"""
        if row == None and recname != None:
            row = self.model.getRecordIndex(recname)
        if col == None and colname != None:
            col = self.model.getColumnIndex(colname)       
        bgcolor = self.model.getColorAt(row,col, 'bg')
        fgcolor = self.model.getColorAt(row,col, 'fg')
        text = self.model.getValueAt(row,col)
        self.draw_Text(row, col, text, fgcolor)
        if bgcolor != None:
            self.draw_rect(row,col, color=bgcolor)
                        
        return
        
    def resizeTable(self, event):
        """Respond to a resize event - redraws table"""
        if self.autoresizecols == 1 and event != None:
            self.cellwidth = (event.width - self.x_start - 24) / self.cols
            #print 'cellwidth', self.cellwidth
            self.redrawTable()
        return

    def adjust_colWidths(self):
        """Optimally adjust col widths at start to accomodate the longest entry"""
        try:
            fontsize=self.celltextsizevar.get()
        except:
            fontsize=11
        scale = 8.5 # +fontsize/10

        for col in range(self.cols):
            width = self.model.getlongestEntry(col) * scale
            #print 'comparing', width,  self.maxcellwidth
            if width >= self.maxcellwidth:
                width = self.maxcellwidth
            elif width < self.cellwidth:
                width = self.cellwidth
            colname=self.model.getColumnName(col)
            self.model.columnwidths[colname]=width
        return

    def set_colPositions(self):
        """Determine current column grid positions"""
        self.col_positions=[]
        w=self.cellwidth
        x_pos=self.x_start
        self.col_positions.append(x_pos)
        for col in range(self.cols):
            colname=self.model.getColumnName(col)
            if self.model.columnwidths.has_key(colname):
                x_pos=x_pos+self.model.columnwidths[colname]
            else:
                x_pos=x_pos+w
            self.col_positions.append(x_pos)
        self.tablewidth = self.col_positions[len(self.col_positions)-1]

        return

    def sortTable(self, sortcol=None, reverse=0):
        """Set up sort order dict based on currently selected field"""
        #self.sortcol = self.currentcol
        self.model.setSortOrder(self.currentcol, self.reverseorder)
        self.reverseorder = reverse
        self.redrawTable()
        return

    def set_xviews(self,*args):
        """Set the xview of table and col header"""
        apply(self.xview,args)
        apply(self.tablecolheader.xview,args)
        return

    def set_yviews(self,*args):
        """Set the xview of table and row header"""
        apply(self.yview,args)
        apply(self.tablerowheader.yview,args)
        return

    def drawNavFrame(self):
        """Draw the frame for selecting pages when paging is on"""
        #print 'adding page frame'
        import Table_images
        self.navFrame = Frame(self.parentframe)
        self.navFrame.grid(row=4,column=0,columnspan=2,sticky='news',padx=1,pady=1,ipady=1)
        pagingbuttons = { 'start' : self.first_Page, 'prev' : self.prev_Page,
                          'next' : self.next_Page, 'end' : self.last_Page}
        images = { 'start' : Table_images.start(), 'prev' : Table_images.prev(),
                   'next' : Table_images.next(), 'end' : Table_images.end()}
        skeys=['start', 'prev', 'next', 'end']
        for i in skeys:
            b = Button(self.navFrame, text=i, command=pagingbuttons[i],
                        relief=GROOVE,
                        image=images[i])
            b.image = images[i]
            b.pack(side=LEFT, ipadx=1, ipady=1)
        Label(self.navFrame,text='Page '+str(self.currentpage+1)+' of '+ str(self.numpages),fg='white',
                  bg='#3366CC',relief=SUNKEN).pack(side=LEFT,ipadx=2,ipady=2,padx=4)
        #Label(self.navFrame,text='Goto Record:').pack(side=LEFT,padx=3)
        #self.gotorecordvar = StringVar()
        #Entry(self.navFrame,textvariable=self.gotorecordvar,
        #          width=8,bg='white').pack(side=LEFT,ipady=3,padx=2)
        Label(self.navFrame,text=str(self.rows)+' records').pack(side=LEFT,padx=3)
        Button(self.navFrame,text='Normal View',command=self.paging_Off,
                   bg='#99CCCC',relief=GROOVE).pack(side=LEFT,padx=3)
        return

    def paging_Off(self):
        self.rows=self.model.getRowCount()
        if self.rows >= 1000:
            tkMessageBox.showwarning("Warning",
                                     'This table has over 1000 rows.'
                                     'You should stay in page view.'
                                     'You can increase the rows per page in settings.',
                                     parent=self.parentframe)
        else:
            self.paging = 0
            self.usepagingvar.set(0)
            self.redrawTable()
        return

    def first_Page(self):
        """Go to next page"""
        self.currentpage = 0
        self.redrawTable()
        return

    def last_Page(self):
        """Go to next page"""
        self.currentpage = self.numpages-1
        self.redrawTable()
        return

    def prev_Page(self):
        """Go to next page"""
        if self.currentpage > 0:
            self.currentpage -= 1
            self.redrawTable()
        return

    def next_Page(self):
        """Go to next page"""
        if self.currentpage < self.numpages-1:
            self.currentpage += 1
            self.redrawTable()
        return

    def get_AbsoluteRow(self, row):
        """This function always returns the corrected absolute row number,
           whether if paging is on or not"""
        if self.paging == 0:
            return row
        absrow = row+self.currentpage*self.rowsperpage
        return absrow

    def check_PageView(self, row):
        """Check if row clickable for page view"""
        if self.paging == 1:
            absrow = self.get_AbsoluteRow(row)
            if absrow >= self.rows or row > self.rowsperpage:
                return 1
        return 0

    def add_Row(self, rowname=None):
        """Add a new row"""
        if rowname == None:
            rowname = tkSimpleDialog.askstring("New row name?",
                                               "Enter row name:",
                                               parent=self.parentframe)
        if rowname != None:
            if rowname == '':
                tkMessageBox.showwarning("Whoops",
                                         "Name should not be blank.",
                                         parent=self.parentframe)
                return
            if self.getModel().data.has_key(rowname):
                 tkMessageBox.showwarning("Name exists",
                                          "Record already exists!",
                                          parent=self.parentframe)
            else:
                self.model.addRow(rowname)
                self.setSelectedRow(self.model.getRecordIndex(rowname))
                self.redrawTable()
        return

    def add_Column(self, newname=None):
        """Add a new column"""
        if newname == None:
            d = SimpleTableDialog(title="New Column",
                                  parent=self.parentframe, table=self)

            if d.result == None:
                return
            else:
                coltype = d.result[0]
                newname = d.result[1]
                
        if newname != None:
            if newname in self.getModel().columnNames:
                tkMessageBox.showwarning("Name exists",
                                         "Name already exists!",
                                         parent=self.parentframe)
            else:
                self.model.addColumn(newname, coltype)
                self.parentframe.configure(width=self.width)
                self.redrawTable()
        return

    def delete_Row(self):
        """Delete a row"""
        if len(self.multiplerowlist)>1:
            print 'deleting mult'
            n = tkMessageBox.askyesno("Delete",
                                      "Delete Selected Records?",
                                      parent=self.parentframe)
            print str(n)
            if n == True:
                rows = self.multiplerowlist
                self.model.deleteRows(rows)
                self.setSelectedRow(0)
                self.multiplerowlist = []
                self.redrawTable()
        else:            
            n = tkMessageBox.askyesno("Delete",
                                      "Delete This Record?",
                                      parent=self.parentframe)
            if n:
                row = self.getSelectedRow()
                self.model.deleteRow(row)
                self.setSelectedRow(row-1)
                self.clearSelected()
                self.redrawTable()
        return

    def delete_Column(self):
        """Delete currently selected column"""
        n =  tkMessageBox.askyesno("Delete",
                                   "Delete This Column?",
                                   parent=self.parentframe)
        if n:
            col = self.getSelectedColumn()
            self.model.deleteColumn(col)
            self.currentcol = self.currentcol - 1
            self.redrawTable()
        return

    def delete_Cells(self, rows, cols):
        """Clear the cell contents"""
        n =  tkMessageBox.askyesno("Clear Confirm",
                                   "Clear this data?",
                                   parent=self.parentframe)
        if not n:
            return
        for col in cols:
            for row in rows:
                absrow = self.get_AbsoluteRow(row)
                self.model.deleteCellRecord(row, col)       
        self.redrawCell(row,col)
        return

    def autoAdd_Rows(self, numrows=None):
        """Automatically add x number of records"""
        import string
        if numrows == None:
            numrows = tkSimpleDialog.askinteger("Auto add rows.",
                                                "How many empty rows?",
                                                parent=self.parentframe)

        self.model.auto_AddRows(numrows)
        self.redrawTable()
        return

    def autoAdd_Columns(self, numcols=None):
        """Automatically add x number of cols"""
        if numcols == None:
            numcols = tkSimpleDialog.askinteger("Auto add rows.",
                                                "How many empty columns?",
                                                parent=self.parentframe)
        self.model.auto_AddColumns(numcols)
        self.parentframe.configure(width=self.width)
        self.redrawTable()
        return

    def getRecordInfo(self, row):
        """Show the record for this row"""
        model = self.model
        #We need a custom dialog for allowing field entries here
        absrow = self.get_AbsoluteRow(row)
        d = RecordViewDialog(title="Record Details",
                                  parent=self.parentframe, table=self, row=absrow)
        return

    def findValue(self, searchstring=None, findagain=None):
        """Return the row/col for the input value"""
        if searchstring == None:
            searchstring = tkSimpleDialog.askstring("Search table.",
                                               "Enter search value",
                                               parent=self.parentframe)
        found=0
        if findagain == None or not hasattr(self,'foundlist'):
            self.foundlist=[]
        if self.model!=None:
            for row in range(self.rows):
                for col in range(self.cols):
                    text = str(self.model.getValueAt(row,col))
                    if text=='' or text==None:
                        continue
                    cell=row,col
                    if findagain == 1 and cell in self.foundlist:
                        continue
                    if text.lower().find(searchstring.lower())!=-1:
                        print 'found in',row,col
                        found=1
                        #highlight cell
                        self.delete('searchrect')
                        self.draw_rect(row, col, color='red', tag='searchrect', delete=0)
                        self.lift('searchrect')
                        self.lift('celltext'+str(col)+'_'+str(row))
                        #add row/col to foundlist
                        self.foundlist.append(cell)
                        #need to scroll to centre the cell here..
                        x,y = self.getCanvasPos(row, col)
                        self.xview('moveto', x)
                        self.yview('moveto', y)
                        self.tablecolheader.xview('moveto', x)
                        self.tablerowheader.yview('moveto', y)
                        return row, col
        if found==0:
            self.delete('searchrect')
            print 'nothing found'
            return None

    def closeFilterFrame(self):
        """Callback for closing filter frame"""
        self.filterframe = None
        self.showAll()
        return
    
    def showAll(self):
        self.model.filteredrecs = None
        self.filtered = False
        self.redrawTable()
        return
    
    def doFilter(self, event=None):
        """Filter the table display by some column values.
        We simply pass the model search function to the the filtering 
        class and that handles everything else.
        See filtering frame class for how searching is done.
        """
        if self.model==None:
            return
        from Filtering import FilterFrame   
        names = self.filterframe.doFiltering(searchfunc=self.model.filterBy)
        #create a list of filtered recs
        self.model.filteredrecs = names 
        self.filtered = True
        if self.paging == 1:
            self.currentpage = 0
        self.redrawTable()
        return

    def createFilteringBar(self, parent=None, fields=None):
        """Add a filter frame"""
        if parent == None:
            parent = Toplevel()            
        if fields == None:
            fields = self.model.columnNames
        from Filtering import FilterFrame    
        self.filterframe = FilterFrame(parent, fields,
                                       self.doFilter, self.closeFilterFrame)
        return self.filterframe

    def showFilteringBar(self):
        frame = self.createFilteringBar()
        frame.pack()
        return
    
    def resize_Column(self, col, width):
        """Resize a column by dragging"""
        #print 'resizing column', col
        #recalculate all col positions..
        colname=self.model.getColumnName(col)
        self.model.columnwidths[colname]=width
        self.set_colPositions()
        self.redrawTable()
        self.drawSelectedCol(self.currentcol)
        return

    def get_currentRecord(self):
        """Get the currently selected record"""
        rec = self.model.getRecordAtRow(self.currentrow)
        return rec

    def get_currentColName(self):
        """Get the currently selected record name"""
        colname = self.mo(self.currentcol)
        return colname

    def get_currentRecordName(self):
        """Get the currently selected record name"""
        recname = self.model.getRecName(self.currentrow)
        return recname

    def get_selectedRecordNames(self):
        """Get a list of the current multiple selection, if any"""
        recnames=[]
        for row in self.multiplerowlist:
            recnames.append(self.model.getRecName(row))
        return recnames

    def get_currentRecCol(self):
        """Get the clicked rec and col names as a tuple"""
        recname = self.get_currentRecordName()
        colname = self.get_currentColName()
        return (recname, colname)

    def get_row_clicked(self, event):
        """get row where event on canvas occurs"""
        h=self.rowheight
        #get coord on canvas, not window, need this if scrolling
        y = int(self.canvasy(event.y))
        y_start=self.y_start
        rowc = (int(y)-y_start)/h
        #rowc = math.floor(rowc)
        #print 'event.y',event.y, 'y',y
        #print 'rowclicked', rowc
        return rowc

    def get_col_clicked(self,event):
        """get col where event on canvas occurs"""
        w=self.cellwidth
        x = int(self.canvasx(event.x))
        x_start=self.x_start
        #print self.col_positions
        for colpos in self.col_positions:
            try:
                nextpos=self.col_positions[self.col_positions.index(colpos)+1]
            except:
                nextpos=self.tablewidth
            if x > colpos and x <= nextpos:
                #print 'x=', x, 'colpos', colpos, self.col_positions.index(colpos)
                return self.col_positions.index(colpos)
            else:
                #print None
                pass
        #return colc

    def setSelectedRow(self, row):
        """Set currently selected row and reset multiple row list"""
        self.currentrow = row
        self.multiplerowlist = []
        self.multiplerowlist.append(row)
        return

    def setSelectedCol(self, col):
        """Set currently selected column"""
        self.currentcol = col
        self.multiplecollist = []
        self.multiplecollist.append(col)
        return

    def getSelectedRow(self):
        """Get currently selected row"""
        return self.currentrow

    def getSelectedColumn(self):
        """Get currently selected column"""
        return self.currentcol

    def select_All(self):
        """Select all rows"""
        self.startrow = 0
        self.endrow = self.rows
        self.multiplerowlist = range(self.startrow,self.endrow)
        self.drawMultipleRows(self.multiplerowlist)
        return

    def getCellCoords(self, row, col):
        """Get x-y coordinates to drawing a cell in a given row/col"""        
        colname=self.model.getColumnName(col)
        if self.model.columnwidths.has_key(colname):
            w=self.model.columnwidths[colname]
        else:
            w=self.cellwidth
        h=self.rowheight
        x_start=self.x_start
        y_start=self.y_start

        #get nearest rect co-ords for that row/col
        #x1=x_start+w*col
        x1=self.col_positions[col]
        y1=y_start+h*row
        x2=x1+w
        y2=y1+h
        return x1,y1,x2,y2

    def getCanvasPos(self, row, col):
        """Get the cell x-y coords as a fraction of canvas size"""
        if self.rows==0:
            return None, None
        x1,y1,x2,y2 = self.getCellCoords(row,col)
        cx=float(x1)/self.tablewidth
        cy=float(y1)/(self.rows*self.rowheight)        
        return cx, cy

    def isInsideTable(self,x,y):
        """Returns true if x-y coord is inside table bounds"""
        if self.x_start < x < self.tablewidth and self.y_start < y < self.rows*self.rowheight:
            return 1
        else:
            return 0
        return answer

    def setRowHeight(self, h):
        """Set the row height"""
        self.rowheight = h
        return

    def clearSelected(self):
        self.delete('rect')
        self.delete('entry')
        self.delete('tooltip')
        self.delete('searchrect')
        self.delete('colrect')
        self.delete('multicellrect')

        #self.delete('formulabox')
        return

    def gotoprevRow(self):
        """Programmatically set previous row - eg. for button events"""
        self.clearSelected()
        current = self.getSelectedRow()
        self.setSelectedRow(current-1)
        self.startrow = current-1
        self.endrow = current-1
        #reset multiple selection list
        self.multiplerowlist=[]
        self.multiplerowlist.append(self.currentrow)
        self.draw_selected_rect(self.currentrow, self.currentcol)
        self.drawSelectedRow()
        coltype = self.model.getColumnType(self.currentcol)
        if coltype == 'text' or coltype == 'number':
            self.draw_cellentry(self.currentrow, self.currentcol)
        return

    def gotonextRow(self):
        """Programmatically set next row - eg. for button events"""
        self.clearSelected()
        current = self.getSelectedRow()
        self.setSelectedRow(current+1)
        self.startrow = current+1
        self.endrow = current+1
        #reset multiple selection list
        self.multiplerowlist=[]
        self.multiplerowlist.append(self.currentrow)
        self.draw_selected_rect(self.currentrow, self.currentcol)
        self.drawSelectedRow()
        coltype = self.model.getColumnType(self.currentcol)
        if coltype == 'text' or coltype == 'number':
            self.draw_cellentry(self.currentrow, self.currentcol)
        return

    def handle_left_click(self, event):
        """Respond to a single press"""
        #which row and column is the click inside?
        self.clearSelected()
        self.allrows = False
        rowclicked = self.get_row_clicked(event)
        colclicked = self.get_col_clicked(event)
        if self.mode == 'formula':
            self.handleFormulaClick(rowclicked, colclicked)
            return
        if hasattr(self, 'cellentry'):
            self.cellentry.destroy()
        #ensure popup menus are removed if present
        if hasattr(self, 'rightmenu'):
            self.rightmenu.destroy()
        if hasattr(self.tablecolheader, 'rightmenu'):
            self.tablecolheader.rightmenu.destroy()
        if self.check_PageView(rowclicked) == 1:
            return

        self.startrow = rowclicked
        self.endrow = rowclicked
        self.startcol = colclicked
        self.endcol = colclicked
        #reset multiple selection list
        self.multiplerowlist=[]
        self.multiplerowlist.append(rowclicked)
        if 0 <= rowclicked < self.rows and 0 <= colclicked < self.cols:
            self.setSelectedRow(rowclicked)
            self.setSelectedCol(colclicked)
            self.draw_selected_rect(self.currentrow, self.currentcol)
            self.drawSelectedRow()
            self.tablerowheader.drawSelectedRows(rowclicked)
            coltype = self.model.getColumnType(colclicked)
            if coltype == 'text' or coltype == 'number':                
                self.draw_cellentry(rowclicked, colclicked)
        return

    def handle_left_release(self,event):
        self.endrow = self.get_row_clicked(event)
        return

    def handle_left_ctrl_click(self, event):
        """Handle ctrl clicks for multiple row selections"""
        rowclicked = self.get_row_clicked(event)
        colclicked = self.get_col_clicked(event)
        if 0 <= rowclicked < self.rows and 0 <= colclicked < self.cols:
            if rowclicked not in self.multiplerowlist:
                self.multiplerowlist.append(rowclicked)
            else:
                self.multiplerowlist.remove(rowclicked)
            self.drawMultipleRows(self.multiplerowlist)
            if colclicked not in self.multiplecollist:
                self.multiplecollist.append(colclicked)
            #print self.multiplecollist
            self.drawMultipleCells()
        return

    def handle_left_shift_click(self, event):
        """Handle shift click, for selecting multiple rows"""
        #Has same effect as mouse drag, so just use same method
        self.handle_mouse_drag(event)
        return

    def handle_mouse_drag(self, event):
        """Handle mouse moved with button held down, multiple selections"""
        if hasattr(self, 'cellentry'):
            self.cellentry.destroy()
        rowover = self.get_row_clicked(event)
        colover = self.get_col_clicked(event)
        if colover == None or rowover == None:
            return
        if self.check_PageView(rowover) == 1:
            return
        if rowover >= self.rows or self.startrow > self.rows:
            #print rowover
            return
        else:
            self.endrow = rowover
        #do columns
        if colover > self.cols or self.startcol > self.cols:
            return
        else:
            self.endcol = colover
            if self.endcol < self.startcol:
                self.multiplecollist=range(self.endcol, self.startcol+1)
            else:
                self.multiplecollist=range(self.startcol, self.endcol+1)
            #print self.multiplecollist
        #draw the selected rows
        if self.endrow != self.startrow:
            if self.endrow < self.startrow:
                self.multiplerowlist=range(self.endrow, self.startrow+1)
            else:
                self.multiplerowlist=range(self.startrow, self.endrow+1)
            self.drawMultipleRows(self.multiplerowlist)
            self.tablerowheader.drawSelectedRows(self.multiplerowlist)
            #draw selected cells outline using row and col lists
            #print self.multiplerowlist
            self.drawMultipleCells()
        else:
            self.multiplerowlist = []
            self.multiplerowlist.append(self.currentrow)
            if len(self.multiplecollist) >= 1:
                self.drawMultipleCells()
            self.delete('multiplesel')
        #print self.multiplerowlist
        return

    def handle_arrow_keys(self, event):
        """Handle arrow keys press"""
        #print event.keysym

        row = self.get_row_clicked(event)
        col = self.get_col_clicked(event)
        x,y = self.getCanvasPos(self.currentrow, 0)
        if x == None:
            return

        if event.keysym == 'Up':
            if self.currentrow == 0:
                return
            else:
                #self.yview('moveto', y)
                #self.tablerowheader.yview('moveto', y)
                self.currentrow  = self.currentrow -1
        elif event.keysym == 'Down':
            if self.currentrow >= self.rows-1:
                return
            else:
                #self.yview('moveto', y)
                #self.tablerowheader.yview('moveto', y)
                self.currentrow  = self.currentrow +1
        elif event.keysym == 'Right' or event.keysym == 'Tab':
            if self.currentcol >= self.cols-1:
                if self.currentrow < self.rows-1:
                    self.currentcol = 0
                    self.currentrow  = self.currentrow +1
                else:
                    return
            else:
                self.currentcol  = self.currentcol +1
        elif event.keysym == 'Left':
            self.currentcol  = self.currentcol -1
        self.draw_selected_rect(self.currentrow, self.currentcol)
        coltype = self.model.getColumnType(self.currentcol)
        if coltype == 'text' or coltype == 'number':
            self.delete('entry')
            self.draw_cellentry(self.currentrow, self.currentcol)
        return

    def handle_double_click(self, event):
        """Do double click stuff. Selected row/cols will already have
           been set with single click binding"""
        #print 'double click'
        row = self.get_row_clicked(event)
        col = self.get_col_clicked(event)
        absrow = self.get_AbsoluteRow(row)
        model=self.getModel()
        cellvalue = model.getCellRecord(absrow, col)
        if Formula.isFormula(cellvalue):
            self.formula_Dialog(row, col, cellvalue)
            #self.enterFormula(rowclicked, colclicked)
        #self.draw_cellentry(self.currentrow, self.currentcol)
        return

    def handle_right_click(self, event):
        """respond to a right click"""
        self.delete('tooltip')
        self.tablerowheader.clearSelected()
        if hasattr(self, 'rightmenu'):
            self.rightmenu.destroy()
        rowclicked = self.get_row_clicked(event)
        colclicked = self.get_col_clicked(event)
        if colclicked == None:
            self.rightmenu = self.popupMenu(event, outside=1)
            return
        if self.check_PageView(rowclicked) == 1:
            self.rightmenu = self.popupMenu(event, outside=1)
            return

        if (rowclicked in self.multiplerowlist or self.allrows == True) and colclicked in self.multiplecollist:
            self.rightmenu = self.popupMenu(event, rows=self.multiplerowlist, cols=self.multiplecollist)
        else:
            if 0 <= rowclicked < self.rows and 0 <= colclicked < self.cols:
                self.clearSelected()
                self.allrows = False
                self.setSelectedRow(rowclicked)
                self.setSelectedCol(colclicked)
                self.draw_selected_rect(self.currentrow, self.currentcol)
                self.drawSelectedRow()
            if self.isInsideTable(event.x,event.y) == 1:
                self.rightmenu = self.popupMenu(event,rows=self.multiplerowlist, cols=self.multiplecollist)
            else:
                self.rightmenu = self.popupMenu(event, outside=1)
        return

    def handle_motion(self, event):
        """Handle mouse motion on table"""
        self.delete('tooltip')
        row = self.get_row_clicked(event)
        col = self.get_col_clicked(event)
        if self.check_PageView(row) == 1:
            return
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.draw_tooltip(row, col)

        return

    def gotonextCell(self, event):
        """Move highlighted cell to next cell in row or a new col"""
        #print 'next'
        if hasattr(self, 'cellentry'):
            self.cellentry.destroy()
        self.currentcol=self.currentcol+1
        if self.currentcol >= self.cols-1:
            self.currentrow  = self.currentrow +1
            self.currentcol = self.currentcol+1
        self.draw_selected_rect(self.currentrow, self.currentcol)
        return

    def movetoSelectedRow(self, row=None, recname=None):
        """Move to selected row, updating table"""
        row=self.model.getRecordIndex(recname)        
        self.setSelectedRow(row)                
        self.drawSelectedRow()  
        x,y = self.getCanvasPos(row, 0)     
        self.yview('moveto', y-0.01)
        self.tablecolheader.yview('moveto', y)        
        return        
    
    def handleFormulaClick(self, row, col):
        """Do a dialog for cell formula entry"""
    
        model = self.getModel()
        cell = list(model.getRecColNames(row, col))
        absrow = self.get_AbsoluteRow(row)
        self.formulaText.insert(END, str(cell))
        self.formulaText.focus_set()
        self.draw_selected_rect(row, col, color='red')
        return

    def formula_Dialog(self, row, col, currformula=None):
        """Formula dialog"""
        self.mode = 'formula'
        print self.mode
        absrow = self.get_AbsoluteRow(row)
        x1,y1,x2,y2 = self.getCellCoords(row,col)
        w=300
        h=h=self.rowheight * 3
        def close():
            if hasattr(self,'formulaWin'):
                self.delete('formulabox')
            self.mode = 'normal'
        def calculate():
            #get text area contents and do formula
            f = self.formulaText.get(1.0, END)
            f = f.strip('\n')
            self.model.setFormulaAt(f,absrow,col)
            value = self.model.doFormula(f)
            color = self.model.getColorAt(absrow,col,'fg')
            self.draw_Text(row, col, value, color)
            close()
            self.mode = 'normal'
            return
        def clear():
            self.formulaText.delete(1.0, END)

        self.formulaFrame = Frame(width=w,height=h,bd=3,relief=RIDGE)
        self.formulaText = Text(self.formulaFrame, width=30, height=8, bg='white',relief=GROOVE)
        self.formulaText.pack(side=LEFT,padx=2,pady=2)
        if currformula != None:
            self.formulaText.insert(END, Formula.getFormula(currformula))
        cancelbutton=Button(self.formulaFrame, text='Cancel',
                            relief=GROOVE,bg='#99ccff',command=close)
        cancelbutton.pack(fill=BOTH,padx=2,pady=2)
        donebutton=Button(self.formulaFrame, text='Done',
                          relief=GROOVE,bg='#99ccff',command=calculate)
        donebutton.pack(fill=BOTH,padx=2,pady=2)
        '''clrbutton=Button(self.formulaFrame, text='Clear',
                         relief=GROOVE,bg='#99ccff',command=clear)
        clrbutton.pack(fill=BOTH,padx=2,pady=2) '''
        #add to canvas
        self.formulaWin = self.create_window(x1+self.inset,y1+self.inset,
                                width=w,height=h,
                                window=self.formulaFrame,anchor='nw',
                                tag='formulabox')
        self.formulaText.focus_set()
        return

    def convertFormulae(self, rows, cols=None):
        """Convert the formulas in the cells to their result values"""
        if len(self.multiplerowlist) == 0 or len(self.multiplecollist) == 0:
            return None
      
        print rows, cols
        if cols == None:
            cols = range(self.cols)
        for r in rows:
            absr=self.get_AbsoluteRow(r)
            for c in cols:
                val = self.model.getValueAt(absr,c)
                self.model.setValueAt(val, absr, c)
        return

    def paste(self, event=None):
        """Copy from clipboard"""
        print self.parentframe.clipboard_get()
        return

    def copyCell(self, rows, cols=None):
        """Copy cell contents to a temp internal clipboard"""
        row = rows[0]; col = cols[0]
        absrow = self.get_AbsoluteRow(row)
        import copy
        self.clipboard = copy.deepcopy(self.model.getCellRecord(absrow, col))
        return

    def pasteCell(self, rows, cols=None):
        """Paste cell from internal clipboard"""
        row = rows[0]; col = cols[0]
        absrow = self.get_AbsoluteRow(row)
        val = self.clipboard
        self.model.setValueAt(val, absrow, col)
        self.redrawTable()
        return

    def copyColumns(self):
        """Copy current selected cols"""
        M = self.model
        coldata = {}
        for col in self.multiplecollist:
            name = M.columnNames[col]
            coldata[name] = M.getColumnData(columnName=name)       
        return coldata
        
    def pasteColumns(self, coldata):
        """Paste new cols, overwrites existing names"""
        M = self.model        
        for name in coldata:            
            if name not in M.columnNames:
                M.addColumn(name)            
            for r in range(len(coldata[name])):
                val = coldata[name][r]
                col = M.columnNames.index(name)                
                if r >= self.rows:
                    break                 
                M.setValueAt(val, r, col)            
        self.redrawTable()
        return coldata       
        
    # --- Some cell specific actions here ---

    def setcellColor(self, rows, cols=None, newColor=None, key=None, redraw=True):
        """Set the cell color for one or more cells and save it in the model color"""

        model = self.getModel()
        if newColor == None:
            import tkColorChooser
            ctuple, newColor = tkColorChooser.askcolor(title='pick a color')
            if newColor == None:
                return

        if type(rows) is IntType:
            x=rows
            rows=[]
            rows.append(x)
        if self.allrows == True:
            #we use all rows if the whole column has been selected
            rows = range(0,self.rows)
        if cols == None:
            cols = range(self.cols)
        for col in cols:
            for row in rows:
                absrow = self.get_AbsoluteRow(row)
                model.setColorAt(absrow, col, color=newColor, key=key)
                #setcolor(absrow, col)
        if redraw == True:
            self.redrawTable()
        return


    def popupMenu(self, event, rows=None, cols=None, outside=None):
        """Add left and right click behaviour for canvas, should not have to override
            this function, it will take its values from defined dicts in constructor"""
        if outside == None:
            row = self.get_row_clicked(event)
            col = self.get_col_clicked(event)
            coltype = self.model.getColumnType(col)
        popupmenu = Menu(self, tearoff = 0)
        def popupFocusOut(event):
            popupmenu.unpost()

        if outside == 1:
            #if outside table, just show general items            
            popupmenu.add_command(label="Show Prefs", command= self.showtablePrefs)
            popupmenu.add_command(label="Export Table", command= self.exportTable)
            popupmenu.add_command(label="Filter Recs", command= self.showFilteringBar)
        else:
            def add_commands(fieldtype):
                """Add commands to popup menu for col type"""
                #add column actions for this table type defined in self.columnactions
                functions = self.columnactions[fieldtype]
                for f in functions.keys():
                    func = getattr(self, functions[f])
                    popupmenu.add_command(label=f, command= lambda : func(row,col))
                return

            def add_defaultcommands():
                """now add general actions for all cells"""
                main = ["Set Fill Color","Set Text Color","Copy", "Paste", "Fill Down","Fill Right", "Clear Data",
                         "Delete Row", "Select All", "Plot Selected","Plot Options",
                         "Show Prefs"]
                utils = ["View Record", "Formulae->Value", "Export Table"]
                defaultactions={"Set Fill Color" : lambda : self.setcellColor(rows,cols,key='bg'),
                                "Set Text Color" : lambda : self.setcellColor(rows,cols,key='fg'),
                                "Copy" : lambda : self.copyCell(rows, cols),
                                "Paste" : lambda : self.pasteCell(rows, cols),
                                "Fill Down" : lambda : self.fill_down(rows, cols),
                                "Fill Right" : lambda : self.fill_across(cols, rows),
                                "Delete Row" : lambda : self.delete_Row(),
                                "View Record" : lambda : self.getRecordInfo(row),
                                "Clear Data" : lambda : self.delete_Cells(rows, cols),
                                "Select All" : self.select_All,
                                "Plot Selected" : self.plot_Selected,
                                "Plot Options" : self.plotSetup,
                                "Export Table" : self.exportTable,
                                "Show Prefs" : self.showtablePrefs,
                                "Formulae->Value" : lambda : self.convertFormulae(rows, cols)}

                for action in main:
                    if action == 'Fill Down' and (rows == None or len(rows) <= 1):
                        continue
                    if action == 'Fill Right' and (cols == None or len(cols) <= 1):
                        continue
                    else:
                        popupmenu.add_command(label=action, command=defaultactions[action])
                popupmenu.add_separator()
                utilsmenu = Menu(popupmenu, tearoff = 0)
                popupmenu.add_cascade(label="Utils",menu=utilsmenu)
                for action in utils:
                    utilsmenu.add_command(label=action, command=defaultactions[action])
                return

            if self.columnactions.has_key(coltype):
                add_commands(coltype)
            add_defaultcommands()

        popupmenu.bind("<FocusOut>", popupFocusOut)
        popupmenu.focus_set()
        popupmenu.post(event.x_root, event.y_root)
        return popupmenu

    # --- spreadsheet type functions ---

    def fill_down(self, rowlist, collist):
        """Fill down a column, or multiple columns"""
        model = self.model
        absrow  = self.get_AbsoluteRow(rowlist[0])
        #remove first element as we don't want to overwrite it
        rowlist.remove(rowlist[0])

        #if this is a formula, we have to treat it specially
        for col in collist:
            val = self.model.getCellRecord(absrow, col)
            f=val #formula to copy
            i=1
            for r in rowlist:
                absr = self.get_AbsoluteRow(r)
                if Formula.isFormula(f):
                    newval = model.copyFormula(f, absr, col, offset=i)
                    model.setFormulaAt(newval, absr, col)
                else:
                    model.setValueAt(val, absr, col)
                #print 'setting', val, 'at row', r
                i+=1

        self.redrawTable()
        return

    def fill_across(self, collist, rowlist):
        """Fill across a row, or multiple rows"""
        model = self.model
        #row = self.currentrow
        #absrow  = self.get_AbsoluteRow(collist[0])
        frstcol = collist[0]
        collist.remove(frstcol)

        for row in rowlist:
            absr = self.get_AbsoluteRow(row)
            val = self.model.getCellRecord(absr, frstcol)
            f=val     #formula to copy
            i=1
            for c in collist:
                if Formula.isFormula(f):
                    newval = model.copyFormula(f, absr, c, offset=i, dim='x')
                    model.setFormulaAt(newval, absr, c)
                else:
                    model.setValueAt(val, absr, c)
                i+=1
        self.redrawTable()
        return

    def getSelectionValues(self):
        """Get values for current multiple cell selection"""
        if len(self.multiplerowlist) == 0 or len(self.multiplecollist) == 0:
            return None
        rows = self.multiplerowlist
        cols = self.multiplecollist
        model = self.model
        if len(rows)<1 or len(cols)<1:
            return None
        #if only one row selected we plot whole col
        if len(rows) == 1:
            rows = self.rowrange
        lists = []

        for c in cols:
            x=[]
            for r in rows:
                absr = self.get_AbsoluteRow(r)
                val = model.getValueAt(absr,c)
                if val == None or val == '':
                    continue
                x.append(val)
            lists.append(x)

        return lists

    def plot_Selected(self):
        """Plot the selected data using pylab - if possible"""
        from PylabPlot import pylabPlotter
        if not hasattr(self, 'pyplot'):
            self.pyplot = pylabPlotter()
        plotdata = []
        for p in self.getSelectionValues():
            x = []
            for d in p:
                try:
                    x.append(float(d))
                except:
                    pass
            plotdata.append(x)

        pltlabels = self.getplotlabels()
        #print pltlabels, plotdata
        if len(pltlabels) > 2:
            self.pyplot.setDataSeries(pltlabels)
            self.pyplot.showlegend = 1
        else:
            self.pyplot.setxlabel(pltlabels[0])
            self.pyplot.setylabel(pltlabels[1])
        self.pyplot.plotCurrent(data=plotdata)
        return

    def plotSetup(self):
        """Call pylab plot dialog setup, send data if we haven't already
            plotted"""
        from PylabPlot import pylabPlotter
        if not hasattr(self, 'pyplot'):
            self.pyplot = pylabPlotter()
        plotdata = self.getSelectionValues()

        if not self.pyplot.hasData() and plotdata != None:
            print 'has data'
            plotdata = self.getSelectionValues()
            pltlabels = self.getplotlabels()
            self.pyplot.setDataSeries(pltlabels)
            self.pyplot.plotSetup(plotdata)
        else:
            self.pyplot.plotSetup()

        return

    def getplotlabels(self):
        """Get labels for plot series from col labels"""
        pltlabels = []
        for col in self.multiplecollist:
            pltlabels.append(self.model.getColumnLabel(col))
        return pltlabels

    #--- Drawing stuff ---

    def draw_grid(self):
        """Draw the table grid lines"""
        self.delete('gridline','text')
        rows=len(self.rowrange)
        cols=self.cols
        w=self.cellwidth
        h=self.rowheight
        x_start=self.x_start
        y_start=self.y_start

        self.data={}
        x_pos=x_start

        if self.vertlines==1:
            for col in range(cols+1):
                #print x_pos
                x=self.col_positions[col]
                self.create_line(x,y_start,x,y_start+rows*h, tag='gridline',
                                     fill=self.grid_color, width=self.linewidth)

        if self.horizlines==1:
            for row in range(rows+1):
                y_pos=y_start+row*h
                self.create_line(x_start,y_pos,self.tablewidth,y_pos, tag='gridline',
                                    fill=self.grid_color, width=self.linewidth)
        return

    def draw_rowheader(self):
        """User has clicked to select a cell"""
        self.delete('rowheader')
        x_start=self.x_start
        y_start=self.y_start
        h=self.rowheight
        rowpos=0
        for row in self.rowrange:
            x1,y1,x2,y2 = self.getCellCoords(rowpos,0)
            self.create_rectangle(0,y1,x_start-2,y2,
                                      fill='gray75',
                                      outline='white',
                                      width=1,
                                      tag='rowheader')
            self.create_text(x_start/2,y1+h/2,
                                      text=row+1,
                                      fill='black',
                                      font=self.thefont,
                                      tag='rowheader')
            rowpos+=1
        return

    def draw_new_row(self):
        """For performance reasons, we can just draw new rows at the end of
           the table, without doing a redraw."""

        return

    def draw_selected_rect(self, row, col, color=None):
        """User has clicked to select a cell"""
        if col >= self.cols:
            return
        self.delete('currentrect')
        bg=self.selectedcolor
        if color == None:
            color = 'gray25'
        w=3
        x1,y1,x2,y2 = self.getCellCoords(row,col)
        rect = self.create_rectangle(x1+w/2,y1+w/2,x2-w/2,y2-w/2,
                                  fill=bg,
                                  outline=color,
                                  width=w,
                                  stipple='gray50',
                                  tag='currentrect')
        #self.lower('currentrect')
        #raise text above all
        self.lift('celltext'+str(col)+'_'+str(row))
        return

    def draw_rect(self, row, col, color=None, tag=None, delete=1):
        """Cell is colored"""
        if delete==1:
            self.delete('cellbg'+str(row)+str(col))
        if color==None or color==self.cellbackgr:
            return
        else:
            bg=color
        if tag==None:
            recttag='fillrect'
        else:
            recttag=tag
        w=1
        x1,y1,x2,y2 = self.getCellCoords(row,col)
        rect = self.create_rectangle(x1+w/2,y1+w/2,x2-w/2,y2-w/2,
                                  fill=bg,
                                  outline=bg,
                                  width=w,
                                  tag=(recttag,'cellbg'+str(row)+str(col)))
        self.lower(recttag)
        return

    def draw_cellentry(self, row, col, text=None):
        """When the user single/double clicks on a text/number cell, bring up entry window"""

        if self.editable == False:
            return
        absrow = self.get_AbsoluteRow(row)
        h=self.rowheight
        model=self.getModel()
        cellvalue = self.model.getCellRecord(absrow, col)
        if Formula.isFormula(cellvalue):
            return
        else:
            text = self.model.getValueAt(absrow, col)
        x1,y1,x2,y2 = self.getCellCoords(row,col)
        w=x2-x1
        #Draw an entry window
        txtvar = StringVar()
        txtvar.set(text)
        def callback(e):
            value = txtvar.get()
            if value == '=':

                #do a dialog that gets the formula into a text area
                #then they can click on the cells they want
                #when done the user presses ok and its entered into the cell
                self.cellentry.destroy()
                #its all done here..
                self.formula_Dialog(row, col)
                return

            coltype = self.model.getColumnType(col)
            if coltype == 'number':
                sta = self.check_data_entry(e)
                if sta == 1:
                    model.setValueAt(value,absrow,col)
            elif coltype == 'text':
                model.setValueAt(value,absrow,col)

            color = self.model.getColorAt(absrow,col,'fg')
            self.draw_Text(row, col, value, color)
            if e.keysym=='Return':
                self.delete('entry')
                #self.draw_rect(row, col)
                #self.gotonextCell(e)
            return
        
        self.cellentry=Entry(self.parentframe,width=20,
                        textvariable=txtvar,
                        bg=self.entrybackgr,
                        relief=FLAT,
                        takefocus=1,
                        font=self.thefont)
        self.cellentry.icursor(END)
        self.cellentry.bind('<Return>', callback)
        self.cellentry.bind('<KeyRelease>', callback)
        self.cellentry.focus_set()
        self.entrywin=self.create_window(x1+self.inset,y1+self.inset,
                                width=w-self.inset*2,height=h-self.inset*2,
                                window=self.cellentry,anchor='nw',
                                tag='entry')

        return

    def check_data_entry(self,event=None):
        """do validation checks on data entry in a widget"""
        #if user enters commas, change to points
        import re
        value=event.widget.get()
        if value!='':
            try:
                value=re.sub(',','.', value)
                value=float(value)

            except ValueError:
                event.widget.configure(bg='red')
                return 0
        elif value == '':
            return 1
        return 1

    def enterFormula(self, row, col):

        return

    def draw_Text(self, row, col, celltxt, fgcolor=None, align=None):
        """Draw the text inside a cell area"""
        self.delete('celltext'+str(col)+'_'+str(row))
        h=self.rowheight
        x1,y1,x2,y2 = self.getCellCoords(row,col)
        w=x2-x1
        wrap = False
        # If celltxt is a number then we make it a string
        import types
        if type(celltxt) is types.FloatType or type(celltxt) is types.IntType:
            celltxt=str(celltxt)
        #if cell width is less than x, print nothing
        if w<=15:
            return

        fontsize = self.fontsize
        scale = fontsize*1.2
        total = len(celltxt)
        
        if len(celltxt) > w/scale:           
            celltxt=celltxt[0:int(w/fontsize*1.2)-3]
        if len(celltxt) < total:
            celltxt=celltxt+'..'            
        if w < 25:
            celltxt = ''
        if fgcolor == None or fgcolor == "None":
            fgcolor = 'black'
        if align == None:
            align = 'center'
        elif align == 'w':
            x1 = x1-w/2+1

        #if celltxt is dict then we are drawing a hyperlink 
        if self.isLink(celltxt) == True:            
            haslink=0
            linktext=celltxt['text']
            if len(linktext) > w/scale or w<28:
                linktext=linktext[0:int(w/fontsize*1.2)-2]+'..'
            if celltxt['link']!=None and celltxt['link']!='':
                #f,s = self.thefont.split(' ')
                f,s = self.thefont
                linkfont = (f, s, 'underline')
                linkcolor='blue'
                haslink=1
            else:
                linkfont = self.thefont
                linkcolor=fgcolor

            rect = self.create_text(x1+w/2,y1+h/2,
                                      text=linktext,
                                      fill=linkcolor,
                                      font=linkfont,
                                      tag=('text','hlink','celltext'+str(col)+'_'+str(row)))
            if haslink == 1:
                self.tag_bind(rect, '<Double-Button-1>', self.check_hyperlink)

        #just normal text        
        else:           
            rect = self.create_text(x1+w/2,y1+h/2,
                                      text=celltxt,
                                      fill=fgcolor,
                                      font=self.thefont,
                                      anchor=align,                                      
                                      tag=('text','celltext'+str(col)+'_'+str(row)))
        return

    def isLink(self, cell):
        """Checks if cell is a hyperlink, without using isinstance"""
        try:
            if cell.has_key('link'):
                return True
        except:
            return False

    def drawSelectedRow(self):
        """Draw the highlight rect for the currently selected row"""
        self.delete('rowrect')
        row=self.currentrow
        x1,y1,x2,y2 = self.getCellCoords(row,0)
        x2=self.tablewidth
        rect = self.create_rectangle(x1,y1,x2,y2,
                                  fill=self.rowselectedcolor,
                                  outline=self.rowselectedcolor,
                                  tag='rowrect')
        self.lower('rowrect')
        self.lower('fillrect')
        return

    def drawSelectedCol(self, col=None, delete=1):
        """Draw an outline rect fot the current column selection"""
        if delete == 1:
            self.delete('colrect')
        if col == None:
            col=self.currentcol
        w=2
        x1,y1,x2,y2 = self.getCellCoords(0,col)
        y2 = self.rows * self.rowheight
        rect = self.create_rectangle(x1+w/2,y1+w/2,x2,y2+w/2,
                                     outline='blue',width=w,
                                     tag='colrect')


        return

    def drawMultipleRows(self, rowlist):
        """Draw more than one row selection"""
        self.delete('multiplesel')
        for r in rowlist:
            if r > self.rows-1:
                continue
            x1,y1,x2,y2 = self.getCellCoords(r,0)
            x2=self.tablewidth
            rect = self.create_rectangle(x1,y1,x2,y2,
                                      fill=self.multipleselectioncolor,
                                      outline=self.rowselectedcolor,
                                      tag=('multiplesel','rowrect'))
        self.lower('multiplesel')
        self.lower('fillrect')
        return

    def drawMultipleCells(self):
        """Draw an outline box for multiple cell selection"""
        self.delete('multicellrect')
        rows = self.multiplerowlist
        cols = self.multiplecollist
        w=2
        x1,y1,a,b = self.getCellCoords(rows[0],cols[0])
        c,d,x2,y2 = self.getCellCoords(rows[len(rows)-1],cols[len(cols)-1])
        rect = self.create_rectangle(x1+w/2,y1+w/2,x2,y2,
                             outline='blue',width=w,activefill='red',activestipple='gray25',
                             tag='multicellrect')

        return

    def draw_tooltip(self, row, col):
        """Draw a tooltip showing contents of cell"""

        absrow = self.get_AbsoluteRow(row)
        x1,y1,x2,y2 = self.getCellCoords(row,col)
        w=x2-x1
        text = self.model.getValueAt(absrow,col)
        if isinstance(text, dict):
            if text.has_key('link'):
                text = text['link']


        # If text is a number we make it a string
        import types
        if type(text) is types.FloatType or type is types.IntType:
            text=str(text)
        if text == NoneType or text == '' or len(str(text))<=3:
            return
        import tkFont
        sfont = tkFont.Font (family='Arial', size=12,weight='bold')
        obj=self.create_text(x1+w/1.5,y2,text=text,
                                anchor='w',
                                font=sfont,tag='tooltip')

        box = self.bbox(obj)
        x1=box[0]-1
        y1=box[1]-1
        x2=box[2]+1
        y2=box[3]+1

        rect = self.create_rectangle(x1+1,y1+1,x2+1,y2+1,tag='tooltip',fill='black')
        rect2 = self.create_rectangle(x1,y1,x2,y2,tag='tooltip',fill='lightyellow')
        self.lift(obj)
        return

    def setcellbackgr(self):
        clr = self.getaColor(self.cellbackgr)
        if clr != None:
            self.cellbackgr = clr
        return

    def setgrid_color(self):
        clr = self.getaColor(self.grid_color)
        if clr != None:
            self.grid_color = clr

        return

    def setrowselectedcolor(self):
        clr = self.getaColor(self.rowselectedcolor)
        if clr != None:
            self.rowselectedcolor = clr
        return

    def getaColor(self, oldcolor):
        import tkColorChooser
        ctuple, newcolor = tkColorChooser.askcolor(title='pick a color', initialcolor=oldcolor,
                                                   parent=self.parentframe)
        if ctuple == None:
            return None
        return str(newcolor)

    def removeColors(self):
        """Remove all color formatting"""
        self.model.resetcolors()
        return

    #--- Preferences stuff ---

    def showtablePrefs(self, prefs=None):
        """Show table options dialog using an instance of prefs"""
        #self.prefs = prefs
        if self.prefs == None:
            self.loadPrefs()
        self.prefswindow=Toplevel()
        self.prefswindow.geometry('+300+450')
        self.prefswindow.title('Preferences')

        frame1=Frame(self.prefswindow)
        frame1.pack(side=LEFT)
        frame2=Frame(self.prefswindow)
        frame2.pack()
        def close_prefsdialog():
            self.prefswindow.destroy()
        row=0
        Checkbutton(frame1, text="Show horizontal lines", variable=self.horizlinesvar,
                    onvalue=1, offvalue=0).grid(row=row,column=0, columnspan=2, sticky='news')
        row=row+1
        Checkbutton(frame1, text="Show vertical lines", variable=self.vertlinesvar,
                    onvalue=1, offvalue=0).grid(row=row,column=0, columnspan=2, sticky='news')
        row=row+1
        Checkbutton(frame1, text="Alternate Row Color", variable=self.alternaterowsvar,
                    onvalue=1, offvalue=0).grid(row=row,column=0, columnspan=2, sticky='news')
        row=row+1        
        lblrowheight=Label(frame1,text='Row Height:')
        lblrowheight.grid(row=row,column=0,padx=3,pady=2)
        rowheightentry=Scale(frame1,from_=12,to=50,resolution=1,orient='horizontal',
                            relief='ridge',variable=self.rowheightvar)
        rowheightentry.grid(row=row,column=1,padx=3,pady=2)
        row=row+1
        lblcellwidth=Label(frame1,text='Cell Width:')
        lblcellwidth.grid(row=row,column=0,padx=3,pady=2)
        cellwidthentry=Scale(frame1,from_=20,to=500,resolution=10,orient='horizontal',
                            relief='ridge',variable=self.cellwidthvar)
        cellwidthentry.grid(row=row,column=1,padx=3,pady=2)
        row=row+1

        lbllinewidth=Label(frame1,text='Line Width:')
        lbllinewidth.grid(row=row,column=0,padx=3,pady=2)
        linewidthentry=Scale(frame1,from_=0,to=10,resolution=1,orient='horizontal',
                            relief='ridge',variable=self.linewidthvar)
        linewidthentry.grid(row=row,column=1,padx=3,pady=2)
        row=row+1
        Checkbutton(frame1, text="Auto resize columns", variable=self.autoresizecolsvar,
                    onvalue=1, offvalue=0).grid(row=row,column=0, columnspan=2, sticky='news')
        row=row+1
        Checkbutton(frame1, text="Use paging", variable=self.usepagingvar,
                    onvalue=1, offvalue=0).grid(row=row,column=0, columnspan=2, sticky='news')
        row=row+1
        Label(frame1, text='Rows/page:').grid(row=row,column=0, sticky='news')
        Entry(frame1, textvariable=self.rowsperpagevar,bg='white',width=12,relief='groove').grid(row=row,column=1, pady=2,sticky='ns')
        row=row+1
        lblfont=Label(frame2,text='Cell Font:')
        lblfont.grid(row=row,column=0,padx=3,pady=2)
        fontentry_button=Menubutton(frame2,textvariable=self.celltextfontvar,
					relief=RAISED,width=16)
        fontentry_menu=Menu(fontentry_button,tearoff=0)
        fontentry_button['menu']=fontentry_menu
        #
        # Other fonts available
        #
        fts=['Arial','Courier','Verdana','Fixed','Times']
        for text in fts:
            fontentry_menu.add_radiobutton(label=text,
                                            variable=self.celltextfontvar,
                                            value=text,
                                            indicatoron=1)
        fontentry_button.grid(row=row,column=1, sticky='nes', padx=3,pady=2)
        row=row+1
        lblfontsize=Label(frame2,text='Text Size:')
        lblfontsize.grid(row=row,column=0,padx=3,pady=2)
        fontsizeentry=Scale(frame2,from_=8,to=30,resolution=1,orient='horizontal',
                            relief='ridge',variable=self.celltextsizevar)

        fontsizeentry.grid(row=row,column=1, sticky='wens',padx=3,pady=2)
        row=row+1
        #colors

        cellbackgrbutton = Button(frame2, text='table background', bg=self.cellbackgr,
                                relief='groove', command=self.setcellbackgr)
        cellbackgrbutton.grid(row=row,column=0,columnspan=2, sticky='news',padx=3,pady=2)
        row=row+1
        grid_colorbutton = Button(frame2, text='grid color', bg=self.grid_color,
                                foreground='black', highlightcolor='white',
                                relief='groove', command=self.setgrid_color)
        grid_colorbutton.grid(row=row,column=0,columnspan=2,  sticky='news',padx=3,pady=2)
        row=row+1
        rowselectedcolorbutton = Button(frame2, text='row highlight color', bg=self.rowselectedcolor,
                                foreground='black', highlightcolor='white',
                                relief='groove', command=self.setrowselectedcolor)
        rowselectedcolorbutton.grid(row=row,column=0,columnspan=2,  sticky='news',padx=3,pady=2)
        row=row+1

        # Data specific settings
        b = Button(frame2, text="Reset Colors", command=self.removeColors)
        b.grid(row=row,column=1,columnspan=2,sticky='news',padx=4,pady=4)

        frame=Frame(self.prefswindow)
        frame.pack()
        #
        # Apply Button
        #
        b = Button(frame, text="Apply Settings", command=self.applyPrefs)
        b.grid(row=row,column=1,columnspan=2,sticky='news',padx=4,pady=4)
        #
        # Close button
        #
        c=Button(frame,text='Close', command=close_prefsdialog)
        c.grid(row=row,column=0,sticky='news',padx=4,pady=4)
        self.prefswindow.focus_set()
        self.prefswindow.grab_set()
        self.prefswindow.wait_window()
        return self.prefswindow

    def loadPrefs(self, prefs=None):
        """Load table specific prefs from the prefs instance used
           if they are not present, create them."""

        if prefs==None:
            prefs=Preferences('Table',{'check_for_update':1})
        self.prefs = prefs
        defaultprefs = {'horizlines':self.horizlines, 'vertlines':self.vertlines,
                        'alternaterows':self.alternaterows,
                        'rowheight':self.rowheight,
                        'cellwidth':120,
                        'autoresizecols': 0,
                        'paging': 0, 'rowsperpage' : 50,
                        'celltextsize':11, 'celltextfont':'Arial',
                        'cellbackgr': self.cellbackgr, 'grid_color': self.grid_color,
                        'linewidth' : self.linewidth,
                        'rowselectedcolor': self.rowselectedcolor}

        for prop in defaultprefs.keys():
            try:
                self.prefs.get(prop);
            except:
                self.prefs.set(prop, defaultprefs[prop])
        #Create tkvars for dialog
        self.rowheightvar = IntVar()
        self.rowheightvar.set(self.prefs.get('rowheight'))
        self.rowheight = self.rowheightvar.get()
        self.cellwidthvar = IntVar()
        self.cellwidthvar.set(self.prefs.get('cellwidth'))
        self.cellwidth = self.cellwidthvar.get()
        self.linewidthvar = IntVar()
        self.linewidthvar.set(self.prefs.get('linewidth'))
        self.autoresizecolsvar = IntVar()
        self.autoresizecolsvar.set(self.prefs.get('autoresizecols'))
        self.horizlinesvar = IntVar()
        self.horizlinesvar.set(self.prefs.get('horizlines'))
        self.vertlinesvar = IntVar()
        self.vertlinesvar.set(self.prefs.get('vertlines'))
        self.alternaterowsvar = IntVar()
        self.alternaterowsvar.set(self.prefs.get('alternaterows'))
        self.usepagingvar = IntVar()
        self.usepagingvar.set(self.prefs.get('paging'))
        self.paging = self.usepagingvar.get()
        self.rowsperpagevar = StringVar()
        self.rowsperpagevar.set(self.prefs.get('rowsperpage'))
        self.celltextsizevar = IntVar()
        self.celltextsizevar.set(self.prefs.get('celltextsize'))
        self.celltextfontvar = StringVar()
        self.celltextfontvar.set(self.prefs.get('celltextfont'))
        self.cellbackgr = self.prefs.get('cellbackgr')
        self.grid_color = self.prefs.get('grid_color')
        self.rowselectedcolor = self.prefs.get('rowselectedcolor')        
        self.fontsize = self.celltextsizevar.get()
        self.thefont = (self.celltextfontvar.get(), self.celltextsizevar.get())
        return

    def savePrefs(self):
        """Save and set the prefs"""
        try:
            self.prefs.set('horizlines', self.horizlinesvar.get())
            self.horizlines = self.horizlinesvar.get()
            self.prefs.set('vertlines', self.vertlinesvar.get())
            self.vertlines = self.vertlinesvar.get()
            self.prefs.set('alternaterows', self.alternaterowsvar.get())
            self.alternaterows = self.alternaterowsvar.get()            
            self.prefs.set('rowheight', self.rowheightvar.get())
            self.rowheight = self.rowheightvar.get()
            self.prefs.set('cellwidth', self.cellwidthvar.get())
            self.cellwidth = self.cellwidthvar.get()
            self.prefs.set('linewidth', self.linewidthvar.get())
            self.linewidth = self.linewidthvar.get()
            self.prefs.set('autoresizecols', self.autoresizecolsvar.get())
            self.autoresizecols = self.autoresizecolsvar.get()
            self.paging = self.usepagingvar.get()
            self.prefs.set('paging', self.usepagingvar.get())
            self.rowsperpage = int(self.rowsperpagevar.get())
            self.prefs.set('rowsperpage', self.rowsperpagevar.get())
            self.prefs.set('celltextsize', self.celltextsizevar.get())
            self.prefs.set('celltextfont', self.celltextfontvar.get())
            self.prefs.set('cellbackgr', self.cellbackgr)
            self.prefs.set('grid_color', self.grid_color)
            self.prefs.set('rowselectedcolor', self.rowselectedcolor)
            self.thefont = (self.celltextfontvar.get(), self.celltextsizevar.get())          
            self.fontsize = self.celltextsizevar.get()
        except ValueError:
            pass
        self.prefs.save_prefs()

        return

    def applyPrefs(self):
        """Apply prefs to the table by redrawing"""
        self.savePrefs()
        self.redrawTable()
        return

    def AskForColorButton(self, frame, text, func):
        def SetColor():
            import tkColorChooser
            ctuple, variable = tkColorChooser.askcolor(title='pick a color',
                                                       initialcolor=self.cellbackgr)

            return
        bgcolorbutton = Button(frame, text=text,command=SetColor)
        return  bgcolorbutton


    def check_hyperlink(self,event=None):
        """Check if a hyperlink was clicked"""
        row = self.get_row_clicked(event)
        col = self.get_col_clicked(event)
        absrow = self.get_AbsoluteRow(row)
        recdata = self.model.getValueAt(absrow, col)
        try:
            link = recdata['link']
            import webbrowser
            webbrowser.open(link,autoraise=1)
        except:
            pass
        return

    def show_progressbar(self,message=None):
        """Show progress bar window for loading of data"""
        progress_win=Toplevel() # Open a new window
        progress_win.title("Please Wait")
        #progress_win.geometry('+%d+%d' %(self.parentframe.rootx+200,self.parentframe.rooty+200))
        #force on top
        progress_win.grab_set()
        progress_win.transient(self.parentframe)
        if message==None:
            message='Working'
        lbl = Label(progress_win,text=message,font='Arial 16')

        lbl.grid(row=0,column=0,columnspan=2,sticky='news',padx=6,pady=4)
        progrlbl = Label(progress_win,text='Progress:')
        progrlbl.grid(row=1,column=0,sticky='news',padx=2,pady=4)
        import ProgressBar
        self.bar = ProgressBar.ProgressBar(progress_win)
        self.bar.frame.grid(row=1,column=1,columnspan=2,padx=2,pady=4)

        return progress_win

    def exportTable(self, filename=None):
        """Do a simple export of the cell contents to csv"""
        from Tables_IO import TableExporter
        exporter = TableExporter()
        exporter.ExportTableData(self)
        return

    @classmethod
    def checkOSType(cls):
        """Check the OS we are in"""
        import os, string
        ostyp=''
        var_s=['OSTYPE','OS']
        for var in var_s:
            if os.environ.has_key(var):
                ostyp=string.lower(os.environ[var])

        ostyp=ostyp.lower()
        if ostyp.find('windows')!=-1:
            ostyp='windows'
        elif ostyp.find('darwin')!=-1 or ostyp.find('apple')!=-1:
            ostyp='mac'
        elif ostyp.find('linux')!=-1:
            ostyp='linux'
        else:
            ostyp='unknown'
            try:
                info=os.uname()
            except:
                pass
            ostyp=info[0].lower()
            if ostyp.find('darwin')!=-1:
                ostyp='mac'
        return ostyp


class ColumnHeader(Canvas):
    """Class that takes it's size and rendering from a parent table
        and column names from the table model."""

    def __init__(self, parent=None, table=None):
        Canvas.__init__(self, parent, bg='gray25', width=500, height=20)
        self.thefont='Arial 14'
        if table != None:
            self.table = table
            self.height = 20
            self.model = self.table.getModel()
            self.config(width=self.table.width)
            #self.colnames = self.model.columnNames
            self.columnlabels = self.model.columnlabels
            self.bind('<Button-1>',self.handle_left_click)
            self.bind("<ButtonRelease-1>", self.handle_left_release)
            self.bind('<B1-Motion>', self.handle_mouse_drag)
            self.bind('<Motion>', self.handle_mouse_move)
            self.bind('<Shift-Button-1>', self.handle_left_shift_click)
            if self.table.ostyp=='mac':
                #For mac we bind Shift, left-click to right click
                self.bind("<Button-2>", self.handle_right_click)
                self.bind('<Shift-Button-1>',self.handle_right_click)
            else:
                self.bind("<Button-3>", self.handle_right_click)
            self.thefont = self.table.thefont
        return

    def redraw(self):
        cols=self.model.getColumnCount()
        self.tablewidth=self.table.tablewidth
        self.configure(scrollregion=(0,0, self.table.tablewidth+self.table.x_start, self.height))
        self.delete('gridline','text')
        self.delete('rect')
        self.atdivider = None

        h=self.height
        x_start=self.table.x_start
        if cols == 0:
            return
        for col in range(cols):
            colname=self.model.columnNames[col]
            if not self.model.columnlabels.has_key(colname):
                self.model.columnlabels[colname]=colname
            collabel = self.model.columnlabels[colname]
            if self.model.columnwidths.has_key(colname):
                w=self.model.columnwidths[colname]
            else:
                w=self.table.cellwidth
            x=self.table.col_positions[col]

            if len(collabel)>w/10:
                collabel=collabel[0:int(w)/12]+'.'
            line = self.create_line(x, 0, x, h, tag=('gridline', 'vertline'),
                                 fill='white', width=2)

            self.create_text(x+w/2,h/2,
                                text=collabel,
                                fill='white',
                                font=self.thefont,
                                tag='text')


        x=self.table.col_positions[col+1]
        self.create_line(x,0, x,h, tag='gridline',
                        fill='white', width=2)

        return

    def handle_left_click(self,event):
        """Does cell selection when mouse is clicked on canvas"""
        self.delete('rect')
        self.table.delete('entry')
        self.table.delete('multicellrect')
        colclicked = self.table.get_col_clicked(event)
        #set all rows selected
        self.table.allrows = True
        self.table.setSelectedCol(colclicked)
        
        if self.atdivider == 1:
            return
        self.draw_rect(self.table.currentcol)
        #also draw a copy of the rect to be dragged
        self.draggedcol=None
        self.draw_rect(self.table.currentcol, tag='dragrect',
                        color='red', outline='white')
        if hasattr(self, 'rightmenu'):
            self.rightmenu.destroy()
        #finally, draw the selected col on the table
        self.table.drawSelectedCol()
        return

    def handle_left_release(self,event):
        """When mouse released implement resize or col move"""
        self.delete('dragrect')
        if self.atdivider == 1:
            #col = self.table.get_col_clicked(event)
            x=int(self.canvasx(event.x))
            col = self.table.currentcol
            x1,y1,x2,y2 = self.table.getCellCoords(0,col)
            newwidth=x - x1
            if newwidth < 5:
                newwidth=5
            self.table.resize_Column(col, newwidth)
            self.table.delete('resizeline')
            self.delete('resizeline')
            self.delete('resizesymbol')
            self.atdivider = 0
            return
        self.delete('resizesymbol')
        #move column
        if self.draggedcol != None and self.table.currentcol != self.draggedcol:
            self.model.moveColumn(self.table.currentcol, self.draggedcol)
            self.table.setSelectedCol(self.draggedcol)
            self.table.redrawTable()
            self.table.drawSelectedCol(self.table.currentcol)
            self.draw_rect(self.table.currentcol)

        return

    def handle_mouse_drag(self, event):
        """Handle column drag, will be either to move cols or resize"""
        x=int(self.canvasx(event.x))
        if self.atdivider == 1:
            self.table.delete('resizeline')
            self.delete('resizeline')
            self.table.create_line(x, 0, x, self.table.rowheight*self.table.rows,
                                width=2, fill='gray', tag='resizeline')
            self.create_line(x, 0, x, self.height,
                                width=2, fill='gray', tag='resizeline')
            return
        else:
            w = self.table.cellwidth
            self.draggedcol = self.table.get_col_clicked(event)
            x1, y1, x2, y2 = self.coords('dragrect')
            x=int(self.canvasx(event.x))
            y = self.canvasy(event.y)
            self.move('dragrect', x-x1-w/2, 0)

        return

    def within(self, val, l, d):
        """Utility funtion to see if val is within d of any
            items in the list l"""
        for v in l:
            if abs(val-v) <= d:
                return 1

        return 0

    def handle_mouse_move(self, event):
        """Handle mouse moved in header, if near divider draw resize symbol"""
        self.delete('resizesymbol')
        w=self.table.cellwidth
        h=self.height
        x_start=self.table.x_start
        #x = event.x
        x=int(self.canvasx(event.x))
        if x > self.tablewidth+w:
            return
        #if event x is within x pixels of divider, draw resize symbol
        if x!=x_start and self.within(x, self.table.col_positions, 4):
            col = self.table.get_col_clicked(event)
            if col == None:
                return
            self.draw_resize_symbol(col)
            self.atdivider = 1
        else:
            self.atdivider = 0
        return

    def handle_right_click(self, event):
        """respond to a right click"""
        self.handle_left_click(event)
        self.rightmenu = self.popupMenu(event)
        return

    def handle_right_release(self, event):
        self.rightmenu.destroy()
        return

    def handle_left_shift_click(self, event):
        """Handle shift click, for selecting multiple cols"""
        self.table.delete('colrect')
        self.delete('rect')
        currcol = self.table.currentcol
        colclicked = self.table.get_col_clicked(event)
        if colclicked > currcol:
            self.table.multiplecollist = range(currcol, colclicked+1)
        elif colclicked < currcol:
            self.table.multiplecollist = range(colclicked, currcol+1)
        else:
            return

        #print self.table.multiplecollist
        for c in self.table.multiplecollist:
            self.draw_rect(c, delete=0)
            self.table.drawSelectedCol(c, delete=0)
        return

    def popupMenu(self, event):
        """Add left and right click behaviour for column header"""
        colname = self.model.columnNames[self.table.currentcol]
        collabel = self.model.columnlabels[colname]
        popupmenu = Menu(self, tearoff = 0)
        def popupFocusOut(event):
            popupmenu.unpost()
        popupmenu.add_command(label="Rename Column", command=self.relabel_Column)
        popupmenu.add_command(label="Sort by "+ collabel, command=self.table.sortTable)
        popupmenu.add_command(label="Sort by "+ collabel +' (descending)', command=lambda : self.table.sortTable(reverse=1))
        popupmenu.add_command(label="Delete This Column", command=self.table.delete_Column)
        popupmenu.add_command(label="Add New Column", command=self.table.add_Column)

        popupmenu.bind("<FocusOut>", popupFocusOut)
        #self.bind("<Button-3>", popupFocusOut)
        popupmenu.focus_set()
        popupmenu.post(event.x_root, event.y_root)
        return popupmenu

    def relabel_Column(self):
        col=self.table.currentcol
        ans = tkSimpleDialog.askstring("New column name?", "Enter new name:")
        if ans !=None:
            if ans == '':
                tkMessageBox.showwarning("Error", "Name should not be blank.")
                return
            else:
                self.model.relabel_Column(col, ans)
                self.redraw()
        return

    def draw_resize_symbol(self, col):
        """Draw a symbol to show that col can be resized when mouse here"""
        self.delete('resizesymbol')
        w=self.table.cellwidth
        h=self.height
        #if x_pos > self.tablewidth:
        #    return
        wdth=1
        hfac1=0.2
        hfac2=0.4
        x_start=self.table.x_start
        x1,y1,x2,y2 = self.table.getCellCoords(0,col)

        self.create_polygon(x2-3,h/4, x2-10,h/2, x2-3,h*3/4, tag='resizesymbol',
            fill='white', outline='gray', width=wdth)
        self.create_polygon(x2+2,h/4, x2+10,h/2, x2+2,h*3/4, tag='resizesymbol',
            fill='white', outline='gray', width=wdth)


        return

    def draw_rect(self,col, tag=None, color=None, outline=None, delete=1):
        """User has clicked to select a col"""
        if tag==None:
            tag='rect'
        if color==None:
            color='#0099CC'
        if outline==None:
            outline='gray25'
        if delete == 1:
            self.delete(tag)
        w=2
        x1,y1,x2,y2 = self.table.getCellCoords(0,col)
        rect = self.create_rectangle(x1,y1-w,x2,self.height,
                                  fill=color,
                                  outline=outline,
                                  width=w,
                                  stipple='gray50',
                                  tag=tag)
        self.lower(tag)
        return

class RowHeader(Canvas):
    """Class that displays the row headings on the table
       takes it's size and rendering from the parent table
       This also handles row/record selection as opposed to cell
       selection"""
    def __init__(self, parent=None, table=None):
        Canvas.__init__(self, parent, bg='gray75', width=40, height=None )

        if table != None:
            self.table = table
            self.width = 40
            self.x_start = 40
            self.inset = 1
            #self.config(width=self.width)
            self.config(height = self.table.height)
            self.startrow = self.endrow = None
            self.model = self.table.getModel()
            self.bind('<Button-1>',self.handle_left_click)
            self.bind("<ButtonRelease-1>", self.handle_left_release)
            self.bind("<Control-Button-1>", self.handle_left_ctrl_click)
            self.bind('<Button-3>',self.handle_right_click)
            self.bind('<B1-Motion>', self.handle_mouse_drag)
            #self.bind('<Shift-Button-1>', self.handle_left_shift_click)
        return

    def redraw(self, paging = 0):
        """Redraw row header"""
        if paging == 1:
            self.height = self.table.rowheight * self.table.rowsperpage+10
        else:
            self.height = self.table.rowheight * self.table.rows+10
     
        self.configure(scrollregion=(0,0, self.width, self.height))
        self.delete('rowheader','text')
        self.delete('rect')

        w=1
        x_start=self.x_start
        y_start=self.table.y_start
        h = self.table.rowheight
        rowpos=0
        for row in self.table.rowrange:
            x1,y1,x2,y2 = self.table.getCellCoords(rowpos,0)
            self.create_rectangle(0,y1,x_start-w,y2,
                                      fill='gray75',
                                      outline='white',
                                      width=w,
                                      tag='rowheader')
            self.create_text(x_start/2,y1+h/2,
                                      text=row+1,
                                      fill='black',
                                      font=self.table.thefont,
                                      tag='text')
            rowpos+=1
        return

    def clearSelected(self):
        self.delete('rect')
        return

    def handle_left_click(self, event):
        rowclicked = self.table.get_row_clicked(event)
        self.startrow = rowclicked
        if 0 <= rowclicked < self.table.rows:
            self.delete('rect')
            self.table.delete('entry')
            self.table.delete('multicellrect')
            #set row selected
            self.table.setSelectedRow(rowclicked)
            self.table.drawSelectedRow()
            self.drawSelectedRows(self.table.currentrow)
        return

    def handle_left_release(self,event):

        return

    def handle_left_ctrl_click(self, event):
        """Handle ctrl clicks - for multiple row selections"""
        rowclicked = self.table.get_row_clicked(event)
        multirowlist = self.table.multiplerowlist
        if 0 <= rowclicked < self.table.rows:
            if rowclicked not in multirowlist:
                multirowlist.append(rowclicked)
            else:
                multirowlist.remove(rowclicked)
            self.table.drawMultipleRows(multirowlist)
            self.drawSelectedRows(multirowlist)
        return

    def handle_right_click(self,event):

        return

    def handle_mouse_drag(self, event):
        """Handle mouse drag for mult row selection"""
        rowover = self.table.get_row_clicked(event)
        colover = self.table.get_col_clicked(event)
        if colover == None or rowover == None:
            return
        if self.table.check_PageView(rowover) == 1:
            return

    def handle_mouse_drag(self, event):
        """Handle mouse moved with button held down, multiple selections"""
        if hasattr(self, 'cellentry'):
            self.cellentry.destroy()
        rowover = self.table.get_row_clicked(event)
        colover = self.table.get_col_clicked(event)
        if rowover == None or self.table.check_PageView(rowover) == 1:
            return
        if rowover >= self.table.rows or self.startrow > self.table.rows:
            return
        else:
            self.endrow = rowover
        #draw the selected rows
        if self.endrow != self.startrow:
            if self.endrow < self.startrow:
                rowlist=range(self.endrow, self.startrow+1)
            else:
                rowlist=range(self.startrow, self.endrow+1)
            self.drawSelectedRows(rowlist)
            self.table.multiplerowlist = rowlist
            self.table.drawMultipleRows(rowlist)
        else:
            self.table.multiplerowlist = []
            self.table.multiplerowlist.append(rowover)
            self.drawSelectedRows(rowover)
            self.table.drawMultipleRows(self.table.multiplerowlist)
        return

    def drawSelectedRows(self, rows=None):
        """Draw selected rows, accepts a list or integer"""
        self.delete('rect')
        if type(rows) is not ListType:
            rowlist=[]
            rowlist.append(rows)
        else:
           rowlist = rows
        for r in rowlist:
            #print r
            self.draw_rect(r, delete=0)
        return

    def draw_rect(self, row=None, tag=None, color=None, outline=None, delete=1):
        """Draw a rect representing row selection"""
        if tag==None:
            tag='rect'
        if color==None:
            color='#0099CC'
        if outline==None:
            outline='gray25'
        if delete == 1:
            self.delete(tag)
        w=0
        i = self.inset
        x1,y1,x2,y2 = self.table.getCellCoords(row, 0)
        rect = self.create_rectangle(0+i,y1+i,self.x_start-i,y2,
                                      fill=color,
                                      outline=outline,
                                      width=w,
                                      tag=tag)
        self.lift('text')
        return

class AutoScrollbar(Scrollbar):
    # a scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        Scrollbar.set(self, lo, hi)
    def pack(self, **kw):
        raise TclError, "cannot use pack with this widget"
    def place(self, **kw):
        raise TclError, "cannot use place with this widget"


class SimpleTableDialog(tkSimpleDialog.Dialog):
    """Simple dialog to get data for new cols and rows"""

    def __init__(self, parent, title=None, table=None):
        if table != None:
            self.items = table.getModel().getDefaultTypes()
        else:
            self.items=['text','number']
        tkSimpleDialog.Dialog.__init__(self, parent, title)


    def body(self, master):

        Label(master, text="Column Type:").grid(row=0)
        Label(master, text="Name:").grid(row=1)
        self.v1=StringVar()
        self.v1.set('text')
        self.b1 = Menubutton(master,textvariable=self.v1,relief=RAISED)
        self.menu=Menu(self.b1,tearoff=0)
        self.b1['menu']=self.menu

        for option in self.items:
            self.menu.add_radiobutton(label=option,
                                          variable=self.v1,
                                          value=option,
                                          indicatoron=1)
        self.e2 = Entry(master)

        self.b1.grid(row=0, column=1,padx=2,pady=2,sticky='news')
        self.e2.grid(row=1, column=1,padx=2,pady=2,sticky='news')
        return self.b1 # initial focus

    def apply(self):
        first = self.v1.get()
        second = self.e2.get()
        self.result = first, second
        return

class RecordViewDialog(tkSimpleDialog.Dialog):
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
        tkSimpleDialog.Dialog.__init__(self, parent, title)
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
        Entry(master, textvariable=self.fieldvars['Name'],
                relief=GROOVE,bg='yellow').grid(row=0,column=1,padx=2,pady=2,sticky='news')
        i=1
        for col in cols:
            self.fieldvars[col] = StringVar()
            if self.recdata.has_key(col):
                val = self.recdata[col]
                self.fieldvars[col].set(val)
            self.fieldnames[col] = Label(master, text=col).grid(row=i,column=0,padx=2,pady=2,sticky='news')
            ent = Entry(master, textvariable=self.fieldvars[col], relief=GROOVE,bg='white')
            ent.grid(row=i,column=1,padx=2,pady=2,sticky='news')
            if not type(self.recdata[col]) is StringType:
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
            if not self.fieldvars.has_key(colname):
                continue
            val = self.fieldvars[colname].get()            
            model.setValueAt(val, absrow, col)
            #print 'changed field', colname
        
        self.table.redrawTable()
        return
