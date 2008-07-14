#!/usr/bin/env python
"""
    Created January 2008
    TableCanvas Class
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

from Tkinter import *
from Prefs import Preferences
import tkFileDialog, tkMessageBox, tkSimpleDialog
import math

class TableCanvas(Canvas):    
    """A tkinter class for providing table functionality"""
    
    def __init__(self, parent=None, model=None):        
        Canvas.__init__(self, parent, bg='#9999CC',
                         width=600, height=400,
                         relief=GROOVE,
                         scrollregion=(0,0,600,600)) 
        self.parentframe = parent
        #get platform into a variable
        import platform
        self.platform=platform.system()
        print self.platform
        self.model = model
        self.width=800
        self.height=600 
        self.cellwidth=150                         
        self.rowheight=24
        self.horizlines=1
        self.vertlines=1
        self.autoresizecols = 0
        self.paging = 0
        self.rowsperpage = 10
        self.currentpage = None
        self.navFrame = None
        self.inset=2
        self.x_start=40
        self.y_start=1
        self.linewidth=1.0    
        self.thefont = "Arial 12"
        self.cellbackgr = '#9999CC'
        self.entrybackgr = 'white'
        self.grid_color = 'gray50'
        self.selectedcolor = 'yellow'
        self.rowselectedcolor = '#CCCCFF'
        self.multipleselectioncolor = '#ECD672'
        self.currentrow = 0           
        self.currentcol = 0
        self.sortcol = None
        self.reverseorder = 0
        #for multiple selections
        self.startrow = self.endrow = None
        self.multiplerowlist=[]
        self.col_positions=[]       #record current column grid positions
        
        if self.model!=None:
            self.rows=self.model.getRowCount()
            self.cols=self.model.getColumnCount()
        else:    
            self.rows=30
            self.cols=8
        self.tablewidth=(self.cellwidth)*self.cols            
        self.tableheader = ColumnHeader(self.parentframe, self) 
        self.do_bindings()
        #
        #column specific actions, define for every column type in the model
        #when you add a column type you should edit this dict
                 
        self.columnactions = {'text' : {"Edit":  'draw_cellentry' },
                              'number' : {"Edit": 'draw_cellentry' }}
        #
        #print self.columnactions
        #print 'Initialised tablecanvas'
        
        return
    
    def mouse_wheel(self, event):
        """Handle mouse wheel scroll for windows"""
        if event.num == 5 or event.delta == -120:
            event.widget.yview_scroll(1, UNITS)        
        if event.num == 4 or event.delta == 120:
            event.widget.yview_scroll(-1, UNITS)
        return
        
    def do_bindings(self):
        """Bind keys and mouse clicks, this can be overriden"""
        self.bind("<Button-1>",self.handle_left_click)
        self.bind("<Double-Button-1>",self.handle_double_click)
        self.bind("<Control-Button-1>", self.handle_left_ctrl_click)
        self.bind("<Shift-Button-1>", self.handle_left_shift_click)
        
        self.bind("<ButtonRelease-1>", self.handle_left_release)
        self.bind("<Button-3>", self.handle_right_click)
        self.bind('<B1-Motion>', self.handle_mouse_drag)         
        self.bind('<Motion>', self.handle_motion) 
        
        self.bind("<Control-x>", self.delete_Row)
        self.bind("<Control-n>", self.add_Row)
        self.bind("<Delete>", self.delete_Cell)
        
        if not hasattr(self,'parentapp'):
            self.parentapp = self.parentframe
        self.parentapp.master.bind("<Right>", self.handle_arrow_keys)
        self.parentapp.master.bind("<Left>", self.handle_arrow_keys)
        self.parentapp.master.bind("<Up>", self.handle_arrow_keys)
        self.parentapp.master.bind("<Down>", self.handle_arrow_keys)
        self.parentapp.master.bind("<KP_8>", self.handle_arrow_keys)
        
        self.parentframe.master.bind("<Return>", self.handle_arrow_keys)
        self.parentframe.master.bind("<Tab>", self.handle_arrow_keys)
        if 'windows' in self.platform:
            self.bind("<MouseWheel>", self.mouse_wheel)            
        self.bind('<Button-4>', lambda event: event.widget.yview_scroll(-1, UNITS))
        self.bind('<Button-5>', lambda event: event.widget.yview_scroll(1, UNITS)) 
        return
        
    def getModel(self):
        """Get the current table model"""        
        return self.model
    
    def setModel(self,model):
        self.model = model
        return
    
    def createTableFrame(self):
        """Adds column header and scrollbars and combines them with
           the current table adding all to the master frame provided in constructor.
           Table is then redrawn."""

        #Add the table and header to the frame  
        self.Yscrollbar=Scrollbar (self.parentframe,orient=VERTICAL,command=self.yview)
        self.Yscrollbar.grid(row=1,column=1,rowspan=1,sticky='news',pady=0,ipady=0)
        self.Xscrollbar=Scrollbar (self.parentframe,orient=HORIZONTAL,command=self.set_xviews)
        self.Xscrollbar.grid(row=2,column=0,columnspan=1,sticky='news')
        self['xscrollcommand']=self.Xscrollbar.set
        self['yscrollcommand']=self.Yscrollbar.set
        self.tableheader['xscrollcommand']=self.Xscrollbar.set
        self.parentframe.rowconfigure(1,weight=1)
        self.parentframe.columnconfigure(0,weight=1)
        #self.parentframe.pack(fill=BOTH, expand=YES)        
        self.savePrefs()
        self.tableheader.grid(row=0,column=0,rowspan=1,sticky='news',pady=0,ipady=0)
        self.grid(row=1,column=0,rowspan=1,sticky='news',pady=0,ipady=0)
        self.redrawTable()
        self.parentframe.bind("<Configure>", self.resizeTable)
        #self.table.xview("moveto", 0)
        #self.table.yview("moveto", 0)
              
        return
        
    def redrawTable(self, event=None):
        """Draw the table from scratch based on it's model data""" 
        import time
        #print 'redrawing',time.time()  
        model = self.model
        self.rows=self.model.getRowCount()
        self.cols=self.model.getColumnCount()                      
        self.tablewidth=(self.cellwidth)*self.cols
        self.configure(bg=self.cellbackgr)
        #determine col positions for first time
        self.set_colPositions()
        #set sort order
        if self.sortcol != None:
            self.model.setSortOrder(self.sortcol, self.reverseorder)

        #check if large no. of records and switch to paging view
        if self.paging == 0 and self.rows >= 1000:
            self.paging = 1
        #if using paging, we only want to display the current page..
        if self.paging == 1:
            self.numpages = int(math.ceil(self.rows/self.rowsperpage))
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
            #print 'self.rowrange',self.rowrange
            self.configure(scrollregion=(0,0, self.tablewidth+self.x_start, self.rowheight*self.rowsperpage+10))
        else:
            self.rowrange = range(0,self.rows)            
            self.configure(scrollregion=(0,0, self.tablewidth+self.x_start, self.rowheight*self.rows+10))
            
        self.draw_grid() 
        self.update_idletasks() 
        self.draw_rowheader()
        self.tableheader.redraw()
        align=None
        self.delete('fillrect')
                        
        #now draw model data in cells  
        rowpos=0
        if self.model!=None:            
            for row in self.rowrange:
                for col in range(self.cols):  
                    if model.getColumnName(col) == 'Name':  
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
        self.drawSelectedRow()
        self.draw_selected_rect(self.currentrow, self.currentcol)  
        if len(self.multiplerowlist)>1:
            self.drawMultipleRows(self.multiplerowlist)
        
        return   

    def resizeTable(self, event):
        """Respond to a resize event - redraws table"""
        if self.autoresizecols == 1 and event != None:            
            self.cellwidth = (event.width - self.x_start - 24) / self.cols 
            #print 'cellwidth', self.cellwidth  
            self.redrawTable()
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
        self.sortcol = self.currentcol
        self.reverseorder = reverse
        self.redrawTable() 
        return
    
    def set_xviews(self,*args):
        """Set the xview of table and header"""
        apply(self.xview,args)
        apply(self.tableheader.xview,args)
        return
    
    def drawNavFrame(self):
        """Draw the frame for selecting pages when paging is on"""
        print 'adding page frame'
        import Table_images
        self.navFrame = Frame(self.parentframe)
        self.navFrame.grid(row=4,column=0,columnspan=1,sticky='news',padx=1,pady=1,ipady=1)        
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
            b.pack(side=LEFT)                
        Label(self.navFrame,text='Page '+str(self.currentpage+1)+' of '+ str(self.numpages+1),fg='white',
                  bg='#3366CC',relief=SUNKEN).pack(side=LEFT,ipadx=2,ipady=2,padx=4)
        Label(self.navFrame,text='Goto Record:').pack(side=LEFT,padx=3)
        self.gotorecordvar = StringVar()
        Entry(self.navFrame,textvariable=self.gotorecordvar,
                  width=8,bg='white').pack(side=LEFT,ipady=3,padx=2)
        Label(self.navFrame,text=str(self.rows)+' records').pack(side=LEFT,padx=3)
        Button(self.navFrame,text='Normal View',command=self.paging_Off,
                   bg='#99CCCC',relief=GROOVE).pack(side=LEFT,padx=3)
        return

    def paging_Off(self):
        self.rows=self.model.getRowCount()
        if self.rows >= 1000:
            tkMessageBox.showwarning("Warning",
                                     "This table has over 1000 rows.\n You should stay in page view.",
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
        self.currentpage = self.numpages
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
        if self.currentpage < self.numpages: 
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
                #print coltype, newname
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
            n = tkMessageBox.askyesno("Delete",
                                      "Delete Selected Records?",
                                      parent=self.parentframe) 
            if n:            
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

    def delete_Cell(self):
        """Clear the cell contents"""
        self.model.deleteCellRecord(self.currentrow,self.currentcol)
        self.redrawTable()
        return
    
    def autoAdd_Rows(self, numrows=None):
        """Automatically add x number of records"""
        if numrows == None:
            numrows = tkSimpleDialog.askinteger("Auto add rows.",
                                                "How many empty rows?",
                                                parent=self.parentframe)
        
        if numrows != None:         
            for rec in range(numrows):
                recname = str(rec)
                self.model.addRow()
        self.redrawTable()         
        return
        
    def autoAdd_Columns(self, numcols=None):
        """Automatically add x number of records"""
        if numcols == None:
            numcols = tkSimpleDialog.askinteger("Auto add rows.",
                                                "How many empty columns?",
                                                parent=self.parentframe)
        import string
        alphabet = string.lowercase[:26]
        currcols=self.model.getColumnCount()
        #find where to start
        if currcols <= 25:
            i=currcols-1
            j=0
        else:
            i=int(currcols%25)
            j=int(round(currcols/25,1))     
        
        for x in range(numcols):
            if i >= len(alphabet):
                i=0
                j=j+1
            name = alphabet[i]+str(j)    
            if name in self.model.columnNames:
                pass                
            else:
                self.model.addColumn(name) 
            i=i+1    
        self.parentframe.configure(width=self.width)
        self.redrawTable()         
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
                        self.lift('celltext'+str(row)+str(col))
                        #add row/col to foundlist
                        self.foundlist.append(cell)
                        #need to scroll to centre the cell here..
                        x,y = self.getCanvasPos(row, col)                         
                        self.xview('moveto', x)
                        self.yview('moveto', y)
                        return row, col
        if found==0:
            self.delete('searchrect')
            print 'nothing found'     
            return None
        
    def resize_Column(self, col, width):
        """Resize a column by dragging"""
        print 'resizing column', col
        #recalculate all col positions..              
        colname=self.model.getColumnName(col)    
        self.model.columnwidths[colname]=width 
        self.set_colPositions()      
        self.redrawTable()        
        return
      
    def get_currentRecord(self):
        """Get the currently selected record"""
        rec = self.model.getRecordAtRow(self.currentrow)
        return rec
        
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
        """Set currently selected row"""   
        self.currentrow = row
        return
        
    def set_selected_col(self, col):
        """Set currently selected column"""
        self.currentcol = col
        return 
        
    def getSelectedRow(self):
        """Get currently selected row"""
        return self.currentrow   
        
    def getSelectedColumn(self):
        """Get currently selected column"""
        return self.currentcol
        
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
        x1,y1,x2,y2 = self.getCellCoords(row,col)        
        cx=float(x1)/self.tablewidth
        cy=float(y1)/(self.rows*self.rowheight)
        print cx,cy
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
        if hasattr(self, 'cellentry'):
            self.cellentry.destroy()
        #ensure popup menus are removed if present
        if hasattr(self, 'rightmenu'):
            self.rightmenu.destroy()        
        if hasattr(self.tableheader, 'rightmenu'):
            self.tableheader.rightmenu.destroy()           
        rowclicked = self.get_row_clicked(event)
        colclicked = self.get_col_clicked(event)
        if self.check_PageView(rowclicked) == 1:
            return

        self.startrow = rowclicked 
        self.endrow = rowclicked 
        #reset multiple selection list
        self.multiplerowlist=[]
        self.multiplerowlist.append(rowclicked)
        if 0 <= rowclicked < self.rows and 0 <= colclicked < self.cols:
            self.setSelectedRow(rowclicked)
            self.set_selected_col(colclicked)
            self.draw_selected_rect(self.currentrow, self.currentcol)
            self.drawSelectedRow()
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
            #print self.multiplerowlist
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
        if self.check_PageView(rowover) == 1:
            return
        if rowover > self.rows or self.startrow > self.rows: #or 0 > colover > self.cols:
            #print rowover
            return
        else:
            self.endrow = rowover
        #draw the selected rows    
        if self.endrow != self.startrow:
            if self.endrow < self.startrow:                
                self.multiplerowlist=range(self.endrow, self.startrow+1)
                self.drawMultipleRows(self.multiplerowlist)
            else:
                self.multiplerowlist=range(self.startrow, self.endrow+1)
                self.drawMultipleRows(self.multiplerowlist)
        else:
            self.delete('multiplesel')
        #print self.multiplerowlist    
        return
     
    def handle_arrow_keys(self, event):
        """Handle arrow keys press"""
        print event.keysym
        row = self.get_row_clicked(event)
        col = self.get_col_clicked(event) 
        #if 0 <= row < self.rows or 0 <= col < self.cols:
        #    return
        if event.keysym == 'Up':
            if self.currentrow == 0:
                return
            else:    
                self.currentrow  = self.currentrow -1                
        elif event.keysym == 'Down':
            if self.currentrow >= self.rows-1:
                return
            else: 
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
        self.draw_cellentry(self.currentrow, self.currentcol)
        return        
        
    def handle_right_click(self, event):
        """respond to a right click"""
        self.delete('tooltip')
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
        if len(self.multiplerowlist) > 1:
            if rowclicked in self.multiplerowlist:
                self.rightmenu = self.popupMenu(event, self.multiplerowlist)
        else:            
            if 0 <= rowclicked < self.rows and 0 <= colclicked < self.cols:
                self.setSelectedRow(rowclicked)
                self.set_selected_col(colclicked)
                self.draw_selected_rect(self.currentrow, self.currentcol)
                self.drawSelectedRow()          
            if self.isInsideTable(event.x,event.y) == 1: 
                self.rightmenu = self.popupMenu(event)
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
        
        
    # --- Some cell specific actions here ---
    
    def setcellColor(self, row, col=None, newColor=None, key=None):
        """Set the cell color and save it in the model color"""
        model = self.getModel()
        absrow = self.get_AbsoluteRow(row)
        if newColor == None:
            import tkColorChooser
            ctuple, newColor = tkColorChooser.askcolor(title='pick a color')
            if newColor == None:
                return
            #print ctuple, newColor
        def setcolor(row, col):
            model.setColorAt(absrow, col, newColor, key)
            text = model.getValueAt(absrow,col)
            #redraw the cell text or fill
            if key=='fg':
                self.draw_Text(row,col, text, fgcolor=newColor)
            elif key=='bg':  
                self.draw_rect(row,col, color=newColor)
        # col is none, do all cols
        if col == None:
            for col in range(self.cols):
                setcolor(row, col)
        else:    
            setcolor(row, col)
        return
        
    def setcellColors(self, rows, key):
        """Color mutliple rows"""
        import tkColorChooser
        ctuple, newColor = tkColorChooser.askcolor(title='pick a color')
        if newColor == None:
            return
        for r in rows:
            self.setcellColor(r, None, newColor, key)
        return
    
    def popupMenu(self, event, rows=None, outside=None):
        """Add left and right click behaviour for canvas, should not have to override
            this function, it will take its values from defined dicts in constructor"""
        if outside == None: 
            row = self.get_row_clicked(event)
            col = self.get_col_clicked(event)
            coltype = self.model.getColumnType(col)
        popupmenu = Menu(self, tearoff = 0)  
        def popupFocusOut(event):
            popupmenu.unpost()

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
            defaultactions={"Set Fill Color" : lambda : self.setcellColor(row,col,key='bg') if rows==None else self.setcellColors(rows, key='bg'),
                            "Set Text Color" : lambda : self.setcellColor(row,col,key='fg') if rows==None else self.setcellColors(rows, key='fg'),
                            "Fill Down" : lambda : self.fill_down(rows),
                            "Clear Data" : self.delete_Cell,
                            "Show Prefs" : self.showtablePrefs}            
            for action in defaultactions.keys():                
                if action == 'Fill Down' and rows == None:
                    pass
                else:
                    popupmenu.add_command(label=action, command=defaultactions[action])                
            return
                                     
        #if outside table, just show general items    
        if outside == 1:            
            popupmenu.add_command(label="Show Prefs", command= self.showtablePrefs)
            popupmenu.add_command(label="Export Table", command= self.exportTable)
        else:
            if self.columnactions.has_key(coltype):  
                add_commands(coltype) 
            add_defaultcommands()
            
        popupmenu.bind("<FocusOut>", popupFocusOut)  
        popupmenu.focus_set()
        popupmenu.post(event.x_root, event.y_root)  
        return popupmenu

    # --- spreadsheet type functions ---
    
    def fill_down(self, rowlist):
        """Fill down a column"""
        model = self.model
        col = self.currentcol 
        absrow  = self.get_AbsoluteRow(rowlist[0])
        val = model.getValueAt(absrow,col)        
        for r in rowlist: 
            absr=self.get_AbsoluteRow(r)
            print r, absr
            model.setValueAt(val, absr, col)
            #print 'setting', val, 'at row', r 
        self.redrawTable()    
        return
    
    def fill_across(self):
        """Fill across a row"""
        
        return
    
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

    def draw_selected_rect(self, row, col):
        """User has clicked to select a cell"""
        self.delete('currentrect')
        bg=self.selectedcolor

        w=3
        x1,y1,x2,y2 = self.getCellCoords(row,col)
        rect = self.create_rectangle(x1+w/2,y1+w/2,x2-w/2,y2-w/2,
                                  fill=bg, 
                                  outline='gray25',
                                  width=w,
                                  stipple='gray50',
                                  tag='currentrect')
        #self.lower('currentrect')
        #raise text above all
        self.lift('celltext'+str(row)+str(col))
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
        """When the user double clicks on a text/number cell, bring up entry window"""
        
        absrow = self.get_AbsoluteRow(row)
        h=self.rowheight  
        model=self.getModel()
        text = self.model.getValueAt(absrow, col)
        x1,y1,x2,y2 = self.getCellCoords(row,col)
        w=x2-x1
        #Draw an entry window
        txtvar = StringVar()
        txtvar.set(text)
        def callback(e):
            value = txtvar.get()
            coltype = self.model.getColumnType(col)
            if coltype == 'number':
                sta = self.check_data_entry(e)
                #print sta
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
        
    def draw_Text(self, row, col, celltxt, fgcolor=None, align=None):
        """Draw the text inside a cell area"""
        self.delete('celltext'+str(row)+str(col))
        h=self.rowheight  
        x1,y1,x2,y2 = self.getCellCoords(row,col)
        w=x2-x1
        #
        # If celltxt is a number then we make it a string
        #
        import types
        if type(celltxt) is types.FloatType or type(celltxt) is types.IntType:
            celltxt=str(celltxt)
        #if cell width is less than x, print nothing
        if w<=15:
            return
        try:
            fontsize=self.celltextsizevar.get()
        except:            
            fontsize=12    
        if len(celltxt)>w/fontsize*1.4 or w<30:
            celltxt=celltxt[0:int(w/fontsize*1.4)-2]+'..'
        
        if fgcolor == None or fgcolor == "None":
            fgcolor = 'black'
        if align == None:
            align = 'center'
        elif align == 'w':                    
            x1 = x1-w/2+1
            
        #if celltxt is dict then we are drawing a hyperlink
        if isinstance(celltxt, dict):
            haslink=0
            linktext=celltxt['text']
            if celltxt['link']!=None and celltxt['link']!='':
                linkfont = (self.thefont[0], self.thefont[1], 'underline') 
                linkcolor='blue'
                haslink=1
            else:
                linkfont = self.thefont            
                linkcolor=fgcolor            
            rect = self.create_text(x1+w/2,y1+h/2,
                                      text=linktext,
                                      fill=linkcolor,
                                      font=linkfont,
                                      tag=('text','hlink','celltext'+str(row)+str(col)))
            if haslink == 1:
                self.tag_bind(rect, '<Button-1>', self.check_hyperlink)
        else:    
            rect = self.create_text(x1+w/2,y1+h/2,
                                      text=celltxt,
                                      fill=fgcolor,
                                      font=self.thefont,
                                      anchor=align,
                                      tag=('text','celltext'+str(row)+str(col)))
        #self.lift('celltext'+str(row)+str(col))
        return
    
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

    def drawMultipleRows(self, rowlist):
        """Draw more than one row selection"""
        self.delete('multiplesel')
        for r in rowlist:
            if r > self.rows-1:
                continue
            #print r
            x1,y1,x2,y2 = self.getCellCoords(r,0)
            x2=self.tablewidth
            rect = self.create_rectangle(x1,y1,x2,y2,
                                      fill=self.multipleselectioncolor, 
                                      outline=self.rowselectedcolor,                                  
                                      tag=('multiplesel','rowrect'))         
        self.lower('multiplesel')
        self.lower('fillrect')
        return

    #
    # ----
    #
       
    def draw_tooltip(self, row, col):
        """Draw a tooltip showing contents of cell"""
        
        absrow = self.get_AbsoluteRow(row)
        x1,y1,x2,y2 = self.getCellCoords(row,col)
        w=x2-x1          
        text = self.model.getValueAt(absrow,col)
        if isinstance(text, dict):
            if text.has_key('link'):
                text = text['link']

        #
        # If text is a number we make it a string
        #
        import types
        if type(text) is types.FloatType or type is types.IntType:
            text=str(text)
        if text == NoneType or text == '' or len(text)<=3:
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
        #self.tag_raise('tooltip')
        rect = self.create_rectangle(x1+1,y1+1,x2+1,y2+1,tag='tooltip',fill='black')
        rect2 = self.create_rectangle(x1,y1,x2,y2,tag='tooltip',fill='lightyellow')
        
        self.lift(obj) 
           
        return       
        
        
    def setcellbackgr(self):
        self.cellbackgr = self.getaColor(self.cellbackgr)
        return 

    def setgrid_color(self):
        self.grid_color = self.getaColor(self.grid_color)
        return 
     
    def setrowselectedcolor(self):
        self.rowselectedcolor = self.getaColor(self.rowselectedcolor)
        return
        
    def getaColor(self,oldcolor):   
        import tkColorChooser
        ctuple, newcolor = tkColorChooser.askcolor(title='pick a color', initialcolor=oldcolor,
                                                   parent=self.parentframe)
        print ctuple, newcolor
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
        defaultprefs = {'horizlines':1, 'vertlines':1, 'rowheight':20, 'cellwidth':120,
                        'autoresizecols': 0,
                        'paging': 0, 'rowsperpage' : 50,
                        'celltextsize':12, 'celltextfont':'Arial',
                        'cellbackgr': self.cellbackgr, 'grid_color': self.grid_color,
                        'linewidth' : self.linewidth,
                        'rowselectedcolor': self.rowselectedcolor}

        for prop in defaultprefs.keys():                                    
            try:
                self.prefs.get(prop)
            except:        
                self.prefs.set(prop, defaultprefs[prop])
        #Create tkvars for dialog                
        self.rowheightvar = IntVar()
        self.rowheightvar.set(self.prefs.get('rowheight'))
        self.cellwidthvar = IntVar()
        self.cellwidthvar.set(self.prefs.get('cellwidth'))    
        self.linewidthvar = IntVar()
        self.linewidthvar.set(self.prefs.get('linewidth'))          
        self.autoresizecolsvar = IntVar()
        self.autoresizecolsvar.set(self.prefs.get('autoresizecols'))
        self.horizlinesvar = IntVar()
        self.horizlinesvar.set(self.prefs.get('horizlines'))     
        self.vertlinesvar = IntVar()
        self.vertlinesvar.set(self.prefs.get('vertlines'))
        self.usepagingvar = IntVar()
        self.usepagingvar.set(self.prefs.get('paging'))
        self.rowsperpagevar = StringVar()
        self.rowsperpagevar.set(self.prefs.get('rowsperpage'))        
        self.celltextsizevar = IntVar()
        self.celltextsizevar.set(self.prefs.get('celltextsize'))      
        self.celltextfontvar = StringVar()
        self.celltextfontvar.set(self.prefs.get('celltextfont')) 
        self.cellbackgr = self.prefs.get('cellbackgr')
        self.grid_color = self.prefs.get('grid_color')
        self.rowselectedcolor = self.prefs.get('rowselectedcolor')
        return
        
    def savePrefs(self):
        """Save and set the prefs"""
        try:
            self.prefs.set('horizlines', self.horizlinesvar.get())
            self.horizlines = self.horizlinesvar.get()
            self.prefs.set('vertlines', self.vertlinesvar.get()) 
            self.vertlines = self.vertlinesvar.get()
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
        except ValueError:
            pass
        self.prefs.save_prefs()
               
        return
        
    #
    # -----
    #
    def applyPrefs(self):
        """Apply prefs to the table by redrawing"""

        self.savePrefs()
        self.redrawTable()
        
        return
    
    def AskForColorButton(self, frame, text, func):
        def SetColor():
            import tkColorChooser
            ctuple, variable = tkColorChooser.askcolor(title='pick a color', initialcolor=self.cellbackgr)
            print ctuple, variable
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
        
        
class ColumnHeader(Canvas):
    """Class that takes it's size and rendering from a parent table
        and column names from the table model."""
        
    def __init__(self, parent=None, table=None):
        Canvas.__init__(self, parent, bg='gray25', width=500, height=20)        
        self.thefont='Arial 14'
        if table != None:
            self.table = table
            self.height=20
            self.model = self.table.getModel()
            self.config(width=self.table.width)
            #self.colnames = self.model.columnNames
            self.columnlabels = self.model.columnlabels
            self.bind('<Button-1>',self.handle_left_click)
            self.bind("<ButtonRelease-1>", self.handle_left_release)
            self.bind('<Button-3>',self.handle_right_click)
            self.bind('<B1-Motion>', self.handle_mouse_drag)   
            self.bind('<Motion>', self.handle_mouse_move)

            
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
        #x_pos=x_start
        for col in range(cols):
            colname=self.model.columnNames[col]
            collabel = self.model.columnlabels[colname]
            if self.model.columnwidths.has_key(colname):
                w=self.model.columnwidths[colname]
            else:
                w=self.table.cellwidth
            x=self.table.col_positions[col]
           
            if len(colname)>w/10:
                collabel=collabel[0:w/12]+'.'
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
        colclicked = self.table.get_col_clicked(event)
        self.table.set_selected_col(colclicked)
        if self.atdivider == 1:            
            return   
        
        self.draw_rect(self.table.currentcol)
        #also draw a copy of the rect to be dragged
        self.draggedcol=None
        self.draw_rect(self.table.currentcol, tag='dragrect', 
                        color='red', outline='white')
        if hasattr(self, 'rightmenu'):
            self.rightmenu.destroy()
            
        return

    def handle_left_release(self,event):
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
        if self.draggedcol!=None and self.table.currentcol != self.draggedcol:
            self.model.moveColumn(self.table.currentcol, self.draggedcol)           
            self.table.redrawTable()
        
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
            #x = self.canvasx(event.x)
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
        
    def draw_rect(self,col, tag=None, color=None, outline=None):
        """User has clicked to select a col"""
        if tag==None:
            tag='rect'
        if color==None: 
            color='blue'  
        if outline==None:
            outline='gray25'
        self.delete(tag)
        w=2
        x1,y1,x2,y2 = self.table.getCellCoords(0,col)
        rect = self.create_rectangle(x1,y1,x2,self.height,
                                  fill=color,  
                                  outline=outline,
                                  width=w,
                                  stipple='gray50',
                                  tag=tag)
        self.lower(tag)
        return
        
#        
# --- Table sub-classes ---
#

        
class LabbookTable(TableCanvas):
    """Sub-class of Tablecanvas, with some changes in behaviour to make
       a more spreadsheet-like interface for labbook"""
    def __init__(self, parent=None, model=None, sheetname=None, peat=None, peatinfo=None):
        TableCanvas.__init__(self, parent, model)
        if sheetname != None:
            self.sheetname=sheetname
        if parent != None:
            self.parent = parent 
        else:
            self.parent = None
        #inside peat?
        if peat != None:
            self.peatapp = peat
            self.peatinfo = peatinfo  #info on peat row and column that contains this table
            print 'self.peatinfo',self.peatinfo
        else:
            self.peatapp = None
            self.peatinfo = None            
        self.cellbackgr = '#FFFAF0'
        self.entrybackgr = 'white'
        self.grid_color = 'gray50'
        self.selectedcolor = 'yellow'
        self.rowselectedcolor = '#B0E0E6'
        self.multipleselectioncolor = '#ECD672'
        self.fileicons = {'txt': 'txticon','img':'imageicon','pdf':'pdficon',
                        'other':'blankicon','zip':'zipicon','doc':'docicon',
                        'xls':'ssheeticon'}
        self.columnactions['File'] = {"Edit File": 'edit_File' ,
                                       "View File" : 'view_File' }
        self.columnactions['Table'] = {"Edit Table": 'edit_Table' } 
        self.columnactions['Ekin'] = {"Open Ekin": 'open_Ekin' } 
        print 'labbooktable'
        return

    def draw_file_tooltip(self, row, col):
        """Draw a tooltip for image and file previews"""
        import os
        h=self.height
        x1,y1,x2,y2 = self.getCellCoords(row,col)
        w=x2-x1
        absrow = self.get_AbsoluteRow(row)
        text = self.model.getValueAt(absrow,col)
        if text == '' or text == None:
            return  
        try:
            location = self.model.getCellRecord(absrow,col)['location']
        except:
            location == None
        
        extension = text.split('.')[-1] 
        if extension in ['jpg','jpeg','tiff','tif','gif','ps','png','ico']:
            extension = 'img' 
        if extension in ['gz','bz','jar']:
            extension = 'zip'  
        if not self.fileicons.has_key(extension):
            extension = 'other'
        
        #Check if its an image and try to make thumbnail.. needs PIL
        if extension == 'img' and location != None:
            path=os.path.join(self.peatapp.data['DBfilesSVN'], location)
            self.pic = self.get_image_thumb(path)
            isthumb=1
        #if can't get thumb, just create icon for the file type    
        if self.pic == None:            
            import File_images
            func = getattr(File_images, self.fileicons[extension])
            self.pic = func()
            isthumb=0
            
        imgobj = self.create_image(x1+w/1.5,y2+2, image=self.pic, anchor='nw')
        if isthumb == 1:
            box = self.bbox(imgobj)
            xa=box[0]-1
            ya=box[1]-1
            xb=box[2]+1
            yb=box[3]+1
            self.create_rectangle(xa,ya,xb,yb,tag='tooltip',fill='black')
            self.lift(imgobj)
        
        #now draw text
        import tkFont
        sfont = tkFont.Font (family='Arial', size=12, weight='bold')
        obj=self.create_text(x1+w/1.5,y2,text=text,
                                anchor='sw',    
                                font=sfont,tag='tooltip')        
        box = self.bbox(obj)
        x1=box[0]
        y1=box[1]
        x2=box[2]+1
        y2=box[3]+1        
        self.create_rectangle(x1+1,y1+1,x2+1,y2+1,tag='tooltip',fill='black')
        self.create_rectangle(x1,y1,x2,y2,tag='tooltip',fill='lightyellow')        
        self.lift(obj) 
        
        return
    
    def get_image_thumb(self, infile):
        """Create an image thumbnail for img types"""
        print 'getting thumbnail......'
        try:
            from PIL import Image, ImageTk
        except:
            return None   
        import os        
        size = 200,200         
        file, ext = os.path.splitext(infile)
        im = Image.open(infile)
        im.thumbnail(size, Image.ANTIALIAS)
        tkim = ImageTk.PhotoImage(im)
        #im.save(file + ".thumbnail", "GIF")
        return tkim
        
    def handle_double_click(self, event):
        """Do double click stuff. Selected row/cols will already have
           been set with single click binding"""
        col = self.get_col_clicked(event) 
        if col == None:
            return
            
        coltype = self.model.getColumnType(col)
        if coltype == 'text' or coltype == 'number': 
            self.draw_cellentry(self.currentrow, self.currentcol)
        elif coltype == 'File':
            try:
                self.view_File(self.currentrow, self.currentcol)
            except:
                #self.edit_File(self.currentrow, self.currentcol)
                pass
        elif coltype == 'Table':
            self.edit_Table(self.currentrow, self.currentcol)
        elif coltype == 'Ekin':
            self.open_Ekin(self.currentrow, self.currentcol)
        return

    def handle_motion(self, event):
        """Handle mouse motion overridden to handle file type tooltips"""
        self.delete('tooltip')
        self.pic = None
        row = self.get_row_clicked(event)
        col = self.get_col_clicked(event) 
        if col == None:
            return
        if self.check_PageView(row) == 1:
            return
        coltype = self.model.getColumnType(col)
        if 0 <= row < self.rows and 0 <= col < self.cols:
            if coltype == 'File':
                self.draw_file_tooltip(row, col)
            else:
                self.draw_tooltip(row, col)
        return
        
       
    def view_File(self, row, col):
        """View an external file"""
        print 'viewing file...'
        model = self.getModel()
        celldata = model.getCellRecord(row, col)
        if celldata != None:
            filename = celldata['filename']
            location = celldata['location']
            peatapp.launch_file(filename, location)     
        
        return
        
        
    def edit_File(self, row, col):
        """Dialog for adding a file to a cell. Called when within PEAT only """
        if self.peatapp == None:
            print 'no peat!'
            tkMessageBox.showwarning("Not available",
                         "You cannot add a file outside PEAT." )  
            return
        peatapp = self.peatapp
        model = self.getModel()
        celldata = model.getCellRecord(row, col)
        #colname = model.getColumnName(col)
        #recname = model.getRecName(row)
        if celldata != None:
            currentfilename = celldata['filename']
            location = celldata['location']
        else:
            currentfilename='No file'                   
        #
        # Call add external file from peat?? 
        #        
        protein = self.peatinfo['record']
        field = self.peatinfo['column']
        
        launch_win=Toplevel()       
        launch_win.title('File manager')
        launch_win.focus_set()
        launch_win.grab_set()
        from EAT_DB import PEAT_window 
        if self.parent:
            PEAT_window.set_geometry(self.parent,launch_win)
        Label(launch_win,text='Filename: %s' %currentfilename).grid(row=0,column=0,columnspan=3) 
        Button(launch_win, text='View file',
                               command=lambda : peatapp.launch_file(currentfilename, location),
                               bg='#33CC99',
                               relief=GROOVE).grid(row=1,column=0,columnspan=3)
        
        self.filename=StringVar()
        self.filename.set('')
        Entry(launch_win,textvariable=self.filename,width=25).grid(row=2,column=0)
        def find_file():
            savedir=peatapp.preferences.get('datadir')
            import tkFileDialog
            filename=tkFileDialog.askopenfilename(defaultextension='.*',
                                                  initialdir=savedir,
                                                  filetypes=[("All files","*.*")],
                                                  parent=launch_win)
            self.filename.set(filename)
            return
        
        def addfile():
            self.add_file(peatapp, self.filename.get(), 
                                           protein_name=protein,field_name=field,
                                           sheet=self.sheetname,row=row,col=col,
                                           oldfilename=currentfilename,
                                           window=launch_win)
            launch_win.destroy()
            return
            
        Button(launch_win,text='Browse',command=find_file,
                               bg='#FFFF99',
                               relief=GROOVE).grid(row=2,column=1)
        
        if currentfilename=='No file':
            txt='Add file to project'
        else:
            txt='Replace file'
        Button(launch_win,text=txt,command=addfile,
                               bg='#FFFF99',
                               relief=GROOVE).grid(row=3,column=0)
                    
        return                                                     

    def add_file(self, peatapp, filename, protein_name, field_name, sheet,
                            row, col, oldfilename=None, window=None):
        """Add a file to the database via the table - needs to be callable outside table"""
        model = self.getModel()
        colname = model.getColumnName(col)
        recname = model.getRecName(row)       
        print oldfilename
        filename, location = peatapp.add_external_file(filename, window=window,
                                                           protein_name=protein_name,column=field_name,
                                                           sheet=sheet,row=recname,col=colname,
                                                           oldfilename=oldfilename)
        #print filename, location
         
        model.setValueAt(None,row,col, filename=filename,location=location)
        color = model.getColorAt(row,col,'fg')
        value = model.getValueAt(row,col)
        self.draw_Text(row, col, value, color)
        #print model.data        
        return

    '''def get_external_filenames(self):
        """Returns all external filenames stored as part of this table"""
        model = self.getModel()
        filenames = model.get_external_filename()        
        return filenames'''
    
        
    def edit_Table(self, row, col):
        """Edit a nested table"""
        #Done by opening up another instance of labbook and returning the data to the parent

        #get cell data and pass to labbook as a new table
        model = self.getModel()
        tabledata= model.getCellRecord(row,col)
        refname = str(row)+'_'+str(col)
        if self.peatinfo != None:
            refname =  self.peatinfo['record']+'_'+self.peatinfo['column']+'_'+refname
        from Labbook import LabbookApp
        if tabledata:
            self.sublabbook = LabbookApp(parent=self, title=refname, data=tabledata)
        else:
            self.sublabbook = LabbookApp(parent=self, title=refname)
        self.master.wait_window(self.sublabbook.labbook_win)
        
        # did we get any data back?
        if not hasattr(self,'templabbookdata'):
            self.templabbookdata=None
        else:   
            model.setValueAt(self.templabbookdata, row, col)
            self.redrawTable()
            self.templabbookdata=None
           
        return

    def open_Ekin(self, row, col):
        """Edit Ekin data, can be used outside PEAT, but does not contain protein and
           field references"""
        model = self.getModel()
        cell_data = model.getCellRecord(row,col)
        if not cell_data:
            ed = EkinModesDialog(title="Select Mode",                                               
                                  parent=self.parentframe)
            mode = ed.result
            print 'MODE',mode
            ekindata = None            
            #cell_data={}
            #cell_data['mode'] = mode
            #model.setValueAt(self.Ekindata, row, col)
        else:
            mode=cell_data['mode']
            ekindata=cell_data['ekindata']
        import EAT_DB.Ekin as Ekin
        EK=Ekin.Ekin(parent=self,mode=mode,data=ekindata,allowreturntoDB=1)
        self.Ekindata=None
        self.master.wait_window(EK.ekin_win)
        if not getattr(self,'Ekindata',None):
            self.Ekindata=None
        else:
            newdata={}
            newdata['mode']=mode
            newdata['ekindata']=self.Ekindata
            model.setValueAt(newdata, row, col)
            self.redrawTable()
            self.Ekindata=None
        return
        
class EkinModesDialog(tkSimpleDialog.Dialog):
    def __init__(self, parent, title=None):   
        self.ekinmodes = ['General', 'Simple enzyme kinetic',
                    'Enzyme pH-activity', 'pH-stability',
                    'NMR titration', 'Protein stability',
                    'Amyloid formation']
        tkSimpleDialog.Dialog.__init__(self, parent, title)                    
                    
    def body(self, master):                  
            
        import Pmw
        self.themode=StringVar()
        self.mode_choice = Pmw.OptionMenu(
            parent = master,labelpos = 'w',
            label_text = 'Enter mode:',
            menubutton_textvariable = self.themode,
            items = self.ekinmodes,
            initialitem = 'General',
            menubutton_width = 16)              
        self.mode_choice.pack(pady=5)
        return self.mode_choice
        
    def apply(self): 
        self.result = self.themode.get()
        return       
                

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

