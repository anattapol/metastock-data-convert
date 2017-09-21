import csv

def readfile(path, callback):
    with open('test.csv', 'rb') as f:
        reader = csv.reader(f, delimiter=',')
        for i, line in enumerate(reader):
            callback(i, line)
