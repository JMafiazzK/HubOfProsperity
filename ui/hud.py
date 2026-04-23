import pygame

from config import (
    DANGER_COLOR,
    HEIGHT,
    INFO_COLOR,
    MAX_PANEL_WIDTH,
    MUTED_TEXT_COLOR,
    OUTLINE_COLOR,
    PANEL_WIDTH,
    POSITIVE_COLOR,
    RESOURCES,
    TEXT_COLOR,
    WARNING_COLOR,
    WIDTH,
)
from ui.controls import (
    draw_action_button,
    draw_badge,
    draw_card,
    draw_divider,
    draw_eye_emblem,
    draw_input,
    draw_meter_row,
    draw_panel,
    draw_resource_row,
    draw_section_title,
    draw_stat_row,
    draw_text,
)
from world.city_types import SPECIALIZABLE_CITY_TYPES


def get_city_panel_layout(game_state, screen_size):
    if game_state.selected_hex is None:
        return None

    metrics = _get_ui_metrics(screen_size)
    panel_rect = pygame.Rect(
        metrics["panel_margin"],
        metrics["panel_margin"],
        metrics["panel_width"],
        screen_size[1] - metrics["panel_margin"] * 2,
    )
    content_left = panel_rect.left + metrics["panel_padding"]
    content_width = panel_rect.width - metrics["panel_padding"] * 2

    close_rect = pygame.Rect(
        panel_rect.right - metrics["close_size"] - metrics["panel_padding"],
        panel_rect.top + metrics["panel_padding"] - 2,
        metrics["close_size"],
        metrics["close_size"],
    )
    header_rect = pygame.Rect(content_left, panel_rect.top + metrics["panel_padding"], content_width, metrics["header_height"])
    name_input_rect = pygame.Rect(content_left, header_rect.bottom + metrics["section_gap"], content_width, metrics["input_height"])

    layout = {
        "panel": panel_rect,
        "close": close_rect,
        "header": header_rect,
        "name_input": name_input_rect,
        "buttons": [],
        "metrics": metrics,
    }

    city = game_state.get_selected_city()
    content_y = name_input_rect.bottom + metrics["section_gap"]

    if city is None:
        empty_rect = pygame.Rect(content_left, content_y, content_width, metrics["empty_card_height"])
        buttons_top = empty_rect.bottom + metrics["section_gap"]
        layout["empty_rect"] = empty_rect
        layout["buttons"].extend(_build_type_buttons(content_left, buttons_top, content_width, "create", metrics))
        return layout

    overview_rect = pygame.Rect(content_left, content_y, content_width, metrics["overview_card_height"])
    resources_rect = pygame.Rect(content_left, overview_rect.bottom + metrics["section_gap"], content_width, metrics["resources_card_height"])
    rename_rect = pygame.Rect(content_left, resources_rect.bottom + metrics["section_gap"], content_width, metrics["button_height"])

    layout["overview_rect"] = overview_rect
    layout["resources_rect"] = resources_rect
    layout["buttons"].append(
        {
            "rect": rename_rect,
            "action": "rename",
            "value": None,
            "label": "Rename City",
            "enabled": True,
            "selected": False,
            "variant": "secondary",
        }
    )

    if city.city_type != "hub":
        buttons_top = rename_rect.bottom + metrics["button_gap"]
        layout["buttons"].extend(
            _build_type_buttons(
                content_left,
                buttons_top,
                content_width,
                "respecialize",
                metrics,
                current_type=city.city_type,
            )
        )

    return layout


def draw_city_panel(screen, game_state):
    layout = get_city_panel_layout(game_state, screen.get_size())
    if layout is None:
        return

    metrics = layout["metrics"]
    mouse_pos = pygame.mouse.get_pos()
    city = game_state.get_selected_city()
    q, r = game_state.selected_hex

    draw_panel(screen, layout["panel"])
    _draw_header(screen, layout, city, q, r, metrics, mouse_pos)

    draw_input(
        screen,
        layout["name_input"],
        game_state.name_input,
        active=game_state.name_input_active,
        placeholder="Enter a city name",
        font_size=metrics["input_font_size"],
    )

    if city is None:
        _draw_empty_state(screen, layout["empty_rect"], q, r, metrics)
    else:
        _draw_overview_card(screen, layout["overview_rect"], city, metrics)
        _draw_resources_card(screen, layout["resources_rect"], city, metrics)

    for button in layout["buttons"]:
        draw_action_button(
            screen,
            button["rect"],
            button["label"],
            variant=button["variant"],
            enabled=button["enabled"],
            selected=button["selected"],
            hovered=button["rect"].collidepoint(mouse_pos),
            font_size=metrics["button_font_size"],
        )


