# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# datamosru_control.py
# Author: Maxim Dubinin (sim@gis-lab.info)
# Created: 10:30 21.04.2013
# Notes: Occasional cleanup
# ---------------------------------------------------------------------------

import glob
import os
import zipfile
import zlib 

dirs = os.walk('.').next()[1]

for adir in dirs:
    if adir != "_listings":
        os.chdir(adir)
        if os.path.exists(adir + "_temp.csv"): 
        	print("Removed: " + adir + "_temp.csv")
        	os.remove(adir + "_temp.csv")
        if os.path.exists(adir + ".csv") and not os.path.exists(adir + ".zip"):
            print("Zipped: " + adir + ".csv")
            fz = zipfile.ZipFile(adir + ".zip",'w')
            fz.write(adir + ".csv", compress_type=zipfile.ZIP_DEFLATED)
            fz.close()
        os.chdir("..")