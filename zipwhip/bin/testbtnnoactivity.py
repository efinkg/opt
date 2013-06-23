#!/usr/bin/env python
import RPIO
from time import sleep

import logging
log_format = '%(levelname)s | %(asctime)-15s | %(message)s'
logging.basicConfig(format=log_format, level=logging.INFO)

RPIO.setmode(RPIO.BCM)

# To mimic push button
RPIO.setup(9, RPIO.OUT, initial=RPIO.HIGH) # BTN_COF    (Lower opto)
RPIO.setup(10, RPIO.OUT, initial=RPIO.HIGH) # BTN_ONOFF (Upper opto) always high