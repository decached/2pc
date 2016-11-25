#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 akash <akothaw1@binghamton.edu>

import glob
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../lib/gen-py')
sys.path.insert(0, glob.glob('/home/akash/clones/thrift/lib/py/build/lib.*')[0])

from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol
from tpc import FileStore
from tpc import Coordinator


class Connection:
    def __init__(self, class_, host, port):
        transport = TSocket.TSocket(host, port)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        self.client = class_.Client(protocol)
        transport.open()
