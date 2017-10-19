"""
Reading metastock files.
"""

import re
import traceback
import os.path

from .utils import *


class DataFileInfo(object):
    """
    I represent a metastock data describing a single symbol, each symbol has a number (file_num).

    To read the quotes we need to read two files: a <file_num>.DAT file with the tick data and a <file_num>.DOP
    file describing what columns are in the DAT file

    Private Variables
    ----------
    file_num : int
        Symbol number

    num_fields : int
        Number of columns in DAT file

    stock_symbol : str
        Stock symbol

    stock_name : str
        Full stock name

    time_frame : char
        Tick time frame (f.e. 'D' means EOD data)

    first_date : date
        First tick date

    last_date : date
        Last tick date

    columns : list
        List of columns names

    """
    file_num = None
    num_fields = None
    stock_symbol = None
    stock_name = None
    time_frame = None
    first_date = None
    last_date = None

    reg = re.compile('\"(.+)\",.+', re.IGNORECASE)
    columns = None

    def _load_columns(self):
        """
        Read columns names from the DOP file
        """
        filename = 'F%d.DOP' % self.file_num
        if not os.path.isfile(filename):
            self.columns = ['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOL', 'OI']
            return
        file_handle = open(filename, 'r')
        lines = file_handle.read().split()
        file_handle.close()
        assert(len(lines) == self.num_fields)
        self.columns = []
        for line in lines:
            match = self.reg.search(line)
            colname = match.groups()[0]
            self.columns.append(colname)

    class Column(object):
        """
        This is a base class for classes reading metastock data for a specific columns.
        The read method is called when reading a decode the column value

        Private Variables
        ----------
        dataSize : int
            Number of bytes is the data file that is used to store a single value

        name : str
            Column name

        """
        dataSize = 4
        name = None

        def __init__(self, name):
            self.name = name

        def read(self, b):
            """
            Read and return a column value
            """

        def format(self, value):
            """
            Return a string containing a value returned by read method
            """
            return str(value)

    class DateColumn(Column):
        """
        A date column
        """
        def read(self, b):
            """
            Convert from MBF to date string
            """
            return float2date(fmsbin2ieee(b))

        def format(self, value):
            if value is not None:
                return value.strftime('%Y%m%d')
            return DataFileInfo.Column.format(self, value)

    class TimeColumn(Column):
        """
        A time column
        """
        def read(self, b):
            """
            Convert read bytes from MBF to time string
            """
            return float2time(fmsbin2ieee(b))

        def format(self, value):
            if value is not None:
                return value.strftime('%Y%m%d')
            return DataFileInfo.Column.format(self, value)

    class FloatColumn(Column):
        """
        A float column

        Private Variables
        ----------
        precision : int
            Round floats to n digits after the decimal point

        """
        precision = 2

        def read(self, b):
            """
            Convert bytes containing MBF to float
            """
            return fmsbin2ieee(b)

        def format(self, value):
            return ("%0."+str(self.precision)+"f") % value

    class IntColumn(Column):
        """
        An integer column
        """
        def read(self, b):
            """Convert MBF bytes to an integer"""
            return int(fmsbin2ieee(b))

    # we map a metastock column name to an object capable reading it
    knownMSColumns = {
        'DATE': DateColumn('Date'),
        'TIME': TimeColumn('Time'),
        'OPEN': FloatColumn('Open'),
        'HIGH': FloatColumn('High'),
        'LOW': FloatColumn('Low'),
        'CLOSE': FloatColumn('Close'),
        'VOL': IntColumn('Volume'),
        'OI': IntColumn('OI'),
    }
    unknownColumnDataSize = 4    # assume unknown column data is 4 bytes long

    max_recs = 0
    last_rec = 0

    def load_candles(self, input_dir, output_dir):
        """
        Load metastock DAT file and write the content
        to a text file

        Parameters
        ----------
        input_dir : str
            Path of MetaStock directory input

        output_dir : str
            Path of CSV directory output

        """
        file_handle = None
        outfile = None
        try:
            ext = (self.file_num <= 255) and 'DAT' or 'MWD'
            filename = 'F%d.%s' % (self.file_num, ext)
            fullpath = os.path.join(input_dir, filename)
            if os.path.getsize(fullpath) == 28:
                print("Corrupt DAT suspected file no: %d" % self.file_num)
                return

            file_handle = open(fullpath, 'rb')
            self.max_recs = readshort(file_handle.read(2))
            self.last_rec = readshort(file_handle.read(2))

            # not sure about this, but it seems to work
            # file_handle.read((self.num_fields - 1) * 4)
            file_handle.read(24)

            # print "Expecting %d candles in file %s. num_fields : %d" % \
            #    (self.last_rec - 1, filename, self.num_fields)

            sanitize_filename = self.stock_symbol.replace('/','_')
            output_filename = os.path.join(output_dir, '%s.TXT' % sanitize_filename)
            outfile = open(output_filename, 'w')
            # write the header line, for example:
            # "Name","Date","Time","Open","High","Low","Close","Volume","Oi"
            outfile.write('"Name"')
            columns = []
            for ms_col_name in self.columns:
                column = self.knownMSColumns.get(ms_col_name)
                if column is not None:
                    outfile.write(',"%s"' % column.name)
                columns.append(column) # we append None if the column is unknown
            outfile.write('\n')

            # we have (self.last_rec - 1) candles to read
            for _ in range(self.last_rec - 1):
                outfile.write(self.stock_symbol)
                for col in columns:
                    if col is None: # unknown column?
                        # ignore this column
                        file_handle.read(self.unknownColumnDataSize)
                    else:
                        # read the column data
                        b = file_handle.read(col.dataSize)
                        # decode the data
                        if (len(b) == 0):
                            print("Corrupt DAT after read skipped file no: %d" % self.file_num)
                            return

                        value = col.read(b)
                        # format it
                        value = col.format(value)
                        outfile.write(',%s' % value)


                outfile.write('\n')
        finally:
            if outfile is not None:
                outfile.close()
            if file_handle is not None:
                file_handle.close()

    def convert2ascii(self, input_dir, output_dir):
        """
        Load Metastock data file and output the data to text file.

        Parameters
        ----------
        input_dir : str
            Path of MetaStock directory input

        output_dir : str
            Path of CSV directory output

        """
        print("Processing %s (fileNo %d)" % (self.stock_symbol, self.file_num))
        try:
            # print self.stock_symbol, self.file_num
            self._load_columns()
            # print self.columns
            self.load_candles(input_dir, output_dir)
        except Exception:
            print("Error while converting symbol", self.stock_symbol)
            traceback.print_exc()

