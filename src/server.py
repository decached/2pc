#!/usr/bin/env python

import argparse
import glob
import os
import socket
import sys
import threading

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib/gen-py')
sys.path.insert(0, glob.glob('/home/akash/clones/thrift/lib/py/build/lib.*')[1])

from tpc import FileStore
from tpc.ttypes import RFile, Status

from thrift import Thrift
from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

# FIXME: Remove FS from Command line
fs = ""

locks = {}
mLock = threading.Lock()


class FileStoreHandler():
    def __init__(self):
        self.fsDir = os.getcwd() + fs
        if not os.path.isdir(self.fsDir):
            os.makedirs(self.fsDir)

    def ping(self):
        print 'ping'

    def writeFile(self, rFile):
        filePath = self.fsDir + rFile.filename + '.bak'

        lock = None
        with mLock:
            if filePath in locks:
                lock = locks[filePath]
            else:
                lock = threading.Lock()
                locks[filePath] = lock

        if lock.locked():
            return Status.NO
        with lock:
            with open(filePath, 'w') as wF:
                wF.write(rFile.content)
                return Status.YES

    def readFile(self, filename):
        filePath = self.fsDir + filename

        with open(filePath, 'r') as oF:
            return RFile(filename=filename, content=oF.read())

    def commit(self, filename):
        filePath = self.fsDir + filename + '.bak'
        os.rename(filePath, self.fsDir + filename)

    def abort(self, filename):
        filePath = self.fsDir + filename + '.bak'
        os.remove(filePath)


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description='Durable File Service Participant.')
        parser.add_argument(dest='port', help='Port')
        parser.add_argument(dest='fs', help='RemoveMe')
        args = parser.parse_args()

        fs = '/' + args.fs + '/'

        handler = FileStoreHandler()
        processor = FileStore.Processor(handler)
        tsocket = TSocket.TServerSocket('0.0.0.0', args.port)
        transport = TTransport.TBufferedTransportFactory()
        protocol = TBinaryProtocol.TBinaryProtocolFactory()
        server = TServer.TThreadedServer(processor, tsocket, transport, protocol)

        host = socket.gethostname()
        host += '.cs.binghamton.edu' if host.startswith('remote') else ''
        print('FileStore server running on ' + host + ':' + args.port)
        server.serve()

    except Thrift.TException as tx:
        print('%s' % (tx.message))
