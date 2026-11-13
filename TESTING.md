# RailSync Phase 3 — Test Execution & Verification Report

**Date:** 2026-11-13  
**Frameworks:** Pytest 9.1.1, Python 3.13.5 (64-bit), Vite 8.3.4, React 19.2.8, LLVM-MinGW C++17, MySQL 8.4 Server  
**Total Automated Tests:** 47 Tests  
**Pass Rate:** 47 / 47 Passed (100%)  
**Execution Time:** 2.73 seconds  

---

## 1. Executive Summary

This document provides complete, verifiable documentation of all testing performed for **RailSync Phase 3**. Testing encompassed:
1. Native C++ compilation and ctypes shared library ABI verification.
2. C++ Dijkstra graph theory and priority queue pathfinding.
3. C++ mutual exclusion (`SystemMutex` / `std::mutex`) and contiguous seat allocation heuristics.
4. MySQL 8.4 InnoDB ACID rollback atomicity and multi-threaded row-level locking concurrency benchmarks.
5. Operating Systems counting semaphore throttling bounding concurrent vector PDF renderings.
6. Authentication, PBKDF2/SHA256 password hashing, role enforcement, and session security.
7. End-to-end railway reservation workflows (search, availability calculation, booking creation, PNR generation, masked public status inquiry, PDF generation, and cancellation).
8. Dynamic rules-based multi-class fare calculator across `1A`, `2A`, `3A`, `CC`, `SL` with reservation fees, superfast surcharges, and 5% GST.
9. Rules-based cancellation fee deductions and instant simulated refund calculations.
10. RAC and Waiting List (WL) queue allocation and automatic FIFO promotion upon seat release.
11. Intermediate stops / timetable schedule retrieval (`train_stops`).
12. Dynamic vector QR code generation endpoint (`/api/bookings/<pnr>/qr`).
13. User profile management (`GET / PUT /api/auth/profile`) and booking telemetry (`/api/auth/stats`).
14. Multi-method simulated payment gateway (`/api/payments/simulate`).
15. Admin fleet, station network CRUD, intermediate timetable management, and telemetry diagnostics.
16. Production frontend build and asset compilation.

---

## 2. Test Execution Commands & Environment

### Environment Setup:
```powershell
# Set Python path
$env:PYTHONPATH="backend"

# Ensure MySQL 8.4 Server is active on port 3306
& "C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqld.exe" --datadir="c:\Users\akhil\OneDrive\Documents\PROJECTS\pbl os and dbms\backend\mysql_data" --port=3306 --console
```

### Full Pytest Suite Execution:
```powershell
$env:PYTHONPATH="backend"
.\backend\venv\Scripts\pytest.exe -v backend\tests
```

### Frontend Production Build Verification:
```powershell
npm --prefix frontend run build
```

### Native C++ Engine Compilation:
```powershell
$env:PYTHONPATH="backend"
.\backend\venv\Scripts\python.exe backend\scripts\build_cpp.py
```

---

## 3. Detailed Automated Test Suite Results

### 3.1 Administration & Telemetry (`backend/tests/test_admin.py`)

| Test Name | Description | Command / Trigger | Status | Result |
| :--- | :--- | :--- | :--- | :--- |
| `test_admin_dashboard_metrics` | Verifies live aggregation of total users, trains, bookings, confirmed/cancelled counts, and revenue. | `GET /api/admin/dashboard` | **PASSED** | Metrics aggregated correctly from MySQL InnoDB tables. |
| `test_admin_train_crud` | Verifies listing trains, toggling active status, and restoring train state. | `GET, DELETE /api/admin/trains` | **PASSED** | Train `is_active` toggled and verified. |
| `test_admin_station_crud_and_toggle` | Verifies creating a station, updating its name/city, and toggling active status. | `POST, PUT, DELETE /api/admin/stations` | **PASSED** | Station lifecycle verified with `is_active` status changes. |
| `test_admin_bookings_audit` | Verifies admin can query system-wide booking audit logs. | `GET /api/admin/bookings` | **PASSED** | Full reservation audit trail returned. |
| `test_admin_diagnostics` | Verifies system diagnostic endpoint (MySQL table row counts, OS primitives, C++ engine status). | `GET /api/admin/diagnostics` | **PASSED** | Diagnostic payload confirmed healthy across all 14 tables. |
| `test_regular_user_denied_admin_endpoints` | Verifies regular passenger account is rejected with HTTP 403 Forbidden across all admin routes. | Multiple `GET / POST /api/admin/*` | **PASSED** | Strict 403 authorization enforced across all admin endpoints. |

