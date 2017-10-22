#!/usr/bin/env python
"""
Command line tool used to upload csv data to MySQL
"""

import sys
import os.path
from optparse import OptionParser
from database.rltrader import RLTraderConnector

Usage = """usage: %prog [options] [market1] [market2] ....

Examples:
    %prog -a SET                        upload all symbols in SET market
    %prog -i /path1 -d /path2 SET       upload only changed symbols in SET market require diff directory
"""


def main():
    parser = OptionParser(usage=Usage)
    parser.add_option('-c', '--config', type='string', dest='config_path',
                      help='database config')
    parser.add_option('-a', '--all', action='store_true', dest='all',
                      help='upload all symbols in market')
    parser.add_option('-d', '--diff', type='string', dest='diff_dir',
                      help='diff directory')
    parser.add_option('-i', '--input', type='string', dest='input_dir',
                      help='input directory')
    parser.add_option('-f', '--force', action='store_true', dest='force',
                      help='force replace')
    (options, args) = parser.parse_args()

    # check if the options are valid
    if not (options.all or options.diff_dir and len(args) > 0):
        parser.print_help()
        sys.exit(0)

    options.config_path = not options.config_path and 'dbconfig.json' or os.path.realpath(options.config_path)
    options.input_dir = not options.input_dir and '.' or os.path.realpath(options.input_dir)
    options.diff_dir = not options.diff_dir and None or os.path.realpath(options.diff_dir)

    # Run Application
    trader = RLTraderConnector(options)
    trader.walk_market(args)


if __name__ == '__main__':
    main()
