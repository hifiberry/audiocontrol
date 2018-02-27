import logging
import threading
import socket
import os
from typing import Dict

import spotipy
from spotipy import oauth2
from zeroconf import ServiceInfo, Zeroconf

from . import AudioBackend

from bottle import route, run, request

MYSERVER_PORT_NUMBER = 14281
SPOTIPY_CLIENT_ID = "e51080e24e9c48b98c6fc28fb838552e"
SPOTIPY_CLIENT_SECRET = "b3d70b9171ec44b29c0ab55537703fc4"
SPOTIPY_REDIRECT_URI = "http://spotify-registration.local:{}/".format(
    MYSERVER_PORT_NUMBER)
SPOTIPY_SCOPE = "user-read-playback-state user-modify-playback-state"
SPOTIPY_CACHE = '.spotipyoauthcache'

spotify_control = None


class SpotifyControl():

    def __init__(self):
        global spotify_control

        self.sp_oauth = oauth2.SpotifyOAuth(
            SPOTIPY_CLIENT_ID,
            SPOTIPY_CLIENT_SECRET,
            SPOTIPY_REDIRECT_URI,
            scope=SPOTIPY_SCOPE,
            cache_path=SPOTIPY_CACHE)

        spotify_control = self
        if (self.get_access_token() is None):
            # Register a temporary name in mDNS, start a web server to
            # provide a web site that registers the access code from
            # Spotify
            print("Spotify access code missing, starting up web server \
            to connect Spotify account")
            self.register_mdns()
            thread = threading.Thread(target=self.run_webserver, args=())
            thread.daemon = True
            thread.start()

    def run_webserver(self):
        run(host='', port=MYSERVER_PORT_NUMBER)

    def get_access_token(self):
        token_info = self.sp_oauth.get_cached_token()
        access_token = None

        if token_info:
            logging.debug("Found cached token!")
            access_token = token_info['access_token']
        else:

            url = request.url
            code = self.sp_oauth.parse_response_code(url)
            if code:
                # Found Spotify auth code in Request URL
                # Trying to get valid access token...")
                token_info = self.sp_oauth.get_access_token(code)
                access_token = token_info['access_token']

                # Ok, we have sucessfully logged into Spotify and
                # received a token. We can now stop th e web server
                # again as we don't need it anymore
                self.unregister_mdns()

        return access_token

    def command(self, cmd):
        access_token = None
        token_info = self.sp_oauth.get_cached_token()
        if token_info:
            logging.debug("Found cached token!")
            access_token = token_info['access_token']

        if access_token:
            sp = spotipy.Spotify(access_token)

            if (cmd == "pause_playback"):
                sp.pause_playback()
            elif (cmd == "next_track"):
                sp.next_track()
            elif (cmd == "previous_track"):
                sp.previous_track()

    def pause(self):
        self.command("pause_playback")

    def skip(self, direction):
        if (direction > 0):
            self.command("next_track")
        elif (direction < 0):
            self.command("previous_track")

    def register_mdns(self):
        print("registering MDNS")
        desc = {'path': '/'}
        self.zeroconf_info = \
            ServiceInfo("_http._tcp.local.",
                        "spotify-registration._http._tcp.local.",
                        socket.inet_aton(get_ip()),
                        MYSERVER_PORT_NUMBER,
                        0,
                        0,
                        desc, "spotify-registration.local.")

        self.zeroconf = Zeroconf()
        logging.info("Registration of spotify-registration.local. in mDNS")
        self.zeroconf.register_service(self.zeroconf_info)

    def unregister_mdns(self):
        logging.info("Unregistering MDNS")
        self.zeroconf.unregister_service(self.zeroconf_info)
        self.zeroconf.close()


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


@route('/')
def index():
    global spotify_control

    access_token = spotify_control.get_access_token()

    if access_token:
        return ("Spotify Web API is connected")

    else:
        auth_url = spotify_control.sp_oauth.get_authorize_url()
        return "<a href='" + auth_url + "'>Login to Spotify</a>"


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP
