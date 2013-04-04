import pygame
from pygame.locals import *
import common
import cv
import imcompare
from State import State

class TutorialState(State):

    INIT_TIME = 5000

    def __init__(self, screen, background, capture, ref_img, transform_mat):
        State.__init__(self, screen, background, capture, ref_img, transform_mat)
        self.ready = False
        self.should_draw_bounding_box = True
        self.player1_rect = pygame.rect.Rect((10, 100, 300, common.RESOLUTION[1] - 100))
        self.player2_rect = pygame.rect.Rect((common.RESOLUTION[0] - 310, 100, 390, common.RESOLUTION[1] - 100))
        self.special_detection_rects += (self.player1_rect, self.player2_rect)
        self.mask = StageMask(self.player1_rect, self.player2_rect)
        self.title = common.FloatingWord(common.load_image('geekfighter.png', alpha = True)[0], center = (common.RESOLUTION[0] / 2, 154), sfx = 'opening.wav')
        self.title.start_size = (19, 10)
        self.title.end_size = (600, 308)
        self.title.anim_time = 2000
        self.title.wait_forever = True
        self.sprites.add(self.title)
        self.explanations1 = common.HelpText((common.RESOLUTION[0] / 2, 330), 'Stand facing each other', self.font, (210, 0, 0), pos_is_center = True)
        self.explanations2 = common.HelpText((common.RESOLUTION[0] / 2, 370), 'in your FIGHTING STANCE', self.font, (210, 0, 0), pos_is_center = True)
        self.explanations3 = common.HelpText((common.RESOLUTION[0] / 2, 410), 'and HOLD STILL for 5 seconds', self.font, (210, 0, 0), pos_is_center = True)
        
        self.player1_counter = 0
        self.player1_heights = []
        self.player2_counter = 0
        self.player2_heights = []

        self.readybar1 = ReadyBar((10, 89), self.INIT_TIME)
        self.readybar2 = ReadyBar((common.RESOLUTION[0] - 310, 89), self.INIT_TIME)        

        self.last_time = pygame.time.get_ticks()        
##        self.text = self.font.render("Players, stand facing each other with your arms at your sides", 1, (10, 10, 10))
##        self.pos = (self.screen.get_width() / 2 - self.text.get_width() / 2, self.screen.get_height() / 10)
##        self.text2 = self.font.render("Press the SPACEBAR when ready...", 1, (10, 10, 10))
##        self.pos2 = (self.screen.get_width() / 2 - self.text2.get_width() / 2, self.screen.get_height() / 10 + self.text.get_height() + 5)
        print "TutorialState: Initialized"

    def _state_specific(self):
        t = pygame.time.get_ticks()
        elapsed_time = t - self.last_time
        self.last_time = t
        
        self.title.start()
        if self.title.grace_period:
            self.sprites.add(self.mask)
            self.sprites.move_to_back(self.mask)
            self.sprites.add(self.explanations1)
            self.sprites.add(self.explanations2)
            self.sprites.add(self.explanations3)
            self.sprites.add(self.readybar1)
            self.sprites.add(self.readybar2)

        if self.player1.initialized and self.player2.initialized:
            if self.player1_rect.contains(self.player1.rect) and not self.player1_rect.contains(self.player2.rect):
                self.player1_counter += elapsed_time
                self.player1_heights.append(imcompare.find_contour_height(self.player1.contour))
            else:
                self.player1_counter = 0
                self.player1_heights = []
            self.readybar1.update_size(self.player1_counter)

            if self.player2_rect.contains(self.player2.rect) and not self.player2_rect.contains(self.player1.rect):
                self.player2_counter += elapsed_time
                self.player2_heights.append(imcompare.find_contour_height(self.player2.contour))
            else:
                self.player2_counter = 0
                self.player2_heights = []
            self.readybar2.update_size(self.player2_counter)

        if self.player1_counter >= self.INIT_TIME and self.player2_counter >= self.INIT_TIME:
            self.player1_height = sorted(self.player1_heights)[len(self.player1_heights) / 2]
            self.player2_height = sorted(self.player2_heights)[len(self.player2_heights) / 2]
            self.state_running = False


class StageMask(pygame.sprite.Sprite):

    def __init__ (self, player1_rect, player2_rect):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface(common.RESOLUTION)
        self.rect = self.image.get_rect()
        self.image.fill((0, 0, 0))
        pygame.draw.rect(self.image, (255, 0, 0), player1_rect)
        pygame.draw.rect(self.image, (255, 0, 0), player2_rect)
        self.image.set_colorkey((255, 0, 0))
        self.image.set_alpha(100)

class ReadyBar(pygame.sprite.Sprite):

    WIDTH = 300    

    def __init__(self, initial_pos, max_full):
        pygame.sprite.Sprite.__init__(self)
        self.max_full = max_full
        self.initial_pos = initial_pos
        self.start_color = (255, 0, 0)
        self.end_color = (0, 255, 0)
        self.last_time = pygame.time.get_ticks()
        self.image = pygame.Surface((1, 10))
        self.image.fill(self.start_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = self.initial_pos

    def update_size(self, new_size):
        ratio = float(new_size) / self.max_full
        self.image = pygame.Surface((int(ratio * self.WIDTH), 10))
        color = [int( (1 - ratio) * self.start_color[i] + ratio * self.end_color[i] ) for i in range(3)]
        for i, c in enumerate(color):
            if c < 0:
                color[i] = 0
            if c > 255:
                color[i] = 255
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = self.initial_pos
        