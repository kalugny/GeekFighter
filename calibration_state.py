import pygame
import cv
from State import State
import common

class CalibrationState:

    def __init__(self, screen, capture):
        self.screen = screen
        self.capture = capture

        pygame.init()        
        

    def run(self):
    
        calib_img = pygame.image.load(common.CALIBRATION_IMAGE).convert()
        calib_img = pygame.transform.scale(calib_img, common.RESOLUTION)
        
        self.screen.blit(calib_img, (0, 0))
        pygame.display.flip()
        pygame.time.wait(1000)  

        # this is actually the dimensions of the "inner chessboard" (see FindChessboardCorners documentation)
        chessboard_dim = ( 8, 5 )

        # For some reason the first capture doesn't get the chessboard (even though it's there 5 secs!) and the second one sometimes comes out blurry.
        whole_view = cv.QueryFrame(self.capture)
        whole_view = cv.QueryFrame(self.capture)

        # converting our image to grayscale. Might be unnecessary.
        whole_view_gs = cv.CreateImage(cv.GetSize(whole_view), whole_view.depth, 1)
        cv.CvtColor(whole_view, whole_view_gs, cv.CV_BGR2GRAY)
        found_all, corners = cv.FindChessboardCorners( whole_view_gs, chessboard_dim )

        if found_all:
            cv.DrawChessboardCorners( whole_view, chessboard_dim, corners, found_all )
        else:
            print "Only found ", len(corners), " corners"
            self.screen.blit(common.opencv_img_to_pygame_img(whole_view), (0,0))
            pygame.display.flip()
            pygame.time.wait(1000)
            exit(1)

        # these are the bounding 4 points of the inner chessboard.
        bounding_rect = (corners[39], corners[32], corners[7], corners[0])
        
        transform_mat = cv.CreateMat(3, 3, cv.CV_32F)
        cv.GetPerspectiveTransform(bounding_rect, common.SCREEN_RECT, transform_mat)
        
        return transform_mat

    def make_background(self, background_image, transform_mat):
        
        self.screen.blit(background_image, (0, 0))
        pygame.display.flip()
        pygame.time.wait(1000)
        reference_img = cv.QueryFrame(self.capture)
        reference_img = cv.QueryFrame(self.capture)
##        small_reference_img = cv.CreateImage((reference_img.width / 2, reference_img.height /2), 8 ,3)
##        cv.Resize(reference_img, small_reference_img)
         
        calibrated_image = cv.CreateImage(common.RESOLUTION, 8, 3)
        cv.WarpPerspective(reference_img, calibrated_image, transform_mat, 0)

        return calibrated_image