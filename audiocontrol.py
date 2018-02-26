import threading
import time
import os
import signal
import sys
import logging

import configparser

from backends import Spotifyd, Shairport, Mpd
from controllers import Nuimo, Keyboard, AlsaVolume

manager = None


class StatusUpdater(object):

    def __init__(self, status, statuspipe):
        self.statuspipe = statuspipe
        self.status = status
        thread = threading.Thread(target=self.run, args=())
        if (not(os.path.exists(statuspipe))):
            os.mkfifo(statuspipe)

        os.chmod(statuspipe, 0o666)

        thread.daemon = True
        thread.start()

    def __del__(self):
        os.remove(self.statuspipe)

    def run(self):
        pipe = open(self.statuspipe)
        while True:
            line = pipe.readline()
            if not line:
                time.sleep(0.1)
            self.parse_line(line)

    def parse_line(self, line):
        if line == "":
            return

        words = line.split()

        if len(words) == 2:
            if words[0] == "START":
                self.status.service_changed(words[1])
            if words[0] == "STOP":
                if (self.status.service == words[1]):
                    self.status.service_changed("")


class status():

    def __init__(self, controller, statuspipe="/tmp/audiostatus"):
        self.controller = controller
        self.service = "UNKNOWN"
        self.statusupdater = StatusUpdater(self, statuspipe)

    def service_changed(self, service):
        self.service = service
        self.controller.service_changed(service)


class Manager():

    def __init__(self):
        self.status = status(self)
        self.stop_other_on_service_change = True
        self.backends = []
        self.controllers = []
        self.terminate = False
        self.volume_percent = 50
        self.active_backend = None

    def run(self):
        print("Backends enabled: ")
        for b in self.backends:
            print(b)
        print("Controllers enabled: ")
        for c in self.controllers:
            print(c)

        while not(self.terminate):
            time.sleep(0.1)

    def add_backend(self, backend):
        self.backends.append(backend)

    def add_controller(self, controller):
        self.controllers.append(controller)
        controller.set_manager(self)

    def service_changed(self, service):
        print("service: {}".format(service))
        if self.stop_other_on_service_change and (service != ""):
            for b in self.backends:
                if b.service == service:
                    self.active_backend = b
                    b.activate()
                else:
                    b.stop()
                    b.activate(False)

    def quit(self):
        self.terminate = True

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


def sigterm_handler(_signal, _frame):
    """
    Shut down gracefully
    """
    global manager
    for b in manager.backends:
        b.terminate()

    for c in manager.backends:
        c.terminate()

    sys.exit(0)


def sigusr1_handler(_signal, _frame):
    """
    STOP playback on SIGUSR1
    """
    for b in manager.backends:
        b.stop()


def main():
    global manager

    manager = Manager()

    config = configparser.ConfigParser()
    config.read("audiocontrol.conf")

    for section in config.sections():
        if section == "spotify":
            manager.add_backend(Spotifyd({}))

        if section == "shairport":
            manager.add_backend(Shairport({}))

        if section == "mpd":
            manager.add_backend(Mpd({}))

        if section == "nuimo":
            manager.add_controller(Nuimo(config["nuimo"]))

        if section == "keyboard":
            manager.add_controller(Keyboard(config["keyboard"]))

        if section == "alsavolume":
            manager.add_controller(AlsaVolume(config["alsavolume"]))

    signal.signal(signal.SIGINT, sigterm_handler)
    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGUSR1, sigusr1_handler)

    try:
        manager.run()
    except KeyboardInterrupt:
        print("CTRL-C pressed")


if __name__ == '__main__':
    main()
