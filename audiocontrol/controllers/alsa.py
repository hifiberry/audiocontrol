import logging
import threading
import time
from typing import Dict

from . import Controller


class AlsaVolume(Controller):

    def __init__(self, params: Dict[str, str]):
        import alsaaudio

        self.manager = None
        self.service = "ALSAVOLUME"
        self.term_received = False
        self.volume = 0
        self.pollinterval = float(params.get("pollinterval", "0.3"))
        if self.pollinterval < 0.1:
            self.pollinterval = 0.1

        self.mixername = params.get("control", "Master")
        if alsaaudio.Mixer(self.mixername) == None:
            logging.error("ALSA mixer device %s not found, aborting",
                          self.mixername)

        thread = threading.Thread(target=self.run_listener, args=())
        thread.daemon = True
        thread.start()

    def volume_changed(self):
        import alsaaudio

        vol = self.manager.volume_percent
        if vol != self.volume:
            alsaaudio.Mixer(self.mixername).setvolume(int(vol),
                                                      alsaaudio.MIXER_CHANNEL_ALL)

    def run_listener(self):
        # Wait until a manager is connected before starting updated
        while (self.manager is None) and not (self.term_received):
            time.sleep(1)

        while not(self.term_received):
            self.update_volume()
            time.sleep(self.pollinterval)

    def update_volume(self):
        import alsaaudio

        volumes = alsaaudio.Mixer(self.mixername).getvolume()
        channels = 0
        vol = 0
        for i in range(len(volumes)):
            channels += 1
            vol += volumes[i]

        if channels > 0:
            vol = vol / channels

        if vol != self.volume:
            logging.debug("ALSA volume changed to {}".format(vol))
            self.volume = vol
            self.manager.set_volume_percent(vol)
