import websocket
import thread
import threading
import time
import sys
import datetime
import zwwebsocketpingpong
import logging
import json

'''
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()
'''
logger = logging.getLogger('zwwebsocket')

traceEnabled = True

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
        logger.setLevel(logging.INFO)
	'''
	
class ZwWebSocket:
	def __init__(self, showframes = True,  
				clientid = None, sessionid = None,
				on_new_message = None, on_new_signal = None, on_new_read = None,
				on_new_contact = None, on_new_conversation = None):
		# define global
		#self.pingPongThread = 0
		
		logger = logging.getLogger("zwwebsocket")
		logger.setLevel(logging.DEBUG)
		formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
		handler = logging.FileHandler("/opt/zipwhip/log/zipwhip-textspresso.log")
		handler.setFormatter(formatter)
		logger.addHandler(handler)
		
		self.clientid = clientid
		logger.info("ClientId=%s" % clientid)
		self.sessionid = sessionid
		if self.clientid == None:
			logger.error("You must provide a clientid to connect to the Zipwhip network.")
			sys.exit(1)
		self.host = "ws://push.zipwhip.com:443/socket.io/1/websocket/" + self.clientid
		self.showframes = showframes
		self.on_new_message = on_new_message
		self.on_new_signal = on_new_signal
		
	def on_message(self, ws, message):
		if traceEnabled:
			logger.debug("Message:\n")
		if self.showframes :
			logger.info(message)
		if message == "1::" :
			time.sleep(2)
			if traceEnabled:
				logger.debug("Sending:\n")
			str = '3:::{"clientId":"' + self.clientid + '","presence":{"category":"Browser","userAgent":{"makeModel":"Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.52 Safari/537.17","build":"zipwhip-textspresso-v2","product":{"name":"RASPI","version":"0.2","build":"zipwhip-textspresso"}},"status":"ONLINE","extraInfo":{"browserLocation":"http://zipwhip.com"}},"action":"CONNECT","class":"com.zipwhip.api.signals.commands.ConnectCommand"}'
			#str += "\n"
			if self.showframes :
				logger.info(str)
			#time.sleep(100)
			ws.send(str)
			time.sleep(2)
			if traceEnabled:
				logger.debug("Sending:\n")
			str = "6:::0"
			if self.showframes :
				logger.info(str)
			ws.send(str)
			#ws.send("")
		else :
			# decode json
			# we have a prefix we have to drop. usually it is of form
			# 4:1::{
			# or some other number
			indx = message.find("{")
			#print "indx was: %s" % indx
			if indx > 0 :
				# it had a prefix. it's good
				msg = message[indx:]
				#print "after stripping\n"
				#print msg
				j = json.loads(msg)
				#print j
				#print json.dumps(j, sort_keys=True,
				#	indent=4, separators=(',', ': '))
				# call the callback we were given and pass json object
				# see what type first
				if j["action"] == "SIGNAL" :
					if j["signal"]["type"] == "message" :
						self._run_with_no_err(self.on_new_message, j)
					elif j["signal"]["type"] == "conversation" :
						self._run_with_no_err(self.on_new_conversation, j)
					else :
						self._run_with_no_err(self.on_new_signal, j)
			else :
				print "Got message but didn't have format we expected. Ignoring..."
	
	def on_error(self, ws, error):
	    print error
	
	def on_close(self, ws):
		logger.info("### got socket closed ###")
		# kill ping/pong thread
		logger.info( "Shutting down ping pong thread.")
		self.pingPongThread.stop()
		# reconnect on a delay
		#self.delay_reconnect()
		#print "At end of on_close method. Exiting..."
	
	def on_open(self, ws):
		if traceEnabled:
			logger.debug("Got into on_open")
		def run(*args):
			logger.debug("Inside run so thread started. Going to start pingpong thread.")
			self = args[0]
			ws = args[1]
			#global self.pingPongThread
			#print "Args:"
			#print args
			#for i in range(2):
			#	print "got on_open args[i]: "
			#	print args[i]
			#time.sleep(1)
			#ws.close()
			#print "Thread terminating..."
			# start my ping/pong
			zwwebsocketpingpong.enableTrace(traceEnabled)
			self.pingPongThread = zwwebsocketpingpong.PingPongThreadClass(ws)
			self.pingPongThread.setDaemon(True)
			self.pingPongThread.start()
			logger.debug("Ok, at end of run(). Done here.")
			
		if traceEnabled:
			logger.debug("Just about to start a new thread")
		thread.start_new_thread(run, (self, ws))
		if traceEnabled:
			logger.debug("Got to end of on_open method.")

	def delay_reconnect(self):
		logger.info("Got disconnected. Reconnecting in 10 seconds.")
		self.delay_recon_thread = threading.Timer(10.0, self.reconnect)
		self.delay_recon_thread.start() # after 10 seconds, reconnect will be run
		
	def reconnect(self):
		logger.info("Reconnecting...")
		#self.connect()
		#self.ws.run_forever()
	
	def disconnect_me(self):
		#global pingPongThread
		#print "artificially disconnecting"
		#ws.close()
		print "artificially stopping ping pongs"
		#self.pingPongThread.stop()
	
	def start_artifical_disconnect_timer(self):
		# setup an artificial disconnect to see if we reconnect
		self.t = threading.Timer(10.0, self.disconnect_me)
		self.t.start() # after 30 seconds, disconnect_me will be run
	
	def connect(self):
		self.ws = websocket.WebSocketApp(self.host,
	                                on_message = self.on_message,
	                                on_error = self.on_error,
	                                on_close = self.on_close)
		self.ws.on_open = self.on_open
		self.ws.run_forever()
		# if we get here, close ourself
		
	def _run_with_no_err(self, callback, *args):
		if callback:
			try:
				callback(self, *args)
			except Exception, e:
				if logger.isEnabledFor(logging.DEBUG):
					logger.error(e)
						
'''
def on_new_msg(caller, jsn):
	print "Got on_new_msg"
	if jsn["signal"]["event"] == "receive" :
		print json.dumps(jsn, sort_keys=True,
			indent=4, separators=(',', ': '))

def on_new_sig(caller, jsn):
	print "Got on_new_sig"
	print jsn
'''

if __name__ == "__main__":
	#websocket.enableTrace(True)
	if len(sys.argv) < 2:
		pass
	else:
		host = sys.argv[1]
	#enableTrace(True)
	while True:
		zwclient = ZwWebSocket()
		zwclient.on_new_message = on_new_msg
		#zwclient.on_new_signal = on_new_sig
		zwclient.connect()
		print "Reconnecting in 10 seconds"
		time.sleep(10)
	print "Got past zwclient.connect() final stmt."
