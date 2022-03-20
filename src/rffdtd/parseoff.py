
import os
import re
import sys
import zipfile
import numpy as np

from .voxzbuf import voxelize
from .conf import CONDUCTOR, MARGIN, PADDING


# basic utilities

def get_fid(fileio):
    if isinstance(fileio, str):
        return open(fileio, 'rb')
    else:
        return fileio


def tofloat(string):
    try:
        return float(string)
    except ValueError:
        pass


def toint(string):
    try:
        return int(string)
    except ValueError:
        pass


# update ports

def to_shape(ix):
    shape = list(max(d) - min(d) + 1 for d in ix)
    return shape


def prism_face(index, axis):
    cmin = tuple(min(d) for d in index[1:])
    cmax = tuple(max(d) for d in index[1:])
    ix = [ d for d in zip(*index) 
           if d[0] != axis and (
              d[axis+1] == cmin[axis] or d[axis+1] == cmax[axis]) ]
    ix = tuple(zip(*ix))
    return ix


def prism_inner(index, axis):
    cmin = tuple(min(d) for d in index[1:])
    cmax = tuple(max(d) for d in index[1:])
    ix = [ d for d in zip(*index) 
           if d[0] != axis and (
              d[axis+1] != cmin[axis] and d[axis+1] != cmax[axis]) ]
    ix = tuple(zip(*ix))
    return ix


def filter_axis(index, axis):
    ix = [ d for d in zip(*index) if d[0] == axis ]
    ix = tuple(zip(*ix))
    return ix


def update_ports(er, sigma, ports):
    for i in range(len(ports)):
        index = ports[i]
        assert(index)   # there should be something here

        # find axis to use
        axis = None
        for ax in range(3):
            ix = prism_face(index, ax)
            # port should be sandwiched between two conductors
            # ALL port face elements must make contact with a conductor
            if ix and np.all(er[ix] == 1) and np.all(sigma[ix] > 1e6):
                axis = ax

        if axis is not None:
            # clear all inner axis-unaligned components
            ix = prism_inner(index, axis)
            if ix:
                er[ix] = 1
                sigma[ix] = 0 
        else:
            print(f'Error: no axis found for port {i+1}, assuming Z.', file=sys.stderr)
            sys.exit(1)
            
        # all indices must form a cube
        ix = filter_axis(index, axis)
        shape = to_shape(ix)
        assert(ix)   # should be something here
        assert(np.prod(shape) == len(ix[0]))

        # reset those indices
        er[ix] = 1
        sigma[ix] = 0
        ports[i] = ix


# off parsing

def load_zip(fileio):
    with get_fid(fileio) as f:
        zf = zipfile.ZipFile(f)
        if zf.comment:
            print(zf.comment.decode().rstrip(), file=sys.stderr)
        mesh = []
        for info in zf.infolist():
            if not info.is_dir():
                ext = os.path.splitext(info.filename)[1]
                if ext.lower() == '.off':
                    with zf.open(info, 'r') as f:
                        mesh.append(load_off(f))
        return mesh


def load_off(fileio):
    with get_fid(fileio) as f:
        filename = f.name
        name = os.path.basename(os.path.splitext(filename)[0])
        vertices = []
        faces = []
        state = 0
        for ln in f:
            ln = ln.strip()
            if not ln or ln[0] == b'#': continue
            d = ln.split()
            aint = tuple(toint(x) for x in d)
            afloat = tuple(tofloat(x) for x in d)
            n = len(d)

            if state == 0:
                # check magic
                if d[0].lower() != b'off': 
                    print('Not an OFF file, ignoring: {}'.format(filename), file=sys.stderr)
                    break
                state = 1
            elif state == 1:
                # read number of vertices and faces
                if n != 3 or None in aint:
                    print('Bad OFF file header, ignoring: {}'.format(filename), file=sys.stderr)
                    break
                num_vertices = aint[0]
                num_faces = aint[1]
                state = 2
            elif state == 2:
                # read vertices
                if n != 3 or None in afloat:
                    print('Bad vertex in OFF file: {}, ignoring'.format(filename), file=sys.stderr)
                    break
                vertices.append(np.array(afloat))
                if len(vertices) == num_vertices:
                    state = 3
            elif state == 3:
                # read faces
                if n < 4 or aint[0] != 3 or None in aint:
                    print('Bad face in OFF file, aborting: {}'.format(filename), file=sys.stderr)
                    break
                faces.append([ vertices[i] for i in aint[1:4] ])
                if len(faces) == num_faces:
                    state = 4
        return { 'name': name, 'filename': filename, 'faces': faces, 'vertices': vertices }


