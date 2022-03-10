

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
Each individual simulation needs about 15.946 MiB of memory.
Running 1 simulation(s) on device cuda.
Using GPU: NVIDIA GeForce RTX 3070 Ti
 393 / 393 / 1   
FDTD simulation time: 0 min 0.33 sec
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
1296 MHz Interdigital 3-Pole Butterworth Filter, 110 MHz Bandwidth.
Interdigital Bandpass Filters for Amateur V.H.F/U.H.F. Applications,
High-Q Filter Construction Made Easy, Reed Fisher, March 1968 QST;
reproduced in the ARRL Handbook 2017, p11.32, figure 11.63.
Grid is 90 x 28 x 68 mm in size and composed of 171360 cells.
Each individual simulation needs about 7.849 MiB of memory.
Running 2 simulation(s) on device cuda.
Using GPU: NVIDIA GeForce RTX 3070 Ti
 260 / 260 / 2   
FDTD simulation time: 0 min 0.40 sec
# HZ S DB R 50
1.9971e+09     -1.875    22.16   -55.293   -56.97   -55.293   -56.97    -1.875    22.16
3.9943e+09     -0.182    -2.33   -59.472   154.44   -59.472   154.44    -0.182    -2.33
5.9914e+09     -1.047   -51.54   -60.071     2.45   -60.071     2.45    -1.047   -51.54
7.9886e+09    -16.478  -149.57   -58.951  -152.98   -58.951  -152.98   -16.478  -149.57
9.9857e+09     -3.156    25.46   -56.457    50.32   -56.457    50.32    -3.156    25.46
1.1983e+10     -2.501   -31.23   -52.593  -109.99   -52.593  -109.99    -2.501   -31.23
```


Also see the examples.ipynb Jupyter notebook in the repo for plots and more.

## Usage


```
$ rffdtd --help
usage: rffdtd [-h] [--output OUTPUT] [--export EXPORT] [--start START] [--stop STOP]
              [--pitch PITCH] [--df DF] [--steps STEPS] [--ntau NTAU] [--ndelay NDELAY]
              [--zline ZLINE] [--ngpu NGPU] [--dtype DTYPE] [--device DEVICE]
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
1296 MHz Interdigital 3-Pole Butterworth Filter, 110 MHz Bandwidth.
Interdigital Bandpass Filters for Amateur V.H.F/U.H.F. Applications,
High-Q Filter Construction Made Easy, Reed Fisher, March 1968 QST;
reproduced in the ARRL Handbook 2017, p11.32, figure 11.63.
  Length      Date    Time    Name
---------  ---------- -----   ----
      492  1980-01-01 00:00   cover-sigma62.11e6.off
     1836  1980-01-01 00:00   box-silver.off
     2524  1980-01-01 00:00   rods0-brass.off
     2456  1980-01-01 00:00   rods1-brass.off
     2474  1980-01-01 00:00   rods2-brass.off
      479  1980-01-01 00:00   tap1-copper.off
      479  1980-01-01 00:00   port1.off
      465  1980-01-01 00:00   tap2-copper.off
      465  1980-01-01 00:00   port2.off
---------                     -------
    11670                     9 files
```


To support other materials, for example PCB substrates with a certain permittivity, use
the following naming format for the material: er99.99e9 or er_99.99e9.
The underscore can be replaced with a space if needed.
For conductors, the naming convention, assuming a permittivity
of 1, is: sigma99.99e9 or sigma_99.99e9.
To define both permittivity and conductivity the naming format is 
er99.99e9_99.99e9 or er_99.99e9_99.99e9.

To create a port, use a material name of port99 or port_99, starting
from port number 1.  The port will be a "lumped" port.  The opposite faces of the 
port should overlap a conductor.  A port can only be represented by a cube or 
a plane, but not a cylinder for example.

The PEC cage mentioned above will abutt the bounding box of your model with a padding 
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



