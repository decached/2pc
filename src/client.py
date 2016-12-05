#!/usr/bin/env python

import argparse
import glob
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib/gen-py')
sys.path.insert(0, glob.glob('/home/akash/clones/thrift/lib/py/build/lib.*')[1])

from tpc import Coordinator
from tpc.ttypes import RFile
import connection


class FSClientHandler:
    def __init__(self, host, port):
        self.con = connection.Connection(Coordinator, host, port)

    def readFile(self, filename):
        rFile = self.con.client.readFile(filename)
        print rFile.content

    def writeFile(self, filename):
        content = ""
        with open(filename, 'r') as f:
            content = f.read()
            rFile = RFile(filename, content)
            print self.con.client.writeFile(rFile)


def process(args):
    fs = FSClientHandler(args.host, args.port)
    action = {'read': fs.readFile, 'write': fs.writeFile}
    action[args.operation](args.filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TPC Durable File Store Client.')
    parser.add_argument(dest='host', help='Host')
    parser.add_argument(dest='port', help='Port')
    parser.add_argument('--operation', dest='operation', help='Operation', required=True)
    parser.add_argument('--filename', dest='filename', help='Filename', required=True)
    process(parser.parse_args())
