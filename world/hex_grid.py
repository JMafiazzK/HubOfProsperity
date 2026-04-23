import math
import pygame
from config import HEX_HIGHLIGHT_COLOR, HEX_RADIUS, HEX_SHADOW_COLOR, OUTLINE_COLOR

# --- Koordinaten Umrechnung ---
def hex_to_pixel(q, r, surface_size):
    center_x, center_y = get_grid_center(surface_size)
    x = HEX_RADIUS * (3/2 * q)
    y = HEX_RADIUS * (math.sqrt(3) * (r + q/2))
    return x + center_x, y + center_y

def pixel_to_hex(mouse_x, mouse_y, surface_size):
    center_x, center_y = get_grid_center(surface_size)
    x = mouse_x - center_x
    y = mouse_y - center_y

    q = (2 / 3 * x) / HEX_RADIUS
    r = (-1/3 * x + math.sqrt(3)/3 * y) / HEX_RADIUS
    return hex_round(q, r)

def get_grid_center(surface_size):
    width, height = surface_size
    return int(width * 0.56), int(height * 0.53)

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
def draw_hex(screen, q, r, color, outline_color=OUTLINE_COLOR, outline_width=2):
    x, y = hex_to_pixel(q, r, screen.get_size())
    corners = polygon_corners(x, y)
    shadow_corners = [(cx, cy + 4) for cx, cy in corners]
    inner_corners = _scale_corners(corners, (x, y), 0.88)

    pygame.draw.polygon(screen, HEX_SHADOW_COLOR, shadow_corners)
    pygame.draw.polygon(screen, _shift_color(color, -18), corners)
    pygame.draw.polygon(screen, color, inner_corners)
    highlight_points = [inner_corners[5], inner_corners[0], inner_corners[1], inner_corners[2]]
    pygame.draw.lines(screen, HEX_HIGHLIGHT_COLOR, False, highlight_points, 2)
    pygame.draw.polygon(screen, outline_color, corners, outline_width)


# --- Nachbarn ---
DIRECTIONS = [
    (1, 0), (1, -1), (0, -1),
    (-1, 0), (-1, 1), (0, 1)
]


def get_start_grid():
    return [(0, 0)] + DIRECTIONS

def get_hex(mouse_x,mouse_y, hexes, surface_size):
    clicked_hex = pixel_to_hex(mouse_x, mouse_y, surface_size)
    if clicked_hex in hexes:
        return clicked_hex
    return None


def _scale_corners(corners, center, factor):
    cx, cy = center
    scaled = []
    for x, y in corners:
        scaled.append((cx + (x - cx) * factor, cy + (y - cy) * factor))
    return scaled


def _shift_color(color, amount):
    return tuple(max(0, min(255, channel + amount)) for channel in color)
