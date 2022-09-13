
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


def read_touchstone(text):
    freq = []
    data = []
    dtype = None
    buf = ''
    f = iter(text.splitlines())
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


def write_touchstone(f, s, dtype=None, zo=None, precision=None):
    zo = zo or 50
    precision = precision or 6
    pad = precision + 6
    dtype = dtype or 'ri'
    dtype = dtype.lower()
    nfreq = s.shape[0]
    nport = s.shape[1]
    ma = abs(s)
    db = dbvolt(s)
    ph = np.angle(s, deg=True)
    lines = []
    lines.append(f'# MHZ S {dtype.upper()} R {zo:.0f}')
    # S11 S21 S12 S22
    for i in range(nfreq):
        buf = '{:<17.16g}'.format(f[i] / 1e6)
        for m in range(nport):
            if m and nport > 2: buf += '\n{:17s}'.format('')
            for n in range(nport):
                ix = (i,n,m) if nport == 2 else (i,m,n)
                fm = '  {{:{c}.{d}g}} {{:{c}.{d}g}}'.format(c=pad, d=precision)
                if dtype == 'db':
                    buf += fm.format(db[ix], ph[ix])
                elif dtype == 'ma':
                    buf += fm.format(ma[ix], ph[ix])
                elif dtype == 'ri':
                    buf += fm.format(s[ix].real, s[ix].imag)
                else:
                    raise ValueError
        lines.append(buf)
    lines.append('')
    return '\n'.join(lines)


#######

def save_touchstone(f, s, dtype=None, zo=None, filename=None, precision=None):
    text = write_touchstone(f, s, zo=zo, dtype=dtype, precision=precision)
    if filename is None:
        print(text, end='')
    else:
        basename, ext = os.path.splitext(filename)
        if (ext == '.npz'):
            np.savez(filename, f=f, s=s)
        else:
            p = pathlib.Path(filename)
            if not p.is_char_device():
                nport = s.shape[1]
                filename = f'{basename}.s{nport}p'
            with open(filename, "w") as fi:
                fi.write(text)


def get_fid(fileio):
    if isinstance(fileio, str):
        return open(fileio)
    else:
        return fileio


def load_touchstone(filename):
    with get_fid(filename) as f:
        text = f.read()
    return read_touchstone(text)


