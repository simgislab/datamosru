# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# batch_process.py
# Author: Maxim Dubinin (sim@gis-lab.info)
# Created: 10:30 01.02.2013
# About: Lots of processing and coversion
# Notes: Heavily Windows based, needs a lot of rework
# Usage example: python process.py
# ---------------------------------------------------------------------------

import glob
import shutil
import os
#import ucsv as csv
import csv
import ogr,osr

def csv2utf(f,fr):
    #convert csv to utf8
    cmd = "c:\\tools\\echo1.exe -ne  \"\xEF\xBB\xBF\" > " + fr + "_utf.csv"
    os.system(cmd)
    cmd = "iconv -f WINDOWS-1251 -t UTF-8 " + f + ">>" + fr + "_utf.csv"
    os.system(cmd)
    os.remove(f)
    shutil.move(fr + "_utf.csv",f)

def strip_whites(f,fr):
    f_csv = open(f,'rb')
    names = csv.reader(f_csv).next()[0].split(";")
    csvreader = csv.DictReader(f_csv,delimiter=";", fieldnames=names)
    
    f_csv_new = open(fr + "_temp.csv",'wb')
    csvwriter = csv.DictWriter(f_csv_new, fieldnames=names,delimiter=";")
    csvwriter.writerow(dict((fn,fn) for fn in csvwriter.fieldnames))
    
    for row in csvreader:
        for k in row.keys():
            try:
                row[k] = row[k].strip()
            except:
                pass
        csvwriter.writerow(row)
    
    f_csv.close()
    f_csv_new.close()
    shutil.move(fr + "_temp.csv",f)
    
def add_latlong(f,fr):
    f_csv = open(f,'rb')
    names = csv.reader(f_csv).next()[0].split(";")
    csvreader = csv.DictReader(f_csv,delimiter=";", fieldnames=names)
    fieldnames = csvreader.fieldnames 

    fieldnames_new = list(fieldnames)
    fieldnames_new.append(u'LAT')
    fieldnames_new.append(u'LON')
    
    f_csv_new = open(fr + "_temp.csv",'wb')
    csvwriter = csv.DictWriter(f_csv_new,fieldnames=fieldnames_new,delimiter=";")
    csvwriter.writerow(dict((fn,fn) for fn in csvwriter.fieldnames))
    
    for row in csvreader:
        row['LAT'],row['LON'] = get_latlon(row)
        csvwriter.writerow(row)
    
    f_csv.close()
    f_csv_new.close()
    shutil.move(fr + "_temp.csv",f)

def get_latlon(row):
    
    x_text = row['X']
    y_text = row['Y']
    
    if row['X'] != "" and row['Y'] != None and row['X'] != "0":
        xcoord = float(x_text.replace(",","."))
        ycoord = float(y_text.replace(",","."))
        srcSR = osr.SpatialReference()
        destSR = osr.SpatialReference()
        dstSR = destSR.ImportFromEPSG(4326)
        
        if abs(int(xcoord)) > 35 and abs(int(xcoord) < 39) and abs(int(ycoord)) < 57: 
            lon,lat = xcoord,ycoord
        if abs(int(xcoord)) < 35 or (abs(int(xcoord)) > 39 and abs(int(xcoord)) < 4000000) or (abs(int(ycoord)) > 57 and abs(int(ycoord)) < 4000000): 
            #srcSR.ImportFromProj4("+proj=tmerc +lat_0=0.116666666667 +lon_0=38.48333333333 +k=1 +x_0=2250000 +y_0=-5700000 +ellps=krass +towgs84=24,-123,-94,0.02,-0.25,-0.13,1.1 +units=m +no_defs")
            srcSR.ImportFromProj4("+proj=tmerc +lat_0=55.66666666666666 +lon_0=37.5 +k=1 +ellps=bessel +towgs84=396,165,557.7,-0.05,0.04,0.01,0 +units=m +no_defs")
            srTrans = osr.CoordinateTransformation(srcSR,destSR)
            lon,lat,z = srTrans.TransformPoint(xcoord, ycoord)
        if abs(int(xcoord)) > 4000000: 
            srcSR.ImportFromEPSG(3857)
            srTrans = osr.CoordinateTransformation(srcSR,destSR)
            lon,lat,z = srTrans.TransformPoint(xcoord, ycoord)
    else:
        lat,lon=0,0
    
    
    return lat,lon
    
