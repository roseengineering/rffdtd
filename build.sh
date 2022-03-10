set -v
python res/zip.py -s 1 -o rffdtd src/* src/*/*
echo '#!/usr/bin/env python3' | cat - rffdtd.zip > rffdtd
rm rffdtd.zip
chmod 755 rffdtd
