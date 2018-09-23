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

CONTROL_VOLUME_UP = 1
CONTROL_VOLUME_DOWN = 2
CONTROL_NEXT = 4
CONTROL_PREVIOUS = 8

from audiocontrol import DummyManager


class Controller():

    def __init__(self, _params: Dict[str, str]):
        self.manager = DummyManager()
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

    def metadata_changed(self, metadata):
        '''
        Notifies a control that the metadata of the song current playing
        have changed
        '''
        pass

    def terminate(self):
        self.term_received = True

    def __str__(self):
        return self.service
