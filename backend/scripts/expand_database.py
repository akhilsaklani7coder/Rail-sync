import os
import sys
import mysql.connector

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.config import Config

def expand_database():
    print("Connecting to MySQL to expand RailSync database for Phase 3...")
    conn = mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )
    conn.autocommit = True
    cursor = conn.cursor(dictionary=True)

    # 1. Expand users table with phone and address
    print("1. Updating 'users' table schema...")
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN phone VARCHAR(20) NULL AFTER email")
    except mysql.connector.Error as e:
        if "Duplicate column name" not in str(e):
            print(f"  users.phone notice: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN address VARCHAR(255) NULL AFTER phone")
    except mysql.connector.Error as e:
        if "Duplicate column name" not in str(e):
            print(f"  users.address notice: {e}")

    # Set default values for admin and demo user
    cursor.execute("UPDATE users SET phone = '+91 98765 43210', address = 'Connaught Place, New Delhi, India' WHERE email = 'admin@railsync.com' AND (phone IS NULL OR phone = '')")
    cursor.execute("UPDATE users SET phone = '+91 91234 56789', address = 'Bandra West, Mumbai, Maharashtra' WHERE email = 'user@railsync.com' AND (phone IS NULL OR phone = '')")

    # 2. Expand trains table with train_type
    print("2. Updating 'trains' table schema...")
    try:
        cursor.execute("ALTER TABLE trains ADD COLUMN train_type ENUM('VANDE_BHARAT', 'RAJDHANI', 'SHATABDI', 'SUPERFAST', 'EXPRESS') NOT NULL DEFAULT 'EXPRESS' AFTER train_name")
    except mysql.connector.Error as e:
        if "Duplicate column name" not in str(e):
            print(f"  trains.train_type notice: {e}")

    # Update train_type based on train_name
    cursor.execute("UPDATE trains SET train_type = 'VANDE_BHARAT' WHERE train_name LIKE '%Vande Bharat%'")
    cursor.execute("UPDATE trains SET train_type = 'RAJDHANI' WHERE train_name LIKE '%Rajdhani%'")
    cursor.execute("UPDATE trains SET train_type = 'SHATABDI' WHERE train_name LIKE '%Shatabdi%'")
    cursor.execute("UPDATE trains SET train_type = 'SUPERFAST' WHERE train_name LIKE '%Superfast%' OR train_name LIKE '%Tejas%' OR train_name LIKE '%Gatimaan%'")

    # 3. Create 'train_stops' table for intermediate timetable stations
    print("3. Creating 'train_stops' table...")
    cursor.execute("""
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
    """)

    # 4. Expand bookings table
    print("4. Updating 'bookings' table schema...")
    try:
        cursor.execute("ALTER TABLE bookings MODIFY COLUMN booking_status ENUM('CONFIRMED', 'RAC', 'WAITLISTED', 'CANCELLED', 'FAILED') NOT NULL DEFAULT 'CONFIRMED'")
    except mysql.connector.Error as e:
        print(f"  bookings status modify notice: {e}")

    for col_def in [
        ("travel_class ENUM('1A', '2A', '3A', 'SL', 'CC') NOT NULL DEFAULT 'CC'", "travel_class"),
        ("base_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00", "base_amount"),
        ("reservation_fee DECIMAL(10, 2) NOT NULL DEFAULT 40.00", "reservation_fee"),
        ("superfast_charge DECIMAL(10, 2) NOT NULL DEFAULT 45.00", "superfast_charge"),
        ("gst_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00", "gst_amount")
    ]:
        try:
            cursor.execute(f"ALTER TABLE bookings ADD COLUMN {col_def[0]}")
        except mysql.connector.Error as e:
            if "Duplicate column name" not in str(e):
                print(f"  bookings.{col_def[1]} notice: {e}")

    # 5. Expand passengers table
    print("5. Updating 'passengers' table schema...")
    try:
        cursor.execute("ALTER TABLE passengers MODIFY COLUMN passenger_status ENUM('CONFIRMED', 'RAC', 'WAITLISTED', 'CANCELLED') NOT NULL DEFAULT 'CONFIRMED'")
    except mysql.connector.Error as e:
        print(f"  passengers status modify notice: {e}")

    try:
        cursor.execute("ALTER TABLE passengers MODIFY COLUMN seat_id INT NULL")
    except mysql.connector.Error as e:
        print(f"  passengers seat_id modify notice: {e}")

    for col_def in [
        ("berth_preference ENUM('NO_PREFERENCE', 'LOWER', 'MIDDLE', 'UPPER', 'SIDE LOWER', 'SIDE UPPER', 'WINDOW', 'AISLE') NOT NULL DEFAULT 'NO_PREFERENCE'", "berth_preference"),
        ("allocated_berth VARCHAR(30) NULL", "allocated_berth")
    ]:
        try:
            cursor.execute(f"ALTER TABLE passengers ADD COLUMN {col_def[0]}")
        except mysql.connector.Error as e:
            if "Duplicate column name" not in str(e):
                print(f"  passengers.{col_def[1]} notice: {e}")

    # 6. Create 'waitlist_entries' table
    print("6. Creating 'waitlist_entries' table...")
    cursor.execute("""
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
            INDEX idx_wl_lookup (train_id, journey_date, travel_class, entry_type, current_status)
        ) ENGINE=InnoDB;
    """)

    # 7. Create 'payments' table
    print("7. Creating 'payments' table...")
    cursor.execute("""
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
    """)

    # 8. Create 'cancellations' table
    print("8. Creating 'cancellations' table...")
    cursor.execute("""
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
    """)

    # 9. Expand stations to 32 major hubs
    print("9. Seeding additional major Indian railway stations (target: 32)...")
    additional_stations = [
        ("CDG", "Chandigarh Junction", "Chandigarh"),
        ("ST", "Surat Railway Station", "Surat"),
        ("BVC", "Bhavnagar Terminus", "Bhavnagar"),
        ("NGP", "Nagpur Junction", "Nagpur"),
        ("GWL", "Gwalior Junction", "Gwalior"),
        ("JBP", "Jabalpur Junction", "Jabalpur"),
        ("GHY", "Guwahati Railway Station", "Guwahati"),
        ("BBS", "Bhubaneswar Railway Station", "Bhubaneswar"),
        ("RNC", "Ranchi Junction", "Ranchi"),
        ("TVC", "Thiruvananthapuram Central", "Thiruvananthapuram"),
        ("MAO", "Madgaon Junction (Goa)", "Goa"),
        ("MYS", "Mysuru Junction", "Mysuru"),
    ]

    for code, name, city in additional_stations:
        cursor.execute("SELECT id FROM stations WHERE station_code = %s", (code,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO stations (station_code, station_name, city, is_active) VALUES (%s, %s, %s, 1)",
                (code, name, city)
            )
            print(f"  Seeded station: {code} - {name} ({city})")

    # Re-index all stations
    cursor.execute("SELECT id, station_code FROM stations")
    stn_map = {row['station_code']: row['id'] for row in cursor.fetchall()}

    # 10. Seed Intermediate Route Stops (Timetable) for all flagship trains
    print("10. Seeding realistic intermediate train stops (timetables)...")
    # For every train, create 3 to 6 stops from source to destination
    # Sample realistic timetables:
    cursor.execute("SELECT id, train_number, train_name, source_station_id, destination_station_id, departure_time, arrival_time FROM trains")
    all_trains = cursor.fetchall()

    intermediate_corridors = {
        # NDLS -> DDN (via HW, Meerut/Roorkee)
        ("NDLS", "DDN"): [
            ("NDLS", "06:45:00", "06:45:00", 0, 0),
            ("AGC", "08:15:00", "08:20:00", 5, 120),
            ("HW", "11:20:00", "11:30:00", 10, 250),
            ("DDN", "12:55:00", "12:55:00", 0, 302)
        ],
        ("DDN", "NDLS"): [
            ("DDN", "17:00:00", "17:00:00", 0, 0),
            ("HW", "18:05:00", "18:15:00", 10, 52),
            ("AGC", "21:10:00", "21:15:00", 5, 180),
            ("NDLS", "22:50:00", "22:50:00", 0, 302)
        ],
        # NDLS -> MMCT (via AGC, BPL, ST)
        ("NDLS", "MMCT"): [
            ("NDLS", "16:55:00", "16:55:00", 0, 0),
            ("AGC", "18:45:00", "18:50:00", 5, 195),
            ("BPL", "23:45:00", "23:55:00", 10, 585),
            ("ST", "06:05:00", "06:10:00", 5, 1120),
            ("MMCT", "08:35:00", "08:35:00", 0, 1384)
        ],
        ("MMCT", "NDLS"): [
            ("MMCT", "17:00:00", "17:00:00", 0, 0),
            ("ST", "19:15:00", "19:20:00", 5, 264),
            ("BPL", "01:45:00", "01:55:00", 10, 799),
            ("AGC", "06:45:00", "06:50:00", 5, 1189),
            ("NDLS", "08:32:00", "08:32:00", 0, 1384)
        ],
        # NDLS -> BSB (Vande Bharat via LKO)
        ("NDLS", "BSB"): [
            ("NDLS", "06:00:00", "06:00:00", 0, 0),
            ("AGC", "07:35:00", "07:40:00", 5, 195),
            ("LKO", "10:50:00", "11:00:00", 10, 512),
            ("BSB", "14:00:00", "14:00:00", 0, 790)
        ],
        ("BSB", "NDLS"): [
            ("BSB", "15:00:00", "15:00:00", 0, 0),
            ("LKO", "18:00:00", "18:10:00", 10, 278),
            ("AGC", "21:20:00", "21:25:00", 5, 595),
            ("NDLS", "23:00:00", "23:00:00", 0, 790)
        ],
        # NDLS -> HWH (Howrah Rajdhani via AGC, LKO, BSB, PNBE)
        ("NDLS", "HWH"): [
            ("NDLS", "16:50:00", "16:50:00", 0, 0),
            ("AGC", "18:40:00", "18:45:00", 5, 195),
            ("BSB", "01:20:00", "01:30:00", 10, 790),
            ("PNBE", "04:30:00", "04:40:00", 10, 1020),
            ("HWH", "09:55:00", "09:55:00", 0, 1447)
        ],
        ("HWH", "NDLS"): [
            ("HWH", "16:50:00", "16:50:00", 0, 0),
            ("PNBE", "22:15:00", "22:25:00", 10, 427),
            ("BSB", "01:30:00", "01:40:00", 10, 657),
            ("AGC", "08:10:00", "08:15:00", 5, 1252),
            ("NDLS", "10:05:00", "10:05:00", 0, 1447)
        ],
        # SBC -> MAS (Bengaluru - Chennai Shatabdi)
        ("SBC", "MAS"): [
            ("SBC", "06:00:00", "06:00:00", 0, 0),
            ("MYS", "07:45:00", "07:50:00", 5, 139),
            ("MAS", "11:00:00", "11:00:00", 0, 358)
        ],
        ("MAS", "SBC"): [
            ("MAS", "17:30:00", "17:30:00", 0, 0),
            ("MYS", "20:30:00", "20:35:00", 5, 219),
            ("SBC", "22:25:00", "22:25:00", 0, 358)
        ]
    }

    # Map station ID to code
    cursor.execute("SELECT id, station_code FROM stations")
    id_to_code = {row['id']: row['station_code'] for row in cursor.fetchall()}

    seeded_stops_count = 0
    for t in all_trains:
        t_id = t['id']
        s_code = id_to_code.get(t['source_station_id'])
        d_code = id_to_code.get(t['destination_station_id'])

        # Check if stops already exist
        cursor.execute("SELECT COUNT(*) AS c FROM train_stops WHERE train_id = %s", (t_id,))
        if cursor.fetchone()['c'] > 0:
            continue

        stops_pattern = intermediate_corridors.get((s_code, d_code))
        if not stops_pattern:
            # Fallback 2-stop pattern (source and destination)
            stops_pattern = [
                (s_code, t['departure_time'], t['departure_time'], 0, 0),
                (d_code, t['arrival_time'], t['arrival_time'], 0, 450)
            ]

        for seq, (stn_code, arr, dep, halt, dist) in enumerate(stops_pattern, start=1):
            if stn_code in stn_map:
                cursor.execute("""
                    INSERT INTO train_stops (train_id, station_id, stop_sequence, arrival_time, departure_time, halt_minutes, distance_from_origin_km, day_number)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
                """, (t_id, stn_map[stn_code], seq, arr, dep, halt, dist))
                seeded_stops_count += 1

    print(f"Seeded {seeded_stops_count} train timetable stops across {len(all_trains)} trains.")

    # 11. Add additional coaches for Sleeper (SL) and 2A to flagship trains for class selection
    print("11. Adding multi-class coach inventory (SL, 2A, 1A) for trains...")
    berth_types = ['WINDOW', 'AISLE', 'MIDDLE', 'LOWER', 'UPPER', 'SIDE LOWER', 'SIDE UPPER']
    
    for t in all_trains:
        t_id = t['id']
        # Check if SL coach already exists
        cursor.execute("SELECT id FROM coaches WHERE train_id = %s AND coach_number = 'S1'", (t_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO coaches (train_id, coach_number, coach_type, total_seats) VALUES (%s, 'S1', 'SL', 16)", (t_id,))
            s1_id = cursor.lastrowid
            for s_num in range(1, 17):
                b_type = berth_types[(s_num - 1) % len(berth_types)]
                cursor.execute("INSERT INTO seats (coach_id, seat_number, berth_type, is_active) VALUES (%s, %s, %s, 1)", (s1_id, s_num, b_type))

        # Check if 2A coach already exists
        cursor.execute("SELECT id FROM coaches WHERE train_id = %s AND coach_number = 'A1'", (t_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO coaches (train_id, coach_number, coach_type, total_seats) VALUES (%s, 'A1', '2A', 16)", (t_id,))
            a1_id = cursor.lastrowid
            for s_num in range(1, 17):
                b_type = berth_types[(s_num - 1) % len(berth_types)]
                cursor.execute("INSERT INTO seats (coach_id, seat_number, berth_type, is_active) VALUES (%s, %s, %s, 1)", (a1_id, s_num, b_type))

    conn.close()
    print("Database expansion completed successfully!")

if __name__ == '__main__':
    expand_database()
