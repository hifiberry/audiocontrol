class MetaData(object):
    '''
    Generic metadata object for song/playback information
    '''

    def __init__(self, params):
        self.title = None
        self.interpret = None
        self.length = 0
        self.current_position = 0
        self.cover = None