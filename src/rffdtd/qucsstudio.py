
# see QucsStudio/octave/share/octave/3.6.4/m/io/loadQucsDataset.m

import struct
import numpy as np

def read_dat(filename):
    def string():
            nonlocal ix
            n = buf[ix:].index(0)
            val = buf[ix:ix + n].decode()
            ix += n + 1
            return val

    def value(fmt):
            nonlocal ix
            n = struct.calcsize(fmt)
            val = struct.unpack(fmt, buf[ix:ix + n])[0]
            ix += n
            return val

    with open(filename, 'rb') as f:
        if f.read(8) != b'QucsData': return
        version = struct.unpack('i', f.read(4))[0]
        size = struct.unpack('i', f.read(4))[0]
        buf = f.read(size)
        data = {}
        ix = 0
        while ix < size:
            dstype = value('I')
            count = value('I')
            name = string()
            dependency = string() if dstype & (1 << 1) else ''
            fmt = '{}d'.format(count * (1 if dstype & (1 << 2) else 2))
            d = np.array(struct.unpack(fmt, f.read(struct.calcsize(fmt))))
            d = d if dstype & (1 << 2) else d[::2] + 1j * d[1::2]
            if dependency:
                shape = tuple(int(k) for k in dependency.split()[1:])
                d = d.reshape((len(d) // np.prod(shape),) + shape) if shape else d
                name = f'{name}:{dependency.split()[0]}'
            data[name] = d
        return data