def draw_economy_panel(screen, game_state):
    layout = get_economy_panel_layout(screen.get_size())
    mouse_pos = pygame.mouse.get_pos()
    hub = game_state.get_hub_city()
    report = game_state.last_economy_result or {}
    running_color = POSITIVE_COLOR if game_state.simulation_running else WARNING_COLOR
    income = report.get("hub_income", 0.0)
    income_prefix = "+" if income >= 0 else ""
    upgrade_cost = hub.hub_upgrade_cost() if hub is not None else 0

    draw_card(screen, layout["panel"])
    draw_badge(screen, layout["state_badge"], "Running" if game_state.simulation_running else "Paused", running_color, font_size=layout["badge_font_size"])
    draw_badge(screen, layout["time_badge"], _format_time(game_state.simulation_time), INFO_COLOR, font_size=layout["badge_font_size"])

    if hub is not None:
        _draw_network_stat(screen, layout["money_stat"], "Gold", _format_money(hub.money), layout, accent=POSITIVE_COLOR if hub.money >= upgrade_cost else TEXT_COLOR)
        _draw_network_stat(screen, layout["tariff_stat"], "Tariff", f"{hub.tariff_rate:+.0%}", layout, accent=WARNING_COLOR)
        _draw_network_stat(screen, layout["hub_stat"], "Hub", f"L{hub.level}", layout, accent=INFO_COLOR)

        for index, resource in enumerate(RESOURCES):
            x = layout["panel"].left + 12 + index * layout["resource_column_width"]
            y = layout["resource_row_y"]
            color = _get_resource_color(resource)
            amount = hub.resources.get(resource, 0.0)
            pygame.draw.circle(screen, color, (x + 5, y + 6), 4)
            draw_text(screen, resource.title(), (x + 14, y), size=layout["tiny_size"], color=MUTED_TEXT_COLOR, bold=True)
            draw_text(screen, _format_number(amount), (x + 14, y + 13), size=layout["body_size"], color=TEXT_COLOR, bold=True)

    draw_divider(screen, layout["panel"].left + 12, layout["panel"].right - 12, layout["divider_y"])
    _draw_network_stat(screen, layout["stat_columns"][0], "Deals", str(report.get("trade_count", 0)), layout)
    _draw_network_stat(screen, layout["stat_columns"][1], "Net", f"{income_prefix}{income:.0f}g", layout)
    _draw_network_stat(screen, layout["stat_columns"][2], "Short", str(report.get("shortage_count", 0)), layout)

    draw_action_button(
        screen,
        layout["tariff_down_button"],
        "- Tariff",
        variant="warning",
        hovered=layout["tariff_down_button"].collidepoint(mouse_pos),
        font_size=layout["button_font_size"],
    )
    draw_action_button(
        screen,
        layout["tariff_up_button"],
        "+ Tariff",
        variant="secondary",
        hovered=layout["tariff_up_button"].collidepoint(mouse_pos),
        font_size=layout["button_font_size"],
    )
    draw_action_button(
        screen,
        layout["upgrade_button"],
        "Upgrade",
        variant="primary",
        enabled=hub is not None and hub.money >= upgrade_cost,
        hovered=layout["upgrade_button"].collidepoint(mouse_pos),
        font_size=layout["button_font_size"],
    )