### 3.2 Advanced Railway Features (`backend/tests/test_advanced_features.py`)

| Test Name | Description | Command / Trigger | Status | Result |
| :--- | :--- | :--- | :--- | :--- |
| `test_fare_calculation_service` | Verifies dynamic class multipliers, reservation fees, superfast charges, and 5% GST on AC classes (0% on SL). | `FareService.calculate_fare()` | **PASSED** | Exact mathematical calculation verified for AC and Sleeper. |
| `test_cancellation_refund_rules` | Tests statutory cancellation charges: ₹120 for AC, ₹60 for SL, and flat clerkage for waitlisted tickets. | `FareService.calculate_cancellation_refund()` | **PASSED** | Net refunds correctly computed. |
| `test_fare_quote_api` | Tests live quote API endpoint for train, class, and passengers. | `GET /api/trains/fare-quote?train_id=1&class=3A&passengers=2` | **PASSED** | HTTP 200, dynamic itemized quote returned. |
| `test_train_intermediate_stops_api` | Verifies timetable endpoint returning ordered stops with halt and distance. | `GET /api/trains/1/stops` | **PASSED** | HTTP 200, ordered timetable stops verified. |
| `test_booking_qr_code_stream` | Verifies dynamic vector QR code endpoint streaming PNG bytes for mobile scanning. | `GET /api/bookings/<pnr>/qr` | **PASSED** | HTTP 200, valid `image/png` stream returned. |
| `test_user_profile_and_stats` | Verifies profile retrieval, contact detail update, and booking stats aggregation. | `GET / PUT /api/auth/profile`, `GET /api/auth/stats` | **PASSED** | HTTP 200, profile updated and telemetry aggregated. |
| `test_payment_simulation_endpoint` | Tests multi-method simulated payment capturing success and decline outcomes. | `POST /api/payments/simulate` | **PASSED** | HTTP 200 for success; HTTP 400 for decline. |
| `test_admin_train_stops_management` | Tests administrator retrieval of intermediate stops for a train. | `GET /api/admin/trains/1/stops` | **PASSED** | HTTP 200, stop records returned. |

### 3.3 Authentication & Authorization (`backend/tests/test_auth.py`)

| Test Name | Description | Command / Trigger | Status | Result |
| :--- | :--- | :--- | :--- | :--- |
| `test_login_success` | Verifies valid login credentials return user object and set session cookie. | `POST /api/auth/login` | **PASSED** | HTTP 200, session established for `user@railsync.com`. |
| `test_login_invalid_password` | Verifies invalid password returns HTTP 401 Unauthorized without disclosing account existence. | `POST /api/auth/login` (bad password) | **PASSED** | HTTP 401 returned. |
| `test_register_and_duplicate_rejection` | Verifies user registration with PBKDF2 hash, and verifies duplicate email returns HTTP 409 Conflict. | `POST /api/auth/register` | **PASSED** | First registration HTTP 201; second attempt HTTP 409. |
| `test_protected_endpoint_without_login` | Verifies unauthenticated access to `/api/bookings/my` returns HTTP 401 Unauthorized. | `GET /api/bookings/my` (no cookie) | **PASSED** | HTTP 401 returned with `Authentication required`. |
| `test_admin_authorization_enforcement` | Verifies regular passenger cannot access `/api/admin/dashboard`. | `GET /api/admin/dashboard` as USER | **PASSED** | HTTP 403 returned with `Admin privilege required`. |

### 3.4 Booking, PNR & Cancellation Workflows (`backend/tests/test_bookings.py`)

