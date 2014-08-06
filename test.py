#!python
import re
import inspect
import pprint

MESSAGE_PREFIX = 'BBBB'
MESSAGE_SUFFIX = 'EEEE' + "\r\n"
SERVER_TURN_ON = MESSAGE_PREFIX + '4,1' + MESSAGE_SUFFIX
SERVER_TURN_OFF = MESSAGE_PREFIX + '4,0' + MESSAGE_SUFFIX
SERVER_ACK = MESSAGE_PREFIX + '+OK' + MESSAGE_SUFFIX
CLIENT_HELLO = r'' + MESSAGE_PREFIX + '1,([A-Za-z0-9]{12}),01,02' + MESSAGE_SUFFIX
CLIENT_STATUS_OFF = MESSAGE_PREFIX + '3,0' + MESSAGE_SUFFIX
CLIENT_STATUS_ON = MESSAGE_PREFIX + '3,1' + MESSAGE_SUFFIX

class Wifiplug():
    def __init__(self, addr, port, data):
        self.state = 'OFF'
        self.addr = addr
        self.port = port
        self.serial = self.decode(data)
    def decode(self, message):
        if(message[0:len(MESSAGE_PREFIX)] == MESSAGE_PREFIX and message[-4:] == MESSAGE_SUFFIX):
            pprint.pprint(message)
            type = message[4]
            if type == 1:
                try:
                    match = re.match(CLIENT_HELLO, message)
                    return match.group(1)
                except Exception as e:
                    pprint.pprint(e)
                    return False
            elif type == 3:
                self.state = 'OFF' if message[6] == '0' else 'ON'
                return self.state

message = "BBBB1,002509030acb,01,02EEEE\r\n"
print message[0:len(MESSAGE_PREFIX)]
print MESSAGE_PREFIX
print message[-4:]
print MESSAGE_SUFFIX

if(message[0:len(MESSAGE_PREFIX)] == MESSAGE_PREFIX and message[-len(MESSAGE_SUFFIX.rstrip()):] == MESSAGE_SUFFIX.rstrip()):
            type = message[4]
            if type == '1':
                try:
                    match = re.match(CLIENT_HELLO.rstrip(), message)
#                    return match.group(1)
                    print match.group(1)
                except Exception as e:
                    print e
else:
  print "didnt"
