import pygame
from pygame.locals import *
import cv
import os
import threading
import time
import winsound

# ======commons======

# consts

# These are the coordinates of the "inner" chessboard that FindChessboardCorners finds in Calibration_Grid3.png
# Calibration_Grid3 is 1280x720, so that is what the "seen" screen size will be.
SCREEN_RECT = ((165, 131), (1113, 131), (165, 581), (1113, 581))
#SCREEN_RECT = ((82, 65), (556, 65), (82, 290), (556, 290))


RESOLUTION = (1280, 720)
#SCALED_RESOLUTION = (640, 360)

MAX_FPS = 60
SHOW_FPS = False
DRAW_BOUNDING_BOXES = True

DIRECTION_RIGHT = 0
DIRECTION_LEFT = 1

ROUNDS_TO_WIN = 2

IMAGES_DIR = 'images'
BACKGROUND_IMAGE = IMAGES_DIR + '/backgrounds/sfz2-vega.gif'
CALIBRATION_IMAGE = IMAGES_DIR + '/Calibration_grid3.png'
FONT_NAME = IMAGES_DIR + '/mk5style.ttf'

SOUNDS_DIR = 'sounds'

# findDifference parameters
THRESHOLD = 45
WIDTH_LIM = 4
VERTEX_COUNT = 100
# gesture parameters
ARRAY_LEN = 5

class InterruptedException(Exception):
    pass
    
def opencv_img_to_pygame_img(opencv_img):
    img_str = opencv_img.tostring()[::-1]    
    pygame_img = pygame.image.fromstring(img_str, cv.GetSize(opencv_img), 'RGB')
    return pygame.transform.flip(pygame_img, True, True)

def load_image(name, colorkey=None, pixel_location = (0,0), alpha = False):
    fullname = os.path.join(IMAGES_DIR, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    if alpha:
        image = image.convert_alpha()
    else:
        image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at(pixel_location)
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def play_sfx(sfx_path):
    fullname = os.path.join(SOUNDS_DIR, sfx_path)
    winsound.PlaySound(fullname, winsound.SND_ASYNC)
    
def load_sliced_sprites(w, h, filename):
    '''
    Specs :
    	Master can be any height.
    	Sprites frames width must be the same width
    	Master width must be len(frames)*frame.width
    Assuming you ressources directory is named "images"
    '''
    images = []
    master_image = pygame.image.load(os.path.join(IMAGES_DIR, filename)).convert_alpha()

    master_width, master_height = master_image.get_size()
    for i in xrange(int(master_width/w)):
    	images.append(master_image.subsurface((i*w,0,w,h)))
    return images

def load_animation(basefilename, colorkey = None, pixel_location = (0,0)):
    filenames = sorted([x for x in os.listdir(IMAGES_DIR) if x.startswith(basefilename)]) # The files are sorted alphabetically
    return [load_image(f, colorkey, pixel_location)[0] for f in filenames]  

def add_to_array(a, o):
    a.insert(len(a), o)
    if len(a) > ARRAY_LEN:
        a.pop(0)

class CameraFeed(threading.Thread):
        def __init__(self, capture, transform_mat):
            self.cap = capture
            self.transform_mat = transform_mat
            # Set width/height
##            cv.SetCaptureProperty( self.cap, cv.CV_CAP_PROP_FRAME_WIDTH, WEBCAM_WIDTH)
##            cv.SetCaptureProperty( self.cap, cv.CV_CAP_PROP_FRAME_HEIGHT, WEBCAM_HEIGHT )
            # Acquire one image, will throw one exeption in case of no webcam present
            self.running = True
            self.readyToStop = False
            self.new_pic_available = False
            self.wait_for_pic = True
            self.lock = threading.Lock()

            threading.Thread.__init__ (self)
            print "CameraFeed: Initialized"
        
        def stop(self):
            if self.running:
                # Normal stop
                self.running = False
                while not self.readyToStop:
                    pass
            else:
                # In case stop in called when already stopped
                print 'CameraFeed: Stopped'
                return
            
        def run(self):
            while self.running:
                if self.wait_for_pic:
                    # Acquire image
                    current_img = cv.QueryFrame(self.cap)
                    # Do not process if abort in progress
                    if not self.running:
                        break
                    self.lock.acquire()
                    self.ready_img = current_img
                    self.new_pic_available = True
                    self.wait_for_pic = False
                    self.lock.release()
                else:
                    time.sleep(1.0 / MAX_FPS)

            # Once loop is finished, thread may be terminated
            self.readyToStop = True

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, images, fps = 10):
        pygame.sprite.Sprite.__init__(self)
        self.images = images

        # Track the time we started, and the time between updates.
        # Then we can figure out when we have to switch the image.
        self._start = pygame.time.get_ticks()
        self._delay = 1000 / fps
        self._last_update = 0
        self._frame = 0

        self.image = images[0]
        self.rect = self.image.get_rect()

    def update(self, t):
        # Note that this doesn't work if it's been more that self._delay
        # time between calls to update(); we only update the image once
        # then, but it really should be updated twice.

        if t - self._last_update > self._delay:
            self._frame += 1
            if self._frame >= len(self.images):
                self._frame = 0
            self.image = self.images[self._frame]
            self._last_update = t

class FloatingWord(pygame.sprite.Sprite):

    def __init__(self, img, center = (RESOLUTION[0] / 2, RESOLUTION[1] / 2), sfx = None):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = self.image = img
        self.rect = self.image.get_rect()
        self.start_size = (500, 500)
        self.end_size = (100, 100)
        self.anim_time = 1000
        self.wait_time = 0
        self.wait_forever = False
        self.finished = False
        self.grace_period = False
        self.started = False
        self.rect.center = center
        self.sfx = sfx

    def start(self):
        if not self.started:
            self.start_time = pygame.time.get_ticks()
            self.started = True
            if self.sfx != None:
                play_sfx(self.sfx)

    def update(self, t):
        elapsed_time = t - self.start_time
        if self.started and not self.grace_period:
            if elapsed_time > self.anim_time:
                self.grace_period = True
            time_ratio = float(elapsed_time) / self.anim_time
            size = (self.end_size[0] - self.start_size[0]) * time_ratio + self.start_size[0], (self.end_size[1] - self.start_size[1]) * time_ratio + self.start_size[1]
            center = self.rect.center
            self.image = pygame.transform.smoothscale(self.original_image, size)
            self.rect = self.image.get_rect()
            self.rect.center = center
        if self.grace_period:
            if self.wait_forever:
                return
            if elapsed_time > self.anim_time + self.wait_time:
                self.finished = True
                self.kill()
                return
            

class HelpText(pygame.sprite.Sprite):

    def __init__(self, initial_pos, text, font, color, pos_is_center = False):
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        self.font = font
        self.pos = initial_pos
        self.pos_is_center = pos_is_center
        self.change_text(text)

    def change_text(self, text):
        self.image = self.font.render(text, True, self.color)
        self.rect = self.image.get_rect()
        if self.pos_is_center:
            self.rect.center = self.pos
        else:
            self.rect.topleft = self.pos
            
    