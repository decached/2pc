#!/usr/bin/env python

import argparse
import glob
import json
import os
import random
import socket
import sys
import threading
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib/gen-py')
sys.path.insert(0, glob.glob('/home/akash/clones/thrift/lib/py/build/lib.*')[1])

from thrift import Thrift
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport

from tpc import Coordinator as CoordinatorRPC, FileStore as FileStoreRPC
from tpc.ttypes import Status
import connection

participants = {}
wLock = threading.Lock()


def formConnection(host, port):
    return connection.Connection(FileStoreRPC, host, port)

CASE = int(os.getenv('testCase', 0))


class MODE:
    DEBUG = True
    INFO = True
    TEST = True


class Action:
    PENDING = 0
    DONE = 1


def recover():
    fs = Coordinator()
    wal = fs._getLog()
    for tID, request in wal["requests"].items():
        tID = int(tID)
        filename = request["name"]
        if request["action"] == Action.PENDING:
            if MODE.INFO: print '[T:%d] "%s" [Recover?]' % (tID, filename)
            votes = request["votes"]
            if not len(votes) == len(participants):
                for pid, location in participants.items():
                    partCon = formConnection(*location)
                    votes[pid] = partCon.client.canCommit(tID, recover=True)

            fs._logVotes(tID, votes)

            if all(votes.values()):
                if MODE.INFO: print '[T:%d] "%s" [Commit?]: %r' % (tID, filename, bool(Status.YES))
                fs._logStatus(tID, Status.YES)
                for pid, location in participants.items():
                    partCon = formConnection(*location)
                    partCon.client.doCommit(tID)
            else:
                if MODE.INFO: print '[T:%d] "%s" [Commit?]: %r' % (tID, filename, bool(Status.NO))
                fs._logStatus(tID, Status.NO)
                for pid, location in participants.items():
                    if votes[pid] == Status.YES:
                        partCon = formConnection(*location)
                        partCon.client.doAbort(tID)

            fs._logAction(tID, Action.DONE)


class Coordinator():
    def __init__(self):
        self.coorDir = os.getcwd() + '/coor/'
        self.logPath = self.coorDir + 'tlog.json'

    def _writeLocalFile(self, rFile):
        filePath = self.coorDir + rFile.filename
        with open(filePath, 'w') as wF:
            wF.write(rFile.content)

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

    def _logInit(self, rFile):
        wal = None
        with wLock:
            self._writeLocalFile(rFile)
            wal = self._getLog()
            newTID = str(int(wal["lastID"]) + 1)
            wal["lastID"] = newTID
            wal["requests"][newTID] = {"name": rFile.filename, "action": Action.PENDING, "status": Status.NO, "votes": {}}
            self._setLog(wal)
            return int(newTID)

    def _logStatus(self, tID, status):
        with wLock:
            wal = self._getLog()
            wal["requests"][str(tID)]["status"] = status
            self._setLog(wal)

    def _logAction(self, tID, action):
        with wLock:
            wal = self._getLog()
            wal["requests"][str(tID)]["action"] = action
            self._setLog(wal)

    def _logVotes(self, tID, votes):
        with wLock:
            wal = self._getLog()
            wal["requests"][str(tID)]["votes"] = votes
            self._setLog(wal)

    def writeFile(self, rFile):
        global participants
        tID = self._logInit(rFile)
        if MODE.INFO: print '[T:%d] "%s" [Write?]: Request' % (tID, rFile.filename)

        for pid, location in participants.items():
            partCon = formConnection(*location)
            partCon.client.writeFile(tID, rFile)

        time.sleep(2)
        # if MODE.TEST and CASE == 2: time.sleep(5)
        if MODE.TEST and CASE == 3: os._exit(0)

        votes = {}
        for pid, location in participants.items():
            partCon = formConnection(*location)
            votes[pid] = partCon.client.canCommit(tID, recover=False)

        if MODE.TEST and CASE == 4: del votes["p2"]

        self._logVotes(tID, votes)

        if MODE.TEST and (CASE == 4 or CASE == 5): os._exit(0)

        if votes and not len(votes) == len(participants):
            for pid, location in participants.items():
                if pid in votes and votes[pid] == Status.YES:
                    partCon = formConnection(*location)
                    partCon.client.doAbort(tID)
            return Status.NO

        status = None
        if all(votes.values()):
            status = Status.YES
            for pid, location in participants.items():
                partCon = formConnection(*location)
                partCon.client.doCommit(tID)
        else:
            status = Status.NO
            for pid, location in participants.items():
                if votes[pid] == Status.YES:
                    partCon = formConnection(*location)
                    partCon.client.doAbort(tID)

        self._logAction(tID, Action.DONE)
        if MODE.INFO: print '[T:%d] "%s" [Commit?]: %r' % (tID, rFile.filename, bool(status))
        self._logStatus(tID, status)
        return status

    def readFile(self, filename):
        global participants
        participant = participants.values()[random.randrange(0, len(participants))]
        con = formConnection(*participant)
        return con.client.readFile(filename)

    def getDecision(self, tID):
        votes = []
        with wLock:
            wal = self._getLog()
            votes = wal["requests"][str(tID)]["votes"].values()
            status = wal["requests"][str(tID)]["status"]
            filename = wal["requests"][str(tID)]["name"]
            if votes and not len(votes) == len(participants):
                if MODE.INFO: print '[T:%d] "%s" [Get-Decision?]: %r' % (tID, filename, bool(Status.NO))
                return Status.NO
            if MODE.INFO: print '[T:%d] "%s" [Get-Decision?]: %r' % (tID, filename, bool(status))
            return status


class CoordinatorHandler():
    def __init__(self):
        self.coor = Coordinator()

    def ping(self):
        print 'ping()'

    def writeFile(self, rFile):
        return self.coor.writeFile(rFile)

    def readFile(self, filename):
        return self.coor.readFile(filename)

    def getDecision(self, tID):
        return self.coor.getDecision(tID)


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description='Durable File Service Coordinator.')
        parser.add_argument(dest='port', help='Port')
        parser.add_argument(dest='filename', help='Participants Details')
        args = parser.parse_args()

        handler = CoordinatorHandler()
        processor = CoordinatorRPC.Processor(handler)
        tsocket = TSocket.TServerSocket('0.0.0.0', args.port)
        transport = TTransport.TBufferedTransportFactory()
        protocol = TBinaryProtocol.TBinaryProtocolFactory()
        server = TServer.TThreadedServer(processor, tsocket, transport, protocol)

        coorDir = os.getcwd() + '/coor/'
        if not os.path.isdir(coorDir):
            os.makedirs(coorDir)

        logPath = coorDir + 'tlog.json'
        if not os.path.exists(logPath):
            with open(logPath, 'w') as wF:
                wal = {"lastID": "0", "requests": {}}
                wF.write(json.dumps(wal))

        with open(args.filename, 'r') as f:
            for line in f.readlines():
                pid, ip, port = line.split()
                participants[pid] = (ip, port)

        recover()

        host = socket.gethostname()
        host += '.cs.binghamton.edu' if host.startswith('remote') else ''
        print('Coordinator running on ' + host + ':' + args.port)

        server.serve()

    except Thrift.TException as tx:
        print('%s' % (tx.message))
