"""
Connect to MySQl server
"""

import json
import pymysql.cursors


class RLTraderConnector(object):
    config = None
    connection = None

    def __init__(self, options):
        with open(options.config_path) as json_data_file:
            self.config = json.load(json_data_file)['database']

        self.connection = pymysql.connect(host=self.config['host'],
                                     user=self.config['user'],
                                     password=self.config['password'],
                                     port=self.config['port'],
                                     db=self.config['db'],
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

    def __del__(self):
        if self.connection:
            self.connection.close()

    def test(self):
        with self.connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT * FROM `market` where id=%s"
            cursor.execute(sql, (int(0),))
            result = cursor.fetchone()
            print(result)
