#!/usr/bin/python -O
#
# Zipwhip Send Utility

import urllib
import urllib2
import logging

# SETUP YOUR SESSION KEY
# You need to grab this from your web browser when logged into Zipwhip
# You can use firebug to watch the network traffic and then cut & paste the session id
# Open Chrome. Hit F12. Click Network tab in Firebug/Dev Console
# Look at any of the AJAX calls and you'll see a "sessions=" parameter
# Grab the key after sessions= and paste it in here
# Don't use the URL Encoded version with the %3A for the colon. We URL encode in this script.
# Example session key. Change to yours.
SESSIONID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee:11111111"

class Zipwhip:
	
	def __init__(self):
		logging.basicConfig(level=logging.INFO)
		self.log = logging.getLogger("Zipwhip")
	
	def sendMsg(self, to, msg):
		
		self.log.info("About to send msg to: %s, msg: %s" % (to, msg))
		
		# check length of msg as a last attempt
		if (len(msg) > 160):
			msg = msg.data[:157] + '...'
		
		url = 'http://network.zipwhip.com/message/send'
		values = {"session" : SESSIONID,
				"contacts" : to,
				"body" : msg,
				"fromAddress" : "0",
				"fromName" : "",
				"scheduledDate" : "-1" }
	
		data = urllib.urlencode(values)
		self.log.info("Sending POST data to url: " + url)
		req = urllib2.Request(url, data)
		response = urllib2.urlopen(req)
		the_page = response.read()
		self.log.info("Response: %s" % the_page)

