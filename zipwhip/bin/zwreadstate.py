import RPIO
import time
from time import sleep
from array import *
import sys
import logging
import pdb

class ZwReadState:
	
	def __init__(self, 
				logger = None,
				clientid = None, sessionid = None,
				):
		# define properties
		# define properties
		if (logger == None):
			logger = logging.getLogger("zwreadstate")
			logger.setLevel(logging.DEBUG)
			formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
			handler = logging.FileHandler("/opt/zipwhip/log/zipwhip-textspresso.log")
			handler.setFormatter(formatter)
			logger.addHandler(handler)
			self.log = logger
		else:
			self.log = logger

		RPIO.setmode(RPIO.BCM)

		# To read the state of LEDs off shift register
		RPIO.setup(7, RPIO.IN, pull_up_down=RPIO.PUD_OFF)	# q1
		RPIO.setup(8, RPIO.IN, pull_up_down=RPIO.PUD_OFF)	# q2
		RPIO.setup(17, RPIO.IN, pull_up_down=RPIO.PUD_OFF)	# q3
		RPIO.setup(22, RPIO.IN, pull_up_down=RPIO.PUD_OFF)	# q4
		RPIO.setup(23, RPIO.IN, pull_up_down=RPIO.PUD_OFF)	# q5
		RPIO.setup(24, RPIO.IN, pull_up_down=RPIO.PUD_OFF)	# q6
		RPIO.setup(25, RPIO.IN, pull_up_down=RPIO.PUD_OFF)	# q7
		RPIO.setup(4, RPIO.IN, pull_up_down=RPIO.PUD_OFF)	# q8
		
		# add callbacks only once or we could get called twice each time
		#RPIO.add_interrupt_callback(4, self.on_q8_rising, edge='rising', threaded_callback=False)
		#RPIO.add_interrupt_callback(25, self.on_q7_rising, edge='rising', threaded_callback=False)

		# keep track of how many calls
		self.ctrRising = 0
		
		# create data storage for the read of the state
		self.indx = [7, 8, 17, 22, 23, 24]
		self.names = ["q1", "q2", "q3", "q4", "q5", "q6"]
		#print indx
		self.dataq7 = [0 for x in range(25)]  #array('i')
		self.dataq8 = [0 for x in range(25)]  #array('i')
		self.log.info("Just setup the input pins for reading LED state off shift register")
		
	def startReadingState(self):
		# start reading state from leds for 2 seconds
		# that should give us enough time to get a decent sample in case
		# the Raspi is busy and thus our callbacks aren't accurate in their reading
		self.log.info("Starting to read state off LEDs for 2 sec")
		
		# Reset global ctr
		self.ctrRising = 0
		
		# Reset data
		for e in self.indx:
			self.dataq7[e] = 0
			self.dataq8[e] = 0
			
		RPIO.add_interrupt_callback(4, self.on_q8_rising, edge='rising', threaded_callback=False)
		RPIO.add_interrupt_callback(25, self.on_q7_rising, edge='rising', threaded_callback=False)
		self.log.info("Inside startReadingState(). Added callback for pin %s" % 4)
		self.log.info("Inside startReadingState(). Added callback for pin %s" % 25)
	
		#pdb.set_trace()
		RPIO.wait_for_interrupts()
		self.log.info("Inside startReadingState(). We just got passed RPIO.wait_for_interrupts() which is awesome cuz thought blocking here never ended.")

		# if we've gottent this far, that's awesome cuz we were finding we never
		# got here. so now we can remove callbacks. we know we only get here once
		# so this is clean.
		RPIO.del_interrupt_callback(4)
		RPIO.del_interrupt_callback(25)
		self.log.info("Inside startReadingState(). Removed interrupt callbacks for GPIO 4 and 25.")

		# let's make sure the doneReadingState() method is finished
		# this is because it does a sleep() and we don't want
		# to return from here until that sleep is finished
		
		'''
		# make sure our ctrRising hasn't changed in a second or so
		start_time = time.time()
		elapsed_time = 0
		loc_ctr = self.ctrRising
		self.log.info("Going to do yield loop for 1 second. Seems to ensure all callbacks are completed before I return.")
		loopCtr = 0
		while (elapsed_time < 1):
			loopCtr += 1
			# if we are having a moving ctrRising, reset our start time. i want 1 full second
			# of no movement on ctrRising
			if (loc_ctr != self.ctrRising):
				self.log.info("ctrRising was still changing. resetting start_time to now to extend our wait.")
				start_time = time.time()
			sleep(0.001)
			#self.log.info("In yield loop to make sure all our interrupt callbacks came back. self.ctrRising: %s, elapsed_time: %s" % (self.ctrRising, elapsed_time))
			elapsed_time = time.time() - start_time
		self.log.info("Returning from startReadingState(). Done with yield loop. Looped: %s" % loopCtr)
		'''
		self.log.info("Done with startReadingState(). Only here should main zwtextspressod continue on.")
		
	def doneReadingState(self):
		# we finished sampling the data
		# now remove the callbacks because we're done sending and no need
		# to keep the load on our script of handling callcacks
		#self.ctrRising = 0
		
		RPIO.stop_waiting_for_interrupts()
		self.log.info("Inside doneReadingState(). Just did stop_waiting_for_interrupts().")

		# of, we just turned off the waiting_for_interrupts()
		# however, this just effects the while loop inside RPIO
		# we need to make sure that while loop gets back to the top
		# so we have to allow more interrupts to occur
		# sleep here for 100 ms to let some more thru
		#self.log.info("Sleeping for 0.1 to let some other callbacks occur to trigger the waiting_for_interrupts() to get to the top of it's loop so it sees the boolean to stop blocking.")
		#sleep(0.1)
		
		#RPIO.del_interrupt_callback(4)
		#RPIO.del_interrupt_callback(25)
		#self.log.info("Removed interrupt callbacks for GPIO 4 and 25.")
		#self.log.info("Not deleting callbacks anymore.")
		#self.log.info("Inside doneReadingState(). Done reading state on LEDs")
		
		# we just finished reading state
		self.log.info("Inside doneReadingState(). ctrRising after reading all state is: %s" % self.ctrRising)

		# make sure our ctrRising hasn't changed in a second or so
		'''
		start_time = time.time()
		elapsed_time = 0
		loc_ctr = self.ctrRising
		self.log.info("Going to do doneReadingState() yield loop for 1 second. Seems to ensure all callbacks are completed before I return.")
		loopCtr = 0
		while (elapsed_time < 1):
			loopCtr += 1
			# if we are having a moving ctrRising, reset our start time. i want 1 full second
			# of no movement on ctrRising
			if (loc_ctr != self.ctrRising):
				self.log.info("ctrRising was still changing. resetting start_time to now to extend our wait.")
				start_time = time.time()
			sleep(0.001)
			#self.log.info("In yield loop to make sure all our interrupt callbacks came back. self.ctrRising: %s, elapsed_time: %s" % (self.ctrRising, elapsed_time))
			elapsed_time = time.time() - start_time
		self.log.info("doneReadingState(). Done with yield loop. Looped: %s" % loopCtr)
		'''
		
		self.log.info("Returning from doneReadingState().")


	def on_q7_rising(self, gpio_id, value):
		
		# we could get called after we're done counting, so ignore that data
		if (self.ctrRising < 1000):
			# we need to scan for the led data
			for e in self.indx:
				self.dataq7[e] = self.dataq7[e] + RPIO.input(e)
				if (e == 23):
					self.dataq7[e] = 0
	
	def on_q8_rising(self, gpio_id, value):
		
		#self.log.info("got on_q8_rising")
		# we need to scan for the led data
		# we could get called after we're done counting, so ignore that data
		if (self.ctrRising < 1000):
			for e in self.indx:
				self.dataq8[e] = self.dataq8[e] + RPIO.input(e)
				if (e == 23):
					self.dataq8[e] = 0
					
		# see if it's time to exit after 2 seconds of reading leds
		#global ctrRising
		self.ctrRising = self.ctrRising + 1
		if (self.ctrRising == 1000):
			self.doneReadingState()
	
	
	def analyzeData(self):
		
		'''
		isOff = self.isMachineOff()
		isReady = self.isReadyToBrew()
		isReadyWithWarn = self.isReadyToBrewWithWarnings()
		'''
		self.convertDataToProperties()
		
		'''
		# this analysis is inaccurate. use getError() now
		if (self.ledWaterOut < 100):
			self.log.info("Water container has water. Good to go.")
		else:
			self.log.info("Water is out. Need to refill.")
		if (self.ledTray > 800):
			self.log.info("Tray needs emptied of it's grinds.")
		else:
			self.log.info("Tray is ok. No need to empty. Good to go.")
		if (self.ledWarning < 100):
			self.log.info("No warning light on. Good to go.")
		else:
			self.log.info("Uh oh. Warning light is on.")
		
		#if (!isOff):
			# See if it's warming up or ready to make coffee
		'''	
		
	def convertDataToProperties(self):
		
		self.log.info("Inside convertDataToProperties()")
		
		# when you see self.led it's just cuz it's not mapped
		# to anything. i just wanted a clean list here of
		# all iterations.
		
		# Full Off < 100
		# Full On > 900
		# Half On > 400 AND < 600
		self.OFF = 0
		self.FULLON = 1
		self.HALFON = 2
		
		# The water out LED does not seem to blink, so should get full on or full off
		self.ledWaterOut = self.dataq7[self.indx[0]] # q7/q1
		self.ledTray = self.dataq7[self.indx[1]] # q7/q2
		self.ledWarning = self.dataq7[self.indx[2]] # q7/q3
		self.ledDecalcify = self.dataq7[self.indx[3]] # q7/q4
		self.ledPreGround = self.dataq7[self.indx[4]] # q7/q5
		self.led = self.dataq7[self.indx[5]] # q7/q6
		self.ledCof = self.dataq8[self.indx[0]] # q8/q1
		self.ledCof2 = self.dataq8[self.indx[1]] # q8/q2
		self.ledHotWater = self.dataq8[self.indx[2]] # q8/q3
		self.led = self.dataq8[self.indx[3]] # q8/q4
		self.led = self.dataq8[self.indx[4]] # q8/q5
		self.led = self.dataq8[self.indx[5]] # q8/q6
		
		self.log.info("Done convertDataToProperties()")
	
	def analyzeIsVendingCof(self):
		
		self.log.info("Doing analyzeIsVendingCof()")
		self.startReadingState()
		self.printData()
		self.analyzeData()
		ret = self.isVendingCof()
		
		# see if we've got blinking on cof and cof2
		# but no lights on anything else
		self.log.info("Done analyzeIsVendingCof(). Ret: %s" % ret)
		return ret
	
	def isVendingCof(self):
		
		# is warming up
		isVending = False
		
		if (self.ledWaterOut < 200 and  # water light off
			self.ledTray < 200 and
			self.ledWarning < 200 and
			self.ledDecalcify < 200 and
			self.ledPreGround < 200 and
			self.ledHotWater < 200 and
			self.ledCof > 800 and # solid on
			self.ledCof2 < 200):  # off
			# we have warming
			isVending = True
		
		if (isVending):
			self.log.info("The machine is vending.")
		else:
			self.log.info("The machine is not vending.")
			
		return isVending
		
	def analyzeIsWarmingUp(self):
		
		self.log.info("Doing analyzeIsWarmingUp()")
		self.startReadingState()
		self.printData()
		self.analyzeData()
		self.log.info("Done doing analyzeIsWarmingUp()")
		ret = self.isWarmingUp()
		
		# see if we've got blinking on cof and cof2
		# but no lights on anything else
		self.log.info("Done analyzeIsWarmingUp(). Ret: %s" % ret)
		return ret
	
	def analyzeIsMachineOff(self):
		
		self.log.info("Inside analyzeIsMachineOff()")
		self.startReadingState()
		self.printData()
		self.analyzeData()
		#self.convertDataToProperties()
		ret = self.isMachineOff()
		self.log.info("Done analyzeIsMachineOff(). Ret: %s" % ret)
		return ret
	
	def isWarmingUp(self):
		
		#pdb.set_trace()
		self.log.info("Inside isWarmingUp()")
		# is warming up
		isWarming = False
		
		if (self.ledWaterOut < 200 and  # water light off
		self.ledTray < 200 and
		self.ledWarning < 200 and
		self.ledDecalcify < 200 and
		self.ledPreGround < 200 and
		self.ledHotWater < 200 and
		self.ledCof > 300 and self.ledCof < 700 and  # blinking
		self.ledCof2 > 300 and self.ledCof2 < 700):  # blinking
			# we have warming
			isWarming = True
		
		if (isWarming):
			self.log.info("The machine is warming up.")
		else:
			self.log.info("The machine is not warming.")
			
		return isWarming
	
	def isMachineOff(self):
		
		# is machine off
		self.log.info("Inside isMachineOff")
		isOff = True
		
		for e in self.indx:
			if (self.dataq7[e] > 100 or self.dataq8[e] > 100):
				isOff = False
				#break
		
		if (isOff):
			self.log.info("The machine is off.")
		else:
			self.log.info("The machine is on.")
		
		self.log.info("Done with isMachineOff. Ret: %s" % isOff)
		
		return isOff
	
	def isReadyToBrew(self):
		
		# is it ready to brew?
		
		# This means the cof and cof dbl lights are on and solid
		# The water out and coffee grinds could also be lit up, but we
		# could still brew because they may have just changed it, however
		# this method only tells you if ALL lights are off
		isReady = False
		
		if (self.dataq7[self.indx[0]] < 100 and # q7/q1
			self.dataq7[self.indx[1]] < 100 and # q7/q2
			self.dataq7[self.indx[2]] < 100 and # q7/q3
			self.dataq7[self.indx[3]] < 100 and # q7/q4
			self.dataq7[self.indx[4]] < 100 and # q7/q5
			self.dataq7[self.indx[5]] < 100 and # q7/q6
			self.dataq8[self.indx[0]] > 1900 and # q8/q1
			self.dataq8[self.indx[1]] > 1900 and # q8/q2
			self.dataq8[self.indx[2]] < 100 and # q8/q3
			self.dataq8[self.indx[3]] < 100 and # q8/q4
			self.dataq8[self.indx[4]] < 100 and # q8/q5
			self.dataq8[self.indx[5]] < 100     # q8/q6
			):
			# yes, ready to brew
			isReady = True
			
		if (isReady):
			self.log.info("The machine is ready to brew.")
		else:
			self.log.info("The machine is not ready to brew.")
		
		return isReady
	
	def isReadyToBrewWithWarnings(self):
		
		# is it ready to brew?
		
		# This means the cof and cof dbl lights are on and solid
		# The water out and coffee grinds could also be lit up, but we
		# could still brew because they may have just refilled the water
		# or added beans, so this warning could be a false alarm
		
		# Really a global memory should be held as to whether we
		# were just in a good state and it went bad, so we would have
		# sent an SMS asking them to fix something
		
		# Somebody could have sent another command in though, so we
		# should always keep track of what the situation was and see
		# if we get these error lights
		isReady = False
		
		dataq7 = self.dataq7
		dataq8 = self.dataq8
		indx = self.indx
		
		if (dataq7[indx[0]] < 100 and # q7/q1
			(dataq7[indx[1]] > 800 and dataq7[indx[1]] < 1200) and # q7/q2
			dataq7[indx[2]] < 100 and # q7/q3
			dataq7[indx[3]] < 100 and # q7/q4
			dataq7[indx[4]] < 100 and # q7/q5
			dataq7[indx[5]] < 100 and # q7/q6
			dataq8[indx[0]] > 1900 and # q8/q1
			dataq8[indx[1]] > 1900 and # q8/q2
			dataq8[indx[2]] < 100 and # q8/q3
			dataq8[indx[3]] < 100 and # q8/q4
			dataq8[indx[4]] < 100 and # q8/q5
			dataq8[indx[5]] < 100     # q8/q6
			):
			# yes, ready to brew
			isReady = True
			
		if (isReady):
			self.log.info("The machine is ready to brew even though it has warning lights.")
		else:
			self.log.info("The machine is not ready to brew (regardless of warnings).")
		
		return isReady

	# Make sure the machine is on before you think you'll get accurate results here
	def analyzeGetError(self, fname):
		
		self.log.info("Inside analyzeGetError()")
		self.startReadingState()
		self.printData()
		self.analyzeData()
		
		ret = self.getError(fname)
		self.log.info("Done analyzeGetError(). Ret: %s" % ret)
		return ret
		

	# Make sure the machine is on before you think you'll get accurate results here
	def getError(self, fname):
		
		msgErr = ""
		isBeansOut = 0
		isWaterOut = 0
		isTrayNeededEmptied = 0
		
		# check some rare situations where multiple lights could blink. catch
		# these first so when we look at individual leds we're in the clear
		if (self.ledWaterOut > 300 and self.ledWaterOut < 700
			and self.ledTray > 300 and self.ledTray < 700
			and self.ledWarning > 300 and self.ledWarning < 700
			and self.ledDecalcify > 300 and self.ledDecalcify < 700):
				
			# we have a situation where all 4 lights are blinking
			msgErr = "I have 4 warning lights going. Usually this means my infuser has been left out of me. Can u pull my power plug and check me?"
		
		elif (self.ledTray > 300 and self.ledTray < 700
			and self.ledWarning > 300 and self.ledWarning < 700):
				
			# we have a situation where all 4 lights are blinking
			msgErr = "I have 2 warning lights going. Usually this means my infuser has been inserted incorrectly. Can u pull my power plug and check me?"

		elif (self.ledCof > 300 and self.ledCof < 700
			and self.ledCof2 > 300 and self.ledCof2 < 700
			and self.ledHotWater > 300 and self.ledHotWater < 700):
				
			# machine switched on and steam know in open position
			msgErr = "Hey, sorry, it looks like my steam knob is open. Can u turn the steam knob clockwise all the way round and resend ur order?"

		elif (self.ledWaterOut > 800):
			
			# The water is clearly out. let user know.
			msgErr = "Hey, sorry, I tried to brew your drink but the water seems to be out. Can u refill it and resend your order?"
			if (len(fname) > 0):
				msgErr = "Hey %s, sorry, I tried to brew your drink but the water seems to be out. Can u refill it and resend your order?" % fname
			
			isWaterOut = 1
			
		elif (self.ledWaterOut > 300 and self.ledWaterOut < 700):
			
			# The water light is blinking. The machine cannot make coffee and is noisy
			msgErr = "My water light is blinking. That usually means steam knob needs turned counter-clockwise or grinding adjustment knob needs to go few clicks clockwise."
			
			isWaterOut = 2
		
		elif (self.ledTray > 800):
			
			# The tray needs emptied
			msgErr = "Hey, sorry, it looks like my tray needs emptied or is not in place. Can u empty or replace it and then resend your order?"
			if (len(fname) > 0):
				msgErr = "Hey %s, sorry, it looks like my tray needs emptied or is not in place. Can u empty or replace it and then resend your order?" % fname
			
			isTrayNeededEmptied = 1
		
		elif (self.ledTray > 300 and self.ledTray < 700):
			
			# This means the tray light is blinking, which indicates no beans
			
			# See if pre-ground button is pushed though
			if (self.ledPreGround > 800):
				# looks like somebody pushed the pre-ground button, that means
				# if we are getting a blinking it's cuz they didn't pour pre-ground beans in
				msgErr = "It looks like the pre-ground coffee btn was pressed, but no beans poured into the funnel. Can u either turn off the pre-ground btn or add grounds then resend?"
			else:
				# if no pre-ground button, then it's the main beans container which is quite
				# common actually. we'll hit this a lot
				msgErr = "Hey, sorry, it looks like I'm out of beans. Can u refill me and then resend your order?"
				if (len(fname) > 0):
					msgErr = "Hey %s, sorry, it looks like I'm out of beans. Can u refill me and then resend your order?" % fname
			
			isBeansOut = 1
			
		elif (self.ledWarning > 800):
			
			# warning light solid
			msgErr = "It looks like my warning light is solid. That may mean my infuser was left out of me or my insides are very dirty. Can u check/clean me and resend?"
		
		elif (self.ledWarning > 300 and self.ledWarning < 700):
			
			# warning light blinking
			msgErr = "It looks like my warning light is blinking. That usually means my service door is open. Can u check me and resend ur order?"
			
		# do additional checks
		elif (self.ledPreGround > 300 and self.ledPreGround < 700):
			
			# pre-ground is blinking which means the fround coffee funnel is clogged
			msgErr = "My pre-ground light is blinking. That usually means the funnel is clogged. Can u check me and resend?"
			
		elif (self.ledDecalcify > 300 and self.ledDecalcify < 700):
			
			# decalcify is blinking
			msgErr = "My decalcification button is lit up. That means I need my lime removed soon. U can keep making coffee, but plz clean me."
		
		d = { "msgErr" : msgErr,
			  "isBeansOut" : isBeansOut,
			  "isTrayNeededEmptied" : isTrayNeededEmptied,
			  "isWaterOut" : isWaterOut,
			  "isErr" : False
			}
			
		self.log.info("We just finished analyzing for errors.")
		if (len(msgErr) > 0):
			d["isErr"] = True
			self.log.info("There were errors. MsgErr: %s" % msgErr)
		return d;

	def printData(self):
		self.log.info("Data Counted on Q7/Q8 for %s milliseconds" % (self.ctrRising * 2))
		#logging.info("CtrRising is at: %s" % ctrRising)
		i = 0
		for e in self.indx:
			self.log.info("(q7 rising) Pin %s (%s) is at count: %s" % (e, self.names[i], self.dataq7[e]))
			#dataR[e] = 0  # reset count
			i = i + 1
		i = 0
		for e in self.indx:
			self.log.info("(q8 rising) Pin %s (%s) is at count: %s" % (e, self.names[i], self.dataq8[e]))
			#dataR[e] = 0  # reset count
			i = i + 1
	
	def exit(self):
		printData()
		analyzeData()
		#RPIO.del_interrupt_callback(4)
		#RPIO.del_interrupt_callback(25)
		sys.exit()
	
def test():
	
	# setup logging
	FORMAT = '%(asctime)s %(levelname)s %(message)s'
	logging.basicConfig(format=FORMAT)
	logger = logging.getLogger()
	logger.setLevel(logging.INFO)
	if not logger.handlers:
		logger.addHandler(logging.StreamHandler())
	log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
	logging.basicConfig(format=log_format, level=logging.INFO)
	
	zwrs = ZwReadState(logger=logger)
	zwrs.startReadingState()
	zwrs.printData()
	zwrs.analyzeData()
	#if (zwrs.isMachineOff()):
		# turn on machine		
	err = zwrs.getError("John")
	if (err["isErr"]):
		logger.info( err)
	else:
		logger.info( "No error on getError()")
	logger.info("Done testing")
	sleep(10)
	
	RPIO.cleanup()
	
#test()