def load_scene(file_list):
    if not isinstance(file_list, (tuple, list)):
        file_list = [ file_list ]
    scene = []
    for f in file_list:
        if type(f) is str:
            ext = os.path.splitext(f.lower())[1]
            if ext == '.off':
                scene.append(load_off(f))
            elif ext == '.zip':
                scene.extend(load_zip(f))
        elif zipfile.is_zipfile(f):
            scene.extend(load_zip(f))
        else:
            scene.append(load_off(f))
    scene = [ d for d in scene if d['faces'] ]
    return scene

# material parsing

def is_port(d):
    return d[0] == 'port'


def is_air(d):
    return d[0] == 'er' and d[1] == 1 and d[2] == 0


def is_material(d):
    return d[0] == 'er' and d[1] != 1


def is_conductor(d):
    return d[0] == 'er' and d[1] == 1 and d[2] != 0


def parse_material(basename):
    name = basename.replace('_', ' ')
    name = name.lower().split('-')[-1]
    d = tuple(name.split()) or ('pec',)

    m = re.search('^([a-zA-Z]+)([\d\.].*)$', d[0])
    if m: d = (m.group(1), m.group(2)) + d[1:]
    tag = d[0]
    afloat = tuple(tofloat(x) for x in d[1:])
    aint = tuple(toint(x) for x in d[1:])
    n = len(d)
    if tag in CONDUCTOR and n == 1:
        return ('er', 1, CONDUCTOR[tag])
    elif tag == 'er' and n == 3 and None not in afloat:
        return ('er', afloat[0], afloat[1])
    elif tag == 'er' and n == 2 and None not in afloat:
        return ('er', afloat[0], 0)
    elif tag == 'sigma' and n == 2 and None not in afloat:
        return ('er', 1, afloat[0])
    elif tag == 'port' and n == 2 and None not in aint:
        assert(aint[0] > 0)
        return ('port', aint[0])
    else:
        return ('er', 1, CONDUCTOR['pec'])
    

# voxelize the scene

def voxelize_scene(scene, ds):
    pitch = ds * 1e3  # assuming OFF files are in millimeters

    # voxelize all meshes
    for d in scene:
        vertices = d['vertices']
        faces = d['faces']
        material = parse_material(d['name'])
        mat_bounds, isplane, matrix = voxelize(
            faces=faces, vertices=vertices, pitch=pitch, skip=is_air(material))
        d['matrix'] = matrix
        d['material'] = material
        d['mat_bounds'] = mat_bounds
        d['isplane'] = isplane 

    # warn of meshes too small to voxelize
    for d in scene:
        filename = d['filename']
        matrix = d['matrix']
        if matrix is not None and not np.any(matrix):
            print(f'Warning: cells too small to voxelize: {filename}', file=sys.stderr)

    # calculate the bounding box of all the meshes together
    cmin = np.min(tuple(d['mat_bounds'][0] for d in scene), axis=0)
    cmax = np.max(tuple(d['mat_bounds'][1] for d in scene), axis=0)
    mat_bounds = [ cmin, cmax ]

    # remove air or dead meshes, air mesh only needed for calculating bounds
    scene = [ d for d in scene if d['matrix'] is not None ]

    # order scene
    scene = ([ d for d in scene if is_material(d['material']) ] +
             [ d for d in scene if is_port(d['material']) ] +
             [ d for d in scene if is_conductor(d['material']) ])

    # calculate the grid origin and size in voxels
    origin = mat_bounds[0] - PADDING - MARGIN
    size = mat_bounds[1] - mat_bounds[0] + 2 * MARGIN + 2 * PADDING
    print('Grid is {:g} x {:g} x {:g} mm in size and composed of {} cells.'.format(
          *(size * pitch), np.prod(size)), file=sys.stderr)

    # initialize er and sigma grid, use a dtype of float32
    dtype = np.float32
    shape = (3,) + tuple(size)
    er = np.ones(shape, dtype=dtype)
    sigma = np.zeros(shape, dtype=dtype)
    return er, sigma, origin, scene


# assign er and sigma values to grid

