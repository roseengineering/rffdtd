
import os
import pathlib
import numpy as np
from .conf import DEFAULT_ZLINE


def buffer_touchstone(freq, sparam, zline=DEFAULT_ZLINE):
    nfreq = sparam.shape[0]
    nport = sparam.shape[1]
    with np.errstate(divide='ignore'):
        db = 20 * np.log10(np.abs(sparam))
    ph = np.angle(sparam, deg=True)
    lines = []
    lines.append('# HZ S DB R {:.0f}'.format(zline))
    for i in range(nfreq):
        buf = '{:<11.4e}'.format(freq[i])
        for m in range(nport):
            if m and nport > 2: buf += '\n{:11s}'.format('')
            for n in range(nport):
                ix = (i,n,m) if nport == 2 else (i,m,n)
                buf += '  {:8.3f} {:8.2f}'.format(db[ix], ph[ix])
        lines.append(buf)
    lines.append('')
    return '\n'.join(lines)


def write_touchstone(freq, sparam, zline=DEFAULT_ZLINE, filename=None):
    buf = buffer_touchstone(freq, sparam, zline=zline)
    nport = sparam.shape[1]
    if filename is None:
        print(buf, end='')
    else:
        p = pathlib.Path(filename)
        if not p.is_char_device():
            basename = os.path.splitext(filename)[0]
            filename = f'{basename}.s{nport}p'
        with open(filename, "w") as fi:
            fi.write(buf)


def rect(db, deg):
    ma = 10**(db / 20)
    return ma * np.exp(1j * np.deg2rad(deg))


def read_touchstone(filename):
    freq = []
    data = []
    with open(filename) as f:
        buf = ''
        while True:
            ln = next(f, None)
            if ln is not None:
                ln = ln.rstrip()
                if not ln or ln[0] == '!':
                    continue
                if ln[0] == '#':
                    d = ln[1:].lower().split()
                    assert(d[0] == 'hz' and d[1] == 's' and
                           d[2] == 'db' and d[3] == 'r' and
                           d[4] == '50')
                    continue
                if ln[0] == ' ':
                    buf += ln
                    continue
            if buf:
                d = [ float(d) for d in buf.split() ]
                freq.append(d[0])
                d = [ rect(d[i], d[i+1]) for i in range(1, len(d), 2) ]
                n = int(np.sqrt(len(d)))
                d = np.array(d).reshape(n, n)
                data.append(d.T if d.size == 4 else d)
            if ln is None: break
            buf = ln
    freq = np.array(freq)
    data = np.array(data)
    return freq, data

