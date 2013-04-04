import pygame
from pygame.locals import *
from State import State
import common
from common import FloatingWord

class CountdownState(State):

    def __init__(self, screen, background, capture, ref_img, transform_mat):
        State.__init__(self, screen, background, capture, ref_img, transform_mat)
        self.one = FloatingWord(common.load_image('1.png', alpha = True)[0], sfx = 'one.wav')
        self.two = FloatingWord(common.load_image('2.png', alpha = True)[0], sfx = 'two.wav')
        self.three = FloatingWord(common.load_image('3.png', alpha = True)[0], sfx = 'three.wav')
        self.fight = FloatingWord(common.load_image('fight.png', alpha = True)[0], sfx = 'fight.wav')
        self.fight.end_size = (200, 200)
        self.fight.anim_time = 1000
        self.fight.wait_time = 100
        self.sprites.add(self.three)
        
        print "CountdownState: Initialized"
        
        
    def _state_specific(self):
        self.three.start()
        if self.three.finished:
            self.two.add(self.sprites)
            self.two.start()
        if self.two.finished:
            self.one.add(self.sprites)
            self.one.start()
        if self.one.finished:
            self.fight.add(self.sprites)
            self.fight.start()
        if self.fight.finished:
            self.state_running = False
    