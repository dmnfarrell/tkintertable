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
try:
    import numpy
except:
    print 'you need numpy to do statistics'
try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.font_manager import FontProperties
    import pylab
except:
    print 'You need matplotlib to plot..'    

class pylabPlotter(object):
    """An interface to matplotlib for plotting Table data"""
    
    colors = ['#0000A0','#FF0000','#437C17','#AFC7C7','#E9AB17','#7F525D','#F6358A']
    linestyles = ['p','-','--']
    shapes = ['p','-','--',':','.' ,'o','^','<','s','+','x','D','1','4','h'] 
    legend_positions = ['best', 'upper left','upper center','upper right',
                         'center left','center','center right'
                         'lower left','lower center','lower right']    
    shape = 'p'
    grid = 1 
    xscale = 0
    yscale = 0
    showlegend = 0
    legendloc = 'best'
    legendlines = []
    legendnames = []
    
    def __init__(self):
        
        return

    @classmethod
    def plotXY(cls, x, y, title='',xlabel=None,ylabel=None):
        """Do xy plot of 2 lists and show correlation"""
        
        if cls.xscale == 1:
            if cls.yscale == 1:
                plotfig = pylab.loglog(x, y, cls.shape)
            else:    
                plotfig = pylab.semilogx(x, y, cls.shape)    
        elif cls.yscale == 1:
            plotfig = pylab.semilogy(x, y, cls.shape) 
        else:                    
            plotfig = pylab.plot(x, y, cls.shape)
        pylab.title(title)
        pylab.xlabel(xlabel)
        pylab.ylabel(ylabel)
        #legend
        cls.legendlines.append(plotfig)
        cls.legendnames.append('A')
        if cls.showlegend == 1:
            pylab.legend(cls.legendlines,cls.legendnames,shadow=True,
                         numpoints=1,loc=cls.legendloc)        
        if cls.grid == 1:
            print 'cls.grid',cls.grid
            pylab.grid(True)
        
        return plotfig

    @classmethod          
    def doHistogram(cls, recs, bins=10, title='', xlabel=None, ylabel=None):
        """Do a pylab histogram of a dict with 1 or more lists"""
        dim=int(ceil(len(recs)/2.0))
        i=1
        for r in recs:
            if len(recs[r])==0:
                continue
            pylab.subplot(2,dim,i)
            i=i+1
            histogram = pylab.hist(recs[r],bins=bins)                         
            pylab.title(r)
            pylab.xlabel(xlabel)
            pylab.ylabel(ylabel)        
        return histogram
        
    @classmethod  
    def clear(cls):
        """clear plot"""
        pylab.clf()
        cls.legendlines = []
        cls.legendnames = []
        return
        
    @classmethod
    def show(cls):
        pylab.show()
        return
    
    @classmethod
    def showStats(cls):
        #cc = numpy.corrcoef(numpy.array([x,y]))  
        #print 'correlation coeff.:', cc[1,0]           
        return
        
    @classmethod  
    def setOptions(cls, shape=None, grid=None, xscale=None, yscale=None,
                    showlegend=None, legendloc=None):
        """Set the options before plotting"""
        if shape != None:
            cls.shape = shape
        if grid != None:
            cls.grid = grid
        if xscale != None:
            cls.xscale = xscale
        if yscale != None:
            cls.yscale = yscale
        if showlegend != None:
            cls.showlegend = showlegend
        if legendloc != None:
            cls.legendloc = legendloc
            
        return
        
