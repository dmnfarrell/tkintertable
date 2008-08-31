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
    
    def __init__(self):

        return

    @classmethod
    def plotXY(cls, x, y,title=None,xlabel=None,ylabel=None):
        """Do xy plot of 2 lists and show correlation"""
        #cc = numpy.corrcoef(numpy.array([x,y]))        
        #print 'correlation coeff.:', cc[1,0]        
        plotfig = pylab.plot(x, y, 'p')
        pylab.title(title)
        pylab.xlabel(xlabel)
        pylab.ylabel(ylabel)        
        #pylab.figtext(0.1,0.2,cc[1,0])
        #plotfig = pylab.plot(x, x, 'r')
        #pylab.show()
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
    def show(cls):
        pylab.show()
        return
    
    @classmethod
    def showStats(cls):

        return

    
   

    
