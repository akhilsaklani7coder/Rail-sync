# Operating System & DBMS Concepts Mapping

This document provides an academic mapping between theoretical Computer Science concepts and their concrete implementation within RailSync.

---

## Operating Systems Concept Mapping

| Academic Concept | RailSync Application Feature | Source File | Mechanism / Algorithm | Verification / Demonstration Method |
| :--- | :--- | :--- | :--- | :--- |
| **Critical Section & Mutual Exclusion** | C++ Shared Seat Allocator & Counter Guard | `backend/cpp_engine/core_logic.cpp`, `core_logic.h` | `std::mutex` / Win32 `CRITICAL_SECTION` with RAII lock guard | `backend/tests/test_cpp_engine.py::test_seat_allocation_contiguous_preference` and `/api/osdbms/status` |
| **Shortest-Path Graph Search** | Railway Network Distance Calculation | `backend/cpp_engine/core_logic.cpp` | Dijkstra algorithm implemented using `std::priority_queue` (Min-Heap) | `backend/tests/test_cpp_engine.py::test_dijkstra_shortest_path` and UI `/lab` interactive solver |
| **Counting Semaphore** | Booking Request Ingress Throttling | `backend/app/services/os_demonstrations.py` | `threading.Semaphore(10)` guarding concurrent access | `backend/tests/test_cpp_engine.py::test_counting_semaphore_limit` and `/api/osdbms/semaphore-test` |
| **Producer-Consumer Bounded Buffer** | Asynchronous Ticket Generation Queue | `backend/app/services/os_demonstrations.py` | `queue.Queue(maxsize=50)` with 3 consumer threads and task completion signaling | `backend/tests/test_cpp_engine.py::test_producer_consumer_queue` and `/api/osdbms/queue-test` |
| **Priority Scheduling** | Tatkal vs General Quota Request Dispatching | `backend/app/services/os_demonstrations.py` | `queue.PriorityQueue` with arrival sequence counter for deterministic FIFO tie-breaking | `backend/tests/test_cpp_engine.py::test_priority_scheduling_simulation` and `/api/osdbms/priority-test` |
| **Deadlock Prevention** | Hierarchical Lock Acquisition | `backend/app/services/booking_service.py` | Strictly ordered row lock acquisition on seat IDs in ascending order (`ORDER BY s.id ASC`) | `backend/tests/test_concurrency.py::test_row_level_locking_concurrency` |

---

## DBMS Concept Mapping

| Academic Concept | RailSync Application Feature | Source File | Mechanism / Algorithm | Verification / Demonstration Method |
| :--- | :--- | :--- | :--- | :--- |
| **Relational Normalization (3NF)** | Database Schema Design | `backend/migrations/001_initial_schema.sql` | 10 normalized tables, composite foreign keys, zero transitive dependencies | Automated migration verification and schema inspection |
| **Date-Specific Reservation Model** | Reusable Physical Seats Across Dates | `backend/migrations/001_initial_schema.sql` | Relational table `seat_allocations` with `UNIQUE (seat_id, journey_date)` | `backend/tests/test_trains.py::test_train_seat_availability_map` |
| **Row-Level Locking & Concurrency** | Race Condition Prevention on Competing Bookings | `backend/app/services/booking_service.py`, `dbms_demonstrations.py` | InnoDB `SELECT ... FOR UPDATE` with isolated transaction boundary | `backend/tests/test_concurrency.py::test_row_level_locking_concurrency` (6 threads, 1 winner, 0 duplicates) |
| **ACID Atomicity & Rollback** | Transaction Failure Recovery | `backend/app/database/connection.py`, `dbms_demonstrations.py` | `conn.start_transaction()`, explicit commit, and guaranteed `conn.rollback()` on exception | `backend/tests/test_concurrency.py::test_innodb_acid_rollback` |
| **Indexing & Query Optimization** | Accelerated Train Search & PNR Lookup | `backend/migrations/001_initial_schema.sql`, `backend/app/services/dbms_demonstrations.py` | B-Tree indexes (`idx_train_search`, `idx_booking_pnr`, `idx_station_code`) | Live MySQL `EXPLAIN` inspection endpoint `/api/osdbms/query-plan` |
| **Connection Pooling** | Resource Recycling & Connection Lifecycle | `backend/app/database/connection.py` | `mysql.connector.pooling.MySQLConnectionPool` with automatic reset | Thread-safe connection context managers |
