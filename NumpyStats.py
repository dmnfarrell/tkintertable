#!/usr/bin/env python
"""
    Created Oct 2008
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
try:
    import numpy as np
except:
    print 'you need numpy to do statistics'

class TableStats(object):
    """An interface to matplotlib for general plotting and stats, using tk backend"""
    
        
    def __init__(self):
        
        return
        
    def corrcoef(self, x, y):
        cc = np.corrcoef(numpy.array([x,y]))  
        print 'correlation coeff.:', cc[1,0]           
        return cc

    def stdDev(self, x):
        return np.std(x)
         
        
