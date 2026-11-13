# RailSync 2.0 — PBL Team Roles, Responsibilities & Viva Examination Guide
## Project: Full-Stack Indian Railway Reservation System (PBL — OS & DBMS)
### Team Roster: Praful (Team Leader), Akhil, Aditya, Abhinav, Yash, Ayush (6 Members)

---

## Executive Overview of Role Distribution

To ensure clear academic division of labor, modular code ownership, and strong individual accountability during faculty project evaluations, the RailSync engineering responsibilities are distributed across **6 specialized technical roles by name**:

```text
+---------------------------------------------------------------------------------------------------+
|                                PRAFUL: TEAM LEADER & SYSTEM ARCHITECT                             |
|       Overall Architecture, Multi-Tier Integration, System Data Flow, Vite Proxy, Build Pipelines  |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
         +----------------------------------------+----------------------------------------+
         |                                                                                 |
+--------v-----------------------------------+                   +-------------------------v---------------------+
|   AKHIL: BACKEND & API SECURITY            |                   |    ADITYA: DATABASE ARCHITECT &               |
|   ENGINEER                                 |                   |    CONCURRENCY ENGINEER                       |
|   - Flask REST Blueprints (7 Modules)      |                   |    - 3NF Normalized Relational Schema         |
|   - PBKDF2 Hashing & RBAC Auth Decorators  |                   |    - Row-Level Locking (SELECT FOR UPDATE)    |
|   - ReportLab PDF Electronic Ticket Engine |                   |    - Date-Specific Seat Isolation Model       |
|   - OS Counting Semaphore Throttling       |                   |    - InnoDB ACID Transactions & Rollback      |
+--------+-----------------------------------+                   +-------------------------+---------------------+
         |                                                                                 |
+--------v-----------------------------------+                   +-------------------------v---------------------+
|   ABHINAV: NATIVE SYSTEMS &                |                   |    YASH: FRONTEND UI/UX DESIGNER &            |
|   C++ ALGORITHM ENGINEER                   |                   |    REACT COMPONENT ARCHITECT                  |
|   - C++17 Core Engine (core_logic.cpp)     |                   |    - React 19 + Vite Setup & Design Tokens    |
|   - std::mutex Memory Critical Sections    |                   |    - Midnight Navy & Saffron Travel Aesthetic |
|   - Dijkstra Shortest Path (Min-Heap)      |                   |    - Unified 3-Mode Booking Panel             |
|   - ctypes CDLL & Native CLI Bridge        |                   |    - Train Search Results & Responsive Navbar |
+--------+-----------------------------------+                   +-------------------------+---------------------+
         |                                                                                 |
         +----------------------------------------+----------------------------------------+
                                                  |
+-------------------------------------------------v-------------------------------------------------+
|                    AYUSH: INTERACTIVE BOOKING WORKFLOWS & QA / TESTING ENGINEER                   |
|       Interactive Coach Seat Map (SeatMap.jsx), Multi-Step Passenger & Payment Simulation,         |
|       Automated Pytest Suite (33 Tests), Concurrency Stress Testing & Browser E2E Verification    |
+---------------------------------------------------------------------------------------------------+
```

---

## 1. Praful — Team Leader & Full-Stack System Architect

### 1. Designation
**Team Leader & Full-Stack System Architect**

### 2. Core Domain & Repository Ownership
* **Primary Ownership**: System integration, multi-tier data pipeline, architectural cohesion, environment management, and project coordination.
* **Key Files Owned**:
  * [`frontend/vite.config.js`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/frontend/vite.config.js) (API reverse proxy configuration)
  * [`backend/main.py`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/backend/main.py) (Flask server entry point)
  * [`backend/app/__init__.py`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/backend/app/__init__.py) (Blueprint registry & CORS setup)
  * [`backend/app/config.py`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/backend/app/config.py) (Environment & connection parameterization)
  * [`README.md`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/README.md) & [`docs/PROJECT_REPORT.md`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/docs/PROJECT_REPORT.md)

### 3. Detailed Responsibilities
* Architected the entire distributed communication contract: React (port 8080) $\rightarrow$ Vite Proxy $\rightarrow$ Flask (port 5001) $\rightarrow$ MySQL 8.4 (port 3306) and C++ native DLL.
* Configured development reverse proxying in Vite to resolve cross-origin cookie restrictions, enabling secure HTTP-only session cookies.
* Defined standard JSON API response envelopes (`success`, `data`, `error`, `status_code`) across all Flask endpoints.
* Supervised the Two-Pass Execution Workflow (Pass 1 functional verification, Pass 2 UI transformation).
* Coordinated peer code reviews, resolved integration bottlenecks, and managed the production build pipeline (`npm run build`).

