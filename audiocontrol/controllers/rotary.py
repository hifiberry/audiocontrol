'''
Copyright (c) 2018 Modul 9/HiFiBerry

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import time
import logging
from typing import Dict

from audiocontrol.controllers import Controller


class Rotary(Controller):

    import RPi.GPIO as GPIO

    CLOCKWISE = 0
    ANTICLOCKWISE = 1

    def __init__(self, params):
        self.service = "ROTARY"

        self.clockPin = int(params.get("clockpin", 14))
        self.dataPin = int(params.get("datapin", 15))
        self.switchPin = int(params.get("switchpin", 0))
        self.rotaryBounceTime = int(params.get("rotarybouncetime", 20))
        self.switchBounceTime = int(params.get("switchbouncetime", 100))
        self.steps = int(params.get("steps", 20))
        self.percentchange = 100 / self.steps

        # setup pins
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setup(self.clockPin, self.GPIO.IN)
        self.GPIO.setup(self.dataPin, self.GPIO.IN)

        if self.switchPin > 0:
            self.GPIO.setup(self.switchPin, self.GPIO.IN,
                            pull_up_down=self.GPIO.PUD_UP)
            self.GPIO.add_event_detect(self.switchPin,
                                       self.GPIO.FALLING,
                                       callback=self._switchCallback,
                                       bouncetime=self.switchBounceTime)

        self.GPIO.add_event_detect(self.clockPin, self.GPIO.FALLING,
                                   callback=self._clockCallback,
                                   bouncetime=self.rotaryBounceTime)

        logging.info("Rotary controller set up with CLK %s DATA %s SWITCH %s",
                     self.clockPin, self.dataPin, self.switchPin)

    def terminate(self):
        self.GPIO.remove_event_detect(self.clockPin)

        if self.switchPin > 0:
            self.GPIO.remove_event_detect(self.switchPin)

    def _clockCallback(self, pin):
        if self.GPIO.input(self.clockPin) == 0:
            data = self.GPIO.input(self.dataPin)
            logging.debug("Rotary clock callback %s", data)
            if data == 1:
                self.manager.change_volume_percent(-self.percentchange)
            else:
                self.manager.change_volume_percent(self.percentchange)

    def _switchCallback(self, pin):
        # TODO: Play/Pause
        pass
