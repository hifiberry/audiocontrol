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
import threading
from typing import Dict

from audiocontrol.controllers import Controller

from bottle import route, run, request

manager = None


class LaMetric(Controller):
    '''
    A controller, that outputs the current song via LaMetric 
    notifications
    '''

    from lmnotify import LaMetricManager, Model, SimpleFrame

    def __init__(self, params: Dict[str, str]):
        self.manager = None
        self.service = "LAMETRIC"
        self.playing = ""
        self.lmn = None

        self.clientid = params.get("client_id", None)
        if self.clientid is None:
            logging.error("clientid for lametric missing, aborting")
            return

        self.clientsecret = params.get("client_secret", None)
        if self.clientsecret is None:
            logging.error("clientsecret for lametric missing, aborting")

        # If a port
        try:
            self.port = int(params.get("server-port"))
            self.hostname = params.get("server-name",
                                       "audiocontrol-lametric")
            thread = threading.Thread(target=self.run_webserver, args=())
            thread.daemon = True
            thread.start()
        except:
            logging.info("Not starting LaMetrci web server")

        self.lifetime = params.get("seconds", 5)
        print(self.lmn)
        self.connect_lmn()
        print(self.lmn)
        sf = self.SimpleFrame("i9278", "AudioControl starting")
        model = self.Model(frames=[sf])
        self.lmn.send_notification(model,
                                   lifetime=self.lifetime)

    def set_manager(self, mgr):
        global manager

        Controller.set_manager(self, mgr)
        manager = mgr

    def run_webserver(self):
        run(host='', port=self.port)

    def connect_lmn(self):
        try:
            self.lmn = self.LaMetricManager(client_id=self.clientid,
                                            client_secret=self.clientsecret)
            devices = self.lmn.get_devices()
            self.lmn.set_device(devices[0])
        except Exception as e:
            logging.error("LaMetric connection problem %s", e)

    def metadata_changed(self, metadata):
        output = str(metadata)
        if output != self.playing:
            self.playing = output
            if self.lmn:
                sf = self.SimpleFrame("i9278", output)
                model = self.Model(frames=[sf])
                try:
                    self.lmn.send_notification(model,
                                               lifetime=self.lifetime)
                except:
                    self.connect_lmn()
                    self.lmn.send_notification(model,
                                               lifetime=self.lifetime)

                logging.debug("Sent %s to LaMetric", output)
            else:
                logging.debug("LaMetric not connected")


@route('/')
def index():
    global spotify_control

    return "{}"
