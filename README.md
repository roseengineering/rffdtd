

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
FDTD simulation time: 0 min 0.27 sec
# HZ S MA R 50
5.0048e+09   3.13273e-01    48.73  3.58495e-01   147.36  0.00000e+00     0.00  0.00000e+00     0.00
1.0010e+10   4.61764e-01  -114.52  3.15175e-01   -37.08  0.00000e+00     0.00  0.00000e+00     0.00
1.5014e+10   6.23159e-01    84.69  2.70816e-01   130.90  0.00000e+00     0.00  0.00000e+00     0.00
2.0019e+10   4.81855e-01   -98.80  2.21730e-01   -64.99  0.00000e+00     0.00  0.00000e+00     0.00
2.5024e+10   5.50076e-01    83.96  1.68761e-01    95.13  0.00000e+00     0.00  0.00000e+00     0.00
3.0029e+10   1.93857e-01  -131.78  1.20521e-01  -111.97  0.00000e+00     0.00  0.00000e+00     0.00
3.5033e+10   3.05653e-01    40.15  8.77883e-02    29.13  0.00000e+00     0.00  0.00000e+00     0.00
4.0038e+10   3.10738e-01   118.62  8.11083e-02   164.59  0.00000e+00     0.00  0.00000e+00     0.00
4.5043e+10   2.81172e-01   -44.39  8.67760e-02   -48.64  0.00000e+00     0.00  0.00000e+00     0.00
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
FDTD simulation time: 0 min 1.04 sec
# HZ S MA R 50
1.9971e+09   7.32801e-01    10.49  5.50376e-03   -75.79  3.21009e-01     5.80  3.44816e-04   -97.87  1.30885e-04   -90.26
             5.50375e-03   -75.79  7.32801e-01    10.49  1.30885e-04    89.74  3.44816e-04    82.13  3.21009e-01  -174.20
             3.20273e-01     4.96  1.26525e-04    89.89  2.47599e-01     9.51  3.52097e-02   154.34  1.31618e-04    67.75
             3.30822e-04   -97.87  3.30823e-04    82.13  3.52740e-02   154.29  3.41037e-01    33.88  3.52740e-02   154.29
             1.26525e-04   -90.11  3.20273e-01  -175.04  1.31618e-04    67.75  3.52097e-02   154.34  2.47599e-01     9.51
3.9943e+09   8.78830e-01     0.64  3.15359e-03   118.48  2.64420e-01  -116.71  3.19885e-04    64.35  8.81095e-05    94.40
             3.15359e-03   118.48  8.78830e-01     0.64  8.81095e-05   -85.60  3.19885e-04  -115.65  2.64420e-01    63.29
             2.61438e-01  -116.35  8.55635e-05   -84.72  2.70196e-01    17.85  2.40803e-02    26.92  1.26014e-04  -109.69
             3.13209e-04    64.47  3.13209e-04  -115.53  2.41419e-02    26.88  4.95132e-01    29.11  2.41419e-02    26.88
             8.55635e-05    95.28  2.61438e-01    63.65  1.26014e-04  -109.69  2.40803e-02    26.92  2.70196e-01    17.85
5.9914e+09   8.87896e-01   -45.75  2.66439e-03   -48.30  2.41771e-01   107.24  5.43276e-04   -92.90  8.75446e-05   -75.88
             2.66439e-03   -48.30  8.87896e-01   -45.75  8.75446e-05   104.12  5.43276e-04    87.10  2.41771e-01   -72.76
             2.41233e-01   108.05  8.61698e-05   105.19  2.94503e-01    18.19  2.22767e-02  -110.47  9.21463e-05    49.97
             5.48273e-04   -92.00  5.48273e-04    88.00  2.23661e-02  -110.46  6.07525e-01    24.00  2.23661e-02  -110.46
             8.61698e-05   -74.81  2.41233e-01   -71.95  9.21463e-05    49.97  2.22767e-02  -110.47  2.94503e-01    18.19
7.9886e+09   1.58063e-01  -101.87  2.73447e-03   143.82  2.25749e-01   -38.41  8.06304e-04   132.13  1.04622e-04   116.68
             2.73447e-03   143.82  1.58063e-01  -101.87  1.04622e-04   -63.32  8.06303e-04   -47.87  2.25749e-01   141.59
             2.24307e-01   -37.54  1.02650e-04   -62.33  2.46973e-01    13.29  2.28204e-02   104.63  3.95251e-04  -137.28
             8.24498e-04   133.51  8.24498e-04   -46.49  2.30012e-02   104.76  6.61491e-01     8.65  2.30012e-02   104.76
             1.02650e-04   117.67  2.24307e-01   142.46  3.95251e-04  -137.28  2.28204e-02   104.63  2.46973e-01    13.29
9.9857e+09   5.37333e-01     9.69  3.30652e-03   -23.86  2.23792e-01   165.88  9.88769e-04    10.07  1.42142e-04   -49.41
             3.30652e-03   -23.86  5.37333e-01     9.69  1.42142e-04   130.59  9.88768e-04  -169.93  2.23792e-01   -14.12
             2.21924e-01   167.74  1.39088e-04   132.43  1.94117e-01    70.09  2.49413e-02   -46.92  1.11901e-03    91.77
             1.03690e-03    12.23  1.03690e-03  -167.77  2.52535e-02   -46.81  4.48472e-01     6.90  2.52535e-02   -46.81
             1.39088e-04   -47.57  2.21924e-01   -12.26  1.11901e-03    91.77  2.49413e-02   -46.92  1.94117e-01    70.09
1.1983e+10   4.10129e-01   -31.02  4.66227e-03   166.61  2.54716e-01     0.34  1.05807e-03   -91.19  2.15698e-04   143.90
             4.66227e-03   166.61  4.10129e-01   -31.02  2.15699e-04   -36.10  1.05807e-03    88.81  2.54716e-01  -179.66
             2.54454e-01     3.00  2.12301e-04   -33.63  5.62899e-01    61.32  2.95408e-02   152.76  2.38220e-03   -33.02
             1.15958e-03   -90.96  1.15958e-03    89.04  2.99088e-02   153.02  7.02422e-01    28.58  2.99088e-02   153.02
             2.12301e-04   146.37  2.54454e-01  -177.00  2.38220e-03   -33.02  2.95408e-02   152.76  5.62899e-01    61.32
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



