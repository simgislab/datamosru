# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# datamosru_control.py
# Author: Maxim Dubinin (sim@gis-lab.info)
# Created: 10:30 01.04.2013
# Notes: To re-initialize data storage clear contents of _listings/_general.csv and data from /data
# ---------------------------------------------------------------------------

import os,sys
import urllib2
from bs4 import BeautifulSoup
import pdb
from datetime import datetime
from collections import namedtuple
import json
import shutil
import codecs
import twitter
import zipfile,zlib
from optparse import OptionParser

def usage():
  '''Show usage synopsis.
  '''
  #python datamosru_control.py /usr/local/www/gis-lab/data/data/mos.ru/data
  print 'Usage: datamosru_control.py data_dir'
  sys.exit( 1 )

def log(message,curdate):
    flog = open(wd + "/log.txt","a")
    str = curdate + " " + datetime.now().strftime("%H-%M-%S") + ":         "
    str = str + message
    flog.write(str + "\n")
    flog.close()

def twit(message,dataset,allowtwit):
    link = "http://gis-lab.info/data/mos.ru/data/" + dataset.code
    shortlink = urllib2.urlopen("http://tinyurl.com/api-create.php?url=%s" % link)
    if allowtwit == True:
            status = api.PostUpdate(message.decode("utf-8") + " " + shortlink.read())

def download_list(listingurl,curdate):
#download list of datasets
    try:
        res = urllib2.urlopen(listingurl)
        localfile = open("_listings/" + curdate + ".html", 'wb')
        localfile.write(res.read())
        localfile.close()
        message = "Listing " + curdate + " saved"
        print(message)
        log(message, curdate)
        res = True
    except:
        message = "Listing " + curdate + " failed to load"
        print(message)
        log(message, curdate)
        res = False
    
    return res
        
def parse_list(listingurl,curdate):
    #prepare csv for saving parsed table
    localfile = open("_listings/" + curdate + ".csv", 'wb')
    localfile.write("CODE;URL;URLDOWN;DESCRIPT;SRC;CAT\n")
    
    lf = open("_listings/" + curdate + ".html") 
    datasets = []
    dataset = namedtuple('dataset', 'code,url,downurl,description,source,cat')
    soup = BeautifulSoup(''.join(lf.readlines()))
    table = soup.find("table", { "class" : "data_table" })
    trs = table.find("tbody").findAll("tr")
    for tr in trs:
        tds = tr.findAll("td")
        url = tds[1].find('a')['href']
        code = url.replace("/datasets/","").split("_")[0]
        url = "http://data.mos.ru" + url
        downurl = "http://data.mos.ru/datasets/download/" + code + "/"
        description = list(tds[1].find('div').strings)[0].strip()
        cat = list(tds[2].strings)[0].strip()
        source = list(tds[3].strings)[0].strip()

        #save to CSV file
        localfile.write(code.encode("utf-8") + ";" + url.encode("utf-8") + ";" + downurl.encode("utf-8") + ";" + description.encode("utf-8") + ";" + source.encode("utf-8") + ";" + cat.encode("utf-8") + "\n")
        
        #save to named tuple
        node = dataset(code,url,downurl,description,source,cat)
        datasets.append(node)
        
    localfile.close()
    print("Total datasets number: " + str(len(datasets)))
    return datasets
    
