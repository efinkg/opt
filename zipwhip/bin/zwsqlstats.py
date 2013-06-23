import sqlite3 as lite
import logging
from datetime import date

SQLFILE = "/opt/zipwhip/db/stats.db"

class ZwStats:
	def __init__(self, 
				logger = None,
				):
		# define properties
		if (logger == None):
			logger = logging.getLogger("zwsqlstats")
			logger.setLevel(logging.DEBUG)
			formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
			handler = logging.FileHandler("/opt/zipwhip/log/zipwhip-textspresso.log")
			handler.setFormatter(formatter)
			logger.addHandler(handler)
			self.log = logger
		else:
			self.log = logger

		con = lite.connect(SQLFILE)
		#self.log.info("test")
		with con:
			cur = con.cursor()    
			cur.execute('SELECT SQLITE_VERSION()')			
			data = cur.fetchone()
			self.log.info("Configuring zwsql stats. Using SQLite version: %s" % data)
			#cur.execute("DROP TABLE IF EXISTS UserStats")
			try:
				cur.execute("""
					CREATE TABLE UserStats(Id INTEGER PRIMARY KEY AUTOINCREMENT, 
					PhoneNum TEXT UNIQUE, FName TEXT, LName TEXT, IsDailyStat INT, 
					CoffeeCnt INT, CoffeeSingleCnt INT, CoffeeDoubleCnt INT, CoffeeTripleCnt INT,
					HotWaterCnt INT, BeansOutCnt INT, WaterOutCnt INT, TrayNeededEmptiedCnt INT,
					MsgsInCnt INT, MsgsOutCnt INT, FirstOrderDate TEXT, LastOrderDate TEXT)
					""")
			except:
				# just skip creating the table
				#self.log.info("Found that UserStats table exists. No need to create it.")
				pass
			
			# Create the log table
			self.logkeys = {"PhoneNum":0, "FName":0, "LName":0, "Coffee":0, "CoffeeSingle":0,
				"CoffeeDouble":0, "CoffeeTriple":0, "HotWater":0, "BeansOut":0, "WaterOut":0,
				"TrayNeededEmptied":0, "MsgIn":0, "MsgOut":0, "MsgOut2":0, "OrderDate":0}
			#cur.execute("DROP TABLE IF EXISTS UserStatsLog")
			try:
				cur.execute("""
					CREATE TABLE UserStatsLog(Id INTEGER PRIMARY KEY AUTOINCREMENT, 
					PhoneNum TEXT, FName TEXT, LName TEXT, 
					Coffee INT, CoffeeSingle INT, CoffeeDouble INT, CoffeeTriple INT,
					HotWater INT, BeansOut INT, WaterOut INT, TrayNeededEmptied INT,
					MsgIn TEXT, MsgOut TEXT, MsgOut2 TEXT, OrderDate TEXT)
					""")
			except:
				# just skip creating the table
				#self.log.info("Found that UserStatsLog table exists. No need to create it.")
				pass

			# Create the global stats record
			try:
				cur.execute("""INSERT INTO UserStats
					VALUES(NULL,'GLOBAL','Machine Stats','',0,0,0,0,0,0,0,0,0,0,0,datetime('now', 'start of day', 'localtime'),datetime('now', 'localtime'))""")
				lid = cur.lastrowid
				#self.log.info("The last Id of the inserted row is %d" % lid)
				'''
				cur.execute("SELECT * FROM UserStats")
				rows = cur.fetchall()
				for row in rows:
					self.log.info(row)
				'''
			except:
				# do nothing on err for insert
				pass
	
	def getNumOrdersGlobal(self):
		#self.log.info("Getting the total orders globally for today for whole machine")
		sql = """SELECT sum(Coffee) FROM UserStatsLog 
				"""	
		return self.getSqlOneData(sql)

	def getNumOrdersGlobalToday(self):
		#self.log.info("Getting the total orders globally for today for whole machine")
		sql = """SELECT sum(Coffee) FROM UserStatsLog 
				WHERE OrderDate >= datetime('now', 'localtime', 'start of day', '-0 day') 
				and OrderDate < datetime('now', 'localtime', 'start of day', '+1 day')
				"""	
		return self.getSqlOneData(sql)

	def getNumOrdersGlobalYest(self):
		#self.log.info("Getting the total orders globally for yesterday for whole machine")
		sql = """SELECT sum(Coffee) FROM UserStatsLog 
				WHERE OrderDate >= datetime('now', 'localtime', 'start of day', '-1 day') 
				and OrderDate < datetime('now', 'localtime', 'start of day', '-0 day')
				"""	
		return self.getSqlOneData(sql)
	
	def getNumOrdersGlobalThisWeek(self):
		#self.log.info("Getting the total orders globally for this week for whole machine")
		sql = """SELECT sum(Coffee) FROM UserStatsLog 
				WHERE OrderDate >= datetime('now', 'localtime', 'start of day', 'weekday 0', '-7 day') 
				and OrderDate < datetime('now', 'localtime', 'start of day', 'weekday 0', '+0 day')
				"""	
		return self.getSqlOneData(sql)

	def getNumOrdersGlobalLastWeek(self):
		#self.log.info("Getting the total orders globally for last for whole machine")
		sql = """SELECT sum(Coffee) FROM UserStatsLog 
				WHERE OrderDate >= datetime('now', 'localtime', 'start of day', 'weekday 0', '-14 day') 
				and OrderDate < datetime('now', 'localtime', 'start of day', 'weekday 0', '-7 day')
				"""	
		return self.getSqlOneData(sql)

	def getNumOrdersThisWeek(self, phonenum):
		sql = """SELECT sum(Coffee) FROM UserStatsLog 
				WHERE OrderDate >= datetime('now', 'localtime', 'start of day', 'weekday 0', '-7 day') 
				and OrderDate < datetime('now', 'localtime', 'start of day', 'weekday 0', '+0 day')
				and PhoneNum LIKE '%s' """ % phonenum	
		return self.getSqlOneData(sql)

	def getNumOrdersLastWeek(self, phonenum):
		#self.log.info("Getting the total orders globally for last for whole machine")
		sql = """SELECT sum(Coffee) FROM UserStatsLog 
				WHERE OrderDate >= datetime('now', 'localtime', 'start of day', 'weekday 0', '-14 day') 
				and OrderDate < datetime('now', 'localtime', 'start of day', 'weekday 0', '-7 day')
				and PhoneNum LIKE '%s' """ % phonenum	
		return self.getSqlOneData(sql)

	def getSqlOneData(self, sql):
		#self.log.info("Getting one data item. sql: %s" % sql)
		con = lite.connect(SQLFILE)
		with con:
			con.row_factory = lite.Row
			cur = con.cursor()
			cur.execute(sql)
			data = cur.fetchone()
		#self.log.info(data[0])
		d = 0
		if (data != None):
			d = data[0]
		return d	

	def getNumOrdersTotal(self, phonenum):
		#self.log.info("Getting the total orders globally for phone: %s" % phonenum)
		con = lite.connect(SQLFILE)
		with con:
			con.row_factory = lite.Row
			cur = con.cursor()
			cur.execute("SELECT CoffeeCnt FROM UserStats WHERE PhoneNum LIKE '%s'" % phonenum)
			data = cur.fetchone()
		#self.log.info(data[0])
		d = 0
		if (data != None):
			d = data[0]
		return d	
	
	def getNumOrdersToday(self, phonenum):
		#self.log.info("Getting the total orders for today for phone: %s" % phonenum)
		con = lite.connect(SQLFILE)
		with con:
			con.row_factory = lite.Row
			cur = con.cursor()
			cur.execute("SELECT sum(Coffee) FROM UserStatsLog WHERE OrderDate >= datetime('now', 'start of day', 'localtime') and PhoneNum LIKE '%s'" % phonenum)
			data = cur.fetchone()
		#self.log.info(data[0])
		d = 0
		if (data != None):
			d = data[0]
		return d	

	def getNumOrdersYest(self, phonenum):
		#self.log.info("Getting the total orders for yesterday for phone: %s" % phonenum)
		con = lite.connect(SQLFILE)
		with con:
			con.row_factory = lite.Row
			cur = con.cursor()
			cur.execute("""SELECT sum(Coffee) FROM UserStatsLog 
				WHERE OrderDate >= datetime('now', 'start of day', '-1 day', 'localtime') 
				and OrderDate < datetime('now', 'start of day', '-0 day', 'localtime')
				and PhoneNum LIKE '%s'
				""" % phonenum)
			data = cur.fetchone()
		#self.log.info(data[0])
		d = 0
		if (data != None):
			d = data[0]
		return d	
		
	def incrUserStats(self, phonenum, fname=None, lname=None,
		coffeesinglecnt=0, coffeedoublecnt=0, coffeetriplecnt=0, isdailystat=0):
		
		self.log.info("Increasing user stats for %s" % phonenum)
		con = lite.connect(SQLFILE)
		with con:
			con.row_factory = lite.Row
			cur = con.cursor()
			#cur.execute("SELECT * FROM UserStats WHERE PhoneNum LIKE \"" + phonenum + "\"")			
			cur.execute("SELECT * FROM UserStats WHERE PhoneNum LIKE '%s'" % phonenum)			
			data = cur.fetchall()
			if data:
				# a row exists, update it
				pass
			else:
				# a row does not exist, do insert
				cur.execute("""INSERT INTO UserStats
					VALUES(NULL, ?, ?, ?,0,0,0,0,0,0,0,0,0,0,0,datetime('now', 'localtime'),datetime('now', 'localtime'))""", 
					(phonenum, fname, lname))
				lid = cur.lastrowid
				self.log.info("User does not exist yet. Doing insert. PK = %d" % lid)
			
			# we should always be guaranteed to have a user record now
			sql = "SELECT * FROM UserStats WHERE PhoneNum LIKE '%s'" % phonenum
			#self.log.info(sql)
			cur.execute(sql)
			data = cur.fetchone()
			#print data
			#self.log.info(data)
			
			# increment everything
			d = {}
			for col in data.keys():
				d[col] = data[col]
				#self.log.info("Col %s = %s" % (col, d[col]))
				
			if fname:
				d["FName"] = fname
			if lname:
				d["LName"] = lname
			d["CoffeeCnt"] += 1
			d["CoffeeSingleCnt"] += coffeesinglecnt
			d["CoffeeDoubleCnt"] += coffeedoublecnt
			d["CoffeeTripleCnt"] += coffeetriplecnt
			d["MsgsInCnt"] += 1
			if coffeesinglecnt > 0:
				d["MsgsOutCnt"] += 1
			else:
				d["MsgsOutCnt"] += 2
			d["IsDailyStat"] = isdailystat
			
			cur.execute("""UPDATE UserStats SET FName=:FName, LName=:LName,  
				IsDailyStat=:IsDailyStat,
				CoffeeCnt=:CoffeeCnt,
				CoffeeSingleCnt=:CoffeeSingleCnt,
				CoffeeDoubleCnt=:CoffeeDoubleCnt,
				CoffeeTripleCnt=:CoffeeTripleCnt,
				MsgsInCnt=:MsgsInCnt,
				MsgsOutCnt=:MsgsOutCnt,
				LastOrderDate=datetime('now', 'localtime')
				WHERE Id=:Id""", d)        
			con.commit()
			#self.log.info( "Number of rows updated: %d" % cur.rowcount)
			
			cur.execute("SELECT * FROM UserStats WHERE PhoneNum LIKE '%s'" % phonenum)
			data = cur.fetchone()
			#self.log.info( data)
						
		# now, call myself to increment the global stats
		if phonenum != "GLOBAL" and isdailystat == 0:
			
			# update global stats
			self.log.info("Going to increase global count.")
			self.incrUserStats(phonenum="GLOBAL", coffeesinglecnt=coffeesinglecnt,
				coffeedoublecnt=coffeedoublecnt, coffeetriplecnt=coffeetriplecnt)
				
			# now, call myself with the daily stat setting to just increment for this day
			# only call ourselves if we're not a global stat, i.e. we're a per user phone number stat
			# and if we're not a dailystat, i.e. we're an individual stat
			self.log.info("Going to increase per day count. Calling now...")
			d = date.today()
			dt = d.isoformat()
			#self.log.info("The per day cnt PK = " + dt)
			self.incrUserStats(phonenum=dt, fname="Daily Stat", coffeesinglecnt=coffeesinglecnt,
				coffeedoublecnt=coffeedoublecnt, coffeetriplecnt=coffeetriplecnt, 
				isdailystat=1)
	
	def logOrder(self, phonenum, cmd, fname="", lname="", msgin="", msgout="", msgout2="",
		beansout=0, waterout=0, trayneededemptied=0):
		
		self.log.info("Storing log for %s" % phonenum)
		con = lite.connect(SQLFILE)
		with con:
			con.row_factory = lite.Row
			cur = con.cursor()
		
			d = {}
			for col in self.logkeys.keys():
				d[col] = 0
				#self.log.info("Col %s = %s" % (col, d[col]))
				
			d["PhoneNum"] = phonenum
			d["FName"] = fname
			d["LName"] = lname
			if (cmd == "coffee" or cmd == "coffeeSingle" or cmd == "coffeeTriple"):
				d["Coffee"] = 1
			if (cmd == "coffeeSingle"):
				d["CoffeeSingle"] = 1
			if (cmd == "coffee"):
				d["CoffeeDouble"] = 1
			if (cmd == "coffeeTriple"):
				d["CoffeeTriple"] = 1
			if (cmd == "water"):
				d["HotWater"] = 1
			d["BeansOut"] = beansout
			d["WaterOut"] = waterout
			d["TrayNeededEmptied"] = trayneededemptied
			d["MsgIn"] = msgin
			d["MsgOut"] = msgout
			d["MsgOut2"] = msgout2
			del d["OrderDate"] # don't want it passed in
			
			'''
			cur.execute("""INSERT INTO UserStatsLog (
				PhoneNum, Name,
				Coffee, CoffeeSingle, CoffeeDouble,
				HotWater, BeansOut, WaterRanOut, TrayNeededEmptied,
				MsgIn,
				MsgOut, MsgOut2,
				OrderDate) VALUES (
				:PhoneNum, :Name,
				:Coffee, :CoffeeSingle, :CoffeeDouble,
				:HotWater, :BeansOut, :TrayNeededEmptied,
				:MsgIn,
				:MsgOut, :MsgOut2,
				datetime()
				""", d)
			'''
			#con.commit()
			qmarks = ', '.join('?' * len(d))
			cols = ', '.join(str(v) for v in d.keys())
			qry = """Insert Into UserStatsLog (%s, OrderDate) 
			Values (%s, datetime('now', 'localtime', '-0 day'))""" % (cols, qmarks)
			#self.log.info(qry)
			#self.log.info(d.keys())
			#self.log.info(d.values())
			cur.execute(qry, d.values())
			lid = cur.lastrowid
			#self.log.info("Added a log row. PK = %d" % lid)
			
			#cur.execute("SELECT * FROM UserStatsLog WHERE Id = %s" % lid)
			#cur.execute("SELECT * FROM UserStatsLog")
			#row = cur.fetchone()
			#self.log.info(row)
			#rows = cur.fetchall()
			#self.printRows(rows)
			#self.log.info(rows)
			#cols = '|'.join(str(v) for v in d.keys())
				
		# now increase overall userstats
		cofsgl = 0
		cofdbl = 0
		coftpl = 0
		if (cmd == "coffee"):
			cofdbl = 1
		if (cmd == "coffeeSingle"):
			cofsgl = 1
		if (cmd == "coffeeTriple"):
			coftpl = 1
		self.incrUserStats(phonenum=phonenum, fname=fname, lname=lname, 
			coffeesinglecnt=cofsgl, coffeedoublecnt=cofdbl, coffeetriplecnt=coftpl)
			
	def printRows(self, rows):
		colp = ""
		for row in rows:
			if (colp == ""):
				colp = '|'.join(str(v) for v in row.keys())
				self.log.info(colp)
			rowp = '|'.join(str(v) for v in row)
			self.log.info(rowp)
			#for col in row:
			#	self.log.info("Col %s = %s" % (col, d[col]))	self.log.info("Row: %s" % row)
	
	def printLog(self):
		con = lite.connect(SQLFILE)
		with con:
			con.row_factory = lite.Row
			cur = con.cursor()
			cur.execute("SELECT * FROM UserStatsLog")
			rows = cur.fetchall()
			self.printRows(rows)

	def printAll(self):
		con = lite.connect(SQLFILE)
		with con:
			con.row_factory = None
			cur = con.cursor()
			cur.execute("SELECT * FROM UserStats")
			rows = cur.fetchall()
			for row in rows:
				self.log.info(row)

