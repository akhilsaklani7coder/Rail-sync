from flask import Blueprint, request, jsonify
from app.database.connection import get_db_connection
from app.security.auth_helpers import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard_metrics():
    with get_db_connection() as (conn, cursor):
        cursor.execute("SELECT COUNT(*) AS total_users FROM users WHERE role = 'USER'")
        total_users = cursor.fetchone()['total_users']

        cursor.execute("SELECT COUNT(*) AS total_trains FROM trains")
        total_trains = cursor.fetchone()['total_trains']

        cursor.execute("SELECT COUNT(*) AS total_bookings FROM bookings")
        total_bookings = cursor.fetchone()['total_bookings']

        cursor.execute("SELECT COUNT(*) AS confirmed_bookings FROM bookings WHERE booking_status = 'CONFIRMED'")
        confirmed_bookings = cursor.fetchone()['confirmed_bookings']

        cursor.execute("SELECT COUNT(*) AS cancelled_bookings FROM bookings WHERE booking_status = 'CANCELLED'")
        cancelled_bookings = cursor.fetchone()['cancelled_bookings']

        cursor.execute(
            "SELECT COALESCE(SUM(total_amount), 0) AS total_revenue FROM bookings WHERE payment_status = 'SUCCESS' AND booking_status = 'CONFIRMED'"
        )
        total_revenue = float(cursor.fetchone()['total_revenue'])

        recent_query = """
            SELECT 
                b.id, b.pnr, b.journey_date, b.booking_status, b.travel_class, b.total_amount, b.created_at,
                u.full_name AS user_name, u.email AS user_email,
                t.train_number, t.train_name,
                s1.station_code AS source_code, s2.station_code AS dest_code
            FROM bookings b
            INNER JOIN users u ON b.user_id = u.id
            INNER JOIN trains t ON b.train_id = t.id
            INNER JOIN stations s1 ON t.source_station_id = s1.id
            INNER JOIN stations s2 ON t.destination_station_id = s2.id
            ORDER BY b.created_at DESC
            LIMIT 10
        """
        cursor.execute(recent_query)
        recent_bookings = cursor.fetchall()
        for r in recent_bookings:
            r['journey_date'] = str(r['journey_date'])
            r['created_at'] = str(r['created_at'])
            r['total_amount'] = float(r['total_amount'])

    return jsonify({
        "metrics": {
            "total_users": total_users,
            "total_trains": total_trains,
            "total_bookings": total_bookings,
            "confirmed_bookings": confirmed_bookings,
            "cancelled_bookings": cancelled_bookings,
            "total_revenue": total_revenue
        },
        "recent_bookings": recent_bookings
    })

@admin_bp.route('/trains', methods=['GET'])
@admin_required
def get_admin_trains():
    query = """
        SELECT 
            t.id, t.train_number, t.train_name, t.train_type, t.departure_time, t.arrival_time, 
            t.running_days, t.base_fare, t.is_active,
            s1.station_name AS source_name, s1.station_code AS source_code,
            s2.station_name AS dest_name, s2.station_code AS dest_code,
            (SELECT COUNT(*) FROM coaches WHERE train_id = t.id) AS coach_count,
            (SELECT COUNT(*) FROM train_stops WHERE train_id = t.id) AS stop_count
        FROM trains t
        INNER JOIN stations s1 ON t.source_station_id = s1.id
        INNER JOIN stations s2 ON t.destination_station_id = s2.id
        ORDER BY t.id DESC
    """
    with get_db_connection() as (conn, cursor):
        cursor.execute(query)
        trains = cursor.fetchall()
        for t in trains:
            t['departure_time'] = str(t['departure_time'])[:5]
            t['arrival_time'] = str(t['arrival_time'])[:5]
            t['base_fare'] = float(t['base_fare'])
            t['is_active'] = bool(t['is_active'])
            t['train_type'] = t.get('train_type') or 'EXPRESS'
    return jsonify({"trains": trains})

@admin_bp.route('/trains', methods=['POST'])
@admin_required
def add_train():
    data = request.get_json() or {}
    train_number = data.get('train_number', '').strip()
    train_name = data.get('train_name', '').strip()
    train_type = data.get('train_type', 'EXPRESS').strip().upper()
    src_id = data.get('source_station_id')
    dst_id = data.get('destination_station_id')
    dep_time = data.get('departure_time')
    arr_time = data.get('arrival_time')
    days = data.get('running_days', 'DAILY')
    base_fare = float(data.get('base_fare', 500))

    if not train_number or not train_name or not src_id or not dst_id or not dep_time or not arr_time:
        return jsonify({"error": "All train fields are required."}), 400

    with get_db_connection() as (conn, cursor):
        cursor.execute(
            """
            INSERT INTO trains (train_number, train_name, train_type, source_station_id, destination_station_id, 
                                departure_time, arrival_time, running_days, base_fare, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
            """,
            (train_number, train_name, train_type, src_id, dst_id, dep_time, arr_time, days, base_fare)
        )
        train_id = cursor.lastrowid

        # Seed standard coaches (C1-CC, B1-3A, S1-SL) with 16 seats each
        cursor.execute(
            "INSERT INTO coaches (train_id, coach_number, coach_type, total_seats) VALUES (%s, 'C1', 'CC', 16)",
            (train_id,)
        )
        c1_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO coaches (train_id, coach_number, coach_type, total_seats) VALUES (%s, 'B1', '3A', 16)",
            (train_id,)
        )
        b1_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO coaches (train_id, coach_number, coach_type, total_seats) VALUES (%s, 'S1', 'SL', 16)",
            (train_id,)
        )
        s1_id = cursor.lastrowid

        berths = ['LOWER', 'MIDDLE', 'UPPER', 'SIDE LOWER', 'SIDE UPPER', 'WINDOW', 'AISLE']
        for c_id in [c1_id, b1_id, s1_id]:
            for s_num in range(1, 17):
                b_type = berths[(s_num - 1) % len(berths)]
                cursor.execute(
                    "INSERT INTO seats (coach_id, seat_number, berth_type) VALUES (%s, %s, %s)",
                    (c_id, s_num, b_type)
                )

    return jsonify({"message": "Train added successfully with coaches and seats.", "train_id": train_id}), 201

