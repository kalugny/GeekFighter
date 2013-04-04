import pygame
from pygame.locals import *
import cv
import common
import imcompare
from player import BasePlayer
from common import InterruptedException

class State:

    def __init__(self, screen, background, capture, ref_img, transform_mat):
        self.screen = screen
        self.background = background
        self.capture = capture
        self.ref_img = ref_img
        self.transform_mat = transform_mat
        self.state_running = True

        self.should_draw_bounding_box = common.DRAW_BOUNDING_BOXES
        self.redraw_next_frame = False

        self.font = pygame.font.Font(common.FONT_NAME, 36)

        self.sprites = pygame.sprite.LayeredUpdates()
        self.rects = []
        self.special_detection_rects = []

        self.player1, self.player2 = self.create_players()

    def create_players(self):
        return BasePlayer(common.DIRECTION_RIGHT, self), BasePlayer(common.DIRECTION_LEFT, self)

    def bounding_box(self, c, cm, ap, color, p_text):
        if self.should_draw_bounding_box:
            p_rect = pygame.rect.Rect(cv.BoundingRect(c))
            pygame.draw.rect(self.screen, color, p_rect, 2)
            pygame.draw.circle(self.screen, color, cm, 10, 2)
            pygame.draw.circle(self.screen, color, ap, 10, 2)
            text = self.font.render(p_text, 1, color)
            self.screen.blit(text, (p_rect[0], p_rect[1] - text.get_height()))
            self.rects.append(p_rect.inflate(5, text.get_height()))

    def process_player_one(self, c1, cm1, ap1):
        self.player1.set_properties(c1, cm1, ap1)
        self.player1.collision_detection(self.player2.attacks)
        self.bounding_box(c1, cm1, ap1, (255,0,0), "Player 1")
        
    def process_player_two(self, c2, cm2, ap2):
        self.player2.set_properties(c2, cm2, ap2)
        self.player2.collision_detection(self.player1.attacks)
        self.bounding_box(c2, cm2, ap2, (0,0,255), "Player 2")

    def process_attacks(self):
        collide_callable = pygame.sprite.collide_rect_ratio(0.8)
        crossed_attacks = pygame.sprite.groupcollide(self.player1.attacks, self.player2.attacks, True, True, collide_callable)
        for attack1, attack2 in crossed_attacks.iteritems():
            self.sprites.remove(attack1)
            self.sprites.remove(attack2)

    def _state_specific(self):
        pass

    def _process_event(self, event):
        pass

    def _state_destruct(self):
        pass

    def run(self):

        game_clock = pygame.time.Clock()

        camera_feed = common.CameraFeed(self.capture, self.transform_mat)
        camera_feed.start()

        self.screen.blit(self.background, (0,0))
        pygame.display.flip()

        while self.state_running:
            for event in pygame.event.get():
                self._process_event(event)
                if event.type == KEYUP and event.key == K_TAB:
                    self.state_running = False
                    break
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    camera_feed.stop()
                    raise InterruptedException()
            
            self.frame = None
            if camera_feed.new_pic_available:
                camera_feed.lock.acquire()
                self.frame = camera_feed.ready_img
                camera_feed.new_pic_available = False
                camera_feed.wait_for_pic = True
                camera_feed.lock.release()
            if not self.frame:
                continue
            self.warped_frame = cv.CreateImage(common.RESOLUTION, 8, 3)
            cv.WarpPerspective(self.frame, self.warped_frame, self.transform_mat, 0)

            self.backup_warped_frame = cv.CreateImage(common.RESOLUTION, 8, 3)            
            cv.Copy(self.warped_frame, self.backup_warped_frame)
            # make the sprites we changed not visible to the image processing
            if len(self.sprites) > 0:
                for sprite in self.sprites:
                    if self.screen.get_rect().inflate(sprite.rect.width, sprite.rect.height).contains(sprite.rect):
                        r = (sprite.rect.x if sprite.rect.x >= 0 else 0,
                             sprite.rect.y if sprite.rect.x >= 0 else 0,
                             sprite.rect.width if sprite.rect.width + sprite.rect.x <= common.RESOLUTION[0] else common.RESOLUTION[0] - sprite.rect.x,
                             sprite.rect.height if sprite.rect.height + sprite.rect.y <= common.RESOLUTION[1] else common.RESOLUTION[1] - sprite.rect.y)
                        cv.SetImageROI(self.warped_frame, r)
                        cv.SetImageROI(self.ref_img, r)
                        cv.Copy(self.ref_img, self.warped_frame)
                cv.ResetImageROI(self.warped_frame)
                cv.ResetImageROI(self.ref_img)

            # Except for those we WANT to be
            if len(self.special_detection_rects) > 0:
                for rect in self.special_detection_rects:
                    r = (rect.x, rect.y, rect.width, rect.height)
                    cv.SetImageROI(self.backup_warped_frame, r)
                    cv.SetImageROI(self.warped_frame, r)
                    cv.Copy(self.backup_warped_frame, self.warped_frame)
                cv.ResetImageROI(self.warped_frame)
                cv.ResetImageROI(self.ref_img)

                                        


            c1, cm1, c2, cm2 = imcompare.findDifference(self.ref_img, self.warped_frame, common.THRESHOLD, common.WIDTH_LIM, common.VERTEX_COUNT)

            ap1, ap2 = imcompare.get_action_points(c1, c2)

            if self.should_draw_bounding_box or self.redraw_next_frame:
                self.screen.blit(self.background, (0,0))

            self.rects = []                

            self._state_specific()
            self.sprites.update(pygame.time.get_ticks())

            if c1:
                self.process_player_one(c1, cm1, ap1)
            if c2:
                self.process_player_two(c2, cm2, ap2)

            self.process_attacks()                

            if common.SHOW_FPS:
                s = "FPS = %f" % game_clock.get_fps()
                text = self.font.render(s, 1, (10, 10, 10), (255, 255, 255))
                self.rects.append(self.screen.blit(text, (0, 0)))

            self.rects += self.sprites.draw(self.screen)


            if self.should_draw_bounding_box or self.redraw_next_frame:
                pygame.display.flip()
                self.redraw_next_frame = False
            else:
                pygame.display.update(self.rects)
            game_clock.tick(common.MAX_FPS)
            self.sprites.clear(self.screen, self.background)

        camera_feed.stop()

    