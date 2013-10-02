set date=20130929

cd data
C:\tools\7-Zip\7z.exe a -t7z -m0=lzma -mx=9 -mfb=64 -md=32m -ms=on ..\data-norm\csv.7z *.csv
cd ..

cd data-norm
mkdir norm-%date%
mkdir osm-%date%
mkdir shp-%date%

for %%i in (norm,osm,shp) do (
    copy /y *%%i.* %%i-%date%
    cd %%i-%date%
    c:\tools\7-Zip\7z x *
    del *.7z
    cd ..
    C:\tools\7-Zip\7z.exe a -t7z -m0=lzma -mx=9 -mfb=64 -md=32m -ms=on %%i.7z %%i-%date%)

cd ..