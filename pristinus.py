#!/usr/bin/python3

# LIBS
import RPi.GPIO as GPIO
from time import sleep
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

### VARIABLES
LEDstatus=False
# PINS FOR RELAY CONTROL
Relays=[22,23,25]
# PIN FOR BIG RED BUTTON
Emergency=29
# PIN FOR DOOR SWITCH
Door=31
# DEFAULT SLEEP TIME
sleep_d=30
# MAX SLEEP TIME
sleep_max=300
###

# apa102 : available / error / running
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

# Control the relay that starts the UVC LED for a specific amount of time
def relay(on):
    global LEDstatus
    try:
        if on:
            GPIO.output(Relays,GPIO.HIGH)
            LEDstatus=True
            try:
                with open("/tmp/pristinus_sleep.txt","r") as f:
                    sleep_t=int(f.read().strip())
                    if sleep_t>0 and sleep_t<sleep_max: sleep(sleep_t)
                    else: sleep(sleep_d)
            except EnvironmentError:
                sleep(sleep_d)
            GPIO.output(Relays,GPIO.LOW)
        else:
            GPIO.output(Relays,GPIO.LOW)
            LEDstatus=False
    except:  
        apa102("error")
        print("Oops, something wrong occurred!") 
    finally:  
    	GPIO.cleanup()

# Callback for the 
def uvled(why):
    # STATE ?
    sw_state=False
    if GPIO.input(why):
        sw_state=False
        print("Switch is open.")
    else:
        sw_state=True
        print("Switch is closed.")
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
GPIO.add_event_detect(Emergency,GPIO.RISING,callback=uvled,bouncetime=500)
GPIO.add_event_detect(Door,GPIO.BOTH,callback=uvled,bouncetime=500)

# GREEN
apa102("available")

try:
    while True:
        pass
except KeyboardInterrupt:
    print("\nAborted by user")

