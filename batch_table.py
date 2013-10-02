#-*- encoding: utf-8 -*-
#Usage example: 
#   lin: env/bin/python batch_table.py
#   win: env\Scripts\python batch_table.py

import csv
import os
import urllib2

f = urllib2.urlopen("http://gis-lab.info/data/mos.ru/data/_listings/_general.csv")
reader = csv.reader(f, delimiter=";" )
date = "20130929"
date_prev = "20130806"

fon = "table.wiki"
fo = open(fon,"w")

fo.write("""===Скачать данные===

Поля:
* "Изменение" - сравнение с версией от %s. Цветами показаны: <span style="background-color:LightGreen">увеличение</span> или <span style="background-color:Salmon">уменьшение</span> количества объектов, <span style="background-color:Yellow">новый набор</span> (отсутствовавший %s)
* "Геоданные, официально" - значится ли, что это геоданные на официальном портале.
* "Геоданные, реально" - есть ли геоданные в последней версии данных, если нет, см. также [http://gis-lab.info/qa/data-mos.html#.D0.A7.D1.82.D0.BE_.D0.B4.D0.B5.D0.BB.D0.B0.D1.82.D1.8C_.D0.B5.D1.81.D0.BB.D0.B8_.D0.B2_.D1.81.D0.B2.D0.B5.D0.B6.D0.B5.D0.B9_.D0.B2.D0.B5.D1.80.D1.81.D0.B8.D0.B8_.D0.BF.D0.BE.D0.BB.D0.BE.D0.BC.D0.B0.D0.BD.D1.8B_.D0.B4.D0.B0.D0.BD.D0.BD.D1.8B.D0.B5.3F тут].
""" % (date_prev,date_prev))

fo.write("""
{| class="wikitable sortable" border="1" width="100%"
! | Код
! | Описание набора
! | Категория
! | Объектов
! | Изменение
! | Геоданные<br>официально
! | Геоданные<br>реально
! | Оригинал
! | Версии
! | Данные
|-
| 
| Все данные
| Все
| 
| 
|
| 
| [http://gis-lab.info/data/mos.ru/csv.7z csv]
|
| [http://gis-lab.info/data/mos.ru/norm.7z csv_norm]<br>[http://gis-lab.info/data/mos.ru/shp.7z shp]<br>[http://gis-lab.info/data/mos.ru/osm.7z osm]
|-
| 
| 
| 
| 
| 
| 
| 
| 
| \n""")

first = True
for row in reader:
    if first:
        first = False
        continue
    code,geo,realgeo,url,urldown,descr,src,cat,added = row
    descr = "[" + url + " " + descr.decode('utf-8').encode('cp1251') + "]"
    datalink = "[http://gis-lab.info/data/mos.ru/" + code + ".7z csv]"
    datalink_norm = "[http://gis-lab.info/data/mos.ru/" + code + "_norm.7z csv_norm]"
    datalink_shp = "[http://gis-lab.info/data/mos.ru/" + code + "_shp.7z shp]"
    datalink_osm = "[http://gis-lab.info/data/mos.ru/" + code + "_osm.7z osm]"
    versions = "[http://gis-lab.info/data/mos.ru/data/" + code + "/archive/ csv]" + "<br>" + "[http://gis-lab.info/data/mos.ru/data/" + code + "/" +code + "_changes.log log]"
    
    #don't gen shp link for non-geo files
    if realgeo == "no":
        datalink_shp = ""
        datalink_osm = ""
        realgeo = "no"
    else:
        realgeo = "yes"
        
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
| %s
| %s
| %s<br>%s<br>%s
""" % (code,
                   descr,
                   cat.decode('utf-8').encode('cp1251'),
                   numobj,
                   style, change,
                   geo, #.decode('utf-8').encode('cp1251'),
                   realgeo,
                   datalink,
                   versions,
                   datalink_norm,
                   datalink_shp,
                   datalink_osm))

fo.write("""|}""")
fo.close()
