#!/usr/bin/python3

# LIBS
import RPi.GPIO as GPIO
from time import sleep
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

### VARIABLES
LEDstatus=False
# PINS FOR RELAY CONTROL
Relays=[23,24]
# PIN FOR BIG RED BUTTON
Emergency=17
# PIN FOR DOOR SWITCH
Door=18
# DEFAULT SLEEP TIME
sleep_d=10
# MAX SLEEP TIME
sleep_max=300
###

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# RELAIS
GPIO.setup(Relays,GPIO.OUT,initial=GPIO.LOW)

GPIO.output(Relays,GPIO.HIGH)

sleep(30)

GPIO.output(Relays,GPIO.LOW)
