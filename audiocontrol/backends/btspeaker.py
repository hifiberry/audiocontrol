import logging
import os

from typing import Dict

from audiocontrol.backends import AudioBackend


class BTSpeaker(AudioBackend):

    def __init__(self, params: Dict[str, str]):
        self.service = "BTSPEAKER"

    def stop(self):
        """
        iBTSpeaker does not have an option to tell the client to stop
        playback. Therefore the only way to disconnect a client is 
        to kill the process. 
        """
        logging.info("Stopping BTSpeaker by killing shairport-sync")
        os.system("killall shairport-sync")
