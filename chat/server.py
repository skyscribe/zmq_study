#!/usr/bin/env python
import zmq

#For broadcasts
room = "tcp://127.0.0.1:6000"
#For join/leave controls
ctrl = "tcp://127.0.0.1:6001"

class Server(object):
    def __init__(self, rm, ctrl):
        self.ctx = zmq.Context()
        self.pub = self.ctx.socket(zmq.PUB)
        self.pub.bind(rm)

        self.ctrl = self.ctx.socket(zmq.REP)
        self.ctrl.bind(ctrl)

    def run(self):
        '''run the service now'''
        while True:
            #Receive messages from ctrl 
            msg = self.ctrl.recv()
            print "received msg: %s" %msg
            self.ctrl.send("okay")

            src, cont = msg.split(':')
            target, _ = cont.split('-')
            if target == 'LOGIN':
                self.login(src)
            else:
                if target == 'LOGOUT':
                    self.logout(src)
                else:
                    self.pub.send(msg)
    
    def login(self, usr):
        '''login process'''
        self.pub.send("%s:ALL-User %s joined this room!"%(usr, usr))

    def logout(self, usr):
        '''logout '''
        self.pub.send("%s:ALL-User %s leaved this room!"%(usr, usr))

if __name__ == '__main__':
    Server(room, ctrl).run()

