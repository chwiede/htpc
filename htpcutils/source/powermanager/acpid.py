#!/usr/bin/python2

# Import sytem, deny output of bytecode
import sys
sys.dont_write_bytecode = True

# imports
import time
import socket
from thread import start_new_thread


class Acpid():
	
	Listen = False
	

	def Stop(self):
		self.Listen = False


	def Listen(self, callback):
		self.Listen = True

		def AsyncSocketListener():	
			while(self.Listen):
				sck = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
				sck.connect("/var/run/acpid.socket")
				socketResult = sck.recv(4096)
				callback(socketResult)
			
		start_new_thread(AsyncSocketListener, ())



# Test Mode			
if (__name__ == '__main__'):
	def testCallback(data):
		print "via callback: ", data

	acpid = Acpid()
	acpid.Listen(testCallback)

	print "Raise an acpid-action, eg louder/mute, or power btn."
	print "Press CTRL+C to exit."

	try:
		time.sleep(300)
	except:
		exit()
