
import sys
sys.path.append('../src')

import numpy as np
from csg.core import CSG
from rffdtd.csgsave import openzip, rectangle


comment = """\
Microstrip Microwave Four Port Coupler.
The Finite-Differnce Time-Domain Method for Electromagnetics with 
MATLAB Simulations, Elsherbeni and Demir.  Section 6.2.
Reproduced from Application of the Three-Dimensional Finite-Difference
Time-Domain Method to the Analysis of Planar Microstrip Circuits,
David Sheen, Sami Ali, IEEE MTT Vol 38, No 7, July 1990, p.849.
"""

with openzip('coupler', comment=comment) as zf:

    # air
    size = (16.160, 36.160, 4.240)
    r = np.array(size) / 2
    air1 = CSG.cube(center=list(r), radius=list(r + 2))
    zf.saveoff('air', air1)

    # pcb
    er = 2.2
    size = (16.160, 36.160, 0.794)
    r = np.array(size) / 2
    cube1 = CSG.cube(center=list(r), radius=list(r))
    zf.saveoff('er{}'.format(er), cube1)

    # ground
    x1, y1 = 0, 0
    x2, y2 = 16.160, 36.160
    h = 0
    plane1 = rectangle((x1,y1,h), (x2,y2,h))
    zf.saveoff('ground', plane1)

    # line 1
    x1, y1 = 2.000, 0.000 
    x2, y2 = 4.410, 12.000
    h = 0.794
    plane2 = rectangle((x1,y1,h), (x2,y2,h))
    zf.saveoff('line1', plane2)

    # line 2
    x1, y1 = 11.750, 0.000
    x2, y2 = 14.160, 12.000
    h = 0.794
    plane3 = rectangle((x1,y1,h), (x2,y2,h))
    zf.saveoff('line2', plane3)

    # line 3
    x1, y1 = 2.000, 24.160
    x2, y2 = 4.410, 36.160
    h = 0.794
    plane4 = rectangle((x1,y1,h), (x2,y2,h))
    zf.saveoff('line3', plane4)

    # line 4
    x1, y1 = 11.750, 24.160
    x2, y2 = 14.160, 36.160
    h = 0.794
    plane5 = rectangle((x1,y1,h), (x2,y2,h))
    zf.saveoff('line4', plane5)

    # quarter wave 1 
    x1, y1 = 2.000, 12.000
    x2, y2 = 14.160, 14.410
    h = 0.794
    plane6 = rectangle((x1,y1,h), (x2,y2,h))
    zf.saveoff('qw1', plane6)

    # quarter wave 2
    x1, y1 = 2.000, 21.750
    x2, y2 = 14.160, 24.160
    h = 0.794
    plane7 = rectangle((x1,y1,h), (x2,y2,h))
    zf.saveoff('qw2', plane7)

    # quarter wave 3
    x1, y1 = 1.225, 13.205
    x2, y2 = 5.185, 22.955
    h = 0.794
    plane8 = rectangle((x1,y1,h), (x2,y2,h))
    zf.saveoff('qw3', plane8)

    # quarter wave 4
    x1, y1 = 10.975, 13.205
    x2, y2 = 14.935, 22.955
    h = 0.794
    plane9 = rectangle((x1,y1,h), (x2,y2,h))
    zf.saveoff('qw4', plane9)

    # port 1
    x1, z1 = 2.000, 0.000 
    x2, z2 = 4.410, 0.794
    w = 0
    plane10 = rectangle((x1,w,z1), (x2,w,z2))
    zf.saveoff('port1', plane10)

    # port 2
    x1, z1 = 11.750, 0.000
    x2, z2 = 14.160, 0.794
    w = 0
    plane11 = rectangle((x1,w,z1), (x2,w,z2))
    zf.saveoff('port2', plane11)

    # port 3
    x1, z1 = 11.750, 0.000 
    x2, z2 = 14.160, 0.794
    w = 36.160
    plane12 = rectangle((x1,w,z1), (x2,w,z2))
    zf.saveoff('port3', plane12)

    # port 4
    x1, z1 = 2.000, 0.000 
    x2, z2 = 4.410, 0.794
    w = 36.160
    plane13 = rectangle((x1,w,z1), (x2,w,z2))
    zf.saveoff('port4', plane13)


