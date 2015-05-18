##ABOUT

Python uses a GUI library called Tkinter as default. This set of classes allows interactive spreadsheet-style tables to be added into an application.
Tkinter is the standard GUI toolkit for python. It is old but still quite popular. There are various libraries that extend Tkinter functionality, such as Pmw, but there is currently no extendable table class for Tkinter.
A sample application using these classes is included in the distribution.

##HOMEPAGE

https://github.com/dmnfarrell/tkintertable

##INSTALLATION

```pip install tkintertable``` or ```easy_install tkintertable```

##GIT CLONE

You can clone the current source using

git clone https://github.com/dmnfarrell/tkintertable.git

##USAGE

Import the class

The core classes are TableCanvas and TableModel. You will likely want to access the TableModel class 
to alter the data programmatically, otherwise the TableCanvas class is all that's required to add to the GUI. 
To import:
```
from tkintertable.Tables import TableCanvas
from tkintertable.TableModels import TableModel
```

Create tables
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
Update the table
This may need to be called to update the display after programmatically changing the table contents:
```
table.redrawTable()
```

Get data into the table
This class is primarily designed to provide an empty table for users to utilise like a spreadsheet,
this data can then be saved and re-loaded. However it is possible to populate the tables by 
importing data from a csv file or python dictionary.

To import from a dictionary we get a handle on the model (or we can create the model 
first and supply it as an argument to the table constructor):
```
model = table.model
model.importDict(data) #can import from a dictionary to populate model
table.redrawTable()
```
where data is a dictionary of the form
```
{'rec1': {'col1': 99.88, 'col2': 108.79, 'label': 'rec1'},
'rec2': {'col1': 99.88, 'col2': 108.79, 'label': 'rec2'},
..
} 
```
One record corresponds to a row in the dictionary. Columns will be created for each child key found in each record.

Importing from a text file can be down interactively from the GUI by right clicking on the table and
choosing 'Import Table' from the popup menu.

Sort the table
```
#by column name
table.sortTable(columnName='label')
#by column index
table.sortTable(columnIndex=1) 
```

Add and delete rows and columns
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

Change data in individual cells
Simply get a handle on the table model and populate the data attribute (a dictionary) directly, then redraw the table.
```
table.model.data[row][col] = value
table.redrawTable()
```
Change column labels
Column labels can be changed programmatically by accessing the columnlabels attribute of the table model:
```
table.model.columnlabels[colname] = newlabel
```

Row headers
The row header displays the row index number by default, but it can be used to show the row/record key names if necessary. You may also want to set the row header width to something larger than the default (40). Both these options are supplied in the constructor.
```
table = TableCanvas(master, model, rowheaderwidth=100, showkeynamesinheader=True)
You can hide the row header by setting rowheaderwidth=0.
```
Set preferences
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

##CHANGES

------
1.1.2
------

* removed defunct code for filtering in model
* can now filter properly from model class
* changed autoaddrows to make much faster for large number of rows
* added notequals operator for filtering

------
1.1.1
------

* changed importdict method to make more efficient for large amounts of data
* added more tests
* fix to autoaddrows
* changes to sort behaviour so that current order is kept when adding/deleting rows
* fix to draw visible multiple row selection only

------
1.1
------

* table now renders large amounts of data by only drawing visible frame
* fixes to filtering bar
* removed paged view
* removed 'name' as a special field
* adding rows from GUI no longer requires rec names
* can now set row header width
* can now show record keys in row header instead of numbers
* row header drawn with same alignment as cells
* renamed most remaining Table.py methods to camel case

------
1.0.3
------

* added new, load and save methods to table directly
* added ImportTable method to table for interactive use
* fixed clicking outside column header bug
* fix to update selected col when redrawing
* added Dialog.py module
* removed simpletabledialog
* tidied up popupmenu

------
1.0.2
------

* restored Filtering.py, filtering works ok
* more improvement to auto resize cols, now checks currrent col sizes
* fixed model.save() method
* added ability to save table, add rows to popup menu
* fixed delete cells button binding
* cell font preferences now uses available fonts from os
* removed unused prefs from dialog

------
1.0.1
------

* add_Column method fixed
* Added ability to align cells left right or center
* Fixed problem of sort order lost when deleting rows
* Sort in descending order works correctly
* Fixes to plotting, but needs reworking or removal
* Added setSelectedCells method so a block of cells can be selected
* Improved text fitting in cells
* Automatic resizing of columns improved

