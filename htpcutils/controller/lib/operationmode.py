#!/usr/bin/python2

import sys
import time
import process

class OperationMode():
	
	CommandStart = ''
	CommandStop = ''
	CheckXRunning = None
	
	
	def __init__(self, commandStart, commandStop):	
		# set member variables
		self.CommandStart = commandStart
		self.CommandStop = commandStop
		self.CheckXRunning = self.GetXRunning
		
	
	def Start(self):
		# start process by command
		print 'starting operationmode by command %s' % self.CommandStart
		process.Start(self.CommandStart)
	
		if(self.CheckXRunning == None):
			print 'no check available'
			return
		
		while (not self.CheckXRunning()):
			time.sleep(0.5)
		
	
	def Stop(self):
		# stop process by command
		print 'stopping operationmode by command %s' % self.CommandStop
		process.Start(self.CommandStop)
		
		if(self.CheckXRunning == None):
			print 'no check available'
			return
		
		while (self.CheckXRunning()):
			time.sleep(0.5)
		
		
	def GetXRunning(self):
		# try to get PID of process 'X'
		result = process.GetOutput('pidof X')
		
		# return true, if PID found!
		return result != None and result != ''
		
