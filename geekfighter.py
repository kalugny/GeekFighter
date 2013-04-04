import pygame
from pygame.locals import *
import cv
import common
from calibration_state import CalibrationState
from tutorial_state import TutorialState
from countdown_state import CountdownState
from game_state import GameState
from winning_state import WinningState
import pgmusic
from common import InterruptedException
    
def main():
    # Initialise screen
    pygame.init()
    screen = pygame.display.set_mode(common.RESOLUTION, FULLSCREEN)
    pygame.display.set_caption('Super Geek Fighter II Turbo')    

    # Start the camera
    capture = cv.CaptureFromCAM(0)
  
    background = pygame.image.load(common.BACKGROUND_IMAGE).convert()
    background = pygame.transform.scale(background, common.RESOLUTION)

    # calibrate the camera with the projection
    calibration_state = CalibrationState(screen, capture)
    transform_mat = calibration_state.run()
    reference_img = calibration_state.make_background(background, transform_mat)
    music_started = False
    try:
        while True:
            tutorial_state = TutorialState(screen, background, capture, reference_img, transform_mat)
            tutorial_state.run()
            players_height = [tutorial_state.player1_height, tutorial_state.player2_height]

            total_win = False
            wins = {'Player 1': 0, 'Player 2': 0}
            pgmusic.start_music_thread()
            music_started = True
            while not total_win:
                countdown_state = CountdownState(screen, background, capture, reference_img, transform_mat)
                countdown_state.run()

                game_state = GameState(screen, background, capture, reference_img, transform_mat, wins, players_height)
                game_state.run()

                winning_player = None
                if game_state.player2.dead:
                    winning_player = game_state.player1
                    winning_player.name = 'Player 1'
                if game_state.player1.dead:
                    winning_player = game_state.player2
                    winning_player.name = 'Player 2'
                # TODO: What if both die at the same time?
                if winning_player:
                    wins[winning_player.name] += 1
                    winning_state = WinningState(screen, background, capture, reference_img, transform_mat, wins, winning_player, game_state.sprites)
                    winning_state.run()
                    total_win = winning_state.big_win
            pgmusic.fadeout()
            music_started = False
    except InterruptedException:
        print 'Bye bye!'
    finally:
        if music_started:
            pgmusic.fadeout()   
  
if __name__ == '__main__':
    main()