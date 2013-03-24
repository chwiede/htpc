#!/usr/bin/python2

# Imports
import os
import sys
import time
import datetime
import subprocess
import record
import config


MANUAL = 0
WAKEUP = 1

def GetLastSetting(persistentFile):
    try:
        fileObj = open(persistentFile, 'r')
        result = float(fileObj.read())
        fileObj.close()
        
        return result
    except:
        return 0.0
    

def ClearWakeup(persistentFile, device):
    # ensure folder exists
    os.system('mkdir -p ' + os.path.dirname(persistentFile))    
    
    # clear file
    os.system('echo 0 > ' + persistentFile)

    # clear device
    os.system('echo 0 > ' + device)
    print 'wakeup cleared on device %s' % device



def SetWakeup(persistentFile, device, timestamp):
    # set timestemp to file
    os.system('echo ' + str(timestamp) + ' > ' + persistentFile)

    # set timestamp to device
    os.system('echo ' + str(timestamp) + ' > ' + device)
    print 'wakeup set to %s on device %s' % (datetime.datetime.fromtimestamp(timestamp), device)




def GetUptime():
    uptimeLine = subprocess.check_output('cat /proc/uptime', shell=True)
    uptimeParts = uptimeLine.split(' ')
    return float(uptimeParts[0])



def GetWakeupReason(persistentFile, allRecords):
    
    switchOnTime = time.time() - GetUptime()
    #print datetime.datetime.fromtimestamp(switchOnTime)
    
    lastSetting = GetLastSetting(persistentFile)
    if(lastSetting == 0 or lastSetting > switchOnTime):
        return MANUAL
    
    nextRecord = record.GetNextRecord(allRecords)
    if(nextRecord == None):
        return MANUAL
    
    recordStartSoon = (nextRecord.TimeBegin - switchOnTime) < config.WAKE_BEFORE
    recordInFuture = (nextRecord.TimeBegin - switchOnTime) > 0
    
    if(recordInFuture and recordStartSoon):
        return WAKEUP
    else:
        return MANUAL    
    
    
    

# direct mode, open configuration and write wakeup or clear
if (__name__ == '__main__'):

    # instantiate record scanner, get next record
    allRecords = record.GetRecords(config.DVR_FOLDER)
    nextRecord = record.GetNextRecord(allRecords)
    valueToSet = 0
    
    if(nextRecord != None):
        valueToSet = int(nextRecord.TimeBegin - config.WAKE_BEFORE)
    
    # determine last setted value
    valueLast = int(GetLastSetting(config.RTC_PERSISTENT))
    
    # avoid multiple rewrites    
    if(valueToSet != valueLast):
        ClearWakeup(config.RTC_PERSISTENT, config.RTC_DEVICE)
        
        if(valueToSet > time.time()):
            SetWakeup(config.RTC_PERSISTENT, config.RTC_DEVICE, valueToSet)
        else:
            print 'no new wakeup to set.'
    
    else:
        print 'no wakeup changes detected.'
        
