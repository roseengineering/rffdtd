
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from . import simulate, parseoff, writeobj, write_touchstone
from .conf import (DEFAULT_DS, DEFAULT_NTAU, DEFAULT_NDELAY, 
                  DEFAULT_ZLINE, DEFAULT_DTYPE)


def parse_args():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('filename', nargs='+',
                        help='OFF geometry file comprising the FDTD simulation, ZIP files accepted')
    parser.add_argument('--output',
                        help='write touchstone output to a file, instead of console')
    parser.add_argument('--export',
                        help='save voxelization as an OBJ file, no simulation')
    parser.add_argument('--start', type=int,
                        help='first port to excite, starting from 1')
    parser.add_argument('--stop', type=int,
                        help='last port to excite, starting from 1')
    parser.add_argument('--pitch', type=float, default=DEFAULT_DS*1e3,
                        help='length of a side of a uniform cell in mm')
    parser.add_argument('--df', type=float,
                        help='frequency step in Hz to resolve, sets simulation steps')
    parser.add_argument('--steps', type=int,
                        help='explicitly set number of simulation steps')
    parser.add_argument('--ntau', type=float, default=DEFAULT_NTAU, 
                        help='pulse width of excitation in units of simulation steps')
    parser.add_argument('--ndelay', type=float, default=DEFAULT_NDELAY, 
                        help='time delay of excitation in units of pulse widths')
    parser.add_argument('--zline', type=float, default=DEFAULT_ZLINE, 
                        help='line impedance of ports in ohms')
    parser.add_argument('--ngpu', type=int,
                        help='number of GPUs to use, or all by default')
    parser.add_argument('--dtype', default=DEFAULT_DTYPE, 
                        help='"float" or "double" data type')
    parser.add_argument('--device', 
                        help='"cuda" or "cpu" compute device, otherwise will autodetect')
    parser.add_argument('--symmetric', action='store_true', 
                        help='make s-parameter matrices symmetric')
    return parser.parse_args()


def main():
    args = parse_args()
    ds = args.pitch * 1e-3
    if args.export:
        er, sigma = parseoff.parser_export(args.filename, ds=ds)
        writeobj.save(args.export, er=er, sigma=sigma, ds=ds)
    else: 
        freq, sparam = simulate(
            args.filename,
            ds=ds, df=args.df, steps=args.steps, zline=args.zline, 
            start=args.start, stop=args.stop,
            ntau=args.ntau, ndelay=args.ndelay,
            ngpu=args.ngpu, symmetric=args.symmetric,
            dtype=args.dtype, device=args.device)
        write_touchstone(freq, sparam, filename=args.output, zline=args.zline)

