#-*- encoding: utf-8 -*-
#python table.py >table

import csv
import os

f = "_general.csv"
reader = csv.reader( open( f, "rb"), delimiter=";" )

print """==Таблица данных==
{| class="wikitable sortable" border="1" width="100%"
! | Код
! | Описание набора
! | Категория
! | Объектов
! | Геоданные
! | Оригинал
! | Данные\n"""

first = True
for row in reader:
    if first:
        first = False
        continue
    code,geo,url,urldown,descr,src,cat,added = row
    descr = "[" + url + " " + descr.decode('utf-8').encode('cp1251') + "]"
    datalink = "[http://gis-lab.info/data/mos.ru/" + code + ".7z csv]"
    datalink_norm = "[http://gis-lab.info/data/mos.ru/" + code + "_norm.7z csv_norm]"
    datalink_shp = "[http://gis-lab.info/data/mos.ru/" + code + "_shp.7z shp]"
    datalink_osm = "[http://gis-lab.info/data/mos.ru/" + code + "_osm.7z osm]"
    
    #don't gen shp link for non-geo files
    if geo == "no":
        datalink_shp = ""
        datalink_osm = ""
        
    #count number of objects
    datafile = open("data/"+code+".csv","rb")
    numobj = len(datafile.readlines()) - 1
    datafile.close()
    
    print """|-
| %s
| %s
| %s
| %s
| %s
| %s
| %s<br>%s<br>%s""" % (code,descr,cat.decode('utf-8').encode('cp1251'),numobj,geo.decode('utf-8').encode('cp1251'),datalink,datalink_norm,datalink_shp,datalink_osm)

print """|}"""
