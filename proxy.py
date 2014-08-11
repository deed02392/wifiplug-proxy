import sys
from socket import *
from threading import Thread
import threading
from flask import Flask
import time
import inspect
from wifiplug import WifiplugPacket

LOGGING = 1

def log( s ):
    if LOGGING:
        print '%s:%s' % ( time.ctime(), s )
        sys.stdout.flush()

plugs = []

class PipeThread( Thread ):
    pipes = []
    def __init__( self, source, sink ):
        Thread.__init__( self )
        self._stop = threading.Event()
        self.daemon = True
        self.source = source
        self.sink = sink
        self.sourcetype = 'unknown'
        self.status = ''
        self.last_msg_type = ''
        self.last_msg_value = ''
        
        log( 'Creating new pipe thread  %s ( %s -> %s )' % \
            ( self, source.getpeername(), sink.getpeername() ))
        PipeThread.pipes.append( self )
        log( '%s pipes active' % len( PipeThread.pipes ))

    def run( self ): # Thread execution payload
        while 1:
            try:
                data = self.source.recv( 1024 )
                if not data: break
                log(data)
                # Determine source type by analysing packet
                packet = wifiplug.WifiplugPacket(data)
                self.sourcetype = packet.device_type
                self.last_msg_type = packet.msg_type
                self.last_msg_value = packet.msg_value
                
                if self.sourcetype == 'plug' and self.last_msg_type == '3':
                    self.status = self.last_msg_value
                
                self.sink.send(data)
            
            except Exception as e:
                log('pipe exception: %s' % e)

        log( '%s terminating' % self )
        PipeThread.pipes.remove( self )
        log( '%s pipes active' % len( PipeThread.pipes ))
    
    def stop(self):
        self._stop.set()

class Pinhole( Thread ): # Extends Thread
    def __init__( self, port, newhost, newport ):
        Thread.__init__( self ) # Call Thread constructor
        log( 'Redirecting: 0.0.0.0:%s -> %s:%s' % ( port, newhost, newport ))
        self.daemon = True
        self.newhost = newhost
        self.newport = newport
        self.sock = socket( AF_INET, SOCK_STREAM )
        self.sock.bind(( '', port ))
        self.sock.listen(5)
    
    def run( self ): # Thread execution payload
        while 1:
            client_sock, address = self.sock.accept()
            log( 'Creating new session for %s:%s ' % address )
            server_sock = socket( AF_INET, SOCK_STREAM )
            server_sock.connect(( self.newhost, self.newport ))
            PipeThread( client_sock, server_sock ).start()
            PipeThread( server_sock, client_sock ).start()

if __name__ == '__main__':
    #sys.stdout = open( 'pinhole.log', 'w' )
    print "Starting Pinhole..."

    import pprint
    import Queue
    import wifiplug
    queue = Queue.Queue( maxsize=0 )
    flask = Flask(__name__)
    
    @flask.route('/toggle')
    def toggle():
        for pipe in PipeThread.pipes:
            if pipe.sourcetype == 'plug':
                if pipe.status == 'plug on':
                    pipe.source.send("BBBB4,0EEEE")
                else:
                    pipe.source.send("BBBB4,1EEEE")
                    
        return "ok"
    
    @flask.route('/pipes')
    def list_pipes():
        count = 1
        str = '<pre>'
        for pipe in PipeThread.pipes:
            str += "Pipe num: %i" % count
            str += "  %s - (%s, %s)\r\n" % (pipe.sourcetype, pipe.last_msg_type, pipe.last_msg_value)
            count += 1
        return str

    Pinhole( 221, '54.217.214.117', 221 ).start()
    flask.run(host='0.0.0.0')
    
    while 1:
        # Ah ah ah ah, stayin' alive
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print "Exiting..."
            for pipe in PipeThread.pipes:
                pipe.source.shutdown(SHUT_RDWR)
                pipe.source.close()
                pipe.sink.shutdown(SHUT_RDWR)
                pipe.sink.close()
            sys.exit(1)
