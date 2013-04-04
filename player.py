import pygame
from pygame.locals import *
import cv
import common
import imcompare
from effects import FireBall, Fist, Boot, Dragon, Shadow


class BasePlayer(pygame.sprite.Sprite):

    CROUCH_RATIO = 0.85
    HIT_DISTANCE_RATIO = 0.35
    HIT_SPEED_RATIO = 0.50
    HIGH_HIT_RATIO = 1.1

    def __init__(self, direction, state):
        pygame.sprite.Sprite.__init__(self)
        self.direction = direction
        self.state = state
        self.contour = None
        self.attacks = pygame.sprite.Group()
        self.initialized = False

    def set_properties(self, c, cm, ap):
        self.rect = pygame.rect.Rect(cv.BoundingRect(c))
        self.contour = c
        self.center_of_mass = cm
        self.action_point = ap
        self.initialized = True

    def collision_detection(self, attacks):
        collide_callable = pygame.sprite.collide_rect_ratio(0.8)
        attackers = pygame.sprite.spritecollide(self, attacks, True, collide_callable)
        for attacker in attackers:
            self.handle_attacker(attacker)

    def set_motion_params(self, height):
        self.height = height
        self.crouch_height = self.CROUCH_RATIO * self.height
        self.hit_distance = self.HIT_DISTANCE_RATIO * self.height
        self.hit_speed = self.HIT_SPEED_RATIO * self.height
        self.high_hit_height = self.HIGH_HIT_RATIO * self.height
        
    def handle_attacker(self, attacker):
        attacker.remove(self.state.sprites)

class Player(BasePlayer):    

    def __init__(self, direction, state, wins, height):
        BasePlayer.__init__(self, direction, state)

        self.set_motion_params(height)
        self.detection_disable_period = 0
        self.cm_array = []
        self.ap_array = []
        self.height_array = []
        self.move_state = 'Idle'
        self.previous_move_states = 'Idle'

        self.wins = wins
        self.dead = False

        if self.direction == common.DIRECTION_RIGHT:
            healthbar_pos = (40, 40)
            wins_pos = (healthbar_pos[0] + HealthBar.HEALTHBAR_DIMS.width + 5, 40)
            dir = 1
            help_text_pos = (40, 40 + healthbar_pos[1] + 5)
            color = (255, 0, 0)
        else:
            healthbar_pos = (common.RESOLUTION[0] - HealthBar.HEALTHBAR_DIMS.width - 40, 40)
            wins_pos = (healthbar_pos[0] - 5, 40)
            dir = -1
            help_text_pos = (common.RESOLUTION[0] / 2, 40 + healthbar_pos[1] + 5)
            color = (0, 0, 255)
        self.healthbar = HealthBar(healthbar_pos, self.direction)
        self.skulls = []
        for i in range(self.wins):
            skull = Skull(wins_pos, self.direction)
            skull.add(self.state.sprites)
            self.skulls.append(skull)
            wins_pos = (wins_pos[0] + dir*5 + dir*skull.rect.width, wins_pos[1])
        self.healthbar.add(self.state.sprites)

        self.help_text = common.HelpText(help_text_pos, self.move_state, self.state.font, color)
        self.hide_show_helptext(self.state.should_draw_bounding_box)
        

    def fireball(self, other = None):
        fireball = FireBall(self.action_point, self.direction)
        fireball.add(self.state.sprites)
        fireball.add(self.attacks)

    def punch(self, other = None):
        fist = Fist(initial_pos = self.action_point, direction = self.direction, groups = (self.state.sprites, self.attacks), sons = 4, alpha_drop = 63, delay = 50)

    def kick(self, other = None):
        boot = Boot(initial_pos = self.action_point, direction = self.direction, groups = (self.state.sprites, self.attacks), sons = 4, alpha_drop = 63, delay = 50)

    def super(self, other = None):
        dragon = Dragon(other.center_of_mass, self.direction)
        dragon.add(self.state.sprites)
        other.take_damage(dragon.damage, dragon.ATTACK_LENGTH)

    def shadow(self, other = None):
        shadow = Shadow({'contour': self.contour, 'orig_image': self.state.warped_frame}, self.center_of_mass, self.direction, (self.state.sprites, self.attacks), sons = 4, alpha = 200, alpha_drop = 40, delay = 70)

    def take_damage(self, damage, disabled_time = 0):
        self.healthbar.take_damage(damage)
        self.previous_move_states = 'Idle'
        if self.healthbar.is_dead():
            self.dead = True
        self.detection_disable_period = disabled_time

    def handle_attacker(self, attacker):
        BasePlayer.handle_attacker(self, attacker)
        self.take_damage(attacker.damage)

    def handle_state(self, times, other):
        common.add_to_array(self.cm_array, self.center_of_mass)
        common.add_to_array(self.ap_array, self.action_point)
        common.add_to_array(self.height_array, imcompare.find_contour_height(self.contour))

        if len(times) == common.ARRAY_LEN:
            xAP, yAP, vAP, vH, h = imcompare.get_motion_params(self.cm_array, self.ap_array, self.height_array, times)
            state = imcompare.get_current_state(xAP, yAP, vAP, vH, h, self.move_state, self.crouch_height, self.hit_distance, self.hit_speed, self.high_hit_height)
            if self.move_state != state:
                self.previous_move_states += '-' + state
                self.make_move(other)
                self.move_state = state

    def make_move(self, other):
        # moves should be ordered from the most complicated to the most simple
        moves = (
                 ('-Crouch-Idle-Punch-Idle-Crouch-Idle-High Punch', self.super),
                 ('-High Punch-Idle-Crouch-Idle-Punch', self.shadow),
                 ('-Crouch-Idle-Kick-Idle-Punch', self.fireball),
                 ('-Crouch-Low Punch', self.punch),
                 ('-Punch', self.punch),
                 ('-Kick', self.kick),
                )
        self.help_text.change_text(self.previous_move_states[-40:])

        for move, move_func in moves:
            if self.previous_move_states.endswith(move):
                move_func(other)
                break

    def hide_show_helptext(self, should_show):
        if not should_show:
            self.help_text.remove(self.state.sprites)
        else:
            self.help_text.add(self.state.sprites)

