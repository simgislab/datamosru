# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# field_sanitizer_write.py
# Author: Maxim Dubinin (sim@gis-lab.info)
# Created: 23:46 12.02.2013
# Updated: 14:49 13.02.2013
# More: http://gis-lab.info/forum/viewtopic.php?f=17&t=11387&p=71031#p71031
# ---------------------------------------------------------------------------

import glob
import sys
import os
import codecs

def usage():
  '''Show usage synopsis.
  '''
  #python field_sanitizer_write.py data\ data-norm\ fields.csv
  print 'Usage: field_sanitizer_write.py input_folder output_folder fieldsfile'
  sys.exit( 1 )

def find(lst, predicate):
    return (i for i, j in enumerate(lst) if predicate(j)).next()

def subst(ss):
    #ss = ss.replace("\n","")
    ss = ss.replace(u"\ufeff","")
    ss = ss.replace("/","_")
    ss = ss.replace(u"№","N")
    ss = ss.replace(u"«","'")
    ss = ss.replace(u"»","'")
    fields = ss.split(";")
    for field in fields:
        field = field.replace("\n","")
        field = field.replace("\r","")
        ind = infields.index(field.upper())
        outfield = outfields[ind]
        ss = ss.replace(field + ";",outfield + ";")
        ss = ss.replace(field + "\n",outfield + "\n")
        ss = ss.replace(field + "\r\n",outfield + "\r\n")
        del infields[ind]
        del outfields[ind]
    
    #remove trailing ;
    if ss[len(ss)-1] == ";": ss = ss[:-1]
    #ss = ss + "\n"
    return ss

def create_fieldlists(ffn):
    infields = []
    outfields = []
    
    for row in fflist:
        infields.append(row.split(";")[0].upper()) 
        outfields.append(row.split(";")[1].replace("\n","")) 
    return infields,outfields

if __name__ == '__main__':
    args = sys.argv[ 1: ]
    if args is None or len( args ) < 2:
        usage()
    
    foin = os.getcwd() + "\\" + args[ 0 ]
    foout = os.getcwd() + "\\" + args[ 1 ]
    
    #get input and output fields
    
    ffn = args[ 2 ]
    ff = codecs.open(ffn,"r", "utf-8")
    fflist = ff.readlines()
    
    os.chdir(foin)
    
    extensions = ["*.csv"]
    files = []
    for extension in extensions:
        files.extend(glob.glob(extension))

    files_count = len(files)
    
    for fn in files:
        print("Processing... " + fn)
        fi = codecs.open(fn,"r","utf-8")
        strs = fi.readlines()
        fi.close()
        
        #recreate field lists
        infields,outfields = create_fieldlists(ffn)
        
        fo = codecs.open(foout+"\\"+fn,"w","utf-8")
        
        i = 0
        for ss in strs:
            if ss.strip().replace("\r\n","")[-1:] == ";": ss = ss.strip().replace("\r\n","")[:-1] + "\r\n"
            if i == 0:
                ss = subst(ss)
                i = 1
            
            fo.write(ss)
        fo.close()
