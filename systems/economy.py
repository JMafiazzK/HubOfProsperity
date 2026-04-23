from config import RESOURCES
from systems.production import (
    clamp_resources_to_capacity,
    get_consumption_rate,
    get_export_price,
    get_export_reserve,
    get_import_price,
    get_import_target,
    get_production_rate,
    get_trade_capacity,
)


def update_economy(city_positions, dt):
    ordered_entries = sorted(city_positions.items(), key=lambda item: (item[0][0], item[0][1]))
    hub = next((city for _, city in ordered_entries if city.city_type == "hub"), None)
    active_cities = [city for _, city in ordered_entries if city.city_type != "hub"]
    report = {
        "trade_count": 0,
        "trade_volume": 0.0,
        "shortage_count": 0,
        "cash_blocked_count": 0,
        "hub_income": 0.0,
        "leveled_up_count": 0,
        "active_city_count": len(active_cities),
        "network_health": round(sum(city.prosperity for city in active_cities) / len(active_cities)) if active_cities else 0,
    }

    if hub is None:
        return report

    hub.efficiency = 1.0

    for city in active_cities:
        _produce_resources(city, dt)

    for city in active_cities:
        report["cash_blocked_count"] += _import_from_hub(city, hub, dt, report)

    for city in active_cities:
        shortage_total = _consume_resources(city, dt, report)
        export_value = _export_surplus_to_hub(city, hub, dt, report)
        report["leveled_up_count"] += _update_city_state(city, shortage_total, export_value, dt)
        clamp_resources_to_capacity(city)

    clamp_resources_to_capacity(hub)
    _update_hub_note(hub, report)
    report["network_health"] = round(sum(city.prosperity for city in active_cities) / len(active_cities)) if active_cities else 0
    return report


def summarize_economy_window(city_positions, report):
    hub = next((city for city in city_positions.values() if city.city_type == "hub"), None)
    tariff_rate = hub.tariff_rate if hub is not None else 0.0
    hub_money = hub.money if hub is not None else 0.0
    summary = _build_live_summary(report, tariff_rate)

    return {
        "summary": summary,
        "trade_count": report.get("trade_count", 0),
        "trade_volume": report.get("trade_volume", 0.0),
        "shortage_count": report.get("shortage_count", 0),
        "cash_blocked_count": report.get("cash_blocked_count", 0),
        "hub_income": report.get("hub_income", 0.0),
        "leveled_up_count": report.get("leveled_up_count", 0),
        "network_health": report.get("network_health", 0),
        "active_city_count": report.get("active_city_count", 0),
        "hub_money": hub_money,
        "tariff_rate": tariff_rate,
    }


def _produce_resources(city, dt):
    for resource, rate in get_production_rate(city, city.efficiency).items():
        amount = rate * dt
        free_capacity = max(0.0, city.storage_capacity(resource) - city.resources[resource])
        stored_amount = min(amount, free_capacity)
        if stored_amount > 0:
            city.resources[resource] += stored_amount
            city.window_produced[resource] += stored_amount
        if stored_amount < amount:
            city.window_waste[resource] += amount - stored_amount


def _import_from_hub(city, hub, dt, report):
    cash_blocked = 0
    trade_capacity = get_trade_capacity(city, hub, dt)

    for resource in RESOURCES:
        target_stock = get_import_target(city, resource)
        reorder_level = target_stock * 0.58
        if city.resources[resource] >= reorder_level or trade_capacity <= 0:
            continue

        desired_amount = target_stock - city.resources[resource]
        purchasable_amount = min(desired_amount, hub.resources[resource], trade_capacity)
        if purchasable_amount <= 0:
            continue

        unit_price = get_import_price(hub, resource)
        affordable_amount = city.money / unit_price if unit_price > 0 else purchasable_amount
        traded_amount = min(purchasable_amount, affordable_amount)

        if traded_amount > 0.01:
            cost = traded_amount * unit_price
            city.resources[resource] += traded_amount
            hub.resources[resource] -= traded_amount
            city.money -= cost
            hub.money += cost
            city.lifetime_trade_cost += cost
            hub.lifetime_trade_revenue += cost
            city.window_imports[resource] += traded_amount
            hub.window_exports[resource] += traded_amount
            city.window_trade_cost += cost
            hub.window_trade_revenue += cost
            city.window_trade_count += 1
            hub.window_trade_count += 1
            report["trade_count"] += 1
            report["trade_volume"] += traded_amount
            report["hub_income"] += cost
            trade_capacity = max(0.0, trade_capacity - traded_amount)
            city.add_turn_note(f"Bought {traded_amount:.1f} {resource} from {hub.name} for {cost:.0f}g.")
        else:
            cash_blocked += 1

    return cash_blocked


def _consume_resources(city, dt, report):
    total_demand = 0.0
    supplied_total = 0.0
    shortage_total = 0.0

    for resource, rate in get_consumption_rate(city).items():
        demand = rate * dt
        total_demand += demand
        local_used = min(city.resources[resource], demand)
        city.resources[resource] -= local_used
        city.window_consumed[resource] += local_used
        supplied_total += local_used

        shortage = demand - local_used
        if shortage > 0.001:
            city.window_shortages[resource] += shortage
            shortage_total += shortage
            report["shortage_count"] += 1

    city.window_supply = _safe_ratio(supplied_total, total_demand)

    if shortage_total > 0.001:
        city.add_turn_note(f"Short on supplies. Efficiency dropped to {int(city.efficiency * 100)}%.")

    return shortage_total


