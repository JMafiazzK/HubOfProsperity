import pygame

from config import HEX_COLOR, HOVER_OUTLINE_COLOR, MIN_HEIGHT, MIN_WIDTH, OUTLINE_COLOR, SELECTED_OUTLINE_COLOR
from game.state import GameState
from ui.controls import draw_scene_background
from ui.hud import (
    draw_city_panel,
    draw_economy_panel,
    handle_city_panel_click,
    handle_city_panel_keydown,
    handle_economy_panel_click,
)
from world.hex_grid import draw_hex, get_start_grid, get_hex


def run_game(screen):
    clock = pygame.time.Clock()

    hexes = get_start_grid()
    game_state = GameState()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                new_width = max(MIN_WIDTH, event.w)
                new_height = max(MIN_HEIGHT, event.h)
                screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if handle_city_panel_keydown(event, game_state):
                    continue
                if event.key == pygame.K_SPACE:
                    game_state.toggle_simulation()
                    continue
                if event.key == pygame.K_ESCAPE:
                    game_state.clear_selection()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if handle_economy_panel_click(event.pos, game_state, screen.get_size()):
                    continue
                if handle_city_panel_click(event.pos, game_state, screen.get_size()):
                    continue

                clicked_hex = get_hex(event.pos[0], event.pos[1], hexes, screen.get_size())
                if clicked_hex is None:
                    game_state.clear_selection()
                else:
                    game_state.select_hex(clicked_hex)

        game_state.update(dt)

        # --- DRAW ---
        draw_scene_background(screen)
        hovered_hex = get_hex(*pygame.mouse.get_pos(), hexes, screen.get_size())
        for q, r in hexes:
            hex_coords = (q, r)
            city = game_state.get_city(hex_coords)
            color = city.color if city is not None else HEX_COLOR
            is_selected = game_state.selected_hex == hex_coords
            is_hovered = hovered_hex == hex_coords
            outline_color = OUTLINE_COLOR
            outline_width = 2

            if is_hovered:
                outline_color = HOVER_OUTLINE_COLOR
                outline_width = 3
            if is_selected:
                outline_color = SELECTED_OUTLINE_COLOR
                outline_width = 4

            draw_hex(screen, q, r, color, outline_color=outline_color, outline_width=outline_width)

        draw_city_panel(screen, game_state)
        draw_economy_panel(screen, game_state)

        pygame.display.flip()
