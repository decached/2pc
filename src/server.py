#!/usr/bin/env python

import argparse
import glob
import json
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
from tpc.ttypes import RFile, Status
import connection

locks = {}
mLock = threading.Lock()
wLock = threading.Lock()

coordinator = {"host": "localhost", "port": "9090"}
myPID = None


def formConnection(host, port):
    return connection.Connection(CoordinatorRPC, host, port)


def recover():
    fs = FileStore()
    wal = fs._getLog()
    for tID, request in wal["requests"].items():
        if request["action"] == Action.DONE:
            continue
        if fs.getDecision(tID):
            fs.commit(request["name"], str(tID), recover=True)
        else:
            fs.abort(request["name"], str(tID), recover=True)


class Action:
    PENDING = 0
    DONE = 1


class FileStore():
    def __init__(self):
        self.fsDir = os.getcwd() + "/" + myPID + "/"
        self.logPath = self.fsDir + 'flog.json'

    def _getLog(self):
        """
        WARN: Should only be called `with wLock:`
        """
        with open(self.logPath, 'r') as rF:
            return json.loads(rF.read())

    def _setLog(self, wal):
        """
        WARN: Should only be called `with wLock:`
        """
        with open(self.logPath, 'w') as wF:
            wF.write(json.dumps(wal))

    def _logInit(self, filename, tID):
        with wLock:
            wal = self._getLog()
            wal["requests"] = {}
            wal["requests"][tID] = {"name": filename, "status": Status.NO, "action": Action.PENDING}
            self._setLog(wal)

    def writeFile(self, tID, rFile):
        self._logInit(rFile.filename, tID)
        filePath = self.fsDir + rFile.filename + '.bak'
        with mLock:
            if rFile.filename not in locks:
                locks[rFile.filename] = threading.Lock()

        if locks[rFile.filename].locked():
            return

        locks[rFile.filename].acquire()
        with open(filePath, 'w') as wF:
            wF.write(rFile.content)
            with wLock:
                wal = self._getLog()
                wal["requests"][str(tID)]["status"] = Status.YES
                self._setLog(wal)

        # if myPID == "p2":
        #     os._exit(0)

    def readFile(self, filename):
        filePath = self.fsDir + filename
        with open(filePath, 'r') as oF:
            return RFile(filename=filename, content=oF.read())

    def canCommit(self, tID):
        with wLock:
            wal = self._getLog()
            return wal["requests"][str(tID)]["status"]

    def doCommit(self, tID, recover=False):
        filename = None
        with wLock:
            wal = self._getLog()
            wal["requests"][str(tID)]["action"] = Action.DONE
            filename = wal["requests"][str(tID)]["name"]
            self._setLog(wal)
        filePath = self.fsDir + filename + '.bak'
        os.rename(filePath, self.fsDir + filename)
        if not recover: locks[filename].release()

    def doAbort(self, tID, recover=False):
        filename = None
        with wLock:
            wal = self._getLog()
            wal["requests"][str(tID)]["action"] = Action.DONE
            filename = wal["requests"][str(tID)]["name"]
            self._setLog(wal)
        filePath = self.fsDir + filename + '.bak'
        os.remove(filePath)
        if not recover: locks[filename].release()

    def getDecision(self, tID):
        con = formConnection(coordinator['host'], coordinator['port'])
        return con.client.getDecision(int(tID))


class FileStoreHandler():
    def __init__(self):
        self.fs = FileStore()

    def ping(self):
        print 'ping'

    def writeFile(self, tID, rFile):
        self.fs.writeFile(tID, rFile)

    def readFile(self, filename):
        self.fs.readFile(filename)

    def canCommit(self, tID):
        return self.fs.canCommit(tID)

    def doCommit(self, tID):
        self.fs.doCommit(tID)

    def doAbort(self, tID):
        self.fs.doAbort(tID)


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description='Durable File Service Participant.')
        parser.add_argument(dest='port', help='Port')
        parser.add_argument(dest='pid', help='Participant ID')
        args = parser.parse_args()

        myPID = args.pid
        fsDir = os.getcwd() + '/' + myPID + '/'
        if not os.path.isdir(fsDir):
            os.makedirs(fsDir)

        logPath = fsDir + 'flog.json'
        if not os.path.exists(logPath):
            with open(logPath, 'w') as wF:
                wal = {"lastID": "0", "requests": {}}
                wF.write(json.dumps(wal))

        # recover()

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
