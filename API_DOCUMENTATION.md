# RailSync: REST API Documentation
**Platform:** RailSync — Railway Reservation Simulation System  
**Base URL:** `http://localhost:5001/api`  
**Data Format:** JSON (`application/json`)  
**Session Authentication:** Cookie-based session (`session_id`), HttpOnly, SameSite=Lax  

---

## 1. Authentication Endpoints (`/api/auth`)

### 1.1 Register New Account
- **Endpoint:** `POST /api/auth/register`
- **Access:** Public
- **Request Body:**
  ```json
  {
    "full_name": "Rahul Sharma",
    "email": "rahul@example.com",
    "password": "Password@123",
    "phone": "+91 98765 43210",
    "address": "Connaught Place, New Delhi"
  }
  ```
- **Responses:**
  - `201 Created`: User registered and authenticated.
  - `400 Bad Request`: Validation error or duplicate email.

### 1.2 User Login
- **Endpoint:** `POST /api/auth/login`
- **Access:** Public
- **Request Body:**
  ```json
  {
    "email": "user@railsync.com",
    "password": "User@123"
  }
  ```
- **Responses:**
  - `200 OK`: Sets HTTP-only session cookie. Returns user metadata.
  - `401 Unauthorized`: Invalid credentials.

### 1.3 Check Session
- **Endpoint:** `GET /api/auth/me`
- **Access:** Authenticated
- **Responses:**
  - `200 OK`: `{ "authenticated": true, "user": { "id": 2, "full_name": "...", "role": "USER" } }`
  - `401 Unauthorized`: Session expired or not logged in.

### 1.4 Logout
- **Endpoint:** `POST /api/auth/logout`
- **Access:** Authenticated
- **Responses:**
  - `200 OK`: Session cleared.

---

## 2. Train Discovery & Timetable Endpoints (`/api/trains`)

### 2.1 Get Active Stations
- **Endpoint:** `GET /api/trains/stations`
- **Query Parameters:**
  - `q` (optional): Filter by station code, name, or city.
  - `sort_by` (optional): `name`, `code`, `city` (default: `name`).
  - `order` (optional): `asc`, `desc`.
- **Response:**
  ```json
  {
    "stations": [
      { "id": 1, "station_code": "NDLS", "station_name": "New Delhi", "city": "New Delhi" }
    ],
    "count": 54
  }
  ```

### 2.2 Search Trains
- **Endpoint:** `GET /api/trains/search`
- **Query Parameters:**
  - `source_id` (int): Origin station ID (supports direct & intermediate stops).
  - `dest_id` (int): Destination station ID.
  - `date` (string, `YYYY-MM-DD`): Journey date.
  - `class` (string): `1A`, `2A`, `3A`, `CC`, `SL`, or `ALL`.
  - `train_type` (string): `VANDE_BHARAT`, `RAJDHANI`, `SHATABDI`, `DURONTO`, `GARIB_RATH`, `SUPERFAST`, `MAIL_EXPRESS`, `INTERCITY`, `EXPRESS`.
  - `departure_slot` (string): `early_morning`, `morning`, `midday`, `night`.
  - `arrival_slot` (string): `early_morning`, `morning`, `midday`, `night`.
  - `min_fare` (float): Minimum fare filter.
  - `max_fare` (float): Maximum fare filter.
  - `only_available` (bool): `true` to return trains with available seats only.
  - `train_query` (string): Direct search by train number or train name.
- **Response:**
  ```json
  {
    "trains": [
      {
        "id": 3,
        "train_number": "12952",
        "train_name": "Mumbai Tejas Rajdhani Express",
        "train_type": "SUPERFAST",
        "source_station_name": "New Delhi Railway Station",
        "source_station_code": "NDLS",
        "destination_station_name": "Mumbai Central",
        "destination_station_code": "MMCT",
        "departure_time": "16:55",
        "arrival_time": "08:35",
        "duration": "15h 40m",
        "distance_km": 1384,
        "base_fare": 1850.0,
        "total_available_seats": 64,
        "classes": [
          { "coach_type": "3A", "available": 32, "total": 32, "fare": 2587.5, "status_label": "AVL 32" }
        ]
      }
    ],
    "count": 1,
    "dijkstra_path": { "engine": "C++17 Min-Heap", "hops": 5, "total_distance_km": 1384 }
  }
  ```

### 2.3 Train Details & Seat Map
- **Endpoint:** `GET /api/trains/<train_id>/availability?date=YYYY-MM-DD`
- **Response:** Returns complete physical coach layout and individual seat statuses (`AVAILABLE` or `BOOKED`) for the given date.

### 2.4 Timetable & Intermediate Stops
- **Endpoint:** `GET /api/trains/<train_id>/stops`
- **Response:** Returns ordered stops with sequence, arrival time, departure time, halt minutes, and cumulative distance from origin.

### 2.5 Authoritative Fare Quote
- **Endpoint:** `GET /api/trains/fare-quote?train_id=<id>&class=<cls>&passengers=<cnt>`
- **Response:**
  ```json
  {
    "travel_class": "3A",
    "train_type": "SUPERFAST",
    "num_passengers": 2,
    "class_fare_per_passenger": 2497.5,
    "reservation_fee_per_passenger": 40.0,
    "superfast_charge_per_passenger": 45.0,
    "gst_per_passenger": 129.13,
    "total_base_amount": 4995.0,
    "total_reservation_fee": 80.0,
    "total_superfast_charge": 90.0,
    "total_gst": 258.26,
    "total_amount": 5423.26
  }
  ```

