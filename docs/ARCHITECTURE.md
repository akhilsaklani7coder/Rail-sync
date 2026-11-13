# RailSync System Architecture

## Overview
RailSync is a modern, full-stack Indian Railway Reservation Prototype architected for college Project-Based Learning (PBL). It unifies a responsive React frontend, a Python Flask API with modular blueprints, a normalized MySQL 8 InnoDB relational database, and a native C++ engine with mutual exclusion and graph pathfinding.

---

## Architectural Layers

```
+-------------------------------------------------------------------------+
|                         React + Vite Frontend                           |
|  - Tailwind CSS + Lucide React                                          |
|  - Axios Client with Session Credentials (withCredentials: true)        |
|  - Interactive Coach Seat Map & Live Booking Flow                       |
|  - OS & DBMS Interactive Demonstration Lab                              |
+------------------------------------+------------------------------------+
                                     |  HTTP REST / JSON
                                     v
+------------------------------------+------------------------------------+
|                         Flask 3.0 Backend                               |
|  - Modular Blueprints: Auth, Trains, Bookings, Payments, Admin, OSDBMS  |
|  - Werkzeug Secure Password Hashing                                     |
|  - Session-based Role Authorization (USER / ADMIN)                      |
|  - ReportLab PDF Electronic Ticket Engine                               |
+------------------+----------------------------------+-------------------+
                   |                                  |
                   | ctypes ABI / Bridge              | Parameterized SQL
                   v                                  v
+------------------+---------------+  +---------------+-------------------+
|     C++17 Native Engine          |  |       MySQL 8.4 Server            |
|  - std::mutex Critical Sections  |  |  - InnoDB ACID Transactions       |
|  - Contiguous Window Allocator   |  |  - Row-Level Locking (FOR UPDATE) |
|  - Dijkstra Shortest Path        |  |  - 3NF Normalized Schema          |
|    (std::priority_queue Min-Heap)|  |  - B-Tree Indexes & Constraints   |
+----------------------------------+  +-----------------------------------+
```

---

## Data Flow & Booking Lifecycle

1. **Station & Train Discovery**:
   - The user selects source, destination, and journey date.
   - The backend runs an optimized SQL query with `INNER JOIN` and calculates journey-specific availability by querying physical seats minus active `seat_allocations` for that date.
2. **Interactive Coach Selection**:
   - Users view real-time availability on the visual coach map.
   - Users can choose either manual seat selection or activate the **C++ Allocator Engine** for automatic contiguous seat selection.
3. **Simulated Payment Gateway**:
   - A realistic mock checkout interface provides options to simulate success or failure without collecting real bank or card numbers.
4. **ACID Transactional Commitment**:
   - The backend initiates an InnoDB transaction (`conn.start_transaction()`).
   - Acquires row-level exclusive locks using `SELECT ... FOR UPDATE`.
   - Re-verifies seat availability.
   - Inserts booking, passenger, ticket, and seat allocation rows.
   - Generates a unique 10-character PNR (`RS` + 8 digits).
   - Commits the transaction atomically. If any error occurs, automatic rollback occurs.
5. **PDF Ticket Issuance**:
   - ReportLab builds an Electronic Reservation Slip PDF with branding, PNR, train timings, and assigned berths.
