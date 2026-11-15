# RailSync — Railway Reservation Simulation System

> **Full-Stack Academic Railway Reservation Simulation System Inspired by Indian Railways (IRCTC).**  
> *Phase 3 Final Production Release — Complete Implementation, Real Database Integration & C++17 Routing Engine.*

---

## 1. Project Overview

**RailSync** is an academic railway reservation simulation system designed to deliver a realistic, responsive, and robust digital booking experience inspired by Indian Railways (IRCTC). Built for college Project-Based Learning (PBL), RailSync integrates modern full-stack web engineering with core Computer Science mechanisms:

* **Relational Database Systems (DBMS):**
  * Fully normalized Third Normal Form (3NF) relational schema spanning **14 InnoDB tables** in MySQL 8.4 Server.
  * Strict ACID transaction control (`COMMIT` on atomic success, instant `ROLLBACK` on error).
  * Explicit row-level concurrency locking via `SELECT ... FOR UPDATE` preventing double-booking race conditions under simultaneous passenger demand.
  * Date-specific relational seat allocation model with `UNIQUE KEY uq_train_seat_date (train_id, seat_id, journey_date)`.
  * Transactional FIFO Waitlist (WL) and RAC queue management with automatic seat promotion upon ticket cancellation.
* **Algorithm & Operating System Engines (OS):**
  * High-performance native C++17 route engine utilizing Dijkstra's shortest-path algorithm with an $O((V+E)\log V)$ min-heap priority queue (`std::priority_queue`).
  * Thread-safe memory access guarded by RAII-scoped mutual exclusion (`std::mutex`).
  * In-memory 64-bit ABI bridge connecting Flask to compiled native C++ binaries via Python `ctypes`.
  * PDF generation CPU bound protection via counting semaphores (`threading.Semaphore(value=5)`).

> [!IMPORTANT]
> **Academic Simulation Notice:** RailSync is an educational railway reservation simulation system. It does not connect to live Indian Railways or IRCTC production systems. All financial transactions and ticketing operations are safe simulations. Dockerization is intentionally excluded from this release.

---

## 2. Key Features

### Passenger & User Experience
* **Station Network & Train Discovery:** Search across 54 major Indian railway hubs and 48 express train services spanning 9 categories (Vande Bharat, Rajdhani, Shatabdi, Duronto, Garib Rath, Superfast, Mail/Express, Intercity, Express) with direct and intermediate stop matching.
* **Intermediate Timetable Stops:** View complete train schedules across 206 route stops with intermediate stop sequences, arrival/departure times, halt durations, and distances from origin.
* **Faceted Search Filters:** Filter trains by departure and arrival time slots (Early Morning, Morning, Mid-day, Night), train categories, travel classes (`1A`, `2A`, `3A`, `CC`, `SL`), live max fare slider, and seat availability.
* **Quick Train Lookup:** Search directly by train number or train name (e.g. `12017`, `Duronto`, `Garib Rath`) with instant timetable and seat availability.
* **Side-by-Side Train Comparison:** Compare 2 to 3 trains simultaneously across departure/arrival timings, journey duration, physical distance, class fares, and seat counts.
* **Dynamic Multi-Class Fare Calculator:** Rules-based fare engine computing authoritative fares across AC First Class (`1A`), AC 2-Tier (`2A`), AC 3-Tier (`3A`), AC Chair Car (`CC`), and Sleeper (`SL`) with class multipliers, reservation fees, superfast surcharges, and 5% statutory GST on AC classes.
* **Multi-Passenger Booking with Berth Preferences:** Book up to 6 passengers per ticket with individual preferences (`Lower`, `Upper`, `Middle`, `Side Lower`, `Side Upper`, `Window`, `Aisle`).
* **RAC & Waiting List Queue Simulation:** When confirmed capacity is exhausted, passengers are queued into RAC (Reservation Against Cancellation, up to 8 per class) and Waiting List (WL).
* **Automatic Waitlist Promotion:** When a confirmed booking is cancelled, released seats are automatically and transactionally allocated to queued RAC and WL passengers in strict FIFO order.
* **Step 4 Simulated Payment Gateway:** Multi-method simulated gateway supporting UPI, Credit/Debit Cards, and Net Banking with deterministic test simulation toggles (Simulate Success vs Bank Decline), explicit state machine, idempotency key protection, and dedicated failure recovery with state preservation.
* **Dynamic Vector QR Code Verification:** Generates real-time verification QR codes embedded in Electronic Reservation Slips and ReportLab PDF tickets.
* **Public PNR Status Inquiry:** Real-time PNR tracking with privacy-preserving passenger name masking for unauthenticated or non-owner lookups (`Rohan S***`).
* **Official PDF Ticket Generation:** Download printable e-tickets with embedded QR codes, journey details, passenger manifests, and fare breakdowns.
* **Categorized Booking History:** View past and upcoming travel organized into **Upcoming Journeys**, **Completed Journeys**, and **Cancelled Journeys**.
* **Rules-Based Cancellation & Instant Refund:** Interactive cancellation modal displaying statutory clerkage/cancellation fee deductions and net refund calculations.
* **Passenger Profile & Telemetry:** User profile with editable contact details, address, and live travel statistics cards (Total Bookings, Confirmed, Cancelled, and Total Fare Invested).

