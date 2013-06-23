import thread
import threading
import time
import sys
import datetime
import logging
	
global ctr

class PingPongThreadClass(threading.Thread):
	"""Thread class with a stop() method. The thread itself has to check
	regularly for the stopped() condition."""
	def __init__(self):
		threading.Thread.__init__(self)
		self._stop = threading.Event()
		#self.ctr = ctr
	
	def stop(self):
		self._stop.set()

	def stopped(self):
		return self._stop.isSet()
		
	def run(self):
		interval = 1;
		time.sleep(interval)
		while True :
			# see if we're stopped. if so exit the thread.
			if self.stopped():
				logging.debug("%s We were asked to stop ping ponging thread. Exiting it." % self.getName())
				break
			global ctr
			logging.info("Ctr is at: %s" % ctr)
			time.sleep(interval)
