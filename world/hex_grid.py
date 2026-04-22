import math
import pygame
from config import HEX_RADIUS, CENTER_X, CENTER_Y, OUTLINE_COLOR

# --- Koordinaten Umrechnung ---
def hex_to_pixel(q, r):
    x = HEX_RADIUS * (3/2 * q)
    y = HEX_RADIUS * (math.sqrt(3) * (r + q/2))
    return x + CENTER_X, y + CENTER_Y

def pixel_to_hex(mouse_x, mouse_y):
    x = mouse_x - CENTER_X
    y = mouse_y - CENTER_Y

    q = (2 / 3 * x) / HEX_RADIUS
    r = (-1/3 * x + math.sqrt(3)/3 * y) / HEX_RADIUS
    return hex_round(q, r)

def hex_round(q, r):
    s = -q - r

    rq = round(q)
    rr = round(r)
    rs = round(s)

    q_diff = abs(rq - q)
    r_diff = abs(rr - r)
    s_diff = abs(rs - s)

    if q_diff > r_diff and q_diff > s_diff:
        rq = -rr - rs
    elif r_diff > s_diff:
        rr = -rq - rs

    return rq, rr


# --- Hex Ecken ---
def polygon_corners(x, y):
    corners = []
    for i in range(6):
        angle = math.radians(60 * i)  # Pointy Top
        cx = x + HEX_RADIUS * math.cos(angle)
        cy = y + HEX_RADIUS * math.sin(angle)
        corners.append((cx, cy))
    return corners


# --- Zeichnen ---
def draw_hex(screen, q, r, color):
    x, y = hex_to_pixel(q, r)
    corners = polygon_corners(x, y)

    pygame.draw.polygon(screen, color, corners)
    pygame.draw.polygon(screen, OUTLINE_COLOR, corners, 2)

    # Debug Mittelpunkt
    pygame.draw.circle(screen, (255, 0, 0), (int(x), int(y)), 3)


# --- Nachbarn ---
DIRECTIONS = [
    (1, 0), (1, -1), (0, -1),
    (-1, 0), (-1, 1), (0, 1)
]


def get_start_grid():
    return [(0, 0)] + DIRECTIONS

def get_hex(mouse_x,mouse_y, hexes):
    clicked_hex = pixel_to_hex(mouse_x, mouse_y)
    if clicked_hex in hexes:
        return clicked_hex
    return None