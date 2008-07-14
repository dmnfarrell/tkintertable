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

class TableModel(object):
    """A base model for managing the data in a TableCanvas class"""
    
    def __init__(self, newdict=None):
        import copy
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
        if newdict == None:
            self.data = {}
            # Define the starting column names and locations in the table.
            self.columnNames = ['Name']
            self.columntypes = {'Name':'text'}
            self.columnOrder = None
            #record column labels for use in a table header
            self.columnlabels={}  
            for colname in self.columnNames:
                self.columnlabels[colname]=colname   
                
        else:
            self.data = copy.deepcopy(newdict)
            self.columnNames=copy.deepcopy(self.data['columnnames'])
            del self.data['columnnames']          
            self.columntypes=copy.deepcopy(self.data['columntypes'])
            del self.data['columntypes']            
            self.columnlabels=copy.deepcopy(self.data['columnlabels'])
            del self.data['columnlabels']
            if self.data.has_key('columnorder'):
                self.columnOrder=copy.deepcopy(self.data['columnorder'])
                del self.data['columnorder']
            else:
                self.columnOrder=None
            if self.data.has_key('colors'):
                self.colors = copy.deepcopy(self.data['colors'])
                del self.data['colors']

        # Store the sorted list of names
        self.reclist = self.data.keys()
        self.reclist.sort()        
        
        #restore last column order
        if self.columnOrder:
            self.columnNames=[]
            for i in self.columnOrder.keys():
                self.columnNames.append(self.columnOrder[i] )
                i=i+1
            print self.columnNames
        
        self.defaulttypes = ['text', 'number']
        #setup default display for column types
        self.default_display = {'text' : 'showstring',
                                'number' : 'numtostring'}

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
        name = self.reclist[rowIndex]
        return name

        
    def getRecordAttributeAtColumn(self, rowIndex, columnIndex):
         """Get the attribute of the record at the specified column index.
            This determines what will be displayed in the cell"""

         value = None   # Holds the value we are going to return
         cell = self.getCellRecord(rowIndex, columnIndex)
         if cell == None:
            cell=''
         # Set the value based on the data record field
         #action = self.default_display[coltype]
         #value = 
         colname = self.getColumnName(columnIndex)
         coltype = self.columntypes[colname]
         if not isinstance(cell,dict):             
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
    
    def setSortOrder(self, columnIndex, reverse=0):
        """Changes the order that records are sorted in, which will
           be reflected in the table upon redrawing"""
        import operator      
        self.sortcolumnIndex = columnIndex  #store current column sorted on
        sortmap=[]
        sortkey = self.getColumnName(columnIndex)
        for rec in self.data.keys():            
            if isinstance(self.data[rec], dict) and self.data[rec].has_key(sortkey):
                sortmap.append((rec, self.data[rec][sortkey]))
            else:
                sortmap.append((rec, ''))
        #print sortmap  
        #sort the mapping by the second key
        self.sortmap = sorted(sortmap, key=operator.itemgetter(1), reverse=reverse)
        #print sortmap
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
        index = self.getRowCount() + 1
        if name == None:
            name=str(index)
        if self.data.has_key(name):
            name = name + '_1'
        self.data[name]={}
        if name != None:
            self.data[name]['Name'] = name
        else:
            self.data[name]['Name'] = ''
        
        self.reclist = self.data.keys()
        self.reclist.sort()        

        return

    def deleteRow(self, rowIndex):
        """Delete a row"""
                
        name = self.reclist[rowIndex]
        del self.data[name]
        self.reclist = self.data.keys()
        self.reclist.sort()
        return
        
    def deleteRows(self, rowlist): 
        print 'deleting' , rowlist
        print 'reclist', self.reclist
        for row in rowlist:
            name = self.reclist[row]
            del self.data[name]
        self.reclist = self.data.keys()  
        self.reclist.sort()
        return

    def addColumn(self, colname=None, coltype=None):
        """Add a column"""
        index = self.getColumnCount()+ 1
        if colname == None:
            colname=str(index)
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
        
        print 'column deleted'
        print 'new cols:', self.columnNames
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
        #print 'new color', color
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
     
