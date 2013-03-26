#!/usr/bin/env python

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Authors:
# - Ricky Elrod <ricky@elrod.me>

import time
import RPi.GPIO as GPIO
from all_cards import all_cards

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

def check(current_read, club_member_cards):
    '''
    Checks if a given current read is a valid card.
    If it is, open the strike, wait for 3s, and close the strike.
    Then return the person's name.
    If not, return false.
    '''
    if len(current_read) < 16:
        return None

    for name, card in club_member_cards.iteritems():
        if card == ''.join(current_read)[-17:-1]:
            # Open the strike for 3 seconds, then close and reset current_read.
            GPIO.output(output, GPIO.HIGH)
            time.sleep(3)
            GPIO.output(output, GPIO.LOW)
            return name
    return None

while True:
    time.sleep(1)
    person_name = check(current_read, all_cards)
    if person_name:
        # Clear the previous read
        del current_read[:]
        # TODO: Logging?
        #log('%s has unlocked the door.' % person_name)
    else:
        #log('An attempted login occurred at %s.' % date)
        continue # TODO: Remove this when this else is actually used.