class Skull(pygame.sprite.Sprite):

    def __init__(self, initial_pos, direction):
        pygame.sprite.Sprite.__init__(self)
        self.direction = direction
        self.image, self.rect = common.load_image('skull.png', -1)
        self.rect.topleft = initial_pos
        if self.direction == common.DIRECTION_LEFT:
            self.rect.topright = self.rect.topleft

class HealthBar(pygame.sprite.Sprite):

    HEALTHBAR_DIMS = pygame.rect.Rect((0, 0, 400, 30))
    INSIDE_RECT = HEALTHBAR_DIMS.inflate(-3, -3)

    def __init__(self, initial_pos, direction, max_health = 100):
        pygame.sprite.Sprite.__init__(self)
        self.max_health = max_health
        self.health = self.last_health = max_health
        self.image = pygame.Surface(self.HEALTHBAR_DIMS.size)
        self.image.fill((250, 250, 250))
        pygame.draw.rect(self.image, (250, 250, 0), self.INSIDE_RECT)
        self.rect = self.image.get_rect()
        self.rect.topleft = initial_pos
        self.pixels_per_health_point = float(self.INSIDE_RECT.width) / self.max_health
        self.direction = direction

    def take_damage(self, damgage):
        self.health -= damgage
        if self.health <= 0:
            self.health = 0

    def is_dead(self):
        return self.health == 0
        
    def update(self, t):
        if self.health != self.last_health:
            self.last_health = self.health
            health_lost = self.max_health - self.health
            lost_rect = self.INSIDE_RECT.copy()
            lost_rect.width = health_lost * self.pixels_per_health_point
            if self.direction == common.DIRECTION_LEFT:
                lost_rect.topleft = self.INSIDE_RECT.topleft
            else:
                lost_rect.topright = self.INSIDE_RECT.topright
            pygame.draw.rect(self.image, (150, 0, 0), lost_rect)         