Python uses a GUI library called Tkinter as default. This set of classes allows interactive spreadsheet-style tables to be added into an application.

_Tkinter_ is the standard GUI toolkit for python. It is old but still quite popular. There are various libraries that extend Tkinter functionality, such as Pmw, but there is currently no extendable table class for Tkinter.

A sample application using these classes is included in the distribution. This shows a possible implementation. Pmw is required to use this application. See the [Usage](http://code.google.com/p/tkintertable/wiki/Usage) page for coding examples.

For API documentation see http://pythonhosted.org/tkintertable/

**Current funcionality:**
  * add, remove rows and columns
  * remove multiple rows, by drag or ctrl-click selection
  * double-click on cells and edit text data, this automatically updates the data held in the model
  * sort by any column
  * relabel columns
  * reorder columns by dragging in the header
  * bindings: select a cell and highlight that row, select multiple rows by dragging, ctrl-clicks or shift-click, move around with arrow keys
  * resize columss dynamically with frame size changes (may be slow for large datasets)
  * set text size, row height, cell width and font in preferences dialog which can be saved
  * set cell colours
  * fill down cells
  * save the table data (as a pickled Python dictionary)
  * export the table as a csv file
  * rendering of very large tables is possible
  * filter/find records using multiple search terms, interactively or programmatically