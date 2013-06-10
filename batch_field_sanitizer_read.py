# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# batch_field_sanitizer_read.py
# Вытащить из файлов CSV все уникальные названия полей для дальнейшей замены с помощью field_sanitizer_write.py или автоматически на транслит
# Author: Maxim Dubinin (sim@gis-lab.info)
# Created: 23:29 11.02.2013
# More: http://gis-lab.info/forum/viewtopic.php?f=17&t=11387&p=71031#p71031
# ---------------------------------------------------------------------------

import glob
import sys
import os
import codecs
from string import maketrans

def usage():
  '''Show usage synopsis.
  '''
  #field_sanitizer_read.py d:\Programming\Python\data.mos.ru\data\ fields.csv yes yes
  print 'Usage: field_sanitizer_read.py folder output_fields_file translit update'
  sys.exit( 1 )

def create_fieldlists(fon):
    ff = open(fon,"r")
    fflist = ff.readlines()
    ff.close()
    
    infields = []
    outfields = []
    
    for row in fflist:
        infields.append(row.split(";")[0].upper()) #.encode("cp1251"))
    return infields

def translit(ss):
#dron@amerigo 200611031405

   "Russian translit: converts 'привет'->'privet'"
   assert ss is not str, "Error: argument MUST be string"

   table1 = maketrans("абвгдеёзийклмнопрстуфхъыьэАБВГДЕЁЗИЙКЛМНОПРСТУФХЪЫЬЭ","abvgdeezijklmnoprstufh'y'eABVGDEEZIJKLMNOPRSTUFH'Y'E")
   table2 = {'ж':'zh','ц':'ts','ч':'ch','ш':'sh','щ':'sch','ю':'ju','я':'ja','Ж':'Zh','Ц':'Ts','Ч':'Ch','Ш':'Sh','Щ':'Sch','Ю':'Ju','Я':'Ja'}

   for k in table2.keys():
       ss = ss.replace(k,table2[k])

   return ss.translate(table1)
    
if __name__ == '__main__':
    args = sys.argv[ 1: ]
    if args is None or len( args ) < 1:
        usage()

    folder_input = unicode(args[ 0 ],'cp1251')
    fon = args[ 1 ]
    translit_switch = False
    if len(args) >= 3:
        if args[2] == "yes": translit_switch = True
    
    write_mode = "w"
    if len(args) == 4:
        if args[3] == "yes": 
            write_mode = "a"
            #get existing fields
            infields = create_fieldlists(fon)  
    
    fo = codecs.open(fon,write_mode,"utf-8")
    os.chdir(folder_input)
    
    extensions = ["*.csv"]
    files = []
    for extension in extensions:
        files.extend(glob.glob(extension))
    
    fields = []
    for fn in files:
        print("Processing....: " + fn)
        fi = codecs.open(fn,"r", "utf-8")
        
        #all fields in current CSV
        fields_line = fi.readlines()[0].replace(u"\ufeff","").replace("\r\n","")   #признак кодировки текста в UTF-8 в начале строки
        if fields_line[len(fields_line)-1] == ";": fields_line = fields_line[:-1]
        
        fields_cur = fields_line.split(";")
        
        for field in fields_cur:
            field = field.replace("\r\n","")
            field = field.replace("\n","")
            field = field.replace(u"/","_")
            field = field.replace(u"\u2116","N")    #знак номер
            field = field.replace(u"\xab","'")      #открывающая кавычка елочка
            field = field.replace(u"\xbb","'")      #закрывающая кавычка елочка
            try:
                ind = infields.index(field.encode('utf-8').replace("\r\n","").upper())
            except:
                if field.upper() not in fields:
                    fields.append(field.upper())
                    if translit_switch == True:
                        subst = translit(field.encode("cp1251")).upper().replace("0_","").replace("1_","")
                    else: 
                        subst = "substitute_here"
                    fo.write(unicode(field) + ";" + subst + ";" + fn + "\n")
    fo.close()
    print(str(len(fields)) + " fields added")
