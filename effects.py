import pygame
from pygame.locals import *
import common
import cv

class FireBall(common.AnimatedSprite):
    FIREBALL_BASENAME = 'fireball'
    FIREBALL_SPPED = 40
    
    def __init__(self, initial_pos, direction):
        try:
            if FireBall.images == None:
                FireBall.images = common.load_animation(self.FIREBALL_BASENAME, -1)
        except AttributeError:
            FireBall.images = common.load_animation(self.FIREBALL_BASENAME, -1)
        common.AnimatedSprite.__init__(self, FireBall.images, 10)
        self.rect.midleft = initial_pos
        self.direction = direction
        if self.direction == common.DIRECTION_LEFT:
            self.images = [pygame.transform.flip(image, True, False) for image in self.images]
            self.rect.midright = self.rect.midleft

        common.play_sfx('hadouken.wav')
        self.damage = 10            

    def update(self, t):
        common.AnimatedSprite.update(self, t)
        if self.direction == common.DIRECTION_LEFT:
            self.rect.move_ip((-self.FIREBALL_SPPED, 0))
        else:
            self.rect.move_ip((self.FIREBALL_SPPED, 0))

class GameSprite(pygame.sprite.Sprite):

    def __init__(self, pic_params, initial_pos, direction, groups, sons, alpha, alpha_drop, delay, first, ignore_dir):
        pygame.sprite.Sprite.__init__(self)
        self.pic_params = pic_params
        self.groups = groups
        self.initial_pos = initial_pos
        self.sons = sons
        self.alpha = alpha
        self.alpha_drop = alpha_drop
        self.delay = delay
        self.image, self.rect = self.load_image(**pic_params)
        self.image.set_alpha(self.alpha)
        self.start_time = self.last_time = pygame.time.get_ticks()
        self.rect.midleft = initial_pos
        self.direction = direction
        self.ignore_dir = ignore_dir
        if self.direction == common.DIRECTION_LEFT:
            if not self.ignore_dir:
                self.image = pygame.transform.flip(self.image, True, False)
            self.rect.midright = self.rect.midleft
        self.add(groups)
        if first:
            self.groups = [self.groups[0]]

    def load_image(self, **kwargs):
        return common.load_image(**kwargs)

    def update(self, t):
        from_start = t - self.start_time
        if self.sons > 0 and from_start > self.delay:
            son = self.__class__(self.pic_params, self.initial_pos, self.direction, self.groups, self.sons - 1, self.alpha - self.alpha_drop, self.alpha_drop, self.delay, False, self.ignore_dir)
            self.groups[0].move_to_back(son)
            self.sons = 0

class Fist(GameSprite):

    FIST_INITIAL_SPEED = 9         # in pixels/frame
    FIST_DECELERATION = 0.01       # in pixels/ms^2

    def __init__(self, pic_params = {'name': 'fist.png', 'alpha': True}, initial_pos = (0,0), direction = common.DIRECTION_LEFT, groups = [], sons = 0, alpha = 255, alpha_drop = 85, delay = 0, first = True, ignore_dir = False):
        GameSprite.__init__(self, pic_params, initial_pos, direction, groups, sons, alpha, alpha_drop, delay, first, ignore_dir)
        self.speed = self.FIST_INITIAL_SPEED
        self.damage = 2
        if first:
            common.play_sfx('punch.wav')

    def update(self, t):
        GameSprite.update(self, t)
        elapsed_time = t - self.last_time
        self.speed = self.speed - self.FIST_DECELERATION * elapsed_time
        self.last_time = pygame.time.get_ticks()
        if self.speed < 0:
            self.kill()
        if self.direction == common.DIRECTION_LEFT:
            
            self.rect.move_ip((-self.speed, 0))
        else:
            self.rect.move_ip((self.speed, 0))

