""" rpi-gpio-kbrd.py by Chris Swan 9 Aug 2012
GPIO Keyboard driver for Raspberry Pi for use with 80s 5 switch joysticks
*** This did not work with AdvMAME - failed attempt - may be useful for another project
based on python-uinput/examples/keyboard.py by tuomasjjrasanen
https://github.com/tuomasjjrasanen/python-uinput/blob/master/examples/keyboard.py
requires uinput kernel module (sudo modprobe uinput)
requires python-uinput (git clone https://github.com/tuomasjjrasanen/python-uinput)
requires (from http://pypi.python.org/pypi/RPi.GPIO/0.3.1a)
for detailed usage see http://blog.thestateofme.com/2012/08/10/raspberry-pi-gpio-joystick/
"""

import uinput
import time
import RPi.GPIO as GPIO
import spidev
import os
from time import gmtime, strftime

GPIO.setmode(GPIO.BOARD)
JUMP_PIN = 12
FIRE_PIN = 11
GPIO_TRIGGER = 16
GPIO_ECHO    = 18
BOUNCE_TIME = 200 
GPIO.setup(JUMP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(FIRE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_TRIGGER,GPIO.OUT)  # Trigger
GPIO.setup(GPIO_ECHO,GPIO.IN)      # Echo
GPIO.output(GPIO_TRIGGER, False)

d = [0, 0, 0]
counter = 0
min_trigger = 3
max_trigger = 6
max_distance = 40
min_distance = 7
max_stay = 1


def measure():
	GPIO.output(GPIO_TRIGGER, True)
	time.sleep(0.00001)
	GPIO.output(GPIO_TRIGGER, False)
	start = time.time()

	while GPIO.input(GPIO_ECHO)==0:
		start = time.time()

	while GPIO.input(GPIO_ECHO)==1:
		stop = time.time()

	elapsed = stop-start
	distance = (elapsed * 34300)/2

	return distance

def measure_average():
	distance1=measure()
	time.sleep(0.1)
	distance2=measure()
	time.sleep(0.1)
	distance3=measure()
	distance = distance1 + distance2 + distance3
	distance = distance / 3
	return distance


events = (uinput.KEY_DOWN, uinput.KEY_UP, uinput.KEY_LEFT, uinput.KEY_RIGHT, uinput.KEY_X, uinput.KEY_Z, uinput.KEY_ENTER)
device = uinput.Device(events)

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)

def callback_function(channel):    
	#print("Button.Click"), strftime("%Y-%m-%d %H:%M:%S", gmtime())
	
	if channel == JUMP_PIN :
		device.emit(uinput.KEY_X, 1) # Press Up key
		time.sleep(0.2)
		device.emit(uinput.KEY_X, 0) # Press Up key
	elif channel == FIRE_PIN :
		device.emit(uinput.KEY_Z, 1) # Press Up key
		time.sleep(0.2)
		device.emit(uinput.KEY_Z, 0) # Press Up key
	else :
		pass

# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = ((adc[1]&3) << 8) + adc[2]
  return data

# Define sensor channels
# (channels 3 to 7 unused)
swt_channel = 0
vrx_channel = 1 
vry_channel = 2 

try:
        GPIO.add_event_detect(JUMP_PIN, GPIO.FALLING, callback=callback_function, bouncetime=BOUNCE_TIME)
        GPIO.add_event_detect(FIRE_PIN, GPIO.FALLING, callback=callback_function, bouncetime=BOUNCE_TIME)

        while True:

		distance = measure_average()
		print "Distance : %.1f" % distance

		d [counter % 3] = round( distance, 1 )
		d0  = d[counter %3]
		d1 = d[(counter-1) %3]
		d2 = d[(counter-2) %3]

		if round(distance, 1) > min_distance and round(distance, 1) < max_distance :
		
			device.emit(uinput.KEY_Z, 1) # Press Up key

			if (d0 - d1 < max_stay) and (d1 - d2 > min_trigger) and (d1 - d2 < max_trigger) :

				print d
			
				time.sleep(0.2)
				device.emit(uinput.KEY_Z, 0) # Press Up key

		counter = counter + 1;


                vrx_pos = ReadChannel(vrx_channel)
                vry_pos = ReadChannel(vry_channel)
                swt_val = ReadChannel(swt_channel)

                #device.emit(uinput.KEY_RIGHT, 1) # Press Up key
                #if vrx_pos < 100:
                #       move_forward()
                #       print("vrx_pos < 100")

                # Print out results
                #print "--------------------------------------------"  
                #print("X : {}  Y : {}  Switch : {}".format(vrx_pos,vry_pos,swt_val))

                #if vrx_pos > 900 :
                #        device.emit(uinput.KEY_X, 0) 
                #        device.emit(uinput.KEY_DOWN, 1) 
                #elif vrx_pos < 100 :
                #        device.emit(uinput.KEY_X, 1) 
                #        device.emit(uinput.KEY_DOWN, 0) 
                #else :
                #        device.emit(uinput.KEY_X, 0) 
                #        device.emit(uinput.KEY_DOWN, 0) 

		# x
                if vry_pos > 750 :
                        device.emit(uinput.KEY_RIGHT, 0) 
                        device.emit(uinput.KEY_LEFT, 1) 
                elif vry_pos < 100 :
                        device.emit(uinput.KEY_RIGHT, 1) 
                        device.emit(uinput.KEY_LEFT, 0) 
                else :
                        device.emit(uinput.KEY_RIGHT, 0) 
                        device.emit(uinput.KEY_LEFT, 0) 

		# y
                if vrx_pos > 750 :
                        device.emit(uinput.KEY_UP, 0) 
                        device.emit(uinput.KEY_DOWN, 1) 
                elif vrx_pos < 100 :
                        device.emit(uinput.KEY_UP, 1) 
                        device.emit(uinput.KEY_DOWN, 0) 
                else :
                        device.emit(uinput.KEY_UP, 0) 
                        device.emit(uinput.KEY_DOWN, 0) 

		# enter
		if swt_val < 100 :
                        device.emit(uinput.KEY_ENTER, 1)
		else :
                        device.emit(uinput.KEY_ENTER, 0)


                time.sleep(0.2)
    		#device.emit(uinput.KEY_X, 0) # Press Up key


except KeyboardInterrupt:
        GPIO.cleanup()    

