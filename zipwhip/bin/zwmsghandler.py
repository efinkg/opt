from time import sleep
from array import *
import sys
import logging
import json
from json import load
from urllib2 import urlopen
import time
import re
import urllib
import urllib2
from random import choice
import zwtwitter
import zwconfig

class ZwMsgHandler:
	
	def __init__(self, 
				logger = None,
				conf = None,
				stats = None,
				clientid = None, sessionid = None,
				):
		# define properties
		# define properties
		if (logger == None):
			logger = logging.getLogger("zwmsghandler")
			logger.setLevel(logging.DEBUG)
			formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
			handler = logging.FileHandler("/opt/zipwhip/log/zipwhip-textspresso.log")
			handler.setFormatter(formatter)
			logger.addHandler(handler)
			self.log = logger
		else:
			self.log = logger
			
		self.conf = conf
		self.stats = stats

	def humanize_time(self, secs):
		mins, secs = divmod(secs, 60)
		if (secs == 0):
			ret = "%s min" % mins
			if (secs > 1):
				ret += "s"
		elif (mins == 0):
			ret = "%s secs" % secs
		else:
			ret = "%sm %ss" % (mins, secs)
		return ret
    
	def createMsg(self, cmd, addr, fname, lname):
		
		# send back msg that we are about to vend and how long it'll take
		# do some other creative stuff as well like:
		# 	if first time ordering, thank them and tell them about the "pay it forward"
		#	if 3rd time ordering say, "just a friendly reminder it's always nice to put an empty cup on the machine for the next guy"
		#	if 10th time ordering, say "you must be really enjoying texting for your coffee"
		#   if they were top (2nd, 3rd) drinker yesterday, let them know
		#	if it's Monday, say "Happy Monday"
		#	if it's Monday, say "You were the top 3rd coffee drinker last week"
		#	if it's Friday, say "TGIF. Enjoy your weekend."
		#	if it's Wed, say "Enjoy hump day."
		#	if it's Sat/Sun say "Why are you working on the weekend?"
		#	if it's been more than 7 days not ordering, say "we missed you"
		#	if it's their 3rd cup today say "wow, 3rd cup today, you must need a pick me up"
		#	if it's after 4pm say, "hey, not too much coffee in the afternoon, you wanna wind down towards end of day"
		#	if 1st cup of day and before 10am say, "Good morning. Enjoy your 1st cup of Joe."
		#	if significant date, say "Happy St. Patrick's Day" or other
		#	perhaps randomly give the local temperature
		#	perhaps randomly give weather forecast
		#	perhaps give a news clip of the day
		#	if have ordered more than one > 1hr later and then another > 1hr later but total less then 3, say "wow, 3 coffees in 3 hours, you must have had a hard night"

		self.log.info("inside create msg")
		# contains our msg we composed
		msg = ""
		
		# ok, see if they've ordered before
		numTotal = self.stats.getNumOrdersTotal(addr)

		drink = "coffee"
		if (cmd == "coffeeSingle"):
			drink = "coffee single"
		if (cmd == "coffeeTriple"):
			drink = "\"Zipwhip\""
		if (cmd == "water"):
			drink = "hot water"
		if (cmd == "decalcify"):
			drink = "decalcify"
			
		# 1st order
		if (numTotal == 0):
			# user has never ordered before. welcome them.
			msg = "Hi %s, welcome to Zipwhip's Textspresso showcasing the power of Zipwhip Landline Texting. We see this is your 1st order. Congrats and enjoy!" % fname
			if (len(msg) > 160 or len(fname) <= 0):
				msg = "Welcome to Zipwhip's Textspresso showcasing the power of Zipwhip Landline Texting and what u can do when u move texting 2 the cloud. Ur 1st order is coming up!"

		# 2nd order
		if (numTotal == 1):
			msg = "%s, your %s order is on its way. As a courtesy, after you get ur order, it's always nice to put an empty cup under the nozzles for the next guy." % (fname, drink)
			if (len(msg) > 160 or len(fname) <= 0):
				msg = "Your %s order is on its way. As a courtesy, after you get ur order, it's always nice to put an empty cup under the nozzles for the next guy." % drink

		# 3rd order
		if (numTotal == 2):
			if (len(fname) > 0):
				if (cmd == "coffee"):
					msg = "%s, we're whipping up ur coffee. Did you know it takes about 1.5 mins for me to make ur yummy coffee." % fname
				if (cmd == "coffeeSingle"):
					msg = "%s, we're whipping up ur coffee single. Did you know it takes about 1 min for me to make ur coffee single." % fname
				if (cmd == "coffeeTriple"):
					msg = "%s, we're whipping up ur \"Zipwhip\" triple shot. Did you know it takes about 3.5 mins for me to make ever-so-special Zipwhip vend." % fname
				if (cmd == "water"):
					msg = "%s, we're whipping up ur hot water. Did you know it takes about 40 seconds for me to vend your steaming hot water." % fname
			else:
				if (cmd == "coffee"):
					msg = "We're whipping up ur coffee. Did you know it takes about 1.5 mins for me to make ur yummy coffee."
				if (cmd == "coffeeSingle"):
					msg = "We're whipping up ur coffee single. Did you know it takes about 1 min for me to make ur coffee."
				if (cmd == "coffeeTriple"):
					msg = "We're whipping up ur \"Zipwhip\" triple shot. Did you know it takes about 3.5 mins for me to make ever-so-special Zipwhip vend." % fname
				if (cmd == "water"):
					msg = "We're whipping up ur hot water. Did you know it takes about 40 seconds for me to vend your steaming hot water."
		
		# 4th order
		if (numTotal == 3):
			if (len(fname) > 0):
				msg = "%s, making your %s now. Did you know I'm tied to a landline that's text-enabled by Zipwhip. Did you notice how fast the texts are?" % (fname, drink)
			if (len(fname) <= 0 or len(msg) > 160):
				msg = "I'm making your %s now. Did you know I'm tied to a landline that's text-enabled by Zipwhip. Did you notice how fast the texts are?"
		
		# 5th order
		if (numTotal == 4):
			if (len(fname) > 0):
				msg = "%s, I'll whip up your %s immediately. This is ur 5th order, you must be enjoying your beverages. Isn't the marriage of cloud texting to a coffee machine awesome?" % (fname, drink)
			if (len(fname) <= 0 or len(msg) > 160):
				msg = "I'll whip up your %s immediately. This is ur 5th order, you must be enjoying your beverages. Isn't the marriage of cloud texting to a coffee machine awesome?" % drink

		# 6th order
		if (numTotal == 5):
			if (len(fname) > 0):
				msg = "%s, %s coming up. If you've got an Android phone, put the Zipwhip app on it from Google Play Store so u can text me from ur desktop." % (fname, drink)
			if (len(fname) <= 0 or len(msg) > 160):
				msg = "Coming up, 1 %s. If you've got an Android phone, put the Zipwhip app on it from Google Play Store so u can text me from ur desktop." % drink

		# 7th order
		if (numTotal == 6):
			if (len(fname) > 0):
				msg = "%s, a %s is being whipped up lickety split. Why not have Zipwhip text-enable your desk landline phone? Then u could text from there as well." % (fname, drink)
			if (len(fname) <= 0 or len(msg) > 160):
				msg = "A %s is being whipped up lickety split. Why not have Zipwhip text-enable your desk landline phone? Then u could text from there as well." % drink

		if (len(msg) <= 0):
			# default msg
			tagline = ["My amazing text capabilities are brought to you by Zipwhip cloud texting.",
				"Made possible by Zipwhip landline texting.",
				"Your hot drink brought to you by the cool folks at Zipwhip.",
				"Zipwhip cloud texting changes everything.",
				"Did you know texting is the most ubiquitous whip-fast medium in the world? Why doesn't somebody move it to the cloud? Oh, Zipwhip did.",
				"Your text order made possible thru Zipwhip's revolutionary landline texting.",
				"Why didn't anybody text-enable landlines before this? Thank god Zipwhip came along.",
				"BTW, isn't texting in an order cool? Gotta love the savvy folks at Zipwhip.",
				"From a philosophical standpoint, isn't speaking to your machines via texting pretty cool?",
				"Did you grab the Zipwhip Android app yet so u can text me from your laptop?",
				"Are you texting me from your desktop or tablet yet? If not, go get Zipwhip on ur Android phone in the Google Play Store.",
				"U should text me from your desktop, but if u have an iPhone, sorry. That's a closed OS. Can't do the magic of Zipwhip on it.",
				"There's 146M landlines and 300M mobile phones in the U.S. The 2 sides have never been able to text eachother. Zipwhip solved that.",
				"Landlines have never been able to text mobile phones in the U.S. until now. Zipwhip solved the tower of babel between the two.",
				"Do you know what cloud texting is? It means texting is finally available on all of your devices--not just stuck on your phone.",
				"If u can get your emails on your desktop, laptop, tablet, and phone, why can't u with texts? Zipwhip's cloud texting solves it.",
				"Obviously u just texted me, but my guess is this is the first machine u've ever talked to via texting.",
				"Did u know I'm powered by a Raspberry Pi and a custom circuit board designed by the brainiacs at Zipwhip?",
				"Did u know that I login to the Zipwhip network to monitor my text messages the same way u login to the Zipwhip web app?",
				"Have you text-enabled your landline yet? You should. It'll make you live longer.",
				"So, have you asked the folks at your hair salon/barber if they've text-enabled their landline yet via Zipwhip?",
				"Next time you make a reservation at a restaurant, ask them if they can text you the confirmation on their landline!",
				"When you order a pizza this weekend, ask your pizza joint if you can start texting in your order to their landline.",
				"Why can't you text for a taxi? Next time u order up a taxi, ask them to Zipwhip-enable their landline so u can.",
				"Why doesn't the dry cleaner text you on their landline when your clothes are ready or if u forget to pick them up?",
				"Ask your dentist next time ur in there if they can text u appt reminders instead of calling u.",
				"Did you know that 40% of voicemails aren't listened to, but 94% of texts are read within 5 minutes. Texting rocks.",
				"Texting is so ubiquitous, especially in the U.S., that it's here to stay forever. So why not text-enable everything.",
				"Next time u call in your Chinese food order, ask them if u can text them instead. Tell 'em to get Zipwhip on their landline."
				]
			
			# generate some stats-based taglines
			num =  self.stats.getNumOrdersGlobal()
			taglinestats = ["Did u know that I've vended over %s coffees since u got me?" % num]
			
			num = self.stats.getNumOrdersGlobalThisWeek()
			if (num >= 10):
				taglinestats.append("Did u know that I've vended over %s coffees this week? Good thing I have caffeine to keep me going as well." % num)
			
			num = self.stats.getNumOrdersGlobalLastWeek()
			if (num >= 10):
				taglinestats.append("Did u know that I dispensed %s coffees last week? What a grind it was." % num)
				
			num = self.stats.getNumOrdersGlobalToday()
			if (num >= 5):
				taglinestats.append("I've had %s orders today already. U guys are working hard. Fortunately my cloud texting isn't breaking a sweat." % num)
	
			num = self.stats.getNumOrdersGlobalYest()
			if (num >= 5):
				taglinestats.append("Yesterday I had %s orders. What would u have done w/out Zipwhip powering me? Push a button on my front panel instead?!?" % num)
	
			num = self.stats.getNumOrdersThisWeek(addr)
			if (num >= 3):
				taglinestats.append("You've ordered %s drinks this week. Glad ur enjoying my fancy brews. Hope ur enjoying the landline texting speeds as well." % num)
	
			num = self.stats.getNumOrdersLastWeek(addr)
			if (num >= 3):
				taglinestats.append("You whipped up %s drinks last week. Nice work. Isn't texting ur espresso machine fun? Did u know ur texting a landline?" % num)
			
			# append weather choice, but wait to load so we don't hit this every time
			taglinestats.append("weather")

			# append tweet choice
			taglinestats.append("tweet")
			
			# ok, now decide if we'll show a static tagline or a dynamic one. just do 50/50 random ratio
			tagType = ['static', 'dynamic']
			pick = choice(tagType)
			#pick = "dynamic"
			
			if (pick == "static"):
				tag = choice(tagline)
			else:
				# it was dynamic
				tag = choice(taglinestats)
				#tag = "weather"
				#tag = "tweet"
				# first check lazy loading items
				if (tag == "weather"):
					# we need to load weather data from url call, this could fail
					tag = self.getWeather()
				if (tag == "tweet"):
					# we need to load tweet
					tag = self.getTweet()
			
			whipitems = ["", ' 4 u', " for ya", " just for u", " the way u like it", " lickety split", " just 4 ya", " steamy hot", " Zipwhip-style", " in a flash", " strong n fresh", " real fast", " in a zip", " zippity zip"]
			whip = choice(whipitems)
			
			verbitems = ["whipping up", "brewing", "vending", "doing", "pouring", "prepping", "making", "cooking up"]
			verb = choice(verbitems)
			
			if (len(fname) > 0):
				msg = "%s, %s a %s%s. %s" % (fname, verb, drink, whip, tag)
			if (len(fname) <= 0 or len(msg) > 160):
				msg = "%s a %s%s. %s" % (verb.capitalize(), drink, whip, tag)
			if (len(msg) > 160):
				msg = msg[:157] + "..."
				
		return msg
	
	def getTweet(self):
		
		zt = zwtwitter.ZwTwitter()
		#zt.search("@Raspberry_Pi")
		searchTerm = self.conf.twittersearch
		listTweets = zt.search(searchTerm)
		ret = "Your lovely brew courtesy of Zipwhip cloud texting (which includes landlines now)"
		if (listTweets):
			ret = "Latest Tweet: %s" % listTweets[0]
		self.log.info("Returning tweet of: %s" % ret)
		return ret
		
	def getWeather(self):
		
		w = "This espresso machine loves to serve u with text-enabled drinks powered by Zipwhip."
		
		citycode = self.conf.region
		matchObj = re.search( r'^(.*?),.*$', citycode, re.I)
		if matchObj:
			cityname = matchObj.group(1).title()
		else:
			cityname = citycode
		self.log.info("Region we'll look up citycode: %s, cityname: %s" % (citycode, cityname))
		#cityname = "San Franciso"
		#citycode = "San%20Francisco,US"
		#cityname = "Seattle"
		#citycode = "Seattle,US"
		#cityname = "Detroit"
		#citycode = "Detroit,US"
		#cityname = "Redmond"
		#citycode = "Redmond,US"
		#citycode = "Bellevue,US"
		try:
			url = 'http://openweathermap.org/data/2.1/find/name?'
			url += 'q=' + urllib.quote(citycode) + '&units=imperial'
			self.log.info("Url: %s" % url)
			data = urlopen(url)
			cities = load(data)
			if cities['count'] > 0:
				city = cities['list'][0]
				from pprint import pprint
				pprint(city)
				ch = int(city['main']['temp_max'])
				cl = int(city['main']['temp_min'])
				cf = city['weather'][0]['description'].lower()
				if (ch > 0 and cl > 0 and len(cf) > 0):
					# we're golden. we ahve a forecast
					w = "Your weather for %s today is highs near %sF, lows at %sF with %s." % (cityname, ch, cl, cf)
					
					# see if contains cloud, snow, rain, sleet
					#matchObj = re.search( r'clouds|rain|snow|sleet', cf, re.M|re.I)
					matchObj = re.search( r'hail|rain|snow|sleet', cf, re.M|re.I)
					if (matchObj):
						t = matchObj.group(0)
						suffixitems = [" %s huh? Good day for coffee." % t.capitalize(), 
						" Darn %s. Coffee will help u forget about it." % t]
						#w += " With %s it's a good day for coffee." % matchObj.group(0)
						suffix = choice(suffixitems)
						#suffix = choice(suffixitems)
						w += suffix
		except:
			pass
			
		return w
		
	def parseMsg(self, msg):
		
		# RETURNS: coffee, coffeeSingle, coffeeTriple, water, decalcify, help, stop, menu, off, on, status
		# we are passed in a message and need to parse it to see if it
		# was a command and then what to do with it
		ret = ""
		
		# see if it's for coffee single
		self.log.info("Searching for words 'coffee single' in '%s'" % msg)
		matchObj = re.search( r'^(\s*)(coffee {1,}single)(\s*)', msg, re.I)
		if matchObj:
			ret = "coffeeSingle"
			self.log.info("Found the words 'coffee single'. Nice!")
		
		else:
			
			# see if it's for coffee triple
			self.log.info("Searching for word 'coffee triple' in '%s'" % msg)
			matchObj = re.search( r'^(\s*)(coffee {1,}triple)(\s*)', msg, re.I)
			if matchObj:
				ret = "coffeeTriple"
				self.log.info("Found the words 'coffee triple'. Nice!")
		
			else:
				
				# see if it's for coffee
				self.log.info("Searching for word 'coffee' in '%s'" % msg)
				matchObj = re.search( r'^(\s*)(coffee)(\s*)', msg, re.I)
				if matchObj:
					ret = "coffee"
					self.log.info("Found the word 'coffee'. Nice!")
			
		# if still no command
		if (ret == ""):
			
			# see if it's for hot water
			self.log.info("Searching for word 'water' in '%s'" % msg)
			matchObj = re.search( r'^(\s*)(water)(\s*)', msg, re.I)
			if matchObj:
				ret = "water"
				self.log.info("Found the word 'water'. Nice!")
			
		if (ret == ""):
			
			# see if it's to decalcify
			self.log.info("Searching for word 'decalcify' in '%s'" % msg)
			matchObj = re.search( r'^(\s*)(decalcify)(\s*)', msg, re.I)
			if matchObj:
				ret = "decalcify"
				self.log.info("Found the word 'decalcify'. Nice!")
		
		if (ret == ""):
			
			# see if it's for help
			self.log.info("Searching for word 'help' in '%s'" % msg)
			matchObj = re.search( r'^(\s*)(help)(\s*)', msg, re.I)
			if matchObj:
				ret = "help"
				self.log.info("Found the word 'help'. Nice!")
				
		if (ret == ""):
			
			# see if it's for menu
			self.log.info("Searching for word 'menu' in '%s'" % msg)
			matchObj = re.search( r'^(\s*)(menu)(\s*)', msg, re.I)
			if matchObj:
				ret = "menu"
				self.log.info("Found the word 'menu'. Nice!")
				
		if (ret == ""):
			
			# see if it's for stop
			self.log.info("Searching for word 'stop' in '%s'" % msg)
			matchObj = re.search( r'^(\s*)(stop)(\s*)', msg, re.I)
			if matchObj:
				ret = "stop"
				self.log.info("Found the word 'stop'. Nice!")
				
		if (ret == ""):
			
			# see if it's for off
			key = "off"
			self.log.info("Searching for word '%s' in '%s'" % (key, msg))
			matchObj = re.search( r'^(\s*)(' + key + ')(\s*)', msg, re.I)
			if matchObj:
				ret = key
				self.log.info("Found the word '%s'. Nice!" % key)
				
		if (ret == ""):
			
			# see if it's for on
			key = "on"
			self.log.info("Searching for word '%s' in '%s'" % (key, msg))
			matchObj = re.search( r'^(\s*)(' + key + ')(\s*)', msg, re.I)
			if matchObj:
				ret = key
				self.log.info("Found the word '%s'. Nice!" % key)
				
		if (ret == ""):
			
			key = "status"
			self.log.info("Searching for word '%s' in '%s'" % (key, msg))
			matchObj = re.search( r'^(\s*)(' + key + ')(\s*)', msg, re.I)
			if matchObj:
				ret = key
				self.log.info("Found the word '%s'. Nice!" % key)
		
		if (ret == ""):
			
			key = "the zipwhip"
			self.log.info("Searching for word '%s' in '%s'" % (key, msg))
			matchObj = re.search( r'^(\s*)(' + key + ')(\s*)', msg, re.I)
			if matchObj:
				ret = "coffeeTriple"
				self.log.info("Found the word '%s'. Nice!" % key)
		
		return ret

	def xparseMsg(self, msg, addr, fname, lname):
		pass
		
	def sendMsg(self, to, msg):
		
		self.log.info("In sending msg")
		
		# check length of msg as a last attempt
		if (len(msg) > 160):
			msg = msg[:157] + '...'
		
		url = 'http://network.zipwhip.com/message/send'
		values = {"session" : self.conf.sessionid,
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
		
def test():
	
	# setup logging
	FORMAT = '%(asctime)s %(levelname)s %(message)s'
	logging.basicConfig(format=FORMAT)
	logger = logging.getLogger()
	logger.setLevel(logging.INFO)
	if not logger.handlers:
            logger.addHandler(logging.StreamHandler())
	
	import zwsqlstats
	stats = zwsqlstats.ZwStats(logger=logger)
	conf = zwconfig.ZwConfig()
	'''
	zwmsg = ZwMsgHandler(logger=logger, stats=stats, conf=conf)
	addr = "5555551212"
	fname = "John"
	lname = "Lastname"
	cmd = "coffee"
	#msg = zwmsg.create("coffee", "5555551212", "John", "")
	msg = zwmsg.createMsg(cmd, addr, fname, "")
	stats.logOrder(addr, cmd, fname, lname,  
		cmd, msg, "msg out 2 folks")
	logger.info(msg)
	logger.info("Length of msg: %s" % len(msg))
	startBrewTime = time.time()
	startBrewTime -= 186
	elapsed = int(time.time() - startBrewTime)
	logger.info("Elapsed: %s" % elapsed)
	outTime = zwmsg.humanize_time(elapsed)
	logger.info("outTime: %s" % outTime)
	msgOut2 = """Your coffee single is brewed. It took me %s to whip it up for u. Enjoy.""" % outTime
	logger.info("Msg back is: %s" % msgOut2)
	weather = zwmsg.getWeather()
	logger.info(weather)
	tweet = zwmsg.getTweet()
	logger.info(tweet)
	logger.info(len(tweet))
	'''
	zwmsg = ZwMsgHandler(logger=logger, stats=stats, conf=conf)
	cmd = zwmsg.parseMsg(""" Status folks

Sent via Textspresso Ordering""")
	logger.info(cmd)
#test()