class Boot(GameSprite):
    BOOT_INITIAL_SPEED = 9
    BOOT_DECELERATION = 0.015

    def __init__(self, pic_params = {'name': 'boot.gif', 'colorkey': -1}, initial_pos = (0,0), direction = common.DIRECTION_LEFT, groups = [], sons = 0, alpha = 255, alpha_drop = 85, delay = 0, first = True, ignore_dir = False):
        GameSprite.__init__(self, pic_params, initial_pos, direction, groups, sons, alpha, alpha_drop, delay, first, ignore_dir)
        self.last_time = pygame.time.get_ticks()
        self.speed = self.BOOT_INITIAL_SPEED
        self.angle = 0
        self.original_image = self.image
        self.damage = 2
        if first:
            common.play_sfx('kick.wav')

    def update(self, t):
        GameSprite.update(self, t)
        elapsed_time = t - self.last_time
        self.speed = self.speed - self.BOOT_DECELERATION * elapsed_time
        self.last_time = pygame.time.get_ticks()
        if self.speed <= 0:
            self.kill()
            
        oldCenter = self.rect.center
        if self.direction == common.DIRECTION_LEFT:
            self.angle -= self.speed
            self.image = pygame.transform.rotate(self.original_image, self.angle)
        else:
            self.angle += self.speed
            self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = oldCenter
        
        if self.direction == common.DIRECTION_LEFT:
            self.rect.move_ip((-self.speed, 0))
        else:
            self.rect.move_ip((self.speed, 0))

class Dragon(common.AnimatedSprite):

    ATTACK_LENGTH = 2200    

    def __init__(self, initial_pos, direction):
        try:
            if Dragon.images == None:
                Dragon.images = common.load_animation('dragon', -1, pixel_location = (725, 0))
        except AttributeError:
            Dragon.images = common.load_animation('dragon', -1, pixel_location = (725, 0))
        common.AnimatedSprite.__init__(self, Dragon.images, 9)
        self.rect.top = 0
        self.rect.center = initial_pos[0], self.rect.center[1]
        self.direction = direction
        if self.direction == common.DIRECTION_LEFT:
            self.images = [pygame.transform.flip(image, True, False) for image in self.images]
            self.rect.move_ip((50,0))
        else:
            self.rect.move_ip((-50,0))

        self.damage = 40

        self.sfx = common.play_sfx('roar.wav')

    def update(self, t):
        common.AnimatedSprite.update(self, t)

        if t - self._start > self.ATTACK_LENGTH:
            self.kill()


class Shadow(GameSprite):
    SHADOW_INITIAL_SPEED = 20
    SHADOW_DECELERATION = 0.015

    def load_image(self, contour, orig_image):
        mask = cv.CreateImage( cv.GetSize(orig_image), 8, 1)
        cv.Set(mask, cv.RGB(0, 0, 0))
        cv.DrawContours(mask, contour, cv.RGB(255, 255, 255), cv.RGB(255, 255, 255), 0, -1)
        img = cv.CreateImage( cv.GetSize(orig_image), 8, 3)
        cv.Set(img, cv.RGB(255, 0, 0))
        cv.Copy(orig_image, img, mask)
        big_image = common.opencv_img_to_pygame_img(img)
        p_rect = pygame.rect.Rect(cv.BoundingRect(contour))
        image = pygame.Surface((p_rect.width, p_rect.height))
        rect = image.blit(big_image, (0, 0), p_rect)
        image.set_colorkey((255, 0, 0), RLEACCEL)
        return image, rect
        

    def __init__(self, pic_params, initial_pos, direction, groups, sons = 0, alpha = 255, alpha_drop = 85, delay = 0, first = True, ignore_dir = True):
        GameSprite.__init__(self, pic_params, initial_pos, direction, groups, sons, alpha, alpha_drop, delay, first, ignore_dir)
        self.last_time = pygame.time.get_ticks()
        self.speed = self.SHADOW_INITIAL_SPEED
        self.damage = 20
        common.play_sfx('whoosh.wav')

    def update(self, t):
        GameSprite.update(self, t)
        elapsed_time = t - self.last_time
        self.speed = self.speed - self.SHADOW_DECELERATION * elapsed_time
        self.last_time = pygame.time.get_ticks()
        if self.speed < 0:
            self.kill()
        if self.direction == common.DIRECTION_LEFT:
            
            self.rect.move_ip((-self.speed, 0))
        else:
            self.rect.move_ip((self.speed, 0))
        
        