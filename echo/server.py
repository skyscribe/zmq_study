#!/usr/bin/env python

import zmq
context = zmq.Context()
sock = context.socket(zmq.REP)
sock.bind("tcp://127.0.0.1:8122")

while True:
    msg = sock.recv()
    print "[Server]:got %s"%msg
    sock.send(msg)

