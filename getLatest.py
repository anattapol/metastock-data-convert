import difflib


def show(new):
    print(new)


def get_latest(func, oldFile, newFile):
    d = difflib.Differ()
    with open(oldFile, 'r') as f1, open(newFile, 'r') as f2:
        differ = difflib.Differ()
        new = []
        for line in differ.compare(f1.read().splitlines() ,f2.read().splitlines()):
            if line.startswith('+ '):
                new.append(line[2:])
    func(new)


def main():
    get_latest(show, 'Test.txt.old', 'Test.txt')


if __name__ == '__main__':
    main()
