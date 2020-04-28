#!/usr/bin/python3

# LIBS
import sys
from daemonize import Daemonize
import RPi.GPIO as GPIO
from time import sleep
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from datetime import datetime

### VARIABLES & PINS
pid="/var/run/pristinus.pid"
ON=True
OFF=False
IsStarted=0
# PINS FOR RELAY CONTROL (23-24) DEFINED IN /opt/pristinus/data/pristinus_relays.txt
# PIN FOR BIG RED BUTTON
Emergency=17
# PIN FOR DOOR SWITCH
Door=18
# DEFAULT SLEEP TIME
sleep_d=40
# MAX SLEEP TIME
sleep_max=300
##########################

# apa102 : available / error / running
def apa102(scene):
    req=Request("http://localhost/cmd?scene="+scene+"&status=start")
    try:
        response=urlopen(req,None,3)
    except HTTPError as e:
        print('Error code: ', e.code)
    except URLError as e:
        print('Reason: ', e.reason)
    else:
        print(scene)

# sleep for some seconds...
def cusleep():
    try:
        with open("/opt/pristinus/data/pristinus_sleep.txt","r") as f:
            sleep_t=int(f.read().strip())
            if sleep_t>=10 and sleep_t<sleep_max: sleep(sleep_t)
            else: sleep(sleep_d)
    except EnvironmentError:
        sleep(sleep_d)

# Control the relay that starts the UVC LED for a specific amount of time
def relay(state):
    try:
        with open("/opt/pristinus/data/pristinus_relays.txt","r") as f: RelaysStr=f.read().splitlines()
        Relays=list(map(int,RelaysStr))
        GPIO.setup(Relays,GPIO.OUT,initial=GPIO.LOW)
        if state:
            apa102("running")
            GPIO.output(Relays,GPIO.HIGH)
            print("On allume XXs les LEDs...")
            cusleep()
            GPIO.output(Relays,GPIO.LOW)
            print("On éteint les LEDs")
            apa102("available")
        else:
            GPIO.output(Relays,GPIO.LOW)
            print("On éteint les LEDs")
    except Exception as e:
        apa102("error")
        print(e)
        print("Oops, something wrong occurred!")
        sys.exit("Now you have to reboot the whole machine...")

def emerg_sw(who):
    if not GPIO.input(who):
        relay(OFF)
        GPIO.cleanup()
        apa102("error")
        sys.exit("Now you have to reboot the whole machine...")

def door_sw(who):
    global IsStarted
    if GPIO.input(who):
            if IsStarted==0:
                IsStarted=1
                print("Door is closed => relay ON")
                sleep(1)
                relay(ON)
    else:
        print("Door is opened => relay OFF")
        relay(OFF)
        apa102("available")
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
    apa102("available")
    GPIO.add_event_detect(Emergency,GPIO.RISING,callback=emerg_sw,bouncetime=50)
    GPIO.add_event_detect(Door,GPIO.BOTH,callback=door_sw,bouncetime=3000)

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nAborted by user")
        relay(OFF)
        GPIO.cleanup()

main()

#daemon=Daemonize(app="pristinus",pid=pid,action=main)
#daemon.start()

