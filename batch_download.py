# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# batch_download.py
# Author: Maxim Dubinin (sim@gis-lab.info)
# Created: 10:30 01.2.2013
# About: Download all Moscow city data using list updated by datamosru_control.py
# Notes: 
# Usage example: env/bin/python batch_download.py
#            or: env\Scripts\python batch_download.py
# ---------------------------------------------------------------------------

import urllib2
import csv
import os

u = urllib2.urlopen("http://gis-lab.info/data/mos.ru/data/_listings/_general.csv")
fc = csv.DictReader(u,delimiter=";")

for row in fc:
    url = row['URLDOWN']
    try:
        remotefile = urllib2.urlopen(url)
        localfile = open("data/" + row['CODE'] + '.csv', 'wb')
        localfile.write(remotefile.read())
        localfile.close()
        print(url)
    except:
        message = row['CODE'] + " failed to load. Downloading substitute"
        print(message)
        fname = row['CODE'] + ".7z"
        url = "http://gis-lab.info/data/mos.ru/20130929/" + fname

        remotefile = urllib2.urlopen(url)
        localfile = open("data/" + fname, 'wb')
        localfile.write(remotefile.read())
        localfile.close()
        
        cmd = "C:/tools/7-Zip/7z.exe x  -odata data/" + fname
        os.system(cmd)
        os.remove("data/" + fname)