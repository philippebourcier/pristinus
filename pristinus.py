#!/usr/bin/python3

# LIBS
import sys
from daemonize import Daemonize
import RPi.GPIO as GPIO
from time import sleep
import requests
import os
from signal import pause

### VARIABLES & PINS
pid="/var/run/pristinus.pid"
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

# HTTP GET STATUS OF UVC LEDS
def getstatus():
    try:
        r=requests.get("http://localhost:8000/status",timeout=5)
        return r.text.strip()
    except:
        return True
        pass

# Control the relay that starts the UVC LED for a specific amount of time
def relay(state):
    httpget("http://localhost:8000/"+state)

def emerg_sw(who):
    if not GPIO.input(who):
        relay("emerg")
        #GPIO.cleanup()
        #sys.exit("Now you have to reboot the whole machine...")
    else:
        if getstatus()=="STOPPED":
            os.system('systemctl reboot')

def door_sw(who):
    if GPIO.input(who):
        if getstatus()=="False":
            sleep(1)
            relay("on")
    else:
        if getstatus()=="False":
            relay("off")
            sleep(3)
        else:
            relay("emerg")
            #GPIO.cleanup()
            #sys.exit("Now you have to reboot the whole machine...") 

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
            pause()
    except KeyboardInterrupt:
        print("\nAborted by user")
        relay("off")
        GPIO.cleanup()

if len(sys.argv)==2 and sys.argv[1]=="-d":
    daemon=Daemonize(app="pristinus",pid=pid,action=main)
    daemon.start()
else:
    main()

