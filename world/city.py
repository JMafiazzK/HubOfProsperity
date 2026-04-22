from config import RESOURCES
from world.city_types import CITY_TYPES


class City:
    def __init__(self, city_type, name):
        self.city_type = city_type
        self.name = name
        self.level = 1
        self.efficiency = 1.0

        # Alle Ressourcen initialisieren
        self.resources = {res: 0 for res in RESOURCES}

        # Startwerte vom Typ laden
        start = CITY_TYPES[city_type].get("start_resources", {})
        for res, amount in start.items():
            self.resources[res] = amount