
import numpy as np

atol = 10


def projection(ray, matrix, faces, normals, shape, origin, pitch):
    axis = ray.index(1)
    ray = np.array(ray)
    dim = np.where(ray == 0)

    index = []
    for j in range(shape[dim][1]):
        for i in range(shape[dim][0]):
            point = (i, j)
            P = origin * pitch
            P[dim] += np.array(point) * pitch + pitch / 2

            # find all intersections of ray with faces
            divisors = np.dot(normals, ray)
            ix = np.nonzero(divisors)
            divisors = divisors[ix]
            normals = normals[ix]
            faces = faces[ix]

            t = (np.einsum('ij,ij->i', normals, faces[:,0]) - 
                 np.dot(normals, P)) / divisors
            Q = P + t[:,np.newaxis] * ray
            u = np.cross(faces[:,1] - Q, faces[:,2] - Q)
            v = np.cross(faces[:,2] - Q, faces[:,0] - Q)
            w = np.cross(faces[:,0] - Q, faces[:,1] - Q)
            data = t[np.where(np.all((
                     np.round(np.einsum('ij,ij->i', u, v), atol) >= 0, 
                     np.round(np.einsum('ij,ij->i', u, w), atol) >= 0), axis=0))]

            # carve out empty space
            minmax = (( np.min(data) / pitch, np.max(data) / pitch )
                      if len(data) else (0, 0))
            zmin, zmax = np.rint(minmax).astype(int)
            cols = np.arange(shape[axis], dtype=int)
            cols = cols[np.where(np.any((cols < zmin, cols >= zmax), axis=0))]

            # set empty space to false
            for k in cols:
                ix = np.zeros(3, dtype=int)
                ix[dim] = point
                ix[axis] = k
                index.append(ix)
    if index:
        matrix[tuple(zip(*index))] = False


def voxelize(faces, vertices, pitch, skip=False):
    cmin = np.min(vertices, axis=0)
    cmax = np.max(vertices, axis=0)
    faces = np.array(faces)

    isplane = np.where(np.isclose(cmin, cmax))[0]
    bounds = np.rint([ cmin / pitch, cmax / pitch ]).astype(int)
    origin = bounds[0]
    shape = bounds[1] - bounds[0]
    axis = None
    matrix = None
    if not skip:
        if len(isplane) == 0:
            matrix = np.ones(shape, dtype=bool)
            normals = np.cross(faces[:,1] - faces[:,0], faces[:,2] - faces[:,0])
            kw = { 'matrix':matrix, 'shape':shape, 
                   'faces':faces, 'normals':normals,
                   'origin':origin, 'pitch':pitch }
            projection((0, 1, 0), **kw) 
            projection((1, 0, 0), **kw)
            projection((0, 0, 1), **kw)
        elif len(isplane) == 1:
            isplane = np.where(np.isclose(cmin, cmax))[0]
            shape[isplane] = 1
            matrix = np.ones(shape, dtype=bool)
            axis = isplane[0]
    mat_bounds = [ origin, origin + shape ]
    return mat_bounds, axis, matrix