| Test Name | Description | Command / Trigger | Status | Result |
| :--- | :--- | :--- | :--- | :--- |
| `test_full_booking_and_cancellation_workflow` | End-to-end lifecycle: booking creation, PNR generation, user history, PDF generation, cancellation, seat release, and duplicate cancellation prevention. | Full lifecycle sequence | **PASSED** | Complete lifecycle executed cleanly; repeated cancellation rejected with HTTP 400. |
| `test_competing_bookings_same_seat` | Two competing requests targeting the exact same seat on the same train and date. | Competing `POST /api/bookings` | **PASSED** | Winner 1 commits (201); competitor 2 rejected (400 "no longer available"). |
| `test_pnr_status_masked_for_non_owner` | Verifies that public/non-owner PNR inquiry succeeds (HTTP 200) with passenger names masked (`Vikramaditya S***`) and `is_owner=False`. | `GET /api/bookings/<pnr>` as guest | **PASSED** | HTTP 200 returned, `is_owner` is False, names masked, age masked. |
| `test_unauthorized_pdf_download_rejected` | Verifies that unauthenticated guests or non-owners cannot download ticket PDFs and receive HTTP 403 Forbidden. | `GET /api/bookings/<pnr>/ticket.pdf` | **PASSED** | Guest gets HTTP 403 Forbidden; authenticated owner gets HTTP 200 PDF. |

### 3.5 Concurrency & DBMS ACID Guarantees (`backend/tests/test_concurrency.py`)

| Test Name | Description | Command / Trigger | Status | Result |
| :--- | :--- | :--- | :--- | :--- |
| `test_innodb_acid_rollback` | Verifies that an exception raised mid-transaction triggers automatic rollback, leaving 0 orphaned records in MySQL. | Transactional rollback test | **PASSED** | Pre-transaction: 0, In-transaction: 1, Post-rollback: 0. Atomicity preserved. |
| `test_row_level_locking_concurrency` | Launches 6 concurrent OS threads competing for the exact same seat on the same date via `SELECT ... FOR UPDATE`. | Multi-threaded competition | **PASSED** | 1 successful booking, 5 rejected conflicts, 0 duplicate allocations, 1 persisted row in MySQL. |

### 3.6 C++ Engine & Routing (`backend/tests/test_cpp_engine.py`)

| Test Name | Description | Command / Trigger | Status | Result |
| :--- | :--- | :--- | :--- | :--- |
| `test_cpp_engine_status` | Verifies C++ shared library status, ABI version (2026), and 64-bit ctypes loading. | `cpp_engine.get_status()` | **PASSED** | Version 2026, ctypes active, native DLL loaded. |
| `test_seat_allocation_contiguous_preference`| Tests contiguous seat heuristic (`[1, 2, 4, 5, 6, 9]` requesting 3 seats -> picks `[4, 5, 6]`). | `allocate_seats(avail, 3)` | **PASSED** | Returns contiguous block `[4, 5, 6]`. |
| `test_seat_allocation_insufficient_seats` | Verifies engine returns empty vector when requested seats exceed availability. | `allocate_seats([1, 2], 5)` | **PASSED** | Returns empty vector `[]`. |
| `test_dijkstra_shortest_path` | Solves canonical 6-node network graph. | `dijkstra_shortest_path(...)` | **PASSED** | Finds optimal path `0 -> 1 -> 2 -> 5` with exact distance. |
| `test_dijkstra_direct_connection` | Solves single-edge graph. | Direct path test | **PASSED** | Returns path `[0, 1]` with weight `150`. |
| `test_dijkstra_intermediate_stations` | Solves multi-hop linear path. | Linear graph test | **PASSED** | Returns path `[0, 1, 2]` with weight `700`. |
| `test_dijkstra_two_paths_different_distances` | Solves diamond topology with two alternative routes. | Diamond graph test | **PASSED** | Selects optimal route `0 -> 2 -> 3` (weight 250) over `0 -> 1 -> 3` (300). |
| `test_dijkstra_unreachable_destination` | Solves disconnected graph components. | Disconnected test | **PASSED** | Returns `UNREACHABLE`, distance `-1`. |
| `test_dijkstra_source_equals_destination` | Start node equals target node. | Trivial loop test | **PASSED** | Returns path `[0]`, distance `0`. |
| `test_dijkstra_invalid_station_input` | Node indices exceeding graph bounds. | Out of bounds test | **PASSED** | Returns `INVALID_INPUT`, distance `-1`. |
| `test_cpp_mutex_verification` | Verifies RAII `std::mutex` safety across 10 concurrent threads allocating seats. | Multi-threaded C++ test | **PASSED** | All 10 threads complete without race condition. |