### Administration & Fleet Operations
* **Executive Metrics Dashboard:** Real-time metrics for registered passengers, active train fleet, booking counts, revenue, and recent reservation audits.
* **Train Fleet Management:** Add, edit, or toggle train statuses with automatic coach and seat seeding.
* **Timetable Editor:** Inspect, add, and remove intermediate timetable stops for any train in the network.
* **Station Management:** Add, edit, and toggle active status for stations across the national network.
* **Reservation Audit Trail:** Audit all system bookings with passenger details and payment records.
* **System Diagnostics Endpoint:** Live telemetry inspecting MySQL table row counts, ACID guarantees, and C++ engine status.

---

## 3. Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 19, Vite 8, React Router 7, Tailwind CSS v4, Axios, Lucide React Icons |
| **Backend** | Python 3.13, Flask 3.1, Flask-CORS, Werkzeug (PBKDF2/SHA256), ReportLab, QRCode, Pillow |
| **Database** | MySQL 8.4 Server (InnoDB Engine, Strict ACID, Row-Level Locking, 14 3NF Tables) |
| **Algorithm Engine** | C++17 Standard Library, `std::mutex`, `std::priority_queue` (Min-Heap) |
| **Language Interop** | Python 64-bit `ctypes` CDLL in-memory ABI bridge + Native CLI executable fallback |
| **Testing** | Pytest 9.1 (52 automated tests passing 100%) |

---

## 4. System Architecture

```text
React 19 Frontend (Port 8080)
      │
      │ REST APIs (JSON / Cookie Sessions) via Vite Proxy (/api)
      ▼
Flask 3.1 Backend (Port 5001)
      │
      ├── In-Memory 64-bit ctypes CDLL / CLI Bridge
      │     └── C++17 Algorithm Engine (railsync_engine.dll / engine_cli.exe)
      │           ├── Dijkstra Shortest Path (std::priority_queue Min-Heap)
      │           └── Mutex Critical Section & Contiguous Seat Allocator
      │
      ├── Python Simulation Services
      │     ├── FareService (Multi-Class Multipliers, Reservation Fees, GST)
      │     ├── WaitlistService (RAC & WL Queuing, Transactional FIFO Promotion)
      │     ├── PDFService (ReportLab Vector PDF + Embedded QRCode)
      │     └── BookingService (InnoDB Row-Level Locking SELECT ... FOR UPDATE)
      │
      └── MySQL Connection Pool (10 Connections)
            └── MySQL 8.4 InnoDB Database (Port 3306)
                  ├── 14 Normalized Relational Tables (InnoDB)
                  ├── Row-Level Concurrency Locking (SELECT ... FOR UPDATE)
                  └── Date-Isolated Seat Allocations (UNIQUE seat_id, journey_date)
```

---

## 5. Database Architecture (14 Normalized Tables)

The database schema is strictly normalized and enforced in InnoDB:

