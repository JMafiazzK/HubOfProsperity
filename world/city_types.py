CITY_TYPES = {
    "wood": {
        "label": "Lumber City",
        "description": "Turns nearby forests into construction material.",
        "color": (156, 116, 80),
        "production": {"wood": 30},
        "consumption": {"water": -10, "food": -15},
        "start_resources": {"wood": 30},
        "start_money": 120,
        "storage_bonus": {"wood": 50},
    },
    "water": {
        "label": "Waterworks",
        "description": "Harvests and stores clean water for the network.",
        "color": (85, 140, 186),
        "production": {"water": 25},
        "consumption": {"food": -10},
        "start_resources": {"water": 30},
        "start_money": 110,
        "storage_bonus": {"water": 50},
    },
    "food": {
        "label": "Farming Town",
        "description": "Feeds the region with steady food production.",
        "color": (205, 178, 90),
        "production": {"food": 25},
        "consumption": {"water": -10},
        "start_resources": {"food": 30},
        "start_money": 110,
        "storage_bonus": {"food": 50},
    },
    "hub": {
        "label": "Central Hub",
        "description": "The fixed heart of the trade network.",
        "color": (120, 180, 120),
        "production": {},
        "consumption": {},
        "start_resources": {"wood": 50, "water": 50, "food": 50},
        "start_money": 100,
        "storage_bonus": {"wood": 100, "water": 100, "food": 100},
    }
}

SPECIALIZABLE_CITY_TYPES = [city_type for city_type in CITY_TYPES if city_type != "hub"]
