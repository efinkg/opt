import websocket
import thread
import threading
import time
import sys
import datetime
import logging

#logger = logging.getLogger('zwwebsocketpingpong')

traceEnabled = False

def enableTrace(tracable):
    """
    turn on/off the tracability.

    tracable: boolean value. if set True, tracability is enabled.
    """
    '''
    global traceEnabled
    traceEnabled = tracable
    if tracable:
        if not logger.handlers:
            logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)
	'''
	
class PingPongThreadClass(threading.Thread):
	"""Thread class with a stop() method. The thread itself has to check
	regularly for the stopped() condition."""
	def __init__(self, ws):

		logger = logging.getLogger("zwwebsocketpingpong")
		logger.setLevel(logging.DEBUG)
		formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
		handler = logging.FileHandler("/opt/zipwhip/log/zipwhip-textspresso.log")
		handler.setFormatter(formatter)
		logger.addHandler(handler)
		self.log = logger
		
		threading.Thread.__init__(self)
		#self.name = "Thread-PingPong"
		self.myws = ws
		self._stop = threading.Event()
	
	def stop(self):
		self._stop.set()

	def stopped(self):
		return self._stop.isSet()
		
	def run(self):
		pingPongIterval = 60 * 3;
		if traceEnabled:
			self.log.debug("%s Just started ping/pong thread. Will ping/pong every %s secs." % (self.getName(), pingPongIterval))
		time.sleep(pingPongIterval)
		while True :
			# see if we're stopped. if so exit the thread.
			if self.stopped():
				if traceEnabled:
					self.log.debug("%s We were asked to stop ping ponging thread. Exiting it." % self.getName())
				break
			if self.myws:
				str = "3:::ping"
				self.log.info(str)
				self.myws.send(str)
				now = datetime.datetime.now()
				if traceEnabled:
					self.log.debug("%s Just did a ping/pong: %s" % (self.getName(), now))
			else:
				self.log.error("The websocket seems to be null. Can't ping. Huh?")
			time.sleep(pingPongIterval)
