#!/usr/bin/env python
from select import select
import sys
from threading import Thread


class CLIThread(Thread):
    '''A CLI thread for interactive input'''
    def __init__(self, ipc, hint):
        Thread.__init__(self)
        self.sock = ipc
        self.hint = hint

    def run(self):
        while True:
            sys.stdout.flush()
            rlist,_,_ = select([sys.stdin], [], [], 5)
            if rlist:
                input = sys.stdin.readline()
                input = input.strip()
                if len(input) > 0 and input[0] == "?":
                    print self.hint
                    continue

                self.sock.send(input)
                msg = self.sock.recv()
                if msg == "quit":
                    print "CLI quitting..."
                    break
        sys.stdout.flush()

