from app.database.connection import get_db_connection
from app.services.fare_service import FareService
from datetime import datetime, date

class TrainService:
    @staticmethod
    def get_all_stations(search_query=None, sort_by="station_name", order="ASC"):
        """
        Retrieves active stations from MySQL with optional search query and column sorting.
        """
        valid_cols = {
            "name": "station_name",
            "station_name": "station_name",
            "code": "station_code",
            "station_code": "station_code",
            "city": "city",
            "id": "id"
        }
        col = valid_cols.get(str(sort_by).lower(), "station_name")
        sort_order = "DESC" if str(order).upper() == "DESC" else "ASC"

        with get_db_connection() as (conn, cursor):
            if search_query:
                param = f"%{search_query}%"
                cursor.execute(
                    f"SELECT id, station_code, station_name, city, is_active "
                    f"FROM stations WHERE is_active = TRUE AND "
                    f"(station_name LIKE %s OR station_code LIKE %s OR city LIKE %s) "
                    f"ORDER BY {col} {sort_order}",
                    (param, param, param)
                )
            else:
                cursor.execute(
                    f"SELECT id, station_code, station_name, city, is_active "
                    f"FROM stations WHERE is_active = TRUE "
                    f"ORDER BY {col} {sort_order}"
                )
            return cursor.fetchall()

    @staticmethod
    def get_station_by_id(station_id):
        with get_db_connection() as (conn, cursor):
            cursor.execute("SELECT id, station_code, station_name, city, is_active FROM stations WHERE id = %s", (station_id,))
            return cursor.fetchone()

    @staticmethod
    def search_trains(source_id, destination_id, journey_date_str=None, travel_class=None, 
                      train_type=None, departure_slot=None, arrival_slot=None,
                      min_fare=None, max_fare=None, only_available=False, train_query=None):
        if not source_id or not destination_id:
            return []

        try:
            source_id = int(source_id)
            destination_id = int(destination_id)
        except (ValueError, TypeError):
            return {"error": "Station IDs must be valid integers."}

        if source_id == destination_id:
            return {"error": "Source and destination stations cannot be the same."}

        # Validate journey date
        if journey_date_str:
            try:
                j_date = datetime.strptime(journey_date_str, "%Y-%m-%d").date()
                if j_date < date.today():
                    return {"error": "Journey date cannot be in the past."}
            except ValueError:
                return {"error": "Invalid date format. Expected YYYY-MM-DD."}
        else:
            journey_date_str = date.today().strftime("%Y-%m-%d")

        with get_db_connection() as (conn, cursor):
            # Verify stations exist
            cursor.execute("SELECT id FROM stations WHERE id IN (%s, %s) AND is_active = TRUE", (source_id, destination_id))
            valid_stations = cursor.fetchall()
            if len(valid_stations) < 2:
                return {"error": "One or both selected stations do not exist or are inactive."}

        query = """
            SELECT DISTINCT
                t.id,
                t.train_number,
                t.train_name,
                t.train_type,
                t.departure_time,
                t.arrival_time,
                t.running_days,
                t.base_fare,
                s1.station_name AS source_station_name,
                s1.station_code AS source_station_code,
                s2.station_name AS destination_station_name,
                s2.station_code AS destination_station_code,
                COALESCE(r.distance_km, (
                    SELECT ABS(ts2.distance_from_origin_km - ts1.distance_from_origin_km)
                    FROM train_stops ts1
                    JOIN train_stops ts2 ON ts1.train_id = ts2.train_id
                    WHERE ts1.train_id = t.id AND ts1.station_id = %s AND ts2.station_id = %s
                    LIMIT 1
                ), 500) AS distance_km,
                COALESCE(r.travel_duration_minutes, 360) AS travel_duration_minutes
            FROM trains t
            INNER JOIN stations s1 ON t.source_station_id = s1.id
            INNER JOIN stations s2 ON t.destination_station_id = s2.id
            LEFT JOIN routes r ON r.source_station_id = t.source_station_id 
                               AND r.destination_station_id = t.destination_station_id
            WHERE t.is_active = TRUE AND (
                (t.source_station_id = %s AND t.destination_station_id = %s)
                OR EXISTS (
                    SELECT 1 FROM train_stops ts1
                    JOIN train_stops ts2 ON ts1.train_id = ts2.train_id
                    WHERE ts1.train_id = t.id
                      AND ts1.station_id = %s
                      AND ts2.station_id = %s
                      AND ts1.stop_sequence < ts2.stop_sequence
                )
            )
        """
        params = [source_id, destination_id, source_id, destination_id, source_id, destination_id]

        if train_type and train_type.upper() != 'ALL':
            query += " AND t.train_type = %s"
            params.append(train_type.upper())

        query += " ORDER BY t.departure_time ASC"

        trains = []
        with get_db_connection() as (conn, cursor):
            cursor.execute(query, params)
            raw_trains = cursor.fetchall()

            for t in raw_trains:
                t_id = t['id']
                t_type = t.get('train_type') or 'EXPRESS'
                dep_time_str = str(t['departure_time'])[:5]
                dep_hour = int(dep_time_str.split(':')[0])

                # Departure time slot filter
                if departure_slot and departure_slot.upper() != 'ALL':
                    slot = departure_slot.lower()
                    if slot == 'early_morning' and not (0 <= dep_hour < 6):
                        continue
                    elif slot == 'morning' and not (6 <= dep_hour < 12):
                        continue
                    elif slot == 'midday' and not (12 <= dep_hour < 18):
                        continue
                    elif slot == 'night' and not (18 <= dep_hour <= 23):
                        continue

                # Arrival time slot filter
                arr_time_str = str(t['arrival_time'])[:5]
                arr_hour = int(arr_time_str.split(':')[0])
                if arrival_slot and arrival_slot.upper() != 'ALL':
                    a_slot = arrival_slot.lower()
                    if a_slot == 'early_morning' and not (0 <= arr_hour < 6):
                        continue
                    elif a_slot == 'morning' and not (6 <= arr_hour < 12):
                        continue
                    elif a_slot == 'midday' and not (12 <= arr_hour < 18):
                        continue
                    elif a_slot == 'night' and not (18 <= arr_hour <= 23):
                        continue

                # Keyword quick filter
                if train_query:
                    tq = train_query.strip().lower()
                    if tq not in t['train_number'].lower() and tq not in t['train_name'].lower():
                        continue

                # Calculate available seats for this journey_date grouped by coach_type
                avail_query = """
                    SELECT 
                        c.coach_type,
                        COUNT(s.id) AS total_capacity,
                        COUNT(sa.id) AS booked_count
                    FROM coaches c
                    INNER JOIN seats s ON s.coach_id = c.id AND s.is_active = TRUE
                    LEFT JOIN seat_allocations sa ON sa.seat_id = s.id 
                                                 AND sa.journey_date = %s
                    WHERE c.train_id = %s
                    GROUP BY c.coach_type
                """
                cursor.execute(avail_query, (journey_date_str, t_id))
                coach_avail = cursor.fetchall()

                total_seats = 0
                booked_seats = 0
                classes = []
                for ca in coach_avail:
                    avail = max(0, ca['total_capacity'] - ca['booked_count'])
                    total_seats += ca['total_capacity']
                    booked_seats += ca['booked_count']
                    c_type = ca['coach_type']

                    # Calculate dynamic fare for this class
                    fare_calc = FareService.calculate_fare(
                        train_base_fare=t['base_fare'],
                        travel_class=c_type,
                        train_type=t_type,
                        num_passengers=1
                    )

                    status_label = f"AVL {avail}"
                    if avail == 0:
                        status_label = "RAC 4"

                    classes.append({
                        "coach_type": c_type,
                        "available": avail,
                        "total": ca['total_capacity'],
                        "fare": fare_calc['total_amount'],
                        "status_label": status_label
                    })

                # Filter by travel class if specified
                if travel_class and travel_class.upper() != 'ALL':
                    matching_class = [c for c in classes if c['coach_type'] == travel_class.upper()]
                    if not matching_class:
                        continue

                total_available = max(0, total_seats - booked_seats)
                # Filter by seat availability if only_available is True
                if only_available and total_available <= 0:
                    continue

                # Filter by fare range if specified
                fares = [c['fare'] for c in classes] if classes else [float(t['base_fare'])]
                min_class_fare = min(fares) if fares else float(t['base_fare'])
                if min_fare is not None and min_class_fare < float(min_fare):
                    continue
                if max_fare is not None and min_class_fare > float(max_fare):
                    continue

                dur_mins = t['travel_duration_minutes'] or 360
                hours = dur_mins // 60
                mins = dur_mins % 60
                duration_str = f"{hours}h {mins}m"

                trains.append({
                    "id": t['id'],
                    "train_number": t['train_number'],
                    "train_name": t['train_name'],
                    "train_type": t_type,
                    "source_station_name": t['source_station_name'],
                    "source_station_code": t['source_station_code'],
                    "destination_station_name": t['destination_station_name'],
                    "destination_station_code": t['destination_station_code'],
                    "departure_time": dep_time_str,
                    "arrival_time": arr_time_str,
                    "duration": duration_str,
                    "distance_km": t['distance_km'] or 300,
                    "base_fare": float(t['base_fare']),
                    "total_available_seats": total_available,
                    "classes": classes,
                    "journey_date": journey_date_str
                })

        return trains

    @staticmethod
    def search_by_keyword(keyword, journey_date_str=None):
        """
        Direct search by train number or train name with real-time seat availability.
        """
        if not keyword:
            return []
        if not journey_date_str:
            journey_date_str = date.today().strftime("%Y-%m-%d")

        param = f"%{keyword.strip()}%"
        query = """
            SELECT 
                t.id, t.train_number, t.train_name, t.train_type,
                t.departure_time, t.arrival_time, t.running_days, t.base_fare,
                s1.station_name AS source_station_name, s1.station_code AS source_station_code,
                s2.station_name AS destination_station_name, s2.station_code AS destination_station_code,
                COALESCE(r.distance_km, 500) as distance_km,
                COALESCE(r.travel_duration_minutes, 360) as travel_duration_minutes
            FROM trains t
            INNER JOIN stations s1 ON t.source_station_id = s1.id
            INNER JOIN stations s2 ON t.destination_station_id = s2.id
            LEFT JOIN routes r ON r.source_station_id = t.source_station_id 
                               AND r.destination_station_id = t.destination_station_id
            WHERE t.is_active = TRUE 
              AND (t.train_number LIKE %s OR t.train_name LIKE %s)
            ORDER BY t.departure_time ASC
        """
        trains = []
        with get_db_connection() as (conn, cursor):
            cursor.execute(query, (param, param))
            raw_trains = cursor.fetchall()

            for t in raw_trains:
                t_id = t['id']
                t_type = t.get('train_type') or 'EXPRESS'
                dep_time_str = str(t['departure_time'])[:5]
                arr_time_str = str(t['arrival_time'])[:5]

                avail_query = """
                    SELECT 
                        c.coach_type,
                        COUNT(s.id) AS total_capacity,
                        COUNT(sa.id) AS booked_count
                    FROM coaches c
                    INNER JOIN seats s ON s.coach_id = c.id AND s.is_active = TRUE
                    LEFT JOIN seat_allocations sa ON sa.seat_id = s.id 
                                                 AND sa.journey_date = %s
                    WHERE c.train_id = %s
                    GROUP BY c.coach_type
                """
                cursor.execute(avail_query, (journey_date_str, t_id))
                coach_avail = cursor.fetchall()

                total_seats = 0
                booked_seats = 0
                classes = []
                for ca in coach_avail:
                    avail = max(0, ca['total_capacity'] - ca['booked_count'])
                    total_seats += ca['total_capacity']
                    booked_seats += ca['booked_count']
                    c_type = ca['coach_type']

                    fare_calc = FareService.calculate_fare(
                        train_base_fare=t['base_fare'],
                        travel_class=c_type,
                        train_type=t_type,
                        num_passengers=1
                    )
                    classes.append({
                        "coach_type": c_type,
                        "available": avail,
                        "total": ca['total_capacity'],
                        "fare": fare_calc['total_amount'],
                        "status_label": f"AVL {avail}" if avail > 0 else "RAC 4"
                    })

                dur_mins = t['travel_duration_minutes'] or 360
                hours = dur_mins // 60
                mins = dur_mins % 60

                trains.append({
                    "id": t['id'],
                    "train_number": t['train_number'],
                    "train_name": t['train_name'],
                    "train_type": t_type,
                    "source_station_name": t['source_station_name'],
                    "source_station_code": t['source_station_code'],
                    "destination_station_name": t['destination_station_name'],
                    "destination_station_code": t['destination_station_code'],
                    "departure_time": dep_time_str,
                    "arrival_time": arr_time_str,
                    "duration": f"{hours}h {mins}m",
                    "distance_km": t['distance_km'] or 300,
                    "base_fare": float(t['base_fare']),
                    "total_available_seats": max(0, total_seats - booked_seats),
                    "classes": classes,
                    "journey_date": journey_date_str
                })

        return trains

    @staticmethod
    def get_train_details(train_id):
        query = """
            SELECT 
                t.id, t.train_number, t.train_name, t.train_type, t.departure_time, t.arrival_time, 
                t.running_days, t.base_fare, t.is_active,
                s1.id AS source_id, s1.station_name AS source_name, s1.station_code AS source_code,
                s2.id AS dest_id, s2.station_name AS dest_name, s2.station_code AS dest_code
            FROM trains t
            INNER JOIN stations s1 ON t.source_station_id = s1.id
            INNER JOIN stations s2 ON t.destination_station_id = s2.id
            WHERE t.id = %s
        """
        with get_db_connection() as (conn, cursor):
            cursor.execute(query, (train_id,))
            t = cursor.fetchone()
            if not t:
                return None
            t['departure_time'] = str(t['departure_time'])[:5]
            t['arrival_time'] = str(t['arrival_time'])[:5]
            t['base_fare'] = float(t['base_fare'])
            return t

    @staticmethod
    def get_train_stops(train_id):
        """
        Retrieves ordered intermediate timetable schedule stops for a train.
        """
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
            return stops

    @staticmethod
    def get_fare_quote(train_id, travel_class='CC', num_passengers=1):
        """
        Calculates a detailed fare quote breakdown for a given train, class, and passenger count.
        """
        with get_db_connection() as (conn, cursor):
            cursor.execute("SELECT base_fare, train_type FROM trains WHERE id = %s", (train_id,))
            train = cursor.fetchone()
            if not train:
                return {"error": "Train not found."}

            return FareService.calculate_fare(
                train_base_fare=train['base_fare'],
                travel_class=travel_class,
                train_type=train.get('train_type', 'EXPRESS'),
                num_passengers=num_passengers
            )

    @staticmethod
    def get_train_seat_map(train_id, journey_date_str):
        """
        Retrieves coaches and seats with real availability for the specified date.
        """
        with get_db_connection() as (conn, cursor):
            # Fetch coaches
            cursor.execute(
                "SELECT id, coach_number, coach_type, total_seats FROM coaches WHERE train_id = %s ORDER BY id ASC",
                (train_id,)
            )
            coaches = cursor.fetchall()
            if not coaches:
                return []

            coach_ids = [c['id'] for c in coaches]
            format_strings = ','.join(['%s'] * len(coach_ids))

            # Fetch seats with seat_allocations join for this date
            seat_query = f"""
                SELECT 
                    s.id,
                    s.coach_id,
                    s.seat_number,
                    s.berth_type,
                    sa.id AS allocation_id
                FROM seats s
                LEFT JOIN seat_allocations sa ON s.id = sa.seat_id AND sa.journey_date = %s
                WHERE s.coach_id IN ({format_strings}) AND s.is_active = TRUE
                ORDER BY s.seat_number ASC
            """
            cursor.execute(seat_query, [journey_date_str] + coach_ids)
            seats = cursor.fetchall()

            # Group seats under their respective coaches
            coach_map = {c['id']: {**c, "seats": []} for c in coaches}
            for s in seats:
                c_id = s['coach_id']
                is_booked = s['allocation_id'] is not None
                coach_map[c_id]['seats'].append({
                    "id": s['id'],
                    "seat_number": s['seat_number'],
                    "berth_type": s['berth_type'],
                    "status": "BOOKED" if is_booked else "AVAILABLE"
                })

            return list(coach_map.values())

    @staticmethod
    def get_popular_routes():
        """
        Retrieves popular corridors populated directly from the relational database.
        """
        query = """
            SELECT 
                r.id,
                r.distance_km,
                r.travel_duration_minutes,
                s1.id AS source_id,
                s1.station_code AS source_code,
                s1.station_name AS source_name,
                s1.city AS source_city,
                s2.id AS destination_id,
                s2.station_code AS destination_code,
                s2.station_name AS dest_name,
                s2.city AS destination_city,
                (
                    SELECT t.train_name 
                    FROM trains t 
                    WHERE t.source_station_id = r.source_station_id 
                      AND t.destination_station_id = r.destination_station_id 
                      AND t.is_active = TRUE 
                    LIMIT 1
                ) AS express_train_name,
                (
                    SELECT MIN(t.base_fare)
                    FROM trains t 
                    WHERE t.source_station_id = r.source_station_id 
                      AND t.destination_station_id = r.destination_station_id 
                      AND t.is_active = TRUE
                ) AS min_fare
            FROM routes r
            INNER JOIN stations s1 ON r.source_station_id = s1.id
            INNER JOIN stations s2 ON r.destination_station_id = s2.id
            WHERE r.id IN (1, 3, 7, 9, 13, 17)
            ORDER BY r.id ASC
            LIMIT 6
        """
        with get_db_connection() as (conn, cursor):
            cursor.execute(query)
            routes = cursor.fetchall()
            formatted = []
            for r in routes:
                dur = r['travel_duration_minutes']
                formatted.append({
                    "route_id": r['id'],
                    "source_id": r['source_id'],
                    "source_code": r['source_code'],
                    "source_city": r['source_city'],
                    "source_name": r['source_name'],
                    "dest_id": r['destination_id'],
                    "dest_code": r['destination_code'],
                    "dest_city": r['destination_city'],
                    "dest_name": r['dest_name'],
                    "distance_km": r['distance_km'],
                    "duration": f"{dur // 60}h {dur % 60}m" if dur else "6h 00m",
                    "train_name": r['express_train_name'] or f"Express {r['source_code']}→{r['destination_code']}",
                    "base_fare": float(r['min_fare'] or 650.00)
                })
            return formatted

    @staticmethod
    def get_featured_trains():
        """
        Returns active flagship trains directly from MySQL with route metrics.
        """
        query = """
            SELECT 
                t.id, t.train_number, t.train_name, t.train_type, t.departure_time, t.arrival_time,
                t.running_days, t.base_fare,
                s1.id AS source_id, s1.station_code AS source_code, s1.station_name AS source_name, s1.city AS source_city,
                s2.id AS dest_id, s2.station_code AS dest_code, s2.station_name AS dest_name, s2.city AS dest_city,
                COALESCE(r.distance_km, 450) AS distance_km,
                COALESCE(r.travel_duration_minutes, 360) AS duration_minutes
            FROM trains t
            INNER JOIN stations s1 ON t.source_station_id = s1.id
            INNER JOIN stations s2 ON t.destination_station_id = s2.id
            LEFT JOIN routes r ON r.source_station_id = t.source_station_id AND r.destination_station_id = t.destination_station_id
            WHERE t.is_active = TRUE
            ORDER BY t.id ASC
            LIMIT 6
        """
        with get_db_connection() as (conn, cursor):
            cursor.execute(query)
            trains = cursor.fetchall()
            result = []
            for t in trains:
                dur = t['duration_minutes']
                result.append({
                    "id": t['id'],
                    "train_number": t['train_number'],
                    "train_name": t['train_name'],
                    "train_type": t.get('train_type') or 'EXPRESS',
                    "departure_time": str(t['departure_time'])[:5],
                    "arrival_time": str(t['arrival_time'])[:5],
                    "duration": f"{dur // 60}h {dur % 60:02d}m",
                    "running_days": t['running_days'],
                    "base_fare": float(t['base_fare']),
                    "source_id": t['source_id'],
                    "source_code": t['source_code'],
                    "source_name": t['source_name'],
                    "source_city": t['source_city'],
                    "dest_id": t['dest_id'],
                    "dest_code": t['dest_code'],
                    "dest_name": t['dest_name'],
                    "dest_city": t['dest_city'],
                    "distance_km": t['distance_km']
                })
            return result

    @staticmethod
    def get_network_shortest_path(source_station_id, destination_station_id):
        """
        Connects MySQL station topology to C++ Dijkstra Graph Engine.
        Returns the optimal path (ordered stations) and total physical distance in km.
        """
        if not source_station_id or not destination_station_id:
            return {"error": "Source and destination station IDs are required."}
        if source_station_id == destination_station_id:
            return {"error": "Source and destination stations must be distinct."}

        from app.services.cpp_engine_service import cpp_engine

        with get_db_connection() as (conn, cursor):
            cursor.execute("SELECT id, station_code, station_name, city FROM stations ORDER BY id ASC")
            all_stations = cursor.fetchall()
            
            station_by_id = {s['id']: s for s in all_stations}
            if source_station_id not in station_by_id or destination_station_id not in station_by_id:
                return {"error": "One or more station identifiers do not exist."}

            id_to_idx = {s['id']: idx for idx, s in enumerate(all_stations)}
            idx_to_station = {idx: s for idx, s in enumerate(all_stations)}
            num_nodes = len(all_stations)

            cursor.execute("SELECT source_station_id, destination_station_id, distance_km FROM routes")
            routes = cursor.fetchall()
            edges = []
            for r in routes:
                u = id_to_idx.get(r['source_station_id'])
                v = id_to_idx.get(r['destination_station_id'])
                w = r['distance_km']
                if u is not None and v is not None and w > 0:
                    edges.append((u, v, w))

            start_idx = id_to_idx[source_station_id]
            target_idx = id_to_idx[destination_station_id]

            dijkstra_res = cpp_engine.dijkstra_shortest_path(
                num_nodes=num_nodes,
                edges=edges,
                start_node=start_idx,
                target_node=target_idx
            )

            if dijkstra_res.get('status') != 'SUCCESS':
                return {
                    "status": "UNREACHABLE",
                    "message": "No connected railway corridor found between the selected stations.",
                    "distance_km": -1,
                    "path": []
                }

            ordered_stations = [idx_to_station[idx] for idx in dijkstra_res.get('path', [])]

            return {
                "status": "SUCCESS",
                "source_station": station_by_id[source_station_id],
                "destination_station": station_by_id[destination_station_id],
                "total_distance_km": dijkstra_res['distance_km'],
                "path": ordered_stations,
                "hops": max(0, len(ordered_stations) - 1),
                "engine": dijkstra_res.get('engine', 'C++17 Min-Heap Priority Queue')
            }
