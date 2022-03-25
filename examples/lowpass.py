
import sys
sys.path.append('../src')

import numpy as np
from csg.core import CSG
from rffdtd.csgsave import openzip, rectangle

comment = """\
Microstrip Lowpass Filter.
The Finite-Differnce Time-Domain Method for Electromagnetics with 
MATLAB Simulations, Elsherbeni and Demir.  Section 6.2.
Reproduced from Application of the Three-Dimensional Finite-Difference
Time-Domain Method to the Analysis of Planar Microstrip Circuits,
David Sheen, Sami Ali, IEEE MTT Vol 38, No 7, July 1990, p.849.
"""

with openzip('lowpass', comment=comment) as zf:

    # bbox
    size = (22.320, 19.472, 4.240)
    r = np.array(size) / 2
    air1 = CSG.cube(center=list(r), radius=list(r + 2))
    zf.saveoff('air', air1)

    # pcb
    er = 2.2
    size = (22.320, 19.472, 0.794)
    r = list(np.array(size) / 2)
    cube1 = CSG.cube(center=[r[0],r[1],r[2]], radius=r)
    zf.saveoff('er{}'.format(er), cube1)

    # ground
    x1 = 0
    y1 = 0
    x2 = 22.320 
    y2 = 19.472
    h = 0
    plane1 = rectangle((x1,y1,h), (x2,y2,h))
    zf.saveoff('ground', plane1)

    # lines
    x1 = 1.000
    y1 = 8.466 
    x2 = 21.320 
    y2 = 11.006
    h = 0.794
    plane2 = rectangle((x1,y1,h), (x2,y2,h))
    zf.saveoff('patch', plane2)

    x1 = 6.650 
    y1 = 0.000 
    x2 = 9.063
    y2 = 8.466
    h = 0.794
    plane3 = rectangle((x1,y1,h), (x2,y2,h))
    zf.saveoff('input', plane3)

    x1 = 13.257
    y1 = 11.006 
    x2 = 15.670 
    y2 = 19.472
    h = 0.794
    plane4 = rectangle((x1,y1,h), (x2,y2,h))
    zf.saveoff('output', plane4)

    # ports
    x1 = 6.650
    z1 = 0.000
    x2 = 9.063 
    z2 = 0.794
    w = 0
    plane5 = rectangle((x1,w,z1), (x2,w,z2))
    zf.saveoff('port1', plane5)

    x1 = 13.257 
    z1 = 0.000 
    x2 = 15.670 
    z2 = 0.794
    w = 19.472 
    plane6 = rectangle((x1,w,z1), (x2,w,z2))
    zf.saveoff('port2', plane6)


