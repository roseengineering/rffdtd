
import numpy as np

CONDUCTOR = {
    'pec':      np.inf,
    'silver':   62.1e6,  # s/m
    'copper':   58.7e6,
    'gold':     44.2e6,
    'aluminum': 36.9e6,
    'brass':    15.9e6,
    'steel':    10.1e6,
    'air':      0
}

MARGIN  = 1             # separation of pec border from the sides of the grid
PADDING = 1

DEFAULT_NTAU = 20       # 20 should be sufficent for a gaussian pulse
DEFAULT_NDELAY = 6.5    # for negligible transition at t=0 with double
DEFAULT_DS = .001
DEFAULT_ZLINE = 50
DEFAULT_DTYPE = 'float'

MASTER_BACKEND = 'gloo'
MASTER_URL = 'tcp://127.0.0.1:29500'

