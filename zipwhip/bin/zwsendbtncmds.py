import RPIO
from time import sleep
import sys
import time

import logging

class ZwSendBtnCmds:
	
	def __init__(self, 
				logger = None,
				clientid = None, sessionid = None,
				):
		# define properties
		# define properties
		if (logger == None):
			logger = logging.getLogger("zwsendbtncmds")
			logger.setLevel(logging.DEBUG)
			formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
			handler = logging.FileHandler("/opt/zipwhip/log/zipwhip-textspresso.log")
			handler.setFormatter(formatter)
			logger.addHandler(handler)
			self.log = logger
		else:
			self.log = logger

		RPIO.setmode(RPIO.BCM)
		
		# Setup q8/q7 for input
		RPIO.setup(4, RPIO.IN, pull_up_down=RPIO.PUD_OFF)	# q8
		RPIO.setup(25, RPIO.IN, pull_up_down=RPIO.PUD_OFF)	# q7
		
		# To mimic push button
		# By default send a HIGH value on both channels to the opto-coupler
		# that sends the button push mimic. This turns the LED on inside the opto
		# which pulls the 5v pull-up resistor to GND. That keeps no noise on the
		# button push signal lines. Once we go LOW on these GPIO ports it turns
		# the LEDs off in the opto-coupler. This makes the photo transistor on the
		# other side float, which means the 5V pull-up resistor pulls the button
		# signal line to a full 5V. If we toggle this on/off at the exact square 
		# wave the espresso machine expects, we can mimic the button push.
		RPIO.setup(9, RPIO.OUT, initial=RPIO.HIGH) # BTN_COF    (Lower opto)
		RPIO.setup(10, RPIO.OUT, initial=RPIO.HIGH) # BTN_ONOFF (Upper opto) always high
		self.log.info("Set GPIO 9 & 10 high so we don't send incorrect button pushes to espresso machine from the start.")
		
		self.btnOnOff = 0 # 0 = don't send, 1 = send push
		self.btnWater = 0
		self.btnCof = 0
		self.btnDecalcify = 0
		
		# global ctr for callbacks
		self.ctrRising2 = 0
		
		# create callbacks that will get called to register counts
		#RPIO.add_interrupt_callback(4, self.on_q8_rising_btn, edge='rising', threaded_callback=False)
		#RPIO.add_interrupt_callback(25, self.on_q7_rising_btn, edge='rising', threaded_callback=False)


	def reset(self):
		self.btnOnOff = 0
		self.btnWater = 0
		self.btnCof = 0
		self.btnDecalcify = 0

	def pushOnOffBtn(self):
		self.log.info("Pushing button for On/Off.")
		self.reset()
		self.btnOnOff = 1
		self.sendBtnPush()

	def pushCofBtn(self):
		self.log.info("Pushing button for Coffee.")
		self.reset()
		self.btnCof = 1
		self.sendBtnPush()

	def pushWaterBtn(self):
		self.log.info("Pushing button for Water.")
		self.reset()
		self.btnWater = 1
		self.sendBtnPush()

	def pushDecalcifyBtn(self):
		self.log.info("Pushing button for Decalcify.")
		self.reset()
		self.btnDecalcify = 1
		self.sendBtnPush()
		
	def sendBtnPush(self):
		
		# reset ctr so we get a full count
		self.ctrRising2 = 0
		
		# create callbacks that will get called to register counts
		# when we get to a count of 2000 these callbacks will call sendBtnPushDone()
		RPIO.add_interrupt_callback(4, self.on_q8_rising_btn, edge='rising', threaded_callback=False)
		RPIO.add_interrupt_callback(25, self.on_q7_rising_btn, edge='rising', threaded_callback=False)
		
		self.log.info("Inside sendBtnPush(). Added callback for buttons to read square wave for pin %s" % 4)
		self.log.info("Inside sendBtnPush(). Added callback for buttons to read square wave for pin %s" % 25)
		
		RPIO.wait_for_interrupts()
		self.log.info("Inside sendBtnPush(). We just got passed RPIO.wait_for_interrupts() which is awesome cuz thought blocking here never ended.")
		
		# now remove the callbacks because we're done sending and no need
		# to keep the load on our script of handling callcacks
		RPIO.del_interrupt_callback(4)
		RPIO.del_interrupt_callback(25)
		self.log.info("Removed interrupt callbacks for GPIO 4 and 25 for button pushing.")

		# Make sure to send high to opto-coupler to ensure
		# espresso side is back to low
		RPIO.output(9, True)
		RPIO.output(10, True)
		
		'''
		# make sure our ctrRising hasn't changed in a second or so
		start_time = time.time()
		elapsed_time = 0
		loc_ctr = self.ctrRising2
		self.log.info("Going to do yield loop for 1 second. Seems to ensure all callbacks are completed before I return.")
		loopCtr = 0
		while (elapsed_time < 1):
			loopCtr += 1
			# if we are having a moving ctrRising, reset our start time. i want 1 full second
			# of no movement on ctrRising
			if (loc_ctr != self.ctrRising2):
				self.log.info("ctrRising2 was still changing. resetting start_time to now to extend our wait.")
				start_time = time.time()
			sleep(0.001)
			#self.log.info("In yield loop to make sure all our interrupt callbacks came back. self.ctrRising: %s, elapsed_time: %s" % (self.ctrRising, elapsed_time))
			elapsed_time = time.time() - start_time
		self.log.info("Returning from startReadingState(). Done with yield loop. Looped: %s" % loopCtr)
		'''
		
	def sendBtnPushDone(self):

		# Make sure to send high to opto-coupler to ensure
		# espresso side is back to low
		RPIO.output(9, True)
		RPIO.output(10, True)
		
		self.log.info("Inside sendBtnPushDone(). Done pushing button.")
		# we just finished reading state
		self.log.info("Inside sendBtnPushDone(). ctrRising2 after reading all state is: %s" % self.ctrRising2)

		'''
		# make sure our ctrRising hasn't changed in a second or so
		start_time = time.time()
		elapsed_time = 0
		loc_ctr = self.ctrRising2
		self.log.info("sendBtnPushDone(). Going to do yield loop for 1 second. Seems to ensure all callbacks are completed before I return.")
		loopCtr = 0
		while (elapsed_time < 1):
			loopCtr += 1
			# if we are having a moving ctrRising, reset our start time. i want 1 full second
			# of no movement on ctrRising
			if (loc_ctr != self.ctrRising2):
				self.log.info("ctrRising2 was still changing. resetting start_time to now to extend our wait.")
				start_time = time.time()
			sleep(0.001)
			#self.log.info("In yield loop to make sure all our interrupt callbacks came back. self.ctrRising: %s, elapsed_time: %s" % (self.ctrRising, elapsed_time))
			elapsed_time = time.time() - start_time
		self.log.info("Returning from sendBtnPushDone(). Done with yield loop. Looped: %s" % loopCtr)
		'''
		RPIO.stop_waiting_for_interrupts()
		self.log.info("Inside sendBtnPushDone(). Just did stop_waiting_for_interrupts(). This should let sendBtnPush() continue on from it's blocking.")

	def cleanup(self):
		RPIO.cleanup()

	def on_q8_rising_btn(self, gpio_id, value):
		#print("gpio_id: %s value: %s" % (gpio_id, value))
		#sleep(0.1)
		if (self.btnOnOff == 1): 
			RPIO.output(10, True)
		if (self.btnWater == 1): 
			RPIO.output(10, False)
		if (self.btnCof == 1):
			RPIO.output(9, True)
		if (self.btnDecalcify == 1):
			RPIO.output(9, False)
		
		# see if it's time to exit after 2 seconds of pushing button
		#global ctrRising
		self.ctrRising2 = self.ctrRising2 + 1
		if (self.ctrRising2 == 2000):
			self.sendBtnPushDone()
			#sys.exit()
	
	def on_q7_rising_btn(self, gpio_id, value):
		#print("gpio_id: %s value: %s" % (gpio_id, value))
		#sleep(0.1)
		if (self.btnOnOff == 1):
			RPIO.output(10, False)
		if (self.btnWater == 1):
			RPIO.output(10, True)
		if (self.btnCof == 1):
			RPIO.output(9, False)
		if (self.btnDecalcify == 1):
			RPIO.output(9, True)
	
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
	
	#stats = ZwStats(logger=logger)
	zwbtn = ZwSendBtnCmds(logger=logger)
	#zwbtn.pushCofBtn()
	zwbtn.pushWaterBtn()

#test()
