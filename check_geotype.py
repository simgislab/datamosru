# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# check_geotype.py
# Author: Maxim Dubinin (sim@gis-lab.info)
# Created: 20:15 10.05.2013
# About: Take all CSVs from working folder and determine if EPSG:4326,3857 or local CS was used, also check for WKT and missing coords
# ---------------------------------------------------------------------------

import os
import glob
import csv

output = open("geotypes.csv","wb")
fieldnames = ("CODE","DD", "MERCATOR", "LOCAL", "WKT", "BLANK")
csvwriter_geo = csv.DictWriter(output, fieldnames=fieldnames)
csvwriter_geo.writerow(dict((fn,fn) for fn in fieldnames))

wd = "d:/Programming/Python/datamosru/data-norm"
os.chdir(wd)

inputs = glob.glob("*.csv")
for input in inputs:
    print(input)
    code = input.replace(".csv","")
    f = open(input, 'rb')
    csvreader = csv.DictReader(f,delimiter = ";")
    fields = csvreader.fieldnames
    wkt = 0
    if 'WKT' in fields:
        wkt = 1
    if 'X' in fields and 'Y' in fields:
        dd = 0
        merc = 0
        local = 0
        blank = 0
        for row in csvreader:
            if row['X'] != "" and row['X'] != None:
                xcoord = abs(float(row['X'].replace(",",".")))
                ycoord = abs(float(row['Y'].replace(",",".")))
                
                if int(xcoord) > 31 and int(xcoord) < 40 and int(ycoord) < 60: 
                    dd = 1
                if int(xcoord) > 40 and int(xcoord) < 4000000: 
                    local = 1
                if int(xcoord) > 4000000: 
                    merc = 1
            else:
                blank = 1
        csvwriter_geo.writerow(dict(CODE=code,
                                    DD=dd,
                                    MERCATOR=merc,
                                    LOCAL=local,
                                    WKT=wkt,
                                    BLANK=blank))
    else:
        csvwriter_geo.writerow(dict(CODE=code,
                                    DD=999,
                                    MERCATOR=999,
                                    LOCAL=999,
                                    WKT=999,
                                    BLANK=999))
    f.close()
output.close()