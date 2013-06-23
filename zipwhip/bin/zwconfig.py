# This class reads the config for Zipwhip
import ConfigParser
import logging

CONFIGFILE = "/opt/zipwhip/conf/zipwhip.conf"

class ZwConfig:
	def __init__(self, 
				logger = None,
				clientid = None, sessionid = None,
				):
		# define properties
		if (logger == None):
			logger = logging.getLogger("zwconfig")
			logger.setLevel(logging.DEBUG)
			formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
			handler = logging.FileHandler("/tmp/zipwhip-textspresso3.log")
			handler.setFormatter(formatter)
			logger.addHandler(handler)
			self.log = logger
		else:
			self.log = logger
		#self.clientid = clientid
		#self.sessionid = sessionid
		#log.info("ClientId=%s" % clientid)

		self.config = ConfigParser.RawConfigParser()
		self.config.read(CONFIGFILE)

		# getfloat() raises an exception if the value is not a float
		# getint() and getboolean() also do this for their respective types
		#self.acctname = self.config.get('Settings', 'acctname')
		self.phonenum = self.config.get('Settings', 'phonenum')
		self.password = self.config.get('Settings', 'password')
		self.sessionid = self.config.get('Settings', 'sessionid')
		self.clientid = self.config.get('Settings', 'clientid')
		self.region = self.config.get('Settings', 'region')
		self.twittersearch = self.config.get('Settings', 'twittersearch')
		if (self.region == None or len(self.region) < 0):
			self.region = "Seattle,US"
		if (self.twittersearch == None or len(self.twittersearch) < 0):
			self.twittersearch = "zipwhip"
		msg = "Using zwconfig. Settings read from %s are " % CONFIGFILE
		msg += "phonenum=%s, pass=%s, sessionid=%s, " % (self.phonenum, self.password, self.sessionid)
		msg += "clientid=%s, region=%s, twittersearch=%s" % (self.clientid, self.region, self.twittersearch)
		self.log.info(msg)
	
	def printVals(self):
		self.log.info("Printing vals")
		msg = "Using zwconfig. Settings read from %s are " % CONFIGFILE
		msg += "phonenum=%s, pass=%s, sessionid=%s, " % (self.phonenum, self.password, self.sessionid)
		msg += "clientid=%s, region=%s, twittersearch=%s" % (self.clientid, self.region, self.twittersearch)
		self.log.info(msg)
		
	def write(self):
		#self.config.set('Settings', 'acctname', self.acctname)
		self.config.set('Settings', 'phonenum', self.phonenum)
		self.config.set('Settings', 'password', self.password)
		self.config.set('Settings', 'sessionid', self.sessionid)
		self.config.set('Settings', 'clientid', self.clientid)
		self.config.set('Settings', 'region', self.region)
		self.config.set('Settings', 'twittersearch', self.twittersearch)
		with open(CONFIGFILE, 'wb') as configfile:
			self.config.write(configfile)
		#self.log.info("Writing to config: phonenum=%s, pass=%s, sessionid=%s, " +
		#	"clientid=%s, region=%s, twittersearch=%s" %
		#	(self.phonenum, self.password, self.sessionid, self.clientid, 
		#	self.region, self.twittersearch))
		self.printVals()

def test():
	log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
	logging.basicConfig(format=log_format, level=logging.INFO)
	zwcf = ZwConfig()
	#zwcf.printVals()
	
#test()