def full_datasets_list(datasets):
#Takes current datasets and updates general list of datasets with new ones. Needed, because current list of datasets sometimes is incomplete.
    localfile = codecs.open("_listings/_general.csv", 'rb', 'utf-8')
    datasets_all = []
    dataset = namedtuple('dataset', 'code,url,downurl,description,source,cat,added')
    strs = localfile.readlines()[1:]
    localfile.close()
    for str in strs:
        code,url,downurl,description,source,cat,added = str.split(";")
        node = dataset(code,url,downurl,description,source,cat.strip(),added)
        datasets_all.append(node)
    
    for dataset in datasets:
        pos = [i for i, v in enumerate(datasets_all) if v[0] == dataset.code]
        if len(pos) == 0: #Dataset missing in general list, i.e. new dataset is found
            #EVENT
            localfile = open("_listings/_general.csv", 'a')
            localfile.write(dataset.code.encode("utf-8") + ";" + dataset.url.encode("utf-8") + ";" + dataset.downurl.encode("utf-8") + ";" + "\"" + dataset.description.encode("utf-8") + "\"" + ";" + "\"" + dataset.source.encode("utf-8") + "\"" + ";" + "\"" + dataset.cat.encode("utf-8") + "\"" + ";" + curdate + "\n")
            localfile.close()
            change_msg = "Новый набор данных (или первая загрузка): " + dataset.description[0:20:].encode("utf-8") + "... ("+ dataset.code + ") "
            change_msg_tw = "Новые данные: " + dataset.description[0:60:].encode("utf-8") + "... ("+ dataset.code + ") "
            print(change_msg)
            log(change_msg,curdate)
            twit(change_msg_tw,dataset,allowtwit)

            if os.path.exists(dataset.code) == False: os.mkdir(dataset.code)
            if os.path.exists(dataset.code + "/archive") == False: os.mkdir (dataset.code + "/archive")
            f = open(dataset.code + "/" + dataset.code + "_changes.log","w")
            f.write("DATE;FIELDS;RECORDS" + "\n")            
            f.write(curdate + ";0;0" + "\n")
            f.close()
            
            #add missing dataset to full list of datasets as well 
            datasetn = namedtuple('dataset', 'code,url,downurl,description,source,cat,added')
            node = datasetn(dataset.code,dataset.url,dataset.downurl,dataset.description,dataset.source,dataset.cat.strip(),curdate)
            datasets_all.insert(0,node)
            #twit(change_msg,dataset,allowtwit)
             
    return datasets_all

def savelocal(dataset,curdate):
    if os.path.exists(dataset.code) == False: os.mkdir(dataset.code)
    if os.path.exists(dataset.code + "/archive") == False: os.mkdir(dataset.code + "/archive")
    downurl = dataset.downurl
    
    u = urllib2.urlopen(downurl)
    meta = u.info()
    #meta_len = len(meta.getheaders("Content-Length"))
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Kb: %s" % (dataset.code, file_size/1024)
    f = open(dataset.code + "/" + dataset.code + "_temp.csv","wb")
    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,

    f.close()

