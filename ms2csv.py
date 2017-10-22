#!/usr/bin/env python
"""
Command line tool used to extract the data from metastock files and save it
in text format.
"""

import sys
import os.path
from optparse import OptionParser

from metastock.files import MSEMasterFile, MSXMasterFile

Usage = """usage: %prog [options] [symbol1] [symbol2] ....

Examples:
    %prog -p 2 --all        extract all symbols from EMASTER file
    %prog FW20 "S&P500"     extract FW20 and S&P500 from EMASTER file
"""


def main():
    """
    launched when running this file
    """

    parser = OptionParser(usage=Usage)
    parser.add_option('-l', '--list', action='store_true', dest='list',
                      help='list all the symbols from EMASTER/XMASTER file')
    parser.add_option('-a', '--all', action='store_true', dest='all',
                      help='extract all the symbols from EMASTER/XMASTER file')
    parser.add_option('-p', '--precision', type='int', dest='precision',
                      help='round the floating point numbers to PRECISION digits after the decimal point (default: 2)')
    parser.add_option('-i', '--input', type='string', dest='input_dir',
                      help='input directory')
    parser.add_option('-o', '--output', type='string', dest='output_dir',
                      help='output directory')

    (options, args) = parser.parse_args()

    # check if the options are valid
    if not (options.all or options.list or len(args) > 0):
        parser.print_help()
        sys.exit(0)

    options.input_dir = not options.input_dir and '.' or os.path.realpath(options.input_dir)
    options.output_dir = not options.output_dir and '.' or os.path.realpath(options.output_dir)

    for dirpath, dirnames, filenames in os.walk(options.input_dir):
        for subdirname in dirnames:
            scan_directory(options, args, subdirname)


def scan_directory(options, args, subdirname=None):
    """
    Add support to CDCDL substructure

    Parameters
    ----------
    options
        pass options

    args
        pass args

    subdirname
        pass subdirname from loop

    """
    fullpath = subdirname is not None and \
                os.path.join(options.input_dir, subdirname) or \
                os.path.join(options.input_dir)

    if os.path.isfile(os.path.join(fullpath, 'EMASTER')):
        em_file = MSEMasterFile(options, subdirname)
        # list the symbols or extract the data
        if options.list:
            em_file.list_all_symbols()
        else:
            em_file.output_ascii(options.all, args)
    else:
        print('Could not found file %s in path %s' % ('EMASTER', options.input_dir, subdirname))
        exit(1)

    if os.path.isfile(os.path.join(fullpath, 'XMASTER')):
        xm_file = MSXMasterFile(options, subdirname)
        # list the symbols or extract the data
        if options.list:
            xm_file.list_all_symbols()
        else:
            xm_file.output_ascii(options.all, args)


if __name__ == '__main__':
    main()
