#!/usr/bin/env python
import zmq
context = zmq.Context()
sock = context.socket(zmq.REQ)
sock.connect("tcp://127.0.0.1:8122")

while True:
    cont = raw_input("")
    sock.send(cont)

    msg = sock.recv()
    print msg
