[![PyPI version shields.io](https://img.shields.io/pypi/v/tkintertable.svg)](https://pypi.python.org/pypi/tkintertable/)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## About

<img align="right" src=https://raw.githubusercontent.com/dmnfarrell/tkintertable/master/img/logo.png width=150px>

Python uses a GUI library called Tkinter as default. This set of classes allows interactive spreadsheet-style tables to be added into an application. Tkinter is the standard GUI toolkit for python. It is old but still quite popular. There are various libraries that extend Tkinter functionality, such as Pmw, but there is currently no extendable table class for Tkinter. A sample application using these classes is included in the distribution.

**This library is also now Python 3 compatible**

## Installation

```pip install tkintertable``` or ```easy_install tkintertable```

You can clone the current source using

git clone https://github.com/dmnfarrell/tkintertable.git

## Usage

### Import the class

The core classes are TableCanvas and TableModel. You will likely want to access the TableModel class 
to alter the data programmatically, otherwise the TableCanvas class is all that's required to add to the GUI. 
To import:

```
from tkintertable import TableCanvas, TableModel
```
or
```
from tkintertable.Tables import TableCanvas
from tkintertable.TableModels import TableModel
```

### Create tables

To create a table, you typically create a frame in your applications GUI and provide this to the table
constructor. Note that the createTableFrame method is used to add the table to the parent frame, 
so avoid using the pack or grid methods.
```
tframe = Frame(master)
tframe.pack()
table = TableCanvas(tframe)
table.createTableFrame()
```

We can also create a model from some data, then use that model to initiate the table:
```
model = TableModel()
table = TableCanvas(frame, model=model)
```

### Get data into the table

It is possible to populate the tables by importing data from a csv file or creating a python dictionary. To import from a dictionary, it should be of the form:
```
data = {'rec1': {'col1': 99.88, 'col2': 108.79, 'label': 'rec1'},
       'rec2': {'col1': 99.88, 'col2': 108.79, 'label': 'rec2'}
       } 
```
Each record corresponds to a row in the dictionary. Columns will be created for each child key found in each record.

Then provide this dict to the constructor:
```
table = TableCanvas(data=data)
```

Or we get a handle on the model (or we can create the model first and supply it as an argument to the table constructor):
```
model = table.model
model.importDict(data) 
table.redrawTable()
```

Importing from a text file can be down interactively from the GUI by right clicking on the table and
choosing 'Import Table' from the popup menu.

### Update the table

This may need to be called to update the display after programmatically changing the table contents:
```
table.redrawTable()
```

### Sort the table
```
#by column name
table.sortTable(columnName='label')
#by column index
table.sortTable(columnIndex=1) 
```

### Add and delete rows and columns

If column names are not given in the argument then a dialog will pop up in the GUI asking for the name which will likely not be what you want.
```
#add with automatic key
table.addRow()
#add with named key, other keyword arguments are interpreted as column values
table.addRow(keyname, label='abc')
#same as above with dict as column data
table.addRow(keyname, **{'label'='abc'})
table.addColumn(colname)
#delete rows
table.deleteRows(range(0,2))
```

### Change data in individual cells
Simply get a handle on the table model dict and populate the data attribute (a dictionary) directly, then redraw the table.
```
table.model.data[row][col] = value
table.redrawTable()
```
### Change column labels
Column labels can be changed programmatically by accessing the columnlabels attribute of the table model:
```
table.model.columnlabels[colname] = newlabel
```

### Row headers
The row header displays the row index number by default, but it can be used to show the row/record key names if necessary. You may also want to set the row header width to something larger than the default (40). Both these options are supplied in the constructor.
```
table = TableCanvas(master, model, rowheaderwidth=100, showkeynamesinheader=True)
You can hide the row header by setting rowheaderwidth=0.
```
### Set preferences
Preferences for the table can be set on the constructor method, for example:
```
TableCanvas(frame, model=model,
               cellwidth=50, cellbackgr='#E3F6CE',
               thefont="Arial 10",rowheight=16,editable=False,
              rowselectedcolor='yellow',reverseorder=1)
```
Or can be loaded later from an external preferences file:
```
preferences=Preferences('TablesApp')
table.loadPrefs(preferences)
Save and load from a file
table.save('test.table')
table.load('test.table')
```

##  See also

https://github.com/dmnfarrell/pandastable

