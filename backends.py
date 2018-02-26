import os
import logging
from typing import Dict

from spotifycontrol import SpotifyControl

STATE_STOPPED = 0
STATE_PLAYING = 1
STATE_PAUSED = 2
STATE_IDLE = 3


class AudioBackend(object):

    def __init__(self, _params: Dict[str, str]):
        self.service = "GENERIC"
        self.active = False
        self.term_received = False

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
        Notifies a control that the playback volume has been changed.
        In most cases, this can be ignored, but it can be useful e.g. 
        to display the volume.
        '''
        pass

    def __str__(self):
        return self.service


class Spotifyd(AudioBackend):

    def __init__(self, params: Dict[str, str]):
        self.spotifyControl = SpotifyControl()
        self.service = "SPOTIFY"

    def stop(self):
        """
        Stop Spotify player using the WebAPI if the spotify client is 
        connected using the client_id, client_secret
        Otherwise kill Spotifyd
        Killing Spotifyd isn't recommended as the client often needs to
        be restarted until it can reconnect to Spotify
        """
        if (self.spotifyControl == None):
            logging.info("Stopping Spotify by killing spotifyd")
            os.system("killall spotifyd")
        else:
            print("Pausing spotify")
            self.spotifyControl.pause()

    def skip(self, direction=1):
        self.spotifyControl.skip(direction)


class Shairport(AudioBackend):
    def __init__(self, _params: Dict[str, str]):
        self.service = "AIRPLAY"

    def stop(self):
        """
        Shairport does not have an option to tell the client to stop
        playback. Therefore the only way to disconnect a client is 
        to kill the process. It will be restarted by systemd after 
        a few seconds
        """
        logging.info("Stopping Airplay by killing shairport-sync")
        os.system("killall shairport-sync")


class Mpd(AudioBackend):
    def __init__(self, _params: Dict[str, str]):
        self.service = "MPD"

    def stop(self):
        """
        mpd can be controlled via the mpc command line tool
        """
        logging.info("Stopping MPC playback using mpc pause")
        os.system("mpc pause")

    def skip(self, direction=1):
        if direction > 0:
            os.system("mpc next")
        if direction < 0:
            os.system("mpc previous")