| Table | Purpose | Key Constraints |
| :--- | :--- | :--- |
| `users` | User accounts, roles, hashed passwords, phone, address | `email UNIQUE`, `role ENUM('USER', 'ADMIN')` |
| `stations` | Major railway hubs and junction codes | `station_code UNIQUE`, indexed on `is_active` |
| `routes` | Network edges with physical rail distances (km) | Foreign keys to `stations`, composite index on source/dest |
| `trains` | Scheduled train services and flagship categories | `train_number UNIQUE`, `train_type ENUM` |
| `train_stops` | Intermediate timetable schedules | `UNIQUE (train_id, stop_sequence)`, foreign keys |
| `coaches` | Physical rail coaches per train (`1A`, `2A`, `3A`, `CC`, `SL`) | Composite index on `(train_id, coach_type)` |
| `seats` | Numbered seats and berths (`LOWER`, `UPPER`, `MIDDLE`, etc.) | Foreign key to `coaches`, indexed on `coach_id` |
| `bookings` | Master reservation records with PNR and fare breakdown | `pnr UNIQUE`, `booking_status ENUM`, foreign keys |
| `passengers` | Travelers with age, gender, berth preference, status | Foreign key to `bookings`, indexed on `booking_id` |
| `tickets` | Issued electronic reservation slips | `ticket_number UNIQUE`, foreign key to `bookings` |
| `seat_allocations`| Date-isolated seat occupation records | `UNIQUE KEY (train_id, seat_id, journey_date)` |
| `waitlist_entries`| RAC and Waiting List priority queues | `entry_type ENUM('RAC', 'WL')`, `current_status ENUM` |
| `payments` | Simulated payment transactions and gateway audit | `transaction_id UNIQUE`, `payment_method ENUM` |
| `cancellations`| Cancellation fee deductions and refund audit | `cancellation_number UNIQUE`, foreign keys |

---

## 6. Project Directory Structure

```text
RailSync/
├── backend/
│   ├── app/
│   │   ├── config.py                 # Central application settings & database config
│   │   ├── database/
│   │   │   ├── connection.py         # MySQL connection pooling & transactional context
│   │   ├── routes/
│   │   │   ├── admin.py              # Fleet, station, timetable, and diagnostic APIs
│   │   │   ├── auth.py               # Authentication, user profile, and telemetry APIs
│   │   │   ├── bookings.py           # Reservation, PNR lookup, cancellation, QR, & PDF APIs
│   │   │   ├── payments.py           # Simulated payment gateway endpoint
│   │   │   └── trains.py             # Station discovery, search, stops, and fare quote APIs
│   │   ├── security/
│   │   │   └── auth_helpers.py       # Session wrappers (@login_required, @admin_required)
│   │   └── services/
│   │       ├── booking_service.py    # Transactional booking & cancellation engine
│   │       ├── cpp_engine_service.py # In-memory ctypes CDLL / CLI bridge
│   │       ├── fare_service.py       # Multi-class dynamic fare calculator & refund rules
│   │       ├── pdf_service.py        # ReportLab vector PDF ticket generator with QR code
│   │       ├── train_service.py      # Train search, availability, stops, & Dijkstra wrapper
│   │       └── waitlist_service.py   # RAC & WL FIFO queuing and automatic promotion
│   ├── cpp_engine/
│   │   ├── include/                  # C++ headers (graph.hpp, allocator.hpp, engine_export.h)
│   │   ├── src/                      # C++ implementations (dijkstra.cpp, allocator.cpp, main.cpp)
│   │   ├── railsync_engine.dll       # Compiled 64-bit native shared library
│   │   └── engine_cli.exe            # Native CLI executable fallback
│   ├── scripts/
│   │   ├── build_cpp.py              # Cross-platform MinGW / MSVC compiler script
│   │   ├── expand_database.py        # Schema migrator & seed generator
│   │   └── generate_seed_sql.py      # Database seed exporter
│   ├── tests/                        # 47 comprehensive automated Pytest test cases
│   ├── main.py                       # Flask entry point (Port 5001)
│   └── requirements.txt              # Backend dependencies
│
├── frontend/
│   ├── src/
│   │   ├── api/axios.js              # Centralized Axios HTTP client
│   │   ├── components/               # Navbar, Footer, TrainCard, StatusBadge, LoadingSpinner
│   │   ├── context/                  # AuthContext, ToastContext
│   │   ├── layouts/                  # PublicLayout, AdminLayout
│   │   ├── pages/                    # Home, SearchTrains, PassengerDetails, Payment,
│   │   │                             # BookingConfirmation, MyBookings, TicketDetails, Profile,
│   │   │                             # AdminDashboard, ManageTrains, ManageStations, ManageBookings
│   │   ├── App.jsx                   # React Router route registry
│   │   └── main.jsx                  # React application root
│   ├── package.json
│   └── vite.config.js                # Vite configuration with proxy to port 5001
│
├── database/
│   ├── schema.sql                    # Complete 14-table DDL with keys and constraints
│   ├── seed.sql                      # Production seed dataset (stations, trains, stops, coaches, seats)
│   └── README.md                     # Database documentation and reproduction guide
│
├── PHASE3_AUDIT.md                   # Complete audit and implementation matrix
├── TESTING.md                        # Verification and test execution report (47/47 passing)
├── .env.example                      # Environment configuration template
└── README.md                         # Main project documentation
```

