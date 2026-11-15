import os
import sys

sys.path.insert(0, os.path.abspath("backend"))
from app.database.connection import get_db_connection

def expand_database():
    print("Starting RailSync Phase 3 Database Expansion...")
    with get_db_connection() as (conn, cursor):
        # 1. Update ENUM for trains.train_type
        print("1. Updating trains.train_type ENUM...")
        cursor.execute("""
            ALTER TABLE trains 
            MODIFY COLUMN train_type ENUM(
                'VANDE_BHARAT', 'RAJDHANI', 'SHATABDI', 
                'DURONTO', 'GARIB_RATH', 'SUPERFAST', 
                'MAIL_EXPRESS', 'INTERCITY', 'EXPRESS'
            ) NOT NULL DEFAULT 'EXPRESS';
        """)

        # 2. Update ENUM for payments.status
        print("2. Updating payments.status ENUM...")
        cursor.execute("""
            ALTER TABLE payments 
            MODIFY COLUMN status ENUM('PENDING', 'SUCCESS', 'FAILED', 'REFUNDED') NOT NULL DEFAULT 'SUCCESS';
        """)

        # 3. Add Key Hub Stations
        print("3. Inserting Key Junction Stations...")
        new_stations = [
            (40, 'CNB', 'Kanpur Central', 'Kanpur'),
            (41, 'PRYJ', 'Prayagraj Junction', 'Prayagraj'),
            (42, 'DDU', 'Pt. Deen Dayal Upadhyaya Junction', 'Mughalsarai'),
            (43, 'KOTA', 'Kota Junction', 'Kota'),
            (44, 'BRC', 'Vadodara Junction', 'Vadodara'),
            (45, 'BVI', 'Borivali', 'Mumbai'),
            (46, 'TNA', 'Thane Junction', 'Mumbai'),
            (47, 'KYN', 'Kalyan Junction', 'Kalyan'),
            (48, 'LNL', 'Lonavala Railway Station', 'Lonavala'),
            (49, 'UMB', 'Ambala Cantt Junction', 'Ambala'),
            (50, 'LDH', 'Ludhiana Junction', 'Ludhiana'),
            (51, 'BZA', 'Vijayawada Junction', 'Vijayawada')
        ]
        for s_id, code, name, city in new_stations:
            cursor.execute("""
                INSERT INTO stations (id, station_code, station_name, city, is_active)
                VALUES (%s, %s, %s, %s, TRUE)
                ON DUPLICATE KEY UPDATE station_name = VALUES(station_name), city = VALUES(city);
            """, (s_id, code, name, city))

        # 4. Add Corridors to routes
        print("4. Adding Corridors to routes table...")
        new_routes = [
            (60, 1, 40, 440, 300),   # NDLS -> CNB
            (61, 40, 1, 440, 300),   # CNB -> NDLS
            (62, 40, 4, 72, 60),     # CNB -> LKO
            (63, 4, 40, 72, 60),     # LKO -> CNB
            (64, 40, 41, 195, 140),  # CNB -> PRYJ
            (65, 41, 40, 195, 140),  # PRYJ -> CNB
            (66, 41, 42, 150, 120),  # PRYJ -> DDU
            (67, 42, 41, 150, 120),  # DDU -> PRYJ
            (68, 42, 12, 670, 520),  # DDU -> HWH
            (69, 12, 42, 670, 520),  # HWH -> DDU
            (70, 1, 43, 465, 300),   # NDLS -> KOTA
            (71, 43, 1, 465, 300),   # KOTA -> NDLS
            (72, 43, 44, 525, 360),  # KOTA -> BRC
            (73, 44, 43, 525, 360),  # BRC -> KOTA
            (74, 44, 26, 130, 90),   # BRC -> ST
            (75, 26, 44, 130, 90),   # ST -> BRC
            (76, 26, 45, 230, 180),  # ST -> BVI
            (77, 45, 26, 230, 180),  # BVI -> ST
            (78, 45, 6, 30, 35),     # BVI -> MMCT
            (79, 6, 45, 30, 35),     # MMCT -> BVI
            (80, 9, 46, 34, 40),     # CSMT -> TNA
            (81, 46, 9, 34, 40),     # TNA -> CSMT
            (82, 46, 47, 20, 25),    # TNA -> KYN
            (83, 47, 46, 20, 25),    # KYN -> TNA
            (84, 47, 48, 74, 75),    # KYN -> LNL
            (85, 48, 47, 74, 75),    # LNL -> KYN
            (86, 48, 13, 64, 60),    # LNL -> PUNE
            (87, 13, 48, 64, 60),    # PUNE -> LNL
        ]
        for r_id, s_id, d_id, dist, dur in new_routes:
            cursor.execute("""
                INSERT INTO routes (id, source_station_id, destination_station_id, distance_km, travel_duration_minutes)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE distance_km = VALUES(distance_km), travel_duration_minutes = VALUES(travel_duration_minutes);
            """, (r_id, s_id, d_id, dist, dur))

        # 5. Insert New Flagship Trains for New Categories
        print("5. Inserting New Trains (Duronto, Garib Rath, Mail Express, Intercity)...")
        new_trains = [
            # DURONTO EXPRESS
            (39, '12259', 'Sealdah - New Delhi AC Duronto Express', 'DURONTO', 12, 1, '18:30:00', '11:00:00', 'DAILY', 2250.00),
            (40, '12260', 'New Delhi - Sealdah AC Duronto Express', 'DURONTO', 1, 12, '19:45:00', '12:45:00', 'DAILY', 2250.00),
            (41, '12267', 'Mumbai Central - Ahmedabad AC Duronto', 'DURONTO', 6, 7, '23:25:00', '05:55:00', 'DAILY', 1150.00),
            (42, '12268', 'Ahmedabad - Mumbai Central AC Duronto', 'DURONTO', 7, 6, '23:45:00', '06:00:00', 'DAILY', 1150.00),
            # GARIB RATH EXPRESS
            (43, '12909', 'Bandra Terminus - Nizamuddin Garib Rath', 'GARIB_RATH', 6, 1, '17:30:00', '09:40:00', 'DAILY', 1050.00),
            (44, '12910', 'Nizamuddin - Bandra Terminus Garib Rath', 'GARIB_RATH', 1, 6, '15:35:00', '07:35:00', 'DAILY', 1050.00),
            # MAIL / EXPRESS
            (45, '12321', 'Howrah - CSMT Mumbai Mail', 'MAIL_EXPRESS', 12, 9, '23:35:00', '13:15:00', 'DAILY', 1650.00),
            (46, '12322', 'CSMT Mumbai - Howrah Mail', 'MAIL_EXPRESS', 9, 12, '21:30:00', '11:40:00', 'DAILY', 1650.00),
            # INTERCITY EXPRESS
            (47, '12127', 'Mumbai CSMT - Pune Intercity SF Express', 'INTERCITY', 9, 13, '06:40:00', '09:55:00', 'DAILY', 290.00),
            (48, '12128', 'Pune - Mumbai CSMT Intercity SF Express', 'INTERCITY', 13, 9, '17:55:00', '21:05:00', 'DAILY', 290.00),
        ]
        for t_id, t_num, t_name, t_type, s_id, d_id, dep, arr, days, fare in new_trains:
            cursor.execute("""
                INSERT INTO trains (id, train_number, train_name, train_type, source_station_id, destination_station_id, departure_time, arrival_time, running_days, base_fare, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
                ON DUPLICATE KEY UPDATE 
                    train_number = VALUES(train_number),
                    train_name = VALUES(train_name),
                    train_type = VALUES(train_type),
                    base_fare = VALUES(base_fare),
                    is_active = VALUES(is_active);
            """, (t_id, t_num, t_name, t_type, s_id, d_id, dep, arr, days, fare))

        # 6. Add Coaches for New Trains (IDs 39 to 48)
        print("6. Adding Coaches and Seats for New Trains...")
        for t_id in range(39, 49):
            cursor.execute("SELECT train_type FROM trains WHERE id = %s", (t_id,))
            t_row = cursor.fetchone()
            t_cat = t_row['train_type'] if t_row else 'EXPRESS'

            if t_cat == 'DURONTO':
                coach_configs = [('H1', '1A'), ('A1', '2A'), ('B1', '3A'), ('B2', '3A')]
            elif t_cat == 'GARIB_RATH':
                coach_configs = [('G1', '3A'), ('G2', '3A'), ('G3', '3A'), ('C1', 'CC')]
            elif t_cat == 'MAIL_EXPRESS':
                coach_configs = [('A1', '2A'), ('B1', '3A'), ('S1', 'SL'), ('S2', 'SL')]
            elif t_cat == 'INTERCITY':
                coach_configs = [('C1', 'CC'), ('C2', 'CC'), ('D1', 'CC'), ('D2', 'CC')]
            else:
                coach_configs = [('B1', '3A'), ('S1', 'SL'), ('C1', 'CC')]

            for c_num, c_type in coach_configs:
                cursor.execute("""
                    INSERT INTO coaches (train_id, coach_number, coach_type, total_seats)
                    VALUES (%s, %s, %s, 16)
                    ON DUPLICATE KEY UPDATE total_seats = VALUES(total_seats);
                """, (t_id, c_num, c_type))

                cursor.execute("SELECT id FROM coaches WHERE train_id = %s AND coach_number = %s", (t_id, c_num))
                coach_row = cursor.fetchone()
                if coach_row:
                    c_id = coach_row['id']
                    berths = ['LOWER', 'MIDDLE', 'UPPER', 'SIDE LOWER', 'SIDE UPPER', 'WINDOW', 'AISLE']
                    for s_num in range(1, 17):
                        b_type = berths[(s_num - 1) % len(berths)]
                        cursor.execute("""
                            INSERT INTO seats (coach_id, seat_number, berth_type, is_active)
                            VALUES (%s, %s, %s, TRUE)
                            ON DUPLICATE KEY UPDATE berth_type = VALUES(berth_type);
                        """, (c_id, s_num, b_type))

        # 7. Comprehensive Expansion of train_stops across Trains
        print("7. Populating Multi-Stop Timetables in train_stops...")
        cursor.execute("DELETE FROM train_stops WHERE id > 0")

        detailed_timetables = [
            # Train 1: Dehradun Shatabdi (NDLS -> DDN)
            (1, [
                (1, '06:45:00', '06:45:00', 0, 0, 1),
                (49, '08:05:00', '08:07:00', 2, 85, 1),
                (3, '11:20:00', '11:28:00', 8, 250, 1),
                (2, '12:55:00', '12:55:00', 0, 302, 1)
            ]),
            # Train 2: Return Shatabdi (DDN -> NDLS)
            (2, [
                (2, '17:00:00', '17:00:00', 0, 0, 1),
                (3, '18:10:00', '18:18:00', 8, 52, 1),
                (49, '21:20:00', '21:22:00', 2, 217, 1),
                (1, '22:50:00', '22:50:00', 0, 302, 1)
            ]),
            # Train 3: Mumbai Tejas Rajdhani (NDLS -> MMCT) - 6 Stops
            (3, [
                (1, '16:55:00', '16:55:00', 0, 0, 1),
                (43, '21:30:00', '21:40:00', 10, 465, 1),
                (44, '03:40:00', '03:50:00', 10, 990, 2),
                (26, '05:10:00', '05:15:00', 5, 1120, 2),
                (45, '07:55:00', '07:57:00', 2, 1354, 2),
                (6, '08:35:00', '08:35:00', 0, 1384, 2)
            ]),
            # Train 4: Return Tejas Rajdhani (MMCT -> NDLS) - 6 Stops
            (4, [
                (6, '17:00:00', '17:00:00', 0, 0, 1),
                (45, '17:35:00', '17:37:00', 2, 30, 1),
                (26, '19:40:00', '19:45:00', 5, 264, 1),
                (44, '21:05:00', '21:15:00', 10, 394, 1),
                (43, '03:15:00', '03:25:00', 10, 919, 2),
                (1, '08:32:00', '08:32:00', 0, 1384, 2)
            ]),
            # Train 5: Ajmer Shatabdi (NDLS -> JP) - 3 Stops
            (5, [
                (1, '06:10:00', '06:10:00', 0, 0, 1),
                (17, '08:05:00', '08:10:00', 5, 195, 1),
                (5, '10:40:00', '10:40:00', 0, 308, 1)
            ]),
            # Train 6: Return Ajmer Shatabdi (JP -> NDLS)
            (6, [
                (5, '17:50:00', '17:50:00', 0, 0, 1),
                (17, '20:15:00', '20:20:00', 5, 113, 1),
                (1, '22:20:00', '22:20:00', 0, 308, 1)
            ]),
            # Train 7: Vande Bharat Express (NDLS -> BSB) - 4 Stops
            (7, [
                (1, '06:00:00', '06:00:00', 0, 0, 1),
                (40, '10:08:00', '10:10:00', 2, 440, 1),
                (41, '12:08:00', '12:10:00', 2, 635, 1),
                (8, '14:00:00', '14:00:00', 0, 790, 1)
            ]),
            # Train 8: Jan Shatabdi (NDLS -> HW) - 3 Stops
            (8, [
                (1, '15:20:00', '15:20:00', 0, 0, 1),
                (49, '17:30:00', '17:35:00', 5, 190, 1),
                (3, '19:30:00', '19:30:00', 0, 250, 1)
            ]),
            # Train 9: Return Jan Shatabdi (HW -> NDLS)
            (9, [
                (3, '06:00:00', '06:00:00', 0, 0, 1),
                (49, '08:00:00', '08:05:00', 5, 60, 1),
                (1, '11:15:00', '11:15:00', 0, 250, 1)
            ]),
            # Train 10: CSMT Rajdhani (NDLS -> CSMT) - 6 Stops
            (10, [
                (1, '16:55:00', '16:55:00', 0, 0, 1),
                (17, '18:45:00', '18:47:00', 2, 195, 1),
                (29, '20:10:00', '20:12:00', 2, 313, 1),
                (18, '00:15:00', '00:20:00', 5, 700, 2),
                (47, '09:50:00', '09:52:00', 2, 1340, 2),
                (9, '11:15:00', '11:15:00', 0, 1384, 2)
            ]),
            # Train 11: Return CSMT Rajdhani (CSMT -> NDLS) - 6 Stops
            (11, [
                (9, '16:00:00', '16:00:00', 0, 0, 1),
                (47, '16:40:00', '16:42:00', 2, 44, 1),
                (18, '02:00:00', '02:05:00', 5, 684, 2),
                (29, '06:00:00', '06:02:00', 2, 1071, 2),
                (17, '07:30:00', '07:32:00', 2, 1189, 2),
                (1, '09:55:00', '09:55:00', 0, 1384, 2)
            ]),
            # Train 12: Mumbai - Ahmedabad Shatabdi (MMCT -> ADI) - 5 Stops
            (12, [
                (6, '06:20:00', '06:20:00', 0, 0, 1),
                (45, '06:50:00', '06:52:00', 2, 30, 1),
                (26, '09:18:00', '09:23:00', 5, 263, 1),
                (44, '10:45:00', '10:50:00', 5, 392, 1),
                (7, '12:45:00', '12:45:00', 0, 493, 1)
            ]),
            # Train 13: Ahmedabad - Mumbai Shatabdi (ADI -> MMCT) - 5 Stops
            (13, [
                (7, '15:10:00', '15:10:00', 0, 0, 1),
                (44, '16:40:00', '16:45:00', 5, 101, 1),
                (26, '18:15:00', '18:20:00', 5, 230, 1),
                (45, '20:55:00', '20:57:00', 2, 463, 1),
                (6, '21:45:00', '21:45:00', 0, 493, 1)
            ]),
            # Train 14: Deccan Queen Express (CSMT -> PUNE) - 5 Stops
            (14, [
                (9, '17:10:00', '17:10:00', 0, 0, 1),
                (46, '17:48:00', '17:50:00', 2, 34, 1),
                (47, '18:10:00', '18:12:00', 2, 54, 1),
                (48, '19:18:00', '19:20:00', 2, 128, 1),
                (13, '20:25:00', '20:25:00', 0, 192, 1)
            ]),
            # Train 15: Return Deccan Queen (PUNE -> CSMT) - 5 Stops
            (15, [
                (13, '07:15:00', '07:15:00', 0, 0, 1),
                (48, '08:15:00', '08:17:00', 2, 64, 1),
                (47, '09:20:00', '09:22:00', 2, 138, 1),
                (46, '09:43:00', '09:45:00', 2, 158, 1),
                (9, '10:25:00', '10:25:00', 0, 192, 1)
            ]),
            # Train 16: Vande Bharat Return (BSB -> NDLS) - 4 Stops
            (16, [
                (8, '15:00:00', '15:00:00', 0, 0, 1),
                (41, '16:30:00', '16:32:00', 2, 155, 1),
                (40, '18:30:00', '18:32:00', 2, 350, 1),
                (1, '23:00:00', '23:00:00', 0, 790, 1)
            ]),
            # Train 17: Lucknow Shatabdi (NDLS -> LKO) - 3 Stops
            (17, [
                (1, '06:10:00', '06:10:00', 0, 0, 1),
                (40, '11:15:00', '11:20:00', 5, 440, 1),
                (4, '12:40:00', '12:40:00', 0, 512, 1)
            ]),
            # Train 18: Return Lucknow Shatabdi (LKO -> NDLS) - 3 Stops
            (18, [
                (4, '15:30:00', '15:30:00', 0, 0, 1),
                (40, '16:50:00', '16:55:00', 5, 72, 1),
                (1, '22:15:00', '22:15:00', 0, 512, 1)
            ]),
            # Train 19: Howrah Rajdhani (NDLS -> HWH) - 6 Stops
            (19, [
                (1, '16:50:00', '16:50:00', 0, 0, 1),
                (40, '21:35:00', '21:40:00', 5, 440, 1),
                (41, '23:50:00', '23:55:00', 5, 635, 1),
                (42, '01:45:00', '01:55:00', 10, 785, 2),
                (19, '04:55:00', '05:05:00', 10, 995, 2),
                (12, '09:55:00', '09:55:00', 0, 1447, 2)
            ]),
            # Train 20: Return Howrah Rajdhani (HWH -> NDLS) - 6 Stops
            (20, [
                (12, '16:50:00', '16:50:00', 0, 0, 1),
                (19, '21:45:00', '21:55:00', 10, 452, 1),
                (42, '00:50:00', '01:00:00', 10, 662, 2),
                (41, '02:50:00', '02:55:00', 5, 812, 2),
                (40, '05:00:00', '05:05:00', 5, 1007, 2),
                (1, '10:05:00', '10:05:00', 0, 1447, 2)
            ]),
            # Train 21: Patna - Howrah Vande Bharat (PNBE -> HWH) - 3 Stops
            (21, [
                (19, '08:00:00', '08:00:00', 0, 0, 1),
                (42, '10:15:00', '10:17:00', 2, 210, 1),
                (12, '14:35:00', '14:35:00', 0, 535, 1)
            ]),
            # Train 22: Howrah - Patna Vande Bharat (HWH -> PNBE) - 3 Stops
            (22, [
                (12, '15:50:00', '15:50:00', 0, 0, 1),
                (42, '20:10:00', '20:12:00', 2, 325, 1),
                (19, '22:40:00', '22:40:00', 0, 535, 1)
            ]),
            # Train 23: Karnataka Express (NDLS -> SBC) - 7 Stops
            (23, [
                (1, '20:20:00', '20:20:00', 0, 0, 1),
                (17, '22:30:00', '22:35:00', 5, 195, 1),
                (29, '23:55:00', '23:58:00', 3, 313, 1),
                (18, '04:15:00', '04:20:00', 5, 700, 2),
                (28, '10:10:00', '10:15:00', 5, 1090, 2),
                (15, '18:40:00', '18:50:00', 10, 1665, 2),
                (10, '12:00:00', '12:00:00', 0, 2400, 3)
            ]),
            # Train 24: Return Karnataka Express (SBC -> NDLS) - 7 Stops
            (24, [
                (10, '19:20:00', '19:20:00', 0, 0, 1),
                (15, '12:10:00', '12:20:00', 10, 735, 2),
                (28, '20:45:00', '20:50:00', 5, 1310, 2),
                (18, '03:10:00', '03:15:00', 5, 1700, 3),
                (29, '07:20:00', '07:23:00', 3, 2087, 3),
                (17, '08:45:00', '08:50:00', 5, 2205, 3),
                (1, '10:30:00', '10:30:00', 0, 2400, 3)
            ]),
            # Train 25: Tamil Nadu Express (NDLS -> MAS) - 6 Stops
            (25, [
                (1, '21:05:00', '21:05:00', 0, 0, 1),
                (17, '23:15:00', '23:20:00', 5, 195, 1),
                (18, '04:55:00', '05:00:00', 5, 700, 2),
                (28, '10:50:00', '10:55:00', 5, 1090, 2),
                (51, '18:15:00', '18:25:00', 10, 1750, 2),
                (11, '06:15:00', '06:15:00', 0, 2180, 3)
            ]),
            # Train 26: Return Tamil Nadu Express (MAS -> NDLS) - 6 Stops
            (26, [
                (11, '22:00:00', '22:00:00', 0, 0, 1),
                (51, '05:15:00', '05:25:00', 10, 430, 2),
                (28, '13:00:00', '13:05:00', 5, 1090, 2),
                (18, '19:10:00', '19:15:00', 5, 1480, 2),
                (17, '04:50:00', '04:55:00', 5, 1985, 3),
                (1, '07:40:00', '07:40:00', 0, 2180, 3)
            ]),
            # Train 27: Bengaluru - Chennai Shatabdi (SBC -> MAS) - 3 Stops
            (27, [
                (10, '06:00:00', '06:00:00', 0, 0, 1),
                (51, '08:45:00', '08:47:00', 2, 215, 1),
                (11, '11:00:00', '11:00:00', 0, 358, 1)
            ]),
            # Train 28: Return Chennai - Bengaluru Shatabdi (MAS -> SBC) - 3 Stops
            (28, [
                (11, '17:30:00', '17:30:00', 0, 0, 1),
                (51, '19:40:00', '19:42:00', 2, 143, 1),
                (10, '22:25:00', '22:25:00', 0, 358, 1)
            ]),
            # Train 33: Bhopal Shatabdi (NDLS -> BPL) - 4 Stops
            (33, [
                (1, '06:00:00', '06:00:00', 0, 0, 1),
                (17, '07:50:00', '07:55:00', 5, 195, 1),
                (29, '09:23:00', '09:28:00', 5, 313, 1),
                (18, '14:40:00', '14:40:00', 0, 700, 1)
            ]),
            # Train 34: Return Bhopal Shatabdi (BPL -> NDLS) - 4 Stops
            (34, [
                (18, '15:00:00', '15:00:00', 0, 0, 1),
                (29, '20:10:00', '20:15:00', 5, 387, 1),
                (17, '21:50:00', '21:55:00', 5, 505, 1),
                (1, '23:45:00', '23:45:00', 0, 700, 1)
            ]),
            # Train 37: Amritsar Shatabdi (NDLS -> ASR) - 4 Stops
            (37, [
                (1, '16:30:00', '16:30:00', 0, 0, 1),
                (49, '19:00:00', '19:05:00', 5, 195, 1),
                (50, '20:15:00', '20:20:00', 5, 310, 1),
                (16, '22:30:00', '22:30:00', 0, 448, 1)
            ]),
            # Train 38: Return Amritsar Shatabdi (ASR -> NDLS) - 4 Stops
            (38, [
                (16, '04:55:00', '04:55:00', 0, 0, 1),
                (50, '07:05:00', '07:10:00', 5, 138, 1),
                (49, '08:25:00', '08:30:00', 5, 253, 1),
                (1, '11:05:00', '11:05:00', 0, 448, 1)
            ]),
            # Train 39: Sealdah - New Delhi Duronto (HWH -> NDLS) - 4 Stops
            (39, [
                (12, '18:30:00', '18:30:00', 0, 0, 1),
                (42, '01:25:00', '01:35:00', 10, 670, 2),
                (40, '05:30:00', '05:35:00', 5, 1010, 2),
                (1, '11:00:00', '11:00:00', 0, 1450, 2)
            ]),
            # Train 40: New Delhi - Sealdah Duronto (NDLS -> HWH) - 4 Stops
            (40, [
                (1, '19:45:00', '19:45:00', 0, 0, 1),
                (40, '00:50:00', '00:55:00', 5, 440, 2),
                (42, '04:45:00', '04:55:00', 10, 780, 2),
                (12, '12:45:00', '12:45:00', 0, 1450, 2)
            ]),
            # Train 41: Mumbai Central - Ahmedabad AC Duronto (MMCT -> ADI) - 4 Stops
            (41, [
                (6, '23:25:00', '23:25:00', 0, 0, 1),
                (26, '02:40:00', '02:45:00', 5, 263, 2),
                (44, '04:05:00', '04:10:00', 5, 392, 2),
                (7, '05:55:00', '05:55:00', 0, 493, 2)
            ]),
            # Train 42: Ahmedabad - Mumbai Central AC Duronto (ADI -> MMCT) - 4 Stops
            (42, [
                (7, '23:45:00', '23:45:00', 0, 0, 1),
                (44, '01:20:00', '01:25:00', 5, 101, 2),
                (26, '02:50:00', '02:55:00', 5, 230, 2),
                (6, '06:00:00', '06:00:00', 0, 493, 2)
            ]),
            # Train 43: Bandra - Nizamuddin Garib Rath (MMCT -> NDLS) - 6 Stops
            (43, [
                (6, '17:30:00', '17:30:00', 0, 0, 1),
                (45, '18:05:00', '18:07:00', 2, 30, 1),
                (26, '20:45:00', '20:50:00', 5, 263, 1),
                (44, '22:15:00', '22:25:00', 10, 392, 1),
                (43, '04:20:00', '04:30:00', 10, 917, 2),
                (1, '09:40:00', '09:40:00', 0, 1382, 2)
            ]),
            # Train 44: Nizamuddin - Bandra Garib Rath (NDLS -> MMCT) - 6 Stops
            (44, [
                (1, '15:35:00', '15:35:00', 0, 0, 1),
                (43, '20:40:00', '20:50:00', 10, 465, 1),
                (44, '02:40:00', '02:50:00', 10, 990, 2),
                (26, '04:15:00', '04:20:00', 5, 1119, 2),
                (45, '06:55:00', '06:57:00', 2, 1352, 2),
                (6, '07:35:00', '07:35:00', 0, 1382, 2)
            ]),
            # Train 45: Howrah - CSMT Mumbai Mail (HWH -> CSMT) - 7 Stops
            (45, [
                (12, '23:35:00', '23:35:00', 0, 0, 1),
                (33, '07:15:00', '07:25:00', 10, 410, 2),
                (28, '17:40:00', '17:50:00', 10, 1140, 2),
                (18, '23:50:00', '23:55:00', 5, 1530, 2),
                (47, '11:45:00', '11:48:00', 3, 1915, 3),
                (46, '12:12:00', '12:15:00', 3, 1935, 3),
                (9, '13:15:00', '13:15:00', 0, 1968, 3)
            ]),
            # Train 46: CSMT Mumbai - Howrah Mail (CSMT -> HWH) - 7 Stops
            (46, [
                (9, '21:30:00', '21:30:00', 0, 0, 1),
                (46, '22:15:00', '22:18:00', 3, 33, 1),
                (47, '22:42:00', '22:45:00', 3, 53, 1),
                (18, '10:30:00', '10:35:00', 5, 438, 2),
                (28, '16:30:00', '16:40:00', 10, 828, 2),
                (33, '03:10:00', '03:20:00', 10, 1558, 3),
                (12, '11:40:00', '11:40:00', 0, 1968, 3)
            ]),
            # Train 47: Mumbai CSMT - Pune Intercity (CSMT -> PUNE) - 4 Stops
            (47, [
                (9, '06:40:00', '06:40:00', 0, 0, 1),
                (46, '07:18:00', '07:20:00', 2, 34, 1),
                (48, '08:48:00', '08:50:00', 2, 128, 1),
                (13, '09:55:00', '09:55:00', 0, 192, 1)
            ]),
            # Train 48: Pune - Mumbai CSMT Intercity (PUNE -> CSMT) - 4 Stops
            (48, [
                (13, '17:55:00', '17:55:00', 0, 0, 1),
                (48, '19:00:00', '19:02:00', 2, 64, 1),
                (46, '20:25:00', '20:27:00', 2, 158, 1),
                (9, '21:05:00', '21:05:00', 0, 192, 1)
            ]),
        ]

        total_stops_inserted = 0
        for t_id, stops in detailed_timetables:
            for seq, (stn_id, arr, dep, halt, dist, day) in enumerate(stops, start=1):
                cursor.execute("""
                    INSERT INTO train_stops (train_id, station_id, stop_sequence, arrival_time, departure_time, halt_minutes, distance_from_origin_km, day_number)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        arrival_time = VALUES(arrival_time),
                        departure_time = VALUES(departure_time),
                        halt_minutes = VALUES(halt_minutes),
                        distance_from_origin_km = VALUES(distance_from_origin_km);
                """, (t_id, stn_id, seq, arr, dep, halt, dist, day))
                total_stops_inserted += 1

        # Also add default 3-stop timetables for any remaining trains without detailed stops
        cursor.execute("SELECT id, source_station_id, destination_station_id, departure_time, arrival_time FROM trains WHERE id NOT IN (%s)" % 
                       ",".join(str(t_id) for t_id, _ in detailed_timetables))
        remaining = cursor.fetchall()
        for r_tr in remaining:
            t_id = r_tr['id']
            s_id = r_tr['source_station_id']
            d_id = r_tr['destination_station_id']
            dep = r_tr['departure_time']
            arr = r_tr['arrival_time']
            # Stop 1 (Origin)
            cursor.execute("""
                INSERT INTO train_stops (train_id, station_id, stop_sequence, arrival_time, departure_time, halt_minutes, distance_from_origin_km, day_number)
                VALUES (%s, %s, 1, %s, %s, 0, 0, 1)
                ON DUPLICATE KEY UPDATE arrival_time=VALUES(arrival_time);
            """, (t_id, s_id, dep, dep))
            # Stop 2 (Destination)
            cursor.execute("""
                INSERT INTO train_stops (train_id, station_id, stop_sequence, arrival_time, departure_time, halt_minutes, distance_from_origin_km, day_number)
                VALUES (%s, %s, 2, %s, %s, 0, 450, 1)
                ON DUPLICATE KEY UPDATE arrival_time=VALUES(arrival_time);
            """, (t_id, d_id, arr, arr))
            total_stops_inserted += 2

        print(f"Total train_stops populated: {total_stops_inserted}")

        # Final Verification counts
        cursor.execute("SELECT COUNT(*) as st_cnt FROM stations")
        st_cnt = cursor.fetchone()['st_cnt']
        cursor.execute("SELECT COUNT(*) as tr_cnt FROM trains")
        tr_cnt = cursor.fetchone()['tr_cnt']
        cursor.execute("SELECT COUNT(*) as stop_cnt FROM train_stops")
        stop_cnt = cursor.fetchone()['stop_cnt']
        cursor.execute("SELECT COUNT(*) as coach_cnt FROM coaches")
        coach_cnt = cursor.fetchone()['coach_cnt']
        cursor.execute("SELECT COUNT(*) as seat_cnt FROM seats")
        seat_cnt = cursor.fetchone()['seat_cnt']

        print("=== Database Expansion Summary ===")
        print(f"Stations: {st_cnt}")
        print(f"Trains: {tr_cnt}")
        print(f"Train Stops: {stop_cnt}")
        print(f"Coaches: {coach_cnt}")
        print(f"Seats: {seat_cnt}")
        print("Expansion completed successfully.")

if __name__ == "__main__":
    expand_database()