### 4. Spoken Viva Script: "Tell me about your role"
> *"Good morning, Professor. I am Praful, the Team Leader and Full-Stack System Architect for RailSync. My primary responsibility was designing the overall system topology and ensuring seamless end-to-end integration across our four core layers: our React 19 frontend, the Flask REST API, our MySQL 8.4 database, and the native C++ algorithm engine. A key engineering challenge I solved was configuring our Vite development reverse proxy on port 8080 to route all '/api' requests directly to our Flask backend on port 5001. This eliminated browser CORS preflight overhead and allowed our session authentication cookies to function without domain mismatches. I also parameterized our environment configuration, managed our production build pipeline, and ensured our team met all academic deadlines with zero mock data."*

### 5. Top 5 Technical Viva Questions & Answers for Praful
* **Q1: Why did you choose a Vite reverse proxy instead of standard Flask-CORS headers?**
  * *Answer:* While Flask-CORS works, relying solely on it in development triggers browser CORS preflight OPTIONS requests for every credentialed API call, adding unnecessary network roundtrips. By configuring a reverse proxy in Vite (port 8080 forward to port 5001), the browser considers frontend and backend identical-origin, simplifying cookie session dispatch and matching real-world Nginx production setups.
* **Q2: How does RailSync handle the bridge between interpreted Python and native C++?**
  * *Answer:* We implemented a dual-bridge architecture. The primary bridge uses Python's standard `ctypes` module to load our compiled engine shared library (`core_logic.dll`) directly into memory. For environments without dynamic loading permissions, we implemented a fallback bridge via the Python `subprocess` module invoking `engine_cli.exe` with structured JSON arguments.
* **Q3: How are application secrets and database credentials managed?**
  * *Answer:* All connection strings, ports, and secret keys are isolated in `backend/app/config.py`, which pulls directly from environment variables. This prevents hardcoding credentials in source code and prepares the app for containerization in Phase 3.
* **Q4: What was the hardest architectural challenge you solved as Team Leader?**
  * *Answer:* Synchronizing state across multiple independent technologies. Specifically, ensuring that when a seat is reserved through the React UI, the database row is locked at the MySQL InnoDB engine level, the C++ mutex synchronizes memory, and the session cookie updates atomically without leaving orphaned records.
* **Q5: How did you verify that the entire system was production-ready?**
  * *Answer:* We established an automated testing workflow using Pytest with 33 comprehensive unit and integration tests. In addition, I verified that our frontend compiles cleanly via `npm run build` in 750ms with zero bundling errors.

---

## 2. Akhil — Backend & API Security Engineer

### 1. Designation
**Backend & API Security Engineer**

### 2. Core Domain & Repository Ownership
* **Primary Ownership**: Flask REST API design, user authentication & role-based authorization, vector PDF ticket generation, and Operating System resource throttling via counting semaphores.
* **Key Files Owned**:
  * [`backend/app/routes/auth.py`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/backend/app/routes/auth.py) (Login, registration, password hashing)
  * [`backend/app/routes/admin.py`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/backend/app/routes/admin.py) (Fleet management, schedule updates)
  * [`backend/app/routes/os_dbms.py`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/backend/app/routes/os_dbms.py) (Live system telemetry & concurrency diagnostics)
  * [`backend/app/services/pdf_service.py`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/backend/app/services/pdf_service.py) (ReportLab PDF generation engine)
  * [`backend/app/middleware.py`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/backend/app/middleware.py) (Request validation, session guards, counting semaphores)

### 3. Detailed Responsibilities
* Structured the entire backend into 7 decoupled Flask Blueprints: `auth_bp`, `trains_bp`, `bookings_bp`, `stations_bp`, `admin_bp`, `os_dbms_bp`, and `pdf_bp`.
* Engineered password security using PBKDF2 (Password-Based Key Derivation Function 2) with SHA-256 and unique cryptographic salt, protecting credentials against rainbow table attacks.
* Created custom security decorators: `@login_required` to guard passenger endpoints and `@admin_required` for role-based administrative control.
* Implemented the vector PDF Electronic Reservation Slip (ERS) generator using ReportLab, creating authentic railway ticket layouts with passenger tables and verification metadata.
* Integrated an **OS Counting Semaphore (`threading.Semaphore(10)`)** to throttle heavy PDF generation ingress, preventing server CPU exhaustion and Denial of Service (DoS) during high-concurrency ticket downloads.

