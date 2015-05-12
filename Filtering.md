**Filtering/searching the table**

Filtering the table simply means searching for a subset of records(rows) with the required field properties. This can be done programmatically or via the widget.

## Interactive filtering ##

Right clicking on the table and choosing 'Filter Records' from the popup menu will display the filtering bar in a separate window below the table. This is a simple interface for adding multiple search conditions that are chained together by boolean operators (AND, OR, NOT). Any number of filters can be added for one search. The '-' button on the right of each filter is used to remove it. When you have entered the required search terms press go and the table will be updated to display just the found rows. Closing the filtering bar restores the whole table.

Filtering bar:

![http://tkintertable.googlecode.com/svn/wiki/images/tkintertablesfiltering.png](http://tkintertable.googlecode.com/svn/wiki/images/tkintertablesfiltering.png)

## Programmatically ##

Filtering data from the table is done via the tabel model. The filter terms are provided as a list of one or more tuples of the form:

**(column, value, operator, boolean)**

where
  * _column_ is the column name
  * _value_ is the integer, float or string value to compare against
  * _operator_ is one of -, !=, contains, <, >, haslength, isnumber
  * _boolean_ determines how this filter is evaluated along with other filters (one of AND, OR, NOT).

example: **filter=[('col1',100,'>','AND')]** means find all rows with a value greater than 100 for col1. In this case the 'AND' is not used as there is only one filter in the list.

Usage:
```
model = table.model
search=[('label','aa','contains','AND'),('col1',100,'>','AND')]
#find a subset of a given column, returns a list
model.getColumnData(columnIndex=0,filters=search)
#multiple columns, returns a list of lists
model.getColumns(names, search)
#same as above but returns a dictionary
model.getDict(names, search)
```