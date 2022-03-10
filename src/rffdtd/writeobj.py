
import os
import numpy as np

from .conf import CONDUCTOR


def save(filename, er, sigma, ds):

    def face(lst, ds, name):
        buf = 'f'
        for ix in lst:
            vertex.append('v {:g} {:g} {:g}'.format(*(ix * ds)))
            buf += ' {}'.format(len(vertex))
        if name not in group:
            group[name] = []
        group[name].append(buf)

    def yee(ix, ds, name, color):
        material[name] = tuple(np.array(color) / 255)
        axis = ix[0]
        pos = np.array(ix[1:])
        if axis == 0:
            face((pos, pos + [0,1,1], pos + [0,0,1]), ds, name)
            face((pos, pos + [0,1,1], pos + [0,1,0]), ds, name)
        if axis == 1:
            face((pos, pos + [1,0,1], pos + [1,0,0]), ds, name)
            face((pos, pos + [1,0,1], pos + [0,0,1]), ds, name)
        if axis == 2: 
            face((pos, pos + [1,1,0], pos + [1,0,0]), ds, name)
            face((pos, pos + [1,1,0], pos + [0,1,0]), ds, name)

    group = {}
    material = {}
    vertex = []

    # dielectrics

    for ix in zip(*np.where(er != 1)):
        color = (144, 238, 144) # light green
        name = 'er {:g} {:g}'.format(er[ix], sigma[ix]).replace('+', '')
        yee(ix, ds=ds * 1e3, name=name, color=color)

    # conductors

    for ix in zip(*np.where(np.all([ er == 1, sigma != 0 ], axis=0))):
        color = (143,0,255)  # electric violet
        data = [ k for k in CONDUCTOR if CONDUCTOR[k] == sigma[ix] ]
        name = data[0] if data else 'sigma {:g}'.format(sigma[ix]).replace('+', '')
        if name == 'silver': color = (192,192,192)
        elif name == 'copper': color = (184,115,51)
        elif name == 'gold': color = (255,215,0)
        elif name == 'aluminum': color = (210,217,219)
        elif name == 'brass': color = (115,90,33)
        elif name == 'steel': color = (154,163,163)
        elif name == 'pec': color = (57,57,57)
        elif sigma[ix] < 10: name = 'port {:g}'.format(sigma[ix])
        yee(ix, ds=ds * 1e3, name=name, color=color)

    # write out obj and mtl files

    base, ext = os.path.splitext(filename)
    shortname = os.path.basename(base)

    with open(base + ".obj", "w") as f:    
        print('mtllib {}.mtl'.format(shortname), file=f)
        print('\n'.join(vertex), file=f)
        for name, faces in group.items():
            print('g {}'.format(name), file=f)
            print('usemtl {}'.format(name), file=f)
            print('\n'.join(faces), file=f)

    with open(base + ".mtl", "w") as f:    
        for name, color in material.items():
            print('newmtl {}'.format(name), file=f)
            print('Kd {:g} {:g} {:g}'.format(*color), file=f)


