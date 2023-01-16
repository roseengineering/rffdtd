set -v
python3 res/zip.py -s 1 -o rffdtd src/* src/*/*
echo '#!python3' | cat - rffdtd.zip > rffdtd
rm rffdtd.zip
chmod 755 rffdtd
