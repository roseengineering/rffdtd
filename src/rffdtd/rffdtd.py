
import time
import sys
import torch
import torch.distributed as dist
import torch.multiprocessing as mp
import numpy as np

from . import parseoff
from .conf import (DEFAULT_NTAU, DEFAULT_NDELAY, DEFAULT_DS, 
                  DEFAULT_ZLINE, DEFAULT_DTYPE,
                  MASTER_BACKEND, MASTER_URL)

muva = 4e-7 * np.pi     # permeability of a vacuum
epsz = 8.8541878128e-12 # permittivity of a vacuum
cair = 299792458.0      # speed of light


############
# simulator
############

def timestep(ds):
    # FDTD should be run as close to the stability limit as possible
    # see p71 of Computation Electromagnetics, Davidson
    dt = ds / cair / np.sqrt(3)
    return dt


def fneaf(er, sigma, dt):
    eaf = dt * sigma / (2 * er * epsz)
    return eaf


def fnca(er, sigma, ds):
    dt = timestep(ds)
    eaf = fneaf(er, sigma, dt)
    with np.errstate(invalid='ignore'):
        ca = (1 - eaf) / (1 + eaf)
    ca = np.nan_to_num(ca, nan=-1)
    return ca


def fncb(er, sigma, ds):
    dt = timestep(ds)
    eaf = fneaf(er, sigma, dt)
    cb = dt / ds / (er * epsz) / (1 + eaf)
    return cb


def fngb(ds):
    dt = timestep(ds)
    gb = dt / ds / muva
    return gb


def update_efield(E, H, ca, cb):
    E[0,1:,1:,1:] = ca[0] * E[0,1:,1:,1:] + cb[0] * (
                            H[2,1:,1:,1:] - H[2,1:,:-1,1:] - 
                            H[1,1:,1:,1:] + H[1,1:,1:,:-1])
    E[1,1:,1:,1:] = ca[1] * E[1,1:,1:,1:] + cb[1] * (
                            H[0,1:,1:,1:] - H[0,1:,1:,:-1] - 
                            H[2,1:,1:,1:] + H[2,:-1,1:,1:])
    E[2,1:,1:,1:] = ca[2] * E[2,1:,1:,1:] + cb[2] * (
                            H[1,1:,1:,1:] - H[1,:-1,1:,1:] - 
                            H[0,1:,1:,1:] + H[0,1:,:-1,1:])


def update_hfield(E, H, gb):
    H[0,:-1,:-1,:-1] += gb * (E[1,:-1,:-1,1:] - E[1,:-1,:-1,:-1] - 
                              E[2,:-1,1:,:-1] + E[2,:-1,:-1,:-1])
    H[1,:-1,:-1,:-1] += gb * (E[2,1:,:-1,:-1] - E[2,:-1,:-1,:-1] - 
                              E[0,:-1,:-1,1:] + E[0,:-1,:-1,:-1])
    H[2,:-1,:-1,:-1] += gb * (E[0,:-1,1:,:-1] - E[0,:-1,:-1,:-1] - 
                              E[1,1:,:-1,:-1] + E[1,:-1,:-1,:-1])


def capture_currents(H, indices, T, currents):
    for i in range(len(indices)):
        currents[i,T] = torch.sum(indices[i] * H)


def capture_voltages(E, indices, T, voltages):
    for i in range(len(indices)):
        voltages[i,T] *= torch.sum(E[indices[i]])


def update_voltages(E, ix, T, vs):
    E[ix] += vs[T]


def cubemag(index):
    axis = index[0][0]
    shape = list(max(d) - min(d) + 1 for d in index)[1:]
    area = np.prod(np.concatenate((shape[:axis], shape[axis+1:])))
    nfields = shape[axis]
    return area, nfields


def voltage_probes(ports):
    probes = []
    for i in range(len(ports)):
        ix = ports[i]
        axis = ix[0][0]
        cmin = np.min(ix[1:], axis=1)
        cmax = np.max(ix[1:], axis=1)
        iu, ju, ku = cmin
        ie, je, ke = cmax
        res = np.s_[axis:axis+1, iu:ie+1, ju:je+1, ku:ke+1 ]
        probes.append(res)
    return probes


def current_probes(ports):
    probes = []
    for i in range(len(ports)):
        ix = ports[i]
        axis = ix[0][0]
        cmin = np.min(ix[1:], axis=1)
        cmax = np.max(ix[1:], axis=1)
        cmid = np.mean((cmin, cmax), axis=0).astype(int)
        iu, ju, ku = cmin
        ie, je, ke = cmax
        im, jm, km = cmid
        if axis == 0:
            res = [ np.s_[1:2, im:im+1, ju:je+1, ku-1:ku],  # bottom 
                    np.s_[2:3, im:im+1, je:je+1, ku:ke+1],  # back
                    np.s_[1:2, im:im+1, ju:je+1, ke:ke+1],  # top
                    np.s_[2:3, im:im+1, ju-1:ju, ku:ke+1] ] # front
        if axis == 1:
            res = [ np.s_[2:3, iu-1:iu, jm:jm+1, ku:ke+1],  # left
                    np.s_[0:1, iu:ie+1, jm:jm+1, ke:ke+1],  # top
                    np.s_[2:3, ie:ie+1, jm:jm+1, ku:ke+1],  # right
                    np.s_[0:1, iu:ie+1, jm:jm+1, ku-1:ku] ] # bottom
        if axis == 2:
            res = [ np.s_[0:1, iu:ie+1, ju-1:ju, km:km+1],  # front
                    np.s_[1:2, ie:ie+1, ju:je+1, km:km+1],  # right
                    np.s_[0:1, iu:ie+1, je:je+1, km:km+1],  # back
                    np.s_[1:2, iu-1:iu, ju:je+1, km:km+1] ] # left
        probes.append(res)
    return probes


