import logging
import os
from typing import Dict

from . import AudioBackend


class Shairport(AudioBackend):
    def __init__(self, _params: Dict[str, str]):
        self.service = "AIRPLAY"

    def stop(self):
        """
        Shairport does not have an option to tell the client to stop
        playback. Therefore the only way to disconnect a client is 
        to kill the process. It will be restarted by systemd after 
        a few seconds
        """
        logging.info("Stopping Airplay by killing shairport-sync")
        os.system("killall shairport-sync")
