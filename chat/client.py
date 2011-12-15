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

        self.commander = self.ctx.socket(zmq.REQ)
        self.commander.connect(ctrl)

        self.commander.send("%s:LOGIN-new user"%self.name)
        self.poller = zmq.Poller()
        self.poller.register(self.receiver, zmq.POLLIN)
        self.poller.register(self.commander, zmq.POLLIN)

    def run(self):
        '''The run'''
        cont = True
        while cont:
            ret = self.poller.poll(500)
            if len(ret) > 0:
                for event in ret:
                    sock, type = event
                    if sock == self.commander:
                        msg = self.commander.recv()
                    else:
                        self.filter(self.receiver.recv())
            cont = self.input()
        self.quit()

    def filter(self, msg):
        ''' check incoming message '''
        src, cont = msg.split(':')
        target, body = cont.split('-')
        if (target == ALL):
            print "[%s]broadcast:%s"%(src, body)
        else:
            if (target == self.name):
                print "[%s]->:%s"%(src, body)

    def input(self):
        msg = raw_input('Input message in format: <toUser>:<msg> or quit:all #')
        target, body = msg.split(':')
        if target == 'quit':
            return False
        else:
            self.commander.send("%s:%s-%s"%(self.name, target, body))

    def quit(self):
        self.commander.send("%s:LOGOUT-new"%self.name)

if __name__ == '__main__':
    import sys
    Client(sys.argv[1], room, ctrl).run()

