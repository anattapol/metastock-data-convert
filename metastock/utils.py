"""
Helper methods
"""

import struct
import datetime


def fmsbin2ieee(in_bytes):
    """
    Convert an array of 4 bytes containing Microsoft Binary floating point
    number to IEEE floating point format (which is used by Python)
    """
    as_int = struct.unpack('i', in_bytes)
    if not as_int:
        return 0.0
    man = int(struct.unpack('H', in_bytes[2:])[0])
    if not man:
        return 0.0
    exp = (man & 0xff00) - 0x0200
    man = man & 0x7f | (man << 8) & 0x8000
    man |= exp >> 1

    bytes2 = bytes([in_bytes[0], in_bytes[1], (man & 255), ((man >> 8) & 255)])
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
    return float2date(date)


def float2time(time):
    """
    Metastock stores date as a float number.
    Here we convert it to a python datetime.time object.
    """
    time = int(time)
    hour = int(time / 10000)
    minute = int((time % 10000) / 100)
    return datetime.time(hour, minute)
