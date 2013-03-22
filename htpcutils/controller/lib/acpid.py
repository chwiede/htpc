#!/usr/bin/python2

# Imports
import re
import sys
import time
import socket
from thread import start_new_thread

class Acpid():

    _IsEnabled = True
    _Socket = '/var/run/acpid.socket'
    _Buffer = 4096    
    _Callbacks = {}

    def _AcpidEvent(self, data):
        # loop through callbaks
        for pattern, callback in self._Callbacks.iteritems():
            isMatch = (pattern == data) or re.match(pattern, data)
            
            # callback found? call it!
            if(isMatch):
                callback(data)                


    def Start(self):
        # define async listener function
        def AsyncSocketListener():    
            sck = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sck.connect(self._Socket)

            while(self._IsEnabled):
                socketResult = sck.recv(self._Buffer)
                for line in socketResult.split('\n'):
                    if(line != None and line != '' and self._IsEnabled):
                        self._AcpidEvent(socketResult)

        # start async listener function
        start_new_thread(AsyncSocketListener, ())


    def Stop(self):
        self._IsEnabled = False
        
        
    def Register(self, pattern, callback):
        self._Callbacks[pattern] = callback