def test():
	
	# setup logging
	FORMAT = '%(asctime)s %(levelname)s %(message)s'
	logging.basicConfig(format=FORMAT)
	logger = logging.getLogger()
	logger.setLevel(logging.INFO)
	if not logger.handlers:
            logger.addHandler(logging.StreamHandler())
	
	stats = ZwStats(logger=logger)
	#stats.incrUserStats(phonenum="5555551212", name="Jed Smith", 
	#	coffeesinglecnt=0, coffeedoublecnt=1)
	#tats.incrUserStats(phonenum="5555551212", fname="Jed", lname="Smith", 
	#	coffeesinglecnt=0, coffeedoublecnt=1)
	#stats.incrUserStats(phonenum="5555551212", fname="John", lname="LastName", 
	#	coffeesinglecnt=0, coffeedoublecnt=1)
	#stats.printAll()
	
	num = "ptn:/5555551212"
	stats.logOrder(num, "coffeeSingle", "John", "LastName",  
		"msg in yeah", "msg out", "msg out 2 folks")
	stats.printLog()
	numToday = stats.getNumOrdersToday(num)
	numTotal = stats.getNumOrdersTotal(num)
	numYest = stats.getNumOrdersYest(num)
	stats.log.info("For phonenum: %s, OrdersTotal: %s, OrdersToday: %s, OrdersYest: %s" % (num, numTotal, numToday, numYest))

	'''
	#stats.logOrder("5555551212", "coffeeSingle", "Suzy", "Smith", 
	#	"msg in yeah", "msg out", "msg out 2 folks")
	numToday = stats.getNumOrdersToday("5555551212")
	numTotal = stats.getNumOrdersTotal("5555551212")
	numYest = stats.getNumOrdersYest("5555551212")
	numIndtw = stats.getNumOrdersThisWeek("5555551212")
	numIndlw = stats.getNumOrdersLastWeek("5555551212")
	stats.log.info("For phonenum: %s, OrdersTotal: %s, OrdersToday: %s, OrdersYest: %s" % ("5555551212", numTotal, numToday, numYest))
	stats.log.info("For phonenum %s, num orders this week: %s, num orders last week: %s" % ("5555551212", numIndtw, numIndlw))
	'''
	
	ngt = stats.getNumOrdersGlobalToday()
	ngy = stats.getNumOrdersGlobalYest()
	ngtw = stats.getNumOrdersGlobalThisWeek()
	nglw = stats.getNumOrdersGlobalLastWeek()
	stats.log.info("Global counts. Today: %s, Yest: %s, ThisWeek: %s, LastWeek: %s" % (ngt, ngy, ngtw, nglw))
	
#test()