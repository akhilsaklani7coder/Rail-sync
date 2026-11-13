# RailSync Database Architecture & Setup Guide (Phase 3 Master Release)

This directory contains the relational database definition, initial master schema, and seed dataset for **RailSync — Railway Reservation Simulation System**.

---

## 1. Overview & Technology Stack

* **Database Engine:** MySQL 8.0 / MySQL 8.4 Server
* **Storage Engine:** `InnoDB` exclusively (guaranteeing ACID transactions, row-level locking, and foreign key referential integrity)
* **Character Set & Collation:** `utf8mb4` with `utf8mb4_unicode_ci`
* **Normalisation Level:** Third Normal Form (3NF)

---

## 2. Relational Schema Summary

The database consists of **14 normalized tables**:

```text
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│    users     │       │   stations   │◄──────┤    routes    │
└──────┬───────┘       └──────┬───────┘       └──────────────┘
       │                      │
       │                      │ (source / destination / intermediate stops)
       │                      ▼
       │               ┌──────────────┐       ┌──────────────┐
       │               │    trains    ├──────►│ train_stops  │
       │               └──────┬───────┘       └──────────────┘
       │                      │
       │                      ├──────────────►┌──────────────┐
       │                      │               │   coaches    │
       │                      ▼               └──────┬───────┘
       │               ┌──────────────┐              │
       │               │ seat_alloc.  │◄─────────────┤
       │               └──────┬───────┘              ▼
       │                      ▲               ┌──────────────┐
       ▼                      │               │    seats     │
┌──────────────┐              │               └──────────────┘
│   bookings   ├──────────────┤
└──────┬───────┘              │
       │                      │
       ├──────────────────────┼──────────────►┌───────────────────┐
       │                      │               │ waitlist_entries  │
       │                      │               └───────────────────┘
       ▼                      ▼
┌──────────────┐       ┌──────────────┐
│  passengers  ├───────┤   payments   │
└──────┬───────┘       └──────────────┘
       │
       ├──────────────────────►┌───────────────────┐
       │                      │   cancellations   │
       ▼                      └───────────────────┘
┌──────────────┐
│   tickets    │
└──────────────┘
```

### Table Dictionary:

1. **`users`**: Passenger and administrator credentials, contact numbers, addresses, and PBKDF2/SHA256 password hashes.
2. **`stations`**: 32 major Indian railway hubs across all zones (NDLS, MMCT, CSMT, SBC, MAS, HWH, DDN, HW, JP, ADI, CDG, ST, BVC, NGP, GWL, JBP, GHY, BBS, RNC, TVC, MAO, MYS, etc.).
3. **`routes`**: 56 bidirectional physical track graph edges with distances in km and durations, consumed by the C++17 Dijkstra engine.
4. **`trains`**: 38 express train services categorized by `train_type` (`VANDE_BHARAT`, `RAJDHANI`, `SHATABDI`, `SUPERFAST`, `EXPRESS`).
5. **`train_stops`**: Intermediate station timetable stops with sequence, arrival time, departure time, halt duration, and distance from origin.
6. **`coaches`**: Physical coaches per train across classes (`1A`, `2A`, `3A`, `SL`, `CC`).
7. **`seats`**: Individual seat records with berth types (`LOWER`, `UPPER`, `MIDDLE`, `SIDE LOWER`, `SIDE UPPER`, `WINDOW`, `AISLE`).
8. **`bookings`**: ACID booking records with unique 10-character PNR (`RS` + 8 digits), travel class, fare breakdown, and status (`CONFIRMED`, `RAC`, `WAITLISTED`, `CANCELLED`).
9. **`passengers`**: Passenger demographics, berth preferences, and allocated seat or waitlist positions (`WL-X`, `RAC-X`).
10. **`tickets`**: Electronic Reservation Slip (ERS) identifiers with verification links.
11. **`seat_allocations`**: Date-specific relational seat allocation model with `UNIQUE KEY uq_seat_date_allocated (seat_id, journey_date)`.
12. **`waitlist_entries`**: FIFO queue tracking RAC and Waiting List positions for automated promotion upon cancellation.
13. **`payments`**: Simulated payment transaction logs with method (`UPI`, `CARD`, `NET_BANKING`), bank reference, and amount.
14. **`cancellations`**: Audit records for cancellations, calculating rules-based charges, simulated refunds, and waitlist promotion counts.

---

## 3. Database Initialization Instructions

### Method A: Automated Initialization via Python (Recommended)

```powershell
# In project root
$env:PYTHONPATH="backend"
.\backend\venv\Scripts\python.exe backend\scripts\expand_database.py
```

### Method B: MySQL Command-Line Client

```bash
# 1. Login to MySQL
mysql -u root -p

# 2. Run the master schema script
mysql -u root -p < database/schema.sql

# 3. Seed master data
mysql -u root -p < database/seed.sql
```

---

## 4. Default Seed Accounts

| Role | Email | Password | Access Privileges |
| :--- | :--- | :--- | :--- |
| **Demo Passenger** | `user@railsync.com` | `User@123` | Search trains, interactive seat booking, PNR inquiry, PDF ticket download, profile update, cancellation. |
| **Administrator** | `admin@railsync.com` | `Admin@123` | Full passenger access plus Admin Dashboard, Train Fleet, Station Network, Route Timetables, and Reservation Audit. |
