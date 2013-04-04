"""
Runs whatever mp3 files are in the %current directory%/music.

to start the music:

>>> import pgmusic
>>> pgmusic.start_music_thread()


to make it stop:

>>> pgmusic.fadeout()


play a MP3 or MIDI music file using module pygame
(does not create a GUI frame in this case)
pygame is free from: http://www.pygame.org/
Tested with pygame-1.8.0 by:  Ene Uran

"""


import pygame
import glob
from threading import Thread
import random
import time
import sys


DJ_SINGLETON = None

class _DJ(Thread):
    """
    randomly plays the songs on the playlist until the list is over.
    """

    def __init__(self):
        Thread.__init__(self)
        self.playing = True
        
    def run(self):
        print 'DJ: Running'
        songs_list = glob.glob("music/*.ogg")
        random.shuffle(songs_list)
        for song in songs_list:
            should_stop = self.play_music(song)
            if should_stop:
                return
        

    def play_music(self, music_file):
        """
        blocking function.
        stream music with mixer.music module until file finishes playing.
        this will stream the sound from disk while playing
        """
        clock = pygame.time.Clock()
        try:
            print 'Loading: %s ...' % music_file,
            pygame.mixer.music.load(music_file)
            print "loaded!"
        except pygame.error:
            print "File %s not found! (%s)" % (music_file, pygame.get_error())
            return
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() and self.playing:
            # check if playback has finished at 15 fps
            clock.tick(15)
        if not self.playing:
            return True
        return False


    def stop(self):
        self.playing = False


def start_music_thread():
    global DJ_SINGLETON
    
    if DJ_SINGLETON is None:
        DJ_SINGLETON = _DJ()
        DJ_SINGLETON.start()
##    else:
##        raise Exception("started music thread twice")

def _init():
    # pick a MP3 or MIDI music file you have ...
    # (if not in working folder, use full path)

    # set up the mixer
    freq = 44100     # audio CD quality
    bitsize = -16    # unsigned 16 bit
    channels = 2     # 1 is mono, 2 is stereo
    buffer = 2048    # number of samples (experiment to get right sound)
    pygame.mixer.init(freq, bitsize, channels, buffer)

    # optional volume 0 to 1.0
    pygame.mixer.music.set_volume(0.6)

def fadeout(delay_seconds=1.0):
    delay_ms = delay_seconds * 1000
    
    # NOTE: docs say this is a blocking function, it's not.
    pygame.mixer.music.fadeout(int(delay_ms))
    time.sleep(delay_seconds)
    pygame.mixer.music.stop()

    global DJ_SINGLETON
    DJ_SINGLETON.stop()
    DJ_SINGLETON = None

def _play_and_fadeout():
    """not used"""
    try:
        #music_file = "Drumtrack.mp3"
        #music_file = "ChancesAre.mid"
        music_file = "music/02 Drivin' Through on Max.mp3"
        play_music(music_file)
    except KeyboardInterrupt:
        # if user hits Ctrl-C then exit
        # (works only in console mode)
        fadeout()
        raise SystemExit

    
_init()

if __name__ == "__main__":
    # just for testing
    start_music_thread()
    #_play_and_fadeout()
    time.sleep(5)
    fadeout()
