# RailSync 2.0 — OS & DBMS Academic Implementation Mapping

> **Prepared for College Project-Based Learning (PBL) Viva & Technical Evaluation**  
> *Demonstrating Operating Systems (OS) Primitives and Database Management System (DBMS) Guarantees in Live Production Code.*

---

## 1. Executive Summary

RailSync is not a visual mockup or simple CRUD portal. The entire system is engineered to manifest core Computer Science principles in actual running workflows:
* **Operating Systems**: Native C++ mutual exclusion (`std::mutex`), graph algorithms with min-heap priority queues (Dijkstra $O((V+E)\log V)$), counting semaphores for throttling, bounded producer-consumer queues, and deterministic priority scheduling.
* **DBMS**: Third Normal Form (3NF) relational schema, MySQL 8.4 InnoDB transactional boundaries, strict Foreign Key referential integrity, row-level locking (`SELECT ... FOR UPDATE`), B-Tree composite indexing, connection pooling, and ACID atomicity with automatic rollback.

---

## 2. Operating Systems (OS) Concepts Mapping

| Academic Concept | System Workflow / Feature | Implementation File | Low-Level Mechanism / Data Structure | Viva Explanation / Demonstration |
| :--- | :--- | :--- | :--- | :--- |
| **Critical Section & Mutual Exclusion** | Native Shared Seat Allocator & Request Counter | `backend/cpp_engine/core_logic.cpp`<br>`backend/cpp_engine/core_logic.h` | `std::mutex g_alloc_mutex;`<br>`std::lock_guard<std::mutex> lock(g_alloc_mutex);` | When concurrent booking requests hit the C++ allocation engine, the mutex ensures only one thread executes the contiguous seat search heuristic at a time. Verified in `test_seat_allocation_contiguous_preference`. |
| **Shortest-Path Graph Search** | Network Route Planning & Intermediate Hops | `backend/cpp_engine/core_logic.cpp`<br>`backend/app/services/train_service.py` | Dijkstra's algorithm implemented with `std::priority_queue` min-heap over adjacency list. Time complexity $O((V+E)\log V)$. | Integrated directly into the homepage booking panel ("Plan Route" tab) and `/api/trains/shortest-path`. Computes shortest corridor distance in km across stations. |
| **Deadlock Prevention (Hierarchical Ordering)** | Multi-Seat Row-Lock Acquisition | `backend/app/services/booking_service.py` | Strictly ordered lock acquisition: `ORDER BY s.id ASC` before `FOR UPDATE`. | Prevents circular wait deadlock conditions when multiple concurrent transactions attempt to book overlapping seat sets. |
| **Counting Semaphore** | PDF Electronic Ticket Ingress Throttling | `backend/app/services/os_demonstrations.py` | `threading.Semaphore(value=10)` | Restricts concurrent vector PDF ReportLab generation jobs to 10 active tasks, preventing CPU starvation and out-of-memory states under heavy load. |
| **Bounded Buffer (Producer-Consumer)** | Asynchronous Ticket Generation Pipeline | `backend/app/services/os_demonstrations.py` | Thread-safe `queue.Queue(maxsize=50)` with worker threads calling `task_done()` and condition variable signaling. | Simulates an asynchronous background ticket processing pipeline where booking requests are enqueued and consumed by worker threads. |
| **Priority Scheduling** | Quota-Based Request Dispatching | `backend/app/services/os_demonstrations.py` | `queue.PriorityQueue` storing `(priority_level, sequence_counter, payload)` tuples. | Guarantees higher-priority reservation requests (e.g., Emergency / Tatkal) preempt standard General requests, using sequence counters for deterministic FIFO tie-breaking. |

---

## 3. Database Management System (DBMS) Concepts Mapping

