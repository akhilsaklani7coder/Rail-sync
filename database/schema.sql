-- ============================================================================
-- RailSync 3NF Relational Database Schema (Phase 3 Master Release)
-- Technology: MySQL 8.0 / 8.4 Server with InnoDB Engine
-- Guarantees: Full ACID Compliance, Foreign Key Referential Integrity,
--             Row-Level Locking (SELECT ... FOR UPDATE),
--             Date-Isolated Seat Allocations, Waitlist/RAC Queues, and Refund Auditing.
-- ============================================================================

CREATE DATABASE IF NOT EXISTS railsync_db 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE railsync_db;

-- ----------------------------------------------------------------------------
-- Table 1: users
-- Stores registered passenger accounts and administrators with secure password hashes.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20) NULL,
    address VARCHAR(255) NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('USER', 'ADMIN') NOT NULL DEFAULT 'USER',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_email (email),
    INDEX idx_user_role (role)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 2: stations
-- Railway station nodes across the national network (32 major hubs).
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    station_code VARCHAR(10) NOT NULL UNIQUE,
    station_name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    INDEX idx_station_code (station_code),
    INDEX idx_station_city (city),
    INDEX idx_station_active (is_active)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 3: routes
-- Bidirectional physical graph edges between stations used by the C++ Dijkstra engine.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS routes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source_station_id INT NOT NULL,
    destination_station_id INT NOT NULL,
    distance_km INT NOT NULL,
    travel_duration_minutes INT NOT NULL,
    FOREIGN KEY (source_station_id) REFERENCES stations(id) ON DELETE RESTRICT,
    FOREIGN KEY (destination_station_id) REFERENCES stations(id) ON DELETE RESTRICT,
    UNIQUE KEY uq_route_pair (source_station_id, destination_station_id),
    INDEX idx_route_source (source_station_id),
    INDEX idx_route_dest (destination_station_id)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 4: trains
