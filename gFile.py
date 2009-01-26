#!/usr/bin/env python
#
#   gFile.py
#   
#   Copyright 2008-2009 Scott Walton <d38dm8nw81k1ng@gmail.com>
#       
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License (version 2), as
#   published by the Free Software Foundation
#     
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#       
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#   MA 02110-1301, USA.

import fuse
import stat
import os
import sys
import errno
import gNet

from time import time
from subprocess import *

fuse.fuse_python_api = (0,2)

class GStat(object):
    """
    The stat class to use for getattr
    """
    def __init__(self):
        """
        Purpose: Ripped straight from the Fuse SimpleFileSystemHowto wiki
        Returns: Nothing
        """
        self.st_mode = stat.S_IFDIR or 0755 # Might change with |, see what actually works
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 2
        self.st_uid = stat.ST_UID
        self.st_gid = stat.ST_GID
        self.st_size = 4096
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0
        
		
class GFile(fuse.Fuse):
    """ 
    The main Google Docs filesystem class. Most work will be done
    in here.
    """
    def __init__(self, em, pw, *args, **kw):
        """ 
        Purpose: Connect to the Google Docs Server and verify credentials
        em: User's email address
        pw: User's password
        *args: Args to pass to Fuse
        **kw: Keywords to pass to Fuse
        Returns: Nothing
        """
        fuse.Fuse.__init__(self, *args, **kw)
        self.gn = gNet.GNet(em, pw)
        
	
    def getattr(self, path):
        """
        Purpose: Get information about a file
        Args:
            path: Path to file
        Returns: a GStat object with some updated values
        """
        st = GStat()
        pe = path.split('/')[1:] #Leave this for now, see how it goes
        
        #Set access times to now
        st.st_atime = int(time())
        st.st_mtime = st.st_atime
        st.st_ctime = st.st_atime
        
        return st
        
    def readdir(self, path, offset):
        """
        Purpose: Give a listing for ls
        path: Path to the file/directory
        offset: Included for compatibility. Does nothing
        Returns: Directory listing
        """
        dirents = ['.', '..']
        #Pray this works
        for entry in self.gn.get_docs().entry:
            dirents.extend(entry.title.text.encode('UTF-8'))
            
        for r in dirents:
            yield fuse.Direntry(r)
        #It didn't work...

def main():
    usage = """Google Docs FS: Mounts Google Docs files on a local filesystem\n
    gFile.py email password mountpoint
    """ + fuse.Fuse.fusage
    gfs = GFile(sys.argv[1], sys.argv[2], version = "%prog " + fuse.__version__,
        usage = usage, dash_s_do='setsingle')
    gfs.parse(errex=1)
    gfs.main()
    return 0

if __name__ == '__main__':
    main()