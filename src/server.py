#!/usr/bin/env python

import argparse
import glob
import os
import socket
import sys
import threading

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib/gen-py')
sys.path.insert(0, glob.glob('/home/akash/clones/thrift/lib/py/build/lib.*')[1])

from thrift import Thrift
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport

from tpc import Coordinator as CoordinatorRPC, FileStore as FileStoreRPC
from tpc.ttypes import RFile, Status, Vote
import connection

locks = {}
mLock = threading.Lock()

coordinator = {"host": "localhost", "port": "9090"}
myPID = None


def formConnection(host, port):
    return connection.Connection(CoordinatorRPC, host, port)


class FileStore():
    def __init__(self):
        self.fsDir = os.getcwd() + "/" + myPID + "/"
        if not os.path.isdir(self.fsDir):
            os.makedirs(self.fsDir)

    def writeFile(self, req):
        filePath = self.fsDir + req.rFile.filename + '.bak'
        with mLock:
            if req.rFile.filename not in locks:
                locks[req.rFile.filename] = threading.Lock()

        if locks[req.rFile.filename].locked():
            con = formConnection(coordinator['host'], coordinator['port'])
            voteNO = Vote(req.tID, myPID, Status.NO)
            con.client.vote(voteNO)

        locks[req.rFile.filename].acquire()
        with open(filePath, 'w') as wF:
            wF.write(req.rFile.content)
            con = formConnection(coordinator['host'], coordinator['port'])
            voteYES = Vote(req.tID, myPID, Status.YES)
            con.client.vote(voteYES)

    def readFile(self, filename):
        filePath = self.fsDir + filename
        with open(filePath, 'r') as oF:
            return RFile(filename=filename, content=oF.read())

    def commit(self, filename):
        filePath = self.fsDir + filename + '.bak'
        os.rename(filePath, self.fsDir + filename)
        locks[filename].release()

    def abort(self, filename):
        filePath = self.fsDir + filename + '.bak'
        os.remove(filePath)
        locks[filename].release()


class FileStoreHandler():
    def __init__(self):
        self.fs = FileStore()

    def ping(self):
        print 'ping'

    def writeFile(self, req):
        self.fs.writeFile(req)

    def readFile(self, filename):
        self.fs.readFile(filename)

    def commit(self, filename):
        self.fs.commit(filename)

    def abort(self, filename):
        self.fs.abort(filename)


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description='Durable File Service Participant.')
        parser.add_argument(dest='port', help='Port')
        parser.add_argument(dest='pid', help='Participant ID')
        args = parser.parse_args()

        myPID = args.pid

        handler = FileStoreHandler()
        processor = FileStoreRPC.Processor(handler)
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
