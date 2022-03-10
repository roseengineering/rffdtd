
import os
import numpy as np
from csg.core import CSG
from csg.geom import Polygon, Vertex, Vector
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

atol = 1e-10


# drawing utilities

def polygon(*ngon):
    poly = Polygon([ Vertex(Vector(d)) for d in ngon ])
    solid = CSG.fromPolygons([ poly ])
    return solid


def rectangle(*ngon):
    x0, y0, z0 = np.min(ngon, axis=0)
    x1, y1, z1 = np.max(ngon, axis=0)
    if x0 == x1:
        solid = polygon((x0,y0,z0),(x0,y1,z0),(x0,y1,z1),(x0,y0,z1))
    if y0 == y1:
        solid = polygon((x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1))
    if z0 == z1:
        solid = polygon((x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0))
    return solid


## OBJ and OFF geometry utilities

def totriangles(solid):
    verts, polys, count = solid.toVerticesAndPolygons()
    faces = []
    for p in polys:
        assert(len(p) > 2)
        assert(not np.allclose(verts[p[0]], verts[p[-1]]))
        if len(p) == 3:
            faces.append(p)
        else:
            v3 = len(verts)
            verts.append(tuple(np.mean([ verts[i] for i in p ], axis=0)))
            p.append(p[0])
            for v1, v2 in zip(p[:-1], p[1:]):
                faces.append([ v1, v2, v3 ])
    return np.array(verts), np.array(faces)


def bufferobj(manifest):
    count = 1
    buf = []
    for group, solid in manifest:
        verts, faces = totriangles(solid)
        for v in verts:
            v[np.abs(v) < atol] = 0
            buf.append('v {:.10g} {:.10g} {:.10g}'.format(*v))
        buf.append(f'g {group}')
        for f in faces:
            buf.append('f {} {} {}'.format(*(f + count)))
        count += len(verts)
    return '\n'.join(buf)


def bufferoff(solid):
    verts, faces = totriangles(solid)
    buf = []
    buf.append('OFF')
    buf.append(f'{len(verts)} {len(faces)} 0')
    for v in verts:
        v[np.abs(v) < atol] = 0
        buf.append('{:.10g} {:.10g} {:.10g}'.format(*v))
    for f in faces:
        buf.append('3 {} {} {}'.format(*f))
    return '\n'.join(buf)


# export utilities

def fileext(fileio, ext):
    if type(fileio) is str:
        if os.path.splitext(fileio.lower())[1] != f'.{ext}'.lower():
            fileio = f'{fileio}.{ext}'
    return fileio 


def saveoff(filename, solid):
    buf = bufferoff(solid)
    fileio = fileext(fileio, 'off')
    with open(fileio, "w") as f:
        f.write(buf)


def saveobj(fileio, manifest):
    buf = bufferobj(manifest)
    fileio = fileext(fileio, 'obj')
    with open(fileio, "w") as f:
        f.write(buf)


class openzip(object):
    def __init__(self, fileio, comment=None, noobj=False):
        self.fileio = fileio
        self.comment = comment
        self.noobj = noobj
        self.manifest = []
    def __enter__(self):
        return self
    def __exit__(self, *args):
        fileio = fileext(self.fileio, 'zip') 
        with ZipFile(fileio, mode='w') as zf:
            if self.comment:
                zf.comment = self.comment.encode()
            for filename, solid in self.manifest:
                buf = bufferoff(solid)
                filename = fileext(filename, 'off')
                if filename in zf.namelist():
                    raise ValueError(f'File "{filename}" already exists in zip file.')
                zinfo = ZipInfo(filename)
                zf.writestr(zinfo, buf, compress_type=ZIP_DEFLATED)
        if not self.noobj and type(self.fileio) is str:
            saveobj(self.fileio, self.manifest)
    def saveoff(self, filename, solid):
        self.manifest.append((filename, solid)) 


