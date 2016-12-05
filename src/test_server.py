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

from tpc import TestFileStore


class TestFileStoreHandler():
    def __init__(self):
        self.ps = []
        self.lock = threading.Lock()

    def threader(self, testCase, pID):
        ps = subprocess.Popen(
            ["./server", "1909" + str(pID), "p" + str(pID)],
            env={"testCase": str(testCase)}
        )
        with self.lock:
            self.ps.append(ps)

    def test(self, testCase):
        for pid in xrange(1, 3):
            t = threading.Thread(target=self.threader, args=(testCase, pid, ))
            t.start()

    def start(self, testCase, pid):
        t = threading.Thread(target=self.threader, args=(testCase, pid, ))
        t.start()

    def clean(self):
        for ps in self.ps:
            ps.kill()
        self.ps = []

    def kill(self):
        os._exit(0)

    def say(self, word):
        print word

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser(description='Durable File Service Participant.')
        parser.add_argument(dest='port', help='Port')
        args = parser.parse_args()

        handler = TestFileStoreHandler()
        processor = TestFileStore.Processor(handler)
        tsocket = TSocket.TServerSocket('0.0.0.0', args.port)
        transport = TTransport.TBufferedTransportFactory()
        protocol = TBinaryProtocol.TBinaryProtocolFactory()
        server = TServer.TThreadedServer(processor, tsocket, transport, protocol)

        host = socket.gethostname()
        host += '.cs.binghamton.edu' if host.startswith('remote') else ''
        print('TestFileStore server running on ' + host + ':' + args.port)
        server.serve()

    except Thrift.TException as tx:
        print('%s' % (tx.message))
