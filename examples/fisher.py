
import sys
sys.path.append('../rffdtd')

import numpy as np
from io import BytesIO
from csg.core import CSG
from rffdtd.csgsave import openzip


def sign(value):
    return 2 * bool(value) - 1


def design(adjust_tap=0, filename=None):
    mm = 25.4
    diam = .250 * mm
    taph = .297 * mm + adjust_tap

    boxh = 2.375 * mm
    rodlen = np.array([ 2.1, 2.1, 2.1 ]) * mm
    rodsep = np.array([ .8, .8 ]) * mm
    rodpos = np.cumsum(np.hstack((0, rodsep))) - np.sum(rodsep) / 2

    thick = 2
    endsep = .8 * mm
    boxb = .75 * mm
    boxl = np.sum(rodsep) + 2 * endsep

    comment = """\
1296 MHz Interdigital 3-Pole Butterworth Filter, 110 MHz Bandwidth.
Interdigital Bandpass Filters for Amateur V.H.F/U.H.F. Applications,
High-Q Filter Construction Made Easy, Reed Fisher, March 1968 QST;
reproduced in the ARRL Handbook 2017, p11.32, figure 11.63.
"""

    filename = filename or BytesIO()
    with openzip(filename, comment=comment) as zf:
        cavity = np.array((boxl, boxb, boxh))

        r = cavity / 2
        inner = CSG.cube(radius=list(r))
        outer = CSG.cube(radius=list(r + thick))

        r = (r[0] + thick, thick / 2, r[2] + thick)
        c = (0, -(boxb + thick) / 2, 0)
        cover = CSG.cube(center=list(c), radius=list(r))
        zf.saveoff('cover-sigma62.11e6', cover)

        box = outer - inner - cover
        zf.saveoff('box-silver', box)
    
        #########################
        # rods
        #########################

        for i in range(len(rodlen)):
            x = rodpos[i]
            z = rodlen[i]
            start = [0,0,0]
            end = [0, 0, -sign(i % 2) * z]
            d = CSG.cylinder(radius=diam/2, start=start, end=end)
            d.translate((x, 0, sign(i % 2) * cavity[2] / 2))
            zf.saveoff(f'rods{i}-brass', d)

        #########################
        # taps
        #########################

        wire = 1
        w = 1

        # first tap

        h = taph - cavity[2] / 2
        x1 = -cavity[0] / 2
        x2 = rodpos[0]

        r = np.array((x2 - x1 - w, w, wire)) / 2
        tap1 = CSG.cube(radius=list(r))
        tap1.translate([x1 + r[0] + w, w / 2, h])
        zf.saveoff('tap1-copper', tap1)

        r = np.array((w, w, w)) / 2
        port1 = CSG.cube(radius=list(r))
        port1.translate((x1 + r[0], w / 2, h))
        zf.saveoff('port1', port1)

        # end tap

        h = -sign(i % 2) * (taph - cavity[2] / 2)
        x1 = rodpos[-1]
        x2 = cavity[0] / 2

        r = np.array((x2 - x1 - w, w, wire)) / 2
        tap2 = CSG.cube(radius=list(r))
        tap2.translate((x2 - r[0] - w, w / 2, h))
        zf.saveoff('tap2-copper', tap2)

        r = np.array((w, w, w)) / 2
        port2 = CSG.cube(radius=list(r))
        port2.translate((x2 - r[0], w / 2, h))
        zf.saveoff('port2', port2)

    return filename


def main(filename, adjust_tap=0):
    import os
    adjust_tap = float(adjust_tap)
    filename = os.path.basename(os.path.splitext(filename)[0])
    design(adjust_tap=adjust_tap, filename=filename)

        
if __name__ == "__main__":
    import sys
    main(*sys.argv[:])
   
 
