from config import RESOURCES


SECONDS_PER_CYCLE = 12.0
BASE_RESOURCE_PRICES = {
    "wood": 2.2,
    "water": 1.7,
    "food": 2.0,
}


def get_level_modifier(city):
    return 1.0 + max(0, city.level - 1) * 0.35


def get_prosperity_modifier(city):
    return 0.75 + city.prosperity / 200


def get_production_rate(city, efficiency=1.0):
    scaled_output = {}
    level_modifier = get_level_modifier(city)
    prosperity_modifier = get_prosperity_modifier(city)
    for resource, amount in city.production.items():
        produced = max(0.0, amount * level_modifier * prosperity_modifier * efficiency / SECONDS_PER_CYCLE)
        if produced > 0:
            scaled_output[resource] = produced
    return scaled_output


def get_consumption_rate(city):
    scaled_demand = {}
    level_modifier = 1.0 + max(0, city.level - 1) * 0.28
    for resource, amount in city.consumption.items():
        if amount >= 0:
            continue
        scaled_demand[resource] = abs(amount) * level_modifier / SECONDS_PER_CYCLE
    return scaled_demand


def get_import_target(city, resource):
    demand_buffer = get_consumption_rate(city).get(resource, 0.0) * 12
    if resource in city.production:
        safety_buffer = max(6.0, city.storage_capacity(resource) * 0.12)
    else:
        safety_buffer = max(10.0, city.storage_capacity(resource) * 0.26)
    return min(city.storage_capacity(resource), max(demand_buffer, safety_buffer))


def get_export_reserve(city, resource):
    if city.city_type == "hub":
        return 0.0

    next_demand = get_consumption_rate(city).get(resource, 0.0) * 10
    producer_buffer = get_production_rate(city, 1.0).get(resource, 0.0) * 5
    safety_buffer = max(8.0, city.storage_capacity(resource) * 0.18)
    return min(city.storage_capacity(resource), max(next_demand, producer_buffer, safety_buffer))


def get_trade_capacity(city, hub, dt):
    return (4.0 + city.level * 0.8 + hub.level * 1.4) * dt


def get_resource_price(resource):
    return BASE_RESOURCE_PRICES.get(resource, 1.0)


def get_import_price(hub, resource):
    return get_resource_price(resource) * (1.0 + hub.tariff_rate)


def get_export_price(resource):
    return get_resource_price(resource)


def clamp_resources_to_capacity(city):
    for resource in RESOURCES:
        city.resources[resource] = min(city.resources[resource], city.storage_capacity(resource))
