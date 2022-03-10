
import sys
sys.path.append('../rffdtd')

import numpy as np
from csg.core import CSG
from rffdtd.csgsave import openzip


def sign(value):
    return 2 * bool(value) - 1


def design():
    thick = 2
    rodend = 13.4
    roddia = 9.52
    rodlen = np.array([ 164 ] * 4)
    rodsep = np.array([ 26.7, 29.3, 26.7 ])
    taph = 20.4
    boxh = 172
    boxb = 19.05

    comment = """\
435 Mhz interdigital butterworth bandpass filter, 16 Mhz bandwidth.
A Simple Way to Desgin Narrowband Interdigital Filters, Ian White, G3SEK.
Radio Communication, Feb 1984, p120.
"""

    with openzip('white', comment=comment) as zf:
        boxl = np.sum(rodsep) + 2 * rodend
        cavity = np.array((boxl, boxb, boxh))

        r = cavity / 2
        inner = CSG.cube(radius=list(r))
        outer = CSG.cube(radius=list(r + thick))

        r = (r[0] + thick, thick / 2, r[2] + thick)
        c = (0, -(boxb + thick) / 2, 0)
        cover = CSG.cube(center=list(c), radius=list(r))
        zf.saveoff('cover-sigma58.71e6', cover)

        box = outer - inner - cover
        zf.saveoff('box-copper', box)
    
        #########################
        # rods
        #########################

        rodpos = np.cumsum(np.hstack((0, rodsep))) - np.sum(rodsep) / 2
        for i in range(len(rodlen)):
            x = rodpos[i]
            z = rodlen[i]
            start = [0,0,0]
            end = [0, 0, -sign(i % 2) * z]
            radius = roddia / 2
            d = CSG.cylinder(radius=radius, start=start, end=end)
            d.translate((x, 0, sign(i % 2) * cavity[2] / 2))
            zf.saveoff(f'rods{i}-brass', d)

        #########################
        # taps
        #########################

        wire = 1  # wire diameter
        w = 1     # port length

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


if __name__ == "__main__":
    design()
   
 
