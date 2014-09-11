#!/usr/bin/python
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#|R|a|s|p|b|e|r|r|y|P|i|.|c|o|m|.|t|w|
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
# Copyright (c) 2014, raspberrypi.com.tw
# All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# push_button_debounces.py
# Response when push button is clicked with poll way, and de-bounces by software
#
# Author : sosorry
# Date   : 06/22/2014

import RPi.GPIO as GPIO
import time
from time import gmtime, strftime

GPIO.setmode(GPIO.BOARD)
BTN_PIN = 11
TIME_LAPSE = 0.2
GPIO.setup(BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
previousTime = time.time()

try :
        while True:
		currentTime = time.time()
                if GPIO.input(BTN_PIN) == GPIO.LOW and (currentTime - previousTime) > TIME_LAPSE :
			previousTime = currentTime
                        print("Button.Click"), strftime("%Y-%m-%d %H:%M:%S", gmtime())

except KeyboardInterrupt:
	print "Exception: KeyboardInterrupt"

finally:
	GPIO.cleanup()          