def compare_with_latest(dataset,curdate):
#compare downloaded dataset with its latest version
    os.chdir(dataset.code)
    change = False
    fnN = dataset.code + "_temp.csv"
    fnC = dataset.code + "_" + curdate + ".csv"
    fnCz = dataset.code + "_" + curdate + ".zip"
    fnP = dataset.code + ".csv"
    fnPz = dataset.code + ".zip"
    logf = dataset.code + "_changes.log"
      
    fN = open(fnN)
    fsN = os.stat(fnN).st_size 
    numfldsN = len(fN.readline().split(";"))
    numrecsN = sum(1 for line in fN)
    
    if os.path.exists(fnP) == False: #first download of the dataset
        shutil.move(fnN, fnP)
        shutil.copy(fnP,"archive/" + dataset.code + "_" + curdate + ".csv")
        fPz = zipfile.ZipFile(fnPz,'w')
        fPz.write(fnP, compress_type=zipfile.ZIP_DEFLATED)
        fPz.close()
        
        f = open(logf,"a")
        f.write(curdate + "," + str(numfldsN) + "," + str(numrecsN) + "\n")
        f.close()

    fP = open(fnP)
    fsP = os.stat(fnP).st_size  
    numfldsP = len(fP.readline().split(";"))
    numrecsP = sum(1 for line in fP)
    
    fN.close()
    fP.close()
    
    if fsN != fsP:
        change = True #file size has changed compared to latest copy
        shortname = dataset.description[0:60:].encode("utf-8") + "... (" + dataset.code.encode("utf-8") + ")"
        rec_change_msg = ""
        fld_change_msg = ""
        
        #check if number of records has changed
        if numrecsN > numrecsP:
            rec_change_msg = ", записи +" + str(numrecsN - numrecsP)
        elif numrecsN < numrecsP:
            rec_change_msg = ", записи -" + str(numrecsP - numrecsN)
        
        #check if number of fields has changed
        if numfldsN > numfldsP:
            fld_change_msg = ", поля +" + str(numfldsN - numfldsP)
        elif numfldsN < numfldsP:
            fld_change_msg = ", поля -" + str(numfldsP - numfldsN)
        
        if rec_change_msg == "" and fld_change_msg == "":
            change_msg = "Обновление: " + shortname + " изменение содержания"
        else:
            change_msg = "Обновление: " + shortname + rec_change_msg + fld_change_msg
        
        f = open(logf,"a")
        f.write(curdate + "," + str(numfldsN) + "," + str(numrecsN) + "\n")
        f.close()
        
        #log everywhere
        print(change_msg)
        log(change_msg,curdate)
        twit(change_msg,dataset,allowtwit)
        
        shutil.move(fnN, fnP)
        shutil.copy(fnP, fnC)
        #save as zip files
        os.remove(fnPz)
        fPz = zipfile.ZipFile(fnPz,'w')
        fPz.write(fnP, compress_type=zipfile.ZIP_DEFLATED)
        fPz.close()
        fCz = zipfile.ZipFile(fnCz,'w')
        fCz.write(fnC, compress_type=zipfile.ZIP_DEFLATED)
        fCz.close()
        os.remove(fnC)
        shutil.move(fnCz, "archive")
    
    os.chdir("..")
    
if __name__ == '__main__':
    usage = "Usage: %prog [-t TWITTER] [-s SPECIFIC ID] input_folder"
    version = "%prog 0.1\nCopyright (C) 2013 Maxim Dubinin (sim@gis-lab.info)"
    description = "Independent control over data.mos.ru data"
    
    # create parser instance
    parser = OptionParser( usage = usage, version = version, description = description )

    # populate options
    parser.add_option( "-t", "--twitter-on", action = "store_true", dest = "allowtwit", default=True, help = "turn twitter on/off [default: %default]" )
    parser.add_option( "-s", "--process-specific-id", action = "store", type = "string", dest = "specific_id", help = "process specific dataset only [default: empty]" )

    parser.set_defaults( allowtwit = True )
    (options, args) = parser.parse_args()
    if len(args) == 0:
        parser.error("working folder is missing")

    #some preparations
    #get twitter credentials for writing http://twitter.com/datamosru
    consumerkey,consumersecret,accesstokenkey,accesstokensecret = open("twitter-credentials.ini").readline().split(",")
    api = twitter.Api(consumer_key=consumerkey, consumer_secret=consumersecret, access_token_key=accesstokenkey, access_token_secret=accesstokensecret)
    
    wd = args[ 0 ]
    allowtwit = options.allowtwit
    specific_id = options.specific_id
    
    os.chdir(wd)

    listingurl = "http://data.mos.ru/datasets"
    if os.path.exists("_listings") == False: os.mkdir("_listings")
    curdate = datetime.now().strftime("%Y%m%d")
    
    success = download_list(listingurl,curdate)
    if success == True:
        #if os.path.exists("data") == False: os.mkdir("data")
        #os.chdir("data")
        datasets = parse_list(listingurl,curdate)
        datasets_all = full_datasets_list(datasets)
        if specific_id is not None:
            message = "Processing specific dataset: %s", specific_id
            log(message, curdate)
            dataset = datasets_all[[i for i, v in enumerate(datasets_all) if v[0] == specific_id][0]]
            savelocal(dataset,curdate)
            change = compare_with_latest(dataset,curdate)
        else:
            for dataset in datasets_all:
                savelocal(dataset,curdate)
                change = compare_with_latest(dataset,curdate)
                if change == True: #do postprocessing for changed datasets
                    print("change")
    else:
        print("Failed to download listing, try again later")
