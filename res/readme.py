#!/usr/bin/python3

import os, subprocess, re 

def run(command, language='', nopython=False):
    cmd = command if nopython else f"COLUMNS=95 PYTHONPATH=src python3 {command}" 
    command = command.replace('src/__main__.py', 'rffdtd')
    command = command.replace('util/snpsum.py', 'python3 snpsum.py')
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    buf = proc.stdout.read().decode()
    buf = re.sub(r'^.*( \d+ / \d+ / \d+.*)$', r'\g<1>', buf, flags=re.MULTILINE)
    buf = re.sub('\r', '', buf)
    buf = re.sub('__main__.py', 'rffdtd', buf)
    proc.wait()
    return f"""
```{language}
$ {command}
{buf}\
```
"""

print(f"""

# Rffdtd 

![s-parameter plot of a simulated interdigital filter](res/fisher_plot.png)
![the same filter but port tuned](res/fisher_tuned.png)

## Overview

This repo provides a FDTD (Finite Difference Time Domain) simulator
called rffdtd for solving RF circuits.  Rffdtd outputs its simulation 
results as s-parameters in the touchstone or .npz file format.  It can also run its simulations
on one or more GPUs.  Other open source FDTD projects either do not support GPUs
or, if they do, cannot generate s-parameters using a GPU.  

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

{run("src/__main__.py --df 5e9 --stop 1 --pitch .264 examples/lowpass.zip")}

To simulate a 1296 MHz interdigital filter [2], run:

{run("src/__main__.py --df 5e9 --pitch 1 examples/fisher.zip")}

Also see the examples.ipynb Jupyter notebook in the repo for plots and more.

## Usage

{run("src/__main__.py --help")}

The value passed to --df not only determines the frequency step in Hz but it also,
in combination with --pitch, determines the number of simulation steps.
If you want to force the number of simulation steps use --steps instead of --df.
The minimum number of allowable simulation steps is set at 2 * --ntau * --ndelay.
If both --step and --df are not set then the simulation will use the minimum number of steps.

The maximum frequency returned is determined by the time
width in seconds of the excitation pulse.  This width is determined
by --ntau which is in simulation step units.
The period in seconds of each simulation step is calculated from the uniform cell size (--pitch)
of the simulation.

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

{run("unzip -l examples/fisher.zip", nopython=True)}

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
To rectify this, any geometry with holes needs to be broken up
to be visible by the voxelizer.
For example with an interdigital filter inside an enclosure,
the enclosure itself must be broken up into a box with a lid, 
each in a separate OFF file, otherwise you get a solid cube. 
See the provided interdigital filter for an example of this.

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
    symmetric=False # make s-parameter matrices symmetric
    )
```

Where freq is a list of frequencies and sparam is a list of 
complex-number s-parameter matrices.  Each frequency in freq 
corresponds to its respective s-parameter matrix in sparam.
The numpy array sparam has the shape (nfreq, m, n).

To read s-parameters from a string in touchstone format, or to
return s-parameters as a string using the touchstone format, 
use:

```python
f, s = rffdtd.read_touchstone(
    text            # load a touchstone file which is residing in a string
)
text = rffdtd.write_touchstone(  # return a touchstone file as a string
    f,              # frequencies corresponding to each s-parameter matrix
    s,              # list of s-parameter matrices
    dtype=None,     # formatting, whether 'RI', 'MA' or 'DB' (default 'RI')
    zo=None,        # line impedance of ports in ohms (default 50)
    precision=None  # number of signficant digits to output (default 6)
)
```

To load s-parameters from a text file in the touchstone format or from a .npz file, or to write s-parameters to a text file using touchstone format or a .npz file, use:


```python
f, s = rffdtd.load_touchstone(
    filename        # name of text file or .npz file to load
)
rffdtd.save_touchstone(  # save to a touchstone file
    f,              # frequencies corresponding to each s-parameter matrix
    s,              # list of s-parameter matrices
    dtype=None,     # formatting, whether 'RI', 'MA' or 'DB' (default 'RI')
    zo=None,        # line impedance of ports in ohms (default 50)
    precision=None, # number of signficant digits to output (default 6)
    filename=None   # name of text file (by default console) or .nzp file 
)
```

## S-Parameter Output In .npz files

If s-sparameters are saved to a .npz file, the frequencies, 
s-parameters, and normalized impedance are stored
as the attributes 'f', 's', and 'z' respectively.

## util/snpsum.py

The script snpsum.py in the util directory sums up the sparameters matrices 
for each frequency across all the touchstone files passed on the 
command line.

{run("util/snpsum.py --help")}

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


""")


