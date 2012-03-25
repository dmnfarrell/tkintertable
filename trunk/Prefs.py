"""
    Manage preferences
    Copyright (C) Damien Farrell, Jens Erik Nielsen, University College Dublin 2005
 
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

class Preferences:

    def __init__(self,program,defaults):
        #
        # Find and load the preferences file
        #
        import os
        filename='.'+program+'_preferences'
        dirs=self.get_dirs()
        self.noprefs = False
        try:    
            for ldir in dirs:
                fn=os.path.join(ldir,filename)

                if os.path.isfile(fn):
                    self.load_prefs(fn)
                    self.save_prefs()
                    return
                else:
                    self.noprefs = True
            if self.noprefs == True:
                raise                 
        except:
            #
            # If we didn't find a file then set to default and save
            #
            print 'Did not find preferences!!!'
            self.prefs=defaults.copy()
	    print dirs
            self.pref_file=os.path.join(dirs[0],filename)
            self.prefs['_prefdir']=dirs[0]
            self.prefs['_preffile']=self.pref_file
            self.save_prefs()
            #
            # Can we set more variables?
            #
            # Defaults savedir?
            #
            if os.environ.has_key('HOMEPATH'):
                self.prefs['datadir']=os.environ['HOMEPATH']
            if os.environ.has_key('HOME'):
                self.prefs['datadir']=os.environ['HOME']
            #
            # Use 'my documents' if available
            #

            if hasattr(self.prefs,'datadir'):
                mydocs=os.path.join(self.prefs['datadir'],'My Documents')
                if os.path.isdir(mydocs):
                    self.prefs['datadir']=mydocs

            #
            # Always save
            #
            self.save_prefs()
        return

    #
    # ---------
    #

    def __del__(self):
        #
        # Make sure we save the file when killed
        #
        self.save_prefs()
        return

    #
    # ---------
    #

    def set(self,key,value):
        #
        # Set a key
        #
        self.prefs[key]=value
        self.save_prefs()
        return

    #
    # ---------
    #

    def get(self,key):
        #
        # Get a value
        #
        if self.prefs.has_key(key):
            return self.prefs[key]
        else:
            raise NameError,'No such key'
        return

    #
    # ---------
    #

    def delete(self,key):
        if self.prefs.has_key(key):
            del self.prefs[key]
        else:
            raise 'No such key',key
        self.save_prefs()
        return
    
    #
    # ---------
    #

    def get_dirs(self):
        #
        # Compile a prioritised list of all dirs
        #
        dirs=[]
        keys=['HOME','HOMEPATH','HOMEDRIVE']
        import os, sys
        for key in keys:
            if os.environ.has_key(key):
                dirs.append(os.environ[key])
        #
        if os.environ.has_key('HOMEPATH'):
            #
            # windows
            #
            dirs.append(os.environ['HOMEPATH'])
        #
        # Drives
        #
        possible_dirs=["C:\\","D:\\","/"]
        for pdir in possible_dirs:
            if os.path.isdir(pdir):
                dirs.append(pdir)
        #
        # Check that all dirs are real
        #
        rdirs=[]
        for dirname in dirs:
            if os.path.isdir(dirname):
                rdirs.append(dirname)
        return rdirs

    #
    # ---------
    #

    def load_prefs(self,filename):
        #
        # Load prefs
        #
        self.pref_file=filename
        print "loading prefs from ",self.pref_file
        import pickle
        try:
            fd=open(filename)
            self.prefs=pickle.load(fd)
            fd.close()            
        except:
            fd.close()
            fd=open(filename,'rb')
            self.prefs=pickle.load(fd)
            fd.close()
        return

    #
    # ----------
    #

    def save_prefs(self):
        #
        # Save prefs
        #
        import pickle

        try:
            fd=open(self.pref_file,'w')
        except:
            print 'could not save'
            return

        pickle.dump(self.prefs,fd)
        fd.close()
        return
    
    
