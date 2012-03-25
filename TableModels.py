#!/usr/bin/env python
"""
    Created January 2008
    TableModel Class
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

from TableFormula import Formula
from types import *

class TableModel(object):
    """A base model for managing the data in a TableCanvas class"""

    keywords = {'columnnames':'columnNames', 'columntypes':'columntypes',
               'columnlabels':'columnlabels', 'columnorder':'columnOrder',
               'colors':'colors'}

    def __init__(self, newdict=None, rows=None, columns=None):
        import copy
        self.initialiseFields()
        if newdict != None:
            self.data = copy.deepcopy(newdict)
            for k in self.keywords:
                if self.data.has_key(k):
                    self.__dict__[self.keywords[k]] = self.data[k]
                    del self.data[k]
            #read in the record list order
            if self.data.has_key('reclist'):
                temp = self.data['reclist']
                del self.data['reclist']
                self.reclist = temp
            else:
                self.reclist = self.data.keys()
        else:
            #just make a new empty model
            self.createEmptyModel()

        if not set(self.reclist) == set(self.data.keys()):
            print 'reclist does not match data keys'
        #restore last column order
        if hasattr(self, 'columnOrder') and self.columnOrder != None:
            self.columnNames=[]
            for i in self.columnOrder.keys():
                self.columnNames.append(self.columnOrder[i] )
                i=i+1
        self.defaulttypes = ['text', 'number']
        #setup default display for column types
        self.default_display = {'text' : 'showstring',
                                'number' : 'numtostring'}
        #add rows and cols if they are given in the constructor
        if newdict == None:
            if rows != None:
                self.auto_AddRows(rows)
            if columns != None:
                self.auto_AddColumns(columns)
        #finally set default sort order as first col
        #self.setSortOrder()
        return

    def initialiseFields(self):
        """Create base fields, some of which are not saved"""
        self.data = None    # holds the table dict
        self.colors = {}    # holds cell colors
        self.colors['fg']={}
        self.colors['bg']={}
        #default types
        self.defaulttypes = ['text', 'number']
        #list of editable column types
        self.editable={}
        self.nodisplay = []
        self.columnwidths={}  #used to store col widths, not held in saved data
        return

    def createEmptyModel(self):
        """Create the basic empty model dict"""
        self.data = {}
        # Define the starting column names and locations in the table.
        self.columnNames = []
        self.columntypes = {}
        self.columnOrder = None
        #record column labels for use in a table header
        self.columnlabels={}
        for colname in self.columnNames:
            self.columnlabels[colname]=colname
        self.reclist = self.data.keys()
        return

    def importDict(self, newdata, namefield=None):
        """Try to create a table model from some arbitrary dict"""
        import types
        if namefield == None:
            namefield = 'name'
        #get cols from sub data keys
        colnames = []
        colnames.append(namefield)
        for k in newdata:
            fields = newdata[k].keys()
            for f in fields:
                if not f in colnames:
                    colnames.append(f)

        for c in colnames:
            self.addColumn(c)

        #add the data
        #print colnames
        for k in newdata:
            self.addRow(k)
            for c in colnames:
                if c == namefield:
                    self.data[k][namefield] = str(k)
                else:
                    self.data[k][c] = str(newdata[k][c])

        return

    def getDefaultTypes(self):
        """Get possible field types for this table model"""
        return self.defaulttypes

    def getData(self):
        """Return the current data for saving"""
        import copy
        data = copy.deepcopy(self.data)
        data['colors'] = self.colors
        data['columnnames'] = self.columnNames
        #we keep original record order
        data['reclist'] = self.reclist
        #record current col order
        data['columnorder']={}
        i=0
        for name in self.columnNames:
            data['columnorder'][i] = name
            i=i+1
        data['columntypes'] = self.columntypes
        data['columnlabels'] = self.columnlabels
        return data

    def getAllCells(self):
        """Return a dict of the form rowname: list of cell contents
          Useful for a simple table export for example"""
        records={}
        for row in range(len(self.reclist)):
            recdata=[]
            for col in range(len(self.columnNames)):
                recdata.append(self.getValueAt(row,col))
            records[row]=recdata
        return records

    def getColCells(self, colIndex):
        """Get the viewable contents of a col into a list"""
        collist = []
        for row in range(len(self.reclist)):
            v = self.getValueAt(row, colIndex)
            collist.append(v)

        return collist

    def getlongestEntry(self, columnIndex):
        """Get the longest cell entry in the col"""
        collist = self.getColCells(columnIndex)
        maxw=0
        for c in collist:
            try:
                w = len(str(c))
            except UnicodeEncodeError:
                pass
            if w > maxw:
                maxw = w
        #print 'longest width', maxw
        return maxw

    def getRecordAtRow(self, rowIndex):
        """Get the entire record at the specifed row."""
        name = self.reclist[rowIndex]
        record = self.data[name]
        return record

    def getCellRecord(self, rowIndex, columnIndex):
        """Get the data held in this row and column"""
        value = None
        colname = self.getColumnName(columnIndex)
        coltype = self.columntypes[colname]
        name = self.reclist[rowIndex]
        if self.data[name].has_key(colname):
            celldata=self.data[name][colname]
        else:
            celldata=None
        return celldata

    def deleteCellRecord(self, rowIndex, columnIndex):
        """Remove the cell data at this row/column"""
        colname = self.getColumnName(columnIndex)
        coltype = self.columntypes[colname]
        name = self.reclist[rowIndex]
        if self.data[name].has_key(colname):
            del self.data[name][colname]
        return

    def getRecName(self, rowIndex):
        """Get record name from row number"""
        if len(self.reclist)==0:
            return None
        name = self.reclist[rowIndex]
        return name

    def setRecName(self, newname, rowIndex):
        """Set the record name to another value - requires re-setting in all
           dicts that this rec is referenced"""
        if len(self.reclist)==0:
            return None
        currname = self.getRecName(rowIndex)
        self.reclist[rowIndex] = newname
        import copy
        temp = copy.deepcopy(self.data[currname])
        self.data[newname] = temp
        self.data[newname]['Name'] = newname
        del self.data[currname]
        for key in ['bg', 'fg']:
            if self.colors[key].has_key(currname):
                temp = copy.deepcopy(self.colors[key][currname])
                self.colors[key][newname] = temp
                del self.colors[key][currname]
        print 'renamed'
        #would also need to resolve all refs to this rec in formulas here!!

        return

    def getRecordAttributeAtColumn(self, rowIndex=None, columnIndex=None,
                                        recName=None, columnName=None):
         """Get the attribute of the record at the specified column index.
            This determines what will be displayed in the cell"""

         value = None
         if columnName != None and recName != None:
             cell = self.data[recName][columnName]
         else:
             cell = self.getCellRecord(rowIndex, columnIndex)
             columnName = self.getColumnName(columnIndex)
         if cell == None:
             cell=''
         # Set the value based on the data record field
         coltype = self.columntypes[columnName]
         if Formula.isFormula(cell) == True:  #change this to e.g. cell.isFormula() ?
             value = self.doFormula(cell)
             return value
         if not type(cell) is DictType:
             if coltype == 'text' or coltype == 'Text':
                 value = cell
             elif coltype == 'number':
                 value = str(cell)
             else:
                 value = 'other'
         if value==None:
             value=''

         return value

    def getRecordIndex(self, recname):
        rowIndex = self.reclist.index(recname)
        return rowIndex

    def setSortOrder(self, columnIndex=0, reverse=0):
        """Changes the order that records are sorted in, which will
           be reflected in the table upon redrawing"""
        import operator
        self.sortcolumnIndex = columnIndex  #store current column sorted by
        sortmap=[]
        sortkey = self.getColumnName(columnIndex)
        for rec in self.data.keys():
            recdata = self.getRecordAttributeAtColumn(recName=rec, columnName=sortkey)
            sortmap.append((rec, recdata))

        #sort the mapping by the second key
        self.sortmap = sorted(sortmap, key=operator.itemgetter(1), reverse=reverse)
        #now sort the main reclist by the mapping order
        self.reclist = map(operator.itemgetter(0),self.sortmap)
        return

    def getSortIndex(self):
        """Return the current sort order index"""
        if self.sortcolumnIndex:
            return self.sortcolumnIndex
        else:
            return 0


    def moveColumn(self, oldcolumnIndex, newcolumnIndex):
        """Changes the order of columns"""
        self.oldnames = self.columnNames
        self.columnNames=[]
        #self.columnOrder=[]

        print oldcolumnIndex, newcolumnIndex
        #write out a new column names list - tedious
        moved = self.oldnames[oldcolumnIndex]
        del self.oldnames[oldcolumnIndex]
        print self.oldnames
        i=0
        for c in self.oldnames:
            if i==newcolumnIndex:
                self.columnNames.append(moved)
                #self.columnOrder.append(moved)
            self.columnNames.append(c)
            #self.columnOrder.append(c)
            i=i+1
        #if new col is at end just append
        if moved not in self.columnNames:
            self.columnNames.append(moved)
            #self.columnOrder.append(moved)

        print self.columnNames
        #print self.columnOrder
        return

    def addRow(self, name=None):
        """Add a row"""

        if self.data.has_key(name) or name in self.reclist:
            print 'name already present!!'
            return
        self.data[name]={}
        if name != None:
            self.data[name]['Name'] = name
        else:
            self.data[name]['Name'] = ''
        self.reclist.append(name)
        #self.reclist.sort()

        return

    def deleteRow(self, rowIndex, update=True):
        """Delete a row"""
        name = self.reclist[rowIndex]
        del self.data[name]
        if update==True:
            self.reclist = self.data.keys()

        return

    def deleteRows(self, rowlist=None):
        """Delete multiple or all rows"""
        if rowlist == None:
            rowlist = range(len(self.reclist))
        print 'deleting' , rowlist
        print 'reclist', self.reclist
        for row in rowlist:
            self.deleteRow(row, update=False)
        self.reclist = self.data.keys()

        return

    def addColumn(self, colname=None, coltype=None):
        """Add a column"""
        index = self.getColumnCount()+ 1
        if colname == None:
            colname=str(index)
        if colname in self.columnNames:
            print 'name is present!'
            return
        self.columnNames.append(colname)
        self.columnlabels[colname] = colname
        if coltype == None:
            self.columntypes[colname]='text'
        else:
            self.columntypes[colname]=coltype

        return

    def deleteColumn(self, columnIndex):
        """delete a column"""
        colname = self.getColumnName(columnIndex)
        print colname
        self.columnNames.remove(colname)
        del self.columnlabels[colname]
        del self.columntypes[colname]
        #remove this field from every record
        for recname in self.reclist:
            if self.data[recname].has_key(colname):
                del self.data[recname][colname]

        if hasattr(self, 'sortcolumnIndex') and columnIndex == self.sortcolumnIndex:
            self.setSortOrder()
        print 'column deleted'
        print 'new cols:', self.columnNames
        return

    def deleteMultipleColumns(self, cols=None):
        """Remove all cols or list provided"""

        while self.getColumnCount() > 0:
            self.deleteColumn(0)
        return


    def auto_AddRows(self, numrows=None):
        """Automatically add x number of records"""
        import string
        alphabet = string.lowercase[:26]
        rows = self.getRowCount()

        if rows <= 25:
            i=rows
            j=0
        else:
            i=int(rows%25)
            j=int(round(rows/25,1))
        #print i, j
        for x in range(numrows):
            if i >= len(alphabet):
                i=0
                j=j+1
            name = alphabet[i]+str(j)
            if name in self.reclist:
                pass
            else:
                self.addRow(name)
            i=i+1
            #print self.reclist
        return

    def auto_AddColumns(self, numcols=None):
        """Automatically add x number of cols"""
        import string
        alphabet = string.lowercase[:26]
        currcols=self.getColumnCount()
        #find where to start
        start = currcols + 1
        end = currcols + numcols + 1
        new = []
        for n in range(start, end):
            new.append(str(n))
        #check if any of these colnames present
        common = set(new) & set(self.columnNames)
        extra = len(common)
        end = end + extra
        for x in range(start, end):
            self.addColumn(str(x))
        return

    def relabel_Column(self, columnIndex, newname):
        """Change the column label - can be used in a table header"""
        colname = self.getColumnName(columnIndex)
        self.columnlabels[colname]=newname
        return

    def getColumnType(self, columnIndex):
        """Get the column type"""
        colname = self.getColumnName(columnIndex)
        coltype = self.columntypes[colname]
        return coltype

    def getColumnCount(self):
         """Returns the number of columns in the data model."""
         return len(self.columnNames)

    def getColumnName(self, columnIndex):
         """Returns the name of the given column by columnIndex."""
         return self.columnNames[columnIndex]

    def getColumnLabel(self, columnIndex):
        """Returns the label for this column"""
        colname = self.getColumnName(columnIndex)
        return self.columnlabels[colname]

    def getColumnIndex(self, columnName):
        """Returns the column index for this column"""
        colindex = self.columnNames.index(columnName)
        return colindex

    def getColumnData(self, columnIndex=None, columnName=None,
                      filterby=None, keyword=None):
        """Return the data in a list for this col, allows to filter by rec attribute"""
        if columnIndex != None:
            columnName = self.getColumnName(columnIndex)
        coldata = []
        for r in self.reclist:
            coldata.append(self.data[r][columnName])          
        return coldata
    
    def getRowCount(self):
         """Returns the number of rows in the table model."""
         return len(self.reclist)

    def getValueAt(self, rowIndex, columnIndex):
         """Returns the cell value at location specified
             by columnIndex and rowIndex."""
         # Get the record object corresponding to this row.
         #rec = self.getRecordAtRow(rowIndex)
         # Get the address attribute corresponding to this column.
         value = self.getRecordAttributeAtColumn(rowIndex, columnIndex)

         return value

    def setValueAt(self, value, rowIndex, columnIndex):
        """Changed the dictionary when cell is updated by user"""
        name = self.reclist[rowIndex]
        colname = self.getColumnName(columnIndex)
        coltype = self.columntypes[colname]
        #print coltype
        if coltype == 'number':
            try:
                if value == '': #need this to allow deletion of values
                    self.data[name][colname] = ''
                else:
                    self.data[name][colname] = float(value)
            except:
                pass
        else:
            self.data[name][colname] = value
        #print self.data
        return

    def setFormulaAt(self, f, rowIndex, columnIndex):
        """Set a formula at cell given"""
        name = self.reclist[rowIndex]
        colname = self.getColumnName(columnIndex)
        coltype = self.columntypes[colname]
        rec = {}
        rec['formula'] = f
        self.data[name][colname] = rec
        return

    def getColorAt(self, rowIndex, columnIndex, key='bg'):
        """Return color of that record field for the table"""
        name = self.reclist[rowIndex]
        colname = self.getColumnName(columnIndex)
        if self.colors[key].has_key(name) and self.colors[key][name].has_key(colname):
            return self.colors[key][name][colname]
        else:
            return None

    def setColorAt(self, rowIndex, columnIndex, color, key='bg'):

        name = self.reclist[rowIndex]
        colname = self.getColumnName(columnIndex)
        if not self.colors[key].has_key(name):
            self.colors[key][name] = {}
        self.colors[key][name][colname] = str(color)
        #print 'new color', self.colors[name][colname]
        #print self.colors
        return

    def resetcolors(self):
        """Remove all color formatting"""
        self.colors={}
        self.colors['fg']={}
        self.colors['bg']={}
        return

    def getRecColNames(self, rowIndex, ColIndex):
        """Returns the rec and col name as a tuple"""
        recname = self.getRecName(rowIndex)
        colname = self.getColumnName(ColIndex)
        return (recname, colname)

    def getRecAtRow(self, recname, colname, offset=1, dim='y'):
        """Get the record name at a specified offset in the current
           table from the record given, by using the current sort order"""
        thisrow = self.getRecordIndex(recname)
        thiscol = self.getColumnIndex(colname)
        #table goto next row
        if dim == 'y':
            nrow = thisrow + offset
            ncol = thiscol
        else:
            nrow = thisrow
            ncol = thiscol + offset

        newrecname, newcolname = self.getRecColNames(nrow, ncol)
        print 'recname, colname', recname, colname
        print 'thisrow, col', thisrow, thiscol
        return newrecname, newcolname

    def appendtoFormula(self, formula, rowIndex, colIndex):
        """Add the input cell to the formula"""
        cellRec = getRecColNames(rowIndex, colIndex)
        formula.append(cellRec)
        return

    def doFormula(self, cellformula):
        """Evaluate the formula for a cell and return the result"""
        value = Formula.doFormula(cellformula, self.data)
        return value

    def copyFormula(self, cellval, row, col, offset=1, dim='y'):
        """Copy a formula down or across, using the provided offset"""
        import re
        frmla = Formula.getFormula(cellval)
        #print 'formula', frmla

        newcells=[]
        cells, ops = Formula.readExpression(frmla)

        for c in cells:
            print c
            if type(c) is not ListType:
                nc = c
            else:
                recname = c[0]
                colname = c[1]
                nc = list(self.getRecAtRow(recname, colname, offset, dim=dim))
            newcells.append(nc)
        #print 'newcells', newcells

        #replace new record refs in formula
        newformula = Formula.doExpression(newcells, ops, getvalues=False)

        #print 'copied formula'
        #print 'old:', cellval
        #print 'new:', newformula
        return newformula

