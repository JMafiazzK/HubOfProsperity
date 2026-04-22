# 🏙️ Hub of Prosperity

A minimalist hex-based city-building strategy game focused on resource management, expansion, and economic control.

---

## 🎮 Concept

You start with a single central hub and expand your influence by building specialized cities on a hex grid.

Each city:

* produces specific resources
* consumes others
* evolves over time

The goal is to build a **self-sustaining and optimized network of cities**.

---

## 🧠 Core Mechanics

### 🟡 Hex Grid System

* Pointy-top hex grid using axial coordinates `(q, r)`
* Click-based interaction
* Dynamic expansion

---

### 🏙️ Cities

Each city has:

* a **type** (e.g. wood, water, hub)
* its own **resources**
* **production & consumption**
* **level & efficiency**

Cities are stored as:

```python
state.cities[(q, r)] = City(...)
```

---

### 📦 Resources

Basic resources:

* Wood
* Water
* Food

Each city:

* produces certain resources per turn
* consumes others
* stores its own inventory

---

### ⚙️ Systems (Planned / WIP)

* Production system (tick-based)
* Trade system between cities
* Dynamic pricing (hub-based economy)
* Upgrade system
* Population & growth mechanics

---

## 🖥️ UI Overview

### 🧭 Main View

* Hex grid map
* Clickable tiles
* Visual feedback (selection, city presence)

---

### 📊 Sidebar

Displays selected tile:

**Empty Tile**

* Option to build a city

**City View**

* Name & type
* Resources
* Production / consumption
* Actions (upgrade, trade, etc.)

---

## 🧱 Project Structure

```plaintext
project/
│
├── game/
│   ├── state.py          # game state (cities, selection)
│   ├── game_loop.py      # main loop & input handling
│
├── world/
│   ├── hex_grid.py       # grid math (pixel ↔ hex)
│   ├── city.py           # City class
│   ├── city_types.py     # definitions of city behavior
│
├── ui/
│   ├── sidebar.py        # sidebar rendering
│
├── config.py             # global constants
│
└── main.py               # entry point
```

---

## 🧩 Architecture Philosophy

* **State-driven design**
* No tight coupling between systems
* Grid = geometry only
* Cities = data only
* Systems = logic only

---

## 🚀 Getting Started

### Requirements

* Python 3.10+
* pygame

### Install

```bash
pip install pygame
```

### Run

```bash
python main.py
```

---

## 🎯 Current Features

* Hex grid rendering
* Mouse interaction
* Tile selection
* City creation
* Basic city data model

---

## 🔮 Roadmap

* [ ] Resource simulation loop
* [ ] City specialization system
* [ ] UI improvements (hover, animations)
* [ ] Economy & trading
* [ ] Save/Load system

---

## 🧠 Vision

A clean, scalable strategy game where complexity emerges from simple systems:

* local decisions → global economy
* resource flow → strategic depth

---

## 📌 Notes

This project is built step-by-step with focus on:

* clean architecture
* simplicity first
* scalability later

---

## 🧑‍💻 Author

Jeremy Krämer

---
