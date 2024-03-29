"""
    Manages preferences for Table class.

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

from __future__ import absolute_import, division, print_function
import os, pickle

class Preferences:

    def __init__(self,program,defaults):

        """Find and load the preferences file"""

        filename='.'+program+'_preferences'
        dirs=self.get_dirs()
        self.noprefs = False
        try:
            for ldir in dirs:
                fn=os.path.join(ldir,filename)
                if os.path.isfile(fn):
                    self.load_prefs(fn)
                    #self.save_prefs()
                    return
                else:
                    self.noprefs = True
            if self.noprefs == True:
                raise
        except:
            # If we didn't find a file then set to default and save
            #print ('Did not find preferences!!!')
            self.prefs=defaults.copy()
            self.pref_file=os.path.join(dirs[0],filename)
            self.prefs['_prefdir']=dirs[0]
            self.prefs['_preffile']=self.pref_file
            self.save_prefs()
            # Defaults savedir?
            if 'HOMEPATH' in os.environ:
                self.prefs['datadir']=os.environ['HOMEPATH']
            if 'HOME' in os.environ:
                self.prefs['datadir']=os.environ['HOME']
            if hasattr(self.prefs,'datadir'):
                mydocs=os.path.join(self.prefs['datadir'],'My Documents')
                if os.path.isdir(mydocs):
                    self.prefs['datadir']=mydocs
            self.save_prefs()
        return

    def __del__(self):
        # Make sure we save the file when killed
        self.save_prefs()
        return

    def set(self,key,value):
        # Set a key
        self.prefs[key]=value
        #self.save_prefs()
        return

    def get(self,key):

        if key in self.prefs:
            return self.prefs[key]
        return


    def delete(self,key):
        if key in self.prefs:
            del self.prefs[key]
        else:
            #raise 'No such key',key
            pass
        self.save_prefs()
        return

    def get_dirs(self):
        """Compile a prioritised list of all dirs"""

        dirs=[]
        keys=['HOME','HOMEPATH','HOMEDRIVE']
        import os, sys
        for key in keys:
            if key in os.environ:
                dirs.append(os.environ[key])

        if 'HOMEPATH' in os.environ:
            # windows
            dirs.append(os.environ['HOMEPATH'])
        # Drives
        possible_dirs=["C:\\","D:\\","/"]
        for pdir in possible_dirs:
            if os.path.isdir(pdir):
                dirs.append(pdir)

        rdirs=[]
        for dirname in dirs:
            if os.path.isdir(dirname):
                rdirs.append(dirname)
        return rdirs

    def load_prefs(self,filename):
        """Load prefs"""

        self.pref_file = filename
        try:
            fd = open(filename,'rb')
            self.prefs = pickle.load(fd)
            #print (self.prefs)
            fd.close()
        except Exception as e:
            print (e)
        return

    def save_prefs(self):
        """Save prefs"""

        try:
            fd = open(self.pref_file,'wb')
            #print (self.prefs)
            pickle.dump(self.prefs, fd, protocol=2)
            fd.close()
        except:
            print ('could not save')
            return
        return
