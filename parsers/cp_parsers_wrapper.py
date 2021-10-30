#!/usr/bin/python3
#
# -*- coding: utf-8 -*-
## this file is part of cheap_pie, a python tool for chip validation
## author: Marco Merlin
## email: marcomerli@gmail.com

import os
import sys
sys.path.append( os.path.join(os.path.dirname(__file__), '..') )

def cp_parsers_wrapper(p,hif=None):
    if p.vendor is None:
        fname = os.path.join(p.devicedir,p.regfname)
        print(fname)
    else:
        # if vendor is indicated, use file from repository
        fname = p.regfname

    if p.format == 'cmsis-svd':
        # parser build for CMSIS-SVD xml file format
        from parsers.svd_parse_repo import svd_parse
        hal = svd_parse(fname=fname,hif=hif,vendor=p.vendor)
    elif p.format == 'svd':
        # parser build for CMSIS-SVD xml file format
        from parsers.svd_parse_repo import svd_parse
        hal = svd_parse(fname=fname,hif=hif,vendor=p.vendor)
    elif p.format == 'ipxact':
        from parsers.ipxact_parse import ipxact_parse
        hal = ipxact_parse(fname=fname,hif=hif)
    elif p.format == 'ipyxact':
        from parsers.ipyxact_parse import ipxact_parse
        hal = ipxact_parse(fname=fname,hif=hif)
    else:
        print('Unsupported input format!')
        assert(False)

    return hal

def test_cp_parsers_wrapper():
    from cheap_pie_core.cp_cli import cp_cli
    p = cp_cli()
    hal = cp_parsers_wrapper(p)
    pass

if __name__ == '__main__':    
    test_cp_parsers_wrapper()
    pass