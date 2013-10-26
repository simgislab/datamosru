# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# datamosru_control.py
# Author: Maxim Dubinin (sim@gis-lab.info)
# Created: 10:30 01.04.2013
# Notes: To re-initialize data storage clear contents of _listings/_general.csv and data from /data
# Usage example: env/bin/python datamosru_control.py -q -s 625 /usr/local/www/gis-lab/data/data/mos.ru/data
#            or: env\Scripts\python datamosru_control.py -q -s 625 /usr/local/www/gis-lab/data/data/mos.ru/data
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
import bitly_api
from diff_side_by_side import side_by_side_diff, generate_html

def log(message,curdate):
    flog = open(wd + "/log.txt","a")
    str = curdate + " " + datetime.now().strftime("%H-%M-%S") + ":         "
    str = str + message
    flog.write((str + "\n").encode("utf-8"))
    flog.close()

def add_struct_log(code,change_type):
    f_structlog = open("log_struct.csv","wb")
    csvwriter_structlog = csv.DictWriter(f_structlog)
    csvwriter_structlog.writerow(dict(CODE=dataset.code,
                                      CHANGETYPE=changetype,
                                      DATETIME=datetime.now().strftime("%H-%M-%S")
                                      ))
    csvwriter_structlog.close()

def twit(message,dataset,allowtwit):
    link = "http://gis-lab.info/data/mos.ru/data/" + dataset.code
    shortlink = bitly.shorten(link)['url'] #urllib2.urlopen("http://tinyurl.com/api-create.php?url=%s" % link)
    if allowtwit == True:
        final_msg = message + " data: " + shortlink
        print("twit length: " + str(len(final_msg)))
        status = api.PostUpdate(final_msg)

def download_list(listingurl,curdate):
#download current list of datasets
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
    localfile.write("CODE;GEO;LASTGEO;URL;URLDOWN;DESCRIPT;SRC;CAT\n")
    
    lf = open("_listings/" + curdate + ".html") 
    datasets_current = []
    dataset = namedtuple('dataset', 'code,geo,lastgeo,url,downurl,description,source,cat')
    soup = BeautifulSoup(''.join(lf.readlines()))
    items = soup.findAll("div", { "class" : "item" })
    catsrc = soup.findAll("div", { "class" : "small-11 small-offset-1 medium-3 medium-offset-0 columns" })
    i = 0
    for item in items:
        url = item.find('a')['href']
        code = url.replace("/datasets/","").split("_")[0]
        geo = ""
        lastgeo = ""
        url = "http://data.mos.ru" + url
        downurl = "http://data.mos.ru/datasets/download/" + code + "/"
        description = item.find('a', { "class" : "title" }).strings.next()
        cat = catsrc[i].strings.next()
        source = catsrc[i+1].strings.next()
        i = i + 2

        #save to CSV file
        localfile.write((code + ";" + geo + ";" + lastgeo + ";" + url + ";" + downurl + ";" + description + ";" + source + ";" + cat + "\n").encode("utf-8"))
        
        #save to named tuple
        node = dataset(code,geo,lastgeo,url,downurl,description,source,cat)
        datasets_current.append(node)
        
    localfile.close()
    print("Total datasets number: " + str(len(datasets_current)))
    return datasets_current
    
