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


def preview_music(music_file):
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
    #import pdb;pdb.set_trace()
    pygame.mixer.music.play()
    start = time.time()
    while pygame.mixer.music.get_busy():
        # check if playback has finished at 15 fps
        clock.tick(15)
        if time.time() - start > 5:
            fadeout()
            return



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


_init()

if __name__ == "__main__":
    # just for testing
    print 'DJ: Running'
    songs_list = glob.glob("*.ogg")
    for song in songs_list:
        print 'Playing', song
        should_stop = preview_music(song)
    
