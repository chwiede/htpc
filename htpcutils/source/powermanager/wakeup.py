#!/usr/bin/python2

# Import sytem, deny output of bytecode
import sys
sys.dont_write_bytecode = True

# imports
import os
import commands


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



# Test Mode
if (__name__ == '__main__'):
	lastSetting = GetLastSetting('/var/tmp/htpc-wakeup.timestamp')
	print 'Last known setting: ', lastSetting
	print '-----------------------------------------'
	print 'RTC: ', open('/proc/driver/rtc', 'r').read()