def full_datasets_list(datasets_current):
#Takes current datasets and updates general list of datasets with new ones. Needed, because current list of datasets sometimes is incomplete.
    localfile = codecs.open("_listings/_general.csv", 'rb', 'utf-8')
    datasets_all = []
    dataset = namedtuple('dataset', 'code,geo,lastgeo,url,downurl,description,source,cat,added')
    strs = localfile.readlines()[1:]
    localfile.close()
    for str in strs:
        code,geo,lastgeo,url,downurl,description,source,cat,added = str.split(";")
        node = dataset(code,geo,lastgeo,url,downurl,description,source,cat.strip(),added)
        datasets_all.append(node)
    
    #check for datasets added in downloaded list compared to general list
    for dataset in datasets_current:
        pos = [i for i, v in enumerate(datasets_all) if v[0] == dataset.code]
        if len(pos) == 0: #Dataset missing in general list, i.e. new dataset is found
            #EVENT - dataset added
            #add a record to full datasets list csv
            localfile = open("_listings/_general.csv", 'a')
            localfile.write((dataset.code + ";" + dataset.geo + ";" + dataset.lastgeo + ";" + dataset.url + ";" + dataset.downurl + ";" + "\"" + dataset.description + "\"" + ";" + "\"" + dataset.source + "\"" + ";" + "\"" + dataset.cat + "\"" + ";" + curdate + "\n").encode("utf-8"))
            localfile.close()
            
            str1 = u"Новые данные: "
            str2 = "... ("+ dataset.code + ") "
            twitlimit = 140 - len(str1) - len(str2) - 37
            change_msg = str1 + dataset.description[0:twitlimit:] + str2
            print(change_msg.encode("utf-8"))
            log(change_msg,curdate)
            twit(change_msg,dataset,allowtwit)

            if os.path.exists(dataset.code) == False: os.mkdir(dataset.code)
            if os.path.exists(dataset.code + "/archive") == False: os.mkdir (dataset.code + "/archive")
            f = open(dataset.code + "/" + dataset.code + "_changes.log","w")
            f.write("DATE;FIELDS;RECORDS" + "\n")            
            f.write(curdate + ";0;0" + "\n")
            f.close()
            
            #add missing dataset to full list of datasets as well 
            datasetn = namedtuple('dataset', 'code,geo,lastgeo,url,downurl,description,source,cat,added')
            node = datasetn(dataset.code,dataset.geo,dataset.lastgeo,dataset.url,dataset.downurl,dataset.description,dataset.source,dataset.cat.strip(),curdate)
            datasets_all.insert(0,node)
             
    return datasets_all

def removed_datasets_list(datasets_current,datasets_all):
    localfile = codecs.open("_listings/_removed.csv", 'rb', 'utf-8')
    datasets_removed = []
    dataset = namedtuple('dataset', 'code,geo,lastgeo,url,downurl,description,source,cat,added')
    strs = localfile.readlines()[1:]
    localfile.close()
    for str in strs:
        code,geo,lastgeo,url,downurl,description,source,cat,added = str.split(";")
        node = dataset(code,geo,lastgeo,url,downurl,description,source,cat.strip(),added)
        datasets_removed.append(node)

    #TODO: handle datasets that were restored
    for dataset in datasets_current:
        pos = [i for i, v in enumerate(datasets_removed) if v[0] == dataset.code]
        if len(pos) != 0: #dataset is present in both current list and removed, meaning it was restored
            str1 = u"Данные восстановлены: "
            str2 = "... ("+ dataset.code + ") "
            twitlimit = 140 - len(str1) - len(str2) - 27
            change_msg = str1 + dataset.description[0:twitlimit:] + str2
            print(change_msg.encode("utf-8"))
            log(change_msg,curdate)
            twit(change_msg,dataset,allowtwit)

            #remove restored dataset from the list of removed, need to edit CSV, otherwise it will keep twiting that the dataset set was restored after every update
            localfile = codecs.open("_listings/_removed.csv", 'rb', 'utf-8')
            tempfile = codecs.open("_listings/_removed_temp.csv", 'wb', 'utf-8')
            for row in localfile.readlines():
                if not row.startswith(dataset.code):
                    tempfile.write(row)
            tempfile.close()
            shutil.move("_listings/_removed_temp.csv", "_listings/_removed.csv")


    #check for datasets removed from current list compared to general list
    for dataset in datasets_all: 
        pos = [i for i, v in enumerate(datasets_current) if v[0] == dataset.code]
        if len(pos) == 0: #Dataset is missing in current list, i.e. dataset is removed
            pos = [i for i, v in enumerate(datasets_removed) if v[0] == dataset.code]
            if len(pos) == 0: #missed dataset was not already announced (otherwise do nothing)
                #EVENT - dataset removed
                #add a record to list of removed.csv
                localfile = open("_listings/_removed.csv", 'a')
                localfile.write((dataset.code + ";" + dataset.geo + ";" + dataset.lastgeo + ";" + dataset.url + ";" + dataset.downurl + ";" + "\"" + dataset.description + "\"" + ";" + "\"" + dataset.source + "\"" + ";" + "\"" + dataset.cat + "\"" + ";" + curdate + "\n").encode("utf-8"))
                localfile.close()
                
                str1 = u"Данные удалены? "
                str2 =  "... ("+ dataset.code + ") "
                twitlimit = 140 - len(str1) - len(str2) - 27
                change_msg = str1 + dataset.description[0:twitlimit:] + str2
                print(change_msg.encode("utf-8"))
                log(change_msg,curdate)
                twit(change_msg,dataset,allowtwit)

                #add removed dataset to the list of removed datasets as well
                datasetn = namedtuple('dataset', 'code,geo,lastgeo,url,downurl,description,source,cat,added')
                node = datasetn(dataset.code,dataset.geo,dataset.lastgeo,dataset.url,dataset.downurl,dataset.description,dataset.source,dataset.cat.strip(),curdate)
                datasets_removed.insert(0,node)


    return datasets_removed

