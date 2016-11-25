#!/usr/bin/env python

import argparse
import glob
import os
import socket
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib/gen-py')
sys.path.insert(0, glob.glob('/home/akash/clones/thrift/lib/py/build/lib.*')[1])

from thrift import Thrift
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport

from tpc import Coordinator
from tpc.ttypes import (Order, Status)
import connection

partCons = []


def formConnection(participant):
    return connection.CoordinatorCon(participant)


class CoordinatorHandler():
    def writeFile(self, rFile):
        raise NotImplementedError

    def readFile(self, filename):
        raise NotImplementedError


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
        server = TServer.TSimpleServer(processor, tsocket, transport, protocol)

        # for participant in participants:
        #     partCons.append(formConnection(participant))

        host = socket.gethostname()
        host += '.cs.binghamton.edu' if host.startswith('remote') else ''
        print('Coordinator running on ' + host + ':' + args.port)

        server.serve()

    except Thrift.TException as tx:
        print('%s' % (tx.message))
