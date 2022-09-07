

# Rffdtd 

![s-parameter plot of a simulated interdigital filter](res/fisher_plot.png)
![the same filter but port tuned](res/fisher_tuned.png)

## Overview

This repo provides a FDTD (Finite Difference Time Domain) simulator
called rffdtd for solving RF circuits.  Rffdtd outputs its simulation 
results as s-parameters in the touchstone file format.  It can also run its simulations
on one or more GPUs.  Other open source FDTD projects either do not support, or
if they do, cannot generate s-parameters using a GPU.  

The simulator is written in Python and requires the libraries numpy and
pytorch in order to execute.

The geometry and material information
needed to run a FDTD simulation are provided through OFF geometry files.  The
contents of the OFF file constitute the physical structure of the model
while the name of the OFF file identifies
the material the geometry represents.  These OFF files can be zipped
up into a ZIP file for your convenience.

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
FDTD simulation time: 0 min 2.87 sec
# MHZ S DB R 50
5004.778404097836       -10.0815      48.728       -8.91034      147.36           -inf           0           -inf           0
10009.55680819567       -6.71159     -114.52        -10.029     -37.085           -inf           0           -inf           0
15014.33521229351       -4.10802      84.686       -11.3465       130.9           -inf           0           -inf           0
20019.11361639134       -6.34167     -98.798       -13.0835     -64.988           -inf           0           -inf           0
25023.89202048918       -5.19155      83.956       -15.4546      95.127           -inf           0           -inf           0
30028.67042458701       -14.2504     -131.78       -18.3788     -111.97           -inf           0           -inf           0
35033.44882868484       -10.2954      40.154       -21.1313      29.134           -inf           0           -inf           0
40038.22723278269       -10.1521      118.62       -21.8187      164.59           -inf           0           -inf           0
45043.00563688052       -11.0206     -44.389        -21.232      -48.64           -inf           0           -inf           0
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
FDTD simulation time: 0 min 3.68 sec
# MHZ S DB R 50
1997.137573007534       -2.70027      10.486       -9.86965      5.8005       -69.2482     -97.873       -77.6622     -90.262       -45.1868     -75.791
                         -9.8896      4.9562        -12.125      9.5121       -29.0668      154.34       -77.6137       67.75       -77.9565      89.891
                        -69.6081     -97.871       -29.0509      154.29       -9.34397      33.878       -29.0509      154.29       -69.6081      82.129
                        -77.9565     -90.109       -77.6137       67.75       -29.0668      154.34        -12.125      9.5122        -9.8896     -175.04
                        -45.1868     -75.791       -77.6622      89.738       -69.2483      82.127       -9.86965      -174.2       -2.70027      10.486
3994.275146015067        -1.1219     0.63527       -11.5541     -116.71       -69.9001      64.354       -81.0995        94.4       -50.0239      118.48
                        -11.6526     -116.35       -11.3664      17.851       -32.3668      26.923       -77.9916     -109.69       -81.3542      -84.72
                        -70.0833      64.467       -32.3446      26.882       -6.10558      29.111       -32.3446      26.882       -70.0833     -115.53
                        -81.3542       95.28       -77.9916     -109.69       -32.3668      26.923       -11.3664      17.851       -11.6526      63.652
                        -50.0239      118.48       -81.0995       -85.6       -69.9001     -115.65       -11.5541       63.29        -1.1219     0.63527
5991.4127190226         -1.03276     -45.751       -12.3319      107.24       -65.2996     -92.896       -81.1554     -75.885        -51.488     -48.302
                        -12.3513      108.05       -10.6182      18.193        -33.043     -110.47       -80.7104      49.967       -81.2929      105.19
                        -65.2201     -91.996       -33.0082     -110.46       -4.32872      23.997       -33.0082     -110.46       -65.2201      88.004
                        -81.2929     -74.811       -80.7104      49.967        -33.043     -110.47       -10.6182      18.193       -12.3513     -71.952
                         -51.488     -48.302       -81.1554      104.12       -65.2996      87.104       -12.3319     -72.762       -1.03276     -45.751
7988.550292030134       -16.0234     -101.87       -12.9275     -38.413         -61.87      132.13       -79.6076      116.68       -51.2626      143.82
                        -12.9831     -37.538        -12.147      13.288       -32.8335      104.63       -68.0625     -137.28       -79.7728     -62.331
                        -61.6762      133.51        -32.765      104.76       -3.58952       8.647        -32.765      104.76       -61.6762     -46.488
                        -79.7728      117.67       -68.0625     -137.28       -32.8335      104.63        -12.147      13.288       -12.9831      142.46
                        -51.2626      143.82       -79.6076     -63.323         -61.87     -47.868       -12.9275      141.59       -16.0234     -101.87
