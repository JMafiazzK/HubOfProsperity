import pygame
from win32api import mouse_event
import mouse

from config import BG_COLOR, HEX_COLOR, HUB_COLOR
from world.hex_grid import draw_hex, get_start_grid, pixel_to_hex


def run_game(screen):
    clock = pygame.time.Clock()

    hexes = get_start_grid()

    running = True
    while running:
        screen.fill(BG_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Linksklick
                    x, y = event.pos
                    pixel_to_hex(x, y)


        # --- DRAW ---
        for q, r in hexes:
            if (q, r) == (0, 0):
                color = HUB_COLOR
            else:
                color = HEX_COLOR

            draw_hex(screen, q, r, color)



        pygame.display.flip()
        clock.tick(60)