def _export_surplus_to_hub(city, hub, dt, report):
    trade_capacity = get_trade_capacity(city, hub, dt)
    export_value = 0.0

    for resource in RESOURCES:
        reserve = get_export_reserve(city, resource)
        surplus = max(0.0, city.resources[resource] - reserve)
        if surplus <= 0 or trade_capacity <= 0:
            continue

        hub_space = max(0.0, hub.storage_capacity(resource) - hub.resources[resource])
        unit_price = get_export_price(resource)
        if unit_price <= 0:
            continue

        hub_affordable = hub.money / unit_price
        traded_amount = min(surplus, hub_space, trade_capacity, hub_affordable)
        if traded_amount <= 0.01:
            continue

        payment = traded_amount * unit_price
        city.resources[resource] -= traded_amount
        hub.resources[resource] += traded_amount
        city.money += payment
        hub.money -= payment
        city.lifetime_trade_revenue += payment
        hub.lifetime_trade_cost += payment
        city.window_exports[resource] += traded_amount
        hub.window_imports[resource] += traded_amount
        city.window_trade_revenue += payment
        hub.window_trade_cost += payment
        city.window_trade_count += 1
        hub.window_trade_count += 1
        report["trade_count"] += 1
        report["trade_volume"] += traded_amount
        report["hub_income"] -= payment
        trade_capacity = max(0.0, trade_capacity - traded_amount)
        export_value += payment
        city.add_turn_note(f"Sold {traded_amount:.1f} {resource} to {hub.name} for {payment:.0f}g.")

    return export_value


def _update_city_state(city, shortage_total, export_value, dt):
    storage_ratio = _safe_ratio(city.total_storage_used(), city.total_storage_capacity())
    target_efficiency = _clamp(
        city.window_supply - max(0.0, storage_ratio - 0.94) * 1.4 - max(0.0, (25 - city.prosperity) / 180),
        0.35,
        1.0,
    )
    city.efficiency += (target_efficiency - city.efficiency) * min(1.0, dt * 3.0)

    prosperity_delta = 0.18 * dt
    if shortage_total > 0:
        prosperity_delta -= shortage_total * 1.5
    if export_value > 0:
        prosperity_delta += min(0.45, export_value * 0.02)
    if city.money < 15:
        prosperity_delta -= 0.08 * dt
    if storage_ratio > 0.96:
        prosperity_delta -= 0.2 * dt
    if city.window_supply >= 0.99:
        prosperity_delta += 0.08 * dt

    city.prosperity = _clamp(city.prosperity + prosperity_delta, 0.0, 100.0)
    city.window_prosperity_delta += prosperity_delta

    growth_delta = 0.0
    if shortage_total <= 0.001 and city.prosperity >= 45:
        growth_delta += dt * (0.55 + city.level * 0.07)
    if export_value > 0:
        growth_delta += min(0.18, export_value * 0.01)
    if city.money < 15:
        growth_delta -= 0.08 * dt
    if shortage_total > 0:
        growth_delta -= shortage_total * 0.6

    city.growth = max(0.0, city.growth + growth_delta)
    city.window_growth_delta += growth_delta

    if city.growth >= city.growth_threshold():
        city.growth -= city.growth_threshold()
        city.level += 1
        city.prosperity = min(100.0, city.prosperity + 5)
        city.leveled_up = True
        city.add_turn_note(f"Reached level {city.level} and expanded its reach.")
        return 1

    return 0


def _update_hub_note(hub, report):
    if report["trade_count"] > 0:
        income_prefix = "+" if report["hub_income"] >= 0 else ""
        hub.add_turn_note(f"Tariff {hub.tariff_rate:+.0%}. Trade income {income_prefix}{report['hub_income']:.0f}g.")
    elif report["active_city_count"] <= 0:
        hub.add_turn_note("No satellite cities yet. The hub is standing by.")
    else:
        hub.add_turn_note("Waiting for cities to need stock or sell surplus.")


def _build_live_summary(report, tariff_rate):
    if report["active_city_count"] <= 0:
        return "No satellite cities yet. Found one to start trade."
    if report["cash_blocked_count"] > 0 and report["shortage_count"] > 0:
        return f"Trade strained: {report['shortage_count']} shortages, tariff {tariff_rate:+.0%}."
    if report["shortage_count"] > 0:
        return f"Supply slipping: {report['shortage_count']} shortages across the network."
    if report["trade_count"] > 0:
        income_prefix = "+" if report["hub_income"] >= 0 else ""
        return f"Live trade: {report['trade_count']} deals, hub {income_prefix}{report['hub_income']:.0f}g, tariff {tariff_rate:+.0%}."
    return f"Network idle. Tariff holds at {tariff_rate:+.0%}."


def _safe_ratio(numerator, denominator):
    if denominator <= 0:
        return 1.0
    return numerator / denominator


def _clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))