### 4. Spoken Viva Script: "Tell me about your role"
> *"Good morning, Professor. I am Akhil, and my role in the project was Backend and API Security Engineer. I was responsible for designing and building our modular RESTful API architecture in Python Flask, structured across seven distinct Blueprints to ensure clean separation of concerns. On the security side, I implemented user authentication using PBKDF2 with SHA-256 and unique cryptographic salt, alongside custom decorators like '@login_required' and '@admin_required' for Role-Based Access Control. One of my key Computer Science implementations was solving the server overload problem during ticket downloads: vector PDF creation is CPU and memory intensive, so I wrapped our ReportLab ticket generation engine inside an OS counting semaphore with a capacity of 10 threads. This guarantees that during peak booking surges, surplus requests block cleanly in the OS wait queue instead of exhausting system memory or crashing the backend."*

### 5. Top 5 Technical Viva Questions & Answers for Akhil
* **Q1: Why did you use PBKDF2 instead of plain SHA-256 or MD5 for password storage?**
  * *Answer:* Standard hash functions like MD5 or raw SHA-256 are designed to be fast, which makes them vulnerable to brute-force attacks computed on modern GPUs at billions of hashes per second. PBKDF2 applies a cryptographic key derivation function with thousands of iterations and a unique per-user salt, introducing intentional computational cost that makes dictionary and rainbow table attacks computationally infeasible.
* **Q2: How does an OS counting semaphore work in your PDF ticket service?**
  * *Answer:* We instantiate `threading.Semaphore(10)`. When a passenger requests their PDF ticket, the worker thread must execute `semaphore.acquire()`. If 10 tickets are already actively being rendered, the 11th thread is placed into a blocked/waiting state by the operating system scheduler. Once any active thread finishes and calls `semaphore.release()`, the OS unblocks the next waiting thread. This caps peak CPU utilization and prevents out-of-memory crashes.
* **Q3: How do you enforce Role-Based Access Control (RBAC) in your Flask routes?**
  * *Answer:* We built custom Python wrapper decorators. The `@admin_required` decorator intercepts incoming HTTP requests, inspects the server-side session dictionary for `user_id`, checks the `users` table for `role == 'admin'`, and immediately aborts with an HTTP 403 Forbidden status if an unauthorized user attempts to access fleet management or train delay controls.
* **Q4: How did you structure your API response contracts across all 7 Blueprints?**
  * *Answer:* Every endpoint returns a consistent JSON envelope containing `success` (boolean), `data` (payload or null), and `error` (descriptive error message or null), accompanied by proper HTTP status codes (200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 500 Internal Error). This makes client-side handling in Axios predictable and robust.
* **Q5: What is the purpose of the `/api/os-dbms/` telemetry routes you created?**
  * *Answer:* They provide live diagnostic telemetry showing the real-time state of backend concurrency primitives—such as active database connection pool counts, semaphore permit availability, producer-consumer buffer depth, and C++ engine execution timings—allowing faculty and evaluators to observe operating system concepts in action.

---

## 3. Aditya — Database Architect & Concurrency Engineer

### 1. Designation
**Database Architect & Concurrency Engineer**

### 2. Core Domain & Repository Ownership
* **Primary Ownership**: Relational database architecture, 3NF schema design, pessimistic row-level locking, calendar-to-seat isolation, and ACID transaction safety.
* **Key Files Owned**:
  * [`backend/database/schema.sql`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/backend/database/schema.sql) (10-table 3NF schema definition)
  * [`backend/database/seed.sql`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/backend/database/seed.sql) (Production railway network seed data)
  * [`backend/app/database.py`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/backend/app/database.py) (MySQL connection pooling & context managers)
  * [`backend/app/routes/bookings.py`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/backend/app/routes/bookings.py) (Row-level lock queries & ACID rollback logic)