class MSEMasterFile(object):
    """
    Metastock extended index file
    Control file number 1-255

    Private Variables
    ----------
    stocks : list(DataFileInfo)
        List of DataFileInfo objects

    """
    stocks = None

    def _read_file_info(self, file_handle):
        """
        read the entry for a single symbol and return a DataFileInfo

        Parameters
        ----------
        file_handle
            EMASTER file handle

        Returns
        -------
        DataFileInfo

        """
        dfi = DataFileInfo()
        file_handle.read(2)
        dfi.file_num = readbyte(file_handle.read(1))
        file_handle.read(3)
        dfi.num_fields = readbyte(file_handle.read(1))
        file_handle.read(4)
        dfi.stock_symbol = readstr(file_handle.read(14))
        file_handle.read(7)
        dfi.stock_name = readstr(file_handle.read(16))
        file_handle.read(12)
        dfi.time_frame = readchar(file_handle.read(1))
        file_handle.read(3)
        dfi.first_date = float2date(readfloat(file_handle.read(4)))
        file_handle.read(4)
        dfi.last_date = float2date(readfloat(file_handle.read(4)))
        file_handle.read(116)
        return dfi

    def __init__(self, options, subdir=None):
        """
        The whole file is read while creating this object

        Parameters
        ----------
        options.filename : str
            Name of the file to open (usually 'EMASTER')

        options.precision : int
            round floats to n digits after the decimal point

        """
        precision = not (options.precision) and None or options.precision
        if precision is not None:
            DataFileInfo.FloatColumn.precision = precision
        file_name = subdir is not None and \
            os.path.join(options.input_dir, subdir, 'EMASTER') or \
            os.path.join(options.input_dir, 'EMASTER')
        file_handle = open(file_name, 'rb')
        files_no = readshort(file_handle.read(2))
        last_file = readshort(file_handle.read(2))
        file_handle.read(188)
        self.stocks = []
        self.options = options
        # print files_no, last_file
        while files_no > 0:
            self.stocks.append(self._read_file_info(file_handle))
            files_no -= 1
        file_handle.close()

    def list_all_symbols(self):
        """
        Lists all the symbols from metastock index file and writes it to the output
        """
        print("List of available symbols:")
        for stock in self.stocks:
            print("symbol: %s, name: %s, file number: %s" %
                   (stock.stock_symbol, stock.stock_name, stock.file_num))

    def output_ascii(self, all_symbols, symbols):
        """
        Read all or specified symbols and write them to text
        files (each symbol in separate file)

        Parameters
        ----------
        all_symbols : bool
            When True, all symbols are processed

        symbols : list(str)
            List of symbols to process

        """
        for stock in self.stocks:
            if all_symbols or (stock.stock_symbol in symbols):
                stock.convert2ascii(self.options.input_dir, self.options.output_dir)