def savelocal(dataset,curdate):
    if os.path.exists(dataset.code) == False: os.mkdir(dataset.code)
    if os.path.exists(dataset.code + "/archive") == False: os.mkdir(dataset.code + "/archive")
    downurl = dataset.downurl.replace("\"","")
    
    try:
        u = urllib2.urlopen(downurl)
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            errmsg = 'We failed to reach a server. ' + 'Reason: ' + str(e.reason)
        elif hasattr(e, 'code'):
            errmsg ='The server couldn\'t fulfill the request. ' + 'Error code: ' + str(e.code)
        msg = "Failed to load " + dataset.code + "." + errmsg
        print msg
        log(msg,curdate)
        success = False
    else:
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
        success = True
    return success

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
    #get date pf the last update
    f = open(logf,"r")
    fdata = f.readlines()
    prevdate = fdata[len(fdata)-1].split(",")[0]
    f.close()
    
    
    fN = open(fnN)  #new version
    try:
        fNcontents = fN.read().decode("utf-8")
    except:
        fN.close()
        fN = open(fnN)
        fNcontents = fN.read().decode("cp1251")
    fN.close()
    fN = open(fnN)
    fsN = os.stat(fnN).st_size 
    numfldsN = len(fN.readline().split(";"))
    numrecsN = sum(1 for line in fN)
    
    if os.path.exists(fnP) == False: #first download of the dataset
        shutil.copy(fnN, fnP)
        shutil.copy(fnP,"archive/" + dataset.code + "_" + curdate + ".csv")
        fPz = zipfile.ZipFile(fnPz,'w')
        fPz.write(fnP, compress_type=zipfile.ZIP_DEFLATED)
        fPz.close()
        
        f = open(logf,"a")
        f.write(curdate + "," + str(numfldsN) + "," + str(numrecsN) + "\n")
        f.close()
    
    fP = open(fnP)  #previous version
    try:
        fPcontents = fP.read().decode("utf-8")
    except:
        fP.close()
        fP = open(fnP)
        fPcontents = fP.read().decode("cp1251")
    fP.close()
    fP = open(fnP)
    fsP = os.stat(fnP).st_size  
    numfldsP = len(fP.readline().split(";"))
    numrecsP = sum(1 for line in fP)
    
    fN.close()
    fP.close()
    
    if fsN != fsP:
        change = True #file size has changed compared to latest copy
        rec_change_msg = ""
        fld_change_msg = ""
        difflink = "http://gis-lab.info/data/mos.ru/data/" + dataset.code + "/archive/diff_" + prevdate + "_" + curdate + ".html"
        diffshortlink = bitly.shorten(difflink)['url']
        
        #check if number of records has changed
        if numrecsN > numrecsP:
            rec_change_msg = u", записи +" + str(numrecsN - numrecsP)
        elif numrecsN < numrecsP:
            rec_change_msg = u", записи -" + str(numrecsP - numrecsN)
        
        #check if number of fields has changed
        if numfldsN > numfldsP:
            fld_change_msg = u", поля +" + str(numfldsN - numfldsP)
        elif numfldsN < numfldsP:
            fld_change_msg = u", поля -" + str(numfldsP - numfldsN)
        
        str1 = u"Обновление: "
        str2 = u" изменение содержания"
        str3 = rec_change_msg + fld_change_msg
        str4 = ", diff: " + diffshortlink
        if rec_change_msg == "" and fld_change_msg == "":
            twitlimit = 140 - len(str1) - len(str2) - len(str4) - 27 - 20
            shortname = dataset.description[0:twitlimit:].replace('"','') + "..(" + dataset.code + ")"
            change_msg = str1 + shortname + str2 + str4
        else:
            twitlimit = 140 - len(str1) - len(str3) - len(str4) - 27 - 20    #7 accounts for ..(520)
            shortname = dataset.description[0:twitlimit:].replace('"','') + "..(" + dataset.code + ")"
            change_msg = str1 + shortname + str3 + str4
        
        f = open(logf,"a")
        f.write(curdate + "," + str(numfldsN) + "," + str(numrecsN) + "\n")
        f.close()

        #get diffs
        arr=[]
        for ss in side_by_side_diff(fPcontents,fNcontents):
            arr.append(ss)

        generate_html(arr,prevdate,curdate)
        
        #log everywhere
        print(change_msg.encode("utf-8"))
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
    
    else: #filesizes are the same, remove temp
        os.remove(fnN)
    
    os.chdir("..")
    