### 3. Detailed Responsibilities
* Normalized the relational database into Third Normal Form (3NF) across 10 tables, eliminating transitive and partial dependencies.
* Designed the date-specific seat isolation model using a composite unique constraint: `UNIQUE KEY uk_seat_date (seat_id, journey_date)` in `seat_allocations`.
* Implemented pessimistic concurrency control using `SELECT ... FOR UPDATE` in MySQL InnoDB, preventing the classic double-booking race condition.
* Enforced ACID transaction boundaries: bundling passenger insertion, allocation recording, and fare calculation into an atomic transaction with instant rollback on payment failure.
* Configured thread-safe MySQL connection pooling (`mysql.connector.pooling.MySQLConnectionPool`) to handle concurrent database requests efficiently.

### 4. Spoken Viva Script: "Tell me about your role"
> *"Good morning, Professor. I am Aditya, the Database Architect and Concurrency Engineer for RailSync. My role was designing our relational schema across 10 tables normalized to Third Normal Form (3NF) on MySQL 8.4 InnoDB. One of the core problems I solved was the calendar seat isolation challenge: in a real railway, a coach has a static set of physical berths that must be reservable for different dates without duplicating physical schema rows. I decoupled physical berths in the 'seats' table from reservations in 'seat_allocations' using a composite constraint: UNIQUE KEY uk_seat_date (seat_id, journey_date). To prevent race conditions when two users click the same berth simultaneously, I implemented pessimistic concurrency control using 'SELECT ... FOR UPDATE'. This instructs the InnoDB engine to lock candidate rows at the index level until the transaction commits, backed by automatic rollback if payment fails."*

### 5. Top 5 Technical Viva Questions & Answers for Aditya
* **Q1: How does `SELECT ... FOR UPDATE` prevent double bookings in MySQL InnoDB?**
  * *Answer:* When Transaction A executes `SELECT ... FOR UPDATE` on candidate seat rows, InnoDB places an exclusive lock on those specific index records. If concurrent Transaction B attempts to select or reserve those same rows, InnoDB forces Transaction B to wait until Transaction A commits or rolls back, completely eliminating race conditions.
* **Q2: Why is the composite constraint `UNIQUE KEY uk_seat_date (seat_id, journey_date)` necessary?**
  * *Answer:* Without this constraint, either physical seats would have to be duplicated for every day in the calendar (exploding table size), or multiple passengers could be booked for different dates without constraint enforcement. This constraint ensures that physical seats stay static, while each physical berth can be allocated at most once per journey date.
* **Q3: What happens in the database if a passenger's payment fails?**
  * *Answer:* All booking steps occur inside an explicit database transaction block. If payment fails, the backend issues `connection.rollback()`. MySQL InnoDB utilizes its rollback segment (`undo log`) to reverse all inserts, immediately releasing row locks and restoring seat availability with zero orphan records.
* **Q4: How did you ensure your schema satisfies Third Normal Form (3NF)?**
  * *Answer:* 1NF is satisfied because all columns contain atomic values. 2NF is satisfied because non-prime attributes depend on the entire primary key. 3NF is satisfied because transitive dependencies are eliminated by separating junction stations, coaches, routes, and bookings into independent reference tables.
* **Q5: Which database indexes did you create and what query performance did you achieve?**
  * *Answer:* We built B-Tree composite indexes: `idx_search` on `(source_id, dest_id, day_of_week)` for sub-5ms train search, `idx_pnr` on `pnr_number` for instant ticket lookups, and `idx_journey` on `journey_date` for fast seat occupancy checks.

---

## 4. Abhinav — Native Systems & C++ Algorithm Engineer

### 1. Designation
**Native Systems & C++ Algorithm Engineer**

### 2. Core Domain & Repository Ownership
* **Primary Ownership**: High-performance C++17 native engine, hardware-speed shortest path calculations, thread-safe memory allocation, and ctypes/CLI bridges.
* **Key Files Owned**:
  * [`backend/cpp_engine/core_logic.cpp`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/backend/cpp_engine/core_logic.cpp) (Dijkstra graph engine & mutex seat allocator)
  * [`backend/cpp_engine/engine_cli.cpp`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/backend/cpp_engine/engine_cli.cpp) (Dynamic CLI interface & JSON serialization)
  * [`backend/app/services/cpp_service.py`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/backend/app/services/cpp_service.py) (Python ctypes & subprocess bridge)

