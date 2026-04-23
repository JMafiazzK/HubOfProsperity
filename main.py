import pygame
from config import WIDTH, HEIGHT
from game.game_loop import run_game

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Hub of Prosperity")

run_game(screen)

pygame.quit()
