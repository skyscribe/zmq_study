#!/usr/bin/env python
import zmq

room = "tcp://127.0.0.1:6000"
ctrl = "tcp://127.0.0.1:6001"

class Server(object):
    def __init__(self, rm, ctrl):
        self.room = rm
        self.ctx = zmq.Context()
        self.pub = self.ctx.socket(zmq.PUB)
        self.pub.bind(rm)

        self.ctrl = self.ctx.socket(zmq.SUB)
        self.ctrl.connect(ctrl)

    def run(self):
        '''run the service now'''
        #Receive messages from ctrl 
        msg = self.ctrl.recv()
        src, cont = msg.split(':')
        type, _ = cont.split('-')
        if type == 'LOGIN':
            self.login(src)
        else:
            if type == 'LOGOUT':
                self.logout(src)
            else:
                self.publish(msg)
    
    def login(self, usr):
        '''login process'''
        self.pub.send("%s -> ALL: User %s joined this room!"%(usr, usr))

    def logout(self, usr):
        '''logout '''
        self.pub.send("%s -> ALL: User %s leaved this room!"%(usr, usr))

    def publish(self, msg):
        '''publish the normal messages'''
        #mssage like   BOB: Alice -  How are you?  => BOB -> Alice: How are you
        src, cont = msg.split(':')
        target, body = cont.split('-')
        self.pub.send("%s -> %s: %s" % (src, target, body)) 

if __name__ == '__main__':
    Server(room, ctrl).run()

