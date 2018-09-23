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

import logging
from typing import Dict

from audiocontrol.controllers import Controller


class Keyboard(Controller):

    def __init__(self, params: Dict[str, str]):
        self.service = "KEYBOARD"
        self.codetable = {}
        for i in params:
            self.codetable[params[i]] = i

        import keyboard
        try:
            keyboard.hook(self.keyboard_hook)
            logging.debug("Keyboard listener started")
        except:
            logging.error("Could not start Keyboard listener, "
                          "no keyboard detected or no permissions")

    def keyboard_hook(self, e):
        import keyboard
        if e.event_type == keyboard.KEY_DOWN:
            try:
                command = self.codetable[str(e.scan_code)]
            except:
                return

            if command == "volume_up":
                self.manager.change_volume_percent(5)
            elif command == "volume_down":
                self.manager.change_volume_percent(-5)
            elif command == "previous":
                self.manager.skip(-1)
            elif command == "next":
                self.manager.skip(1)

    def run(self):
        import keyboard
        keyboard.wait()