### 3. Detailed Responsibilities
* Developed the native C++17 algorithm engine, compiling with `-O3` optimizations for sub-millisecond execution.
* Implemented Dijkstra's shortest path algorithm over a dynamic railway adjacency list using a `std::priority_queue` min-heap ($O((V+E)\log V)$).
* Engineered memory mutual exclusion using `std::mutex` and `std::lock_guard` to protect shared coach berth arrays during contiguous window seat allocations.
* Built cross-language integration: a high-speed ctypes shared library bridge (`core_logic.dll`) and a dynamic CLI fallback bridge (`engine_cli.exe`).
* Handled edge cases including unreachable network nodes, cyclic paths, and disconnected subgraphs.

### 4. Spoken Viva Script: "Tell me about your role"
> *"Good morning, Professor. I am Abhinav, the Native Systems and C++ Algorithm Engineer. My responsibility was developing our compiled C++17 native engine to execute computationally heavy algorithms at bare-metal hardware speeds. I implemented two core Computer Science concepts: first, thread-safe memory management using C++ 'std::mutex' and 'std::lock_guard' to protect shared seat buffers from race conditions during contiguous window seat allocations. Second, I implemented Dijkstra's shortest path algorithm using an adjacency list and a 'std::priority_queue' min-heap, achieving an optimal time complexity of O((V + E) log V) across our 56-junction railway graph. I bridged these C++ functions into our Python backend using both ctypes shared library loading and a fast CLI bridge."*

### 5. Top 5 Technical Viva Questions & Answers for Abhinav
* **Q1: Why use C++ instead of performing pathfinding and allocation directly in Python?**
  * *Answer:* Python is an interpreted language with a Global Interpreter Lock (GIL) and significant object overhead. In high-concurrency booking scenarios where millions of graph evaluations and memory buffers are inspected per second, C++ compiles directly to machine code, provides zero-cost abstractions, and allows fine-grained memory management without garbage collection pauses.
* **Q2: Explain the time complexity of your Dijkstra implementation.**
  * *Answer:* We represent the railway network as an adjacency list of vertices (stations) and weighted edges (track distances). By using a min-heap priority queue (`std::priority_queue` with `std::greater`), extracting the minimum distance vertex takes $O(\log V)$, and relaxing neighbor distances takes $O(E \log V)$. This yields a total time complexity of $O((V + E) \log V)$, which is asymptotically optimal for sparse graphs.
* **Q3: How does `std::lock_guard` guarantee exception-safe mutual exclusion?**
  * *Answer:* `std::lock_guard` implements the RAII (Resource Acquisition Is Initialization) pattern. Upon construction, it acquires the mutex; upon destruction—whether the function completes normally or an exception is thrown—the destructor automatically releases the mutex, preventing deadlocks caused by unreleased locks.
* **Q4: How does your contiguous seat allocator work?**
  * *Answer:* It iterates through coach seat matrices looking for consecutive unoccupied seats with window berth attributes. Because multiple passenger booking threads may query this function simultaneously, the critical search-and-reserve loop is enclosed in an `std::mutex` lock guard to ensure atomic state updates.
* **Q5: How did you handle unreachable or disconnected stations in your C++ graph?**
  * *Answer:* If the priority queue empties without reaching the destination node, the distance remains set to infinity (`INT_MAX`). The C++ engine detects this condition, returns a distance of -1, and outputs an empty path array with an appropriate error flag, which the Python backend cleanly translates into an HTTP 404 response.

---

## 5. Yash — Frontend UI/UX Designer & React Component Architect

### 1. Designation
**Frontend UI/UX Designer & React Component Architect**

### 2. Core Domain & Repository Ownership
* **Primary Ownership**: React 19 component hierarchy, Tailwind CSS v4 design tokens, railway visual aesthetic, and unified booking search panels.
* **Key Files Owned**:
  * [`frontend/src/index.css`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/frontend/src/index.css) (Design tokens, midnight navy & saffron palette)
  * [`frontend/src/pages/Home.jsx`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/frontend/src/pages/Home.jsx) (Unified 3-mode booking panel & hero banner)
  * [`frontend/src/components/TrainCard.jsx`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/frontend/src/components/TrainCard.jsx) (Responsive train cards & dynamic fare badges)
  * [`frontend/src/components/Navbar.jsx`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/frontend/src/components/Navbar.jsx) (Navigation, active session status & auth modal trigger)

