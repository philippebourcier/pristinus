#!/usr/bin/python3

from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading
import RPi.GPIO as GPIO
from time import sleep
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import sys

### VARIABLES & PINS
pid="/var/run/relayd.pid"
ON=True
OFF=False
# PINS FOR RELAY CONTROL (23-24) DEFINED IN /opt/pristinus/data/pristinus_relays.txt
# DEFAULT SLEEP TIME
sleep_d=40
# MAX SLEEP TIME
sleep_max=300
##########################

def httpget(url):
    try:
        requests.get(url,timeout=1)
    except requests.exceptions.ReadTimeout:
        pass

# sleep for some seconds...
def cusleep():
    try:
        with open("/opt/pristinus/data/pristinus_sleep.txt","r") as f:
            sleep_t=int(f.read().strip())
            if sleep_t>=10 and sleep_t<sleep_max: sleep(sleep_t)
            else: sleep(sleep_d)
    except EnvironmentError:
        sleep(sleep_d)

# apa102 : available / error / running
def apa102(scene):
    httpget("http://localhost/cmd?scene="+scene+"&status=start")

# Control the relay that starts the UVC LED for a specific amount of time
def relay(state):
    try:
        # INIT
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
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

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        if self.path == "/on":
            relay(ON)
            self.wfile.write("ON".encode('utf-8'))
        elif self.path == "/off":
            relay(OFF)
            apa102("available")
            self.wfile.write("OFF".encode('utf-8'))
        elif self.path == "/emerg":
            relay(OFF)
            apa102("error")
            self.wfile.write("EMERG".encode('utf-8'))
            GPIO.cleanup()
            sys.exit("Now you have to reboot the whole machine...")
        else :
            self.wfile.write("".encode('utf-8'))

class ThreadingSimpleServer(ThreadingMixIn,HTTPServer): pass

def run():
    server=ThreadingSimpleServer(('127.0.0.1',8000),Handler)
    server.serve_forever()

if __name__ == '__main__':
    try:
    	run()
    except KeyboardInterrupt:
        print('\nFinished.')