def make_csvt(f,fr):
    fcsv = open(f,"r")
    ss = fcsv.readlines()[0]
    fcsv.close()
    
    fields = ss.split(";")
    ss = ""
    for field in fields:
        ss = ss + "\"String(255)\","
    
    fcsvtname = fr + ".csvt"
    fcsvt = open(fcsvtname,"w")
    fcsvt.write(ss[:-1])
    fcsvt.close()

def copy_prj(f,fr):
    fprjname = fr + ".prj"
    shutil.copyfile("../wgs84.prj",fprjname)

def csv_7z(f,fr):
    csv_7zname = fr + "_norm.7z"
    cmd = "C:/tools/7-Zip/7z.exe a -t7z -m0=lzma -mx=9 -mfb=64 -md=32m -ms=on " + csv_7zname + " " + fr + "*"
    os.system(cmd)

def make_vrt(f,fr):
    fvrtname = fr + ".vrt"
    flyrname = fr
    
    vrt_wkt = """<OGRVRTDataSource>
    <OGRVRTLayer name="%s">
        <SrcDataSource relativeToVRT="1">%s</SrcDataSource>
        <LayerSRS>EPSG:3857</LayerSRS>
        <GeometryType>wkbUnknown</GeometryType>
        <GeometryField encoding="WKT" field="WKT"/>
    </OGRVRTLayer>
</OGRVRTDataSource>""" % (flyrname,f)

    vrt_latlon = """<OGRVRTDataSource>
    <OGRVRTLayer name="%s">
        <SrcDataSource relativeToVRT="1">%s</SrcDataSource>
        <LayerSRS>EPSG:4326</LayerSRS>
        <GeometryType>wkbUnknown</GeometryType>
        <GeometryField encoding="PointFromColumns" x="LON" y="LAT"/>
    </OGRVRTLayer>
</OGRVRTDataSource>""" % (flyrname,f)
    
    fcsvt = open(fvrtname,"w")
    fcsvt.write(vrt_latlon)
    fcsvt.close()

def make_shp(f,fr):
    #previous version, to be removed if new version is ok
    #if "WKT" in ss:
    #    flyrname = fr
    #    fshpname = fr + ".shp"
    #    cmd = "ogr2ogr -lco ENCODING=UTF-8 -s_srs \"EPSG:3857\" -t_srs \"EPSG:4326\" " + fshpname + " " + f
    #    print(cmd)
    #    os.system(cmd)

    flyrname = fr
    fshpname = fr + ".shp"
    cmd = "ogr2ogr -lco ENCODING=UTF-8 " + fshpname + " " + fr + ".vrt"
    print(cmd)
    os.system(cmd)
    
    shp_7zname = f.replace(".csv","_shp.7z")
    cmd = "C:/tools/7-Zip/7z.exe a -t7z -m0=lzma -mx=9 -mfb=64 -md=32m -ms=on " + shp_7zname + " " + flyrname+".shp " + flyrname+".shx " + flyrname+".dbf " + flyrname+".prj " + flyrname+".cpg" 
    os.system(cmd)

def make_osm(f,fr):
    cmd = "python c:\gis\osm2shp\ogr2osm.py " + fr + ".vrt"
    os.system(cmd)

def osm_7z(f,fr):
    osm_7zname = fr + "_osm.7z"
    if os.path.isfile(fr + ".osm"):
        cmd = "C:/tools/7-Zip/7z.exe a -t7z -m0=lzma -mx=9 -mfb=64 -md=32m -ms=on " + osm_7zname + " " + fr + ".osm"
        os.system(cmd)

if __name__ == '__main__':
    #working folder, todo: move to params
    os.chdir("data-norm")
    for f in glob.glob("*.csv"):
    
        fr = f.replace(".csv","") #short name for easy filenames generation
        
        #Convert CSV from CP1251 to UTF-8 without BOM
        #csv2utf(f,fr)
        
        #Strip all whitespaces
        strip_whites(f,fr)
        
        #Create CSVT file for field types
        make_csvt(f,fr)
        
        fcsv = open(f,"r")
        fields = fcsv.readlines()[0]
        fcsv.close()

        if "X;Y" in fields:
            #Add LAT and LON fields
            add_latlong(f,fr)
        
            #Add *.prj file
            copy_prj(f,fr)
            
            #Add *.vrt file
            make_vrt(f,fr)
            
        #Compress
        csv_7z(f,fr)
            
        if "X;Y" in fields:
            #Convert to ESRI Shape
            make_shp(f,fr)
            
            #Convert to OSM XML using ogr2osm
            make_osm(f,fr)
            
            osm_7z(f,fr)
        
        #Clean up
        for fd in glob.glob(fr + ".*"):
            os.remove(fd) 