#!/usr/bin/python2

import sys
import time
import process
from thread import start_new_thread

class ScreenAgent():
    
    _command = 'xrandr --current | grep connected'
    _pollInterval = 5.0
    _pollEnabled = False
    _callback = None
    
    
    def __init__(self, screenChangedCallback):
        # save callback
        self._callback = screenChangedCallback
    
    
    def _GetState(self):
        # execute xrandr, calculate hash and return
        cmdResult = process.GetOutput(self._command)
        return hash(cmdResult)
    

    def _PollWorker(self):
        # define flags
        _newChanged = False
        _newState = self._GetState()
        _lastChanged = _newChanged
        _lastState = _newState
        
        # start main loop
        while(self._pollEnabled):
            time.sleep(self._pollInterval)
            _newState = self._GetState()
            _newChanged = _newState != _lastState
            
            # wait until change-sig is going from true to false            
            if(_lastChanged and not _newChanged):
                if(self._pollEnabled and self._callback != None):
                    # execute callback
                    self._callback()
                    
                    # reset values to avoid multiple events
                    _newState = self._GetState()
                    _lastChanged = False
            
            # save current states
            _lastState = _newState
            _lastChanged = _newChanged


    def Start(self):
        # start poll worker as extra thread
        self._pollEnabled = True
        start_new_thread(self._PollWorker, ())
        
        
    def Stop(self):
        self._pollEnabled = False
        

