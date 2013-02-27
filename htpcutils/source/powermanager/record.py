#!/usr/bin/python2

# Import sytem, deny output of bytecode
import sys
sys.dont_write_bytecode = True

# imports
import os
import time
import json


class Record():

	Title = ""
	TimeBegin = 0
	TimeEnd = 0
	ErrorCode = 0
	IsRunning = False	



class RecordScanner():

	# the current folder, wich is scanned for records
	folder = ''


	def __init__(self, folder):
		self.folder = folder



	def GetRecords(self):
		# define result list
		result = []
		
		# no folder? return empty list
		if (not os.path.isdir(self.folder)):
			return result

		# Loop through the folders files, and read as json
		# Append a new record-object to result list
		for fl in os.listdir(self.folder):
			filePath = os.path.join(self.folder, fl)
			result.append(self.GetRecord(filePath))
	
		# give out result list
		return result
	
	

	def GetRecord(self, filepath):
		# load json file
		data = json.load(open(filepath))
	
		# instantiate new object
		result = Record()
	
		# set properties
		result.TimeBegin = data["start"] - 60 * data["start_extra"]
		result.TimeEnd = data["stop"] + 60 * data["stop_extra"]
		result.Title = data["title"].itervalues().next()
	
		if(data.has_key("errorcode")):
			result.ErrorCode = data["errorcode"]
	
		timestmp = time.time()
		result.IsRunning = (
			(result.ErrorCode == 0) and 
			(result.TimeBegin < timestmp) and 
			(timestmp < result.TimeEnd)
		)
	
		# return
		return result
	
	
	
	def GetActiveRecords(self, records = None):
		# Load records, if nothing given
		if(records == None):
			records = self.GetRecords()
			
		# count running records
		result = 0		
		for record in records:
			if(record.IsRunning):
				result += 1
		
		# give out
		return result
		
		
		
	def GetNextRecord(self, records = None):
		# get all records
		if(records == None):
			records = self.GetRecords()
		
		# loop through, find next
		result = None
		tsNow = time.time()
		tsNext = sys.maxint
		
		for rec in records:
			if(rec.TimeBegin > tsNow and rec.TimeBegin < tsNext):
				tsNext = rec.TimeBegin
				result = rec

		return result
			
			

# Test Mode			
if (__name__ == '__main__'):
	scanner = RecordScanner('/home/hts/.hts/tvheadend/dvr/log/')
	records = scanner.GetRecords()
	
	# soft for begin
	records = sorted(records, key=lambda rec: rec.TimeBegin)
	
	# give out
	for rec in records:
		print ('"%s" in about %s minutes.' % (
			rec.Title, 
			int((rec.TimeBegin - time.time()) / 60)
		))
	
