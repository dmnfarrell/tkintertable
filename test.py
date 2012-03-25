#!/usr/bin/env python

from Tkinter import *
from Tables import TableCanvas
from TableModels import TableModel

class App:

    def __init__(self, master):

        tframe = Frame(master)
        tframe.pack(fill=BOTH)
        
        d = {1: {'date': 1189774539.345525, 'message': 'Commiting project ', 'author': 'damien'},
             2: {'date': 1189776100.545814, 'message': 'tommytest1', 'author': 'tc'},
             3: {'date': 1189776148.873471, 'message': 'test', 'author': 'elisa'},
             4: {'date': 1189776217.082571, 'message': "barbara's wt and mutant", 'author': 'btconnolly'},
             5: {'date': 1189776969.9782951, 'message': 'Adding a column', 'author': 'nielsen'},
             6: {'date': 1189777126.719934, 'message': 'fergal_test', 'author': 'fomeara'},
             7: {'date': 1189777948.4796059, 'message': 'TEST', 'author': 'elisa'},
             8: {'date': 1189778073.3868899, 'message': 'Adding 7TLN and deleting damen wt', 'author': 'nielsen'},
             9: {'date': 1189778472.5035281, 'message': 'Adding exp. data', 'author': 'nielsen'},
             10: {'date': 1189778553.6663699, 'message': 'Adding NMR tirtaion curve', 'author': 'nielsen'},
             11: {'date': 1189778701.032536, 'message': 'blaah', 'author': 'nielsen'}}

        self.tmodel = TableModel()
        self.tmodel.importDict(d)
        self.table = TableCanvas(tframe, self.tmodel)
        self.table.createTableFrame()
        return

        
root = Tk()
app = App(root)
root.mainloop()

