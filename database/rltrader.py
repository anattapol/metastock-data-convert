"""
Upload data to RLTrader data set
"""

import csv
import os
import json
import pymysql.cursors
from datetime import datetime


class RLTraderConnector(object):
    cache_symbol = {}
    config = None
    connection = None
    force = None
    market_id = None
    upload_payload = []

    def __init__(self, options):
        """
        RLTraderConnector Constructor

        Copy options into private variable

        Parameters
        ----------
        options.config_path : str
            Path to dbconfig.json, use for connecting to database

        options.force : bool, optional
            Force upload to replace existing price data on symbol that recognized

        Private Variables
        ----------
        cache_symbol : str
            Buffer mapping symbol_name -> SymbolSQLRow

        config
            Store database configuration read from dbconfig.json

        connection
            Store activate MySQL connection

        force : bool
            Store command line `options.force` value

        market_id : int
            Store current market_id

        upload_payload : list(tuple)
            Buffer rows for bulk REPLACE(INSERT) operation

        """
        with open(options.config_path) as json_data_file:
            self.config = json.load(json_data_file)['database']

        self.force = options.force
        self.connection = pymysql.connect(
            host=self.config['host'],
            user=self.config['user'],
            password=self.config['password'],
            port=self.config['port'],
            db=self.config['db'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def __del__(self):
        """
        Close MySQL Connection after object has been garbage collected
        """
        if self.connection:
            self.connection.close()

    def set_market(self, symbol):
        """
        Fetch row data from `market`
        Also change self.market_id for preceding upload chunks

        Require market data to be pre-existing in database

        Parameters
        ----------
        symbol : str
            Symbol of Market. Retrieved from csv-directory structure.

        Returns
        -------
        MarketSQLRow

        """
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM `market` WHERE name=%s"
            cursor.execute(sql, (symbol,))
            row = cursor.fetchone()
            self.market_id = row['id']
            return row

    def get_symbol(self, symbol):
        """
        Fetch row data from `symbol`

        If that symbol is not existing, create new symbol and return new row

        Parameters
        ----------
        symbol : str

        Returns
        -------
        SymbolSQLRow

        """
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM `symbol` WHERE name=%s and market_id=%s"
            cursor.execute(sql, (symbol, self.market_id))
            row = cursor.fetchone()
            if row is not None:
                row['is_new'] = False
                return row

            sql = "INSERT INTO `symbol`(name,market_id) VALUES(%s,%s)"
            cursor.execute(sql, (symbol, self.market_id))
            # self.connection.commit()

            sql = "SELECT * FROM `symbol` WHERE ID=last_insert_id()"
            cursor.execute(sql)
            row = cursor.fetchone()
            row['is_new'] = True
            return row

    def get_price_count(self, symbol_id):
        """
        Fetch count rows owned by symbol_id

        Parameters
        ----------
        symbol_id : int

        Returns
        -------
        int

        """
        with self.connection.cursor() as cursor:
            sql = "SELECT count(*) FROM `price` WHERE symbol_id=%s"
            cursor.execute(sql, (symbol_id,))
            row = cursor.fetchone()
            return row[0]

    def _process_row(self, row_index, csv_row):
        """
        Add new rows into self.upload_payload

        Parameters
        ----------
        row_index : int
            Symbol of Security. Retrieved from CSV file name.

        csv_row : CSVRow
            Row data read from CSV
                [0] symbol_name
                [1] date
                [2] open
                [3] high
                [4] low
                [5] close
                [6] volume

        """
        self.upload_payload.append(
            (self._cache_symbol_id(csv_row[0]),
             datetime.strptime(csv_row[1], '%Y%m%d').date(),
             csv_row[2],
             csv_row[3],
             csv_row[4],
             csv_row[5],
             csv_row[6]
            )
        )

    def _process_start(self, symbol):
        """
        Check before start read csv

        Currently does not proceed if symbol existed in database

        Parameters
        ----------
        symbol : str
            Symbol of Security

        Returns
        -------
        bool
            Should proceed to read csv file or not

        """
        print('Loading %s...' % symbol)
        fetch_row = self.get_symbol(symbol)
        self.upload_payload = []
        rds_row_count = self.get_price_count(fetch_row['id'])
        print('row count: %d' % rds_row_count)
        return fetch_row['is_new']

    def _process_end(self, symbol):
        """
        Perform bulk REPLACE(INSERT) from self.upload_payload once csv has been read for that security
        Commit afterward

        Parameters
        ----------
        symbol : str

        """
        size = len(self.upload_payload)
        print('Upload %d rows' % size)
        if size > 0:
            with self.connection.cursor() as cursor:
                sql = ("REPLACE INTO `price`(symbol_id,date,open,high,low,close,volume) "
                       "VALUES(%s,%s,%s,%s,%s,%s,%s)")
                cursor.executemany(sql, self.upload_payload)
            self.connection.commit()
            print('Committed')

    def walk_market(self, dirpath, filters=None):
        """
        Scan through all file in path. If market symbol found in filters then proceed read csv from that directory
        File in directory need to end with .TXT and not start with '$' (funky data from CDCDL)

        Parameters
        ----------
        dirpath : str

        filters : list(str), optional
            List of market that will be process
            Default will scan all market

        """
        if isinstance(filters,str):
            filters = (filters,)
        for dirpath, dirnames, filenames in os.walk(dirpath):
            market = os.path.basename(dirpath)
            if filters is None or market in filters:
                self.set_market(market)

                # Only grab csv file with extension .TXT
                csv_list = sorted([f for f in filenames if f.endswith('.TXT') and not f.startswith('$')])
                for filename in csv_list:
                    self._read_csv(dirpath, filename)

    def _read_csv(self, dirpath, filename):
        """
        Read csv file

        Pre-check condition using self._process_start(symbol)
        Process row using self._process_row(i, line)
        Commit rows using self._process_end(symbol)

        Parameters
        ----------
        dirpath : str
        filename : str

        """
        symbol = os.path.splitext(filename)[0].replace('_','/')

        # Skip if already uploaded
        if not self._process_start(symbol) and not self.force:
            print('Skipped!')
            return

        with open(os.path.join(dirpath, filename), 'r', newline='') as f:
            reader = csv.reader(f, delimiter=',')
            # Skip Header
            next(reader)

            for i, line in enumerate(reader):
                self._process_row(i, line)
            self._process_end(symbol)

    def _cache_symbol_id(self, symbol):
        """
        Find symbol_id self.cache_symbol
        If not hit, fetch from database using self.get_symbol(symbol)

        Parameters
        ----------
        symbol : str

        Returns
        -------
        int
            symbol_id

        """
        symbol_row = self.cache_symbol.get(symbol)
        if symbol_row is not None:
            return symbol_row['id']

        self.cache_symbol[symbol] = self.get_symbol(symbol)
        symbol_row = self.cache_symbol[symbol]
        return symbol_row['id']
