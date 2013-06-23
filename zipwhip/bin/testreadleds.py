#!/usr/bin/env python
import RPIO
from time import sleep
from array import *
import sys

import logging
log_format = '%(levelname)s | %(asctime)-15s | %(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)

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

# keep track of how many calls
ctrRising = 0

# create data storage for the read of the state
indx = [7, 8, 17, 22, 23, 24]
names = ["q1", "q2", "q3", "q4", "q5", "q6"]
print indx
dataq7 = [0 for x in range(25)]  #array('i')
dataq8 = [0 for x in range(25)]  #array('i')

def on_q7_rising(gpio_id, value):
	
	# we need to scan for the led data
	for e in indx:
		dataq7[e] = dataq7[e] + RPIO.input(e)

def on_q8_rising(gpio_id, value):

	# we need to scan for the led data
	for e in indx:
		dataq8[e] = dataq8[e] + RPIO.input(e)

	# see if it's time to exit after 2 seconds of reading leds
	global ctrRising
	ctrRising = ctrRising + 1
	if (ctrRising >= 2000):
		exit()

def analyzeData():
	
	isOff = isMachineOff()
	isReady = isReadyToBrew()
	isReadyWithWarn = isReadyToBrewWithWarnings()
	
	#if (!isOff):
		# See if it's warming up or ready to make coffee
		
	
def isMachineOff():
	
	# is machine off
	isOff = True
	
	for e in indx:
		if (dataq7[e] > 100 or dataq8[e] > 100):
			isOff = False
			break
	
	if (isOff):
		logging.info("The machine is off.")
	else:
		logging.info("The machine is on.")
	
	return isOff

def isReadyToBrew():
	
	# is it ready to brew?
	
	# This means the cof and cof dbl lights are on and solid
	# The water out and coffee grinds could also be lit up, but we
	# could still brew because they may have just changed it
	isReady = False
	
	if (dataq7[indx[0]] < 100 and # q7/q1
		dataq7[indx[1]] < 100 and # q7/q2
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
		logging.info("The machine is ready to brew.")
	else:
		logging.info("The machine is not ready to brew.")
	
	return isReady

def isReadyToBrewWithWarnings():
	
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
		logging.info("The machine is ready to brew even though it has warning lights.")
	else:
		logging.info("The machine is not ready to brew (regardless of warnings).")
	
	return isReady

def printData():
	logging.info("Data Counted on Q7/Q8 for %s milliseconds" % ctrRising)
	#logging.info("CtrRising is at: %s" % ctrRising)
	i = 0
	for e in indx:
		logging.info("(q7 rising) Pin %s (%s) is at count: %s" % (e, names[i], dataq7[e]))
		#dataR[e] = 0  # reset count
		i = i + 1
	i = 0
	for e in indx:
		logging.info("(q8 rising) Pin %s (%s) is at count: %s" % (e, names[i], dataq8[e]))
		#dataR[e] = 0  # reset count
		i = i + 1

def exit():
	printData()
	analyzeData()
	#RPIO.del_interrupt_callback(4)
	#RPIO.del_interrupt_callback(25)
	sys.exit()

RPIO.add_interrupt_callback(4, on_q8_rising, edge='rising', threaded_callback=False)
RPIO.add_interrupt_callback(25, on_q7_rising, edge='rising', threaded_callback=False)

logging.info("Added callback for pin %s" % 4)
logging.info("Added callback for pin %s" % 25)

try:
	RPIO.wait_for_interrupts()

except KeyboardInterrupt:
	RPIO.cleanup()