class MSXMasterFile(object):
    """
    Metastock XMASTER index file
    Control file number 255+

    Private Variables
    ----------
    stocks : list(DataFileInfo)
        List of DataFileInfo objects

    """
    stocks = None

    def _read_file_info(self, file_handle):
        """
        read the entry for a single symbol and return a DataFileInfo

        Parameters
        ----------
        file_handle
            XMASTER file handle

        Returns
        -------
        DataFileInfo

        """
        dfi = DataFileInfo()
        file_handle.read(1)
        dfi.stock_symbol = readstr(file_handle.read(15))
        dfi.stock_name = readstr(file_handle.read(46))
        dfi.time_frame = readchar(file_handle.read(1))
        file_handle.read(2)
        dfi.file_num = readshort(file_handle.read(2))
        file_handle.read(37)
        dfi.first_date = int2date(readint(file_handle.read(4)))
        file_handle.read(8)
        dfi.last_date = int2date(readint(file_handle.read(4)))
        file_handle.read(30)
        return dfi

    def __init__(self, options, subdir=None):
        """
        The whole file is read while creating this object

        Parameters
        ----------
        options.filename : str
            Name of the file to open (usually 'XMASTER')

        options.precision : int
            round floats to n digits after the decimal point

        """
        precision = not (options.precision) and options.precision or None
        if precision is not None:
            DataFileInfo.FloatColumn.precision = precision
        file_name = subdir is not None and \
                    os.path.join(options.input_dir, subdir, 'EMASTER') or \
                    os.path.join(options.input_dir, 'XMASTER')
        file_handle = open(file_name, 'rb')
        file_handle.read(10)
        files_no = readshort(file_handle.read(2))
        file_handle.read(2)
        last_file = readshort(file_handle.read(2))
        file_handle.read(2)
        next = readshort(file_handle.read(2))
        file_handle.read(130)
        self.stocks = []
        self.options = options
        # print files_no, last_file
        while files_no > 0:
            self.stocks.append(self._read_file_info(file_handle))
            files_no -= 1
        file_handle.close()

    def list_all_symbols(self):
        """
        Lists all the symbols from metastock index file and writes it to the output
        """
        print("List of available symbols:")
        for stock in self.stocks:
            print("symbol: %s, name: %s, file number: %s" %
                   (stock.stock_symbol, stock.stock_name, stock.file_num))

    def output_ascii(self, all_symbols, symbols):
        """
        Read all or specified symbols and write them to text
        files (each symbol in separate file)

        Parameters
        ----------
        all_symbols : bool
            When True, all symbols are processed

        symbols : list(str)
            List of symbols to process

        """
        for stock in self.stocks:
            if all_symbols or (stock.stock_symbol in symbols):
                stock.convert2ascii(self.options.input_dir, self.options.output_dir)
