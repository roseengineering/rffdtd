
import sys
sys.path.append('../rffdtd')

import os
import numpy as np
from csg.core import CSG
from rffdtd.csgsave import openzip, polygon, rectangle

mm = 25.4

def sign(value):
    return 2 * bool(value) - 1


def design(filename, tap_adj=11, rodlen_adj='3,0,3', rodsep_adj='2,2'):
    tap_adj = float(tap_adj)
    rodlen_adj = np.array([ float(d) for d in rodlen_adj.split(',') ])
    rodsep_adj = np.array([ float(d) for d in rodsep_adj.split(',') ])

    screw = .112 * mm   # 4-40 screw
    diam = .250 * mm
    thick = 2
    boxh = 2.375 * mm
    boxb = .75 * mm
    endsep = .8 * mm

    tap = .297 * mm + tap_adj
    rodlen = np.array([ 2.1, 2.1, 2.1 ]) * mm + rodlen_adj
    rodsep = np.array([ .8, .8 ]) * mm + rodsep_adj

    ###################

    rodpos = np.cumsum(np.hstack((0, rodsep))) - np.sum(rodsep) / 2
    boxl = np.sum(rodsep) + 2 * endsep
    N = len(rodlen)
    comment = '1296 MHz Interdigital 3-Pole Butterworth Filter, 110 MHz BW'
    with openzip(filename, comment=comment) as zf:
        cavity = np.array((boxl, boxb, boxh))

        # create lid 
        r = (cavity[0] / 2 + thick, thick / 2, cavity[2] / 2 + thick)
        cover = CSG.cube(radius=list(r))
        cover.translate((0, -(boxb + thick) / 2, 0))
        zf.saveoff('lid-aluminum', cover)
        #zf.saveoff('cover-sigma62.11e6', cover)

        # create box
        r = cavity / 2
        inner = CSG.cube(radius=list(r))
        outer = CSG.cube(radius=list(r + thick))
        hcube = outer - inner
        box = hcube - cover
        zf.saveoff('box-aluminum', box)

        #########################
        # rods
        #########################

        for i in range(N):
            x = rodpos[i]
            z = cavity[2] / 2
            minspace = 1
            if i % 2 == 0:
                start = [x,0,-z]
                end = [x,0,rodlen[i]-z] 
                solid = CSG.cylinder(radius=diam/2, start=start, end=end)

                # screw
                zscrew = rodlen[i] / 2 + minspace / 2
                start = [x,0,zscrew]
                end = [x,0,z]
                solid += CSG.cylinder(radius=screw/2, start=start, end=end)
                zf.saveoff(f'rods{i+1}-aluminum', solid)

                # tuning port
                solid = rectangle((x-1,0, zscrew), (x+1,0,rodlen[i]-z))
                zf.saveoff(f'port{i+2}', solid)
            else:
                start = [x,0,z]
                end = [x,0,z-rodlen[i]] 
                solid = CSG.cylinder(radius=diam/2, start=start, end=end)

                # screw
                zscrew = -rodlen[i] / 2 - minspace / 2
                start = [x,0, zscrew]
                end = [x,0,-z]
                solid += CSG.cylinder(radius=screw/2, start=start, end=end)
                zf.saveoff(f'rods{i+1}-aluminum', solid)

                # tuning port
                solid = rectangle((x-1,0,zscrew), (x+1,0,z-rodlen[i]))
                zf.saveoff(f'port{i+2}', solid)

        #########################
        # taps
        #########################

        wire = 1
        w = 1

        # first tap

        h = tap - cavity[2] / 2
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

        h = -sign(i % 2) * (tap - cavity[2] / 2)
        x1 = rodpos[-1]
        x2 = cavity[0] / 2

        r = np.array((x2 - x1 - w, w, wire)) / 2
        tap2 = CSG.cube(radius=list(r))
        tap2.translate((x2 - r[0] - w, w / 2, h))
        zf.saveoff('tap2-copper', tap2)

        r = np.array((w, w, w)) / 2
        port2 = CSG.cube(radius=list(r))
        port2.translate((x2 - r[0], w / 2, h))
        zf.saveoff(f'port{N+2}', port2)

    return filename


def main(filename, *d):
    filename = os.path.basename(os.path.splitext(filename)[0])
    design(filename, *d)

        
if __name__ == "__main__":
    import sys
    main(*sys.argv[:])
   
 
