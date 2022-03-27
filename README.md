

# Rffdtd 

![s-parameter plot of a simulated interdigital filter](res/fisher_plot.png)
![the same filter but port tuned](res/fisher_tuned.png)

## Overview

This repo provides a FDTD (Finite Differences Time Domain) simulator
called rffdtd for solving RF circuits.  Rffdtd outputs its simulation 
results as s-parameters in the touchstone file format.  It is not limited in the number of
s-parameter ports it can excite, so it can be used for example
to "port tune" a multielement filter.  It can also run its simulations
on a GPU, which other open source projects either do not support or
if they do cannot generate s-parameters using a GPU.  

The simulator is written in Python and requires the libraries numpy and
pytorch in order to execute.  To install them use:

```
$ pip install numpy torch
OR
$ conda install -y -c pytorch pytorch
$ conda install -y numpy
```

The geometry and material information
needed to run a FDTD simulation are provided through OFF geometry files.  The
contents of the OFF file constitute the physical structure of the model
while the name of the OFF file identifies
the material the geometry represents.  These OFF files can be zipped
up into one or more ZIP files for your convenience.

Rffdtd places your model inside a PEC cage, thereby surrounding the model within a PEC boundary.  The software does not
support any type of absorbing boundaries, such as PMLs.  The
simulator was constructed as a tool to help design devices
such as filters or other circuits that will be placed inside an
enclosure, not for antennas necessarily or solving "scattering" problems like
radar or MRI.

## Examples

To simulate the microstrip lowpass filter example included [1], run the following below.
The simulator will use the OFF files in the ZIP file to construct the lowpass filter.
The --df option sets the frequency step you want the s-parameter results to provide.  The
--pitch option sets the length of a side of a FDTD grid cell in millimeters to use.
The --stop option tells rffdtd which port it should excite last.


```
$ rffdtd --df 5e9 --stop 1 --pitch .264 examples/lowpass.zip
Microstrip Lowpass Filter.
The Finite-Differnce Time-Domain Method for Electromagnetics with 
MATLAB Simulations, Elsherbeni and Demir.  Section 6.2.
Reproduced from Application of the Three-Dimensional Finite-Difference
Time-Domain Method to the Analysis of Planar Microstrip Circuits,
David Sheen, Sami Ali, IEEE MTT Vol 38, No 7, July 1990, p.849.
Grid is 27.456 x 24.552 x 9.504 mm in size and composed of 348192 cells.
Each individual simulation needs about 17.939 MiB of memory.
Running 1 simulation(s) on device cuda.
Using GPU: NVIDIA GeForce RTX 3070 Ti
 393 / 393 / 1   
FDTD simulation time: 0 min 0.29 sec
# HZ S DB R 50
5.0048e+09    -10.082    48.73    -8.910   147.36      -inf     0.00      -inf     0.00
1.0010e+10     -6.712  -114.52   -10.029   -37.08      -inf     0.00      -inf     0.00
1.5014e+10     -4.108    84.69   -11.347   130.90      -inf     0.00      -inf     0.00
2.0019e+10     -6.342   -98.80   -13.084   -64.99      -inf     0.00      -inf     0.00
2.5024e+10     -5.192    83.96   -15.455    95.13      -inf     0.00      -inf     0.00
3.0029e+10    -14.250  -131.78   -18.379  -111.97      -inf     0.00      -inf     0.00
3.5033e+10    -10.295    40.15   -21.131    29.13      -inf     0.00      -inf     0.00
4.0038e+10    -10.152   118.62   -21.819   164.59      -inf     0.00      -inf     0.00
4.5043e+10    -11.021   -44.39   -21.232   -48.64      -inf     0.00      -inf     0.00
```


To simulate a 1296 MHz interdigital filter [2], run:


