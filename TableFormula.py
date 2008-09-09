#!/usr/bin/env python
"""
    Created August 2008
    TablePlotter Class
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

import sys, os
from Tkinter import *
from types import *
import re

class Formula(object):
    """A class to handle formulas in the table"""
    
    def __init__(self):
        
        return
        
    @classmethod
    def isFormula(cls, rec):
        """Evaluate the cell and return true if its a formula"""        
        isform = False
        if type(rec) is DictType:
            if rec.has_key('formula'):
                isform = True        
        return isform
        
    @classmethod
    def getFormula(cls, rec):
        if not type(rec) is DictType:
            return None
        string = rec['formula']
        #print string
        return string
        
    @classmethod
    def doFormula(cls, cellformula, data):
        """Evaluate the formula for a cell and return the result
           takes a formula dict or just the string as input"""        
        if type(cellformula) is DictType:
            cellformula = cellformula['formula']
        #print 'formula', cellformula
        ops = []
        cells = []
        vals = []           
        
        p = re.compile('[*/+-]')
        x = p.split(cellformula)
        for i in x:            
            cells.append(eval(i))
        ops = p.findall(cellformula)
        #print cells, ops  
        #get cell coords into values
        for i in cells:
            if type(i) is TupleType:
                recname = i[0]; col= i[1]
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
            elif type(i) is IntType or type(i) is FloatType:
                vals.append(i)
            else:
                return ''
                
        #print vals, ops
        #finally create expression string to evaluate        
        j=0
        expr = ''
        for v in vals: 
            expr += str(float(v))
            if j < len(ops):
                expr += ops[j]
                j=j+1
        #print 'expr', expr                    
        result = eval(expr)
        return str(round(result,3))
    