def as_voxel(matrix, origin):
    ix = set()
    for d in zip(*np.where(matrix)):
        x, y, z = d + origin 
        ix.add((0, x, y, z))
        ix.add((0, x, y + 1, z))
        ix.add((0, x, y + 1, z + 1))
        ix.add((0, x, y, z + 1))

        ix.add((1, x, y, z))
        ix.add((1, x + 1, y, z))
        ix.add((1, x + 1, y, z + 1))
        ix.add((1, x, y, z + 1))

        ix.add((2, x, y, z))
        ix.add((2, x + 1, y, z))
        ix.add((2, x + 1, y + 1, z))
        ix.add((2, x, y + 1, z))
    return tuple(zip(*ix))


def as_plane(matrix, origin, isplane):
    ix = set()
    for d in zip(*np.where(matrix)):
        x, y, z = d + origin
        if isplane == 0:
            ix.add((2, x, y, z))
            ix.add((2, x, y + 1, z))
            ix.add((1, x, y, z))
            ix.add((1, x, y, z + 1))
        if isplane == 1:
            ix.add((2, x, y, z))
            ix.add((2, x + 1, y, z))
            ix.add((0, x, y, z))
            ix.add((0, x, y, z + 1))
        if isplane == 2:
            ix.add((0, x, y, z))
            ix.add((0, x, y + 1, z))
            ix.add((1, x, y, z))
            ix.add((1, x + 1, y, z))
    return tuple(zip(*ix))


def set_yeegrid(er, sigma, scene, origin):
    ports = {}
    for d in scene:
        pos = d['mat_bounds'][0] - origin
        matrix = d['matrix']
        isplane = d['isplane']
        material = d['material']
        ix = (as_voxel(matrix, pos) if isplane is None else 
              as_plane(matrix, pos, isplane))
        if not ix: continue

        if material[0] == 'port':
            i = material[1]
            assert(i not in ports)
            ports[i] = ix
        elif material[0] == 'er':
            er_val = material[1]
            sigma_val = material[2]
            er[ix] = er_val
            sigma[ix] = sigma_val

    assert(len(ports) == 0 or len(ports) == max(ports))
    ports = [ ports[i+1] for i in range(len(ports)) ]
    return ports


# setup pec borders

def set_borders(er, sigma):
    if MARGIN > 0:
        er   [:2,:,:,MARGIN] = 1
        sigma[:2,:,:,MARGIN] = np.inf
        er   [:2,:,:,-MARGIN] = 1
        sigma[:2,:,:,-MARGIN] = np.inf

        er   [::2,:,MARGIN,:] = 1
        sigma[::2,:,MARGIN,:] = np.inf
        er   [::2,:,-MARGIN,:] = 1
        sigma[::2,:,-MARGIN,:] = np.inf

        er   [1:,MARGIN,:,:] = 1
        sigma[1:,MARGIN,:,:] = np.inf
        er   [1:,-MARGIN,:,:] = 1
        sigma[1:,-MARGIN,:,:] = np.inf


def parser(file_list, ds):
    scene = load_scene(file_list)
    er, sigma, origin, scene = voxelize_scene(scene, ds=ds)
    ports = set_yeegrid(er, sigma, scene, origin)
    update_ports(er, sigma, ports)
    set_borders(er, sigma)
    return er, sigma, ports


# export

def as_voxel_export(matrix, origin):
    ix = set()
    for d in zip(*np.where(matrix)):
        x, y, z = d + origin 
        ix.add((0, x, y, z))
        ix.add((0, x + 1, y, z))
        ix.add((1, x, y, z))
        ix.add((1, x, y + 1, z))
        ix.add((2, x, y, z))
        ix.add((2, x, y, z + 1))
    return tuple(zip(*ix))


def as_plane_export(matrix, origin, isplane):
    ix = []
    for d in zip(*np.where(matrix)):
        x, y, z = d + origin
        ix.append((isplane, x, y, z))
    return tuple(zip(*ix))


def set_exportgrid(er, sigma, scene, origin):
    for d in scene:
        pos = d['mat_bounds'][0] - origin
        material = d['material']
        matrix = d['matrix']
        isplane = d['isplane']
        ix = (as_voxel_export(matrix, pos) if isplane is None else 
              as_plane_export(matrix, pos, isplane))
        if not ix: continue

        if material[0] == 'port':
            er_val = 1
            sigma_val = material[1]
        elif material[0] == 'er':
            er_val = material[1]
            sigma_val = material[2]
        er[ix] = er_val
        sigma[ix] = sigma_val


def parser_export(file_list, ds):
    scene = load_scene(file_list)
    er, sigma, origin, scene = voxelize_scene(scene, ds=ds)
    set_exportgrid(er, sigma, scene, origin)
    return er, sigma