```
$ rffdtd --df 5e9 --pitch 1 examples/fisher.zip
1296 MHz Interdigital 3-Pole Butterworth Filter, 110 MHz BW
Grid is 94 x 28 x 68 mm in size and composed of 178976 cells.
Each individual simulation needs about 10.764 MiB of memory.
Running 5 simulation(s) on device cuda.
Using GPU: NVIDIA GeForce RTX 3070 Ti
 260 / 260 / 5   
FDTD simulation time: 0 min 1.02 sec
# HZ S DB R 50
1.9971e+09     -2.700    10.49   -45.187   -75.79    -9.870     5.80   -69.248   -97.87   -77.662   -90.26
              -45.187   -75.79    -2.700    10.49   -77.662    89.74   -69.248    82.13    -9.870  -174.20
               -9.890     4.96   -77.956    89.89   -12.125     9.51   -29.067   154.34   -77.614    67.75
              -69.608   -97.87   -69.608    82.13   -29.051   154.29    -9.344    33.88   -29.051   154.29
              -77.956   -90.11    -9.890  -175.04   -77.614    67.75   -29.067   154.34   -12.125     9.51
3.9943e+09     -1.122     0.64   -50.024   118.48   -11.554  -116.71   -69.900    64.35   -81.100    94.40
              -50.024   118.48    -1.122     0.64   -81.100   -85.60   -69.900  -115.65   -11.554    63.29
              -11.653  -116.35   -81.354   -84.72   -11.366    17.85   -32.367    26.92   -77.992  -109.69
              -70.083    64.47   -70.083  -115.53   -32.345    26.88    -6.106    29.11   -32.345    26.88
              -81.354    95.28   -11.653    63.65   -77.992  -109.69   -32.367    26.92   -11.366    17.85
5.9914e+09     -1.033   -45.75   -51.488   -48.30   -12.332   107.24   -65.300   -92.90   -81.155   -75.88
              -51.488   -48.30    -1.033   -45.75   -81.155   104.12   -65.300    87.10   -12.332   -72.76
              -12.351   108.05   -81.293   105.19   -10.618    18.19   -33.043  -110.47   -80.710    49.97
              -65.220   -92.00   -65.220    88.00   -33.008  -110.46    -4.329    24.00   -33.008  -110.46
              -81.293   -74.81   -12.351   -71.95   -80.710    49.97   -33.043  -110.47   -10.618    18.19
7.9886e+09    -16.023  -101.87   -51.263   143.82   -12.927   -38.41   -61.870   132.13   -79.608   116.68
              -51.263   143.82   -16.023  -101.87   -79.608   -63.32   -61.870   -47.87   -12.927   141.59
              -12.983   -37.54   -79.773   -62.33   -12.147    13.29   -32.834   104.63   -68.063  -137.28
              -61.676   133.51   -61.676   -46.49   -32.765   104.76    -3.590     8.65   -32.765   104.76
              -79.773   117.67   -12.983   142.46   -68.063  -137.28   -32.834   104.63   -12.147    13.29
9.9857e+09     -5.395     9.69   -49.613   -23.86   -13.003   165.88   -60.098    10.07   -76.946   -49.41
              -49.613   -23.86    -5.395     9.69   -76.946   130.59   -60.098  -169.93   -13.003   -14.12
              -13.076   167.74   -77.134   132.43   -14.239    70.09   -32.062   -46.92   -59.023    91.77
              -59.685    12.23   -59.685  -167.77   -31.954   -46.81    -6.965     6.90   -31.954   -46.81
              -77.134   -47.57   -13.076   -12.26   -59.023    91.77   -32.062   -46.92   -14.239    70.09
1.1983e+10     -7.742   -31.02   -46.628   166.61   -11.879     0.34   -59.510   -91.19   -73.323   143.90
              -46.628   166.61    -7.742   -31.02   -73.323   -36.10   -59.510    88.81   -11.879  -179.66
              -11.888     3.00   -73.461   -33.63    -4.991    61.32   -30.592   152.76   -52.460   -33.02
              -58.714   -90.96   -58.714    89.04   -30.484   153.02    -3.068    28.58   -30.484   153.02
              -73.461   146.37   -11.888  -177.00   -52.460   -33.02   -30.592   152.76    -4.991    61.32
```


Also see the examples.ipynb Jupyter notebook in the repo for plots and more.

## Usage


