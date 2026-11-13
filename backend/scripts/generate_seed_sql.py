import os
import sys
import mysql.connector

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.config import Config

def export_seed():
    conn = mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )
    cursor = conn.cursor(dictionary=True)

    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'seed.sql'))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('-- ============================================================================\n')
        f.write('-- RailSync Master Seed Data (Phase 3 Master Release)\n')
        f.write('-- Seeds Demo Users, 32 Major Stations, Routes, Trains, Train Stops (Timetables),\n')
        f.write('-- Multi-Class Coaches & Seats.\n')
        f.write('-- Idempotent: Can be safely imported repeatedly.\n')
        f.write('-- ============================================================================\n\n')
        f.write('USE railsync_db;\n\n')

        # 1. Users
        f.write('-- 1. Default Evaluation Accounts\n')
        f.write('-- Admin: admin@railsync.com / Admin@123\n')
        f.write('-- User:  user@railsync.com  / User@123\n')
        cursor.execute("SELECT id, full_name, email, phone, address, password_hash, role FROM users WHERE email IN ('admin@railsync.com', 'user@railsync.com') ORDER BY id ASC")
        users = cursor.fetchall()
        for u in users:
            ph = f"'{u['phone']}'" if u['phone'] else 'NULL'
            addr = f"'{u['address']}'" if u['address'] else 'NULL'
            f.write(f"INSERT INTO users (id, full_name, email, phone, address, password_hash, role) VALUES ({u['id']}, '{u['full_name']}', '{u['email']}', {ph}, {addr}, '{u['password_hash']}', '{u['role']}') ON DUPLICATE KEY UPDATE full_name=VALUES(full_name), phone=VALUES(phone), address=VALUES(address), password_hash=VALUES(password_hash), role=VALUES(role);\n")
        f.write('\n')

        # 2. Stations
        f.write('-- 2. Major Indian Railway Stations (32 Major Hubs)\n')
        cursor.execute('SELECT id, station_code, station_name, city, is_active FROM stations ORDER BY id ASC')
        stations = cursor.fetchall()
        for s in stations:
            name_esc = s['station_name'].replace("'", "''")
            city_esc = s['city'].replace("'", "''")
            is_act = 1 if s['is_active'] else 0
            f.write(f"INSERT INTO stations (id, station_code, station_name, city, is_active) VALUES ({s['id']}, '{s['station_code']}', '{name_esc}', '{city_esc}', {is_act}) ON DUPLICATE KEY UPDATE station_name=VALUES(station_name), city=VALUES(city), is_active=VALUES(is_active);\n")
        f.write('\n')

        # 3. Routes
        f.write('-- 3. Bidirectional Physical Graph Edges (56 Routes for C++ Dijkstra Engine)\n')
        cursor.execute('SELECT id, source_station_id, destination_station_id, distance_km, travel_duration_minutes FROM routes ORDER BY id ASC')
        routes = cursor.fetchall()
        for r in routes:
            f.write(f"INSERT INTO routes (id, source_station_id, destination_station_id, distance_km, travel_duration_minutes) VALUES ({r['id']}, {r['source_station_id']}, {r['destination_station_id']}, {r['distance_km']}, {r['travel_duration_minutes']}) ON DUPLICATE KEY UPDATE distance_km=VALUES(distance_km), travel_duration_minutes=VALUES(travel_duration_minutes);\n")
        f.write('\n')

        # 4. Trains
        f.write('-- 4. Express Train Services (38 Trains)\n')
        cursor.execute('SELECT id, train_number, train_name, train_type, source_station_id, destination_station_id, departure_time, arrival_time, running_days, base_fare, is_active FROM trains ORDER BY id ASC')
        trains = cursor.fetchall()
        for t in trains:
            tname = t['train_name'].replace("'", "''")
            ttype = t.get('train_type') or 'EXPRESS'
            is_act = 1 if t['is_active'] else 0
            f.write(f"INSERT INTO trains (id, train_number, train_name, train_type, source_station_id, destination_station_id, departure_time, arrival_time, running_days, base_fare, is_active) VALUES ({t['id']}, '{t['train_number']}', '{tname}', '{ttype}', {t['source_station_id']}, {t['destination_station_id']}, '{t['departure_time']}', '{t['arrival_time']}', '{t['running_days']}', {t['base_fare']}, {is_act}) ON DUPLICATE KEY UPDATE train_name=VALUES(train_name), train_type=VALUES(train_type), base_fare=VALUES(base_fare), is_active=VALUES(is_active);\n")
        f.write('\n')

        # 5. Train Stops (Timetables)
        f.write('-- 5. Train Timetable Stops (Intermediate Stations, Arrival, Departure, Distance)\n')
        cursor.execute('SELECT id, train_id, station_id, stop_sequence, arrival_time, departure_time, halt_minutes, distance_from_origin_km, day_number FROM train_stops ORDER BY train_id ASC, stop_sequence ASC')
        stops = cursor.fetchall()
        for st in stops:
            arr = f"'{st['arrival_time']}'" if st['arrival_time'] else 'NULL'
            dep = f"'{st['departure_time']}'" if st['departure_time'] else 'NULL'
            f.write(f"INSERT INTO train_stops (id, train_id, station_id, stop_sequence, arrival_time, departure_time, halt_minutes, distance_from_origin_km, day_number) VALUES ({st['id']}, {st['train_id']}, {st['station_id']}, {st['stop_sequence']}, {arr}, {dep}, {st['halt_minutes']}, {st['distance_from_origin_km']}, {st['day_number']}) ON DUPLICATE KEY UPDATE arrival_time=VALUES(arrival_time), departure_time=VALUES(departure_time), distance_from_origin_km=VALUES(distance_from_origin_km);\n")
        f.write('\n')

        # 6. Coaches
        f.write('-- 6. Coaches (Multi-Class: 1A, 2A, 3A, SL, CC)\n')
        cursor.execute('SELECT id, train_id, coach_number, coach_type, total_seats FROM coaches ORDER BY id ASC')
        coaches = cursor.fetchall()
        for c in coaches:
            f.write(f"INSERT INTO coaches (id, train_id, coach_number, coach_type, total_seats) VALUES ({c['id']}, {c['train_id']}, '{c['coach_number']}', '{c['coach_type']}', {c['total_seats']}) ON DUPLICATE KEY UPDATE coach_type=VALUES(coach_type), total_seats=VALUES(total_seats);\n")
        f.write('\n')

        # 7. Seats
        f.write('-- 7. Physical Seat Templates\n')
        cursor.execute('SELECT id, coach_id, seat_number, berth_type, is_active FROM seats ORDER BY id ASC')
        seats = cursor.fetchall()
        for i in range(0, len(seats), 50):
            chunk = seats[i:i+50]
            vals = [f"({s['id']}, {s['coach_id']}, {s['seat_number']}, '{s['berth_type']}', {1 if s['is_active'] else 0})" for s in chunk]
            f.write(f"INSERT INTO seats (id, coach_id, seat_number, berth_type, is_active) VALUES {', '.join(vals)} ON DUPLICATE KEY UPDATE berth_type=VALUES(berth_type), is_active=VALUES(is_active);\n")

    conn.close()
    print(f"Exported Phase 3 master seed to {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == '__main__':
    export_seed()
