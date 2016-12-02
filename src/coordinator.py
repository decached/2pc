#!/usr/bin/env python

import argparse
import glob
import json
import os
import random
import socket
import sys
import threading

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib/gen-py')
sys.path.insert(0, glob.glob('/home/akash/clones/thrift/lib/py/build/lib.*')[1])

from thrift import Thrift
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport

from tpc import Coordinator, FileStore
from tpc.ttypes import Request
import connection

participants = {}
wLock = threading.Lock()


def formConnection(host, port):
    return connection.Connection(FileStore, host, port)


class CoordinatorHandler():
    def __init__(self):
        self.coorDir = os.getcwd() + '/coor/'
        if not os.path.isdir(self.coorDir):
            os.makedirs(self.coorDir)

    def _writeLocalFile(self, rFile):
        filePath = self.coorDir + rFile.filename
        with open(filePath, 'w') as wF:
            wF.write(rFile.content)

    def _getLog(self):
        """
        WARN: Should only be called `with wLock:`
        """
        with open('tlog.json', 'r') as rF:
            return json.loads(rF.read())

    def _setLog(self, wal):
        """
        WARN: Should only be called `with wLock:`
        """
        with open('tlog.json', 'w') as wF:
            wF.write(json.dumps(wal))

    def _logInit(self, rFile):
        wal = None
        with wLock:
            self._writeLocalFile(rFile)
            wal = self._getLog()
            newTID = str(int(wal["lastID"]) + 1)
            wal["lastID"] = newTID
            wal["requests"][newTID] = {"name": rFile.filename, "status": {}}
            self._setLog(wal)
            return int(newTID)

    def ping(self):
        print 'ping()'

    def writeFile(self, rFile):
        global participants
        tID = self._logInit(rFile)

        for pid, location in participants.items():
            partCon = formConnection(*location)
            req = Request(tID, rFile)
            partCon.client.writeFile(req)

    def readFile(self, filename):
        global participants
        participant = participants.values()[random.randrange(0, len(participants))]
        con = formConnection(*participant)
        return con.client.readFile(filename)

    def vote(self, v):
        votes = None
        with wLock:
            wal = self._getLog()
            wal["requests"][str(v.tID)]["status"][v.pID] = v.status
            self._setLog(wal)

            votes = wal["requests"][str(v.tID)]["status"].values()
            filename = wal["requests"][str(v.tID)]["name"]
            if votes and not len(votes) == len(participants):
                return

        if all(votes):
            for pid, location in participants.items():
                partCon = formConnection(*location)
                partCon.client.commit(filename)
        else:
            for pid, location in participants.items():
                partCon = formConnection(*location)
                partCon.client.abort(filename)


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description='Durable File Service Coordinator.')
        parser.add_argument(dest='port', help='Port')
        parser.add_argument(dest='filename', help='Participants Details')
        args = parser.parse_args()

        handler = CoordinatorHandler()
        processor = Coordinator.Processor(handler)
        tsocket = TSocket.TServerSocket('0.0.0.0', args.port)
        transport = TTransport.TBufferedTransportFactory()
        protocol = TBinaryProtocol.TBinaryProtocolFactory()
        server = TServer.TThreadedServer(processor, tsocket, transport, protocol)

        if not os.path.exists('tlog.json'):
            with open('tlog.json', 'w') as wF:
                wal = {"lastID": "0", "requests": {}}
                wF.write(json.dumps(wal))

        with open(args.filename, 'r') as f:
            for line in f.readlines():
                pid, ip, port = line.split()
                participants[pid] = (ip, port)

        host = socket.gethostname()
        host += '.cs.binghamton.edu' if host.startswith('remote') else ''
        print('Coordinator running on ' + host + ':' + args.port)

        server.serve()

    except Thrift.TException as tx:
        print('%s' % (tx.message))
