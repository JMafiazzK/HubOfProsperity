import os

import pygame

from config import (
    BG_BOTTOM_COLOR,
    BG_GLOW_COLOR,
    BG_SECONDARY_GLOW_COLOR,
    BG_TOP_COLOR,
    BUTTON_ACTIVE_COLOR,
    BUTTON_ACTIVE_HOVER_COLOR,
    BUTTON_COLOR,
    BUTTON_DISABLED_COLOR,
    BUTTON_TEXT_LIGHT,
    CARD_BG_COLOR,
    CARD_BORDER_COLOR,
    DANGER_COLOR,
    DIVIDER_COLOR,
    INFO_COLOR,
    INPUT_ACTIVE_COLOR,
    INPUT_BG_COLOR,
    INPUT_BORDER_COLOR,
    MUTED_TEXT_COLOR,
    PANEL_ACCENT_COLOR,
    PANEL_ACCENT_SOFT_COLOR,
    PANEL_BG_BOTTOM_COLOR,
    PANEL_BG_COLOR,
    PANEL_BORDER_COLOR,
    PANEL_SHADOW_COLOR,
    POSITIVE_COLOR,
    STATUS_BG_COLOR,
    TEXT_COLOR,
    WARNING_COLOR,
)


_FONT_CACHE = {}
_GRADIENT_CACHE = {}
_HEADER_FONT_PATH = "C:\\Windows\\Fonts\\BOOKOSB.TTF"
_BODY_FONT_PATH = "C:\\Windows\\Fonts\\segoeui.ttf"
_BODY_BOLD_FONT_PATH = "C:\\Windows\\Fonts\\segoeuib.ttf"


def get_font(size, bold=False, face="body"):
    key = (size, bold, face)
    if key not in _FONT_CACHE:
        font_path = _get_font_path(face, bold)
        if font_path and os.path.exists(font_path):
            _FONT_CACHE[key] = pygame.font.Font(font_path, size)
        else:
            fallback_name = "book antiqua" if face == "header" else "segoe ui"
            _FONT_CACHE[key] = pygame.font.SysFont(fallback_name, size, bold=bold)
    return _FONT_CACHE[key]


