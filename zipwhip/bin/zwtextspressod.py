#This has been reworked to initialize an existing automatic french press.
#See code in MakeCoffee.py and coffeetimethreading.py

import pdb

# Standard imports
import signal
import os
import sys
import json
import time
import logging
import re
import urllib
import urllib2
import daemon
import lockfile
import threading
from coffeetimethreading import CoffeeMaker

coffee_maker = CoffeeMaker()

# Third party libs
from daemon import runner

class App():
    
	def __init__(self, logger=None):
		self.stdin_path = '/dev/null'
		self.stdout_path = '/opt/zipwhip/log/zipwhip-textspresso.daemon_stdout'
		self.stderr_path = '/opt/zipwhip/log/zipwhip-textspresso.daemon_stderr'
		self.pidfile_path =  '/var/run/zipwhip-textspresso.pid'
		self.pidfile_timeout = 5
		
		self.log = logger
		
		# our global queue of previous commands
		self.pastcmds = []
	    
	def run(self):
		
		# Import other Zipwhip libraries
		import zwwebsocket
		import zwconfig
		import zwsendbtncmds
		import zwmsghandler
		import zwreadstate
		import zwsqlstats
		
		self.stats = zwsqlstats.ZwStats()
		
		# get our config info. this is a config file that contains
		# acct phone number, acct name, sessionid, clientid, etc
		self.conf = zwconfig.ZwConfig(logger=logger)
		
		# create our msg handler object for parsing, composing
		self.zwmsg = zwmsghandler.ZwMsgHandler(stats=self.stats, conf=self.conf)
		
		# get our obj to send button commands
		# btw, this turns on GPIO 9 and 10 to HIGH which is critical
		# to do as QUICKLY as possible or the Espresso machine thinks
		# all 4 buttons are being pressed at the start including on/off and coffee
		self.sendbtncmds = zwsendbtncmds.ZwSendBtnCmds()
		
		# get our obj to read the LED state
		self.ledstate = zwreadstate.ZwReadState()
		
		zwclient = zwwebsocket.ZwWebSocket(showframes=True, sessionid=self.conf.sessionid, clientid=self.conf.clientid)
		zwclient.on_new_message = self.on_new_msg

		while True:
			#Main code goes here ...

			#print "In main program while loop"
			self.log.info("In main program loop. Starting socket connection to Zipwhip.")
			self.log.info("Connecting to Zipwhip for account phone number %s" % self.conf.phonenum)
			zwclient.connect()
				
			# if we get here, we need to cleanup all threads that zwclient created
			# so when we loop we don't have multiple threads being created
			
			self.log.info("Reconnecting in 10 seconds")
			time.sleep(10)
			
			#Note that logger level needs to be set to logging.DEBUG before this shows up in the logs 
			self.log.debug("Debug message") 
			self.log.info("Info message") 
			self.log.warn("Warning message")
			self.log.error("Error message")
			time.sleep(10)
			
	def on_new_msg(self, caller, jsn):

		self.log.info("I got myself an on_new_msg")
		
		if jsn["signal"]["event"] == "receive" :
			
			self.log.info(json.dumps(jsn, sort_keys=True,
				indent=4, separators=(',', ': ')))
			body = jsn["signal"]["content"]["body"]
			addr = jsn["signal"]["content"]["address"]
			fname = jsn["signal"]["content"]["firstName"]
			lname = jsn["signal"]["content"]["lastName"]

			#pdb.set_trace()
			
			# use our handy utility to parse to a cmd
			# RETURNS: coffee, coffeeSingle, coffeeTriple, water, decalcify, help, stop, menu, off, on, status
			cmd = self.zwmsg.parseMsg(body)
			self.log.info("Cmd back in main Textspresso loop: " + cmd)
			
	
			elif (cmd == "halt"):
				msg = "I hope this means you accidentally sent a message since coffee is awesome."
				self.zwmsg.sendMsg(addr, msg)
				coffee_maker.force_stop()
                                print 'done force stopping'

			elif (cmd == "caffeine"):

				msg = "I am making you a cup of coffee."
				self.zwmsg.sendMsg(addr, msg)
				coffee_maker.makeCoffee(16)
				print 'Making your coffee.  Like a Boss.'

				
			# push onto the queue what our last command was, just to have a record
			self.pastcmds.append({"cmd":cmd,"addr":addr,"fname":fname,"lname":lname,"time":time.strftime('%Y-%m-%d %H:%M:%S')})
			self.log.info("Pastcmds storage list:")
			self.log.info(self.pastcmds)
			
		else :
			self.log.info("It was a msg of \"event\":\"%s\"" % jsn["signal"]["event"])


	def sendCoffee(self, cmd, fname):
		#pdb.set_trace()
		self.log.info("Inside sendCoffee. Going to analyze if machine is off.")
		
		# This will send the coffee command
		# first of all, see if machine is off. if so, turn it on.
		isOff = self.ledstate.analyzeIsMachineOff()
		# we can call this cuz we just did an analysis
		#isOff = self.ledstate.isMachineOff()
		#self.ledstate.startReadingState()
		#self.ledstate.printData()
		#self.ledstate.analyzeData()
		#isOff = isMachineOff()
		self.log.info("Done analyzing if machine is off. isOff: %s" % isOff)
			
	def on_new_sig(self, caller, jsn):
		self.log.info("Got on_new_sig")
		self.log.info(jsn)
	
	

logger = logging.getLogger("zwtextspressod")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler("/opt/zipwhip/log/zipwhip-textspresso.log")
handler.setFormatter(formatter)
logger.addHandler(handler)
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)

app = App(logger=logger)
#app.run()

daemon_runner = runner.DaemonRunner(app)

#This ensures that the logger file handle does not get closed during daemonization
daemon_runner.daemon_context.files_preserve=[handler.stream]
daemon_runner.do_action()

# This never gets hit cuz main daemon run() blocks
print "Exiting Zipwhip Textspresso Daemon..."

