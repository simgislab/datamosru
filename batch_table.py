#-*- encoding: utf-8 -*-
#python table.py >table

import csv
import os
import urllib2

f = "_general.csv"
f = urllib2.urlopen("http://gis-lab.info/data/mos.ru/data/_listings/_general.csv")
reader = csv.reader(f, delimiter=";" )
date = "20130626"
date_prev = "20130611"

fon = "table.wiki"
fo = open(fon,"w")

fo.write("""===Скачать данные===

Поле "изменение" показывает сравнение с версией от %s.

Цветами показаны: <span style="background-color:LightGreen">увеличение</span> или <span style="background-color:Salmon">уменьшение</span> количества объектов, <span style="background-color:Yellow">новый набор</span> (отсутствовавший %s)
""" % (date_prev,date_prev))

fo.write("""
{| class="wikitable sortable" border="1" width="100%"
! | Код
! | Описание набора
! | Категория
! | Объектов
! | Изменение
! | Геоданные
! | Оригинал
! | Данные\n""")

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
        geo = "нет"
    else:
        geo = "да"
        
    #count number of objects
    print("data-norm/norm-" + date + "/"+code+".csv")
    if os.path.isfile("data-norm/norm-" + date + "/"+code+".csv") == False:
        print("This file is missing in local folder and skipped in the table")
        numobj = "X"
        style = "bgcolor=\"Yellow\" | "
        change = "еще не импортирован"
        datalink_norm = "еще не импортирован"
        datalink_shp = ""
        datalink_osm = ""
    else:
        f = open("data-norm/norm-" + date + "/"+code+".csv","rb")
        numobj = len(f.readlines()) - 1
        f.close()
        
        #change compared to prev version
        if os.path.isfile("data-prev/"+code+".csv"):
            datafileprev = open("data-prev/"+code+".csv","rb")
            numobjprev = len(datafileprev.readlines()) - 1
            datafileprev.close()
            change = numobj - numobjprev
        else:
            change = ""

        
        
        if change == "":
            style = "bgcolor=\"Yellow\" | "
        elif change > 0:
            style = "bgcolor=\"LightGreen\" | "
            change = "+" + str(change)
        elif change < 0:
            style = "bgcolor=\"Salmon\" | "
        else:
            style = ""
        
    fo.write("""|-
| %s
| %s
| %s
| %s
| %s%s
| %s
| %s
| %s<br>%s<br>%s
""" % (code,
                   descr,
                   cat.decode('utf-8').encode('cp1251'),
                   numobj,
                   style, change,
                   geo, #.decode('utf-8').encode('cp1251'),
                   datalink,
                   datalink_norm,
                   datalink_shp,
                   datalink_osm))

fo.write("""|}""")
fo.close()
