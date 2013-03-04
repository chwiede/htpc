#!/usr/bin/python2

# Import sytem, deny output of bytecode
import sys
sys.dont_write_bytecode = True

# imports
import os
import time
import record
import config
import commands
import datetime
import ConfigParser

def GetLastSetting(persistentFile):
	try:
		fileObj = open(persistentFile, 'r')
		result = float(fileObj.read())
		fileObj.close()
		
		return result
	except:
		return 0.0
	


def ClearWakeup(persistentFile, device):
	# clear file
	os.system('echo 0 > ' + persistentFile)

	# clear device
	os.system('echo 0 > ' + device)



def SetWakeup(persistentFile, device, timestamp):
	# set timestemp to file
	os.system('echo ' + str(timestamp) + ' > ' + persistentFile)

	# set timestamp to device
	os.system('echo ' + str(timestamp) + ' > ' + device)



def GetUptime():
	uptimeLine = commands.getoutput('cat /proc/uptime')
	uptimeParts = uptimeLine.split(' ')
	return float(uptimeParts[0])



# direct mode, open configuration and write wakeup or clear
if (__name__ == '__main__'):

	# instantiate record scanner, get next record
	recordScanner = record.RecordScanner(config.DVR_LOG_PATH)
	nextRecord = recordScanner.GetNextRecord()
	
	# clear wakeup. happens wether record defined or not
	ClearWakeup(config.RTC_PERSISTENT, config.RTC_DEVICE)
	
	if(nextRecord != None):
		wakeupTimestamp = nextRecord.TimeBegin - float(config.WAKE_BEFORE)
		SetWakeup(config.RTC_PERSISTENT, config.RTC_DEVICE, int(wakeupTimestamp))
		print 'timestamp rec:     ', int(wakeupTimestamp)
		print 'Next wakeup set to: %s' % datetime.datetime.fromtimestamp(wakeupTimestamp)
	else:
		print 'Wakup was cleared. No record planned!'
	
	
	