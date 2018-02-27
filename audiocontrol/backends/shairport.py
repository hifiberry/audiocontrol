import logging
import os
import stat
import threading
import xmltodict
import base64

from typing import Dict

from audiocontrol.metadata import Attributes

from . import AudioBackend

METADATA_MAPPING = {
    "asal": Attributes.SONG_ALBUM,
    "asar": Attributes.SONG_ARTIST,
    "ascm": Attributes.SONG_COMMENT,
    "ascp": Attributes.SONG_COMPOSER,
    "asdc": Attributes.DISC_COUNT,
    "asdn": Attributes.DISC_NUMBER,
    "asgn": Attributes.SONG_GENRE,
    "asdt": Attributes.SONG_DESCRIPTION,
    "astm": Attributes.SONG_TIME,
    "astc": Attributes.TRACK_COUNT,
    "astn": Attributes.TRACK_NUMBER,
    "asyr": Attributes.SONG_YEAR,
    "asbt": Attributes.SONG_BPM,
    "minm": Attributes.SONG_TITLE,
}


class Shairport(AudioBackend):

    def __init__(self, params: Dict[str, str]):
        self.service = "AIRPLAY"

        self.metadatafifo = params.get("metadata",
                                       "/tmp/shairport-sync-metadata")

        thread = threading.Thread(target=self.metadata_updater, args=())
        thread.daemon = True
        thread.start()

    def stop(self):
        """
        Shairport does not have an option to tell the client to stop
        playback. Therefore the only way to disconnect a client is 
        to kill the process. It will be restarted by systemd after 
        a few seconds
        """
        logging.info("Stopping Airplay by killing shairport-sync")
        os.system("killall shairport-sync")

    def metadata_updater(self):
        if not(stat.S_ISFIFO(os.stat(self.metadatafifo).st_mode)):
            logging.info("%s does not exists or is no FIFO, "
                         "disabling shairport metadata reader",
                         self.metadatafifo)
        with open(self.metadatafifo, 'r') as fifo:
            temp_line = ""
            for line in fifo:
                if not line.strip().endswith("</item>"):
                    temp_line += line.strip()
                    continue
                line = temp_line + line
                temp_line = ""
                self.process_item(line)

    def process_item(self, line):
        try:
            item = xmltodict.parse(line).get("item")
            subtype = self.parse_numbers(item["type"])
            code = self.parse_numbers(item["code"])
        except:
            logging.debug("% is not a valid item, ignoring", line)
            return

        try:
            data = item["data"]["#text"]
            enc = item["data"]["@encoding"]

            if (enc == "base64"):
                data = base64.b64decode(data)
        except KeyError:
            data = None

        if subtype == "core" and (data is not None):
            attr = METADATA_MAPPING.get(code)
            self.manager.update_metadata({attr: data})

    def parse_numbers(self, string, base=16, digits_per_char=2):
        return "".join([chr(int(string[i:i + digits_per_char], base=base)) for i in range(0, len(string), digits_per_char)])
