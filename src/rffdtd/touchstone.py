
import os
import pathlib
import numpy as np


def dbvolt(s):
    with np.errstate(divide='ignore', invalid='ignore'):
        return 20 * np.log10(abs(s))


def rect(x, y, dtype):
    if dtype == 'db' or dtype =='ma':
        x = 10**(x / 20) if dtype == 'db' else x
        value = x * np.exp(1j * np.deg2rad(y))
    elif dtype == 'ri':
        value = x + 1j * y
    else:
        raise ValueError("Bad touchstone file type")
    return value


def prefix(unit):
    if unit == 'hz':
        return 1
    elif unit == 'khz':
        return 1e3
    elif unit == 'mhz':
        return 1e6
    elif unit == 'ghz':
        return 1e9
    else:
        raise ValueError


def get_fid(fileio):
    if isinstance(fileio, str):
        return open(fileio)
    else:
        return fileio


def read_touchstone(filename):
    freq = []
    data = []
    dtype = None
    with get_fid(filename) as f:
        buf = ''
        while True:
            ln = next(f, None)
            if ln is not None:
                ln = ln.rstrip()
                if not ln or ln[0] == '!':
                    continue
                # handle header line
                if ln[0] == '#':
                    d = ln[1:].lower().split()
                    if d[1] != 's' or d[3] != 'r':
                        raise ValueError
                    zo = float(d[4])
                    scale = prefix(d[0])
                    dtype = d[2]
                    continue
                # handle line continuation
                if ln[0] == ' ':
                    buf += ln
                    continue
            if buf:
                d = [ float(d) for d in buf.split() ]
                freq.append(d[0] * scale)
                d = [ rect(d[i], d[i+1], dtype=dtype) for i in range(1, len(d), 2) ]
                n = int(np.sqrt(len(d)))
                d = np.array(d).reshape(n, n)
                data.append(d.T if d.size == 4 else d)
            if ln is None: break
            buf = ln
    freq = np.array(freq)
    data = np.array(data)
    return freq, data


def write_touchstone(freq, sparam, filename=None, zo=None):
    zo = zo or 50
    nfreq = sparam.shape[0]
    nport = sparam.shape[1]
    db = dbvolt(sparam)
    ph = np.angle(sparam, deg=True)
    lines = []
    lines.append(f'# MHZ S DB R {zo:.0f}')
    # S11 S21 S12 S22
    for i in range(nfreq):
        buf = '{:<17.16g}'.format(freq[i] / 1e6)
        for m in range(nport):
            if m and nport > 2: buf += '\n{:17s}'.format('')
            for n in range(nport):
                ix = (i,n,m) if nport == 2 else (i,m,n)
                buf += '  {:13.6g} {:11.5g}'.format(db[ix], ph[ix])
        lines.append(buf)
    lines.append('')
    buf = '\n'.join(lines)

    # write out
    if filename is None:
        print(buf, end='')
    else:
        p = pathlib.Path(filename)
        if not p.is_char_device():
            basename = os.path.splitext(filename)[0]
            filename = f'{basename}.s{nport}p'
        with open(filename, "w") as fi:
            fi.write(buf)



