"""
Connect to MySQl server
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
        if self.connection:
            self.connection.close()

    def set_market(self, symbol):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM `market` WHERE name=%s"
            cursor.execute(sql, (symbol,))
            row = cursor.fetchone()
            self.market_id = row['id']
            return row

    def get_symbol(self, symbol):
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

    def _process_row(self, row_index, csv_row):
        # Add new rows into self.upload_payload
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
        print('Loading %s...' % symbol)
        fetch_row = self.get_symbol(symbol)
        self.upload_payload = []
        return fetch_row['is_new']

    def _process_end(self, symbol):
        size = len(self.upload_payload)
        print('Upload %d rows' % size)
        if size > 0:
            with self.connection.cursor() as cursor:
                sql = ("REPLACE INTO `price`(symbol_id,date,open,high,low,close,volume) "
                       "VALUES(%s,%s,%s,%s,%s,%s,%s)")
                cursor.executemany(sql, self.upload_payload)
            self.connection.commit()
            print('Committed')

    def walk_market(self, path, filters=None):
        if isinstance(filters,str):
            filters = (filters,)
        for dirpath, dirnames, filenames in os.walk(path):
            market = os.path.basename(dirpath)
            if filters is None or market in filters:
                self.set_market(market)
                for filename in sorted(filenames):
                    if len(filename) > 0:
                        self._read_csv(dirpath, filename)

    def _read_csv(self, dir, filename):
        symbol = os.path.splitext(filename)[0]

        # Skip if already uploaded
        if not self._process_start(symbol) and not self.force:
            print('Skipped!')
            return

        with open(os.path.join(dir, filename), 'r', newline='') as f:
            reader = csv.reader(f, delimiter=',')
            # Skip Header
            next(reader)

            for i, line in enumerate(reader):
                self._process_row(i, line)
            self._process_end(symbol)

    def _cache_symbol_id(self, symbol):
        symbol_row = self.cache_symbol.get(symbol)
        if symbol_row is not None:
            return symbol_row['id']

        self.cache_symbol[symbol] = self.get_symbol(symbol)
        symbol_row = self.cache_symbol[symbol]
        return symbol_row['id']