---

## 7. Installation & Setup Guide

### Prerequisites
* **Python 3.11+ (64-bit)**
* **Node.js 18+ and npm**
* **MySQL Server 8.0 or 8.4**
* **C++ Compiler (Optional for re-compilation):** MinGW-w64 (g++) or MSVC (`cl.exe`). A precompiled 64-bit DLL is already bundled.

---

### Step 1: Database Setup

1. Start your local MySQL server.
2. Log into MySQL and create the database:
   ```sql
   CREATE DATABASE IF NOT EXISTS railsync CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. Import the schema and seed data using MySQL CLI:
   ```powershell
   mysql -u root -p railsync < database\schema.sql
   mysql -u root -p railsync < database\seed.sql
   ```

---

### Step 2: Backend Setup

1. Navigate to the backend directory and activate the virtual environment:
   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. Install Python dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Configure environment variables. Copy `.env.example` to `backend\.env` and adjust your MySQL credentials:
   ```env
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=railsync
   SECRET_KEY=railsync-super-secret-key-phase3
   FLASK_ENV=development
   ```
4. Start the Flask backend server:
   ```powershell
   $env:PYTHONPATH="backend"
   python backend\main.py
   ```
   *The backend will start on `http://127.0.0.1:5001`.*

---

### Step 3: Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```powershell
   cd frontend
   npm install
   ```
2. Start the Vite development server:
   ```powershell
   npm run dev
   ```
   *The frontend user interface will be live at `http://localhost:8080`.*

---

### Step 4: Verification & Automated Tests

Run the full automated test suite using Pytest:
```powershell
$env:PYTHONPATH="backend"
.\backend\venv\Scripts\pytest.exe -v backend\tests
```
*Expected result: 47 passed in ~2.5 seconds (100% pass rate).*

Verify the production frontend build:
```powershell
npm --prefix frontend run build
```
*Expected result: Vite production bundle builds cleanly in <1 second with 0 errors.*

---

## 8. Default Credentials

The database seed script creates the following demo accounts:

| Role | Email | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@railsync.com` | `Admin@123` | Full access to fleet, stations, timetable, and reservation audits |
| **Passenger** | `user@railsync.com` | `User@123` | Passenger reservation, PNR lookups, cancellations, and profile |

---

## 9. Academic PBL Assessment Criteria

| Criteria | Implementation Evidence |
| :--- | :--- |
| **OS Primitives** | C++17 `std::mutex` critical section; `std::priority_queue` min-heap Dijkstra routing; counting semaphores bounding CPU-heavy PDF generation. |
| **DBMS Transactions** | MySQL InnoDB ACID atomicity; row-level locking (`SELECT ... FOR UPDATE`); date-isolated relational seat allocation table. |
| **Full-Stack Integration** | React 19 UI → RESTful Flask APIs → C++ in-memory ABI interop → MySQL InnoDB storage. |
| **Concurrency Protection** | Two simultaneous requests competing for the exact same seat: the first commits atomically, the second receives an immediate rejection with zero duplicate allocations. |
| **Automated Testing** | 47 automated Pytest unit and integration tests verifying all critical workflows. |

---

## 10. License & Academic Disclaimer

This project is submitted for academic assessment purposes under the MIT License. Developed as a Project-Based Learning (PBL) simulation system demonstrating Operating Systems and Database Management Systems engineering principles.
