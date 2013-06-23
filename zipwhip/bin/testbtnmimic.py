#!/usr/bin/env python
import RPIO
from time import sleep
import sys

import logging
log_format = '%(levelname)s | %(asctime)-15s | %(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)

RPIO.setmode(RPIO.BCM)

# Setup q8 for input
RPIO.setup(4, RPIO.IN, pull_up_down=RPIO.PUD_OFF)	# q8
RPIO.setup(25, RPIO.IN, pull_up_down=RPIO.PUD_OFF)	# q7

# To mimic push button
RPIO.setup(9, RPIO.OUT, initial=RPIO.HIGH) # BTN_COF    (Lower opto)
RPIO.setup(10, RPIO.OUT, initial=RPIO.HIGH) # BTN_ONOFF (Upper opto) always high

btnOnOff = 0 # 0 = don't send, 1 = send push
btnWater = 0
btnCof = 1
btnDecalcify = 0

ctrRising = 0

def on_q8_rising(gpio_id, value):
	#print("gpio_id: %s value: %s" % (gpio_id, value))
	#sleep(0.1)
	if (btnOnOff == 1): 
		RPIO.output(10, True)
	if (btnWater == 1): 
		RPIO.output(10, False)
	if (btnCof == 1):
		RPIO.output(9, True)
	if (btnDecalcify == 1):
		RPIO.output(9, False)
	
	# see if it's time to exit after 2 seconds of pushing button
	global ctrRising
	ctrRising = ctrRising + 1
	if (ctrRising > 2000):
		RPIO.output(9, True)
		RPIO.output(10, True)
		sys.exit()

def on_q7_rising(gpio_id, value):
	#print("gpio_id: %s value: %s" % (gpio_id, value))
	#sleep(0.1)
	if (btnOnOff == 1):
		RPIO.output(10, False)
	if (btnWater == 1):
		RPIO.output(10, True)
	if (btnCof == 1):
		RPIO.output(9, False)
	if (btnDecalcify == 1):
		RPIO.output(9, True)

RPIO.add_interrupt_callback(4, on_q8_rising, edge='rising', threaded_callback=False)
RPIO.add_interrupt_callback(25, on_q7_rising, edge='rising', threaded_callback=False)


logging.info("Added callback for pin %s" % 4)
logging.info("Added callback for pin %s" % 25)

try:
	RPIO.wait_for_interrupts()

except KeyboardInterrupt:
	RPIO.cleanup()
