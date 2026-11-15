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
| 3 | **Aditya** | **Frontend Architect & UI/UX Lead** | React 18 SPA & Interactive UI | Search filters, Coach Seat Map, Checkout modal, PNR inquiry |
| 4 | **Vedansh** | **Database Architect** | MySQL 8.4 Schema & Concurrency | 14 InnoDB tables, Row locking (`FOR UPDATE`), 206 stops dataset |
| 5 | **Yash** | **Systems & Algorithms Engineer** | C++17 Dijkstra Engine & OS Mutex | Min-Heap shortest path, Contiguous allocator, Python `ctypes` bridge |
| 6 | **Abhinav** | **QA Lead & Documentation Specialist** | Automated Testing & Project Report | 52 Pytest automated tests, Concurrency verification, Project Report |

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
- **Viva / Defense Topics to Present:**
  - Multi-stage Docker build benefits (reducing bundle sizes from 600MB+ to lightweight ~30MB alpine images).
  - Reverse proxy benefits: routing frontend and API under a single origin to eliminate browser CORS overhead.
  - Container health check sequencing and graceful startup dependencies.

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
  - `backend/app/routes/auth.py`: Session authentication, user profile management, and password hashing (`werkzeug.security`).
- **Key Technical Responsibilities:**
  - Overhauled Step 4 Payment Authorization to prevent race conditions and duplicate booking submissions.
  - Designed backend-authoritative fare calculation ensuring client cannot tamper with pricing.
  - Implemented CPU protection bounded semaphores to prevent Denial of Service during PDF generation.
- **Viva / Defense Topics to Present:**
  - REST API architectural principles and HTTP status code semantics (200, 201, 400, 401, 403, 404, 409).
  - Idempotent request handling: how unique `idempotency_key` tokens prevent duplicate charges during network lag.
  - Atomicity in booking creation: why booking, payment, and seat locking must execute within the same database transaction.

---

### 2.3 Aditya (Frontend Architect & UI/UX Specialist)
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
- **Viva / Defense Topics to Present:**
  - React 18 component lifecycle, hooks (`useState`, `useEffect`, `useCallback`, `useMemo`), and React Router v7 navigation.
  - Client state machine management during payment processing to prevent duplicate form submission.
  - Asynchronous HTTP communication with Axios and centralized error handling with toast notifications.

---

### 2.4 Vedansh (Database Architect & SQL Concurrency Engineer)
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
- **Viva / Defense Topics to Present:**
  - ACID properties (Atomicity, Consistency, Isolation, Durability) in MySQL InnoDB.
  - Pessimistic concurrency control vs optimistic concurrency control, and how `SELECT ... FOR UPDATE` prevents race conditions.
  - Foreign key constraints with `ON DELETE CASCADE` and `RESTRICT` to protect referential integrity.

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
- **Viva / Defense Topics to Present:**
  - Dijkstra shortest path time complexity: $\mathcal{O}((V + E) \log V)$ using a binary min-heap versus $\mathcal{O}(V^2)$ with simple arrays.
  - Hardware-level mutual exclusion (`std::mutex`) and Critical Section management in C++17.
  - In-process native code execution: how Python `ctypes` directly loads shared libraries into the process address space.

---

### 2.6 Abhinav (QA Lead & Documentation Specialist)
- **Role:** Quality Assurance, Test Automation & Technical Documentation Lead
- **Source Code & Files Owned:**
  - `backend/tests/`: Complete automated test suite containing 52 unit, integration, and stress tests:
    - `test_admin.py`: Fleet management, station CRUD, diagnostics, and RBAC authorization (6 tests).
    - `test_advanced_features.py`: Fares, timetable stops, refunds, and QR code streams (8 tests).
    - `test_auth.py`: Password hashing, session security, and unauthorized endpoint rejection (5 tests).
    - `test_bookings.py`: End-to-end booking flow, competing seat reservations, and PNR masking (4 tests).
    - `test_concurrency.py`: InnoDB ACID rollback and simultaneous row-level locking (2 tests).
    - `test_cpp_engine.py`: Dijkstra edge cases, unreachable nodes, contiguous allocator, and mutex lock verification (11 tests).
    - `test_payment_refinements.py`: Payment success/decline, idempotency, and intermediate stops (5 tests).
    - `test_trains.py`: Station APIs, multi-category search, and seat map layout (11 tests).
  - `PROJECT_REPORT.md`: Comprehensive academic project report.
  - `FINAL_TEST_REPORT.md`: Complete test execution matrix with logs and verification evidence.
  - `SETUP_GUIDE.md`: Step-by-step installation instructions for Docker and bare-metal setups.
  - `docs/screenshots/`: High-resolution live application screenshots.
- **Key Technical Responsibilities:**
  - Designed and executed 52 automated tests in Pytest achieving 100% pass rate.
  - Conducted concurrent booking stress tests simulating two passengers attempting to book the exact same seat simultaneously.
  - Prepared the complete academic project documentation and submission package.
- **Viva / Defense Topics to Present:**
  - Test automation methodology: unit testing, integration testing, and concurrency regression testing.
  - Simulating race conditions in automated tests using Python threads and transactional clients.
  - Verification of data masking for passenger privacy compliance.

---

## 3. Quick Reference for Viva / Presentation Allocation

| Viva Question / Evaluation Topic | Best Member to Answer | Relevant Code / File |
|---|---|---|
| **Docker, Nginx Reverse Proxy & Container Networking** | **Umanga** | `docker-compose.yml`, `frontend/nginx.conf` |
| **Flask REST Architecture, Payment Simulation & Fares** | **Akhil** | `backend/app/routes/payments.py`, `fare_service.py` |
| **React SPA Architecture, Seat Map & UI State Machine** | **Aditya** | `frontend/src/pages/TrainDetails.jsx`, `Payment.jsx` |
| **MySQL InnoDB Transactions, Concurrency & Row Locks** | **Vedansh** | `database/schema.sql`, `booking_service.py` |
| **Dijkstra Graph Algorithm, C++17 Engine & Mutex** | **Yash** | `backend/cpp_engine/core_logic.cpp`, `cpp_engine_service.py` |
| **Testing Suite, Concurrency Verification & Test Matrix** | **Abhinav** | `backend/tests/`, `FINAL_TEST_REPORT.md` |
