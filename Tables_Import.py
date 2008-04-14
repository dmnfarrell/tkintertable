"""
    Created January 2008
    Table Model class
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

from Tkinter import *

class TableImporter:
    """Provides import utility methods for the Table and Table Model classes"""
    
    def ImportTableModel(self,parent,filename):
        """Import table data from a comma separated file and create data for a model"""        
        
        import os
        if not os.path.isfile(filename):
            return None

        import csv        
        #takes first row as field names
        dictreader = csv.DictReader(open(filename, "rb"))
        dictdata = {}
        count=0
        for rec in dictreader:            
            dictdata[count]=rec
            count=count+1
        print dictdata 
        
        modeldata={} 
        modeldata['columnnames']=[]
        modeldata['columntypes']={}
        modeldata['columnlabels']={}
        count=0
        modeldata['columnnames'] = dictdata[0].keys()
        
        #check for col types, text or num?
        for col in modeldata['columnnames']:
            '''coltype='text'
            for row in dictdata.keys():
                if 
            modeldata['columntypes'][col]=coltype'''
            modeldata['columntypes'][col] = 'text'
            
        for colname in modeldata['columnnames']:
            modeldata['columnlabels'][colname]=colname          
        
        #now add the data
        for row in dictdata.keys():
            modeldata[row]=dictdata[row]                
            
        print '-------MODELDATA------\n',modeldata          

        return modeldata
        
