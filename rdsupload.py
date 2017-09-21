#!/usr/bin/env python
"""
Command line tool used to upload csv data to Amazon RDS
"""

import sys
import os.path
from optparse import OptionParser
from database.rltrader import RLTraderConnector

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
    parser.add_option('-c', '--config', type='string', dest='config_path',
                      help='database config')
    (options, args) = parser.parse_args()

    options.config_path = not (options.config_path) and 'dbconfig.json' or os.path.realpath(options.config_path)

    # Run Application
    trader = RLTraderConnector(options)
    trader.test()

if __name__ == '__main__':
    main()
