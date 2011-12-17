#!/usr/bin/env python
import sys
from server import ctrl
from server import room
import zmq
from cli import CLIThread

class Client(object):
    def __init__(self, name, rm, ctrl):
        self.name = name
        self.ctx = zmq.Context()

        self.receiver = self.ctx.socket(zmq.SUB)
        self.receiver.setsockopt(zmq.SUBSCRIBE, '')
        self.receiver.connect(rm)

        self.commander = self.ctx.socket(zmq.REQ)
        self.commander.connect(ctrl)

        self.commander.send("%s:LOGIN-new user"%self.name)
        self.commander.recv()

        self.channel = "ipc://test-%s"%name
        self.checker = self.ctx.socket(zmq.REP)
        self.checker.bind(self.channel)

        notif = self.ctx.socket(zmq.REQ)
        notif.connect(self.channel)
        self.cliThread = CLIThread(notif, 'Input message in format: <toUser>:<msg> or quit #')
        self.cliThread.start()

        self.poller = zmq.Poller()
        self.poller.register(self.receiver, zmq.POLLIN)
        self.poller.register(self.checker, zmq.POLLIN)

    def run(self):
        '''The run'''
        cont = True
        while cont:
            ret = self.poller.poll(500)
            if len(ret) > 0:
                for event in ret:
                    sock, type = event
                    if sock == self.receiver:
                        self.filter(self.receiver.recv())
                    else:
                        if sock == self.checker:
                            msg = sock.recv()
                            cont = self.input(msg)
                        else:
                            continue
        self.quit()

    def filter(self, msg):
        ''' check incoming message '''
        sys.stdout.flush()
        src, cont = msg.split(':')
        target, body = cont.split('-')
        if src == self.name:
            return 

        if (target == 'ALL'):
            print ">>> [broadcast][%s]:%s"%(src, body)
        else:
            if (target == self.name):
                print ">>> [private][%s]:%s"%(src, body)

    def input(self, input):
        '''check for user input, return True for continue'''
        if len(input.split(':')) == 2:
            target, body = input.split(':')
            self.commander.send("%s:%s-%s"%(self.name, target, body))
            self.commander.recv()
        else:
            input = input.strip()
            if len(input) > 0 and input[0] == 'q':
                self.checker.send('quit')
                #self.quit()
                return False
            else:
                print "~~~ input: %s ignored!"%input
        self.checker.send('ok')
        return True

    def quit(self):
        ''' quit processing'''
        self.commander.send("%s:LOGOUT-new"%self.name)
        self.commander.recv()
        self.cliThread.join()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print "Usage: %s <username>"%sys.argv[0]
        sys.exit(1)
    else:
        Client(sys.argv[1], room, ctrl).run()
