#!/usr/bin/env python
"""
    Module for basic plotting inside the TableCanvas. Uses matplotlib.
    Created August 2008
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

from __future__ import absolute_import, print_function
import sys, os
import copy
try:
    from tkinter import *
    from tkinter.ttk import *
except:
    from Tkinter import *
    from ttk import *
if (sys.version_info > (3, 0)):
    from tkinter import filedialog, messagebox, simpledialog
else:
    import tkFileDialog as filedialog
    import tkSimpleDialog as simpledialog
    import tkMessageBox as messagebox

from math import *
try:
    import numpy
except:
    pass

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.font_manager import FontProperties
import pylab


class pylabPlotter(object):
    """An interface to matplotlib for general plotting and stats, using tk backend"""

    colors = ['#0049B4','#C90B11','#437C17','#AFC7C7','#E9AB17','#7F525D','#F6358A',
              '#52D017','#FFFC17','#F76541','#F62217' ]
    linestyles = ['-','--']
    shapes = ['o','-','--',':','.' ,'p','^','<','s','+','x','D','1','4','h']
    legend_positions = ['best', 'upper left','upper center','upper right',
                         'center left','center','center right'
                         'lower left','lower center','lower right']

    graphtypes = ['XY', 'hist', 'bar', 'pie']
    fonts = ['serif', 'sans-serif', 'cursive', 'fantasy', 'monospace']


    def __init__(self):
        #Setup variables
        self.shape = 'o'
        self.grid = 0
        self.xscale = 0
        self.yscale = 0
        self.showlegend = 0
        self.legendloc = 'best'
        self.legendlines = []
        self.legendnames = []
        self.graphtype = 'XY'
        self.datacolors = self.colors
        self.dpi = 300
        self.linewidth = 1.5
        self.font = 'sans-serif'
        self.fontsize = 12
        try:
            self.setupPlotVars()
        except:
            print ('no tk running')
        self.currdata = None
        #self.format = None  #data format
        self.plottitle = ''
        self.plotxlabel = ''
        self.plotylabel = ''
        return

    def plotXY(self, x, y, title='', xlabel=None, ylabel=None, shape=None,
                            clr=None, lw=1):
        """Do x-y plot of 2 lists"""
        if shape == None:
            shape = self.shape
        if clr == None:
            clr = 'b'
        if self.xscale == 1:
            if self.yscale == 1:
                line, = pylab.loglog(x, y, shape, color=clr, linewidth=lw)
            else:
                line, = pylab.semilogx(x, y, shape, color=clr, linewidth=lw)
        elif self.yscale == 1:
            line, = pylab.semilogy(x, y, shape, color=clr, linewidth=lw)
        else:
            line, = pylab.plot(x, y, shape, color=clr, linewidth=lw)
        return line

    def doHistogram(self, data, bins=10):
        """Do a pylab histogram of 1 or more lists"""
        if len(data) == 1:
            ydim=1
        else:
            ydim=2
        dim=int(ceil(len(data)/2.0))
        i=1
        #fig = pylab.figure()
        for r in data:
            if len(r)==0:
                continue
            ax = pylab.subplot(ydim,dim,i)
            print (r)
            for j in range(len(r)):
                r[j] = float(r[j])
            pylab.hist(r,bins=bins)
            i=i+1
        return ax

    def doBarChart(self, x, y, clr):
        """Do a pylab bar chart"""
        #xloc = range(len(x))
        for i in range(len(x)):
            x[i] = float(x[i]);y[i] = float(y[i])
        plotfig = pylab.bar(x, y, color=clr, alpha=0.6)

        return plotfig

    def doPieChart(self, data):
        """Do a pylab bar chart"""
        if len(data) == 1:
            ydim=1
        else:
            ydim=2
        dim=int(ceil(len(data)/2.0))
        i=1
        for r in data:
            if len(r)==0:
                continue
            fig = pylab.subplot(ydim,dim,i)

            for j in range(len(r)):
                r[j] = float(r[j])
            pylab.pie(r)
            i=i+1

        return

    def setData(self, data):
        """Set the current plot data, useful for re-plotting without re-calling
           explicit functions from the parent"""

        self.currdata = data
        return

    def hasData(self):
        """Is there some plot data?"""
        if self.currdata != None and len(self.currdata) > 0:
            return True
        else:
            return False

    def setDataSeries(self, names=None, start=1):
        """Set the series names, for use in legend"""
        self.dataseriesvars=[]
        for i in range(start,len(names)):
           s=StringVar()
           s.set(names[i])
           self.dataseriesvars.append(s)
        #print self.dataseriesvars
        return

    def setFormat(self, format):
        """Set current data format of currdata"""
        self.format = format
        return

    def plotCurrent(self, data=None, graphtype='bar', show=True, guiopts=False,title=None):
        """Re-do the plot with the current options and data"""
        if guiopts == True:
            self.applyOptions()
        if title != None:
            self.settitle(title)
        self.clear()
        currfig = pylab.figure(1)

        if data == None:
            try:
                data = self.currdata
            except:
                print ('no data to plot')
                return
        else:
            self.setData(data)

        seriesnames = []
        legendlines = []
        for d in self.dataseriesvars:
            seriesnames.append(d.get())

        self.graphtype = graphtype
        #do an X-Y plot, with the first list as X xals
        if self.graphtype == 'bar' or len(data) == 1:
            i=0
            pdata = copy.deepcopy(data)
            if len(pdata)>1:
                x = pdata[0]
                pdata.remove(x)
                for y in pdata:
                    if i >= len(self.colors):
                        i = 0
                    c = self.colors[i]
                    self.doBarChart(x, y, clr=c)
                    i+=1
            else:
                y = pdata[0]
                x = range(len(y))
                self.doBarChart(x, y, clr='b')

        elif self.graphtype == 'XY':
            pdata = copy.deepcopy(data)
            x = pdata[0]
            pdata.remove(x)
            i=0
            for y in pdata:
                if i >= len(self.colors):
                    i = 0
                c = self.colors[i]
                line = self.plotXY(x, y, clr=c, lw=self.linewidth)
                legendlines.append(line)
                i+=1

        elif self.graphtype == 'hist':
            self.doHistogram(data)
        elif self.graphtype == 'pie':
            self.doPieChart(data)

        pylab.title(self.plottitle)
        pylab.xlabel(self.plotxlabel)
        pylab.ylabel(self.plotylabel)
        #create legend data
        if self.showlegend == 1:
            pylab.legend(legendlines,seriesnames,
                         loc=self.legendloc)
        if self.grid == 1:
            pylab.grid(True)

        if show == True:
            self.show()
        return currfig

    def clear(self):
        """clear plot"""
        pylab.clf()
        self.legendlines = []
        self.legendnames = []
        return

    def show(self):
        pylab.show()
        return

    def saveCurrent(self, filename=None):
        import tkFileDialog, os
        filename=tkFileDialog.asksaveasfilename(parent=self.plotprefswin,
                                                defaultextension='.png',
                                                filetypes=[("Png file","*.png"),
                                                           ("All files","*.*")])
        if not filename:
            return
        fig = self.plotCurrent(show=False)
        fig.savefig(filename, dpi=self.dpi)
        return

    def setTitle(self, title=None):
        self.plottitle = title

    def setxlabel(self, label=None):
        self.plotxlabel = label

    def setylabel(self, label=None):
        self.plotylabel = label

    def setOptions(self, shape=None, grid=None, xscale=None, yscale=None,
                    showlegend=None, legendloc=None, linewidth=None,
                    graphtype=None, font=None, fontsize=None):
        """Set the options before plotting"""
        if shape != None:
            self.shape = shape
        if grid != None:
            self.grid = grid
        if xscale != None:
            self.xscale = xscale
        if yscale != None:
            self.yscale = yscale
        if showlegend != None:
            self.showlegend = showlegend
        if legendloc != None:
            self.legendloc = legendloc
        if linewidth != None:
            self.linewidth = linewidth
        if graphtype !=None:
            self.graphtype = graphtype
        if font != None:
            self.font = font
        if fontsize != None:
            self.fontsize = fontsize
        pylab.rc("font", family=self.font, size=self.fontsize)
        return

    def setupPlotVars(self):
        """Plot Vars """
        self.pltgrid = IntVar()
        self.pltlegend = IntVar()
        self.pltsymbol = StringVar()
        self.pltsymbol.set(self.shape)
        self.legendlocvar = StringVar()
        self.legendlocvar.set(self.legendloc)
        self.xscalevar = IntVar()
        self.yscalevar = IntVar()
        self.xscalevar.set(0)
        self.yscalevar.set(0)
        self.graphtypevar = StringVar()
        self.graphtypevar.set(self.graphtype)
        self.linewidthvar = DoubleVar()
        self.linewidthvar.set(self.linewidth)
        self.fontvar = StringVar()
        self.fontvar.set(self.font)
        self.fontsizevar = DoubleVar()
        self.fontsizevar.set(self.fontsize)
        #plot specific
        self.plottitlevar = StringVar()
        self.plottitlevar.set('')
        self.plotxlabelvar = StringVar()
        self.plotxlabelvar.set('')
        self.plotylabelvar = StringVar()
        self.plotylabelvar.set('')
        self.dataseriesvars=[]
        return


    def applyOptions(self):
        """Apply the gui option vars to the plotter options"""
        self.setOptions(shape=self.pltsymbol.get(), grid=self.pltgrid.get(),
               xscale=self.xscalevar.get(), yscale=self.yscalevar.get(),
               showlegend = self.pltlegend.get(),
               legendloc = self.legendlocvar.get(),
               linewidth = self.linewidthvar.get(),
               graphtype = self.graphtypevar.get(),
               font = self.fontvar.get(),
               fontsize = self.fontsizevar.get())
        self.setTitle(self.plottitlevar.get())
        self.setxlabel(self.plotxlabelvar.get())
        self.setylabel(self.plotylabelvar.get())
        return

    def plotSetup(self, data=None):
        """Plot options dialog"""

        if data != None:
            self.setData(data)
        self.plotprefswin=Toplevel()
        self.plotprefswin.geometry('+300+450')
        self.plotprefswin.title('Plot Preferences')
        row=0
        frame1=LabelFrame(self.plotprefswin, text='General')
        frame1.grid(row=row,column=0,sticky='news',padx=2,pady=2)
        def close_prefsdialog():
            self.plotprefswin.destroy()

        def choosecolor(x):
            """Choose color for data series"""
            d=x[0]
            c=x[1]
            #print 'passed', 'd',d, 'c',c
            import tkColorChooser
            colour,colour_string = tkColorChooser.askcolor(c,parent=self.plotprefswin)
            if colour != None:
                self.datacolors[d] = str(colour_string)
                cbuttons[d].configure(bg=colour_string)

            return

        Checkbutton(frame1, text="Grid lines", variable=self.pltgrid,
                    onvalue=1, offvalue=0).grid(row=0,column=0, columnspan=2, sticky='news')
        Checkbutton(frame1, text="Legend", variable=self.pltlegend,
                    onvalue=1, offvalue=0).grid(row=1,column=0, columnspan=2, sticky='news')

        Label(frame1,text='Symbol:').grid(row=2,column=0,padx=2,pady=2)
        symbolbutton = Menubutton(frame1,textvariable=self.pltsymbol,
					                relief=GROOVE, width=16, bg='lightblue')
        symbol_menu = Menu(symbolbutton, tearoff=0)
        symbolbutton['menu'] = symbol_menu
        for text in self.shapes:
            symbol_menu.add_radiobutton(label=text,
                                            variable=self.pltsymbol,
                                            value=text,
                                            indicatoron=1)
        symbolbutton.grid(row=2,column=1, sticky='news',padx=2,pady=2)
        row=row+1

        Label(frame1,text='Legend pos:').grid(row=3,column=0,padx=2,pady=2)
        legendposbutton = Menubutton(frame1,textvariable=self.legendlocvar,
					                relief=GROOVE, width=16, bg='lightblue')
        legendpos_menu = Menu(legendposbutton, tearoff=0)
        legendposbutton['menu'] = legendpos_menu
        i=0
        for p in self.legend_positions:
            legendpos_menu.add_radiobutton(label=p,
                                        variable=self.legendlocvar,
                                        value=p,
                                        indicatoron=1)
            i+=1
        legendposbutton.grid(row=3,column=1, sticky='news',padx=2,pady=2)

        Label(frame1,text='Font:').grid(row=4,column=0,padx=2,pady=2)
        fontbutton = Menubutton(frame1,textvariable=self.fontvar,
					                relief=GROOVE, width=16, bg='lightblue')
        font_menu = Menu(fontbutton, tearoff=0)
        fontbutton['menu'] = font_menu
        for f in self.fonts:
            font_menu.add_radiobutton(label=f,
                                            variable=self.fontvar,
                                            value=f,
                                            indicatoron=1)
        fontbutton.grid(row=4,column=1, sticky='news',padx=2,pady=2)
        row=row+1
        Label(frame1,text='Font size:').grid(row=5,column=0,padx=2,pady=2)
        Scale(frame1,from_=8,to=26,resolution=0.5,orient='horizontal',
                            relief=GROOVE,variable=self.fontsizevar).grid(row=5,column=1,padx=2,pady=2)

        Label(frame1,text='linewidth:').grid(row=6,column=0,padx=2,pady=2)
        Scale(frame1,from_=1,to=10,resolution=0.5,orient='horizontal',
                            relief=GROOVE,variable=self.linewidthvar).grid(row=6,column=1,padx=2,pady=2)
        row=0
        scalesframe = LabelFrame(self.plotprefswin, text="Axes Scales")
        scales={0:'norm',1:'log'}
        for i in range(0,2):
            Radiobutton(scalesframe,text='x-'+scales[i],variable=self.xscalevar,
                            value=i).grid(row=0,column=i,pady=2)
            Radiobutton(scalesframe,text='y-'+scales[i],variable=self.yscalevar,
                            value=i).grid(row=1,column=i,pady=2)
        scalesframe.grid(row=row,column=1,sticky='news',padx=2,pady=2)

        row=row+1
        frame=LabelFrame(self.plotprefswin, text='Graph type')
        frame.grid(row=row,column=0,columnspan=2,sticky='news',padx=2,pady=2)
        for i in range(len(self.graphtypes)):
            Radiobutton(frame,text=self.graphtypes[i],variable=self.graphtypevar,
                            value=self.graphtypes[i]).grid(row=0,column=i,pady=2)

        row=row+1
        labelsframe = LabelFrame(self.plotprefswin,text='Labels')
        labelsframe.grid(row=row,column=0,columnspan=2,sticky='news',padx=2,pady=2)
        Label(labelsframe,text='Title:').grid(row=0,column=0,padx=2,pady=2)
        Entry(labelsframe,textvariable=self.plottitlevar,bg='white',relief=GROOVE).grid(row=0,column=1,padx=2,pady=2)
        Label(labelsframe,text='X-axis label:').grid(row=1,column=0,padx=2,pady=2)
        Entry(labelsframe,textvariable=self.plotxlabelvar,bg='white',relief=GROOVE).grid(row=1,column=1,padx=2,pady=2)
        Label(labelsframe,text='Y-axis label:').grid(row=2,column=0,padx=2,pady=2)
        Entry(labelsframe,textvariable=self.plotylabelvar,bg='white',relief=GROOVE).grid(row=2,column=1,padx=2,pady=2)

        if self.currdata != None:
            #print self.dataseriesvars
            row=row+1
            seriesframe = LabelFrame(self.plotprefswin, text="Data Series Labels")
            seriesframe.grid(row=row,column=0,columnspan=2,sticky='news',padx=2,pady=2)
            #self.dataseriesvars=[]
            if len(self.dataseriesvars) == 0:
                self.setDataSeries(range(len(self.currdata)))
            r=1
            sr=1
            cl=0
            for s in self.dataseriesvars:
                Label(seriesframe,text='Series '+str(r)).grid(row=r,column=cl,padx=2,pady=2)
                Entry(seriesframe,textvariable=s,bg='white',
                                          relief=GROOVE).grid(row=r,column=cl+1,padx=2,pady=2)
                r+=1
                if r > 8:
                    r=1
                    cl+=2
            row=row+1
            cbuttons = {}
            frame = LabelFrame(self.plotprefswin, text="Dataset Colors")
            r=1
            cl=0
            sr=1
            ci=0
            for d in range(len(self.dataseriesvars)):
                if d >= len(self.datacolors):
                    self.datacolors.append(self.colors[ci])
                    ci+=1
                c = self.datacolors[d]
                action = lambda x =(d,c): choosecolor(x)
                cbuttons[d]=Button(frame,text='Series '+str(sr),bg=c,command=action)
                cbuttons[d].grid(row=r,column=cl,sticky='news',padx=2,pady=2)
                r+=1
                sr+=1
                if r > 8:
                    r=1
                    cl+=1
            frame.grid(row=row,column=0,columnspan=2,sticky='news',padx=2,pady=2)

        row=row+1
        frame=Frame(self.plotprefswin)
        frame.grid(row=row,column=0,columnspan=2,sticky='news',padx=2,pady=2)
        replotb = Button(frame, text="Replot",
                command=lambda:self.plotCurrent(graphtype=self.graphtype,guiopts=True),
                relief=GROOVE, bg='#99ccff')
        replotb.pack(side=LEFT,fill=X,padx=2,pady=2)
        b = Button(frame, text="Apply", command=self.applyOptions, relief=GROOVE, bg='#99ccff')
        b.pack(side=LEFT,fill=X,padx=2,pady=2)
        b = Button(frame, text="Save", command=self.saveCurrent, relief=GROOVE, bg='#99ccff')
        b.pack(side=LEFT,fill=X,padx=2,pady=2)
        c=Button(frame,text='Close', command=close_prefsdialog, relief=GROOVE, bg='#99ccff')
        c.pack(side=LEFT,fill=X,padx=2,pady=2)
        if self.currdata == None:
            replotb.configure(state=DISABLED)

        self.plotprefswin.focus_set()
        self.plotprefswin.grab_set()

        return