### 3. Detailed Responsibilities
* Rebuilt the entire user interface using React 19 and Tailwind CSS v4, adhering to modern travel web design standards.
* Established the RailSync visual identity: deep midnight-navy surfaces (`#0B132B`, `#1C2541`), railway saffron accents (`#EA580C`), and Inter typography.
* Built the unified 3-mode booking search panel supporting Train Ticket Search, 10-digit PNR Tracking, and Live Station Status queries without page reloads.
* Completely eliminated hardcoded frontend station lists by connecting search inputs dynamically to `/api/stations` with debounced search filtering.
* Designed responsive train search listing cards with live class availability badges (SL, 3A, 2A, 1A) and journey duration calculators.

### 4. Spoken Viva Script: "Tell me about your role"
> *"Good morning, Professor. I am Yash, the Frontend UI/UX Designer and React Component Architect for RailSync. My goal was transforming our application from a basic college prototype into a modern, production-grade travel platform inspired by modern web design standards. I built our component hierarchy using React 19 and Tailwind CSS v4, establishing an authentic Indian railway aesthetic featuring midnight-navy surfaces and railway saffron accents. I engineered our central 3-mode booking panel, which allows travelers to seamlessly toggle between Train Search, 10-digit PNR Tracking, and Live Station Status without page reloads. I also eliminated all hardcoded mockups by connecting our station dropdowns directly to our backend MySQL database via live Axios requests."*

### 5. Top 5 Technical Viva Questions & Answers for Yash
* **Q1: Why did you choose Tailwind CSS v4 over traditional CSS or component libraries?**
  * *Answer:* Tailwind CSS v4 introduces CSS-first configuration with native CSS variables and lightning-fast compilation via the Oxide engine. It allowed us to define customized design tokens for our midnight-navy and saffron color palette with zero CSS bundle bloat, ensuring sub-second page loads.
* **Q2: How did you eliminate mock data in the frontend station dropdowns?**
  * *Answer:* In previous iterations, station dropdowns used hardcoded JavaScript arrays. I refactored the station inputs to fetch directly from our backend `/api/stations` endpoint upon component mount via Axios. As the user types, the list filters dynamically against real MySQL records with station codes and junction names.
* **Q3: How does your unified 3-mode booking panel manage tab switching?**
  * *Answer:* The panel uses local React state (`activeTab`) to conditionally render either the Train Search form, the 10-digit PNR tracking input, or the Live Station query interface within a single cohesive container, providing an intuitive experience without full page reloads.
* **Q4: How do the train listing cards display dynamic class availability?**
  * *Answer:* Each train card receives pricing and availability objects mapped directly from the backend. The card renders responsive badges for Sleeper (SL), 3rd AC (3A), 2nd AC (2A), and 1st AC (1A), showing dynamic pricing and availability indicators based on real database records.
* **Q5: How did you ensure responsive design across mobile and desktop viewports?**
  * *Answer:* I used Tailwind's mobile-first responsive utility classes (e.g., `grid-cols-1 md:grid-cols-3`, `flex-col md:flex-row`). Interactive cards, navigation bars, and forms automatically adapt their flex and grid directions based on screen width.

---

## 6. Ayush — Interactive Booking Workflows & QA / Testing Engineer

### 1. Designation
**Interactive Booking Workflows & QA / Testing Engineer**

### 2. Core Domain & Repository Ownership
* **Primary Ownership**: Interactive coach seat map visualization, multi-step passenger checkout workflow, simulated payment gateway, and automated test suite.
* **Key Files Owned**:
  * [`frontend/src/components/SeatMap.jsx`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/frontend/src/components/SeatMap.jsx) (Interactive SVG coach berth map)
  * [`frontend/src/pages/TrainDetails.jsx`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/frontend/src/pages/TrainDetails.jsx) (Coach class selection & seat selection flow)
  * [`frontend/src/pages/Payment.jsx`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/frontend/src/pages/Payment.jsx) (Simulated payment gateway & confirmation)
  * [`backend/tests/`](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/backend/tests/) (Complete automated Pytest suite across 33 tests)

### 3. Detailed Responsibilities
* Developed the interactive coach seat map in `SeatMap.jsx`, visually rendering Lower, Middle, Upper, and Side berths with color-coded states (Available, Selected, Booked).
* Engineered the multi-step checkout workflow: Train Selection $\rightarrow$ Seat Selection $\rightarrow$ Passenger Details $\rightarrow$ Payment Simulation $\rightarrow$ PNR Issuance.
* Built the simulated payment gateway modal supporting UPI, Credit/Debit Cards, and NetBanking with deterministic success and failure toggles to demonstrate ACID rollback.
* Authored the automated Pytest test suite with **33 test cases (100% pass rate)**, verifying authentication, concurrency locking, ACID rollbacks, and Dijkstra graph pathfinding.
* Performed browser end-to-end testing, confirming sub-second response times and zero UI glitches.