if __name__ == '__main__':
    usage = "Usage: %prog [-t TWITTER] [-s SPECIFIC ID] input_folder"
    version = "%prog 0.1\nCopyright (C) 2013 Maxim Dubinin (sim@gis-lab.info)"
    description = "Independent control over data.mos.ru data"
    
    # create parser instance
    parser = OptionParser( usage = usage, version = version, description = description )

    # populate options
    parser.add_option( "-q", "--quiet", action = "store_false", dest = "allowtwit", default=True, help = "turn twitter on/off [default: %default]" )
    parser.add_option( "-s", "--process-specific-id", action = "store", type = "string", dest = "specific_id", help = "process specific dataset only [default: empty]" )

    #parser.set_defaults( allowtwit = True )
    (options, args) = parser.parse_args()
    if len(args) == 0:
        parser.error("working folder is missing")

    #some preparations
    #get twitter credentials for writing http://twitter.com/datamosru
    consumerkey,consumersecret,accesstokenkey,accesstokensecret = open("twitter-credentials.ini").readline().split(",")
    api = twitter.Api(consumer_key=consumerkey, consumer_secret=consumersecret, access_token_key=accesstokenkey, access_token_secret=accesstokensecret)
    
    #get bitly credentials for url shortening
    api_user,api_key = open("bitly-credentials.ini").readline().split(",")
    bitly = bitly_api.Connection(api_user, api_key)
    
    wd = parser.parse_args()[1][0] #args[ 0 ] strangely this is not working
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
        datasets_current = parse_list(listingurl,curdate)
        datasets_all = full_datasets_list(datasets_current)
        datasets_removed = removed_datasets_list(datasets_current,datasets_all)
        if specific_id is not None:
            message = "Processing specific dataset: " + specific_id
            log(message, curdate)
            dataset = datasets_all[[i for i, v in enumerate(datasets_all) if v[0] == specific_id][0]]
            success = savelocal(dataset,curdate)
            if success == True:
                change = compare_with_latest(dataset,curdate)
        else:
            for dataset in datasets_all:
                success = savelocal(dataset,curdate)
                if success == True:
                    change = compare_with_latest(dataset,curdate)
    else:
        print("Failed to download listing, try again later")
