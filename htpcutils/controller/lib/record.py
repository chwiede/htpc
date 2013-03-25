#!/usr/bin/python2

import os
import sys
import time
import json
import datetime

class Record():
    Title = ""
    TimeBegin = 0
    TimeEnd = 0
    ErrorCode = 0
    IsRunning = False    
    
    
def GetRecords(folder):
    # define result list
    result = []
    
    # no folder? return empty list
    if (not os.path.isdir(folder)):
        return result

    # Loop through the folders files, and read as json
    # Append a new record-object to result list
    for fl in os.listdir(folder):
        filePath = os.path.join(folder, fl)
        result.append(GetRecord(filePath))

    # give out result list
    return result



def GetRecord(filepath):
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



def GetActiveRecords(records):
    # count running records
    result = 0        
    for record in records:
        if(record.IsRunning):
            result += 1
    
    # give out
    return result
    
    
    
def GetNextRecord(records):
    # loop through, find next
    result = None
    tsNow = time.time()
    tsNext = sys.maxint
    
    for rec in records:
        if(rec.TimeBegin > tsNow and rec.TimeBegin < tsNext):
            tsNext = rec.TimeBegin
            result = rec

    return result    


if (__name__ == '__main__'):
    # list records, sorted by time begin
    print 'Known Records (planned, done and error):\n'
    records = GetRecords('/home/hts/.hts/tvheadend/dvr/log')
    records = sorted(records, key=lambda rec: rec.TimeBegin)

    for rec in records:
        print '"%s" %s\n%s - %s\n' % (
            rec.Title,
            '*' if rec.IsRunning else '',
            datetime.datetime.fromtimestamp(rec.TimeBegin),
            datetime.datetime.fromtimestamp(rec.TimeEnd)
        )
        
    rec = GetNextRecord(records)
    if(rec != None):
        print 'about %s minutes to next record: "%s"' % (
            int((rec.TimeBegin - time.time()) / 60),
            rec.Title
        )
        
