"""
Helper methods
"""

import struct
import datetime


def fmsbin2ieee(b):
    """
    Convert an array of 4 bytes containing Microsoft Binary floating point
    number to IEEE floating point format (which is used by Python)

    Parameters
    ----------
    b : byte
        Microsoft Binary Fucking Floating Point

    Returns
    -------
    float
        Ordinary Floating Point

    """
    as_int = struct.unpack('i', b)
    if not as_int:
        return 0.0
    man = int(struct.unpack('H', b[2:])[0])
    if not man:
        return 0.0
    exp = (man & 0xff00) - 0x0200
    man = man & 0x7f | (man << 8) & 0x8000
    man |= exp >> 1

    bytes2 = bytes([b[0], b[1], (man & 255), ((man >> 8) & 255)])
    return struct.unpack('f', bytes2)[0]


def float2date(date):
    """
    Metastock stores date as a float number.
    Here we convert it to a python datetime.date object.

    Parameters
    ----------
    date : float
        YYYYMMDD format (either in int or float)

    Returns
    -------
    datetime.date

    """
    date = int(date)
    year = 1900 + int(date / 10000)
    month = int((date % 10000) / 100)
    day = date % 100
    return datetime.date(year, month, day)


def int2date(date):
    """
    Int to date use in XMASTER header format.
    Does same thing as float2date but sometimes date = 0 so tread as None

    Parameters
    ----------
    date : int
        YYYYMMDD format

    Returns
    -------
    datetime.date

    """
    return date > 0 and float2date(date) or None


def float2time(time):
    """
    Metastock stores date as a float number.
    Here we convert it to a python datetime.time object.

    Parameters
    ----------
    time : int
        HHMM format

    Returns
    -------
    datetime.time

    """
    time = int(time)
    hour = int(time / 10000)
    minute = int((time % 10000) / 100)
    return datetime.time(hour, minute)


def readstr(b):
    """
    Read string block from MetaStock data

    Parameters
    ----------
    b : byte

    Returns
    -------
    str

    """
    return b[:b.index(b'\0')].decode('ascii')


def readchar(b):
    """
    Read single character block from MetaStock data

    Parameters
    ----------
    b : byte

    Returns
    -------
    char

    """
    return struct.unpack('c', b)[0]


def readbyte(b):
    """
    Read 1-byte integer from MetaStock data

    Parameters
    ----------
    b : byte

    Returns
    -------
    byte

    """
    return struct.unpack('B', b)[0]


def readshort(b):
    """
    Read 2-byte integer from MetaStock data

    Parameters
    ----------
    b : byte

    Returns
    -------
    int

    """
    return struct.unpack('H', b)[0]


def readint(b):
    """
    Read 4-byte integer from MetaStock data. Usually found in date field.

    Parameters
    ----------
    b : byte

    Returns
    -------
    int

    """
    return struct.unpack('<I', b)[0]


def readfloat(b):
    """
    Read IEEE float from MetaStock data

    Parameters
    ----------
    b : byte

    Returns
    -------
    float

    """
    return struct.unpack('f', b)[0]