########
# main 
########

def dftosteps(df, ds):
    dt = timestep(ds)
    steps = 1 / (df * dt)
    return steps


def stepstodf(steps, ds):
    dt = timestep(ds)
    df = 1 / (steps * dt)
    return df


def fmaxtimewidth(ntau, ds):
    # tau = sqrt(2.3) / (pi * fmax) or approximately .5 / fmax
    dt = timestep(ds)
    fmax = .5 / (ntau * dt)
    return fmax


def excitation(steps, t0, ntau):
    # use the gaussian derivative to avoid simulating low frequency components
    # rather than the gaussian, ie v = np.exp(-((t - t0) / ntau)**2)
    t = np.arange(steps)
    v = -np.sqrt(2 * np.exp(1)) / ntau * (t - t0) * np.exp(-((t - t0) / ntau)**2)
    return v


def simulate(filename, 
             df=None, 
             ds=DEFAULT_DS,
             ntau=DEFAULT_NTAU,
             ndelay=DEFAULT_NDELAY,
             zline=DEFAULT_ZLINE,
             dtype=DEFAULT_DTYPE,
             device=None,
             steps=None, 
             start=None, 
             stop=None, 
             ngpu=None
            ):

    # calculate steps
    t0 = np.ceil(ndelay * ntau)
    steps = dftosteps(df, ds) if df else steps or 0
    steps = int(np.rint(max(steps, 2 * t0)))

    # load model
    er, sigma, ports = parseoff.parser(filename, ds=ds)
    nport = len(ports)

    # set port conductivities
    for ix in ports:
        area, nfields = cubemag(ix)
        sigma[ix] = 1 / (area / nfields * zline * ds)
        er[ix] = 1

    # find memory needed
    itemsize = 8 if dtype.lower() == 'double' else 4
    nbytes = (2 * er.size * er.itemsize +     # ca, cb
              2 * er.size * itemsize +        # E, H
              nport * er.size +               # probes
              2 * nport * steps * itemsize +  # currents, voltages
              steps * itemsize)               # vs
    print('Each individual simulation needs about {:.3f} MiB of memory.'
          .format(nbytes / 2**20), file=sys.stderr)

    # deallocate er and sigma
    er = er[:,1:,1:,1:]
    sigma = sigma[:,1:,1:,1:]
    ca = fnca(er, sigma, ds)
    cb = fncb(er, sigma, ds)
    del er, sigma  

    # ports to excite
    start = 0 if start is None else np.max((0, start - 1))
    stop = nport if stop is None else np.min((nport, stop))
    start = np.min((start, nport))
    stop = np.max((stop, start))
    port_area = [ cubemag(ix)[0] for ix in ports ]
    cprobes_ix = current_probes(ports)
    vprobes_ix = voltage_probes(ports)

    # simulation payload
    payload = {
        'ca': ca,
        'cb': cb,
        'ds': ds,
        't0': t0,
        'ntau': ntau,
        'steps': steps,
        'nport': nport,
        'port_area': port_area,
        'cprobes_ix': cprobes_ix,
        'vprobes_ix': vprobes_ix,
        'ports': ports,
        'zline': zline,
        'start': start,
        'stop': stop,
        'dtype': dtype
    }

    # determine device
    if device is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # run simulations
    nsim = stop - start
    size = torch.cuda.device_count()
    size = size if ngpu is None or ngpu > size else ngpu
    size = min(nsim, size)

    # handle multiple gpus
    if device == 'cuda' and stop - start > 1 and size > 1:
        print(f'Distributing {nsim} simulations across {size} GPUs:', file=sys.stderr)
        for i in range(size):
            name = torch.cuda.get_device_name(i)
            print(f'  GPU {i}: {name}', file=sys.stderr)
        sparam = simulate_multigpu(size, payload)

    # otherwise
    else:
        print(f'Running {nsim} simulation(s) on device {device}.', file=sys.stderr)
        if device == 'cuda' or device[:5] == 'cuda:':
            name = torch.cuda.get_device_name(device)
            print(f'Using GPU: {name}', file=sys.stderr)
        sparam = simulate_batch(start, stop, device, payload)

    # convert back to numpy from pytorch
    sparam = sparam.numpy()

    # show elapsed time
    elapsed = time.time() - payload['time']
    print('\nFDTD simulation time: {:d} min {:.2f} sec'.format(
          int(elapsed / 60), elapsed % 60), file=sys.stderr)

    # keep resolvable frequencies
    fmax = fmaxtimewidth(ntau, ds)
    df = stepstodf(steps, ds)
    nfreq = int(fmax / df) + 1
    dt = timestep(ds)
    freq = np.fft.rfftfreq(steps, d=dt)[:nfreq]
    sparam = sparam[:nfreq]

    # exclude dc components
    sparam = sparam[1:]
    freq = freq[1:]
    return freq, sparam


