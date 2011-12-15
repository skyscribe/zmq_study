#!/usr/bin/env python
import zmq
from server import room
from server import ctrl

class Client(object):
    def __init__(self, name, rm, ctrl):
        self.name = name
        self.ctx = zmq.Context()
        self.receiver = self.ctx.socket(zmq.SUB)
        self.receiver.connect(rm)

        self.commander = self.ctx.socket(zmq.PUB)
        self.commander.bind(ctrl)

        self.commander.send("%s:LOGIN"%self.name)

    def run(self):
        '''The run'''
        pass

    def quit(self):
        self.commander.send("%s:LOGOUT"%self.name)

if __name__ == '__main__':
    import sys
    Client(sys.argv[1], server.room, server.ctrl).run()

