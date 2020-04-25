#!/usr/bin/python3

# PIN 22
# PIN 23
# PIN 25

import RPi.GPIO as GPIO
from time import sleep

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

LEDstatus=False
Relays=[22,23,25]
Emergency=29
Door=31

def apa102(scene):
    req=Request("http://localhost/cmd?scene="+scene+"&status=start")
    try:
        response = urlopen(req)
    except HTTPError as e:
            print('Error code: ', e.code)
    except URLError as e:
            print('Reason: ', e.reason)
    else:
            print(scene)

def stop():
    try:
        GPIO.output(Relays,GPIO.HIGH)
        apa102("available")


def uvled():
    if(LEDstatus):
        stop()
    else:
        start()

# available / error / running
# get("available")

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# RELAIS
GPIO.setup(Relays,GPIO.OUT,initial=GPIO.LOW)

# COUPURE
GPIO.setup(Emergency,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(Door,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(Emergency,GPIO.BOTH,callback=uvled,bouncetime=200)
GPIO.add_event_detect(Door,GPIO.BOTH,callback=uvled,bouncetime=500)

# GREEN
apa102("available")

while True:
    pass

