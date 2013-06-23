#!/usr/bin/env python
from time import sleep
#import RPi.GPIO as GPIO
import RPIO
#import testthread
from array import *

import logging
log_format = '%(levelname)s | %(asctime)-15s | %(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)

#RPIO.cleanup()
RPIO.setmode(RPIO.BCM)

# We are using pins 8 and 9
# BCM mode Pin 2, BOARD mode Pin 8 INPUT is for the button detect for resetting wifi.
# BCM mode Pin 3, BOARD mode Pin 9 OUTPUT is for sending a voltage to the NPN transistor to turn on the relay

# set up GPIO input with pull-up control
#   (pull_up_down be PUD_OFF, PUD_UP or PUD_DOWN, default PUD_OFF)

# We need pulldown so no float, when btn pushed this input will go high
#GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# set up input channel with pull-up control
#   (pull_up_down be PUD_OFF, PUD_UP or PUD_DOWN, default PUD_OFF)
pinCb = 25;
# To read the state of LEDs off shift register

RPIO.setup(7, RPIO.IN, pull_up_down=RPIO.PUD_OFF)	# q1
RPIO.setup(8, RPIO.IN, pull_up_down=RPIO.PUD_OFF)	# q2
RPIO.setup(17, RPIO.IN, pull_up_down=RPIO.PUD_OFF)	# q3
RPIO.setup(22, RPIO.IN, pull_up_down=RPIO.PUD_OFF)	# q4
RPIO.setup(23, RPIO.IN, pull_up_down=RPIO.PUD_OFF)	# q5
RPIO.setup(24, RPIO.IN, pull_up_down=RPIO.PUD_OFF)	# q6
RPIO.setup(25, RPIO.IN, pull_up_down=RPIO.PUD_OFF)	# q7
RPIO.setup(4, RPIO.IN, pull_up_down=RPIO.PUD_OFF)	# q8
# Two control pins for mimic of push button
#RPIO.setup(9, RPIO.OUT, initial=RPIO.HIGH)
#RPIO.setup(10, RPIO.OUT, initial=RPIO.HIGH)
# To read button push state
RPIO.setup(11, RPIO.IN, pull_up_down=RPIO.PUD_DOWN)

# To mimic push button
RPIO.setup(9, RPIO.OUT, initial=RPIO.HIGH) # BTN_COF    (Lower opto)
RPIO.setup(10, RPIO.OUT, initial=RPIO.HIGH) # BTN_ONOFF (Upper opto) always high
#RPIO.setup(9, RPIO.IN, pull_up_down=RPIO.PUD_DOWN)
#RPIO.setup(10, RPIO.IN, pull_up_down=RPIO.PUD_DOWN)
btnOnOff = 1 # 0 = don't send, 1 = send push

#global ctr
#ctr = 0
ctrRising = 0
ctrFalling = 0
#global index
indx = [7, 8, 17, 22, 23, 24, 4]
#indx = [7]
names = ["q1", "q2", "q3", "q4", "q5", "q6", "Q8"]
print indx
#index = array('i' [7, 8, 17, 22, 23, 24, 25])
#global c
#data = [0 for x in range(30)]  #array('i')
dataR = [0 for x in range(30)]  #array('i')
dataF = [0 for x in range(30)]  #array('i')

def do_something(gpio_id, value):
	logging.info("New value for GPIO %s: %s" % (gpio_id, value))
	# read input from gpio 7
	#input_value = RPIO.input(17)
	#logging.info("Read value for GPIO %s: %s" % (gpio_id, input_value))

def on_falling(gpio_id, value):
	global ctr
	ctr = ctr + 1
	#logging.info("Falling")
	#input_value = RPIO.input(17)
	#logging.info("Read value for GPIO %s: %s" % (gpio_id, input_value))

def on_rising(gpio_id, value):
	global ctr
	ctr = ctr + 1
	#logging.info("Rising")
	if (ctr % 1000 == 0):
		logging.info("Ctr is at: %s" % ctr)
	#input_value = RPIO.input(17)
	#logging.info("Read value for GPIO %s: %s" % (gpio_id, input_value))

