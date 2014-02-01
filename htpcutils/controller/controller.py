#!/usr/bin/python2

# Imports
import time
from lib import wakeup
from lib import record
from lib import config
from lib import process
from lib.operationmode import OperationMode
from lib.screenagent import ScreenAgent
from lib.acpid import Acpid


class Controller():
	
	_acpidListener = None
	_screenListener = None
	_changeLock = False
	
	IsEnabled = True
	ModeCurrent = None
	ModeRecord = None
	ModeWatch = None
	
	
	def SubscribePowerButton(self):
		self._acpidListener = Acpid()
		self._acpidListener.Register('button/power PBTN', self.PowerButton)
		self._acpidListener.Start()
		
		
	
	def PowerButton(self, data):
		# execute locked
		if(self._changeLock):
			print 'return because lock active'
			return
		else:
			self._changeLock = True
		
		# print info
		print 'powerbutton event raised.'
		
		# what is the current mode?
		if (self.ModeCurrent == self.ModeWatch):
			# watch mode has ended, shutdown or go into record mode
			self.WatchModeStop()
			
		elif (self.ModeCurrent == self.ModeRecord):
			# go to watch mode and keep alive!
			self.ChangeMode(self.ModeWatch)
	
		# reset lock flag
		self._changeLock = False
		
		
	
	def GetRecordPending(self):
		records = record.GetRecords(config.DVR_FOLDER)
		isRunning = record.GetActiveRecords(records) > 0
		if(isRunning):
			return True		
		
		# no planned record? leave immediatly
		nextRecord = record.GetNextRecord(records)		
		if (nextRecord == None):
			return False
			
		# calculate time to next record
		timeToNextRec = nextRecord.TimeBegin - time.time()
		timeToNextRec = timeToNextRec - config.WAKE_BEFORE
		
		# smaller then bridgetime??
		return timeToNextRec < config.RECORD_BRIDGE
		
		
	
	def WatchModeStop(self):
		# message, check for active or pending records
		print 'watchmode stopped. check for pending records...'
		recordsPending = self.GetRecordPending()
		
		# stay alive?
		if(recordsPending):
			print 'records running or pending. staying alive!'
			self.ChangeMode(self.ModeRecord)
		else:
			print 'no running or pending records. bye bye!'
			self.Shutdown()
			
			
		
	def Shutdown(self):	
		try:
			# close event listener
			self._acpidListener.Stop()
			self._screenListener.Stop()
			
			# stop current mode
			self.ModeCurrent.Stop()
			
		except:
			print 'error while stop logic. shutdown anyway...'
			
		# Shutdown cmd
		process.Start(config.CMD_SHUTDOWN)

		# stop main loop
		self.IsEnabled = False
		
		
		
	def SetWakeup(self):
		# get next record and last setting
		nextRecord = record.GetNextRecord(record.GetRecords(config.DVR_FOLDER))
		lastSetting = wakeup.GetLastSetting(config.RTC_PERSISTENT)
		
		# something new to set?
		if(nextRecord != None):
			timestamp = nextRecord.TimeBegin - config.WAKE_BEFORE
			if(timestamp != lastSetting):
				wakeup.ClearWakeup(config.RTC_PERSISTENT, config.RTC_DEVICE)							
				wakeup.SetWakeup(config.RTC_PERSISTENT, config.RTC_DEVICE, timestamp)
			else:
				print 'wakeup timestamp was already set. no changes done.'
		else:
			if(lastSetting != 0):
				wakeup.ClearWakeup(config.RTC_PERSISTENT, config.RTC_DEVICE)
			else:
				print 'wakeup already cleared. no changes done.'
		
		
	
	def ChangeMode(self, mode):
		# stop screen change detection
		self._screenListener.Stop()
		
		# stop current mode, wait little bit for hardware
		self.ModeCurrent.Stop()
		time.sleep(5)
		
		# change current mode, wait little bit for hardware
		self.ModeCurrent = mode
		self.ModeCurrent.Start()
		time.sleep(2)
		
		# restart screen change detection
		self._screenListener.Start()
		
			
	
	def SubscribeScreenChange(self):
		self._screenListener = ScreenAgent(self.ScreenChange)
		self._screenListener.Start()
		
		# reset lock flag
		self._changeLock = False
		
	
	
	def ScreenChange(self):
		# execute locked
		if(self._changeLock):
			print 'return because lock active'
			return
		else:
			self._changeLock = True

		# restart current mode
		print 'screen change detected. restarting current mode.'
		self.ModeCurrent.Stop()
		self.ModeCurrent.Start()		
	
		# reset lock flag
		self._changeLock = False
		
		
	def PrintWelcome(self, modeStr):
		print 'HTPC CONTROLLER STARTED (%s)' % modeStr		
	
	
	def Run(self):
		# wait some time for tvheadend
		time.sleep(0.5)

		# determine the wakeup-reason
		# set current mode due to this information
		allRecords = record.GetRecords(config.DVR_FOLDER)
		activeRecs = record.GetActiveRecords(allRecords)
		wakeReason = wakeup.GetWakeupReason(config.RTC_PERSISTENT, allRecords)
		if (wakeReason == wakeup.MANUAL and activeRecs == 0):
			self.PrintWelcome('watch mode')
			self.ModeCurrent = self.ModeWatch
		else:
			self.PrintWelcome('record mode')
			self.ModeCurrent = self.ModeRecord
		
		# start mode
		self.ModeCurrent.Start()
		
		# wait for display if needed
		if config.WAIT_FOR_DISPLAY != None:
			if int(config.WAIT_FOR_DISPLAY) > 0:
				time.sleep(int(config.WAIT_FOR_DISPLAY))
		
		# subscribe to events
		self.SubscribePowerButton()
		self.SubscribeScreenChange()
		
		_lastRecCheck = time.time()
		while (self.IsEnabled):
			# wait
			time.sleep(1)
			
			# recordmode? check for running or pending
			if(self.ModeCurrent == self.ModeRecord):
				if(time.time() - _lastRecCheck > 300):
					_lastRecCheck = time.time()
					if(not self.GetRecordPending()):
						self.Shutdown()			
			


if (__name__ == '__main__'):
	# define controller
	controller = Controller()
	
	# define run modes
	controller.ModeRecord = OperationMode(
		config.MODE_RECORD_START,
		config.MODE_RECORD_STOP)
		
	controller.ModeWatch = OperationMode(
		config.MODE_WATCH_START,
		config.MODE_WATCH_STOP)
		
	# startup controller
	controller.Run()
	
	# bye
	exit()