def draw_panel(surface, rect):
    radius = max(18, min(rect.width, rect.height) // 20)
    draw_soft_shadow(surface, rect, color=PANEL_SHADOW_COLOR, offset=(0, 12), spread=22)
    draw_gradient_rect(surface, rect, PANEL_BG_COLOR, PANEL_BG_BOTTOM_COLOR, radius)
    pygame.draw.rect(surface, PANEL_BORDER_COLOR, rect, 2, border_radius=radius)

    inner_rect = rect.inflate(-10, -10)
    pygame.draw.rect(surface, (48, 60, 80), inner_rect, 1, border_radius=max(12, radius - 4))

    accent_rect = pygame.Rect(rect.left + 18, rect.top + 16, rect.width - 36, 2)
    draw_gradient_rect(surface, accent_rect, PANEL_ACCENT_COLOR, PANEL_ACCENT_SOFT_COLOR, 1)

    _draw_corner_ornaments(surface, rect, PANEL_BORDER_COLOR)
    _draw_corner_ornaments(surface, inner_rect, PANEL_ACCENT_SOFT_COLOR, inset=5)


def draw_card(surface, rect, fill_color=CARD_BG_COLOR, border_color=CARD_BORDER_COLOR):
    radius = max(14, min(rect.width, rect.height) // 4)
    draw_soft_shadow(surface, rect, color=(0, 0, 0, 72), offset=(0, 5), spread=10)
    draw_gradient_rect(surface, rect, fill_color, _shift_color(fill_color, -10), radius)
    pygame.draw.rect(surface, border_color, rect, 1, border_radius=radius)
    _draw_corner_ornaments(surface, rect, border_color, corner_size=max(8, rect.height // 5))


def draw_badge(surface, rect, label, fill_color, text_color=BUTTON_TEXT_LIGHT, font_size=16):
    radius = max(10, rect.height // 2)
    draw_gradient_rect(surface, rect, _shift_color(fill_color, 10), _shift_color(fill_color, -8), radius)
    pygame.draw.rect(surface, _shift_color(fill_color, -36), rect, 1, border_radius=radius)

    text_surface = get_font(font_size, bold=True, face="header").render(label.upper(), True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)


def draw_divider(surface, left, right, y):
    pygame.draw.line(surface, DIVIDER_COLOR, (left, y), (right, y), 1)
    pygame.draw.line(surface, (44, 54, 70), (left, y + 1), (right, y + 1), 1)
    center_x = (left + right) // 2
    pygame.draw.line(surface, PANEL_ACCENT_SOFT_COLOR, (center_x - 18, y), (center_x - 5, y), 1)
    pygame.draw.line(surface, PANEL_ACCENT_SOFT_COLOR, (center_x + 5, y), (center_x + 18, y), 1)
    pygame.draw.polygon(surface, PANEL_ACCENT_COLOR, [(center_x, y - 3), (center_x + 3, y), (center_x, y + 3), (center_x - 3, y)])


def draw_scene_background(surface):
    width, height = surface.get_size()
    surface.blit(_get_gradient_surface((width, height), BG_TOP_COLOR, BG_BOTTOM_COLOR), (0, 0))

    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.circle(overlay, BG_GLOW_COLOR, (int(width * 0.74), int(height * 0.18)), int(min(width, height) * 0.34))
    pygame.draw.circle(overlay, BG_SECONDARY_GLOW_COLOR, (int(width * 0.18), int(height * 0.82)), int(min(width, height) * 0.3))
    pygame.draw.circle(overlay, (8, 12, 19, 124), (width // 2, height // 2), int(min(width, height) * 0.54))

    for index in range(4):
        y = int(height * (0.2 + index * 0.16))
        pygame.draw.line(overlay, (255, 255, 255, 4), (0, y), (width, y), 1)

    pygame.draw.line(overlay, (205, 163, 91, 8), (int(width * 0.08), int(height * 0.16)), (int(width * 0.24), int(height * 0.08)), 1)
    pygame.draw.line(overlay, (205, 163, 91, 8), (int(width * 0.8), int(height * 0.9)), (int(width * 0.94), int(height * 0.8)), 1)
    surface.blit(overlay, (0, 0))


def draw_text(surface, text, position, size=18, color=TEXT_COLOR, bold=False, face="body"):
    text_surface = get_font(size, bold=bold, face=face).render(text, True, color)
    surface.blit(text_surface, position)


def wrap_text(text, size, max_width, bold=False, face="body"):
    font = get_font(size, bold=bold, face=face)
    words = text.split()
    if not words:
        return []

    lines = []
    current_line = words[0]
    for word in words[1:]:
        candidate = f"{current_line} {word}"
        if font.size(candidate)[0] <= max_width:
            current_line = candidate
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)
    return lines


def draw_wrapped_text(surface, text, rect, size=18, color=TEXT_COLOR, bold=False, line_gap=2, face="body"):
    font = get_font(size, bold=bold, face=face)
    y = rect.top
    line_height = font.get_linesize() + line_gap
    if rect.height <= 0:
        return y

    max_lines = max(1, (rect.height + line_gap) // line_height)
    lines = wrap_text(text, size, rect.width, bold=bold, face=face)

    if len(lines) > max_lines:
        visible_lines = lines[:max_lines]
        overflow_source = visible_lines[-1]
        while overflow_source:
            candidate = overflow_source.rstrip() + "..."
            if font.size(candidate)[0] <= rect.width:
                visible_lines[-1] = candidate
                break
            overflow_source = overflow_source[:-1]
        else:
            visible_lines[-1] = "..."
        lines = visible_lines

    for line in lines:
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (rect.left, y))
        y += line_height
    return y


def draw_action_button(surface, rect, label, variant="default", enabled=True, selected=False, hovered=False, font_size=18):
    top_color, bottom_color, border_color, text_color = _get_button_palette(variant, hovered, enabled, selected)
    radius = max(10, rect.height // 3)
    draw_soft_shadow(surface, rect, color=(0, 0, 0, 72), offset=(0, 5), spread=10)
    draw_gradient_rect(surface, rect, top_color, bottom_color, radius)
    pygame.draw.rect(surface, border_color, rect, 2, border_radius=radius)
    _draw_corner_ornaments(surface, rect.inflate(-4, -4), _shift_color(border_color, 20), corner_size=max(7, rect.height // 5))
    pygame.draw.line(surface, (255, 244, 218), (rect.left + 10, rect.top + 8), (rect.right - 10, rect.top + 8), 1)

    button_font = _get_fitted_font(label.upper(), font_size, max(10, rect.width - 24), bold=True, face="header")
    text_surface = button_font.render(label.upper(), True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)


def draw_input(surface, rect, text, active=False, placeholder="", font_size=18):
    border_color = INPUT_ACTIVE_COLOR if active else INPUT_BORDER_COLOR
    radius = max(10, rect.height // 3)
    draw_soft_shadow(surface, rect, color=(0, 0, 0, 64), offset=(0, 4), spread=8)
    draw_gradient_rect(surface, rect, INPUT_BG_COLOR, _shift_color(INPUT_BG_COLOR, -10), radius)
    pygame.draw.rect(surface, border_color, rect, 2, border_radius=radius)
    pygame.draw.line(surface, (58, 69, 90), (rect.left + 10, rect.top + 8), (rect.right - 10, rect.top + 8), 1)

    display_text = text or placeholder
    text_color = TEXT_COLOR if text else MUTED_TEXT_COLOR
    text_surface = get_font(font_size, face="body").render(display_text, True, text_color)
    text_y = rect.centery - text_surface.get_height() // 2
    surface.blit(text_surface, (rect.left + 12, text_y))

    if active:
        caret_x = min(rect.right - 14, rect.left + 16 + text_surface.get_width())
        caret_height = max(14, rect.height // 2)
        pygame.draw.line(surface, PANEL_ACCENT_COLOR, (caret_x, rect.centery - caret_height // 2), (caret_x, rect.centery + caret_height // 2), 2)


def draw_progress_bar(surface, rect, fraction, fill_color):
    fraction = max(0.0, min(1.0, fraction))
    radius = max(4, rect.height // 2)
    draw_gradient_rect(surface, rect, (14, 21, 31), (8, 13, 21), radius)
    pygame.draw.rect(surface, (58, 70, 88), rect, 1, border_radius=radius)

    if fraction <= 0:
        return

    fill_width = max(8, int((rect.width - 4) * fraction))
    fill_rect = pygame.Rect(rect.left + 2, rect.top + 2, min(rect.width - 4, fill_width), rect.height - 4)
    draw_gradient_rect(surface, fill_rect, _shift_color(fill_color, 18), _shift_color(fill_color, -10), max(3, radius - 2))
    pygame.draw.line(surface, (255, 248, 230), (fill_rect.left + 4, fill_rect.top + 1), (fill_rect.right - 4, fill_rect.top + 1), 1)


def draw_eye_emblem(surface, center, size, accent_color=PANEL_ACCENT_COLOR):
    cx, cy = center
    star_points = [
        (cx, cy - size),
        (cx + size * 0.34, cy - size * 0.34),
        (cx + size, cy),
        (cx + size * 0.34, cy + size * 0.34),
        (cx, cy + size),
        (cx - size * 0.34, cy + size * 0.34),
        (cx - size, cy),
        (cx - size * 0.34, cy - size * 0.34),
    ]
    star_points = [(int(x), int(y)) for x, y in star_points]
    pygame.draw.polygon(surface, _shift_color(accent_color, -60), star_points)
    pygame.draw.polygon(surface, accent_color, star_points, 2)

    ring_radius = max(8, int(size * 0.56))
    pygame.draw.circle(surface, (18, 24, 37), center, ring_radius)
    pygame.draw.circle(surface, accent_color, center, ring_radius, 2)

    eye_width = int(size * 1.1)
    eye_height = max(8, int(size * 0.52))
    eye_rect = pygame.Rect(cx - eye_width // 2, cy - eye_height // 2, eye_width, eye_height)
    pygame.draw.ellipse(surface, BUTTON_TEXT_LIGHT, eye_rect)
    pygame.draw.ellipse(surface, _shift_color(accent_color, -32), eye_rect, 2)
    pygame.draw.circle(surface, _shift_color(INFO_COLOR, 28), center, max(4, int(size * 0.18)))
    pygame.draw.circle(surface, (14, 10, 10), center, max(2, int(size * 0.09)))

    for dx, dy in ((0, -size - 6), (0, size + 6), (-size - 6, 0), (size + 6, 0)):
        pygame.draw.line(surface, accent_color, (cx, cy), (cx + dx, cy + dy), 1)


def draw_section_title(surface, text, position, size=16):
    draw_text(surface, text.upper(), position, size=size, color=PANEL_ACCENT_COLOR, bold=True, face="header")


def draw_stat_row(surface, label_pos, value_pos, label, value, label_size=13, value_size=16, value_color=TEXT_COLOR):
    draw_text(surface, label.upper(), label_pos, size=label_size, color=PANEL_ACCENT_COLOR, bold=True)
    draw_text(surface, value, value_pos, size=value_size, color=value_color, bold=True)


def draw_meter_row(surface, rect, label, value_text, fraction, fill_color, label_size=12, value_size=14):
    draw_text(surface, label.upper(), (rect.left, rect.top), size=label_size, color=MUTED_TEXT_COLOR, bold=True)
    value_surface = get_font(value_size, bold=True, face="body").render(value_text, True, TEXT_COLOR)
    surface.blit(value_surface, (rect.right - value_surface.get_width(), rect.top - 1))
    bar_rect = pygame.Rect(rect.left, rect.bottom - 10, rect.width, 8)
    draw_progress_bar(surface, bar_rect, fraction, fill_color)


def draw_resource_row(
    surface,
    rect,
    label,
    amount_text,
    fraction,
    fill_color,
    value_size=14,
    detail_text="",
    detail_color=MUTED_TEXT_COLOR,
):
    pygame.draw.circle(surface, fill_color, (rect.left + 6, rect.centery - 4), 4)
    draw_text(surface, label.title(), (rect.left + 18, rect.top), size=value_size, color=TEXT_COLOR)
    value_surface = get_font(value_size, bold=True, face="body").render(amount_text, True, TEXT_COLOR)
    surface.blit(value_surface, (rect.right - value_surface.get_width(), rect.top))
    detail_width = 0
    if detail_text:
        detail_surface = get_font(max(11, value_size - 2), bold=True, face="body").render(detail_text, True, detail_color)
        detail_pos = (rect.right - detail_surface.get_width(), rect.bottom - detail_surface.get_height())
        surface.blit(detail_surface, detail_pos)
        detail_width = detail_surface.get_width() + 10

    bar_rect = pygame.Rect(rect.left + 18, rect.bottom - 8, max(42, rect.width - 18 - detail_width), 7)
    draw_progress_bar(surface, bar_rect, fraction, fill_color)


def draw_flow_row(surface, rect, label, amount_text, amount_color, value_size=14):
    draw_text(surface, amount_text, (rect.left, rect.top), size=value_size, color=amount_color, bold=True)
    draw_text(surface, label.title(), (rect.left + 54, rect.top), size=value_size, color=TEXT_COLOR)


def draw_status_pill(surface, rect, label, font_size=15):
    radius = max(12, rect.height // 2)
    draw_gradient_rect(surface, rect, _shift_color(STATUS_BG_COLOR, 8), _shift_color(STATUS_BG_COLOR, -6), radius)
    pygame.draw.rect(surface, PANEL_ACCENT_SOFT_COLOR, rect, 1, border_radius=radius)
    text_surface = get_font(font_size, bold=True, face="body").render(label, True, BUTTON_TEXT_LIGHT)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)


def draw_gradient_rect(surface, rect, top_color, bottom_color, radius):
    gradient = _get_gradient_surface((rect.width, rect.height), top_color, bottom_color)
    clipped = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(clipped, (255, 255, 255, 255), clipped.get_rect(), border_radius=radius)
    gradient.blit(clipped, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surface.blit(gradient, rect)


def draw_soft_shadow(surface, rect, color, offset=(0, 8), spread=16):
    base_color = _normalize_color(color)
    shadow_rect = rect.move(offset[0], offset[1])
    shadow_surface = pygame.Surface((shadow_rect.width + spread * 2, shadow_rect.height + spread * 2), pygame.SRCALPHA)

    for index, alpha in enumerate((44, 24, 12)):
        inflate = index * 10
        local_rect = pygame.Rect(spread - inflate // 2, spread - inflate // 2, shadow_rect.width + inflate, shadow_rect.height + inflate)
        radius = max(14, rect.height // 4 + index * 4)
        pygame.draw.rect(shadow_surface, (base_color[0], base_color[1], base_color[2], min(base_color[3], alpha)), local_rect, border_radius=radius)

    surface.blit(shadow_surface, (shadow_rect.left - spread, shadow_rect.top - spread))


def _draw_corner_ornaments(surface, rect, color, corner_size=12, inset=0):
    left = rect.left + inset
    right = rect.right - inset
    top = rect.top + inset
    bottom = rect.bottom - inset

    for x_dir, y_dir in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        base_x = left if x_dir == 1 else right
        base_y = top if y_dir == 1 else bottom
        pygame.draw.line(surface, color, (base_x, base_y + y_dir * corner_size), (base_x, base_y + y_dir * (corner_size // 2)), 1)
        pygame.draw.line(surface, color, (base_x + x_dir * corner_size, base_y), (base_x + x_dir * (corner_size // 2), base_y), 1)
        pygame.draw.line(surface, color, (base_x + x_dir * (corner_size // 2), base_y), (base_x, base_y + y_dir * (corner_size // 2)), 1)


def _get_gradient_surface(size, top_color, bottom_color):
    key = (size, _normalize_color(top_color), _normalize_color(bottom_color))
    if key in _GRADIENT_CACHE:
        return _GRADIENT_CACHE[key].copy()

    width, height = size
    gradient = pygame.Surface(size, pygame.SRCALPHA)
    top_rgba = _normalize_color(top_color)
    bottom_rgba = _normalize_color(bottom_color)

    if height <= 1:
        gradient.fill(top_rgba)
    else:
        for y in range(height):
            ratio = y / (height - 1)
            color = tuple(int(top_rgba[index] + (bottom_rgba[index] - top_rgba[index]) * ratio) for index in range(4))
            pygame.draw.line(gradient, color, (0, y), (width, y))

    _GRADIENT_CACHE[key] = gradient.copy()
    return gradient


def _get_fitted_font(text, preferred_size, max_width, bold=False, face="body"):
    if max_width <= 0:
        return get_font(max(10, preferred_size - 2), bold=bold, face=face)

    for size in range(preferred_size, 9, -1):
        font = get_font(size, bold=bold, face=face)
        if font.size(text)[0] <= max_width:
            return font

    return get_font(10, bold=bold, face=face)


def _get_font_path(face, bold):
    if face == "header":
        return _HEADER_FONT_PATH
    if bold:
        return _BODY_BOLD_FONT_PATH
    return _BODY_FONT_PATH


def _get_button_palette(variant, hovered, enabled, selected):
    palettes = {
        "default": (BUTTON_COLOR, _shift_color(BUTTON_COLOR, -26), PANEL_BORDER_COLOR, BUTTON_TEXT_LIGHT),
        "primary": (BUTTON_COLOR, _shift_color(BUTTON_COLOR, -26), PANEL_BORDER_COLOR, BUTTON_TEXT_LIGHT),
        "secondary": (INFO_COLOR, _shift_color(INFO_COLOR, -30), _shift_color(INFO_COLOR, 16), BUTTON_TEXT_LIGHT),
        "positive": (POSITIVE_COLOR, _shift_color(POSITIVE_COLOR, -30), _shift_color(POSITIVE_COLOR, 12), BUTTON_TEXT_LIGHT),
        "danger": (DANGER_COLOR, _shift_color(DANGER_COLOR, -30), _shift_color(DANGER_COLOR, 10), BUTTON_TEXT_LIGHT),
        "arcane": (BUTTON_ACTIVE_COLOR, _shift_color(BUTTON_ACTIVE_COLOR, -28), _shift_color(BUTTON_ACTIVE_COLOR, 14), BUTTON_TEXT_LIGHT),
        "warning": (WARNING_COLOR, _shift_color(WARNING_COLOR, -28), _shift_color(WARNING_COLOR, 10), BUTTON_TEXT_LIGHT),
    }
    top_color, bottom_color, border_color, text_color = palettes.get(variant, palettes["default"])

    if not enabled:
        return BUTTON_DISABLED_COLOR, _shift_color(BUTTON_DISABLED_COLOR, -8), MUTED_TEXT_COLOR, MUTED_TEXT_COLOR

    if selected:
        active_color = BUTTON_ACTIVE_HOVER_COLOR if hovered else BUTTON_ACTIVE_COLOR
        return _shift_color(active_color, 10), _shift_color(active_color, -12), _shift_color(active_color, 20), BUTTON_TEXT_LIGHT

    if hovered:
        top_color = _shift_color(top_color, 18)
        bottom_color = _shift_color(bottom_color, 10)
        border_color = _shift_color(border_color, 22)

    return top_color, bottom_color, border_color, text_color


def _normalize_color(color):
    if len(color) == 4:
        return color
    return color[0], color[1], color[2], 255


def _shift_color(color, amount):
    rgba = _normalize_color(color)
    shifted = tuple(max(0, min(255, channel + amount)) for channel in rgba[:3])
    return shifted if len(color) == 3 else (*shifted, rgba[3])
