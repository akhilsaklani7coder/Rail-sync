# RailSync — Team Task Distribution & Module Ownership

**Project:** RailSync — Railway Reservation Simulation System  
**Course:** Problem Based Learning (Operating Systems & Database Management Systems)  
**Academic Year:** 2026  
**GitHub Repository:** [https://github.com/akhilsaklani7coder/Rail-sync](https://github.com/akhilsaklani7coder/Rail-sync)  

---

## 1. Team Roster & Executive Division of Responsibility

The development, architectural design, algorithmic implementation, database engineering, and quality assurance of **RailSync** were divided among six team members:

| S.No. | Member Name | Assigned Role | Primary Focus Area | Key Modules Owned |
|:---:|---|---|---|---|
| 1 | **Umanga** | **Team Leader & DevOps Architect** | System Architecture & Dockerization | Multi-container Docker Compose, Nginx Reverse Proxy, Git Governance |
| 2 | **Akhil** | **Core Backend Architect** | Flask REST API & Transactional Services | Booking engine, Payment simulation, Fare calculator, Waitlist, QR Tickets |
| 3 | **Vedansh** | **Frontend Architect & UI/UX Lead** | React 18 SPA & Interactive UI | Search filters, Coach Seat Map, Checkout modal, PNR inquiry |
| 4 | **Aditya** | **Database Architect** | MySQL 8.4 Schema & Concurrency | 14 InnoDB tables, Row locking (`FOR UPDATE`), 206 stops dataset |
| 5 | **Yash** | **Systems & Algorithms Engineer** | C++17 Dijkstra Engine & OS Mutex | Min-Heap shortest path, Contiguous allocator, Python `ctypes` bridge |
| 6 | **Abhinav** | **Security, Diagnostics & QA Lead** | RBAC, Diagnostics API & Testing | System Diagnostics API, QR Verification, 52 Pytest automated tests |

---

## 2. Detailed Member Profiles & Module Breakdown

### 2.1 Umanga (Team Leader & DevOps Architect)
- **Role:** Project Lead, Containerization & Systems Orchestration
- **Source Code & Files Owned:**
  - `docker-compose.yml`: Multi-container topology orchestrating MySQL 8.4, Flask backend, and Nginx frontend.
  - `frontend/Dockerfile`: Multi-stage production build (`node:20-alpine` builder $\to$ `nginx:alpine` runner).
  - `frontend/nginx.conf`: Production web server configuration with SPA fallback routing and `/api/` reverse proxy.
  - `backend/Dockerfile`: Debian-based Python 3.11 container compiling C++17 `librailsync_engine.so` via `g++`.
  - `DOCKER_GUIDE.md`: Container operations, persistent volume lifecycle, and deployment documentation.
- **Key Technical Responsibilities:**
  - Designed the isolated bridge network (`railsync-network`) and health check dependencies (`condition: service_healthy`).
  - Managed persistent Docker volume (`mysql_data`) and automated `/docker-entrypoint-initdb.d/` database initialization.
  - Overall project milestone governance, task tracking, and final delivery coordination.

---

### 2.2 Akhil (Core Backend Architect & Flask REST API Engineer)
- **Role:** Backend Application Logic & Transactional Services Specialist
- **Source Code & Files Owned:**
  - `backend/app/routes/bookings.py` & `backend/app/services/booking_service.py`: Atomic reservation transactions and booking lookup.
  - `backend/app/routes/payments.py`: Simulated payment gateway API supporting idempotency tokens, bank decline toggles, and state machine transitions.
  - `backend/app/services/fare_service.py`: Rules-based authoritative fare engine factoring distance, class multipliers, superfast surcharges, reservation fees, and GST.
  - `backend/app/services/waitlist_service.py`: FIFO queue manager for RAC (Reservation Against Cancellation) and Waiting List (WL) auto-promotion.
  - `backend/app/services/pdf_service.py`: Vector e-Ticket PDF generator with ReportLab 4.0, embedded QR codes, and a counting semaphore (`threading.Semaphore(value=5)`).
  - `backend/app/services/train_service.py` & `backend/app/routes/trains.py`: Multi-criteria train searching and intermediate stop route matching.
- **Key Technical Responsibilities:**
  - Overhauled Step 4 Payment Authorization to prevent race conditions and duplicate booking submissions.
  - Designed backend-authoritative fare calculation ensuring client cannot tamper with pricing.
  - Implemented CPU protection bounded semaphores to prevent Denial of Service during PDF generation.

---

### 2.3 Vedansh (Frontend Architect & UI/UX Specialist — Swapped)
- **Role:** React Single Page Application & Client Experience Lead
- **Source Code & Files Owned:**
  - `frontend/src/App.jsx` & `frontend/src/layouts/PublicLayout.jsx`: Application navigation routing and top navbar.
  - `frontend/src/pages/SearchTrains.jsx` & `frontend/src/components/TrainCard.jsx`: Faceted train search, quick keyword lookup, class availability badges, and 3-train comparison modal.
  - `frontend/src/pages/TrainDetails.jsx` & `frontend/src/components/SeatMap.jsx`: Interactive Coach Seat Map showing layout, available/occupied seats, and class coach selector.
  - `frontend/src/pages/PassengerDetails.jsx`: Multi-passenger dynamic manifest form (up to 6 passengers) with berth preferences.
  - `frontend/src/pages/Payment.jsx`: 4-step payment modal with state machine (`IDLE` $\to$ `PROCESSING` $\to$ `SUCCESS`/`FAILED`), gateway simulation, and retry flow.
  - `frontend/src/pages/PNRStatus.jsx`, `TicketDetails.jsx`, & `BookingConfirmation.jsx`: PNR tracking with masked passenger privacy, printable digital ticket, and vector QR code.
  - `frontend/src/context/AuthContext.jsx` & `ToastContext.jsx`: Global authentication state and floating notification toasts.
- **Key Technical Responsibilities:**
  - Connected the entire booking workflow seamlessly from Train Search $\to$ Seat Map $\to$ Passenger Details $\to$ Payment $\to$ Ticket.
  - Built responsive mobile, tablet, and desktop layouts using modern Tailwind CSS.
  - Ensured that selected travel class (e.g. `3A`, `2A`, `CC`) automatically opens the corresponding coach in the seat picker.

---

### 2.4 Aditya (Database Architect & SQL Concurrency Engineer — Swapped)
- **Role:** Relational Schema Designer & Database Concurrency Specialist
- **Source Code & Files Owned:**
  - `database/schema.sql`: Full DDL defining 14 normalized tables operating under the MySQL 8.4 InnoDB engine.
  - `database/seed_data.sql`: Repeatable 139 KB SQL dataset seeding 55 stations, 48 trains, 206 timetable stops, 84 routes, 192 coaches, and 3,072 seats.
  - `backend/scripts/generate_seed_sql.py`: Automated export script synchronizing live database state to seed files.
  - `DATABASE_DOCUMENTATION.md`: Schema dictionary, entity relationship diagram (ERD), constraint definitions, and indexing strategies.
- **Key Technical Responsibilities:**
  - Normalized the database schema to Third Normal Form (3NF) to eliminate update and deletion anomalies.
  - Implemented explicit row-level locking (`SELECT ... FOR UPDATE`) in MySQL InnoDB to guarantee serializable isolation for concurrent seat reservations.
  - Created composite indexes (`(train_id, stop_sequence)`, `(coach_id, seat_number)`) to accelerate timetable search and seat lookups.

---

### 2.5 Yash (Systems & Algorithms Engineer)
- **Role:** High-Performance C++ Core & Operating Systems Synchronization Lead
- **Source Code & Files Owned:**
  - `backend/cpp_engine/core_logic.cpp` & `core_logic.h`: Native C++17 implementations of Dijkstra's algorithm and contiguous seat allocator.
  - `backend/cpp_engine/engine_cli.cpp`: Standalone native CLI execution bridge.
  - `backend/cpp_engine/Makefile`: Cross-platform compilation generating `railsync_engine.dll` (Windows) and `librailsync_engine.so` (Linux).
  - `backend/app/services/cpp_engine_service.py`: In-memory 64-bit ABI bridge using Python `ctypes.CDLL` with subprocess fallback.
  - `backend/scripts/build_cpp.py`: Automated build script compiling C++ source files across platforms.
- **Key Technical Responsibilities:**
  - Modeled the national railway network as an adjacency list graph and implemented Dijkstra's shortest path using `std::priority_queue` min-heap.
  - Implemented mutual exclusion (`std::mutex`) around shared critical sections to demonstrate OS synchronization principles.
  - Built the deterministic contiguous seat allocation algorithm to assign adjoining seats to family reservations.

---

### 2.6 Abhinav (Security, Diagnostics & QA Lead — Expanded)
- **Role:** Security Engineer, System Diagnostics Architect & Test Automation Lead
- **Source Code & Files Owned:**
  - `backend/app/routes/admin.py`: Live System Diagnostics API (`/api/admin/diagnostics`) inspecting MySQL row counts, active connections, ACID rollback verification, and C++ engine status telemetry.
  - `backend/app/services/pdf_service.py`: Vector QR code generation, SHA-256 digital validation hashing, and tamper-detection verification (`/api/tickets/<pnr>/verify`).
  - `backend/app/routes/auth.py` & Security Middleware: Role-Based Access Control (`USER` vs `ADMIN`), session hardening, and parameterized SQL enforcement (`%s`).
  - `backend/tests/`: 52 automated tests across 8 comprehensive test suites achieving a 100% pass rate.
  - `PROJECT_REPORT.md` & `FINAL_TEST_REPORT.md`: Comprehensive academic project report and test matrix documentation.
- **Key Technical Responsibilities:**
  - Hardened application endpoints with role-based authorization ensuring standard users cannot access administrative APIs or view unmasked passenger records.
  - Implemented the diagnostic telemetry endpoint (`/api/admin/diagnostics`) allowing administrators to monitor database health live.
  - Designed multithreaded simulation fixtures in Pytest verifying that competing requests for the same seat commit atomically without double allocations.
