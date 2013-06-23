#!/usr/bin/python -O
#
# Zipwhip Twiiter Search Utility

import urllib
import urllib2
import logging
import json

class ZwTwitter:
	
	def __init__(self):
		logger = logging.getLogger("zwtwitter")
		logger.setLevel(logging.DEBUG)
		formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
		handler = logging.FileHandler("/opt/zipwhip/log/zipwhip-textspresso.log")
		handler.setFormatter(formatter)
		logger.addHandler(handler)
		self.log = logger
		#logging.basicConfig(level=logging.INFO)
		#self.log = logging.getLogger("zwtwitter")
	
	def search(self, query):
		
		self.log.info("Going to search Twitter for query: %s" % query)
		url = 'http://search.twitter.com/search.json?q=' + query
		#url = urllib.urlencode(url)
		self.log.info("Hitting URL: %s" % url)
		req = urllib2.Request(url)
		response = urllib2.urlopen(req)
		the_page = response.read()
		#self.log.info("Response: %s" % the_page)
		
		# decode json
		j = json.loads(the_page)
		txt = j['results'][1]['text']
		#self.log.info(txt)
		#self.log.info("Len: %s" % len(txt))
		
		listTweets = []
		for tweet in j['results']:
			listTweets.append(tweet['text'])
		self.log.info(listTweets)
		return listTweets		
		
def test():
	
	zt = ZwTwitter()
	zt.search("Zipwhip")

#test()