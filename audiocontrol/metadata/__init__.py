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
