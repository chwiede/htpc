#!/usr/bin/python2

# imports
import ConfigParser

# load config, set variables
configParser = ConfigParser.ConfigParser()
configParser.read(['/etc/htpcutils/htpc.conf'])

DVR_FOLDER = configParser.get('common', 'dvr_folder')
RTC_PERSISTENT = configParser.get('common', 'rtc_persistent')
RTC_DEVICE = configParser.get('common', 'rtc_device')

CMD_SHUTDOWN = configParser.get('common', 'cmd_shutdown')

WAIT_FOR_DISPLAY = configParser.get('common', 'wait_for_display')

MODE_RECORD_START = configParser.get('modes', 'mode_record_start')
MODE_RECORD_STOP = configParser.get('modes', 'mode_record_stop')
MODE_WATCH_START = configParser.get('modes', 'mode_watch_start') 
MODE_WATCH_STOP = configParser.get('modes', 'mode_watch_stop')

WAKE_BEFORE = float(configParser.get('times', 'wake_before'))
RECORD_BRIDGE = float(configParser.get('times', 'record_bridge')) * 60