-- Scheduled express train services connecting pairs of stations.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS trains (
    id INT AUTO_INCREMENT PRIMARY KEY,
    train_number VARCHAR(20) NOT NULL UNIQUE,
    train_name VARCHAR(150) NOT NULL,
    train_type ENUM('VANDE_BHARAT', 'RAJDHANI', 'SHATABDI', 'SUPERFAST', 'EXPRESS') NOT NULL DEFAULT 'EXPRESS',
    source_station_id INT NOT NULL,
    destination_station_id INT NOT NULL,
    departure_time TIME NOT NULL,
    arrival_time TIME NOT NULL,
    running_days VARCHAR(50) NOT NULL DEFAULT 'DAILY',
    base_fare DECIMAL(10, 2) NOT NULL DEFAULT 500.00,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (source_station_id) REFERENCES stations(id) ON DELETE RESTRICT,
    FOREIGN KEY (destination_station_id) REFERENCES stations(id) ON DELETE RESTRICT,
    INDEX idx_train_search (source_station_id, destination_station_id, is_active),
    INDEX idx_train_number (train_number),
    INDEX idx_train_type (train_type)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 5: train_stops (Timetable & Intermediate Stations)
-- Route timetable with sequence order, arrival, departure, halt, and distance from origin.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS train_stops (
    id INT AUTO_INCREMENT PRIMARY KEY,
    train_id INT NOT NULL,
    station_id INT NOT NULL,
    stop_sequence INT NOT NULL,
    arrival_time TIME NULL,
    departure_time TIME NULL,
    halt_minutes INT NOT NULL DEFAULT 2,
    distance_from_origin_km INT NOT NULL DEFAULT 0,
    day_number INT NOT NULL DEFAULT 1,
    FOREIGN KEY (train_id) REFERENCES trains(id) ON DELETE CASCADE,
    FOREIGN KEY (station_id) REFERENCES stations(id) ON DELETE RESTRICT,
    UNIQUE KEY uq_train_stop_seq (train_id, stop_sequence),
    INDEX idx_stop_station (station_id),
    INDEX idx_train_stop (train_id, stop_sequence)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 6: coaches
-- Physical coaches assigned to a train (1A, 2A, 3A, SL, CC).
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS coaches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    train_id INT NOT NULL,
    coach_number VARCHAR(10) NOT NULL,
    coach_type ENUM('1A', '2A', '3A', 'SL', 'CC') NOT NULL DEFAULT 'SL',
    total_seats INT NOT NULL DEFAULT 32,
    FOREIGN KEY (train_id) REFERENCES trains(id) ON DELETE CASCADE,
    UNIQUE KEY uq_train_coach (train_id, coach_number),
    INDEX idx_coach_train (train_id),
    INDEX idx_coach_type (coach_type)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 7: seats
-- Physical seat layout template per coach with berth/seat attributes.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS seats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    coach_id INT NOT NULL,
    seat_number INT NOT NULL,
    berth_type ENUM('LOWER', 'MIDDLE', 'UPPER', 'SIDE LOWER', 'SIDE UPPER', 'WINDOW', 'AISLE') NOT NULL DEFAULT 'LOWER',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (coach_id) REFERENCES coaches(id) ON DELETE CASCADE,
    UNIQUE KEY uq_coach_seat (coach_id, seat_number),
    INDEX idx_seat_coach (coach_id)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 8: bookings
-- Core reservation record storing booking status, simulated payment, and unique PNR.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pnr VARCHAR(12) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    train_id INT NOT NULL,
    journey_date DATE NOT NULL,
    travel_class ENUM('1A', '2A', '3A', 'SL', 'CC') NOT NULL DEFAULT 'CC',
    booking_status ENUM('CONFIRMED', 'RAC', 'WAITLISTED', 'CANCELLED', 'FAILED') NOT NULL DEFAULT 'CONFIRMED',
    base_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    reservation_fee DECIMAL(10, 2) NOT NULL DEFAULT 40.00,
    superfast_charge DECIMAL(10, 2) NOT NULL DEFAULT 45.00,
    gst_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_status ENUM('PENDING', 'SUCCESS', 'FAILED', 'REFUNDED') NOT NULL DEFAULT 'SUCCESS',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMP NULL DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (train_id) REFERENCES trains(id) ON DELETE RESTRICT,
    INDEX idx_booking_user (user_id),
    INDEX idx_booking_pnr (pnr),
    INDEX idx_booking_train_date (train_id, journey_date),
    INDEX idx_booking_status (booking_status)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 9: passengers
-- Passenger demographic information and allocated berth details.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS passengers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender ENUM('MALE', 'FEMALE', 'OTHER') NOT NULL,
    berth_preference ENUM('NO_PREFERENCE', 'LOWER', 'MIDDLE', 'UPPER', 'SIDE LOWER', 'SIDE UPPER', 'WINDOW', 'AISLE') NOT NULL DEFAULT 'NO_PREFERENCE',
    seat_id INT NULL,
    allocated_berth VARCHAR(30) NULL,
    passenger_status ENUM('CONFIRMED', 'RAC', 'WAITLISTED', 'CANCELLED') NOT NULL DEFAULT 'CONFIRMED',
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (seat_id) REFERENCES seats(id) ON DELETE SET NULL,
    INDEX idx_passenger_booking (booking_id),
    INDEX idx_passenger_seat (seat_id)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 10: tickets
-- Electronic Reservation Slip (ERS) ticket identification.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    ticket_number VARCHAR(30) NOT NULL UNIQUE,
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    INDEX idx_ticket_booking (booking_id),
    INDEX idx_ticket_number (ticket_number)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 11: seat_allocations
-- Date-specific relational allocation model preventing double-booking race conditions.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS seat_allocations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    train_id INT NOT NULL,
    seat_id INT NOT NULL,
    journey_date DATE NOT NULL,
    booking_id INT NOT NULL,
    passenger_id INT NOT NULL,
    allocated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (train_id) REFERENCES trains(id) ON DELETE CASCADE,
    FOREIGN KEY (seat_id) REFERENCES seats(id) ON DELETE CASCADE,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (passenger_id) REFERENCES passengers(id) ON DELETE CASCADE,
    UNIQUE KEY uq_seat_date_allocated (seat_id, journey_date),
    INDEX idx_train_date_alloc (train_id, journey_date)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 12: waitlist_entries
-- Tracks RAC and Waiting List queue orders for auto-promotion on cancellation.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS waitlist_entries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    train_id INT NOT NULL,
    journey_date DATE NOT NULL,
    travel_class ENUM('1A', '2A', '3A', 'SL', 'CC') NOT NULL DEFAULT 'CC',
    booking_id INT NOT NULL,
    passenger_id INT NOT NULL,
    entry_type ENUM('RAC', 'WL') NOT NULL DEFAULT 'WL',
    queue_number INT NOT NULL,
    current_status ENUM('WAITING', 'PROMOTED', 'CANCELLED') NOT NULL DEFAULT 'WAITING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (train_id) REFERENCES trains(id) ON DELETE CASCADE,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (passenger_id) REFERENCES passengers(id) ON DELETE CASCADE,
    INDEX idx_wl_queue (train_id, journey_date, travel_class, entry_type, current_status)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 13: payments
-- Simulated payment transactions with payment method, gateway, and bank reference.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    transaction_id VARCHAR(50) NOT NULL UNIQUE,
    payment_method ENUM('UPI', 'CARD', 'NET_BANKING') NOT NULL DEFAULT 'UPI',
    payment_gateway VARCHAR(50) NOT NULL DEFAULT 'Simulated Indian RailPay',
    amount DECIMAL(10, 2) NOT NULL,
    status ENUM('SUCCESS', 'FAILED', 'REFUNDED') NOT NULL DEFAULT 'SUCCESS',
    bank_ref_number VARCHAR(50) NOT NULL,
    payment_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    INDEX idx_pay_booking (booking_id),
    INDEX idx_pay_txn (transaction_id)
) ENGINE=InnoDB;

-- ----------------------------------------------------------------------------
-- Table 14: cancellations
-- Audit trail of cancelled bookings with calculated cancellation fees and refunds.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cancellations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    cancellation_number VARCHAR(50) NOT NULL UNIQUE,
    cancelled_by_user_id INT NOT NULL,
    gross_amount DECIMAL(10, 2) NOT NULL,
    cancellation_charge DECIMAL(10, 2) NOT NULL,
    refund_amount DECIMAL(10, 2) NOT NULL,
    refund_status ENUM('INITIATED', 'PROCESSED', 'COMPLETED') NOT NULL DEFAULT 'COMPLETED',
    seats_released INT NOT NULL DEFAULT 1,
    waitlist_promoted_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (cancelled_by_user_id) REFERENCES users(id) ON DELETE RESTRICT,
    INDEX idx_canc_booking (booking_id),
    INDEX idx_canc_user (cancelled_by_user_id)
) ENGINE=InnoDB;
