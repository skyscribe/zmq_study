#!/usr/bin/env python
import zmq
from cli import CLIThread

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

        ipc = "ipc://server-internal"
        self.cliSock = self.ctx.socket(zmq.REP)
        self.cliSock.bind(ipc)
        notif = self.ctx.socket(zmq.REQ)
        notif.connect(ipc)
        self.cliThread = CLIThread(notif, 'Input q to quit, ? for help')
        self.cliThread.start()

        self.poller = zmq.Poller()
        self.poller.register(self.cliSock, zmq.POLLIN)
        self.poller.register(self.ctrl, zmq.POLLIN)

        

    def run(self):
        '''run the service now'''
        cont = True
        while cont:
            ret = self.poller.poll(200)
            for event in ret:
                sock, _ = event
                if sock == self.ctrl:
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
                else:
                    assert sock == self.cliSock
                    msg = sock.recv().strip()
                    if len(msg) > 0 and msg[0] == 'q':
                        cont = False
                        sock.send('quit')
                        break
                    else:
                        sock.send('fine')
        self.quit()
    
    def login(self, usr):
        '''login process'''
        self.pub.send("%s:ALL-User %s joined this room!"%(usr, usr))

    def logout(self, usr):
        '''logout '''
        self.pub.send("%s:ALL-User %s leaved this room!"%(usr, usr))

    def quit(self):
        self.cliThread.join()

if __name__ == '__main__':
    Server(room, ctrl).run()

