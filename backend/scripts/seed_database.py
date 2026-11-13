import sys
import os

# Add parent directory to sys.path so app can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from werkzeug.security import generate_password_hash
from app.config import Config
from app.database.connection import get_db_connection, init_connection_pool

def seed_database():
    """
    Idempotent database seeder for RailSync.
    Seeds realistic sample stations, routes, trains, coaches, and seats for major Indian corridors.
    """
    print("Connecting to MySQL to seed RailSync database...")
    init_connection_pool()
    
    with get_db_connection() as (conn, cursor):
        # 1. Seed Users (Admin and Demo User)
        users_data = [
            ("Admin User", "admin@railsync.com", "Admin@123", "ADMIN"),
            ("Demo Passenger", "user@railsync.com", "User@123", "USER")
        ]
        
        for name, email, password, role in users_data:
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if not cursor.fetchone():
                pw_hash = generate_password_hash(password)
                cursor.execute(
                    "INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                    (name, email, pw_hash, role)
                )
                print(f"Created {role} user: {email}")

        # 2. Seed 20 Major Indian Railway Stations (Normalized 3NF)
        stations = [
            ("NDLS", "New Delhi Railway Station", "New Delhi"),
            ("MMCT", "Mumbai Central", "Mumbai"),
            ("CSMT", "Chhatrapati Shivaji Maharaj Terminus", "Mumbai"),
            ("SBC", "KSR Bengaluru City Junction", "Bengaluru"),
            ("MAS", "Puratchi Thalaivar Dr. M.G. Ramachandran Central", "Chennai"),
            ("HWH", "Howrah Junction", "Kolkata"),
            ("DDN", "Dehradun Railway Station", "Dehradun"),
            ("HW", "Haridwar Junction", "Haridwar"),
            ("LKO", "Lucknow Charbagh", "Lucknow"),
            ("JP", "Jaipur Junction", "Jaipur"),
            ("ADI", "Ahmedabad Junction", "Ahmedabad"),
            ("PUNE", "Pune Junction", "Pune"),
            ("HYB", "Hyderabad Deccan", "Hyderabad"),
            ("SC", "Secunderabad Junction", "Secunderabad"),
            ("ASR", "Amritsar Junction", "Amritsar"),
            ("BSB", "Varanasi Junction", "Varanasi"),
            ("AGC", "Agra Cantt", "Agra"),
            ("BPL", "Bhopal Junction", "Bhopal"),
            ("PNBE", "Patna Junction", "Patna"),
            ("VSKP", "Visakhapatnam Junction", "Visakhapatnam"),
        ]
        
        station_id_map = {}
        for code, name, city in stations:
            cursor.execute("SELECT id FROM stations WHERE station_code = %s", (code,))
            row = cursor.fetchone()
            if not row:
                cursor.execute(
                    "INSERT INTO stations (station_code, station_name, city, is_active) VALUES (%s, %s, %s, 1)",
                    (code, name, city)
                )
                station_id_map[code] = cursor.lastrowid
                print(f"Seeded station: {code} - {name} ({city})")
            else:
                station_id_map[code] = row['id']
                # Ensure is_active is 1
                cursor.execute("UPDATE stations SET is_active = 1, station_name = %s, city = %s WHERE id = %s", (name, city, row['id']))

        # 3. Seed Routes (Bidirectional physical edges for Dijkstra network graph)
        routes = [
            # Northern Corridors
            ("NDLS", "DDN", 302, 360),
            ("DDN", "NDLS", 302, 360),
            ("NDLS", "HW", 250, 270),
            ("HW", "NDLS", 250, 270),
            ("HW", "DDN", 52, 75),
            ("DDN", "HW", 52, 75),
            ("NDLS", "AGC", 195, 100),
            ("AGC", "NDLS", 195, 100),
            ("AGC", "BPL", 390, 270),
            ("BPL", "AGC", 390, 270),
            ("BPL", "MMCT", 830, 650),
            ("MMCT", "BPL", 830, 650),
            ("NDLS", "ASR", 448, 360),
            ("ASR", "NDLS", 448, 360),
            ("NDLS", "JP", 308, 270),
            ("JP", "NDLS", 308, 270),
            ("JP", "ADI", 625, 540),
            ("ADI", "JP", 625, 540),
            
            # Central / Western Corridors
            ("NDLS", "MMCT", 1384, 960),
            ("MMCT", "NDLS", 1384, 960),
            ("NDLS", "CSMT", 1384, 980),
            ("CSMT", "NDLS", 1384, 980),
            ("MMCT", "ADI", 493, 380),
            ("ADI", "MMCT", 493, 380),
            ("CSMT", "PUNE", 192, 190),
            ("PUNE", "CSMT", 192, 190),
            ("MMCT", "CSMT", 10, 25),
            ("CSMT", "MMCT", 10, 25),

            # Eastern Corridors
            ("NDLS", "LKO", 512, 420),
            ("LKO", "NDLS", 512, 420),
            ("LKO", "BSB", 300, 270),
            ("BSB", "LKO", 300, 270),
            ("NDLS", "BSB", 790, 480),
            ("BSB", "NDLS", 790, 480),
            ("BSB", "PNBE", 230, 210),
            ("PNBE", "BSB", 230, 210),
            ("PNBE", "HWH", 535, 410),
            ("HWH", "PNBE", 535, 410),
            ("NDLS", "HWH", 1447, 1020),
            ("HWH", "NDLS", 1447, 1020),

            # Southern Corridors
            ("SBC", "MAS", 358, 290),
            ("MAS", "SBC", 358, 290),
            ("SBC", "HYB", 620, 660),
            ("HYB", "SBC", 620, 660),
            ("HYB", "SC", 10, 20),
            ("SC", "HYB", 10, 20),
            ("SC", "VSKP", 700, 510),
            ("VSKP", "SC", 700, 510),
            ("MAS", "VSKP", 780, 660),
            ("VSKP", "MAS", 780, 660),
            ("NDLS", "SBC", 2400, 2000),
            ("SBC", "NDLS", 2400, 2000),
            ("NDLS", "MAS", 2180, 1900),
            ("MAS", "NDLS", 2180, 1900),
            ("NDLS", "BPL", 700, 480),
            ("BPL", "NDLS", 700, 480),
        ]

        for src, dst, dist, dur in routes:
            src_id = station_id_map[src]
            dst_id = station_id_map[dst]
            cursor.execute(
                "SELECT id FROM routes WHERE source_station_id = %s AND destination_station_id = %s",
                (src_id, dst_id)
            )
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO routes (source_station_id, destination_station_id, distance_km, travel_duration_minutes) "
                    "VALUES (%s, %s, %s, %s)",
                    (src_id, dst_id, dist, dur)
                )

        # 4. Seed Trains (Simulated Express & Flagship Services)
        trains = [
            # Northern / Dehradun
            ("12017", "Dehradun Shatabdi Express", "NDLS", "DDN", "06:45:00", "12:55:00", "DAILY", 750.00),
            ("12018", "New Delhi Shatabdi Express", "DDN", "NDLS", "17:00:00", "22:50:00", "DAILY", 750.00),
            ("12055", "Dehradun Jan Shatabdi Express", "NDLS", "HW", "15:20:00", "19:30:00", "DAILY", 480.00),
            ("12056", "New Delhi Jan Shatabdi Express", "HW", "NDLS", "06:00:00", "11:15:00", "DAILY", 480.00),

            # Western / Mumbai
            ("12952", "Mumbai Tejas Rajdhani Express", "NDLS", "MMCT", "16:55:00", "08:35:00", "DAILY", 1850.00),
            ("12951", "New Delhi Tejas Rajdhani Express", "MMCT", "NDLS", "17:00:00", "08:32:00", "DAILY", 1850.00),
            ("22222", "CSMT Mumbai Rajdhani Express", "NDLS", "CSMT", "16:55:00", "11:15:00", "DAILY", 1820.00),
            ("22221", "Hazrat Nizamuddin Rajdhani Express", "CSMT", "NDLS", "16:00:00", "09:55:00", "DAILY", 1820.00),
            ("12009", "Mumbai - Ahmedabad Shatabdi", "MMCT", "ADI", "06:20:00", "12:45:00", "DAILY", 920.00),
            ("12010", "Ahmedabad - Mumbai Shatabdi", "ADI", "MMCT", "15:10:00", "21:45:00", "DAILY", 920.00),
            ("12123", "Deccan Queen Express", "CSMT", "PUNE", "17:10:00", "20:25:00", "DAILY", 360.00),
            ("12124", "Deccan Queen Express (Return)", "PUNE", "CSMT", "07:15:00", "10:25:00", "DAILY", 360.00),

            # Jaipur Corridor
            ("12015", "Ajmer Shatabdi Express", "NDLS", "JP", "06:10:00", "10:40:00", "DAILY", 680.00),
            ("12016", "New Delhi Shatabdi Express", "JP", "NDLS", "17:50:00", "22:20:00", "DAILY", 680.00),

            # Eastern / Varanasi / Kolkata
            ("22436", "Vande Bharat Express", "NDLS", "BSB", "06:00:00", "14:00:00", "DAILY", 1450.00),
            ("22435", "Vande Bharat Express (Return)", "BSB", "NDLS", "15:00:00", "23:00:00", "DAILY", 1450.00),
            ("12004", "Lucknow Shatabdi Express", "NDLS", "LKO", "06:10:00", "12:40:00", "DAILY", 790.00),
            ("12003", "New Delhi Shatabdi Express", "LKO", "NDLS", "15:30:00", "22:15:00", "DAILY", 790.00),
            ("12302", "Howrah Rajdhani Express", "NDLS", "HWH", "16:50:00", "09:55:00", "DAILY", 2150.00),
            ("12301", "New Delhi Rajdhani Express", "HWH", "NDLS", "16:50:00", "10:05:00", "DAILY", 2150.00),
            ("22348", "Patna - Howrah Vande Bharat", "PNBE", "HWH", "08:00:00", "14:35:00", "DAILY", 1240.00),
            ("22347", "Howrah - Patna Vande Bharat", "HWH", "PNBE", "15:50:00", "22:40:00", "DAILY", 1240.00),

            # Southern / Bengaluru / Chennai / Hyderabad
            ("12628", "Karnataka Express", "NDLS", "SBC", "20:20:00", "12:00:00", "DAILY", 2200.00),
            ("12627", "Karnataka Express (Return)", "SBC", "NDLS", "19:20:00", "10:30:00", "DAILY", 2200.00),
            ("12622", "Tamil Nadu Express", "NDLS", "MAS", "21:05:00", "06:15:00", "DAILY", 2180.00),
            ("12621", "Tamil Nadu Express (Return)", "MAS", "NDLS", "22:00:00", "07:40:00", "DAILY", 2180.00),
            ("12028", "Bengaluru - Chennai Shatabdi", "SBC", "MAS", "06:00:00", "11:00:00", "DAILY", 860.00),
            ("12027", "Chennai - Bengaluru Shatabdi", "MAS", "SBC", "17:30:00", "22:25:00", "DAILY", 860.00),
            ("12786", "Kacheguda Superfast Express", "SBC", "HYB", "18:20:00", "05:40:00", "DAILY", 740.00),
            ("12785", "Bengaluru Superfast Express", "HYB", "SBC", "19:05:00", "06:25:00", "DAILY", 740.00),
            ("20678", "Vande Bharat Express", "MAS", "VSKP", "05:15:00", "14:10:00", "DAILY", 1620.00),
            ("20677", "Vande Bharat Express (Return)", "VSKP", "MAS", "14:30:00", "23:30:00", "DAILY", 1620.00),

            # Central Corridors
            ("12002", "Bhopal Shatabdi Express", "NDLS", "BPL", "06:00:00", "14:40:00", "DAILY", 1150.00),
            ("12001", "New Delhi Shatabdi Express", "BPL", "NDLS", "15:00:00", "23:45:00", "DAILY", 1150.00),
            ("12050", "Gatimaan Express", "NDLS", "AGC", "08:10:00", "09:50:00", "DAILY", 540.00),
            ("12049", "Gatimaan Express (Return)", "AGC", "NDLS", "17:50:00", "19:30:00", "DAILY", 540.00),
            ("12013", "Amritsar Shatabdi Express", "NDLS", "ASR", "16:30:00", "22:30:00", "DAILY", 840.00),
            ("12014", "New Delhi Shatabdi Express", "ASR", "NDLS", "04:55:00", "11:05:00", "DAILY", 840.00),
        ]

        train_id_map = {}
        for number, name, src, dst, dep, arr, days, fare in trains:
            cursor.execute("SELECT id FROM trains WHERE train_number = %s", (number,))
            row = cursor.fetchone()
            if not row:
                cursor.execute(
                    "INSERT INTO trains (train_number, train_name, source_station_id, destination_station_id, "
                    "departure_time, arrival_time, running_days, base_fare, is_active) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)",
                    (number, name, station_id_map[src], station_id_map[dst], dep, arr, days, fare)
                )
                train_id_map[number] = cursor.lastrowid
                print(f"Seeded train: {number} - {name} ({src} -> {dst})")
            else:
                train_id_map[number] = row['id']
                cursor.execute(
                    "UPDATE trains SET is_active = 1, train_name = %s, base_fare = %s WHERE id = %s",
                    (name, fare, row['id'])
                )

        # 5. Seed Coaches and Seats for Each Train (Idempotent)
        berth_types = ['WINDOW', 'AISLE', 'MIDDLE', 'LOWER', 'UPPER', 'SIDE LOWER', 'SIDE UPPER']
        coaches_config = [
            ("C1", "CC", 16),
            ("B1", "3A", 16)
        ]
        
        for number, t_id in train_id_map.items():
            for c_no, c_type, total in coaches_config:
                cursor.execute(
                    "SELECT id FROM coaches WHERE train_id = %s AND coach_number = %s",
                    (t_id, c_no)
                )
                c_row = cursor.fetchone()
                if not c_row:
                    cursor.execute(
                        "INSERT INTO coaches (train_id, coach_number, coach_type, total_seats) "
                        "VALUES (%s, %s, %s, %s)",
                        (t_id, c_no, c_type, total)
                    )
                    coach_id = cursor.lastrowid
                    
                    # Insert seats for this coach
                    for s_num in range(1, total + 1):
                        b_type = berth_types[(s_num - 1) % len(berth_types)]
                        cursor.execute(
                            "INSERT INTO seats (coach_id, seat_number, berth_type, is_active) VALUES (%s, %s, %s, 1)",
                            (coach_id, s_num, b_type)
                        )
                else:
                    coach_id = c_row['id']
                    # Verify seats exist
                    cursor.execute("SELECT COUNT(*) as count FROM seats WHERE coach_id = %s", (coach_id,))
                    seat_count = cursor.fetchone()['count']
                    if seat_count < total:
                        for s_num in range(seat_count + 1, total + 1):
                            b_type = berth_types[(s_num - 1) % len(berth_types)]
                            cursor.execute(
                                "INSERT INTO seats (coach_id, seat_number, berth_type, is_active) VALUES (%s, %s, %s, 1)",
                                (coach_id, s_num, b_type)
                            )
                
    print(f"Database seeding completed successfully! Seeded {len(stations)} stations, {len(routes)} routes, and {len(trains)} trains.")

if __name__ == "__main__":
    seed_database()
