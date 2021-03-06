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

import threading
import time
import os
import signal
import sys
import configparser
import logging

from audiocontrol import Manager

manager = None


class StatusUpdater(object):

    def __init__(self, status, statuspipe):
        self.statuspipe = statuspipe
        self.status = status
        thread = threading.Thread(target=self.run, args=())
        try:
            os.remove(self.statuspipe)
        except:
            pass

        try:
            os.mkfifo(statuspipe)
            os.chmod(statuspipe, 0o666)
        except PermissionError:
            logging.error("Can't create named pipe %s", statuspipe)
            sys.exit(1)

        thread.daemon = True
        thread.start()

    def __del__(self):
        try:
            os.remove(self.statuspipe)
        except PermissionError:
            logging.error("Can't remove named pipe %s", self.statuspipe)

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

        logging.debug("Received message from FIFO: %s", line.strip())

        words = line.split()

        if len(words) == 2:
            if words[0] == "START":
                self.status.service_changed(words[1])
            if words[0] == "STOP":
                if (self.status.service == words[1]):
                    self.status.service_changed("")

        elif len(words) == 3:
            if (words[0] == "TRACK"):
                self.status.track_changed(words[1], words[2])


class status():

    def __init__(self, manager, statuspipe="/tmp/audiostatus"):
        self.manager = manager
        self.service = "UNKNOWN"
        self.statusupdater = StatusUpdater(self, statuspipe)

    def service_changed(self, service):
        self.service = service
        self.manager.service_changed(service)

    def track_changed(self, service, trackdata):
        self.manager.track_changed(service, trackdata)

    def received_metadata(self, key, value):
        logging.debug("Received metadata %s:%s", key, value)


class MyManager(Manager):

    def __init__(self, params):
        super(MyManager, self).__init__()

        self.status = status(self)
        self.backends = []
        self.controllers = []
        self.terminate = False
        self.volume_percent = 50
        self.active_backend = None

        self.stop_other_on_service_change = params.get("stop_other_on_service_change",
                                                       True)

    def run(self):
        logging.info("Backends enabled: %s",
                     ",".join(str(b) for b in self.backends))
        logging.info("Controllers enabled: %s",
                     ",".join(str(c) for c in self.controllers))

        while not(self.terminate):
            time.sleep(0.1)

    def service_changed(self, service):
        logging.debug("service: %s", service)
        if self.stop_other_on_service_change and (service != ""):
            for b in self.backends:
                if b.service == service:
                    self.active_backend = b
                    b.activate()
                else:
                    b.stop()
                    b.activate(False)

    def track_changed(self, service, trackdata):
        logging.debug("Track changed %s:%s", service, trackdata)
        for b in self.backends:
            if b.service == service:
                b.track_changed(trackdata)

    def quit(self):
        self.terminate = True

    def skip(self, direction=1):
        logging.debug("Skip %s", direction)
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


def run():
    global manager

    config = configparser.ConfigParser()
    config.read("/etc/audiocontrol.conf")

    if "general" in config.sections():
        manager = MyManager(config["general"])
    else:
        manager = MyManager({})

    for section in config.sections():
        if section == "spotify":
            from audiocontrol.backends.spotify import Spotifyd
            manager.add_backend(Spotifyd(config["spotify"]))

        if section == "shairport":
            from audiocontrol.backends.shairport import Shairport
            manager.add_backend(Shairport(config["shairport"]))

        if section == "mpd":
            from audiocontrol.backends.mpd import Mpd
            manager.add_backend(Mpd({}))

        if section == "btspaker":
            from audiocontrol.backends.btspeaker import BTSpeaker
            manager.add_backend(BTSpeaker(config["btspeaker"]))

        # ----

        if section == "nuimo":
            from audiocontrol.controllers.nuimo import Nuimo
            manager.add_controller(Nuimo(config["nuimo"]))

        if section == "keyboard":
            from audiocontrol.controllers.keyboard import Keyboard
            manager.add_controller(Keyboard(config["keyboard"]))

        if section == "alsavolume":
            from audiocontrol.controllers.alsa import AlsaVolume
            manager.add_controller(AlsaVolume(config["alsavolume"]))

        if section == "songlogger":
            from audiocontrol.controllers.songlogger import SongLogger
            manager.add_controller(SongLogger(config["songlogger"]))

        if section == "lametric":
            from audiocontrol.controllers.lametric import LaMetric
            manager.add_controller(LaMetric(config["lametric"]))

        if section == "rotary":
            from audiocontrol.controllers.rotary import Rotary
            manager.add_controller(Rotary(config["rotary"]))

        if section == "cec":
            from audiocontrol.controllers.cec import Cec
            manager.add_controller(Rotary(config["cec"]))

    signal.signal(signal.SIGINT, sigterm_handler)
    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGUSR1, sigusr1_handler)

    try:
        manager.run()
    except KeyboardInterrupt:
        print("CTRL-C pressed")


if __name__ == '__main__':
    run()
