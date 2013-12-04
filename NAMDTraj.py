'''Functions for manipulating trajectory files.  Currently
relies on VMD calls through the shell, and as such is dependent on
VMD CML access and living on a UNIX-like system.'''

import NAMDConf
import os

def extract_data(Config, target = "protein noh", time_cut = 0):
    #Properties I'll need exposed
    #Config.dcd_file   DONE
    #Config.psf_file   DONE
    #Config.timestep   DONE
    #Config.total_time DONE
    #NAMDConf will need variable substitution in these parameters 
    pass


