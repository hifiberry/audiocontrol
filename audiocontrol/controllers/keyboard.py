import logging
from typing import Dict

from . import Controller


class Keyboard(Controller):

    def __init__(self, params: Dict[str, str]):
        self.service = "KEYBOARD"
        self.codetable = {}
        for i in params:
            self.codetable[params[i]] = i

        import keyboard
        keyboard.hook(self.keyboard_hook)
        logging.debug("Keyboard listener started")

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
