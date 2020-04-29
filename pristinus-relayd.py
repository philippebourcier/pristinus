#!/usr/bin/python3

from daemonize import Daemonize
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import RPi.GPIO as GPIO
from time import sleep
import os
import sys
import requests

### VARIABLES & PINS
pid="/var/run/pristinus-relayd.pid"
ON=True
OFF=False
BigRedButton=False
IsStarted=False
# PINS FOR RELAY CONTROL (23-24) DEFINED IN /opt/pristinus/data/pristinus_relays.txt
# DEFAULT SLEEP TIME
sleep_d=40
# MAX SLEEP TIME
sleep_max=300
##########################

def httpget(url):
    try:
        requests.get(url,timeout=3)
    except:
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
def relay(start):
    try:
        # INIT
        global IsStarted
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        with open("/opt/pristinus/data/pristinus_relays.txt","r") as f: RelaysStr=f.read().splitlines()
        Relays=list(map(int,RelaysStr))
        GPIO.setup(Relays,GPIO.OUT,initial=GPIO.LOW)
        if start:
            IsStarted=True
            apa102("running")
            GPIO.output(Relays,GPIO.HIGH)
            print("On allume XXs les LEDs...")
            cusleep()
            print("On éteint les LEDs")
            GPIO.output(Relays,GPIO.LOW)
            sleep(2)
            IsStarted=False
        else:
            GPIO.output(Relays,GPIO.LOW)
            print("On éteint les LEDs")
    except Exception as e:
        apa102("error")
        print(e)
        print("Oops, something wrong occurred!")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global BigRedButton
        global IsStarted
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        if not BigRedButton:
            if self.path == "/on":
                relay(ON)
                if not BigRedButton: apa102("available")
                self.wfile.write("ON".encode('utf-8'))
            elif self.path == "/off":
                relay(OFF)
                apa102("available")
            elif self.path == "/status":
                self.wfile.write(str(IsStarted).encode('utf-8'))
            elif self.path == "/emerg":
                BigRedButton=True
                relay(OFF)
                apa102("error")
                self.wfile.write("EMERG".encode('utf-8'))
            else:
                self.wfile.write("".encode('utf-8'))
        else:
            self.wfile.write("STOPPED".encode('utf-8'))
    def log_message(self,format,*args):
        return

class ThreadingSimpleServer(ThreadingMixIn,HTTPServer): pass

def main():
    try:
        apa102("available")
        server=ThreadingSimpleServer(('127.0.0.1',8000),Handler)
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nFinished.')

if len(sys.argv)==2 and sys.argv[1]=="-d":
    daemon=Daemonize(app="pristinus-relayd",pid=pid,action=main)
    daemon.start()
else:
    main()