9985.687865037668       -5.39513      9.6913       -13.0031      165.88       -60.0981      10.069       -76.9456     -49.413       -49.6126     -23.856
                        -13.0759      167.74       -14.2387      70.088       -32.0616     -46.917       -59.0233      91.774       -77.1342      132.43
                        -59.6853      12.228       -31.9536     -46.806        -6.9653      6.8974       -31.9536     -46.806       -59.6853     -167.77
                        -77.1342     -47.572       -59.0233      91.774       -32.0616     -46.917       -14.2387      70.088       -13.0759     -12.262
                        -49.6126     -23.856       -76.9456      130.59       -60.0981     -169.93       -13.0031     -14.122       -5.39513      9.6913
11982.8254380452        -7.74158     -31.017       -11.8789     0.33866       -59.5097     -91.185       -73.3231       143.9        -46.628      166.61
                        -11.8878       3.001        -4.9914       61.32       -30.5916      152.76       -52.4605     -33.016        -73.461     -33.627
                         -58.714     -90.955        -30.484      153.02       -3.06803      28.584        -30.484      153.02        -58.714      89.045
                         -73.461      146.37       -52.4605     -33.016       -30.5916      152.76        -4.9914       61.32       -11.8878        -177
                         -46.628      166.61       -73.3231     -36.099       -59.5097      88.815       -11.8789     -179.66       -7.74158     -31.017
```


Also see the examples.ipynb Jupyter notebook in the repo for plots and more.

## Usage


```
$ rffdtd --help
usage: rffdtd [-h] [--output OUTPUT] [--export EXPORT] [--start START] [--stop STOP]
                   [--pitch PITCH] [--df DF] [--steps STEPS] [--ntau NTAU] [--ndelay NDELAY]
                   [--zo ZO] [--ngpu NGPU] [--dtype DTYPE] [--device DEVICE] [--symmetric]
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
  --zo ZO          line impedance of ports in ohms (default: 50)
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
made out of the same materal, you can prefix the material name with a group 
name and then a dash.

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
      123  1980-01-01 00:00   port2.off
     5072  1980-01-01 00:00   rods2-aluminum.off
      105  1980-01-01 00:00   port3.off
     5026  1980-01-01 00:00   rods3-aluminum.off
      118  1980-01-01 00:00   port4.off
      479  1980-01-01 00:00   tap1-copper.off
      479  1980-01-01 00:00   port1.off
      465  1980-01-01 00:00   tap2-copper.off
      465  1980-01-01 00:00   port5.off
---------                     -------
    19786                     12 files
```


To support other materials, for example PCB substrates with a certain permittivity, use
the following naming format for the material: er99.99e9.
For conductors, the naming convention, assuming a permittivity
of 1, is: sigma99.99e9.

To define both permittivity and conductivity the naming format is 
er99.99e9_99.99e9, the underscore separating the two.

## Lumped Ports

To create a port, use a material name of port99 starting
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
For example an interdigital filter inside a hollowed cube enclosure must
be broken into a box with a lid.  In addition this lid
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

To build rffdtd, run the following then copy the resulting executable rffdtd to whichever directory you want.

```
$ pip install numpy torch
OR
$ conda install -y -c pytorch pytorch
$ conda install -y numpy

$ sh build.sh
python res/zip.py -s 1 -o rffdtd src/* src/*/*
echo '#!/usr/bin/env python3' | cat - rffdtd.zip > rffdtd
rm rffdtd.zip
chmod 755 rffdtd
```

Or you can pip install it by entering the root directory of this repo and running:

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
    filename,       # file descriptor or name or as list of OFF or ZIP geometry files
    df=None,        # frequency step in Hz to resolve, sets simulation steps
    ds=.001,        # length of a side of a uniform cell in m
    ntau=20,        # pulse width of excitation in units of simulation steps
    ndelay=6.5,     # time delay of excitation in units of pulse widths
    zo=50,          # line impedance of ports in ohms
    dtype='float',  # "float" or "double" data type'
    device=None     # "cuda" or "cpu" compute device, otherwise will autodetect
    steps=None,     # explicitly set number of simulation steps
    start=None,     # first port to excite, starting from 1
    stop=None,      # last port to excite, starting from 1
    ngpu=None,      # number of GPUs to use, or all by default
    symmetric=False # make s-parameter matrices symmetric
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
    filename=None  # name of file to write touchstone output to, instead of console
    zo=50,         # line impedance of ports in ohms
    )

rffdtd.read_touchstone(
    filename       # name of file to load touchstone input from
    )
```

## util/snpsum.py

The script snpsum.py in the util directory sums up the sparameters matrices 
for each frequency across all the touchstone files passed on the 
command line.  It then outputs the result to the console.

snpsum.py should be useful when running
a batch of simulations (each exciting a different set of
ports) on multiple machines against the same model.
All the touchstone file results can then be pulled together onto one machine
and summed up into one aggregated touchstone file using this utility.


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



