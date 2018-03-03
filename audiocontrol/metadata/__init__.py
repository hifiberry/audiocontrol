from enum import Enum, unique

from typing import Dict


@unique
class Attributes(Enum):
    CLEAR = 0

    SONG_ALBUM = 1
    SONG_ARTIST = 2
    SONG_TITLE = 3
    SONG_COMMENT = 4
    SONG_COMPOSER = 5
    SONG_GENRE = 6
    SONG_DESCRIPTION = 7
    SONG_DURATION_MS = 8
    SONG_YEAR = 9
    SONG_BPM = 10

    TRACK_COUNT = 30
    TRACK_NUMBER = 31

    DISC_COUNT = 40
    DISC_NUMBER = 41
    DISC_GENRE = 42

    PICTURE = 100
    PICTURE_URL = 101
    URL = 102


class MetaData(object):
    '''
    Generic metadata object for song/playback information
    '''

    def __init__(self):
        self.attributes = {}

    def clear(self):
        self.attributes = {}

    def set_attribute(self, values: Dict):
        for k in values:
            self.attributes[k] = values[k]

    def __str__(self):
        return "{}: {}".format(self.attributes.get(Attributes.SONG_ARTIST),
                               self.attributes.get(Attributes.SONG_TITLE))
