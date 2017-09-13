# Reading Metastock files

Last week I decided to check how my trading system performs while playing on different foreign indexes. First I had to download the test data. I found a web page offering the quotations I was interested in – luckily it wasn’t expensive.The problem was (of course it occurred after I had paid) that the data was available only in Metastock format. Of course I use my own software (just as every other programmer 😉 ) that helps me to play stocks and futures and I don’t have Metastock. So I decided I would give it a try and I wrote a tiny program that reads Metastock files and generates text files with quotes. I used my beloved Python. You can find the source [here](http://themech.net/downloads/ms_convert.py).

### Metastock format

The data was in Metastock 6.x format (XMASTER file was not present). Generally Metastock data consist of:

- MASTER/EMASTER file which holds general information about the tickers, stock names. This is an index file
- F{n}.DAT files which hold actual quotation data.
- Every F{n}.DAT file has a corresponding F{n}.DOP file which holds an information about the data columns available in the DAT file

The EMASTER file is essential because it holds the references to F{n}.DAT. So at the beginning we open EMASTER file and read what quotations are available and in which DAT files they are held. The following data describes each symbol:

  - file number
  - number of fields in one quotation
  - stock symbol
  - stock name
  - first date and last date

After reading the description we open the appropriate DAT file and read the quotations. Each row contain at least the date, open price, highest prices, lowest price and close price. Optionally there data contains volume and open positions data. The problem is that each data entry is a float number. To make is worse it is in Microsoft Binary floating point format :), while most of the programming languages use IEEE floating point format.

### Microsoft Binary Format floating point number

In the ’80’s Microsoft had a proprietary binary structure to handle floating point numbers. IEEE format (used nowadays) is more accurate and MBF format is generally not supported nowadays. Unfortunately Metastock still uses MBF so we have to handle it.
We have to convert the 4 bytes of the MS Binary Format to IEEE. After some googling I found a little piece of code in pure C and I’ve rewritten it using Python. The function is quite simple:

```python
def fmsbin2ieee(bytes):  
    """Convert an array of 4 bytes containing Microsoft Binary 
    floating point number to IEEE floating point format 
    (which is used by Python)"""  
    r = struct.unpack("i", bytes)  
    if not r:  
        return 0.0  
    man = long(struct.unpack('H', bytes[2:])[0])  
    if not man:  
        return 0.0  
    exp = (man & 0xff00) - 0x0200  
    man = man & 0x7f | (man < < 8) & 0x8000  
    man |= exp >> 1     
    bytes2 = bytes[:2]  
    bytes2 += chr(man & 255)  
    bytes2 += chr((man >> 8) & 255)  
    return struct.unpack("f", bytes2)[0]  
```

This little function returns a valid Python floating point number.

### Handling floats

As I said every data entry is a floating point number which represents different data types. Converting it to integer is straightforward. But converting it to a data or time is more tricky. The following functions show how to extract date and time from floating point numbers:

```python
def float2date(date):  
    """Convert a float to a string containig a date"""  
    date = int(date)  
    year = 1900 + (date / 10000)  
    month = (date % 10000) / 100  
    day = date % 100  
    return '%04d%02d%02d' % (year, month, day)  
  
def float2time(time):  
    """Convert a float to a string containig a time"""  
    time = int(time)  
    hour = time / 10000  
    min = (time % 10000) / 100  
    return '%02d%02d' % (hour, min)  
```

### About the tool

The tool I included should be run inside a directory containing Metastock quotations. It opens EMASTER file and lets you do the following things:

- list all the symbols
- extract to text files all the symbols
- extract to text files specified symbols

For those who don’t have python installed I included this tool as a Windows executable. Download it [here](http://themech.net/downloads/ms_convert.zip).

[mech](mech@themech.net), Source: http://themech.net/2008/08/reading-metastock-files/

P.S. There is another open source Metastock converter written by Rudi: https://github.com/rudimeier/atem. It’s written in C and the source is very well commented, so I recommend checking it out if you’re interested in reading MS files.

