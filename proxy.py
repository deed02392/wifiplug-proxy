"""
usage 'pinhole port host [newport]'

Pinhole forwards the port to the host specified.
The optional newport parameter may be used to
redirect to a different port.

eg. pinhole 80 webserver
    Forward all incoming WWW sessions to webserver.

    pinhole 23 localhost 2323
    Forward all telnet sessions to port 2323 on localhost.
"""

import sys
from socket import *
from threading import Thread
import time

LOGGING = 1

def log( s ):
    if LOGGING:
        print '%s:%s' % ( time.ctime(), s )
        sys.stdout.flush()

class PipeThread( Thread ):
    pipes = []
    def __init__( self, source, sink ):
        Thread.__init__( self )
        self.source = source
        self.sink = sink

        log( 'Creating new pipe thread  %s ( %s -> %s )' % \
            ( self, source.getpeername(), sink.getpeername() ))
        PipeThread.pipes.append( self )
        log( '%s pipes active' % len( PipeThread.pipes ))

    def run( self ): # Thread execution payload
        while 1:
            try:
                data = self.source.recv( 1024 )
                if not data: break
                self.sink.send( data )
            except:
                break

        log( '%s terminating' % self )
        PipeThread.pipes.remove( self )
        log( '%s pipes active' % len( PipeThread.pipes ))

class AdminThread( Thread ):
    def __init__( self, bind, port ):
        Thread.__init__( self )
        self.bind = bind
        self.port = port
        self.sock = socket( AF_INET, SOCK_STREAM )
        self.sock.bind(( bind, port ))
        self.sock.listen(1)
        
        log( "Starting admin thread: %s:%s" % \
            ( bind, port ))
    
    def run( self ): # Thread execution payload
        while 1:
            try:
                while 1:
                    adminsock, address = self.sock.accept()
                    log( 'Admin connected from %s %s ' % address )
                    while 1:
                        adminsock.send( "%s" % pprint.pformat(PipeThread.pipes, depth=5) )
                        time.sleep(5)
            except Exception as e:
                log ( 'Admin thread: Exception: %s' % e )
                sys.exit(2)

class Pinhole( Thread ): # Extends Thread
    def __init__( self, port, newhost, newport ):
        Thread.__init__( self ) # Call Thread constructor
        log( 'Redirecting: localhost:%s -> %s:%s' % ( port, newhost, newport ))
        self.newhost = newhost
        self.newport = newport
        self.sock = socket( AF_INET, SOCK_STREAM )
        self.sock.bind(( '', port ))
        self.sock.listen(5)
    
    def run( self ): # Thread execution payload
        while 1:
            newsock, address = self.sock.accept()
            log( 'Creating new session for %s %s ' % address )
            fwd = socket( AF_INET, SOCK_STREAM )
            fwd.connect(( self.newhost, self.newport ))
            PipeThread( newsock, fwd ).start()
            PipeThread( fwd, newsock ).start()
       
if __name__ == '__main__':

    print 'Starting Pinhole'

    import pprint
    import sys
    import Queue
    sys.stdout = open( 'pinhole.log', 'w' )
    queue = Queue.Queue( maxsize=0 )
    
    if len( sys.argv ) > 1:
        port = newport = int( sys.argv[1] )
        newhost = sys.argv[2]
        if len( sys.argv ) == 4: newport = int( sys.argv[3] )
        Pinhole( port, newhost, newport ).start()
    else:
        try:
            Pinhole( 9090, '127.0.0.1', 5005 ).start()
            AdminThread( '', 8091 ).start()
        except KeyboardInterrupt:
            sys.exit(1)