
# usage: pass a list of touchstone files on the command line
#
# The utility will sum up the sparameters across the files
# and output the result.  This may be useful for running
# a batch of simulations (each exciting a different set of
# ports) on multiple machines against the same model.
# The results can then be pulled together onto one machine
# and summed up into one sparameter matrix using this utility.

import sys
sys.path.append('../src')

import numpy as np
from rffdtd import read_touchstone, write_touchstone

def main(*filename):
    freq = None
    for fn in filename:
        f, s = read_touchstone(fn)
        if freq is None:
            freq = f
            sparam = s 
        else:
            assert(np.all(f == freq))
            assert(s.shape == sparam.shape)
            sparam += s
    if freq is not None:
        write_touchstone(freq, sparam)


if __name__ == "__main__":
    main(*sys.argv[1:])

