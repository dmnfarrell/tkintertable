#!/usr/bin/env python

from Tkinter import *
from Tables import TableCanvas

class App:

    def __init__(self, master):

        tframe = Frame(master)
        tframe.pack()        
        table = TableCanvas(tframe)
        table.createTableFrame()


root = Tk()
app = App(root)
root.mainloop()
