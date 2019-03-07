cd ..\data
del *.* /Q
copy ..\data-src .
..\gzip *.* --suffix=.gz
cd ..\data-src
