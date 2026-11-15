# RailSync — Final Project & Architecture Audit

**Project:** RailSync — Full-Stack Indian Railway Reservation Simulation System  
**Evaluation:** Academic PBL (Operating Systems & Database Management Systems)  
**Date of Audit:** November 15, 2026  
**Status:** 100% Implemented, Verified & Submission-Ready  

---

## 1. System Architecture Overview

RailSync is engineered as a three-tier, ACID-compliant railway reservation simulation architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                   React 18 + Vite SPA                       │
│    (Tailwind CSS, Lucide Icons, Dynamic Faceted Search,      │
│     Interactive Coach Seat Map, 4-Step Checkout Modal)      │
└──────────────────────────────┬──────────────────────────────┘
                               │ JSON REST API (HTTP/CORS)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Python 3.11 / Flask REST API                 │
│  (Auth, Booking, Payments, Fare Quoting, PDF Generator)     │
│                              │                              │
│   ┌──────────────────────────┴──────────────────────────┐   │
│   │   C++17 Engine (ctypes CDLL & Native Process CLI)   │   │
│   │   • Dijkstra Shortest Path (std::priority_queue)   │   │
│   │   • Deterministic Contiguous Seat Allocator         │   │
│   │   • std::mutex Mutual Exclusion Verification        │   │
│   └─────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────┘
                               │ Parameterized SQL (%s)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  MySQL 8.4 Server (InnoDB)                  │
│   (14 Relational Tables, Row-Level Locking 'FOR UPDATE',    │
│    Idempotency Verification, Foreign Key Cascades)          │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Comprehensive Component Audit

### 2.1 Frontend Tier (`frontend/`)
- **Technology:** React 18, Vite 8, Tailwind CSS, React Router v7.
- **Pages & Routes:**
  - `/`: Home Landing page with railway corridor highlights and quick PNR search.
  - `/search`: Faceted train search supporting origin, destination, journey date, train categories (Vande Bharat, Rajdhani, Shatabdi, Duronto, Garib Rath, Superfast, Mail/Express, Intercity), class filters (`1A`, `2A`, `3A`, `CC`, `SL`), fare slider, and 3-train side-by-side comparison.
  - `/train/:trainId`: Interactive Coach Seat Map displaying coaches (`B1`, `A1`, `H1`, `C1`), real-time seat states (`AVAILABLE`, `BOOKED`, `SELECTED`), and C++ allocation strategy toggle.
  - `/passenger-details`: Multi-passenger manifest (up to 6 passengers), auto seat assignment mapping, real-time backend fare quote.
  - `/payment`: 4-step payment authorization modal featuring gateway state machine (`IDLE` $\to$ `PROCESSING` $\to$ `SUCCESS` / `FAILED`), test cards, state-preserving retry, and idempotency protection.
  - `/booking-confirmation/:pnr`: Booking summary with PNR, travel class, and ticket actions.
  - `/ticket/:pnr`: Official-format digital ticket with embedded vector QR code and PDF download.
  - `/pnr-status`: PNR lookup with passenger status and journey timeline.
  - `/my-bookings`: Booking history with status filters (Confirmed, Cancelled, Completed) and cancellation triggers.
  - `/admin/*`: Comprehensive administration portal for stations, trains, timetable stops, bookings, and diagnostic telemetry.
- **Audit Findings & Fixes:**
  - *Fixed Issue:* Clicking "Book Now" on train search cards bypassed seat selection. Resolved by routing `TrainCard` and comparison modal directly to `/train/:id` with initial class and coach synchronization.
  - *Fixed Issue:* Step 4 Payment authorization previously failed due to client class mismatches and lack of idempotency. Fully resolved with atomic idempotency and synchronized coach data.

