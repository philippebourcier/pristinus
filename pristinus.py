#!/usr/bin/python3

# LIBS
import sys
from daemonize import Daemonize
import RPi.GPIO as GPIO
from time import sleep
import requests

### VARIABLES & PINS
pid="/var/run/pristinus.pid"
IsStarted=0
# PIN FOR BIG RED BUTTON
Emergency=17
# PIN FOR DOOR SWITCH
Door=18
##########################

# HTTP GET NO ASYNC WAIT
def httpget(url):
    try:
        requests.get(url,timeout=1)
    except: 
        pass

# Control the relay that starts the UVC LED for a specific amount of time
def relay(state):
    httpget("http://localhost:8000/"+state)

def emerg_sw(who):
    if not GPIO.input(who):
        relay("emerg")
        GPIO.cleanup()
        sys.exit("Now you have to reboot the whole machine...")

def door_sw(who):
    global IsStarted
    if GPIO.input(who):
        if IsStarted==0:
            IsStarted=1
            sleep(1)
            relay("on")
    else:
        if IsStarted==1:
            relay("emerg")
            GPIO.cleanup()
            sys.exit("Now you have to reboot the whole machine...")
        else:
            relay("off")
            sleep(3)
            IsStarted=0

def main():
    # INIT
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    # COUPURE
    GPIO.setup(Emergency,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    GPIO.setup(Door,GPIO.IN,pull_up_down=GPIO.PUD_UP)
    emerg_sw(Emergency)
    GPIO.add_event_detect(Emergency,GPIO.RISING,callback=emerg_sw,bouncetime=50)
    GPIO.add_event_detect(Door,GPIO.BOTH,callback=door_sw,bouncetime=3000)
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nAborted by user")
        relay("off")
        GPIO.cleanup()

if len(sys.argv)==2 and sys.argv[1]=="-d":
    daemon=Daemonize(app="pristinus",pid=pid,action=main)
    daemon.start()
else:
    main()

