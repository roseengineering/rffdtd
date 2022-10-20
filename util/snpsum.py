
# usage: pass a list of touchstone files on the command line
#
# The utility will sum up the sparameters across the files
# and output the result.  This may be useful for running
# a batch of simulations (each exciting a different set of
# ports) on multiple machines against the same model.
# The results can then be pulled together onto one machine
# and summed up into one sparameter matrix using this utility.

import argparse
import numpy as np
from rffdtd import load_touchstone, save_touchstone

def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='sum up all the s-parameter files provided on the command line')
    parser.add_argument('filename', nargs='+', help='touchstone or .npz file to union together')
    parser.add_argument('--output', help='touchstone or .npz file to write the summed result into')
    return parser.parse_args()


def main(args):
    freq = None
    for fn in args.filenames:
        f, s, z = load_touchstone(fn)
        if freq is None:
            freq = f
            sparam = s 
            zo = z
        else:
            assert(z == zo)
            assert(np.all(f == freq))
            assert(s.shape == sparam.shape)
            sparam += s
    if freq is not None:
        save_touchstone(freq, sparam, filename=args.output)


if __name__ == "__main__":
    main(parse_args())

