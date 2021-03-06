#!/usr/bin/env python

# University of Akron Amateur Radio Club - W8UPD
# GPLv2+
# Authors:
# - Ricky Elrod <ricky@elrod.me>

import sys
import syslog
import time
import RPi.GPIO as GPIO
from datetime import datetime
from time import gmtime, strftime
import requests
import threading

sys.path.insert(0, '/etc/door')
from all_cards import *

GPIO.setmode(GPIO.BOARD)

door_open = 26
alarm_triggered = 7
GPIO.setup(door_open, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(alarm_triggered, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def log(severity, message):
    syslog.syslog(
        '[%s] [%s] %s' % (
            strftime("%Y-%m-%d %H:%M:%S", gmtime()),
            severity.upper(),
            message))

def log_upstream(event):
    try:
        r = requests.get(
                log_cgi,
                verify=False,
                params={
                    'password': log_cgi_password,
                    'event': event
                })
    except Exception as e:
        log('fatal', 'A fatal has occurred while logging: %s' % e)

last_door_open_callback = None

def callback_door_open(a):
    global last_door_open_callback
    current = GPIO.input(a)
    if current == last_door_open_callback:
        return None
    last_door_open_callback = current

    if current:
        log('info', 'Door opened')
        log_upstream('door_opened')
    else:
        log('info', 'Door closed')
        log_upstream('door_closed')

last_alarm_triggered_callback = 0

def callback_alarm_triggered(a):
    global last_alarm_triggered_callback
    current = time.time()
    if current <= last_alarm_triggered_callback + 10:
        return None
    last_alarm_triggered_callback = current

    log('info', 'Alarm triggered')
    log_upstream('alarm_triggered')

GPIO.add_event_detect(door_open, GPIO.BOTH, callback=callback_door_open)
GPIO.add_event_detect(alarm_triggered, GPIO.RISING, callback=callback_alarm_triggered, bouncetime=250)

while True:
    # Wait for callbacks
    time.sleep(0.5)
