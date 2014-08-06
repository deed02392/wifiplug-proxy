#!python
import socket
import sys
import time
from threading import Thread

class Wifiplug():
    state = 'OFF'
    def go_off():
        self.state = 'OFF'
    def go_on():
        self.state = 'ON'
wifiplug = Wifiplug()

class WifiplugNetwork(Thread):
    def __init__(self, sock, wifiplug):
        Thread.__init__(self)
        self.daemon = True
        self.sock = sock

    def run(self): # Thread execution payload
        while 1:
            self.sock.send(wifiplug.state)
            time.sleep(3)

server = '127.0.0.1'
port = 9090

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((server, port))
print "Connected"
WifiplugNetwork(sock, wifiplug).start()

while 1:
    cmd = raw_input("> ")
    exec(cmd)