#!/usr/bin/python2

# Import sytem, deny output of bytecode
import sys
sys.dont_write_bytecode = True

# imports
import os
import time
import record
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
	
	# load config
	config = ConfigParser.ConfigParser()
	config.read(['/etc/htpcutils/htpc.conf'])
	
	# define wakeup variables
	wakeupFile = config.get('Paths', 'RtcPersistent')
	wakeupDevice = config.get('Devices', 'RtcDevice')
	
	# print config
	print 'persistend file:   ', wakeupFile
	print 'rtc device:        ', wakeupDevice
	print 'timestamp now:     ', int(time.time())
	
	# instantiate record scanner, get next record
	recordScanner = record.RecordScanner(config.get('Paths', 'DvrLogPath'))
	nextRecord = recordScanner.GetNextRecord()
	
	# clear wakeup. happens wether record defined or not
	ClearWakeup(wakeupFile, wakeupDevice)
	
	if(nextRecord != None):
		wakeupTimestamp = nextRecord.TimeBegin - float(config.get('Times', 'WakeUpBefore'))
		SetWakeup(wakeupFile, wakeupDevice, int(wakeupTimestamp))
		print 'timestamp rec:     ', int(wakeupTimestamp)
		print 'Next wakeup set to: %s' % datetime.datetime.fromtimestamp(wakeupTimestamp)
	else:
		print 'Wakup was cleared. No record planned!'
	
	
	