def handle_city_panel_click(mouse_pos, game_state, screen_size):
    layout = get_city_panel_layout(game_state, screen_size)
    if layout is None:
        return False

    if not layout["panel"].collidepoint(mouse_pos):
        game_state.name_input_active = False
        return False

    if layout["close"].collidepoint(mouse_pos):
        game_state.clear_selection()
        return True

    if layout["name_input"].collidepoint(mouse_pos):
        game_state.name_input_active = True
        return True

    game_state.name_input_active = False

    for button in layout["buttons"]:
        if button["rect"].collidepoint(mouse_pos):
            if not button["enabled"]:
                return True

            if button["action"] == "create":
                game_state.create_city(button["value"])
            elif button["action"] == "rename":
                game_state.rename_selected_city()
            elif button["action"] == "respecialize":
                game_state.respecialize_selected_city(button["value"])
            return True

    return True


def handle_economy_panel_click(mouse_pos, game_state, screen_size):
    layout = get_economy_panel_layout(screen_size)
    if not layout["panel"].collidepoint(mouse_pos):
        return False

    if layout["tariff_down_button"].collidepoint(mouse_pos):
        game_state.adjust_hub_tariff(-0.05)
        return True

    if layout["tariff_up_button"].collidepoint(mouse_pos):
        game_state.adjust_hub_tariff(0.05)
        return True

    if layout["upgrade_button"].collidepoint(mouse_pos):
        game_state.upgrade_hub()
        return True

    return True


def handle_city_panel_keydown(event, game_state):
    if not game_state.name_input_active or game_state.selected_hex is None:
        return False

    if event.key == pygame.K_BACKSPACE:
        game_state.backspace_name_input()
        return True

    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
        if game_state.get_selected_city() is not None:
            game_state.rename_selected_city()
            return True
        return False

    if event.key == pygame.K_ESCAPE:
        game_state.name_input_active = False
        return True

    if event.unicode and event.unicode.isprintable() and event.unicode not in "\r\t":
        game_state.append_name_input(event.unicode)
        return True

    return False


