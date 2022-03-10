
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
import os

def parse_args():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('filename', nargs='+', help='files to zip up')
    parser.add_argument('-o', '--output', help='output zip file')
    parser.add_argument('-s', '--strip', default=0, type=int, help='remove prefix')
    return parser.parse_args()

def fileext(filename, ext):
    if os.path.splitext(filename.lower())[1] != f'.{ext}'.lower():
        filename = f'{filename}.{ext}'
    return filename

def main():
    if args.output:
        output = fileext(args.output, 'zip')
        with ZipFile(output, mode='w') as zf:
            for filename in args.filename:
                if not os.path.isdir(filename):
                    d = filename.split(os.path.sep)
                    zinfo = ZipInfo(os.path.sep.join(d[args.strip:]))
                    with open(filename, 'rb') as f:
                        zf.writestr(zinfo, f.read(), compress_type=ZIP_DEFLATED)

if __name__ == "__main__":
    args = parse_args()
    main()


