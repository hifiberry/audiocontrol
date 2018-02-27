import logging
import os
from typing import Dict

from . import AudioBackend


class Mpd(AudioBackend):
    def __init__(self, _params: Dict[str, str]):
        self.service = "MPD"

    def stop(self):
        """
        mpd can be controlled via the mpc command line tool
        """
        logging.info("Stopping MPC playback using mpc pause")
        os.system("mpc pause")

    def skip(self, direction=1):
        if direction > 0:
            os.system("mpc next")
        if direction < 0:
            os.system("mpc previous")
