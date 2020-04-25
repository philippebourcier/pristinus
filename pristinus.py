#!/usr/bin/python3

import RPi.GPIO as GPIO
from time import sleep

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

LEDstatus=False
Relays=[22,23,25]
Emergency=29
Door=31

# available / error / running
def apa102(scene):
    req=Request("http://localhost/cmd?scene="+scene+"&status=start")
    try:
        response=urlopen(req)
    except HTTPError as e:
        print('Error code: ', e.code)
    except URLError as e:
        print('Reason: ', e.reason)
    else:
        print(scene)

def relay(on):
    global LEDstatus
    if on:
        state=GPIO.HIGH
    else:
        state=GPIO.LOW
    try:
        GPIO.output(Relays,state)
        if on:
            LEDstatus=True
            sleep(20)
            GPIO.output(Relays,GPIO.LOW)
        else: LEDstatus=False
    except:  
        apa102("error")
        print("Oops, something wrong occurred!") 
    finally:  
    	GPIO.cleanup()

def uvled(why):
    # BIG RED BUTTON
    if why==Emergency:
        if LEDstatus:
            relay(False)
            apa102("error")
            sys.exit("Now you have to reboot the whole machine...")
    else:
    # DOOR OPEN/CLOSED
        if LEDstatus:
            relay(False)
            apa102("available")
        else:
            relay(True)
            apa102("running")

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# RELAIS
GPIO.setup(Relays,GPIO.OUT,initial=GPIO.LOW)

# COUPURE
GPIO.setup(Emergency,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(Door,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(Emergency,GPIO.RISING,callback=uvled,bouncetime=200)
GPIO.add_event_detect(Door,GPIO.BOTH,callback=uvled,bouncetime=500)

# GREEN
apa102("available")

try:
    while True:
        pass
except KeyboardInterrupt:
    print("\nAborted by user")

