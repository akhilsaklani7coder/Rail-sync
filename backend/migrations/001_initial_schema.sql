-- RailSync Initial Database Schema (MySQL 8 / InnoDB)
-- Normalized 3NF Schema with Foreign Keys, Indexes, and Relational Seat Allocation Model

CREATE DATABASE IF NOT EXISTS railsync_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE railsync_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('USER', 'ADMIN') NOT NULL DEFAULT 'USER',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_email (email)
) ENGINE=InnoDB;

-- 2. Stations Table
CREATE TABLE IF NOT EXISTS stations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    station_code VARCHAR(10) NOT NULL UNIQUE,
    station_name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    INDEX idx_station_code (station_code),
    INDEX idx_station_city (city)
) ENGINE=InnoDB;

-- 3. Routes Table (Graph edges for Dijkstra and train connectivity)
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

-- 4. Trains Table
CREATE TABLE IF NOT EXISTS trains (
    id INT AUTO_INCREMENT PRIMARY KEY,
    train_number VARCHAR(20) NOT NULL UNIQUE,
    train_name VARCHAR(150) NOT NULL,
    source_station_id INT NOT NULL,
    destination_station_id INT NOT NULL,
    departure_time TIME NOT NULL,
    arrival_time TIME NOT NULL,
    running_days VARCHAR(50) NOT NULL DEFAULT 'DAILY', -- e.g. DAILY or MON,TUE,WED
    base_fare DECIMAL(10, 2) NOT NULL DEFAULT 500.00,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (source_station_id) REFERENCES stations(id) ON DELETE RESTRICT,
    FOREIGN KEY (destination_station_id) REFERENCES stations(id) ON DELETE RESTRICT,
    INDEX idx_train_search (source_station_id, destination_station_id, is_active),
    INDEX idx_train_number (train_number)
) ENGINE=InnoDB;

-- 5. Coaches Table
CREATE TABLE IF NOT EXISTS coaches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    train_id INT NOT NULL,
    coach_number VARCHAR(10) NOT NULL, -- e.g. 'A1', 'B1', 'S1'
    coach_type ENUM('1A', '2A', '3A', 'SL', 'CC') NOT NULL DEFAULT 'SL',
    total_seats INT NOT NULL DEFAULT 32,
    FOREIGN KEY (train_id) REFERENCES trains(id) ON DELETE CASCADE,
    UNIQUE KEY uq_train_coach (train_id, coach_number),
    INDEX idx_coach_train (train_id)
) ENGINE=InnoDB;

-- 6. Seats Table (Physical layout template)
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

-- 7. Bookings Table
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pnr VARCHAR(12) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    train_id INT NOT NULL,
    journey_date DATE NOT NULL,
    booking_status ENUM('CONFIRMED', 'CANCELLED', 'FAILED') NOT NULL DEFAULT 'CONFIRMED',
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_status ENUM('PENDING', 'SUCCESS', 'FAILED', 'REFUNDED') NOT NULL DEFAULT 'SUCCESS',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMP NULL DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (train_id) REFERENCES trains(id) ON DELETE RESTRICT,
    INDEX idx_booking_user (user_id),
    INDEX idx_booking_pnr (pnr),
    INDEX idx_booking_train_date (train_id, journey_date)
) ENGINE=InnoDB;

-- 8. Passengers Table
CREATE TABLE IF NOT EXISTS passengers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender ENUM('MALE', 'FEMALE', 'OTHER') NOT NULL,
    seat_id INT NOT NULL,
    passenger_status ENUM('CONFIRMED', 'CANCELLED') NOT NULL DEFAULT 'CONFIRMED',
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (seat_id) REFERENCES seats(id) ON DELETE RESTRICT,
    INDEX idx_passenger_booking (booking_id),
    INDEX idx_passenger_seat (seat_id)
) ENGINE=InnoDB;

-- 9. Tickets Table
CREATE TABLE IF NOT EXISTS tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    ticket_number VARCHAR(30) NOT NULL UNIQUE,
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    INDEX idx_ticket_booking (booking_id),
    INDEX idx_ticket_number (ticket_number)
) ENGINE=InnoDB;

-- 10. Seat Allocations Table (Date-Specific Relational Allocation Model)
-- Prevents duplicate booking of the same seat on the same train on the same date.
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