### 2.2 Backend Tier (`backend/app/`)
- **Technology:** Python 3.11, Flask 3.0, ReportLab 4.0, QRCode, MySQL Connector Python.
- **Modules & Services:**
  - `booking_service.py`: Atomic reservation transactions using `SELECT ... FOR UPDATE`, idempotency checking, and rollback safety.
  - `fare_service.py`: Backend-authoritative fare calculation factoring base fare, class multipliers, distance, superfast surcharges, and reservation fees.
  - `cpp_engine_service.py`: Dual-mode C++ engine bridge utilizing direct 64-bit in-process `ctypes.CDLL` and subprocess fallback.
  - `pdf_service.py`: Vector e-Ticket PDF generator with ReportLab and embedded QR verification code bounded by a threading Semaphore.
  - `train_service.py`: Multi-criteria train searching, intermediate timetable stop matching, and station network graphs.
  - `waitlist_service.py`: Automated RAC / Waitlist promotion upon booking cancellation.

### 2.3 Database Tier (`database/`)
- **Technology:** MySQL 8.4 InnoDB.
- **Dataset Metrics:**
  - **Stations:** 55 major railway stations across 12 zonal divisions (NR, WR, CR, SR, ER, NCR, etc.).
  - **Trains:** 48 verified express, superfast, Vande Bharat, Rajdhani, and Shatabdi trains.
  - **Timetable Stops:** 206 sequenced intermediate station stops with arrival, departure, distance, and halt times.
  - **Routes:** 84 railway network track edges with kilometer distances.
  - **Coaches:** 192 coaches spanning classes `1A`, `2A`, `3A`, `CC`, and `SL`.
  - **Seats:** 3,072 individual seats with berth positions (Lower, Middle, Upper, Side Lower, Side Upper, Window, Aisle).
  - **Integrity Constraints:** Foreign key constraints with `ON DELETE CASCADE` or `RESTRICT`, unique composite index on `(coach_id, seat_number)` and `(train_id, stop_sequence)`.

### 2.4 C++17 Dijkstra Route Engine (`backend/cpp_engine/`)
- **Implementation:** `core_logic.h`, `core_logic.cpp`, `engine_cli.cpp`, `Makefile`.
- **Features:**
  - Graph representation using adjacency lists with positive edge weights.
  - Shortest path calculated via `std::priority_queue` min-heap in $\mathcal{O}((V + E) \log V)$ time.
  - Mutex-protected contiguous seat allocator (`allocate_seats`) with `std::mutex` mutual exclusion.
  - Cross-platform export macros supporting Linux (`librailsync_engine.so`) and Windows (`railsync_engine.dll`).
- **Telemetry:** Tested and operational on Windows 11 64-bit and Linux x86_64 container environments.

### 2.5 Dockerization & Deployment Architecture
- **Docker Compose:** Multi-container topology (`db`, `backend`, `frontend`) connected via isolated bridge network `railsync-network`.
- **Container Health Checks:** Health checks configured on all services with explicit startup dependencies (`condition: service_healthy`).
- **Automated Seeding:** Mounted `./database/schema.sql` and `./database/seed_data.sql` to `/docker-entrypoint-initdb.d/` for zero-configuration startup.

---

## 3. Test Coverage & Verification Audit

- **Total Automated Tests:** 52 tests executed via `pytest backend/tests/ -v`.
- **Pass Rate:** 100% (52 passed in 3.62s).
- **Test Categories:**
  - Admin & Role Authorization: 6/6 passed.
  - Advanced Features & Fares: 8/8 passed.
  - Authentication & Token Security: 5/5 passed.
  - Booking & Seat Locking Transactions: 4/4 passed.
  - Concurrency & ACID Rollback: 2/2 passed.
  - C++ Dijkstra Engine & Mutex: 11/11 passed.
  - Payment Refinements & Idempotency: 5/5 passed.
  - Train Search & Intermediate Stops: 11/11 passed.

---

## 4. Final Verdict

The RailSync application satisfies all architectural, functional, security, concurrency, algorithmic, database, and containerization requirements set forth in the master specification. The project is verified, cleanly committed, and prepared for final delivery.
