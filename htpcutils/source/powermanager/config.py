#!/usr/bin/python2

# Import sytem, deny output of bytecode
import sys
sys.dont_write_bytecode = True

# imports
import ConfigParser

# load config, set variables
configParser = ConfigParser.ConfigParser()
configParser.read(['/etc/htpcutils/htpc.conf'])

DVR_LOG_PATH = configParser.get('paths', 'dvr_log_path')
RTC_PERSISTENT = configParser.get('paths', 'rtc_persistent')
RTC_DEVICE = configParser.get('paths', 'rtc_device')
CMD_SHUTDOWN = configParser.get('paths', 'shutdown')
CMD_FRONTEND = configParser.get('paths', 'frontend')
PROC_FRONTEND = configParser.get('paths', 'frontend_proc')

BOOT_TIME = float(configParser.get('times', 'boot_time'))
POLL_TIME = float(configParser.get('times', 'poll_time'))
WAKE_BEFORE = float(configParser.get('times', 'wake_up_before'))
RECORD_BRIDGE = max(300, float(configParser.get('times', 'record_bridge')) * 60.0)

FRONTEND_RESTART = configParser.get('misc', 'frontend_restart') == '1' 
