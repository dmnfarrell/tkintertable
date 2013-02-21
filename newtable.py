#!/usr/bin/env python

from Tkinter import *
from Tables import TableCanvas, RowHeader, ColumnHeader
from TableModels import TableModel
from Tables import AutoScrollbar
import Testing

import math

class App:
    def __init__(self, master):
        self.main = Frame(master)
        self.main.pack(fill=BOTH,expand=1)
        master.geometry('600x400+200+100')

class LargeTable(TableCanvas):
    def __init__(self, parent=None, model=None, newdict=None,
                    width=None, height=None, **kwargs):
        TableCanvas.__init__(self, parent=parent, model=model, newdict=newdict,
                    width=width, height=width, **kwargs)
        return

    def createTableFrame(self, callback=None):
        """Adds column header and scrollbars and combines them with
           the current table adding all to the master frame provided in constructor.
           Table is then redrawn."""

        #Add the table and header to the frame
        self.tablerowheader = LargeRowHeader(self.parentframe, self)
        self.tablecolheader = LargeColumnHeader(self.parentframe, self)
        self.Yscrollbar = AutoScrollbar(self.parentframe,orient=VERTICAL,command=self.set_yviews)
        self.Yscrollbar.grid(row=1,column=2,rowspan=1,sticky='news',pady=0,ipady=0)
        self.Xscrollbar = AutoScrollbar(self.parentframe,orient=HORIZONTAL,command=self.set_xviews)
        self.Xscrollbar.grid(row=2,column=1,columnspan=1,sticky='news')
        self['xscrollcommand'] = self.Xscrollbar.set
        self['yscrollcommand'] = self.Yscrollbar.set
        self.tablecolheader['xscrollcommand'] = self.Xscrollbar.set
        self.tablerowheader['yscrollcommand'] = self.Yscrollbar.set
        self.parentframe.rowconfigure(1,weight=1)
        self.parentframe.columnconfigure(1,weight=1)

        self.tablecolheader.grid(row=0,column=1,rowspan=1,sticky='news',pady=0,ipady=0)
        self.tablerowheader.grid(row=1,column=0,rowspan=1,sticky='news',pady=0,ipady=0)
        self.grid(row=1,column=1,rowspan=1,sticky='news',pady=0,ipady=0)

        self.adjustColumnWidths()
        self.redrawTable(callback=callback)
        self.parentframe.bind("<Configure>", self.redrawVisible)
        self.tablecolheader.xview("moveto", 0)
        self.xview("moveto", 0)
        return

    def getVisibleRegion(self):
        x1, y1 = self.canvasx(0), self.canvasy(0)
        w, h = self.winfo_width(), self.winfo_height()
        if w <= 1.0 or h <= 1.0:
            w, h = self.master.winfo_width(), self.master.winfo_height()
        x2, y2 = self.canvasx(w), self.canvasy(h)
        return x1, y1, x2, y2

    def getRowPosition(self, y):
        h = self.rowheight
        y_start = self.y_start
        row = (int(y)-y_start)/h
        if row < 0:
            return 0
        if row > self.rows:
            row = self.rows
        return row

    def getColPosition(self, x):
        x_start = self.x_start
        w = self.cellwidth
        i=0
        col=0
        for c in self.col_positions:
            col = i
            if c+w>=x:
                break
            i+=1
        return col

    def getVisibleRows(self, y1, y2):
        """Get the visible row range"""
        start = self.getRowPosition(y1)
        end = self.getRowPosition(y2)+1
        if end > self.rows:
            end = self.rows
        return start, end

    def getVisibleCols(self, x1, x2):
        """Get the visible column range"""
        start = self.getColPosition(x1)
        end = self.getColPosition(x2)+1
        if end > self.cols:
            end = self.cols
        return start, end

    def redrawVisible(self, event=None, callback=None):
        """Redraw the visible portion of the canvas"""

        #print 'redraw'
        model = self.model
        self.rows = self.model.getRowCount()
        self.cols = self.model.getColumnCount()
        if self.cols == 0 or self.rows == 0:
            self.delete('entry')
            self.delete('rowrect')
            self.delete('currentrect')
            return
        self.tablewidth = (self.cellwidth) * self.cols
        self.configure(bg=self.cellbackgr)
        self.set_colPositions()

        #are we drawing a filtered subset of the recs?
        if self.filtered == True and self.model.filteredrecs != None:
            self.rows = len(self.model.filteredrecs)
            self.delete('colrect')

        self.rowrange = range(0,self.rows)
        self.configure(scrollregion=(0,0, self.tablewidth+self.x_start,
                self.rowheight*self.rows+10))

        x1, y1, x2, y2 = self.getVisibleRegion()
        #print x1, y1, x2, y2
        startvisiblerow, endvisiblerow = self.getVisibleRows(y1, y2)
        self.visiblerows = range(startvisiblerow, endvisiblerow)
        startvisiblecol, endvisiblecol = self.getVisibleCols(x1, x2)
        self.visiblecols = range(startvisiblecol, endvisiblecol)

        self.drawGrid(startvisiblerow, endvisiblerow)
        align = self.align
        self.delete('fillrect')
        for row in self.visiblerows:
            if callback != None:
                callback()
            for col in self.visiblecols:
                colname = model.getColumnName(col)
                bgcolor = model.getColorAt(row,col, 'bg')
                fgcolor = model.getColorAt(row,col, 'fg')
                text = model.getValueAt(row,col)
                self.draw_Text(row, col, text, fgcolor, align)
                if bgcolor != None:
                    self.draw_rect(row,col, color=bgcolor)

        #self.drawSelectedCol()
        self.tablecolheader.redraw()
        self.tablerowheader.redraw()
        #self.setSelectedRow(self.currentrow)
        self.drawSelectedRow()
        self.draw_selected_rect(self.currentrow, self.currentcol)
        #print self.multiplerowlist

        if len(self.multiplerowlist)>1:
            self.tablerowheader.drawSelectedRows(self.multiplerowlist)
            self.drawMultipleRows(self.multiplerowlist)
            self.drawMultipleCells()
        return

    def drawGrid(self, startrow, endrow):
        """Draw the table grid lines"""
        self.delete('gridline','text')
        rows=len(self.rowrange)
        cols=self.cols
        w = self.cellwidth
        h = self.rowheight
        x_start=self.x_start
        y_start=self.y_start
        x_pos=x_start

        if self.vertlines==1:
            for col in range(cols+1):
                x=self.col_positions[col]
                self.create_line(x,y_start,x,y_start+rows*h, tag='gridline',
                                     fill=self.grid_color, width=self.linewidth)
        if self.horizlines==1:
            for row in range(startrow, endrow+1):
                y_pos=y_start+row*h
                self.create_line(x_start,y_pos,self.tablewidth,y_pos, tag='gridline',
                                    fill=self.grid_color, width=self.linewidth)
        return

    def redrawTable(self, event=None, callback=None):
        self.redrawVisible(event, callback)
        return

    def set_xviews(self,*args):
        """Set the xview of table and col header"""
        apply(self.xview,args)
        apply(self.tablecolheader.xview,args)
        self.redrawVisible()
        return

    def set_yviews(self,*args):
        """Set the xview of table and row header"""
        apply(self.yview,args)
        apply(self.tablerowheader.yview,args)
        self.redrawVisible()
        return

    def mouse_wheel(self, event):
        """Handle mouse wheel scroll for windows"""

        if event.num == 5 or event.delta == -120:
            event.widget.yview_scroll(1, UNITS)
            self.tablerowheader.yview_scroll(1, UNITS)
        if event.num == 4 or event.delta == 120:
            if self.canvasy(0) < 0:
                return
            event.widget.yview_scroll(-1, UNITS)
            self.tablerowheader.yview_scroll(-1, UNITS)
        self.redrawVisible()
        return

