#!/usr/bin/python3
#
# -*- coding: utf-8 -*-
## this file is part of cheap_pie, a python tool for chip validation
## author: Marco Merlin
## email: marcomerli@gmail.com

# Ipython autoreload
# %load_ext autoreload
# %autoreload 2
# %reset
# %run cheap_pie

# init transport
import sys
# clear all references
sys.modules[__name__].__dict__.clear()

## banner #######################################################################
from cheap_pie_core.cp_banner import cp_banner
cp_banner()

## input parameters ###########################################################
print('Parsing input arguments...')

if 'p' not in locals():
    from cheap_pie_core.cp_cli import cp_cli
    import sys
    p = cp_cli(sys.argv[1:])

## configure paths %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
print('Configuring paths...')

import os
import sys
global system_root
system_root = os.getcwd()

## transport hif interface %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
print('Initialising Host Interface...')

# init jlink transport
if p.transport == 'jlink': # disable jlink for testing
    from transport.cp_jlink_transport import cp_jlink
    hif = cp_jlink(device = p.device )
elif p.transport == 'dummy':
    from transport.cp_dummy_transport import cp_dummy
    hif = cp_dummy()
elif p.transport == 'ocd':
    from transport.cp_pyocd_transport import cp_pyocd
    hif = cp_pyocd(device = p.device )
elif p.transport == 'esptool':
    from transport.cp_esptool_transport import cp_esptool
    hif = cp_esptool(port = p.port )   
elif p.transport == 'verilator':
    from transport.cp_pyverilator_transport import cp_pyverilator_transport
    hif = cp_pyverilator_transport( p.top_verilog )
else:
    hif=None
    # assert(False,'Invalid transport: %s' % p.transport)
    assert(False)

## init chip ##################################################################
print('Initialising Hardware Abstraction Layer...')
from parsers.cp_parsers_wrapper import cp_parsers_wrapper
from cheap_pie_core.cp_hal import cp_hal
hal = cp_hal( cp_parsers_wrapper( p, hif=hif ) )

## welcome ####################################################################
print('Cheap Pie is ready! Type hal.<TAB> to start browsing...')