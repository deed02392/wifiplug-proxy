import sys
from socket import *
from threading import Thread
import threading
from flask import Flask
import time
import inspect

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
                # Determine source type
                if self.sourcetype == 'unknown':
                    # Is it a plug?
                    
                    if not self.sourcetype == 'server':
                        self.plug = wifiplug.Wifiplug('', '', data)
                        if self.plug.serial and (len(self.plug.serial) == 12):
                            for pipe in self.pipes:
                                if pipe.plug and pipe.plug.serial == self.plug.serial:
                                    # Dead connection needs resetting
                                    pipe.stop()
                            self.sourcetype = 'plug'
                            while 1:
                                try:
                                    data = self.source.recv(1024)
                                    if not data: break
                                    self.plug.decode(data)
                                    self.sink.send(data)
                                except:
                                    break
                        else:
                            self.sourcetype = 'server'
                    else:
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
                client = pipe
            elif pipe.sourcetype == 'server':
                server = pipe
        if client.plug.state == 'ON':
            client.source.send(wifiplug.SERVER_TURN_OFF) # To Client
            server.source.send(wifiplug.CLIENT_STATUS_OFF) # To Server
        else:
            client.source.send(wifiplug.SERVER_TURN_ON) # To Client
            server.source.send(wifiplug.CLIENT_STATUS_ON) # To Server
        return "ok"
    
    @flask.route('/pipes')
    def list_pipes():
        str = ''
        for pipe in PipeThread.pipes:
            str += "%s\r\n" % pprint.pformat(inspect.getmembers(pipe), depth=5)
        return str
    @flask.route('/plugs')
    def list_plugs():
        str = ''
        for pipe in PipeThread.pipes:
            if pipe.sourcetype == 'plug':
                str += "%s\r\n" % pprint.pformat(inspect.getmembers(pipe.plug), depth=5)
        return str

    Pinhole( 221, '54.217.214.117', 221 ).start()
    flask.run(host='0.0.0.0')
    
    while 1:
        # Ah ah ah ah, stayin' alive
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print "Exiting..."
            sys.exit(1)
