from typing import Dict

STATE_STOPPED = 0
STATE_PLAYING = 1
STATE_PAUSED = 2
STATE_IDLE = 3


class AudioBackend(object):

    def __init__(self, _params: Dict[str, str]):
        self.service = "GENERIC"
        self.active = False
        self.term_received = False

    def play(self):
        print("{} play - not implemented", self.service)

    def pause(self):
        print("{} pause - not implemented", self.service)

    def stop(self):
        print("{} stop - not implemented", self.service)

    def skip(self, _direction=1):
        print("{} skip - not implemented", self.service)

    def seek(self, _seconds=5):
        print("{} seek - not implemented", self.service)

    def activate(self, _active=True):
        self.active = True

    def is_active(self):
        return self.active

    def terminate(self):
        self.term_received = True

    def volume_changed(self):
        '''
        Notifies a control that the playback volume has been changed.
        In most cases, this can be ignored, but it can be useful e.g. 
        to display the volume.
        '''
        pass

    def __str__(self):
        return self.service
