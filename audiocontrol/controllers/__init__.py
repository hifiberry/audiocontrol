from typing import Dict

CONTROL_VOLUME_UP = 1
CONTROL_VOLUME_DOWN = 2
CONTROL_NEXT = 4
CONTROL_PREVIOUS = 8


class Controller():

    def __init__(self, _params: Dict[str, str]):
        self.manager = None
        self.term_received = False

    def set_manager(self, manager):
        self.manager = manager

    def volume_changed(self):
        '''
        Notifies a control that the playback volume has been changed.
        In most cases, this can be ignored, but it can be useful e.g. 
        to display the volume.
        '''
        pass

    def terminate(self):
        self.term_received = True

    def __str__(self):
        return self.service
