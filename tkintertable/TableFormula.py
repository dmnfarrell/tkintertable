#!/usr/bin/env python
"""
    Module implements the Formula class for cell formulae.
    Created Oct 2008
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

#import sys, os
from __future__ import absolute_import, division, print_function
try:
    from tkinter import *
    from tkinter.ttk import *
    from tkinter import filedialog, messagebox, simpledialog
except:
    from Tkinter import *
    from ttk import *
    import tkFileDialog as filedialog
    import tkSimpleDialog as simpledialog
    import tkMessageBox as messagebox
from types import *
import re

class Formula(object):
    """A class to handle formulas functionality in the table"""

    #replace symbols in recnames with strings for proper parsing
    #replace = {'+':'plus', '-':'minus', '*':'mult',

    def __init__(self):

        return

    @classmethod
    def isFormula(cls, rec):
        """Evaluate the cell and return true if its a formula"""
        isform = False
        if type(rec) is dict:
            if 'formula' in rec:
                isform = True
        return isform

    @classmethod
    def getFormula(cls, rec):
        """Get the formula field string"""
        if not type(rec) is dict:
            return None
        string = rec['formula']
        #print string
        return string

    @classmethod
    def readExpression(cls, expr):
        """Get the operands and operators into lists from a string expression"""
        ops = []
        vals = []
        p = re.compile('[()*/+-]')
        x = p.split(expr)
        ops = p.findall(expr)
        #print expr, ops
        for i in x:
            if i == '':
                vals.append(i)
            else:
                vals.append(eval(i))

        #print ops, vals
        return vals, ops

    @classmethod
    def doExpression(cls, vals, ops, getvalues=True):
        """Create an expression string from provided operands and operators"""
        expr = ''
        if getvalues == True:
            for i in range(len(vals)):
                if vals[i] != '':
                    vals[i] = float(vals[i])
        if len(ops)>len(vals):
            while len(ops):
                #use lists as queues
                expr += ops.pop(0)
                if len(vals)!=0:
                    v=vals.pop(0)
                    if v == '':
                        pass
                    else:
                        expr += str(v)
        elif len(ops)<len(vals):
            while len(vals):
                #use lists as queues
                v=vals.pop(0)
                if v == '':
                    pass
                else:
                    expr += str(v)
                if len(ops)!=0:
                    expr += ops.pop(0)
        return expr

    @classmethod
    def doFormula(cls, cellformula, data):
        """Evaluate the formula for a cell and return the result
           takes a formula dict or just the string as input"""
        if type(cellformula) is dict:
            cellformula = cellformula['formula']

        vals = []
        cells, ops = cls.readExpression(cellformula)

        #get cell records into their values
        for i in cells:
            if type(i) is ListType:
                recname, col= i
                if data.has_key(recname):
                    if data[recname].has_key(col):
                        v = data[recname][col]
                        if cls.isFormula(v):
                            #recursive
                            v = cls.doFormula(cls.getFormula(v),data)
                        vals.append(v)
                    else:
                        return ''
                else:
                    return ''
            elif i== '' or type(i) is IntType or type(i) is FloatType:
                vals.append(i)
            else:
                return ''
        if vals == '':
            return ''
        #print vals, ops
        expr = cls.doExpression(vals, ops)
        #print 'expr', expr
        result = eval(expr)
        return str(round(result,3))