### 4. Spoken Viva Script: "Tell me about your role"
> *"Good morning, Professor. I am Ayush, the Interactive Booking Workflows and QA / Testing Engineer. My focus was building the critical passenger checkout workflow and verifying our application through automated quality assurance. I developed our interactive coach seat map in 'SeatMap.jsx', which visually renders physical coach layouts—including Lower, Middle, Upper, and Side berths—with real-time color coding for Available, Selected, and Booked states. I also engineered our payment simulation modal with toggles to demonstrate atomic commits and rollbacks. On the testing side, I authored our comprehensive automated Pytest suite with 33 test cases covering database row locks, ACID rollback, Dijkstra pathfinding, and counting semaphores, achieving a 100% test pass rate in 1.21 seconds."*

### 5. Top 5 Technical Viva Questions & Answers for Ayush
* **Q1: How does the interactive seat map fetch and display real-time berth availability?**
  * *Answer:* When a user selects a train and date, the component queries `/api/trains/{id}/seats?date={journey_date}`. The backend joins physical seats with existing allocations for that specific date. The seat map renders berths in green for available, red for booked, and amber when selected by the current user, updating state dynamically.
* **Q2: How did you test row-level concurrency in your automated test suite?**
  * *Answer:* In `test_bookings.py`, we simulate concurrent booking attempts using multi-threaded test requests targeting the exact same seat and date. We assert that exactly one booking succeeds with HTTP 201, while the competing request receives an HTTP 400 error indicating the berth has already been allocated.
* **Q3: How did you verify ACID rollback behavior during test execution?**
  * *Answer:* We created automated test cases where a booking is initiated with an intentional payment gateway failure flag. The test verifies that the HTTP response is 400, no passenger records remain in the database, and the candidate seat remains 100% available for subsequent bookings.
* **Q4: What user feedback is provided during payment processing?**
  * *Answer:* The payment component features a multi-method modal supporting UPI, Credit/Debit Cards, and NetBanking. During submission, an interactive loading spinner informs the passenger of bank verification, and upon confirmation, the user is automatically redirected to the Ticket Confirmation page with their generated 10-digit PNR.
* **Q5: How many test cases are in the automated test suite and what do they cover?**
  * *Answer:* The suite contains 33 automated tests covering: User Registration and Login (4 tests), Station and Schedule APIs (6 tests), Train Search and Filters (5 tests), Database Row Locking and ACID Rollbacks (6 tests), C++ Dijkstra Shortest Path and Graph Routing (6 tests), and OS Counting Semaphore Throttling (6 tests). All 33 pass in 1.21 seconds.

---

## 7. Recommended Team Live Presentation Sequence for Faculty Evaluation

To deliver a seamless, coordinated 10-to-15 minute live demonstration during PBL evaluation, the team should present in this sequential order:

1. **Praful (Team Leader & System Architect):** Opens the architecture diagram, explains the 4-tier topology, and shows the Vite reverse proxy running on port 8080 connecting to Flask on port 5001.
2. **Yash (Frontend UI/UX Architect):** Demonstrates the home page travel aesthetic, live station search dropdowns, and executes a real search between New Delhi and Mumbai Central.
3. **Ayush (Interactive Workflows):** Clicks a train card, opens the interactive coach seat map (`SeatMap.jsx`), selects berths, fills passenger details, and opens the payment modal.
4. **Aditya (Database Architect):** Explains the row-level lock (`SELECT ... FOR UPDATE`) taking place in MySQL, the date-specific allocation table, and initiates simulated payment success to generate the PNR.
5. **Abhinav (Native Systems Engineer):** Demonstrates the C++ algorithm engine executing Dijkstra's shortest path across the 56-junction railway graph and explains `std::mutex` memory protection.
6. **Akhil (Backend & API Security):** Downloads the generated vector PDF ticket slip, shows the OS counting semaphore throttling the generation, and demonstrates PNR lookup.
7. **Ayush & Team:** Runs the automated Pytest test suite in terminal showing 33 passing tests (100% pass rate) and summarizes Phase 3 cloud expansion plans.
