from sys import argv
from dataset import *
from regression import *

if __name__ == '__main__':
    if argv[1] == 'gen':
        gen_fips()
        data2000()
        data2004()
        data20082016()
    elif argv[1] == 'query':
        query(argv[2])
    elif argv[1] == 'dump':
        dump()
    elif argv[1] == 'census':
        census()