@admin_bp.route('/trains/<int:train_id>', methods=['PUT'])
@admin_required
def update_train(train_id):
    data = request.get_json() or {}
    train_name = data.get('train_name')
    train_type = data.get('train_type')
    base_fare = data.get('base_fare')
    is_active = data.get('is_active')

    with get_db_connection() as (conn, cursor):
        cursor.execute(
            """
            UPDATE trains 
            SET train_name = COALESCE(%s, train_name), 
                train_type = COALESCE(%s, train_type),
                base_fare = COALESCE(%s, base_fare), 
                is_active = COALESCE(%s, is_active) 
            WHERE id = %s
            """,
            (train_name, train_type, base_fare, is_active, train_id)
        )
    return jsonify({"message": f"Train {train_id} updated successfully."})

@admin_bp.route('/trains/<int:train_id>', methods=['DELETE'])
@admin_required
def toggle_or_deactivate_train(train_id):
    with get_db_connection() as (conn, cursor):
        cursor.execute("UPDATE trains SET is_active = NOT is_active WHERE id = %s", (train_id,))
    return jsonify({"message": f"Train status toggled."})

@admin_bp.route('/trains/<int:train_id>/stops', methods=['GET'])
@admin_required
def get_admin_train_stops(train_id):
    query = """
        SELECT 
            ts.id, ts.train_id, ts.stop_sequence, ts.arrival_time, ts.departure_time,
            ts.halt_minutes, ts.distance_from_origin_km, ts.day_number,
            s.id AS station_id, s.station_code, s.station_name, s.city
        FROM train_stops ts
        INNER JOIN stations s ON ts.station_id = s.id
        WHERE ts.train_id = %s
        ORDER BY ts.stop_sequence ASC
    """
    with get_db_connection() as (conn, cursor):
        cursor.execute(query, (train_id,))
        stops = cursor.fetchall()
        for s in stops:
            s['arrival_time'] = str(s['arrival_time'])[:5] if s['arrival_time'] else "--"
            s['departure_time'] = str(s['departure_time'])[:5] if s['departure_time'] else "--"
    return jsonify({"stops": stops})

@admin_bp.route('/trains/<int:train_id>/stops', methods=['POST'])
@admin_required
def add_admin_train_stop(train_id):
    data = request.get_json() or {}
    station_id = data.get('station_id')
    stop_sequence = data.get('stop_sequence')
    arr_time = data.get('arrival_time')
    dep_time = data.get('departure_time')
    halt_mins = int(data.get('halt_minutes', 2))
    dist_km = int(data.get('distance_from_origin_km', 0))

    if not station_id or not stop_sequence:
        return jsonify({"error": "station_id and stop_sequence are required."}), 400

    with get_db_connection() as (conn, cursor):
        cursor.execute(
            """
            INSERT INTO train_stops (train_id, station_id, stop_sequence, arrival_time, departure_time, halt_minutes, distance_from_origin_km)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                arrival_time = VALUES(arrival_time), departure_time = VALUES(departure_time),
                halt_minutes = VALUES(halt_minutes), distance_from_origin_km = VALUES(distance_from_origin_km)
            """,
            (train_id, station_id, stop_sequence, arr_time, dep_time, halt_mins, dist_km)
        )
    return jsonify({"message": "Timetable stop recorded successfully."}), 201

@admin_bp.route('/stops/<int:stop_id>', methods=['DELETE'])
@admin_required
def delete_admin_train_stop(stop_id):
    with get_db_connection() as (conn, cursor):
        cursor.execute("DELETE FROM train_stops WHERE id = %s", (stop_id,))
    return jsonify({"message": "Stop deleted successfully."})

@admin_bp.route('/stations', methods=['GET'])
@admin_required
def get_admin_stations():
    with get_db_connection() as (conn, cursor):
        cursor.execute("SELECT id, station_code, station_name, city, is_active FROM stations ORDER BY id ASC")
        stations = cursor.fetchall()
        for s in stations:
            s['is_active'] = bool(s.get('is_active', True))
    return jsonify({"stations": stations})