```
$ rffdtd --help
usage: rffdtd [-h] [--output OUTPUT] [--export EXPORT] [--start START] [--stop STOP]
              [--pitch PITCH] [--df DF] [--steps STEPS] [--ntau NTAU] [--ndelay NDELAY]
              [--zline ZLINE] [--ngpu NGPU] [--dtype DTYPE] [--device DEVICE] [--symmetric]
              filename [filename ...]

positional arguments:
  filename         OFF geometry file comprising the FDTD simulation, ZIP files accepted

optional arguments:
  -h, --help       show this help message and exit
  --output OUTPUT  write touchstone output to a file, instead of console (default: None)
  --export EXPORT  save voxelization as an OBJ file, no simulation (default: None)
  --start START    first port to excite, starting from 1 (default: None)
  --stop STOP      last port to excite, starting from 1 (default: None)
  --pitch PITCH    length of a side of a uniform cell in mm (default: 1.0)
  --df DF          frequency step in Hz to resolve, sets simulation steps (default: None)
  --steps STEPS    explicitly set number of simulation steps (default: None)
  --ntau NTAU      pulse width of excitation in units of simulation steps (default: 20)
  --ndelay NDELAY  time delay of excitation in units of pulse widths (default: 6.5)
  --zline ZLINE    line impedance of ports in ohms (default: 50)
  --ngpu NGPU      number of GPUs to use, or all by default (default: None)
  --dtype DTYPE    "float" or "double" data type (default: float)
  --device DEVICE  "cuda" or "cpu" compute device, otherwise will autodetect (default: None)
  --symmetric      make s-parameter matrices symmetric (default: False)
```


## Materials

To identify your OFF geometry as being made out of a particular material,
give the OFF file the same name as the material.  For example, if the
material is made out of silver, name it silver.off.  Rffdtd supports the following
material names: pec, silver, copper, gold, aluminum, brass, steel,
and air.  Any material it does not know, rffdtd will consider it a
PEC (Perfect Electrical Conductor).  If you have several OFF geometries
made out of the same materal, you can prefix the material name with a group name and then a dash.

For example the interdigital filter uses the following OFF files and file names:


```
$ unzip -l examples/fisher.zip
Archive:  examples/fisher.zip
1296 MHz Interdigital 3-Pole Butterworth Filter, 110 MHz BW
  Length      Date    Time    Name
---------  ---------- -----   ----
      492  1980-01-01 00:00   lid-aluminum.off
     1836  1980-01-01 00:00   box-aluminum.off
     5126  1980-01-01 00:00   rods1-aluminum.off
      123  1980-01-01 00:00   port3.off
     5072  1980-01-01 00:00   rods2-aluminum.off
      105  1980-01-01 00:00   port4.off
     5026  1980-01-01 00:00   rods3-aluminum.off
      118  1980-01-01 00:00   port5.off
      479  1980-01-01 00:00   tap1-copper.off
      479  1980-01-01 00:00   port1.off
      465  1980-01-01 00:00   tap2-copper.off
      465  1980-01-01 00:00   port2.off
---------                     -------
    19786                     12 files
```


To support other materials, for example PCB substrates with a certain permittivity, use
the following naming format for the material: er99.99e9 or er_99.99e9.
The underscore can be replaced with a space if needed.
For conductors, the naming convention, assuming a permittivity
of 1, is: sigma99.99e9 or sigma_99.99e9.
To define both permittivity and conductivity the naming format is 
er99.99e9_99.99e9 or er_99.99e9_99.99e9.

## Ports

To create a port, use a material name of port99 or port_99, starting
from port number 1.  The port will be a "lumped" port.  The opposite faces of the 
port should overlap a conductor.  A port can only be represented by a cube or 
a plane, but not a cylinder for example.

## Expanding The PEC Cage

The PEC cage, as mentioned above, will abutt the bounding box of your model with a padding 
of one cell.  To enlarge the bounding box use the air material.  The air material will be dropped and 
ignored when the model is voxelized.  However it will be considered when calculating
the model's bounding box.  See the lowpass and coupler examples.

## OFF Files

Provided in the example directory are scripts for generating
the OFF file simulation model examples.  The scripts use the python library
pycsg to generate these models.  To install pycsg run:

```
$ pip install pycsg
```

In addition there is a utility python library file, named csgsave.py, provided in the src
directory and zipped up in rffdtd.
The library contains code for saving the CSG solids pycsg creates as OFF files.
Of course, you can also use FreeCAD or OpenSCAD to generate your own OFF files
and simulation models as well.

## Voxelization

The simulator performs the voxelization using a "z-buffer" algorithm.
This algorithm has the advantage that it will fill mesh geometries.
Unfortunately it also has problems in that it might fill holes
that it should not.  This is especially so with hollowed cubes.
To rectify this, any geometry with holes needs to be broken up.
For example an interdigital filter inside a hollowed cube as an
enclosure needs to have a cover.  In addition this cover 
needs to be placed in a separate OFF file than the box.  See the
provided interdigital filter for an example of this.

