#!/usr/bin/python2

# Import sytem, deny output of bytecode
import sys
sys.dont_write_bytecode = True

# imports
import os
import time
import subprocess
import commands
from thread import start_new_thread


def Start(cmd):
	return subprocess.Popen(cmd, shell=True)


def StartWithCallback(cmd, exitCallback):
	def StartAsync():
		proc = subprocess.Popen(cmd, shell=True)
		proc.wait()
		exitCallback(proc)
		
	start_new_thread(StartAsync, ())


def WaitFor(name, timeout = 10):
	now = time.time()
	while(GetPid(name) == 0):
		time.sleep(0.25)
		if(time.time() - now > timeout):
			return False

	return True



def Kill(name, wait = True):
	pid = GetPid(name)
	os.system("kill %s" % pid)
		
	while(wait and GetPid(name) != 0):
		time.sleep(0.25)



def GetProcessIsActive(name):
	pid = GetPid(name)
	return pid != 0



def GetPid(name):
	pid = commands.getoutput("pidof %s" % name)
	return 0 if (pid == None or pid == '') else pid



