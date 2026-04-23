from systems.economy import summarize_economy_window, update_economy
from world.city import City
from world.city_types import CITY_TYPES


class GameState:
    def __init__(self):
        self.city_positions = {(0, 0): City(city_type="hub", name="Home")}
        self.selected_hex = None
        self.name_input = ""
        self.name_input_active = False
        self.status_message = ""
        self.economy_message = "Found a satellite city to start autonomous trade."
        self.last_economy_result = self._empty_economy_report()
        self.simulation_time = 0.0
        self.simulation_running = True
        self.simulation_speed = 1.0
        self._step_duration = 0.25
        self._report_duration = 1.0
        self._step_accumulator = 0.0
        self._report_accumulator = 0.0
        self._report_buffer = self._empty_economy_report()

    def get_city(self, hex_coords):
        if hex_coords is None:
            return None
        return self.city_positions.get(hex_coords)

    def get_selected_city(self):
        return self.get_city(self.selected_hex)

    def get_hub_city(self):
        for city in self.city_positions.values():
            if city.city_type == "hub":
                return city
        return None

    def select_hex(self, hex_coords):
        self.selected_hex = hex_coords
        self.name_input_active = False

        if hex_coords is None:
            self.name_input = ""
            self.status_message = ""
            return

        city = self.get_city(hex_coords)
        if city is None:
            self.name_input = self._default_city_name(hex_coords)
            self.status_message = "This hex has no city yet."
            return

        self.name_input = city.name
        self.status_message = f"{city.name} selected."

    def clear_selection(self):
        self.select_hex(None)

    def set_name_input(self, value):
        self.name_input = value[:24]

    def append_name_input(self, value):
        self.name_input = f"{self.name_input}{value}"[:24]

    def backspace_name_input(self):
        self.name_input = self.name_input[:-1]

    def create_city(self, city_type):
        if self.selected_hex is None or self.selected_hex in self.city_positions:
            return False

        city_name = self._clean_name(self.name_input, self.selected_hex)
        self.city_positions[self.selected_hex] = City(city_type=city_type, name=city_name)
        self.name_input = city_name
        city_label = CITY_TYPES[city_type]["label"]
        self.status_message = f"{city_name} founded as {city_label}."
        return True

    def rename_selected_city(self):
        city = self.get_selected_city()
        if city is None:
            return False

        city_name = self._clean_name(self.name_input, self.selected_hex)
        city.rename(city_name)
        self.name_input = city.name
        self.status_message = f"City renamed to {city.name}."
        return True

    def respecialize_selected_city(self, city_type):
        city = self.get_selected_city()
        if city is None or city.city_type == "hub" or city.city_type == city_type:
            return False

        city.respecialize(city_type)
        city_label = CITY_TYPES[city_type]["label"]
        self.status_message = f"{city.name} now specializes as {city_label}."
        return True

    def update(self, dt):
        if not self.simulation_running:
            return

        scaled_dt = dt * self.simulation_speed
        self.simulation_time += scaled_dt
        self._step_accumulator += scaled_dt
        self._report_accumulator += scaled_dt

        while self._step_accumulator >= self._step_duration:
            step_result = update_economy(self.city_positions, self._step_duration)
            self._merge_report(step_result)
            self._step_accumulator -= self._step_duration

        if self._report_accumulator >= self._report_duration:
            self.last_economy_result = summarize_economy_window(self.city_positions, self._report_buffer)
            self.economy_message = self.last_economy_result["summary"]

            selected_city = self.get_selected_city()
            if selected_city is not None:
                self.status_message = selected_city.summarize_turn()
            else:
                self.status_message = self.economy_message

            self._report_accumulator = 0.0
            self._report_buffer = self._empty_economy_report()
            for city in self.city_positions.values():
                city.reset_window_metrics()

    def toggle_simulation(self):
        self.simulation_running = not self.simulation_running
        self.status_message = "Simulation running." if self.simulation_running else "Simulation paused."
        return self.simulation_running

    def adjust_hub_tariff(self, delta):
        hub = self.get_hub_city()
        if hub is None:
            return False

        hub.tariff_rate = self._clamp(hub.tariff_rate + delta, -0.25, 1.0)
        self.status_message = f"Hub tariff set to {hub.tariff_rate:+.0%}."
        return True

    def upgrade_hub(self):
        hub = self.get_hub_city()
        if hub is None:
            return False

        cost = hub.hub_upgrade_cost()
        if hub.money < cost:
            self.status_message = f"The hub needs {cost:.0f}g to upgrade."
            return False

        hub.money -= cost
        hub.level += 1
        hub.prosperity = min(100.0, hub.prosperity + 6)
        hub.add_turn_note(f"Upgraded to level {hub.level}. Trade capacity improved.")
        self.status_message = f"The hub upgraded to level {hub.level}."
        return True

    def _merge_report(self, step_result):
        for key in ("trade_count", "shortage_count", "cash_blocked_count", "leveled_up_count"):
            self._report_buffer[key] += step_result.get(key, 0)

        for key in ("trade_volume", "hub_income"):
            self._report_buffer[key] += step_result.get(key, 0.0)

        self._report_buffer["active_city_count"] = step_result.get("active_city_count", self._report_buffer["active_city_count"])
        self._report_buffer["network_health"] = step_result.get("network_health", self._report_buffer["network_health"])

    @staticmethod
    def _empty_economy_report():
        return {
            "trade_count": 0,
            "trade_volume": 0.0,
            "shortage_count": 0,
            "cash_blocked_count": 0,
            "hub_income": 0.0,
            "leveled_up_count": 0,
            "network_health": 0,
            "active_city_count": 0,
        }

    @staticmethod
    def _clean_name(name, hex_coords):
        compact_name = " ".join(name.split()).strip()
        if compact_name:
            return compact_name[:24]
        return GameState._default_city_name(hex_coords)

    @staticmethod
    def _default_city_name(hex_coords):
        q, r = hex_coords
        return f"City {q:+d},{r:+d}"

    @staticmethod
    def _clamp(value, minimum, maximum):
        return max(minimum, min(value, maximum))