To inspect how well the model is voxelized, use the --export option.
This will output the voxel result as an OBJ file and skip the simulation.

```
$ rffdtd --pitch 1 --export examples/fisher_voxel.obj examples/fisher.zip
```

The export process fuses all similar material into one mesh.  So to create a cover
that can be hid in your CAD software, use a different material, but not very different,
for the cover.  See again the interdigital filter example.

![interdigital filter voxelization](res/fisher_voxel.png)

Its original non-voxelized geometry is shown here.  This geometry
is from fisher.obj.  To generate this file as well as fisher.zip,
run python on fisher.py.

![interdigital filter original geometry](res/fisher.png)

Planes can also be voxelized.  This is used to create microstrip models.
Rffdtd recognizes a geometry as a plane if the plane uses an entire OFF file for
itself and it has one dimension that is constant.  Also, only one rectangular
plane per OFF file is supported at the moment.  See the lowpass filter and
microwave coupler in the example directory. 

![lowpass filter voxelized](res/lowpass_voxel.png)

## Installation

To build rffdtd, run the following then copy it to the directory you want.


```
$ sh build.sh
python res/zip.py -s 1 -o rffdtd src/* src/*/*
echo '#!/usr/bin/env python3' | cat - rffdtd.zip > rffdtd
rm rffdtd.zip
chmod 755 rffdtd
```


Or you can pip install it in this directory with:

```sh
$ pip install .
```

Besides installing the library named rffdtd it also installs the rffdtd 
command line script to your path.

## Python API

Import the library:

```python
import rffdtd
```

Run a simulation:

```python
freq, sparam = rffdtd.simulate(
    filename,      # file descriptor or name or as list of OFF or ZIP geometry files
    df=None,       # frequency step in Hz to resolve, sets simulation steps
    ds=.001,       # length of a side of a uniform cell in m
    ntau=20,       # pulse width of excitation in units of simulation steps
    ndelay=6.5,    # time delay of excitation in units of pulse widths
    zline=50,      # line impedance of ports in ohms
    dtype='float', # "float" or "double" data type'
    device=None    # "cuda" or "cpu" compute device, otherwise will autodetect
    steps=None,    # explicitly set number of simulation steps
    start=None,    # first port to excite, starting from 1
    stop=None,     # last port to excite, starting from 1
    ngpu=None      # number of GPUs to use, or all by default
    )
```

Where freq is a list of frequencies and sparam is a list of 
complex-number s-parameter matrices.  Each frequency in freq 
corresponds to its respective s-parameter matrix in sparam.
The numpy array sparam has the shape (nfreq, m, n).
The maximum frequency returned in freq is determined by the 
length of the excitation pulse width.  The frequency step used
is determined by the number of simulation steps.  The minimum number of
allowable steps is set to 2 * ntau * ndelay.

Load or save s-sparameters to a touchstone file:

```python
rffdtd.write_touchstone(
    freq,          # list of frequencies corresponding to each s-parameter matrix
    sparam,        # list of s-parameter matrices
    zline=50,      # line impedance of ports in ohms
    filename=None  # name of file to write touchstone output to, instead of console
    )

rffdtd.read_touchstone(
    filename       # name of file to load touchstone input from
    )
```


## Notes

Pytorch does not support the M1 GPU yet.  I could not 
use tensorflow, which does support the M1 GPU, because my code requires a mutable
tensor which tensorflow does not provide.

Also I have issues with pytorch over reserving space on the GPU.
Unfortunately I have not resolved the issue.  I cannot find any
memory leaks in the code.

## Footnotes

[1] The Finite-Differnce Time-Domain Method for Electromagnetics with 
MATLAB Simulations, Elsherbeni and Demir.  Section 6.2 contains two
of the examples provided here: a lowpass filter and a microwave coupler.
The examples are from Application of the Three-Dimensional Finite-Difference
Time-Domain Method to the Analysis of Planar Microstrip Circuits,
David Sheen, Sami Ali, IEEE MTT Vol 38, No 7, July 1990, p.849.

[2] Interdigital Bandpass Filters for Amateur V.H.F/U.H.F. Applications,
High-Q Filter Construction Made Easy, Reed Fisher, March 1968 QST;
reproduced in the ARRL Handbook 2017, p11.32, figure 11.63.



