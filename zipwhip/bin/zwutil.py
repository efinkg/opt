from time import sleep
from array import *
import sys
import logging
import json
#from json import load
from urllib2 import urlopen
import time
import re
import urllib
import urllib2

class ZwUtil:
	
	def __init__(self, 
				logger = None,
				conf = None,
				):
		# define properties
		# define properties
		if (logger == None):
			logger = logging.getLogger("zwutil")
			logger.setLevel(logging.DEBUG)
			formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
			handler = logging.FileHandler("/opt/zipwhip/log/zipwhip-textspresso.log")
			handler.setFormatter(formatter)
			logger.addHandler(handler)
			self.log = logger
		else:
			self.log = logger
			
		self.conf = conf

	def getSessionId(self):
		
		sessionid = ""
		
		# get session id from username/password
		self.log.info("Getting sessionid for user: %s, pass: %s" % 
			(self.conf.phonenum, self.conf.password))
		
		url = 'http://network.zipwhip.com/user/login'
		values = {"userName" : self.conf.phonenum,
				"mobileNumber" : self.conf.phonenum,
				"password" : self.conf.password,
				"remember" : "false"
				}
	
		data = urllib.urlencode(values)
		self.log.info("Sending POST data to url: " + url)
		req = urllib2.Request(url, data)
		response = urllib2.urlopen(req)
		the_page = response.read()
		#content = the_page
		self.log.info("Response: %s" % the_page)
		j = json.loads(the_page)
		self.log.info(j)
		sessionid = j['response']
		self.log.info("The new sessionid is: %s" % sessionid)
		
		return sessionid
		
	def getClientId(self):
		
		clientid = ""
		
		# get session id from username/password
		self.log.info("Getting clientid for sessionid: %s" % 
			(self.conf.sessionid))
		
		url = 'http://push.zipwhip.com:443/socket.io/1/?t=1364165545096'
	
		# we'll get a response from the websocket server like this:
		# 213586793448674424:1680:1800:websocket,xhr-polling,rawsocket
		# so just regex to grab new clientid
		self.log.info("Sending GET regquest to url: " + url)
		req = urllib2.Request(url)
		response = urllib2.urlopen(req)
		the_page = response.read()
		self.log.info("Response: %s" % the_page)
		
		m = re.search( r'^(.*?):', the_page, re.M|re.I)
		if (m):
			clientid = m.group(1)

		self.log.info("The new clientid is: %s" % clientid)
		
		return clientid

	def getConnectSessionIdToClientId(self):
		
		result = ""
		
		# get session id from username/password
		self.log.info("Connecting sessiondid to clientid for clientid: %s, sessionid: %s" % 
			(self.conf.clientid, self.conf.sessionid))
		
		url = 'http://network.zipwhip.com/signals/connect'
		values = {"clientId" : self.conf.clientid,
				"sessions" : self.conf.sessionid,
				}
	
		data = urllib.urlencode(values)
		self.log.info("Sending POST data to url: " + url)
		req = urllib2.Request(url, data)
		response = urllib2.urlopen(req)
		the_page = response.read()
		#content = the_page
		self.log.info("Response: %s" % the_page)
		j = json.loads(the_page)
		self.log.info(j)
		result = j['response']
		self.log.info("The result of signals/connect is: %s" % result)
		
		return result

def test():
	log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
	logging.basicConfig(format=log_format, level=logging.INFO)
	import zwconfig
	zwconf = zwconfig.ZwConfig()
	zwutil = ZwUtil(conf=zwconf)
	sessionid = zwutil.getSessionId()
	zwconf.sessionid = sessionid
	clientid = zwutil.getClientId()
	zwconf.clientid = clientid
	result = zwutil.getConnectSessionIdToClientId()
	logging.info("Final results. sessionid: %s, clientid: %s, connectResult: %s" %
		(sessionid, clientid, result))
	#zwconf.printVals()
	zwconf.write()
	zwconf.printVals()
	
#test()