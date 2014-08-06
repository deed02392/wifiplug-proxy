#!python
import re

MESSAGE_PREFIX = 'BBBB'
MESSAGE_SUFFIX = 'EEEE'
MSG_TYPES = {
    '+': 'MSG_SERVER_GENERIC',
    '1': 'MSG_CLIENT_REGISTRATION',
    '3': 'MSG_CLIENT_STATUS',
    '4': 'MSG_SERVER_COMMAND',
}
SERVER_CMDS = {
    '0': 'turn off',
    '1': 'turn on',
}
CLIENT_HELLO = r'' + MESSAGE_PREFIX + '1,([A-Fa-f0-9]{12}),01,02' + MESSAGE_SUFFIX
CLIENT_STATES = {
    '0': 'plug off',
    '1': 'plug on',
}

## Represents a packet in the WifiPlug protocol
#
#  Provides methods for validating and decoding a WifiPlug protocol packet
class WifiplugPacket():

    ## @var device_type
    #  Device type the packet came from
    

    ## Constructor
    #  Takes packet payload as string and populates the object with the data contained
    #  @param data String containing packet payload
    #  @return 
    def __init__(self, data):
        self.device_type = 'unknown'
        self.data = data
        self.msg_type = ''
        self.msg_value = ''
        
        if not self.validate_data(data):
            raise ValueError("Invalid packet data: %s" % data)
        
        self.msg_type = self.get_message_type(data)
        
        if msg_type == '+':
            self.device_type = 'server'
            self.msg_value = self.get_server_msg(data)
        elif msg_type == '1':
            self.device_type = 'plug'
            self.msg_value = self.get_registration(data)
        elif msg_type == '3':
            self.device_type = 'plug'
            self.msg_value = self.get_client_status(data)
        elif msg_type == '4':
            self.device_type = 'server'
            self.msg_value = self.get_server_command(data)
        else:
            raise Exception("Logic error: a valid message type has no parse handler")
    
    def validate_data(self, data):
        data = data.strip()
        if not data.startswith(MESSAGE_PREFIX):
            return False
        if not data.endswith(MESSAGE_SUFFIX):
            return False
        return True
    
    def get_message_type(self, data):
        type_offset = len(MESSAGE_PREFIX)
        type = data[type_offset]
        if type in MSG_TYPES:
            return type
        else:
            raise LookupError("Unknown packet message type: %s" % type)
    
    def get_registration(self, data):
        match = re.match(CLIENT_HELLO, data) # BBBB1,002509030acb,01,02EEEE 002509030acb
        return match.group(1)
    
    def get_client_status(self, data):
        status_offset = len(MESSAGE_PREFIX) + 2 # BBBB3,1 plug on
        status = data[status_offset]
        if status in CLIENT_STATES:
            return CLIENT_STATES[status]
        else:
            raise LookupError("Unknown client status: %s" % status)
            
    def get_server_command(self, data):
        cmd_offset = len(MESSAGE_PREFIX) + 2 # BBBB4,1 turn on
        cmd = data[cmd_offset]
        if cmd in SERVER_CMDS:
            return SERVER_CMDS[cmd]
        else:
            raise LookupError("Unknown server command: %s" % cmd)
            
    def get_server_msg(self, data):
        msg_start = len(MESSAGE_PREFIX) + 1 # BBBB+OKEEEE OK
        msg_end = len(data) - len(MESSAGE_SUFFIX)
        return data[msg_start:msg_end]

class Wifiplug():
    def __init__(self, addr, port, data):
        self.state = 'OFF'
        self.addr = addr
        self.port = port
        self.serial = self.decode(data)
    def decode(self, message):
        message = message.rstrip()
        if(message[0:len(MESSAGE_PREFIX)] == MESSAGE_PREFIX and message[-len(MESSAGE_SUFFIX.rstrip()):] == MESSAGE_SUFFIX.rstrip()):
            type = message[4]
            if type == '1':
                try:
                    match = re.match(CLIENT_HELLO.rstrip(), message)
                    return match.group(1)
                except Exception as e:
                    return False
            elif type == '3':
                self.state = 'OFF' if message[6] == '0' else 'ON'
                return self.state