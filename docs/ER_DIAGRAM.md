# RailSync Entity-Relationship (ER) Diagram

## Conceptual Model & Normalization
The RailSync database schema is designed according to Third Normal Form (3NF) principles using the MySQL 8 InnoDB storage engine.

### Key Architectural Strengths:
1. **Date-Specific Relational Allocation Model**: Unlike simplistic designs that globally set a `seat.status` column to "BOOKED", RailSync separates physical seat inventory from date-specific reservations via the `seat_allocations` table with a composite `UNIQUE (seat_id, journey_date)` constraint.
2. **Referential Integrity**: Cascading and restrictive foreign key constraints prevent orphaned records.
3. **Optimized Indexes**: B-tree indexes are applied to search paths (`source_station_id`, `destination_station_id`, `is_active`), PNR lookups, and user booking history.

---

## Mermaid ER Diagram

```mermaid
erDiagram
    USERS ||--o{ BOOKINGS : places
    STATIONS ||--o{ ROUTES : "origin station"
    STATIONS ||--o{ ROUTES : "destination station"
    STATIONS ||--o{ TRAINS : "origin hub"
    STATIONS ||--o{ TRAINS : "destination hub"
    TRAINS ||--o{ COACHES : contains
    COACHES ||--o{ SEATS : has
    BOOKINGS ||--|{ PASSENGERS : includes
    BOOKINGS ||--|| TICKETS : issues
    BOOKINGS ||--o{ SEAT_ALLOCATIONS : reserves
    SEATS ||--o{ PASSENGERS : assigned_to
    SEATS ||--o{ SEAT_ALLOCATIONS : allocated_for_date

    USERS {
        int id PK
        string full_name
        string email UK
        string password_hash
        string role "USER or ADMIN"
        timestamp created_at
    }

    STATIONS {
        int id PK
        string station_code UK
        string station_name
        string city
    }

    ROUTES {
        int id PK
        int source_station_id FK
        int destination_station_id FK
        int distance_km
        int travel_duration_minutes
    }

    TRAINS {
        int id PK
        string train_number UK
        string train_name
        int source_station_id FK
        int destination_station_id FK
        time departure_time
        time arrival_time
        string running_days
        decimal base_fare
        boolean is_active
    }

    COACHES {
        int id PK
        int train_id FK
        string coach_number "e.g. C1, B1"
        string coach_type "CC, 3A, 2A, 1A, SL"
        int total_seats
    }

    SEATS {
        int id PK
        int coach_id FK
        int seat_number
        string berth_type "LOWER, MIDDLE, UPPER, SIDE LOWER, SIDE UPPER"
        boolean is_active
    }

    BOOKINGS {
        int id PK
        string pnr UK "10-character e.g. RS29384751"
        int user_id FK
        int train_id FK
        date journey_date
        string booking_status "CONFIRMED, CANCELLED, FAILED"
        decimal total_amount
        string payment_status "PENDING, SUCCESS, FAILED, REFUNDED"
        timestamp created_at
        timestamp cancelled_at
    }

    PASSENGERS {
        int id PK
        int booking_id FK
        string full_name
        int age
        string gender "MALE, FEMALE, OTHER"
        int seat_id FK
        string passenger_status "CONFIRMED, CANCELLED"
    }

    TICKETS {
        int id PK
        int booking_id FK
        string ticket_number UK
        timestamp issued_at
    }

    SEAT_ALLOCATIONS {
        int id PK
        int train_id FK
        int seat_id FK
        date journey_date
        int booking_id FK
        int passenger_id FK
        timestamp allocated_at
    }
```

---

## Schema Integrity Rules
* `UNIQUE (email)` on `users` table prevents duplicate customer registration.
* `UNIQUE (seat_id, journey_date)` on `seat_allocations` strictly enforces single-occupancy per journey in MySQL InnoDB.
* `UNIQUE (pnr)` on `bookings` ensures ticket traceability.
* Composite B-Tree index on `(source_station_id, destination_station_id, is_active)` speeds up search queries by index range scan.
