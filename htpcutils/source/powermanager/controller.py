#!/usr/bin/python2

# Import sytem, deny output of bytecode
import sys
sys.dont_write_bytecode = True

# imports
import os
import time
import acpid
import config
import record
import wakeup
import process
import datetime
import ConfigParser
from thread import start_new_thread

class controller():
    
    ControllerAlive = True
    RestartCounter = 0
    RecordScanner = record.RecordScanner(config.DVR_LOG_PATH)
    FrontendDesired = False
    PollRequest = False
    
    
    def FrontendExit(self, proc):
        print 'frontend has been closed with returncode ', proc.returncode
        
        # clean exit? correct frontend desired state
        if(proc.returncode == 0):
            self.FrontendDesired = False
        
        # frontend crashed, but should be open? restart!
        elif(self.FrontendDesired and config.FRONTEND_RESTART):
            time.sleep(5)
            if(self.RestartCounter < 10):
                self.RestartCounter = self.RestartCounter + 1
                self.FrontendStateChange()
            else:
                print 'ERROR! Frontent crashed more then 10 times.'
                print 'something strange is happening... exit!'
                self.ControllerAlive = False
                exit()
            
        # frontend dead, and no frontend desired?? request for shutdown
        if(not self.FrontendDesired):
            print 'initiating exit request'
            self.PollRequest = True
        
    

    def FrontendStateChange(self):
        # frontend desired, but not running? start it!
        if(self.FrontendDesired and not process.GetProcessIsActive(config.PROC_FRONTEND)):
            print 'starting frontend.'
            process.StartWithCallback(config.CMD_FRONTEND, self.FrontendExit)
            process.WaitFor(config.PROC_FRONTEND)
            
        # frontend not desired, but running? kill it
        if(not self.FrontendDesired and process.GetProcessIsActive(config.PROC_FRONTEND)):
            print 'wait for frontend exit...'
            time.sleep(5.0)
            
            # frontend still running? send kill signal.                
            if(process.GetProcessIsActive(config.PROC_FRONTEND)):
                print 'frontend still alive -> sending kill signal!'
                process.Kill(config.PROC_FRONTEND, True)


    
    def AcpidEvent(self, acpiResult):
        # check for power button
        if(acpiResult.startswith('button/power')):
            print 'got acpid-powerbutton event, toggle frontend desired state'
            self.FrontendDesired = not self.FrontendDesired
            self.FrontendStateChange()
            
                
                
    def GetIsUpForRecord(self):
        # machine is in record mode, if
        # * known wakeup is some minutes ago
        # * a records is planned in some minutes
        
        # so get some timestamps to work with
        lastWakeup = wakeup.GetLastSetting(config.RTC_PERSISTENT)
        nextRecord = self.RecordScanner.GetNextRecord()
        uptime = wakeup.GetUptime()
        now = time.time()
        
        return (
            lastWakeup != 0
            and nextRecord != None
            and ((now - uptime) - lastWakeup) < config.BOOT_TIME
            and (nextRecord.TimeBegin - now) < config.WAKE_BEFORE
        )
    
    
    
    def GetIsRecordMode(self):
        records = self.RecordScanner.GetRecords()
        
        for rec in records:
            if(rec.IsRunning):
                return True
            
        nextRecord = self.RecordScanner.GetNextRecord(records)
        if(nextRecord == None):
            return False
        else:
            return (nextRecord.TimeBegin - time.time()) < config.RECORD_BRIDGE
            
            
            
    def Shutdown(self):
        print 'initiating shutdown: ', config.CMD_SHUTDOWN
        process.Start(config.CMD_SHUTDOWN)
        exit()
                                

    
    def Run(self):
        print 'HTPC-UTILS CONTROLLER STARTED!'
        # hook into acpid
        acpiWatcher = acpid.Acpid()
        acpiWatcher.Listen(self.AcpidEvent)

        # up for a record?
        upForRecord = self.GetIsUpForRecord()
        if(upForRecord):
            print 'wakeup for an record => standbymode'
        else:
            print 'normal wakeup => starting frontend'
        
        isRecordMode = upForRecord
        self.FrontendDesired = not upForRecord
        self.FrontendStateChange()

        # main loop
        checkDone = False
        lastCheck = time.time()
        while(self.ControllerAlive):
            
            # poll for records
            if(self.PollRequest or (time.time() - lastCheck) > config.POLL_TIME):
                isRecordMode = self.GetIsRecordMode()
                lastCheck = time.time()
                checkDone = True
                self.PollRequest = False
            
            # no record, no frontend? leave main loop.
            if(checkDone and not isRecordMode and not self.FrontendDesired):
                break;
            
            # wait some time, clear flags            
            time.sleep(0.25)
            checkDone = False
        
        # bye
        if(self.ControllerAlive):
            self.Shutdown()        




# Run Mode            
if (__name__ == '__main__'):
    ctl = controller()

    try:
        ctl.Run()
    except SystemExit:
        print '\nsystem exit.\n'
        pass
    except KeyboardInterrupt:
        print '\nuser has aborted via ctrl+c.\n'
        pass
    except Exception ,e:
        import traceback
        print 'GOT EXCEPTION! Program aborted.'
        print traceback.format_exc()        
        
        