class LargeColumnHeader(ColumnHeader):
    """Class that takes it's size and rendering from a parent table
        and column names from the table model."""

    def __init__(self, parent=None, table=None):
        ColumnHeader.__init__(self, parent, table)

    def redraw(self):
        cols = self.model.getColumnCount()
        self.tablewidth=self.table.tablewidth
        self.configure(scrollregion=(0,0, self.table.tablewidth+self.table.x_start, self.height))
        self.delete('gridline','text')
        self.delete('rect')
        self.atdivider = None

        h=self.height
        x_start=self.table.x_start
        if cols == 0:
            return
        for col in self.table.visiblecols:
            colname=self.model.columnNames[col]
            if not self.model.columnlabels.has_key(colname):
                self.model.columnlabels[colname]=colname
            collabel = self.model.columnlabels[colname]
            if self.model.columnwidths.has_key(colname):
                w = self.model.columnwidths[colname]
            else:
                w = self.table.cellwidth
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

class LargeRowHeader(RowHeader):
    """Class that displays the row headings on the table
       takes it's size and rendering from the parent table
       This also handles row/record selection as opposed to cell
       selection"""
    def __init__(self, parent=None, table=None):
        RowHeader.__init__(self, parent, table)

    def redraw(self):
        """Redraw row header"""

        self.height = self.table.rowheight * self.table.rows+10
        self.configure(scrollregion=(0,0, self.width, self.height))
        self.delete('rowheader','text')
        self.delete('rect')
        w=1
        x_start = self.x_start
        h = self.table.rowheight

        for row in self.table.visiblerows:
            x1,y1,x2,y2 = self.table.getCellCoords(row,0)
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
        return

def test(root):
    data = Testing.createData(2000,20)
    model = TableModel()
    model.importDict(data)
    app = App(root)
    master = app.main
    table = LargeTable(master, model)
    #table.load('large.table')
    table.createTableFrame()

def main():
    root = Tk()
    test(root)
    root.mainloop()

if __name__ == '__main__':
    main()
