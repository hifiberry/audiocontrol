import logging

from typing import Dict

from .metadata import MetaData


class Manager():

    def __init__(self):
        self.backends = []
        self.controllers = []
        self.metadata = MetaData()
        print("*3")

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
        print("Skip {}".format(direction))
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
