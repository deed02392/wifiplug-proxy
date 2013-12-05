#!python
import socket
import sys

TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 20

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

conn, addr = s.accept()
sys.stdout.write("Connection address: %s:%s" % addr)
sys.stdout.flush()
while 1:
    data = conn.recv(BUFFER_SIZE)
    if not data: break
    sys.stdout.write("recv: %s" % data)
    sys.stdout.flush()
    conn.send(data)  # echo
conn.close()