def _draw_header(screen, layout, city, q, r, metrics, mouse_pos):
    header_rect = layout["header"]
    emblem_center = (header_rect.left + metrics["icon_size"] // 2, header_rect.top + metrics["icon_size"] // 2 + 2)
    emblem_color = city.color if city is not None else WARNING_COLOR
    draw_eye_emblem(screen, emblem_center, metrics["icon_size"] // 2, accent_color=emblem_color)

    title_x = header_rect.left + metrics["icon_size"] + 16
    title = city.name if city is not None else "Open Tile"
    subtitle = city.label if city is not None else "Found a new settlement"
    draw_text(screen, title, (title_x, header_rect.top + 2), size=metrics["city_name_size"], color=TEXT_COLOR, bold=True, face="header")
    draw_text(screen, subtitle, (title_x, header_rect.top + metrics["subtitle_offset"]), size=metrics["subtitle_size"], color=metrics["type_color"], bold=True)
    draw_text(screen, f"({q}, {r})", (title_x, header_rect.top + metrics["position_offset"]), size=metrics["body_size"], color=MUTED_TEXT_COLOR)

    badge_rect = pygame.Rect(
        header_rect.right - metrics["badge_width"],
        header_rect.top + metrics["badge_top"],
        metrics["badge_width"],
        metrics["badge_height"],
    )
    if city is None:
        badge_label = "Frontier"
        badge_color = WARNING_COLOR
    else:
        badge_label = city.status_label()
        badge_color = _get_health_color(city.prosperity, city.city_type == "hub")
    draw_badge(screen, badge_rect, badge_label, badge_color, font_size=metrics["badge_font_size"])

    draw_divider(screen, header_rect.left, header_rect.right, header_rect.bottom - 6)
    close_color = metrics["close_hover_color"] if layout["close"].collidepoint(mouse_pos) else OUTLINE_COLOR
    draw_text(screen, "X", (layout["close"].left + 4, layout["close"].top - 1), size=metrics["close_font_size"], color=close_color, bold=True)


def _draw_empty_state(screen, rect, q, r, metrics):
    draw_card(screen, rect)
    draw_section_title(screen, "Unclaimed", (rect.left + 12, rect.top + 12), size=metrics["section_title_size"])
    draw_text(screen, f"({q}, {r})", (rect.left + 12, rect.top + 42), size=metrics["body_size"], color=MUTED_TEXT_COLOR)
    draw_text(screen, "Choose a role below", (rect.left + 12, rect.top + 66), size=metrics["body_size"], color=TEXT_COLOR, bold=True)


def _draw_overview_card(screen, rect, city, metrics):
    draw_card(screen, rect)

    if city.city_type == "hub":
        _draw_hub_overview(screen, rect, city, metrics)
        return

    draw_stat_row(
        screen,
        (rect.left + 12, rect.top + 34),
        (rect.right - 98, rect.top + 32),
        "Level",
        str(city.level),
        label_size=metrics["label_size"],
        value_size=metrics["body_size"],
    )
    draw_stat_row(
        screen,
        (rect.left + rect.width // 2 - 6, rect.top + 34),
        (rect.right - 74, rect.top + 32),
        "Cash",
        _format_money(city.money),
        label_size=metrics["label_size"],
        value_size=metrics["label_size"],
        value_color=POSITIVE_COLOR if city.money >= 30 else WARNING_COLOR,
    )

    prosperity_row = pygame.Rect(rect.left + 12, rect.top + 54, rect.width - 24, 24)
    draw_meter_row(
        screen,
        prosperity_row,
        "Prosperity",
        f"{city.prosperity:.0f}%",
        city.prosperity / 100,
        _get_health_color(city.prosperity, False),
        label_size=metrics["label_size"],
        value_size=metrics["body_size"],
    )

    efficiency_row = pygame.Rect(rect.left + 12, rect.top + 78, rect.width - 24, 24)
    draw_meter_row(
        screen,
        efficiency_row,
        "Efficiency",
        f"{int(city.efficiency * 100)}%",
        city.efficiency,
        INFO_COLOR,
        label_size=metrics["label_size"],
        value_size=metrics["body_size"],
    )

    growth_row = pygame.Rect(rect.left + 12, rect.top + 102, rect.width - 24, 24)
    draw_meter_row(
        screen,
        growth_row,
        "Growth",
        f"{city.growth:.0f}/{city.growth_threshold():.0f}",
        city.growth / city.growth_threshold(),
        POSITIVE_COLOR,
        label_size=metrics["label_size"],
        value_size=metrics["body_size"],
    )


def _draw_hub_overview(screen, rect, city, metrics):
    draw_stat_row(
        screen,
        (rect.left + 12, rect.top + 34),
        (rect.right - 118, rect.top + 32),
        "Level",
        str(city.level),
        label_size=metrics["label_size"],
        value_size=metrics["body_size"],
    )
    draw_stat_row(
        screen,
        (rect.left + rect.width // 2 - 6, rect.top + 34),
        (rect.right - 72, rect.top + 32),
        "Cash",
        _format_money(city.money),
        label_size=metrics["label_size"],
        value_size=metrics["label_size"],
        value_color=POSITIVE_COLOR if city.money >= city.hub_upgrade_cost() else WARNING_COLOR,
    )

    tariff_fraction = (city.tariff_rate + 0.25) / 1.25
    tariff_row = pygame.Rect(rect.left + 12, rect.top + 54, rect.width - 24, 24)
    draw_meter_row(
        screen,
        tariff_row,
        "Tariff",
        f"{city.tariff_rate:+.0%}",
        max(0.0, min(1.0, tariff_fraction)),
        WARNING_COLOR,
        label_size=metrics["label_size"],
        value_size=metrics["body_size"],
    )

    storage_row = pygame.Rect(rect.left + 12, rect.top + 78, rect.width - 24, 24)
    draw_meter_row(
        screen,
        storage_row,
        "Storage",
        f"{_format_number(city.total_storage_used())}/{_format_number(city.total_storage_capacity())}",
        city.total_storage_used() / city.total_storage_capacity(),
        INFO_COLOR,
        label_size=metrics["label_size"],
        value_size=metrics["body_size"],
    )

    upgrade_cost = city.hub_upgrade_cost()
    upgrade_row = pygame.Rect(rect.left + 12, rect.top + 102, rect.width - 24, 24)
    draw_meter_row(
        screen,
        upgrade_row,
        "Upgrade",
        f"{upgrade_cost:.0f}g",
        min(1.0, city.money / upgrade_cost if upgrade_cost > 0 else 1.0),
        POSITIVE_COLOR if city.money >= upgrade_cost else WARNING_COLOR,
        label_size=metrics["label_size"],
        value_size=metrics["body_size"],
    )


def _draw_resources_card(screen, rect, city, metrics):
    draw_card(screen, rect)
    draw_text(
        screen,
        f"{_format_number(city.total_storage_used())}/{_format_number(city.total_storage_capacity())}",
        (rect.left + 12, rect.top + 10),
        size=metrics["tiny_size"],
        color=MUTED_TEXT_COLOR,
        bold=True,
    )

    row_top = rect.top + 34
    for index, resource in enumerate(RESOURCES):
        amount = city.resources.get(resource, 0.0)
        cap = city.storage_capacity(resource)
        delta = city.resource_delta(resource)
        row_rect = pygame.Rect(rect.left + 12, row_top + index * metrics["resource_row_step"], rect.width - 24, metrics["resource_row_height"])
        draw_resource_row(
            screen,
            row_rect,
            resource,
            f"{_format_number(amount)}/{_format_number(cap)}",
            amount / cap if cap else 0,
            _get_resource_color(resource),
            value_size=metrics["body_size"],
            detail_text=f"net {delta:+.1f}",
            detail_color=_get_net_color(delta),
        )


def _build_type_buttons(left, top, width, action, metrics, current_type=None):
    gap = metrics["button_gap"]
    button_width = (width - gap * 2) // 3
    buttons = []

    for index, city_type in enumerate(SPECIALIZABLE_CITY_TYPES):
        rect = pygame.Rect(left + index * (button_width + gap), top, button_width, metrics["button_height"])
        buttons.append(
            {
                "rect": rect,
                "action": action,
                "value": city_type,
                "label": city_type.title(),
                "enabled": current_type != city_type,
                "selected": current_type == city_type,
                "variant": _get_type_button_variant(city_type),
            }
        )

    return buttons


def _draw_network_stat(screen, rect, label, value, layout, accent=TEXT_COLOR):
    draw_text(screen, label.upper(), (rect.left, rect.top), size=layout["tiny_size"], color=MUTED_TEXT_COLOR, bold=True)
    draw_text(screen, value, (rect.left, rect.top + 12), size=layout["body_size"], color=accent, bold=True, face="header")


def _format_time(seconds):
    minutes = int(seconds // 60)
    remainder = int(seconds % 60)
    return f"{minutes:02d}:{remainder:02d}"


def _format_money(amount):
    return f"{amount:.0f}g"


def _format_number(amount):
    return f"{amount:.0f}"


def _get_resource_color(resource):
    return {
        "wood": WARNING_COLOR,
        "water": INFO_COLOR,
        "food": POSITIVE_COLOR,
    }.get(resource, WARNING_COLOR)


def _get_net_color(amount):
    if amount > 0:
        return POSITIVE_COLOR
    if amount < 0:
        return DANGER_COLOR
    return MUTED_TEXT_COLOR


def _get_health_color(value, is_hub):
    if is_hub:
        if value >= 65:
            return POSITIVE_COLOR
        if value >= 40:
            return WARNING_COLOR
        return INFO_COLOR
    if value >= 75:
        return POSITIVE_COLOR
    if value >= 45:
        return WARNING_COLOR
    return DANGER_COLOR


def _get_type_button_variant(city_type):
    return {
        "wood": "warning",
        "water": "secondary",
        "food": "positive",
    }.get(city_type, "default")


def get_economy_panel_layout(screen_size):
    scale = _get_scale(screen_size)
    panel_width = _clamp(int(292 * scale), 280, 360)
    panel_height = _clamp(int(176 * scale), 176, 214)
    margin = _clamp(int(14 * scale), 14, 22)
    panel_rect = pygame.Rect(screen_size[0] - panel_width - margin, margin, panel_width, panel_height)
    button_gap = 8
    bottom_width = panel_rect.width - 24
    upgrade_width = int(bottom_width * 0.34)
    small_width = (bottom_width - upgrade_width - button_gap * 2) // 2
    stat_width = (panel_rect.width - 24) // 3
    stats_top = panel_rect.top + 98

    return {
        "panel": panel_rect,
        "state_badge": pygame.Rect(panel_rect.right - 102, panel_rect.top + 10, 90, 22),
        "time_badge": pygame.Rect(panel_rect.right - 102, panel_rect.top + 38, 90, 22),
        "money_stat": pygame.Rect(panel_rect.left + 12, panel_rect.top + 10, 96, 28),
        "tariff_stat": pygame.Rect(panel_rect.left + 12, panel_rect.top + 40, 96, 28),
        "hub_stat": pygame.Rect(panel_rect.left + 116, panel_rect.top + 40, 54, 28),
        "resource_row_y": panel_rect.top + 68,
        "divider_y": panel_rect.top + 90,
        "stat_columns": [
            pygame.Rect(panel_rect.left + 12 + index * stat_width, stats_top, stat_width - 8, 28)
            for index in range(3)
        ],
        "tariff_down_button": pygame.Rect(panel_rect.left + 12, panel_rect.bottom - 34, small_width, 24),
        "tariff_up_button": pygame.Rect(panel_rect.left + 12 + small_width + button_gap, panel_rect.bottom - 34, small_width, 24),
        "upgrade_button": pygame.Rect(panel_rect.right - 12 - upgrade_width, panel_rect.bottom - 34, upgrade_width, 24),
        "resource_column_width": (panel_rect.width - 36) // 3,
        "title_size": _clamp(int(17 * scale), 17, 22),
        "badge_font_size": _clamp(int(10 * scale), 10, 14),
        "body_size": _clamp(int(13 * scale), 13, 17),
        "tiny_size": _clamp(int(10 * scale), 10, 13),
        "button_font_size": _clamp(int(11 * scale), 11, 15),
    }


def _get_ui_metrics(screen_size):
    scale = _get_scale(screen_size)
    screen_width, _ = screen_size
    panel_margin = _clamp(int(12 * scale), 12, 20)
    panel_padding = _clamp(int(18 * scale), 18, 28)
    panel_width = _clamp(int(screen_width * 0.31), PANEL_WIDTH, MAX_PANEL_WIDTH)

    return {
        "panel_margin": panel_margin,
        "panel_padding": panel_padding,
        "panel_width": panel_width,
        "header_height": _clamp(int(70 * scale), 70, 96),
        "input_height": _clamp(int(36 * scale), 36, 48),
        "section_gap": _clamp(int(10 * scale), 10, 16),
        "icon_size": _clamp(int(54 * scale), 54, 72),
        "close_size": _clamp(int(24 * scale), 24, 32),
        "close_font_size": _clamp(int(20 * scale), 20, 28),
        "city_name_size": _clamp(int(24 * scale), 24, 32),
        "subtitle_size": _clamp(int(16 * scale), 16, 20),
        "body_size": _clamp(int(13 * scale), 13, 17),
        "label_size": _clamp(int(12 * scale), 12, 16),
        "tiny_size": _clamp(int(10 * scale), 10, 13),
        "input_font_size": _clamp(int(18 * scale), 18, 24),
        "button_font_size": _clamp(int(13 * scale), 13, 18),
        "section_title_size": _clamp(int(15 * scale), 15, 20),
        "badge_width": _clamp(int(102 * scale), 102, 132),
        "badge_height": _clamp(int(26 * scale), 26, 36),
        "badge_top": _clamp(int(8 * scale), 8, 14),
        "badge_font_size": _clamp(int(11 * scale), 11, 15),
        "subtitle_offset": _clamp(int(28 * scale), 28, 40),
        "position_offset": _clamp(int(48 * scale), 48, 64),
        "type_color": (214, 164, 91),
        "overview_card_height": _clamp(int(126 * scale), 126, 164),
        "resources_card_height": _clamp(int(110 * scale), 110, 146),
        "empty_card_height": _clamp(int(110 * scale), 110, 148),
        "resource_row_height": _clamp(int(24 * scale), 24, 32),
        "resource_row_step": _clamp(int(24 * scale), 24, 32),
        "button_height": _clamp(int(32 * scale), 32, 42),
        "button_gap": _clamp(int(8 * scale), 8, 12),
        "close_hover_color": (222, 164, 91),
    }


def _get_scale(screen_size):
    screen_width, screen_height = screen_size
    return _clamp(min(screen_width / WIDTH, screen_height / HEIGHT), 1.0, 1.45)


def _clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))
