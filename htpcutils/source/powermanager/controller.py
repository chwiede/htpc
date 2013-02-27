#!/usr/bin/python2

# Import sytem, deny output of bytecode
import sys
sys.dont_write_bytecode = True

# imports
import os
import time
import acpid
import record
import wakeup
import process
import datetime
import ConfigParser
from thread import start_new_thread

class controller():    
    
    RecordScanner = None
    WakeupFile = None
    WakeupDevice = None
    Config = None
    FrontendActive = False
    CheckingForShutdown = False
    IsEnabled = True
    
    
    def __init__(self):
        # open configuration
        self.Config = ConfigParser.ConfigParser()
        self.Config.read(['/etc/htpcutils/htpc.conf'])
        
        self.WakeupFile = self.Config.get('Paths', 'RtcPersistent')
        self.WakeupDevice = self.Config.get('Devices', 'RtcDevice')
        
        self.RecordScanner = record.RecordScanner(self.Config.get('Paths', 'DvrLogPath'))
      
        
        
    def GetAwakedForRecord(self):
        # machine is in record mode, if
        # * known wakeup is some minutes ago
        # * a records is planned in some minutes
        
        # so get some timestamps to work with
        lastWakeup = wakeup.GetLastSetting(self.WakeupFile)
        nextRecord = self.RecordScanner.GetNextRecord()
        uptime = wakeup.GetUptime()
        now = time.time()
        
        bootTimeAvg = float(self.Config.get('Times', 'BootTime'))
        wakeupBefore = float(self.Config.get('Times', 'WakeUpBefore'))
                
        return (
            lastWakeup != 0
            and nextRecord != None
            and ((now - uptime) - lastWakeup) < bootTimeAvg
            and (nextRecord.TimeBegin - now) < wakeupBefore
        )  
    
    
    
    
    def GetFrontendRunning(self):
        procName = self.Config.get('Paths', 'FrontendProcess')
        return process.GetProcessIsActive(procName)
    
    
    
    def FrontendHasEnded(self, proc):
        restartAtError = self.Config.get('Misc', 'FrontendRestart')
        
        if(proc.returncode == 0 or self.FrontendActive == False):
            print 'frontend has ended successfully.'
            self.StopFrontend(False)
        elif (restartAtError == '1'):
            print 'frontend has ended with error=', proc.returncode
            print 'frontend will be restarted...'
            self.StartFrontend()
        else:
            print 'frontend as endet with error, but will not be restarted.'
            print 'change configuration to restart frontend.'
    
    
    
    def StartFrontend(self):
        # set flag
        self.FrontendActive = True        
        
        frontendCmd = self.Config.get('Paths', 'Frontend')
        process.StartWithCallback(frontendCmd, self.FrontendHasEnded)
        
        while(not self.GetFrontendRunning()):
            time.sleep(0.5)
            
    
    
    def StopFrontend(self, kill = True, killWait = 0):
        # set flag
        self.FrontendActive = False
        
        # define worker logic
        def StopFrontendLogic():
            time.sleep(killWait)            
            procName = self.Config.get('Paths', 'FrontendProcess')
            if(kill and process.GetProcessIsActive(procName)):
                process.Kill(procName)
                print 'frontend terminated.'
                
            self.CheckForShutdown()
            
        # Call worker logic
        if(killWait > 0):
            start_new_thread(StopFrontendLogic, ())
        else:
            StopFrontendLogic()
            
            
        
        
    
    #def EnsureFrontendState(self):
    #    # check for frontend and correct state
    #    frontendRunning = self.GetFrontendRunning()
    #    if(self.FrontendActive and not frontendRunning):
    #        self.StartFrontend()
    #        
    #    if(frontendRunning and not self.FrontendActive):
    #        self.StopFrontend()
            
            
        
    def GetIsRecordActive(self):
        # is currently a record active?
        allRecords = self.RecordScanner.GetRecords()
        
        for rec in allRecords:
            if(rec.IsRunning):
                return True
            
        #maybe there's a record in a few minutes?
        recordBridgeTime = 60.0 * float(self.Config.get('Times', 'RecordBridgeTime'))
        recordNext = self.RecordScanner.GetNextRecord(allRecords)
        
        if(recordNext == None):
            return False

        return ((recordNext.TimeBegin - time.time()) < recordBridgeTime)
    
    
    
    def Shutdown(self):
        # shutdown only once :-)
        if(self.IsEnabled == False):
            return;
        else:
            self.IsEnabled = False
        
        # set next wakeup
        nextRecord = self.RecordScanner.GetNextRecord()
        wakeup.ClearWakeup(self.WakeupFile, self.WakeupDevice)
        if(nextRecord != None):
            wakeupTimestamp = nextRecord.TimeBegin - float(self.Config.get('Times', 'WakeUpBefore'))
            wakeup.SetWakeup(self.WakeupFile, self.WakeupDevice, wakeupTimestamp)
            print 'Next Wakeup set to %s' % datetime.datetime.fromtimestamp(wakeupTimestamp)              
        
        # bye bye, see you next time
        if(self.FrontendActive):
            self.StopFrontend(True)
        
        # run shutdown command
        shutdownCmd = self.Config.get('Paths', 'Shutdown')
        os.system(shutdownCmd)        
                
    
    
    
    def CheckForShutdown(self):
        # leave, if flag or frontend active
        if(self.CheckingForShutdown or self.FrontendActive):
            return
        
        # set flag
        self.CheckingForShutdown = True
        
        # is an record (soon) running? 
        isRecordActive = self.GetIsRecordActive()
        
        # no record, no frontend?? go sleep!
        if(not isRecordActive):
            print 'nothing to do, invoke shutdown.'
            self.Shutdown()
        else:
            print 'frontend standby mode (record active)'
            
        # reset flag
        self.CheckingForShutdown = False
       
    
    
    def AcpidEvent(self, acpiResult):
        # check for power button
        if(acpiResult.startswith('button/power')):
            
            print 'got acpid-powerbutton event.'
            
            # frontend not active? toggle bit, and start!
            if(self.FrontendActive == False):
                print 'starting frontend...'
                self.StartFrontend()
            
            # frontend seems to be active. stop with delay...    
            else:
                print 'try stopping frontend...'
                self.StopFrontend(kill=True, killWait=5.0)
            
    
 

    def Run(self):
        # find out, if machine was started for an record
        isAwakedForRecord = self.GetAwakedForRecord()        
        
        # if not recordmode, start frontend
        if(not isAwakedForRecord):
            self.StartFrontend()
            
        # start acpid-watchdog
        acpiWatcher = acpid.Acpid()
        acpiWatcher.Listen(self.AcpidEvent)
        
        # get polling time
        checkPollTime = max(10, float(self.Config.get('Times', 'PollTime')))
        
        # go into main loop
        lastCheck = 0        
        while(self.IsEnabled):
            # wich time? someone has a clock?
            now = time.time()
            
            # check records not to often. (multi file scan...)
            if(now - lastCheck > checkPollTime):
                self.CheckForShutdown()
                lastCheck = now                 
                        
            time.sleep(0.2)
        
        



# Direct Mode            
if (__name__ == '__main__'):
    ctl = controller()
    ctl.Run()
