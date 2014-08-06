#!python
import socket
import sys
import wifiplug
import re
import time

TCP_IP = ''
TCP_PORT = 221
BUFFER_SIZE = 128

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

conn, addr = s.accept()
sys.stdout.write("Connection address: %s:%s" % addr)
sys.stdout.flush()
try:
    while 1:
        data = conn.recv(BUFFER_SIZE)
        if not data: break
        # Presumably received a new plug
        sys.stdout.write(data)
        sys.stdout.flush()
        plug = wifiplug.Wifiplug(addr[0], addr[1], data)
        conn.send(wifiplug.SERVER_ACK)
        while 1:
            data = conn.recv(BUFFER_SIZE)
            if not data: break
            sys.stdout.write("Plug: %s" % plug.serial)
            sys.stdout.flush()
            time.sleep(10)
            conn.send(wifiplug.SERVER_TURN_ON)
            time.sleep(10)
            conn.send(wifiplug.SERVER_TURN_OFF)
except Exception as e:
    conn.close()
    raise e