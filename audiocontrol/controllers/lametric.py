import logging
from typing import Dict

from audiocontrol.controllers import Controller


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

        self.lifetime = params.get("seconds", 5)
        print(self.lmn)
        self.connect_lmn()
        print(self.lmn)
        sf = self.SimpleFrame("i9278", "AudioControl starting")
        model = self.Model(frames=[sf])
        self.lmn.send_notification(model,
                                   lifetime=self.lifetime)

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
