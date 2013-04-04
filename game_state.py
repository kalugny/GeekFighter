import pygame
from pygame.locals import *
import cv
from State import State
from player import Player
import common
        
class GameState(State):

    def __init__(self, screen, background, capture, ref_img, transform_mat, wins, players_height):
        self.wins = wins
        self.players_height = players_height
        State.__init__(self, screen, background, capture, ref_img, transform_mat)
        self.times = []

        print "GameState: Initialized"


    def create_players(self):
        return Player(common.DIRECTION_RIGHT, self, self.wins['Player 1'], self.players_height[0]), Player(common.DIRECTION_LEFT, self, self.wins['Player 2'], self.players_height[1])

    def _process_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_a:
                self.player2.fireball()
            elif event.key == K_x:
                self.player1.fireball()
            elif event.key == K_c:
                self.player1.punch()
            elif event.key == K_s:
                self.player2.punch()
            elif event.key == K_d:
                self.player2.kick()
            elif event.key == K_v:
                self.player1.kick()
            elif event.key == K_g:
                self.player2.shadow()
            elif event.key == K_n:
                self.player1.shadow()
            elif event.key == K_f:
                self.player2.super(self.player1)
            elif event.key == K_b:
                self.player1.super(self.player2)
            elif K_1 <= event.key <= K_9:
                common.WIDTH_LIM = event.key - K_1 + 1
            elif event.key == K_LCTRL:
                self.should_draw_bounding_box = not self.should_draw_bounding_box
                self.redraw_next_frame = True
                self.player1.hide_show_helptext(self.should_draw_bounding_box)
                self.player2.hide_show_helptext(self.should_draw_bounding_box)

    def update_player_motion_disabled_period(self, player, ticks):
        if player.detection_disable_period > 0:
            player.detection_disable_period -= ticks
        if player.detection_disable_period < 0:
            player.detection_disable_period = 0

    def _state_specific(self):
        ticks = pygame.time.get_ticks() 
        common.add_to_array(self.times, ticks / 1000.0)
        self.update_player_motion_disabled_period(self.player1, ticks)
        self.update_player_motion_disabled_period(self.player2, ticks)
        if self.player1.dead or self.player2.dead:
            self.state_running = False

    def process_player_one(self, c, cm, ap):
        State.process_player_one(self, c, cm, ap)
        if self.player1.detection_disable_period == 0:
            self.player1.handle_state(self.times, self.player2)

    def process_player_two(self, c, cm, ap):
        State.process_player_two(self, c, cm, ap)
        if self.player1.detection_disable_period == 0:
            self.player2.handle_state(self.times, self.player1)        
        