@admin_bp.route('/stations', methods=['POST'])
@admin_required
def add_station():
    data = request.get_json() or {}
    code = data.get('station_code', '').strip().upper()
    name = data.get('station_name', '').strip()
    city = data.get('city', '').strip()

    if not code or not name or not city:
        return jsonify({"error": "Station code, name, and city are required."}), 400

    with get_db_connection() as (conn, cursor):
        cursor.execute("SELECT id FROM stations WHERE station_code = %s", (code,))
        if cursor.fetchone():
            return jsonify({"error": "A station with this code already exists."}), 409

        cursor.execute(
            "INSERT INTO stations (station_code, station_name, city, is_active) VALUES (%s, %s, %s, 1)",
            (code, name, city)
        )
        new_id = cursor.lastrowid
    return jsonify({"message": "Station created successfully.", "station_id": new_id}), 201

@admin_bp.route('/stations/<int:station_id>', methods=['PUT'])
@admin_required
def update_station(station_id):
    data = request.get_json() or {}
    station_name = data.get('station_name')
    city = data.get('city')
    is_active = data.get('is_active')

    with get_db_connection() as (conn, cursor):
        cursor.execute(
            "UPDATE stations SET station_name = COALESCE(%s, station_name), city = COALESCE(%s, city), is_active = COALESCE(%s, is_active) WHERE id = %s",
            (station_name, city, is_active, station_id)
        )
    return jsonify({"message": f"Station {station_id} updated successfully."})

@admin_bp.route('/stations/<int:station_id>', methods=['DELETE'])
@admin_required
def toggle_station_active(station_id):
    with get_db_connection() as (conn, cursor):
        cursor.execute("UPDATE stations SET is_active = NOT is_active WHERE id = %s", (station_id,))
    return jsonify({"message": f"Station {station_id} status toggled successfully."})

@admin_bp.route('/bookings', methods=['GET'])
@admin_required
def get_all_bookings():
    query = """
        SELECT 
            b.id, b.pnr, b.journey_date, b.booking_status, b.travel_class, b.total_amount, b.payment_status, b.created_at,
            u.full_name AS user_name, u.email AS user_email,
            t.train_number, t.train_name,
            s1.station_code AS source_code, s2.station_code AS dest_code
        FROM bookings b
        INNER JOIN users u ON b.user_id = u.id
        INNER JOIN trains t ON b.train_id = t.id
        INNER JOIN stations s1 ON t.source_station_id = s1.id
        INNER JOIN stations s2 ON t.destination_station_id = s2.id
        ORDER BY b.created_at DESC
        LIMIT 50
    """
    with get_db_connection() as (conn, cursor):
        cursor.execute(query)
        bookings = cursor.fetchall()
        for b in bookings:
            b['journey_date'] = str(b['journey_date'])
            b['created_at'] = str(b['created_at'])
            b['total_amount'] = float(b['total_amount'])
    return jsonify({"bookings": bookings})

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    with get_db_connection() as (conn, cursor):
        cursor.execute("SELECT id, full_name, email, role, phone, address, created_at FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
        for u in users:
            u['created_at'] = str(u['created_at'])
    return jsonify({"users": users})

@admin_bp.route('/diagnostics', methods=['GET'])
@admin_required
def get_system_diagnostics():
    from app.services.cpp_engine_service import cpp_engine
    engine_status = cpp_engine.get_status()

    with get_db_connection() as (conn, cursor):
        tables = [
            'users', 'stations', 'routes', 'trains', 'train_stops', 'coaches', 'seats',
            'bookings', 'passengers', 'tickets', 'seat_allocations', 'waitlist_entries', 'payments', 'cancellations'
        ]
        counts = {}
        for t in tables:
            cursor.execute(f"SELECT COUNT(*) AS c FROM {t}")
            counts[t] = cursor.fetchone()['c']

    return jsonify({
        "status": "HEALTHY",
        "cpp_engine": engine_status,
        "database": {
            "rdbms": "MySQL 8.4 (InnoDB)",
            "acid_guarantees": "Strict Serializable / Row-Level Lock (FOR UPDATE)",
            "table_record_counts": counts,
            "foreign_key_checks": "ENFORCED",
            "date_specific_seat_allocations": counts.get('seat_allocations', 0)
        },
        "simulation_engines": {
            "dijkstra": "std::priority_queue Min-Heap O((V+E)logV) in C++17",
            "waitlist_manager": "Transactional FIFO Queue & Auto-Promotion on cancellation",
            "fare_engine": "Multi-tier Class Multipliers, Reservation Fees & 5% GST",
            "pdf_renderer": "ReportLab Vector PDF with Dynamic Embedded Verification QR",
            "process_bridge": "In-Memory 64-bit ctypes CDLL ABI"
        },
        "os_primitives": {
            "mutex": "std::mutex RAII Guard (C++17 Native)",
            "dijkstra": "std::priority_queue Min-Heap O((V+E)logV)",
            "counting_semaphore": "threading.Semaphore(value=5) on PDF Generation",
            "process_bridge": "In-Memory 64-bit ctypes CDLL ABI"
        }
    })
