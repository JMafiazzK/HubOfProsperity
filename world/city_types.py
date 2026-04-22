CITY_TYPES = {
    "wood": {
        "production": {"wood": 30},
        "consumption": {"water": -10, "food": -15},
        "start_resources": {"wood": 30}
    },
    "water": {
        "production": {"water": 25},
        "consumption": {"food": -10},
        "start_resources": {"water": 30}
    },
    "hub": {
        "production": {},
        "consumption": {},
        "start_resources": {"wood": 50, "water": 50, "food": 50}
    }
}