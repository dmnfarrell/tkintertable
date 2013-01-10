#!/usr/bin/env python

import random, string
from Tkinter import *
from Tables import TableCanvas
from TableModels import TableModel

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
    """Creare random dict"""
    data = {}
    names = createRandomStrings(10,8)
    cols = 6
    colnames = createRandomStrings(cols,4)    
    for n in names:        
        data[n]={}        
        for c in range(0,cols):
            colname=colnames[c]
            data[n][colname] = round(random.normalvariate(100,100),2)
    return data

def testGUI(master):
    """Setup a table and populate it with data"""
    tmodel = TableModel()
    data = createData()
    tmodel.importDict(data)
    table = TableCanvas(master, tmodel, namefield='name',
                        cellwidth=70, cellbackgr='#E3F6CE',
                        thefont="Arial 10",rowheight=16, 
                        rowselectedcolor='yellow')
    table.createTableFrame()
    
    table.add_Row('new')    
    table.add_Column('col6')    
    tmodel.data['new']['col6']='TEST'
    table.redrawTable()
    return


root = Tk()
app = App(root)
testGUI(app.main)
root.mainloop()
