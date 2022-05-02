from sys import argv
from ntpath import exists, getsize, realpath
from shutil import copy2

def byteswap(file):

    copy = realpath(file) + '.bak'
    existing = exists(copy)
    while existing:
        copy += '.bak'
        existing = exists(copy)
    copy2(file, copy)

    #input file, output file, file size
    f = open(file, "r+b")
    fsize = getsize(file)

    #check that file size is divisible by 4
    if fsize % 4 != 0:
        print("Invalid file size!")

    #read 4 bytes at a time from the file, then rewrite the 4 bytes in reverse
    else:
        x = 0
        while x < fsize:
            f.seek(x)
            data = [int.from_bytes(f.read(1), "big"), int.from_bytes(f.read(1), "big"), int.from_bytes(f.read(1), "big"), int.from_bytes(f.read(1), "big")]
            data = data[::-1]
            f.seek(x)
            f.write(bytes(data))
            x += 4

    f.close()
    if endian(file) == 'little':
        print("\"" + file + "\" is now in Little Endian format.")
    if endian(file) == 'big':
        print("\"" + file + "\" is now in Big Endian format.")

def endian(file):
    result = ""
    with open(file, 'rb') as f:
        f.seek(8)
        sample=f.read(4)
        if sample == b'ADLE':
            result = 'little'
        if sample == b'ELDA':
            result = 'big'
    return result

def run():
    if len(argv) == 1:
        file=input("Enter the path to the file you want to byte swap:")
    if len(argv) == 2:
        file=argv[1]

    if exists(file):

        if endian(file) == 'big' or endian(file) == 'little':
            byteswap(file)
        else:
            print("\"" + file + "\" is invalid.")

    else:
        print("\"" + file + "\" does not exist.")


## MAIN ##
if len(argv) == 2:
    run()

elif len(argv) > 2:
    print("Too many arguments.")

else:
    if argv[0] == 'byteswap.py':
        print("Usage: python byteswap.py <PATH-TO-FILE>")
    else:
        run()