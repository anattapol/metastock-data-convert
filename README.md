## Author: mech

Python utility that reads Metastock data files and save the quotations in
text files.
Full article is available here: http://themech.net/2008/08/reading-metastock-files/

## ms2csv.py
This script converts data from metastock format to CSV.

Input directory must contain metastock data EMASTER/XMASTER.

#### Usage

Listing the symbols in Metastock data:
```python
python ms2csv.py --list
```

Extracting all quotes:
```python
python ms2csv.py --all -d <path-to-ms-dir> -o <path-to-csv-dir>
```

More help:
```python
python ms2csv.py --help
```

## rdsupload.py
This script upload all CSV from input directory to MySQL server.
Input directory should contains substructure like the following diagram

```
📁 csv-dir
├── 📁 market1-dir
│   ├── 📃 symbol-1.TXT
│   ├── 📃 symbol-2.TXT
│   ...
│   └── 📃 symbol-n.TXT
...
```

#### Require Modules
- pymysql

#### Usage

Listing the symbols in Metastock data:
```python
python rdsupload.py -d <path-to-csv-dir>
```