#########################
# multiple gpu functions
#########################

def simulate_multigpu(size, payload):
    mp.set_start_method("spawn")
    processes = []
    for rank in range(1, size):
        args = (rank, size, f'cuda:{rank}', payload)
        p = mp.Process(target=simulate_worker, args=args)
        p.start()
        processes.append(p)
    tensor = simulate_worker(0, size, 'cuda:0', payload)
    for p in processes:
        p.join()
    sparam = torch.complex(tensor[0], tensor[1])
    return sparam


def simulate_worker(rank, size, device, payload):
    dist.init_process_group(
        backend=MASTER_BACKEND,
        init_method=MASTER_URL,
        rank=rank,
        world_size=size)

    start = payload['start']
    stop = payload['stop']

    # run batch
    inc = int(np.ceil((stop - start) / size))
    bstart = start + inc * rank
    bstop = min(start + inc * (rank + 1), stop)
    tensor = simulate_batch(bstart, bstop, device, payload)

    # reduce fails on complex tensors
    tensor = torch.stack((tensor.real, tensor.imag))
    dist.reduce(tensor, dst=0)
    return tensor


#########################
# simulation routines
#########################

def show_progress(T, steps, n):
    if T == 0 or T + 1 == steps or (T + 1) % 100 == 0:
        print('  {} / {} / {}   '.format(T+1, steps, n+1), end='\r', file=sys.stderr)


def simulate_batch(start, stop, device, payload):
    steps = payload['steps']
    nport = payload['nport']
    ca = payload['ca']
    cb = payload['cb']
    assert(ca.dtype == np.float32)
    assert(cb.dtype == np.float32)

    # send tensors to device
    payload['ca'] = torch.from_numpy(ca).to(device)
    payload['cb'] = torch.from_numpy(cb).to(device)

    # run simulations
    nfreq = steps // 2 + 1
    sparam = torch.zeros((nfreq, nport, nport), dtype=torch.complex128)
    for n in range(start, stop):
        sparam[:,:,n] = simulate_fdtd(n, device, payload)
    return sparam


def simulate_fdtd(n, device, payload):
    if 'time' not in payload:
        payload['time'] = time.time()

    # unload payload
    ca = payload['ca']
    cb = payload['cb']
    ds = payload['ds']
    nport = payload['nport']
    port_area = payload['port_area']
    cprobes_ix = payload['cprobes_ix']
    vprobes_ix = payload['vprobes_ix']
    ports = payload['ports']
    zline = payload['zline']
    dtype = payload['dtype']
    steps = payload['steps']
    ntau = payload['ntau']
    t0 = payload['t0']

    # determine torch dtype
    if dtype == 'double': dtype = torch.float64
    if dtype == 'float': dtype = torch.float32

    # simulation constants
    shape = tuple(ca.shape + (np.arange(4) > 0))
    currents = np.zeros((nport, steps))
    voltages = np.ones((nport, steps))
    for i in range(nport):
        voltages[i] *= -1 / port_area[i]

    # initialize tensors on device
    E = torch.zeros(shape, dtype=dtype, device=device)
    H = torch.zeros(shape, dtype=dtype, device=device)
    vs = torch.tensor(excitation(steps, t0, ntau), dtype=dtype, device=device)
    gb = torch.tensor(fngb(ds), dtype=dtype, device=device)
    currents = torch.tensor(currents, dtype=dtype, device=device)
    voltages = torch.tensor(voltages, dtype=dtype, device=device)

    # initialize current probe tensors on device
    cprobes = []
    for i in range(nport):
        d = torch.zeros(shape, dtype=torch.int8, device=device)
        ix = cprobes_ix[i]
        d[ix[0]] = 1
        d[ix[1]] = 1
        d[ix[2]] = -1
        d[ix[3]] = -1
        cprobes.append(d)

    # run simulation
    for T in range(steps):
        show_progress(T, steps, n)
        update_hfield(E, H, gb)
        capture_currents(H, cprobes, T, currents)    # 54s (slice) / 19s (dense)
        update_efield(E, H, ca, cb)
        update_voltages(E, vprobes_ix[n], T, vs)
        capture_voltages(E, vprobes_ix, T, voltages) # 16s (slice) / 21s (dense)
    voltages = voltages.cpu()
    currents = currents.cpu()

    # calculate s-parameters
    voltages = torch.fft.rfft(voltages)
    currents = torch.fft.rfft(currents)
    a = 0.5 * (voltages + zline * currents) / np.sqrt(zline)
    b = 0.5 * (voltages - zline * currents) / np.sqrt(zline)
    return (b / a[n]).T