---

## 3. Reservation & Booking Endpoints (`/api/bookings`)

### 3.1 Create ACID Reservation
- **Endpoint:** `POST /api/bookings`
- **Access:** Authenticated User
- **Request Body:**
  ```json
  {
    "train_id": 3,
    "journey_date": "2026-11-28",
    "travel_class": "3A",
    "passengers": [
      { "full_name": "Vikram Malhotra", "age": 34, "gender": "MALE", "berth_preference": "LOWER" },
      { "full_name": "Pooja Malhotra", "age": 31, "gender": "FEMALE", "berth_preference": "WINDOW" }
    ],
    "seat_ids": [101, 102],
    "payment_details": {
      "transaction_id": "TXN-SIM-CC7A6F8D2045",
      "payment_method": "UPI",
      "bank_ref_number": "REF-27925326",
      "idempotency_key": "IDEMP-1731560000000-ABCDEF"
    }
  }
  ```
- **Responses:**
  - `201 Created`: Returns confirmed PNR, ticket number, and allocated berths.
  - `400 Bad Request`: Validation failure or seat conflict.

### 3.2 Lookup Booking by PNR
- **Endpoint:** `GET /api/bookings/<pnr>`
- **Access:** Public / Authenticated (Anonymizes passenger full names for unauthenticated callers).

### 3.3 Dynamic Verification QR Code
- **Endpoint:** `GET /api/bookings/<pnr>/qr`
- **Response:** Image (`image/png`) containing digital verification URL and integrity hash.

### 3.4 Vector PDF E-Ticket Download
- **Endpoint:** `GET /api/bookings/<pnr>/ticket.pdf` or `GET /api/bookings/<pnr>/pdf`
- **Access:** Booking Owner or Admin
- **Response:** Streamed binary PDF (`application/pdf`) generated on-the-fly via ReportLab.

### 3.5 Cancel Reservation
- **Endpoint:** `POST /api/bookings/<pnr>/cancel`
- **Access:** Booking Owner or Admin
- **Response:**
  ```json
  {
    "success": true,
    "pnr": "RS82201721",
    "cancellation_number": "CAN-2C295C8EC1",
    "gross_amount": "3155.24",
    "cancellation_fee": 240.0,
    "refund_amount": 2915.24,
    "seats_released": 2,
    "waitlist_promoted_count": 0
  }
  ```

---

## 4. Simulated Payment Gateway (`/api/payments`)

### 4.1 Payment Gateway Simulation
- **Endpoint:** `POST /api/payments/simulate`
- **Access:** Public / Authenticated
- **Request Body:**
  ```json
  {
    "amount": 3155.24,
    "payment_method": "UPI",
    "outcome": "SUCCESS"
  }
  ```
- **Responses:**
  - `200 OK` (when `outcome="SUCCESS"`):
    ```json
    {
      "status": "SUCCESS",
      "transaction_id": "TXN-SIM-CC7A6F8D2045",
      "bank_ref_number": "REF-27925326",
      "amount": 3155.24,
      "payment_method": "UPI",
      "payment_gateway": "Simulated Indian RailPay Gateway"
    }
    ```
  - `400 Bad Request` (when `outcome="FAILURE"`):
    ```json
    {
      "status": "FAILED",
      "success": false,
      "transaction_id": "TXN-SIM-DEC12345",
      "bank_ref_number": "REF-DEC67890",
      "message": "Payment simulation declined: Issuing bank rejected authorization.",
      "can_retry": true
    }
    ```

---

## 5. Administration Endpoints (`/api/admin`)

*Note: All `/api/admin/*` endpoints strictly enforce `role == 'ADMIN'`.*

| Method | Path | Description |
| :--- | :--- | :--- |
| `GET` | `/api/admin/dashboard` | Returns aggregate metrics (revenue, total bookings, users, active cancellations). |
| `GET` | `/api/admin/trains` | List all trains with coach and stop counts. |
| `POST` | `/api/admin/trains` | Create new train service and auto-seed coaches and seats. |
| `PUT` | `/api/admin/trains/<id>` | Update train schedule, category, or fare. |
| `DELETE` | `/api/admin/trains/<id>` | Toggle train active/disabled status. |
| `GET` | `/api/admin/trains/<id>/stops` | View timetable stops for train. |
| `POST` | `/api/admin/trains/<id>/stops` | Insert/update intermediate timetable stop. |
| `DELETE` | `/api/admin/stops/<stop_id>` | Remove intermediate timetable stop. |
| `GET` | `/api/admin/stations` | List all active stations. |
| `POST` | `/api/admin/stations` | Add new station. |
| `PUT` | `/api/admin/stations/<id>` | Update station details. |
| `DELETE` | `/api/admin/stations/<id>` | Toggle station active/inactive. |
| `GET` | `/api/admin/bookings` | View all platform bookings. |
| `GET` | `/api/admin/users` | View all registered accounts. |
| `GET` | `/api/admin/diagnostics` | System health check (C++ ctypes, MySQL table counts, Semaphore metrics). |

