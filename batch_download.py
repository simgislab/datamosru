# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# batch_download.py
# Author: Maxim Dubinin (sim@gis-lab.info)
# Created: 10:30 01.2.2013
# About: Download all Moscow city data using list updated by datamosru_control.py
# Notes: 
# Usage example: python datamosru_control.py -q -s 625 /usr/local/www/gis-lab/data/data/mos.ru/data
# ---------------------------------------------------------------------------

import urllib2
import csv

u = urllib2.urlopen("http://gis-lab.info/data/mos.ru/data/_listings/_general.csv")
fc = csv.DictReader(u,delimiter=";")

for row in fc:
    url = row['URLDOWN']
    print(url)
    remotefile = urllib2.urlopen(url)
    localfile = open("data/" + row['CODE'] + '.csv', 'wb')
    localfile.write(remotefile.read())
    localfile.close()