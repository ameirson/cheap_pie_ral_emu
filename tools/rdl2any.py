#!/usr/bin/python3

import sys
import os
from systemrdl import RDLCompiler, RDLCompileError
from peakrdl.verilog import VerilogExporter
from peakrdl.ipxact import IPXACTExporter
from peakrdl.uvm import UVMExporter
import argparse

def cli(args):
    parser = argparse.ArgumentParser(description='rdl2any')
    # register format options
    parser.add_argument("-f", "--fname", help="register file description .rdl", action='store', type = str, default="./devices/rdl/basic.rdl")
    parser.add_argument("-ofmt", "--out-format", help="output format", action='store', type = str, default="ipxact", choices=["ipxact","uvm"])

    return parser.parse_args(args)

def main(args=[]):
    p = cli(args)
    rdlc = RDLCompiler()

    try:
        rdlc.compile_file(p.fname)
        root = rdlc.elaborate()
    except RDLCompileError:
        sys.exit(1)

    if p.out_format == 'ipxact': 
        exporter = IPXACTExporter()
        ext = '.xml'
    elif p.out_format == 'uvm': 
        exporter = UVMExporter()
        ext = '.uvm'
    else:
        print('Unsupported output format!')
        assert(False)

    base = os.path.splitext(p.fname)[0]
    outfname = base + ext
    print('output file: ' + outfname)
    exporter.export(root, outfname )
    return outfname

def test_rdl2any():
    main(['-ofmt','ipxact'])
    main(['-ofmt','uvm'])

if __name__ == '__main__':
    main(sys.argv[1:])