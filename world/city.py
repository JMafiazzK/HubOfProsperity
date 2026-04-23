from config import RESOURCES
from world.city_types import CITY_TYPES


class City:
    def __init__(self, city_type, name):
        self.level = 1
        self.efficiency = 1.0
        self.prosperity = 50.0
        self.growth = 0.0
        self.money = 0.0
        self.tariff_rate = 0.15
        self.lifetime_trade_revenue = 0.0
        self.lifetime_trade_cost = 0.0
        self.resources = {res: 0.0 for res in RESOURCES}
        self.city_type = None
        self.name = ""
        self.last_turn_notes = []
        self.rename(name)
        self._set_city_type(city_type, reset_resources=True)
        self.reset_window_metrics()

    def rename(self, name):
        self.name = name

    def respecialize(self, city_type):
        self._set_city_type(city_type, reset_resources=False)

    def _set_city_type(self, city_type, reset_resources):
        if city_type not in CITY_TYPES:
            raise ValueError(f"Unknown city type: {city_type}")

        self.city_type = city_type
        if reset_resources:
            self.resources = {res: 0.0 for res in RESOURCES}

        start = CITY_TYPES[city_type].get("start_resources", {})
        for res, amount in start.items():
            if reset_resources:
                self.resources[res] = float(amount)
            else:
                self.resources[res] = max(self.resources[res], float(amount))

        start_money = float(CITY_TYPES[city_type].get("start_money", 120))
        if reset_resources:
            self.money = start_money
        else:
            self.money = max(self.money, start_money * 0.65)

        if city_type == "hub":
            self.tariff_rate = 0.15

    @property
    def type_data(self):
        return CITY_TYPES[self.city_type]

    @property
    def label(self):
        return self.type_data["label"]

    @property
    def description(self):
        return self.type_data["description"]

    @property
    def color(self):
        return self.type_data["color"]

    @property
    def production(self):
        return self.type_data.get("production", {})

    @property
    def consumption(self):
        return self.type_data.get("consumption", {})

    def storage_capacity(self, resource):
        base_capacity = 180 if self.city_type == "hub" else 105
        storage_bonus = self.type_data.get("storage_bonus", {}).get(resource, 0)
        return float(base_capacity * self.level + storage_bonus)

    def total_storage_used(self):
        return sum(self.resources.values())

    def total_storage_capacity(self):
        return sum(self.storage_capacity(resource) for resource in RESOURCES)

    def growth_threshold(self):
        return 38 + self.level * 18

    def hub_upgrade_cost(self):
        return 140 + max(0, self.level - 1) * 120

    def resource_delta(self, resource):
        return (
            self.window_produced.get(resource, 0.0)
            + self.window_imports.get(resource, 0.0)
            - self.window_consumed.get(resource, 0.0)
            - self.window_exports.get(resource, 0.0)
            - self.window_waste.get(resource, 0.0)
        )

    def status_label(self):
        if self.city_type == "hub":
            if self.money >= self.hub_upgrade_cost():
                return "Ready"
            if sum(self.window_exports.values()) > 0 or sum(self.window_imports.values()) > 0:
                return "Trading"
            return "Command"
        if sum(self.window_shortages.values()) > 0 or self.efficiency < 0.6:
            return "Strained"
        if self.money < 20:
            return "Poor"
        if self.prosperity >= 75:
            return "Prosperous"
        if self.growth >= self.growth_threshold() * 0.6:
            return "Growing"
        return "Stable"

    def reset_window_metrics(self):
        self.window_produced = {resource: 0.0 for resource in RESOURCES}
        self.window_consumed = {resource: 0.0 for resource in RESOURCES}
        self.window_imports = {resource: 0.0 for resource in RESOURCES}
        self.window_exports = {resource: 0.0 for resource in RESOURCES}
        self.window_shortages = {resource: 0.0 for resource in RESOURCES}
        self.window_waste = {resource: 0.0 for resource in RESOURCES}
        self.window_supply = 1.0
        self.window_growth_delta = 0.0
        self.window_prosperity_delta = 0.0
        self.window_trade_revenue = 0.0
        self.window_trade_cost = 0.0
        self.window_trade_count = 0
        self.leveled_up = False

    def add_turn_note(self, note):
        if not note:
            return
        if not self.last_turn_notes or self.last_turn_notes[0] != note:
            self.last_turn_notes = [note]

    def summarize_turn(self):
        if self.leveled_up:
            return f"{self.name} reached level {self.level}."
        if self.last_turn_notes:
            return self.last_turn_notes[0]
        return f"{self.name} is holding steady."
