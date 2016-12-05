#!/usr/bin/env python

import argparse
import glob
import os
import subprocess
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib/gen-py')
sys.path.insert(0, glob.glob('/home/akash/clones/thrift/lib/py/build/lib.*')[1])

from tpc import TestCoordinator, TestFileStore
import connection


def process(args):
    # for testCase in xrange(1, tests+1):
    pTest = connection.Connection(TestFileStore, 'localhost', '8082')
    cTest = connection.Connection(TestCoordinator, args.chost, args.cport)

    FNULL = open(os.devnull, 'w')

    # Test Case 1
    testCase = 1
    print '[Test:%d] Set Up' % (testCase)
    cTest.client.say('Case: ' + str(testCase))
    pTest.client.say('Case: ' + str(testCase))

    cTest.client.test(testCase)
    pTest.client.test(testCase)

    raw_input('> ')
    print '[Test:%d] Execute' % (testCase)

    ps = subprocess.Popen(
        ["./client", "localhost", "9090", "--operation", "write", "--filename", "Makefile"],
        env={"testCase": str(testCase)},
        stderr=FNULL
    )

    time.sleep(3)
    raw_input('> ')
    print '[Test:%d] Kill Participants' % (testCase)
    pTest.client.clean()

    time.sleep(3)
    print '[Test:%d] Restart Participants' % (testCase)
    pTest.client.test(testCase)

    raw_input('> ')
    ps = subprocess.Popen(
        ["./client", "localhost", "9090", "--operation", "read", "--filename", "Makefile"],
        env={"testCase": str(testCase)},
        stderr=FNULL
    )

    time.sleep(2)
    raw_input('> ')
    print '[Test:%d] Tear Down' % (testCase)
    cTest.client.clean()
    pTest.client.clean()

    # Test Case 2
    testCase = 2
    print '[Test:%d] Set Up' % (testCase)
    cTest.client.say('Case: ' + str(testCase))
    pTest.client.say('Case: ' + str(testCase))

    cTest.client.test(testCase)
    pTest.client.test(testCase)

    raw_input('> ')
    print '[Test:%d] Execute' % (testCase)

    ps1 = subprocess.Popen(
        ["./client", "localhost", "9090", "--operation", "write", "--filename", "Makefile"],
        env={"testCase": str(testCase)},
        stderr=FNULL
    )
    ps2 = subprocess.Popen(
        ["./client", "localhost", "9090", "--operation", "write", "--filename", "Makefile"],
        env={"testCase": str(testCase)},
        stderr=FNULL
    )

    time.sleep(3)
    raw_input('> ')
    print '[Test:%d] Tear Down' % (testCase)
    cTest.client.clean()
    pTest.client.clean()

    # Test Case 3.1
    raw_input('> ')
    testCase = 3
    print '[Test:%d.1] Set Up' % (testCase)
    cTest.client.say('Case: ' + str(testCase) + '.1')
    pTest.client.say('Case: ' + str(testCase) + '.1')

    cTest.client.test(testCase)
    pTest.client.test(testCase)

    raw_input('> ')
    print '[Test:%d.1] Execute' % (testCase)
    ps1 = subprocess.Popen(
        ["./client", "localhost", "9090", "--operation", "write", "--filename", "Makefile"],
        env={"testCase": str(testCase)},
        stderr=FNULL
    )

    time.sleep(2)
    raw_input('> ')
    print '[Test:%d.1] Coordinator Recovery' % (testCase)
    cTest.client.test(testCase)

    raw_input('> ')
    print '[Test:%d.1] Tear Down' % (testCase)
    cTest.client.clean()
    pTest.client.clean()

    # Test Case 3.2
    raw_input('> ')
    testCase = 3
    print '[Test:%d.2] Set Up' % (testCase)
    cTest.client.say('Case: ' + str(testCase) + '.2')
    pTest.client.say('Case: ' + str(testCase) + '.2')

    cTest.client.test(testCase)
    pTest.client.test(testCase)

    raw_input('> ')
    print '[Test:%d.2] Execute' % (testCase)
    ps1 = subprocess.Popen(
        ["./client", "localhost", "9090", "--operation", "write", "--filename", "Makefile"],
        env={"testCase": str(testCase)},
        stderr=FNULL
    )

    time.sleep(10)
    raw_input('> ')
    print '[Test:%d.2] Coordinator Recovery' % (testCase)
    cTest.client.test(testCase)

    raw_input('> ')
    print '[Test:%d.2] Tear Down' % (testCase)
    cTest.client.clean()
    pTest.client.clean()


    raw_input('> ')
    testCase = 4
    print '[Test:%d.1] Set Up' % (testCase)
    cTest.client.say('Case: ' + str(testCase) + '.1')
    pTest.client.say('Case: ' + str(testCase) + '.1')

    cTest.client.test(testCase)
    pTest.client.test(testCase)

    raw_input('> ')
    print '[Test:%d.1] Execute' % (testCase)
    ps1 = subprocess.Popen(
        ["./client", "localhost", "9090", "--operation", "write", "--filename", "Makefile"],
        env={"testCase": str(testCase)},
        stderr=FNULL
    )

    time.sleep(2)
    raw_input('> ')
    print '[Test:%d.1] Coordinator Recovery' % (testCase)
    cTest.client.test(testCase)

    raw_input('> ')
    print '[Test:%d.1] Tear Down' % (testCase)
    cTest.client.clean()
    pTest.client.clean()

    raw_input('> ')
    testCase = 5
    tCase = 4
    print '[Test:%d.2] Set Up' % (tCase)
    cTest.client.say('Case: ' + str(tCase) + '.2')
    pTest.client.say('Case: ' + str(tCase) + '.2')

    cTest.client.test(testCase)
    pTest.client.test(testCase)

    raw_input('> ')
    print '[Test:%d.2] Execute' % (tCase)
    ps1 = subprocess.Popen(
        ["./client", "localhost", "9090", "--operation", "write", "--filename", "Makefile"],
        env={"testCase": str(testCase)},
        stderr=FNULL
    )

    time.sleep(3)
    raw_input('> ')
    print '[Test:%d.2] Coordinator Recovery' % (tCase)
    cTest.client.test(testCase)

    raw_input('> ')
    print '[Test:%d.2] Tear Down' % (tCase)
    cTest.client.clean()
    pTest.client.clean()

    raw_input('> ')
    testCase = 6
    tCase = 5
    print '[Test:%d] Set Up' % (tCase)
    cTest.client.say('Case: ' + str(tCase))
    pTest.client.say('Case: ' + str(tCase))
    cTest.client.test(testCase)
    pTest.client.test(testCase)

    raw_input('> ')
    print '[Test:%d] Execute' % (tCase)
    ps1 = subprocess.Popen(
        ["./client", "localhost", "9090", "--operation", "write", "--filename", "Makefile"],
        env={"testCase": str(testCase)},
        stderr=FNULL
    )

    time.sleep(3)
    raw_input('> ')
    print '[Test:%d] Participant Recovery' % (tCase)
    pTest.client.start(testCase, 2)

    raw_input('> ')
    print '[Test:%d] Tear Down' % (tCase)
    cTest.client.clean()
    pTest.client.clean()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TPC Durable File Store Client.')
    parser.add_argument(dest='chost', help='Host')
    parser.add_argument(dest='cport', help='Port')
    parser.add_argument(dest='phost', help='Host')
    parser.add_argument(dest='pport', help='Port')
    process(parser.parse_args())
