import threading
import time
import os
import signal
import sys

from backends import Spotifyd, Shairport

controller = None


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


class Controller():

    def __init__(self):
        self.status = status(self)
        self.stop_other_on_service_change = True
        self.backends = []

    def run(self):
        print("Backends enabled: ")
        for b in self.backends:
            print(b)
        while True:
            print("* {} *".format(self.status.service))
            time.sleep(60)

    def add_backend(self, backend):
        self.backends.append(backend)

    def service_changed(self, service):
        print("service: {}".format(service))
        if self.stop_other_on_service_change and (service != ""):
            for b in self.backends:
                if b.service != service:
                    b.stop()


def sigterm_handler(_signal, _frame):
    """
    Shut down gracefully
    """
    sys.exit(0)


def sigusr1_handler(_signal, _frame):
    """
    STOP playback on SIGUSR1
    """
    for b in controller.backends:
        b.stop()


def main():
    global controller

    signal.signal(signal.SIGINT, sigterm_handler)
    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGUSR1, sigusr1_handler)
    controller = Controller()
    controller.add_backend(Spotifyd({}))
    controller.add_backend(Shairport({}))

    controller.run()


if __name__ == '__main__':
    main()
