#!/usr/bin/env python

import argparse
import glob
import os
import subprocess
import socket
import sys
import threading

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib/gen-py')
sys.path.insert(0, glob.glob('/home/akash/clones/thrift/lib/py/build/lib.*')[1])

from thrift import Thrift
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.transport import TSocket, TTransport

from tpc import TestCoordinator

coorFile = None
port = None


class TestCoordinatorHandler():
    def __init__(self):
        self.ps = None

    def threader(self, testCase):
        ps = subprocess.Popen(
            ["./coordinator", "49090", coorFile],
            env={"testCase": str(testCase)}
        )
        self.ps = ps

    def test(self, testCase):
        threading.Thread(target=self.threader, args=(testCase, )).start()

    def clean(self):
        self.ps.kill()

    def kill(self):
        os._exit(0)

    def say(self, word):
        print word

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description='Durable File Service Participant.')
        parser.add_argument(dest='port', help='Port')
        parser.add_argument(dest='filename', help='Input File')
        args = parser.parse_args()

        port = args.port
        coorFile = args.filename

        handler = TestCoordinatorHandler()
        processor = TestCoordinator.Processor(handler)
        tsocket = TSocket.TServerSocket('0.0.0.0', args.port)
        transport = TTransport.TBufferedTransportFactory()
        protocol = TBinaryProtocol.TBinaryProtocolFactory()
        server = TServer.TThreadedServer(processor, tsocket, transport, protocol)

        host = socket.gethostname()
        host += '.cs.binghamton.edu' if host.startswith('remote') else ''
        print('TestCoordinator server running on ' + host + ':' + args.port)
        server.serve()

    except Thrift.TException as tx:
        print('%s' % (tx.message))
