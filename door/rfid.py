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
from storm.locals import *

sys.path.insert(0, '/etc/door')
from all_cards import *

class Entry(object):
    __storm_table__ = 'entries'
    id = Int(primary=True)
    name = Unicode()

database = create_database(sql_server)
store = Store(database)

current_read = []

GPIO.setmode(GPIO.BOARD)

# GPIO 18 - Input 1 from reader
# GPIO 24 - Input 2 from reader
# GPIO 22 - Output (High for Strike open)
input_zeros = 18
input_ones = 24
output = 22
GPIO.setup(input_zeros, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(input_ones, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(output, GPIO.OUT, initial=GPIO.LOW)

def callback_zeros(a):
    current_read.append('0')

def callback_ones(a):
    current_read.append('1')

GPIO.add_event_detect(input_zeros, GPIO.FALLING, callback=callback_zeros)
GPIO.add_event_detect(input_ones, GPIO.FALLING, callback=callback_ones)

def log(severity, message):
    syslog.syslog(
        '[%s] [%s] %s' % (
            strftime("%Y-%m-%d %H:%M:%S", gmtime()),
            severity.upper(),
            message))

def check(current_read, club_member_cards):
    '''
    Checks if a given current read is a valid card.
    If it is, open the strike, wait for 3s, and close the strike.
    Then return true.
    If not, return false.
    '''
    if len(current_read) < 16:
        return None

    print ''.join(current_read)[-17:-1]

    for name, entry in club_member_cards.iteritems():
        if entry['rfid'] == ''.join(current_read)[-17:-1]:
            if entry['active']:
                # Open the strike for 3 seconds, then close and reset current_read.
                GPIO.output(output, GPIO.HIGH)
                time.sleep(3)
                GPIO.output(output, GPIO.LOW)

                log('valid', 'Successful entry by %s' % name)

                # Try logging to SQL, but be careful not to fatal if the sql server goes down.
                try:
                    entry = Entry()
                    entry.name = name
                    store.add(entry)
                    store.flush()
                except Exception as e:
                    log('fatal', 'A fatal has occurred while logging to SQL: %s' % e)

                return name
            else:
                log('unauthorized', 'Unauthorized entry by %s' % name)
    return None

while True:
    del current_read[:]
    time.sleep(1)
    if current_read != '':
        person_name = check(current_read, all_cards)
