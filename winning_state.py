import pygame
from pygame.locals import *
from State import State
import common

class Spotlight(pygame.sprite.Sprite):

    def __init__(self, center, end_radius):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = self.image = pygame.Surface(common.RESOLUTION)
        self.rect = self.image.get_rect()
        self.initial_radius = self.rect.width
        self.center = center
        self.end_radius = end_radius
        self.start_time = pygame.time.get_ticks()
        self.anim_time = 4000

    def update(self, t):
        elapsed_time = t - self.start_time
        if elapsed_time < self.anim_time:
            time_ratio = float(elapsed_time) / self.anim_time
            radius = (self.end_radius - self.initial_radius) * time_ratio + self.initial_radius
            self.image.fill((0, 0, 0))
            pygame.draw.circle(self.image, (255, 0, 0), self.center, radius)
            self.image.set_colorkey((255, 0, 0))    
            

class WinningState(State):

    def __init__(self, screen, background, capture, ref_img, transform_mat, wins, winning_player, more_sprites = None):
        State.__init__(self, screen, background, capture, ref_img, transform_mat)
        if more_sprites:
            self.sprites.add(more_sprites)
        self.winning_player = winning_player
        if wins[self.winning_player.name] >= common.ROUNDS_TO_WIN:
            self.big_win = True
            self.winning_text = self.font.render(self.winning_player.name + ' WINS!', True, (139, 0, 0))
            self.text_anim = common.FloatingWord(self.winning_text)
            self.text_anim.start_size = common.RESOLUTION
            self.text_anim.end_size = (common.RESOLUTION[0] * 0.7, common.RESOLUTION[1] * 0.7)
            self.spotlight = Spotlight(winning_player.center_of_mass, winning_player.rect.height * 0.6)
            self.spotlight.add(self.sprites)
        else:
            self.big_win = False
            self.winning_text = self.font.render(self.winning_player.name + ' wins this round!', True, (139, 0, 0))
            self.text_anim = common.FloatingWord(self.winning_text)
            self.text_anim.start_size = common.RESOLUTION
            self.text_anim.end_size = (common.RESOLUTION[0] / 2, common.RESOLUTION[1] / 2)
        self.text_anim.anim_time = 3000
        self.text_anim.wait_time = 2000
        self.sprites.add(self.text_anim)
        self.text_anim.start()
        print "WinningState: Initialized"

    def _state_specific(self):
        if self.text_anim.finished:
            self.state_running = False




                
            
        
        