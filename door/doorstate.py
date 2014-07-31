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
GPIO.setup(door_open, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
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

def callback_door_open(a):
    log_upstream('door_opened')

def callback_alarm_triggered(a):
    log_upstream('alarm_triggered')

def callback_door_closed(a):
    log_upstream('door_closed')

def callback_alarm_silenced(a):
    log_upstream('alarm_silenced')

GPIO.add_event_detect(door_open, GPIO.RISING, callback=callback_door_open)
GPIO.add_event_detect(alarm_triggered, GPIO.RISING, callback=callback_alarm_triggered)
GPIO.add_event_detect(door_open, GPIO.FALLING, callback=callback_door_closed)
GPIO.add_event_detect(alarm_triggered, GPIO.FALLING, callback=callback_alarm_silenced)

while True:
    # Wait for callbacks