| Academic Concept | System Workflow / Feature | Implementation File | Low-Level SQL / Database Primitives | Viva Explanation / Demonstration |
| :--- | :--- | :--- | :--- | :--- |
| **3NF Relational Normalization** | Relational Database Schema Architecture | `backend/migrations/001_initial_schema.sql` | 10 normalized tables (`users`, `stations`, `trains`, `coaches`, `seats`, `routes`, `bookings`, `passengers`, `tickets`, `seat_allocations`). | Zero transitive functional dependencies, primary keys, explicit Foreign Key cascading constraints. |
| **Row-Level Locking (Pessimistic Concurrency)** | Preventing Double-Bookings & Race Conditions | `backend/app/services/booking_service.py` (lines 48–64) | `SELECT s.id, ... FROM seats s ... FOR UPDATE;` executed inside an open transaction. | When two users simultaneously attempt to book the last seat, the first transaction acquires an exclusive row lock. The second transaction blocks or re-reads available seats, eliminating double allocation. Verified in `test_row_level_locking_concurrency`. |
| **Date-Specific Seat Allocation Model** | Reusable Physical Seats Across Calendar Dates | `backend/migrations/001_initial_schema.sql` (lines 101–114) | Table `seat_allocations` with constraint: `UNIQUE KEY uk_seat_date (seat_id, journey_date)`. | A train coach seat (e.g., Coach C1, Seat 1) is a static asset. The date-specific uniqueness constraint ensures seat 1 can be reserved on October 25 and independently reserved on October 26 without modifying the physical seat row. |
| **ACID Atomicity & Rollback** | Transaction Failure Recovery | `backend/app/database/connection.py`<br>`backend/app/services/booking_service.py` | Context manager `get_db_transaction()` with `conn.start_transaction()`, explicit `conn.commit()`, and `conn.rollback()` on exception. | If a payment simulation fails, network drops, or seat constraint fails halfway, all intermediate insertions into `bookings`, `passengers`, and `seat_allocations` are rolled back atomically. Verified in `test_innodb_acid_rollback`. |
| **B-Tree Indexing & Query Plans** | Accelerated Train Search & PNR Lookup | `backend/migrations/001_initial_schema.sql` | `CREATE INDEX idx_train_search ON trains (source_station_id, destination_station_id, is_active);`<br>`CREATE INDEX idx_bookings_pnr ON bookings (pnr);` | Ensures index scans instead of full table scans ($O(\log N)$ lookup speed). |
| **Connection Pooling** | Resource Recycling & Connection Lifecycle | `backend/app/database/connection.py` | `mysql.connector.pooling.MySQLConnectionPool(pool_size=10, pool_reset_session=True)` | Manages a persistent pool of 10 database connections, eliminating the latency of repeated TCP handshakes and authentications. |

---

## 4. Key Source Code References for Viva Examination

* **C++ Engine & std::mutex**: [backend/cpp_engine/core_logic.cpp](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/backend/cpp_engine/core_logic.cpp)
* **C++ Engine Header ABI**: [backend/cpp_engine/core_logic.h](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/backend/cpp_engine/core_logic.h)
* **Dijkstra Shortest Path Integration**: [backend/app/services/train_service.py](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/backend/app/services/train_service.py#L300-L367)
* **Transactional Seat Allocation with FOR UPDATE**: [backend/app/services/booking_service.py](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/backend/app/services/booking_service.py#L34-L167)
* **ACID Connection Pool & Transaction Manager**: [backend/app/database/connection.py](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/backend/app/database/connection.py#L12-L95)
* **Relational 3NF SQL Schema**: [backend/migrations/001_initial_schema.sql](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/backend/migrations/001_initial_schema.sql)
* **Concurrency & ACID Automated Tests**: [backend/tests/test_concurrency.py](file:///c:/Users/akhil/OneDrive/Documents/PROJECTS/pbl%20os%20and%20dbms/backend/tests/test_concurrency.py)

---

## 5. Automated Verification Test Suite

To demonstrate these mechanisms to evaluators:

```powershell
$env:PYTHONPATH="backend"
.\backend\venv\Scripts\pytest.exe -v backend\tests
```

Every test verifies a concrete OS or DBMS guarantee with zero mock data.
