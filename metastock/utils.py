"""
Helper methods
"""

import struct
import datetime
import traceback


def fmsbin2ieee(b):
    """
    Convert an array of 4 bytes containing Microsoft Binary floating point
    number to IEEE floating point format (which is used by Python)
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
    """
    date = int(date)
    year = 1900 + int(date / 10000)
    month = int((date % 10000) / 100)
    day = date % 100
    return datetime.date(year, month, day)


def int2date(date):
    return date > 0 and float2date(date) or None


def float2time(time):
    """
    Metastock stores date as a float number.
    Here we convert it to a python datetime.time object.
    """
    time = int(time)
    hour = int(time / 10000)
    minute = int((time % 10000) / 100)
    return datetime.time(hour, minute)

def readstr(b):
    return b.decode('ascii').split('\x00', 1)[0]

def readchar(b):
    return struct.unpack('c', b)[0]

def readbyte(b):
    return struct.unpack('B', b)[0]

def readshort(b):
    return struct.unpack('H', b)[0]

def readint(b):
    return struct.unpack('<I', b)[0]

def readfloat(b):
    return struct.unpack('f', b)[0]
