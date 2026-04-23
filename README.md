# HubOfProsperity
A simple City Trade Manager

## Economy System

The game now runs on a live, speed-based resource economy.

- Every city has stored resources, production, consumption, and storage capacity.
- Cities produce and consume continuously while the simulation is running.
- If a city drops low on needed stock, it automatically buys from the hub with its own money.
- Cities sell surplus goods back to the hub, which gives them income and feeds the network buffer.
- The hub applies a live tariff to imports, so you can make trade cheaper or extract more revenue.
- Hub revenue can be spent on hub upgrades, which improve storage and trade capacity.
- Shortages lower efficiency and prosperity, while stable profitable trade grows cities over time.
- Overfilled storage still creates pressure, so hoarding is not free.

## Controls

- `Left Click` a hex to inspect or manage its city.
- `Tariff -` and `Tariff +` in the top-right economy panel change hub prices.
- `Upgrade` in the top-right economy panel spends hub money on a hub level.
- `Space` pauses or resumes the live simulation.
- `Enter` renames the currently selected city while the name field is active.
- `Esc` closes the selected city panel.