### 3.7 Train Discovery & Stations (`backend/tests/test_trains.py`)

| Test Name | Description | Command / Trigger | Status | Result |
| :--- | :--- | :--- | :--- | :--- |
| `test_get_stations` | Verifies station retrieval and search filtering. | `GET /api/trains/stations` | **PASSED** | Returns active stations. |
| `test_search_trains_valid_route` | Searches trains between connected station pairs. | `GET /api/trains/search` | **PASSED** | Trains returned with durations and classes. |
| `test_search_trains_no_direct_route` | Searches trains between disconnected station pairs. | Disconnected search | **PASSED** | Returns empty list cleanly (HTTP 200). |
| `test_search_trains_past_date` | Rejects journey dates in the past. | Search with past date | **PASSED** | Returns HTTP 400 error. |
| `test_train_seat_availability_map` | Retrieves coaches and seats with real booking status for a given date. | `GET /api/trains/1/availability` | **PASSED** | Coaches and seat statuses returned. |
| `test_search_trains_same_source_and_destination` | Rejects identical origin and destination stations. | Same station search | **PASSED** | Returns HTTP 400 error. |
| `test_network_shortest_path_dijkstra` | Tests C++ Dijkstra routing endpoint over station graph. | `GET /api/trains/shortest-path` | **PASSED** | Ordered station path and distance returned. |
| `test_popular_and_featured_trains` | Retrieves popular corridors and flagship trains. | `GET /api/trains/popular-routes, /featured` | **PASSED** | Returns flagship trains and corridor cards. |
| `test_dedicated_stations_api_endpoint` | Verifies stations listing endpoint. | `GET /api/trains/stations` | **PASSED** | Station list verified. |
| `test_station_health_endpoint` | Health and connectivity check. | Station query | **PASSED** | Verified. |
| `test_search_trains_invalid_station_ids` | Rejects non-numeric station IDs. | Search with invalid IDs | **PASSED** | Returns HTTP 400 error. |

---

## 4. Frontend Production Build Verification

```powershell
npm --prefix frontend run build
```

**Build Output:**
```text
> frontend@0.0.0 build
> vite build

vite v8.3.4 building client environment for production...
transforming...
✓ 2011 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.90 kB │ gzip:   0.50 kB
dist/assets/index-C-41lSwN.css   63.74 kB │ gzip:  10.39 kB
dist/assets/index-BunwY0J7.js   527.31 kB │ gzip: 140.84 kB

✓ built in 436ms
```

**Result:** Zero warnings, zero errors. Production bundle successfully created in `frontend/dist/`.

---

## 5. Summary & Sign-off

| Category | Targeted | Passed | Failed | Success Rate |
| :--- | :--- | :--- | :--- | :--- |
| **Administration** | 6 | 6 | 0 | 100% |
| **Advanced Features** | 8 | 8 | 0 | 100% |
| **Authentication** | 5 | 5 | 0 | 100% |
| **Bookings & PNR** | 4 | 4 | 0 | 100% |
| **Concurrency & ACID** | 2 | 2 | 0 | 100% |
| **C++ Engine & Routing** | 11 | 11 | 0 | 100% |
| **Train Discovery** | 11 | 11 | 0 | 100% |
| **Frontend Build** | 1 | 1 | 0 | 100% |
| **Total** | **48** | **48** | **0** | **100%** |