def on_q8_rising(gpio_id, value):
	#print("gpio_id: %s value: %s" % (gpio_id, value))
	global ctr
	ctr = ctr + 1
	#logging.info("Rising")
	# we need to scan for other data
	for e in indx:
		data[e] = data[e] + RPIO.input(e)
	if (ctr % 1000 == 0):
		logging.info("Ctr is at: %s" % ctr)
		i = 0
		for e in indx:
			logging.info("Pin %s (%s) is at count: %s" % (e, names[i], data[e]))
			data[e] = 0  # reset count
			i = i + 1

def on_q7_both(gpio_id, value):
	# we get called here for both rise & fall
	# so figure out if we're falling and if so dish it off
	if (RPIO.input(gpio_id) == 0):
		# we're falling so call falling method
		on_q7_falling(gpio_id, value)
	else:
		on_q7_rising(gpio_id, value)

def on_q7_rising(gpio_id, value):
	#print("gpio_id: %s value: %s" % (gpio_id, value))
	global ctrRising
	ctrRising = ctrRising + 1

	#logging.info("Rising")
	# we need to scan for other data
	for e in indx:
		dataR[e] = dataR[e] + RPIO.input(e)

	# Mimic push btn for on/off
	if (btnOnOff == 1):
		# mimic it. so when q7 is rising we want to go low
		RPIO.output(10, False)

	if (ctrRising % 2000 == 0):
		logging.info("CtrRising is at: %s" % ctrRising)
		ctrRising = 0
		i = 0
		for e in indx:
			logging.info("(Rising) Pin %s (%s) is at count: %s" % (e, names[i], dataR[e]))
			dataR[e] = 0  # reset count
			i = i + 1

def on_q7_falling(gpio_id, value):
	#print("gpio_id: %s value: %s" % (gpio_id, value))
	global ctrFalling
	ctrFalling = ctrFalling + 1

	#logging.info("Rising")
	# we need to scan for other data
	for e in indx:
		dataF[e] = dataF[e] + RPIO.input(e)
	
	# Mimic push btn for on/off
	if (btnOnOff == 1):
		# mimic it. so when q7 is falling we want to go high
		RPIO.output(10, True)

	if (ctrFalling % 2000 == 0):
		logging.info("CtrFalling is at: %s" % ctrFalling)
		ctrFalling = 0
		i = 0
		for e in indx:
			logging.info("(Falling) Pin %s (%s) is at count: %s" % (e, names[i], dataF[e]))
			dataF[e] = 0  # reset count
			i = i + 1

def on_rising_all(gpio_id, value):
	#global index
	#global c
	global ctr
	ctr = ctr + 1
	data[gpio_id] = data[gpio_id] + 1
	#logging.info("Rising")
	if (ctr % 5000 == 0):
		logging.info("Ctr is at: %s" % ctr)
		for e in indx:
			logging.info("Pin %s is at count: %s" % (e, data[e]))

#RPIO.add_interrupt_callback(17, on_rising, edge='rising', threaded_callback=False)
#RPIO.add_interrupt_callback(pinCb, on_rising, edge='rising', threaded_callback=False)

#print indx
#for e in indx:
#	print e
#	RPIO.add_interrupt_callback(e, on_rising_all, edge='rising', threaded_callback=False)
#	logging.info("Added callback for pin %s" % e)
	
#do_something(17, -1)
#RPIO.add_interrupt_callback(25, on_q8_rising, edge='both', threaded_callback=False)
RPIO.add_interrupt_callback(25, on_q7_both, edge='both', threaded_callback=False)
#RPIO.add_interrupt_callback(25, on_q7_falling, edge='falling', threaded_callback=False)
logging.info("Added callback for pin %s" % 25)	
#logging.info("About to wait for interrupts")
logging.info("About to wait for 2 separate interrupts. Rising and Falling.")
try:
	#pingPongThread = testthread.PingPongThreadClass()
	#pingPongThread.setDaemon(True)
	#pingPongThread.start()
	RPIO.wait_for_interrupts()
	
	#while(True):
		#RPIO.wait_for_interrupts()
	
		# sleep for 1 second and see how many interrupts i get
		#sleep(1)
	
		#logging.info("Ctr after 1s is at: %s" % ctr)

except KeyboardInterrupt:
	RPIO.cleanup()
