#!/usr/bin/python2

import time
import subprocess


def Start(cmd):
    # simply start process and return popen-object
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def GetReturncode(cmd):
    # start process, get popen object
    proc = Start(cmd)
    
    # wait until polling finished
    while (proc.poll() == None):
        time.sleep(0.05)
    
    # return returncode
    return proc.returncode


def GetOutput(cmd):
    # start process, get popen object
    proc = Start(cmd)

    # wait until polling finished
    while proc.poll() == None:
        time.sleep(0.05)

    #return proc out-value or error-messages due to return code
    if(proc.returncode == 0):
        return proc.stdout.read().strip()
    else:
        return proc.stderr.read().strip()
