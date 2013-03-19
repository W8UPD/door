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

import time
import RPi.GPIO as GPIO

current_read = ''

GPIO.setmode(GPIO.BOARD)

# GPIO 8 - Input 1 from reader
# GPIO 10 - Input 2 from reader
# GPIO 12 - Output (High for Strike open)
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW)

GPIO.add_event_detect(8, GPIO.RISING, callback=lambda: current_read += '1')
GPIO.add_event_detect(10, GPIO.RISING, callback=lambda: current_read += '0')

def check(current_read, club_member_cards):
    '''
    Checks if a given current read is a valid card.
    If it is, open the strike, wait for 3s, and close the strike.
    Then return the person's name.
    If not, return None.
    '''
    if len(current_read) < 16:
        return None

    scanned_card = current_read[-17:-1]
    
    for name, card in club_member_cards:
        if card == scanned_card:
            # Open the strike for 3 seconds, then close and reset current_read.
            GPIO.output(12, GPIO.HIGH)
            time.sleep(3)
            GPIO.output(12, GPIO.LOW)
            return name
    return None

while True:
    time.sleep(1)
    person_name = check(current_read, all_cards)
    if person_name:
        current_read = ''
        # TODO: Logging?
        #log('%s has unlocked the door.' % person_name)
    else:
        #log('An attempted login occurred at %s.' % date)
        continue # TODO: Remove this when this else is actually used.
    
