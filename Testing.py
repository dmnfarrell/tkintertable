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
        val = ''.join(random.choice(string.ascii_uppercase) for x in range(n))
        names.append(val)
    return names

def createData():
    """Creare random dict for test data"""
    
    data = {}
    names = createRandomStrings(1000,8)
    cols = 12
    colnames = createRandomStrings(cols,4)    
    for n in names:        
        data[n]={}        
        for c in range(0,cols):
            colname=colnames[c]
            data[n][colname] = round(random.normalvariate(100,100),2)
    return data

def GUITest(root):
    """Setup a table and populate it with data"""
    
    app = App(root) 
    master = app.main
    model = TableModel()
    data = createData()
    model.importDict(data)
    table = TableCanvas(master, model, namefield='name',
                        cellwidth=70, cellbackgr='#E3F6CE',
                        thefont="Arial 10",rowheight=16, rowsperpage=100,
                        rowselectedcolor='yellow', editable=False)
    table.createTableFrame()    
    #remove cols
    model.deleteColumns([0,2,3])
    model.deleteRows(range(0,40))
    table.redrawTable()
    #add rows and cols
    table.add_Row(1)    
    table.add_Column('col6')    
    model.data[1]['col6']='TEST'
    table.redrawTable()
    #change col labels
    model.columnlabels['col6'] = 'new label'    
    #save data
    model.save('test.table')
    #load new data
    model.load('test.table')
    table.redrawTable()
    print 'GUI tests done'
    root.after(2000, root.quit)
    return


def main():
    root = Tk()       
    GUITest(root)    
    root.mainloop()
    #loadSaveTest()

if __name__ == '__main__':
    main()
