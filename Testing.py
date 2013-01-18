#!/usr/bin/env python

import random, string
from Tkinter import *
from Tables import TableCanvas
from TableModels import TableModel

"""Testing general functionality of tables"""

class App:
    def __init__(self, master):
        self.main = Frame(master)
        self.main.pack(fill=BOTH,expand=1)

def createRandomStrings(l,n):
    """create list of l random strings, each of length n"""
    names = []
    for i in range(l):
        val = ''.join(random.choice(string.ascii_lowercase) for x in range(n))
        names.append(val)
    return names

def createData():
    """Creare random dict for test data"""

    data = {}
    names = createRandomStrings(20,12)
    cols = 5
    colnames = createRandomStrings(cols,5)
    for n in names:
        data[n]={}
        data[n]['label'] = n
    for c in range(0,cols):
        colname=colnames[c]
        vals = [round(random.normalvariate(100,50),2) for i in range(0,len(names))]
        vals = sorted(vals)
        i=0
        for n in names:
            data[n][colname] = vals[i]
            i+=1
    return data

def GUITest(root):
    """Setup a table and populate it with data"""

    app = App(root)
    master = app.main
    model = TableModel()
    data = createData()
    #import after model created
    model.importDict(data)
    table = TableCanvas(master, model, namefield='name',
                        cellwidth=60, cellbackgr='#E3F6CE',
                        thefont=('Arial',12),rowheight=18, rowsperpage=100,
                        rowselectedcolor='yellow', editable=False)
    table.createTableFrame()
    #remove cols
    model.deleteColumns([0])
    model.deleteRows(range(0,2))
    table.redrawTable()
    #add rows and cols
    table.add_Row(1)
    table.add_Column('col6')
    model.data[1]['label']='XHJHJSAHSHJ'
    model.data[1]['col6']='TEST'
    table.redrawTable()
    #change col labels
    model.columnlabels['col6'] = 'new label'
    #set and get selections
    table.setSelectedRow(2)
    table.setSelectedCol(1)
    table.setSelectedCells(1,80,2,4)
    #print table.getSelectionValues()
    #table.plot_Selected(graphtype='XY')
    #save data
    model.save('test.table')
    #load new data
    #model.load('test.table')
    table.redrawTable()
    print 'GUI tests done'
    #root.after(2000, root.quit)
    return


def main():
    root = Tk()
    GUITest(root)
    root.mainloop()
    #loadSaveTest()

if __name__ == '__main__':
    main()
