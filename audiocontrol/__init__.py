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

from audiocontrol.metadata import MetaData

__version__ = "0.3"


class Manager():

    def __init__(self):
        self.backends = []
        self.controllers = []
        self.metadata = MetaData()

    def run(self):
        pass

    def add_backend(self, backend):
        self.backends.append(backend)
        backend.set_manager(self)

    def add_controller(self, controller):
        self.controllers.append(controller)
        controller.set_manager(self)

    def service_changed(self, service):
        pass

    def quit(self):
        pass

    def set_volume_percent(self, volume_percent):
        volume_old = self.volume_percent
        if (volume_percent < 0):
            volume_percent = 0
        elif (volume_percent > 100):
            volume_percent = 100

        self.volume_percent = volume_percent
        if volume_old != self.volume_percent:
            for b in self.backends:
                b.volume_changed()
            for c in self.controllers:
                c.volume_changed()

        logging.debug("Volume: {}%".format(self.volume_percent))

    def change_volume_percent(self, diff):
        self.set_volume_percent(self.volume_percent + diff)

    def skip(self, direction=1):
        if self.active_backend is not None:
            self.active_backend.skip(direction)

    def update_metadata(self, values: Dict):
        self.metadata.set_attribute(values)
        for b in self.backends:
            b.metadata_changed(self.metadata)
        for c in self.controllers:
            c.metadata_changed(self.metadata)


class DummyManager(Manager):

    def __init__(self):
        super(DummyManager, self).__init__()
