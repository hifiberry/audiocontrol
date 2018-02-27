import logging
from typing import Dict

from . import Controller


class SongLogger(Controller):
    '''
    A very simple conptroller, that outputs the current song via logging
    '''

    def __init__(self, _params: Dict[str, str]):

        self.manager = None
        self.service = "SONGLOGGER"
        self.playing = ""

    def metadata_changed(self, metadata):
        output = str(metadata)
        if output != self.playing:
            self.playing = output
            logging.info(output)