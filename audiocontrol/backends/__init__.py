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

from typing import Dict

from audiocontrol import DummyManager

STATE_STOPPED = 0
STATE_PLAYING = 1
STATE_PAUSED = 2
STATE_IDLE = 3


class AudioBackend(object):

    def __init__(self, _params: Dict[str, str]):
        self.service = "GENERIC"
        self.active = False
        self.term_received = False
        self.manager = DummyManager()

    def set_manager(self, manager):
        self.manager = manager

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
        Notifies a backend that the playback volume has been changed.
        In most cases, this can be ignored, but it can be useful e.g. 
        to display the volume.
        '''
        pass

    def metadata_changed(self, metadata):
        '''
        Notifies a backend that the current music metadata has been 
        changed. Usually this should be ignored.
        '''
        pass

    def track_changed(self, trackdata):
        '''
        Notifies a backend that the current track has been 
        changed. Usually this is a good time to refresh the metadata for
        the song currently playing.
        '''
        pass

    def __str__(self):
        return self.service
