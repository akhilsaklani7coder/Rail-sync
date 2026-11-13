import random
import string
import uuid
from datetime import datetime, date
from app.database.connection import get_db_connection, get_db_transaction
from app.services.cpp_engine_service import cpp_engine
from app.services.fare_service import FareService
from app.services.waitlist_service import WaitlistService

def generate_pnr():
    """Generates a unique 10-character Indian Railway PNR format (e.g. RS29384751)"""
    digits = ''.join(random.choices(string.digits, k=8))
    return f"RS{digits}"

class BookingService:
    @staticmethod
    def create_booking(user_id, train_id, journey_date_str, passengers, travel_class='CC', requested_seat_ids=None, payment_details=None):
        """
        Executes safe, transactional seat booking with row-level locking (SELECT ... FOR UPDATE),
        rules-based dynamic fare calculation, multi-passenger berth preference matching,
        and automatic RAC/Waitlist allocation if confirmed seats are exhausted.
        """
        if not passengers or len(passengers) == 0:
            return {"success": False, "error": "At least one passenger is required."}

        # 1. Validate date
        try:
            j_date = datetime.strptime(journey_date_str, "%Y-%m-%d").date()
            if j_date < date.today():
                return {"success": False, "error": "Journey date cannot be in the past."}
        except ValueError:
            return {"success": False, "error": "Invalid date format. Expected YYYY-MM-DD."}

        travel_class = str(travel_class).upper()
        if travel_class not in FareService.CLASS_MULTIPLIERS:
            travel_class = 'CC'

        num_passengers = len(passengers)

        try:
            with get_db_transaction() as (conn, cursor):
                # 2. Validate train and calculate dynamic fare breakdown
                cursor.execute(
                    "SELECT id, train_number, train_name, train_type, base_fare, is_active FROM trains WHERE id = %s",
                    (train_id,)
                )
                train = cursor.fetchone()
                if not train or not train['is_active']:
                    return {"success": False, "error": "Selected train is inactive or does not exist."}

                train_type = train.get('train_type') or 'EXPRESS'
                fare_breakdown = FareService.calculate_fare(
                    train_base_fare=train['base_fare'],
                    travel_class=travel_class,
                    train_type=train_type,
                    num_passengers=num_passengers
                )
                total_amount = fare_breakdown['total_amount']

                # 3. Retrieve available seats for this train, class and date with row-locking
                seat_query = """
                    SELECT s.id, s.coach_id, s.seat_number, s.berth_type, c.coach_number, c.coach_type
                    FROM seats s
                    INNER JOIN coaches c ON s.coach_id = c.id
                    WHERE c.train_id = %s AND c.coach_type = %s AND s.is_active = TRUE
                      AND s.id NOT IN (
                          SELECT seat_id FROM seat_allocations 
                          WHERE train_id = %s AND journey_date = %s
                      )
                    ORDER BY s.id ASC
                    FOR UPDATE
                """
                cursor.execute(seat_query, (train_id, travel_class, train_id, journey_date_str))
                available_seats_pool = cursor.fetchall()

                # If no coaches found for that exact class on this train, fall back to any available coach
                if not available_seats_pool:
                    cursor.execute("""
                        SELECT s.id, s.coach_id, s.seat_number, s.berth_type, c.coach_number, c.coach_type
                        FROM seats s
                        INNER JOIN coaches c ON s.coach_id = c.id
                        WHERE c.train_id = %s AND s.is_active = TRUE
                          AND s.id NOT IN (
                              SELECT seat_id FROM seat_allocations 
                              WHERE train_id = %s AND journey_date = %s
                          )
                        ORDER BY s.id ASC
                        FOR UPDATE
                    """, (train_id, train_id, journey_date_str))
                    available_seats_pool = cursor.fetchall()

                avail_seat_ids = [s['id'] for s in available_seats_pool]
                avail_seat_dict = {s['id']: s for s in available_seats_pool}

                num_confirmed = min(len(avail_seat_ids), num_passengers)
                num_waiting = num_passengers - num_confirmed

                # 4. Seat Allocation Strategy for confirmed passengers
                assigned_seats = []
                if requested_seat_ids:
                    for r_id in requested_seat_ids:
                        if r_id not in avail_seat_dict:
                            return {
                                "success": False,
                                "error": f"Seat ID {r_id} is no longer available. Please select another seat."
                            }
                    assigned_seats = [avail_seat_dict[r_id] for r_id in requested_seat_ids[:num_confirmed]]
                elif num_confirmed > 0:
                        # Match berth preference where possible
                        remaining_pool = list(available_seats_pool)
                        for idx in range(num_confirmed):
                            pax = passengers[idx]
                            pref = str(pax.get('berth_preference', 'NO_PREFERENCE')).upper()
                            matched_seat = None
                            if pref != 'NO_PREFERENCE':
                                for candidate in remaining_pool:
                                    if candidate['berth_type'].upper() == pref:
                                        matched_seat = candidate
                                        break
                            if not matched_seat and remaining_pool:
                                matched_seat = remaining_pool[0]

                            if matched_seat:
                                remaining_pool.remove(matched_seat)
                                assigned_seats.append(matched_seat)

                # Determine overall booking status
                if num_waiting == 0:
                    booking_status = 'CONFIRMED'
                elif num_confirmed > 0:
                    booking_status = 'RAC'
                else:
                    # Check if next queue position is RAC or WL
                    next_type, _, _ = WaitlistService.get_next_queue_position(cursor, train_id, journey_date_str, travel_class)
                    booking_status = next_type if next_type == 'RAC' else 'WAITLISTED'

                # 5. Generate unique PNR and insert Booking record
                pnr = generate_pnr()
                cursor.execute(
                    """
                    INSERT INTO bookings (
                        pnr, user_id, train_id, journey_date, travel_class,
                        base_amount, reservation_fee, superfast_charge, gst_amount, total_amount,
                        booking_status, payment_status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'SUCCESS')
                    """,
                    (
                        pnr, user_id, train_id, journey_date_str, travel_class,
                        fare_breakdown['total_base_amount'],
                        fare_breakdown['total_reservation_fee'],
                        fare_breakdown['total_superfast_charge'],
                        fare_breakdown['total_gst'],
                        total_amount,
                        booking_status
                    )
                )
                booking_id = cursor.lastrowid

                # 6. Insert Passenger records & Seat / Waitlist Allocations
                passengers_result = []
                for idx, pax in enumerate(passengers):
                    full_name = pax.get('full_name', f'Passenger {idx+1}').strip()
                    age = int(pax.get('age', 30))
                    gender = pax.get('gender', 'MALE').upper()
                    if gender not in ['MALE', 'FEMALE', 'OTHER']:
                        gender = 'OTHER'
                    berth_pref = pax.get('berth_preference', 'NO_PREFERENCE').upper()

                    if idx < num_confirmed:
                        # Confirmed passenger
                        seat = assigned_seats[idx]
                        seat_id = seat['id']
                        berth_str = f"{seat['coach_number']}-{seat['seat_number']} ({seat['berth_type']})"

                        cursor.execute(
                            """
                            INSERT INTO passengers (
                                booking_id, full_name, age, gender, berth_preference,
                                allocated_berth, seat_id, passenger_status
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, 'CONFIRMED')
                            """,
                            (booking_id, full_name, age, gender, berth_pref, berth_str, seat_id)
                        )
                        passenger_id = cursor.lastrowid

                        cursor.execute(
                            """
                            INSERT INTO seat_allocations (train_id, seat_id, journey_date, booking_id, passenger_id)
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (train_id, seat_id, journey_date_str, booking_id, passenger_id)
                        )

                        passengers_result.append({
                            "passenger_name": full_name,
                            "age": age,
                            "gender": gender,
                            "coach": seat['coach_number'],
                            "seat_number": seat['seat_number'],
                            "berth_type": seat['berth_type'],
                            "allocated_berth": berth_str,
                            "status": "CONFIRMED"
                        })
                    else:
                        # RAC or Waitlisted passenger
                        q_type, q_num, q_label = WaitlistService.get_next_queue_position(
                            cursor, train_id, journey_date_str, travel_class
                        )
                        p_status = 'RAC' if q_type == 'RAC' else 'WAITLISTED'

                        cursor.execute(
                            """
                            INSERT INTO passengers (
                                booking_id, full_name, age, gender, berth_preference,
                                allocated_berth, seat_id, passenger_status
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, NULL, %s)
                            """,
                            (booking_id, full_name, age, gender, berth_pref, q_label, p_status)
                        )
                        passenger_id = cursor.lastrowid

                        cursor.execute(
                            """
                            INSERT INTO waitlist_entries (
                                train_id, journey_date, travel_class, booking_id, passenger_id,
                                entry_type, queue_number, current_status
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, 'WAITING')
                            """,
                            (train_id, journey_date_str, travel_class, booking_id, passenger_id, q_type, q_num)
                        )

                        passengers_result.append({
                            "passenger_name": full_name,
                            "age": age,
                            "gender": gender,
                            "coach": "WL",
                            "seat_number": "-",
                            "berth_type": q_type,
                            "allocated_berth": q_label,
                            "status": p_status
                        })

                # 7. Record payment transaction in payments table
                txn_id = (payment_details or {}).get('transaction_id') or f"TXN-SIM-{uuid.uuid4().hex[:12].upper()}"
                pay_method = (payment_details or {}).get('payment_method', 'UPI').upper()
                if pay_method not in ['UPI', 'CARD', 'NET_BANKING']:
                    pay_method = 'UPI'
                bank_ref = (payment_details or {}).get('bank_ref_number') or f"REF-{random.randint(10000000, 99999999)}"

                cursor.execute(
                    """
                    INSERT INTO payments (
                        booking_id, transaction_id, payment_method, payment_gateway,
                        amount, status, bank_ref_number
                    )
                    VALUES (%s, %s, %s, 'Simulated Indian RailPay', %s, 'SUCCESS', %s)
                    """,
                    (booking_id, txn_id, pay_method, total_amount, bank_ref)
                )

                # 8. Issue Electronic Ticket Record
                ticket_number = f"TKT-{uuid.uuid4().hex[:10].upper()}"
                cursor.execute(
                    "INSERT INTO tickets (booking_id, ticket_number) VALUES (%s, %s)",
                    (booking_id, ticket_number)
                )

                return {
                    "success": True,
                    "pnr": pnr,
                    "ticket_number": ticket_number,
                    "booking_id": booking_id,
                    "booking_status": booking_status,
                    "travel_class": travel_class,
                    "total_amount": total_amount,
                    "fare_breakdown": fare_breakdown,
                    "journey_date": journey_date_str,
                    "assigned_seats": passengers_result,
                    "payment": {
                        "transaction_id": txn_id,
                        "payment_method": pay_method,
                        "bank_ref_number": bank_ref,
                        "status": "SUCCESS"
                    },
                    "message": f"Ticket successfully booked with status {booking_status}."
                }

        except Exception as e:
            return {"success": False, "error": f"Booking transaction failed: {str(e)}"}

    @staticmethod
    def get_user_bookings(user_id):
        query = """
            SELECT 
                b.id, b.pnr, b.journey_date, b.booking_status, b.travel_class,
                b.base_amount, b.reservation_fee, b.superfast_charge, b.gst_amount,
                b.total_amount, b.payment_status, b.created_at, b.cancelled_at,
                t.train_number, t.train_name, t.train_type, t.departure_time, t.arrival_time,
                s1.station_name AS source_station, s1.station_code AS source_code,
                s2.station_name AS dest_station, s2.station_code AS dest_code,
                (SELECT COUNT(*) FROM passengers WHERE booking_id = b.id) AS passenger_count,
                c.refund_amount, c.cancellation_charge
            FROM bookings b
            INNER JOIN trains t ON b.train_id = t.id
            INNER JOIN stations s1 ON t.source_station_id = s1.id
            INNER JOIN stations s2 ON t.destination_station_id = s2.id
            LEFT JOIN cancellations c ON c.booking_id = b.id
            WHERE b.user_id = %s
            ORDER BY b.created_at DESC
        """
        with get_db_connection() as (conn, cursor):
            cursor.execute(query, (user_id,))
            bookings = cursor.fetchall()
            for b in bookings:
                b['journey_date'] = str(b['journey_date'])
                b['departure_time'] = str(b['departure_time'])[:5]
                b['arrival_time'] = str(b['arrival_time'])[:5]
                b['created_at'] = str(b['created_at'])
                b['cancelled_at'] = str(b['cancelled_at']) if b['cancelled_at'] else None
                b['total_amount'] = float(b['total_amount'])
                b['refund_amount'] = float(b['refund_amount']) if b.get('refund_amount') is not None else None
                b['cancellation_charge'] = float(b['cancellation_charge']) if b.get('cancellation_charge') is not None else None
            return bookings

    @staticmethod
    def get_booking_by_pnr(pnr, user_id=None, is_admin=False):
        query = """
            SELECT 
                b.id, b.pnr, b.user_id, b.train_id, b.journey_date, b.booking_status, b.travel_class,
                b.base_amount, b.reservation_fee, b.superfast_charge, b.gst_amount,
                b.total_amount, b.payment_status, b.created_at, b.cancelled_at,
                t.train_number, t.train_name, t.train_type, t.departure_time, t.arrival_time,
                s1.station_name AS source_station, s1.station_code AS source_code,
                s2.station_name AS dest_station, s2.station_code AS dest_code
            FROM bookings b
            INNER JOIN trains t ON b.train_id = t.id
            INNER JOIN stations s1 ON t.source_station_id = s1.id
            INNER JOIN stations s2 ON t.destination_station_id = s2.id
            WHERE b.pnr = %s
        """
        with get_db_connection() as (conn, cursor):
            cursor.execute(query, (pnr,))
            b = cursor.fetchone()
            if not b:
                return None

            # Fetch passengers and assigned seat details
            pax_query = """
                SELECT 
                    p.id, p.full_name, p.age, p.gender, p.berth_preference, p.allocated_berth,
                    p.passenger_status, p.seat_id,
                    s.seat_number, s.berth_type, c.coach_number, c.coach_type
                FROM passengers p
                LEFT JOIN seats s ON p.seat_id = s.id
                LEFT JOIN coaches c ON s.coach_id = c.id
                WHERE p.booking_id = %s
            """
            cursor.execute(pax_query, (b['id'],))
            passengers = cursor.fetchall()

            # Fetch ticket details
            cursor.execute("SELECT ticket_number, issued_at FROM tickets WHERE booking_id = %s", (b['id'],))
            ticket = cursor.fetchone()

            # Fetch payment details
            cursor.execute(
                "SELECT transaction_id, payment_method, payment_gateway, amount, status, bank_ref_number, payment_time FROM payments WHERE booking_id = %s",
                (b['id'],)
            )
            payment = cursor.fetchone()

            # Fetch cancellation record if cancelled
            cancellation = None
            if b['booking_status'] == 'CANCELLED':
                cursor.execute(
                    "SELECT cancellation_number, gross_amount, cancellation_charge, refund_amount, refund_status, created_at FROM cancellations WHERE booking_id = %s",
                    (b['id'],)
                )
                cancellation = cursor.fetchone()

            # Check if caller is the authenticated booking owner or admin
            is_owner_or_admin = bool(is_admin or (user_id and b['user_id'] == user_id))
            if not is_owner_or_admin:
                b.pop('user_id', None)
                for p in passengers:
                    parts = p['full_name'].split()
                    if len(parts) > 1:
                        p['full_name'] = f"{parts[0]} {parts[-1][0]}***"
                    else:
                        p['full_name'] = f"{parts[0][:2]}***" if len(parts[0]) > 2 else "Passenger"
                    p['age'] = "**"

            b['journey_date'] = str(b['journey_date'])
            b['departure_time'] = str(b['departure_time'])[:5]
            b['arrival_time'] = str(b['arrival_time'])[:5]
            b['created_at'] = str(b['created_at'])
            b['cancelled_at'] = str(b['cancelled_at']) if b['cancelled_at'] else None
            b['total_amount'] = float(b['total_amount'])
            b['base_amount'] = float(b.get('base_amount') or 0.0)
            b['reservation_fee'] = float(b.get('reservation_fee') or 0.0)
            b['superfast_charge'] = float(b.get('superfast_charge') or 0.0)
            b['gst_amount'] = float(b.get('gst_amount') or 0.0)
            b['passengers'] = passengers
            b['ticket'] = ticket
            b['payment'] = payment
            b['cancellation'] = cancellation
            b['is_owner'] = is_owner_or_admin
            b['qr_code_url'] = f"/api/bookings/{pnr}/qr"

            return b

    @staticmethod
    def cancel_booking(pnr, user_id, is_admin=False):
        """
        Cancels an eligible booking, calculates cancellation charges and net refund,
        records in cancellations table, releases seats back to pool, and automatically
        promotes queued RAC / Waitlist passengers using WaitlistService.
        """
        try:
            with get_db_transaction() as (conn, cursor):
                cursor.execute(
                    """
                    SELECT id, user_id, train_id, journey_date, travel_class, booking_status, total_amount
                    FROM bookings 
                    WHERE pnr = %s 
                    FOR UPDATE
                    """,
                    (pnr,)
                )
                b = cursor.fetchone()
                if not b:
                    return {"success": False, "error": "Booking not found."}

                if not is_admin and b['user_id'] != user_id:
                    return {"success": False, "error": "Unauthorized to cancel this booking."}

                if b['booking_status'] == 'CANCELLED':
                    return {"success": False, "error": "Booking has already been cancelled."}

                booking_id = b['id']
                journey_date_str = str(b['journey_date'])
                travel_class = b.get('travel_class', 'CC')

                # Fetch passenger count and allocated seats
                cursor.execute(
                    "SELECT id, seat_id, passenger_status FROM passengers WHERE booking_id = %s FOR UPDATE",
                    (booking_id,)
                )
                passengers = cursor.fetchall()
                num_passengers = max(1, len(passengers))

                # Calculate cancellation fee and net simulated refund
                refund_calc = FareService.calculate_cancellation_refund(
                    total_amount=b['total_amount'],
                    booking_status=b['booking_status'],
                    travel_class=travel_class,
                    num_passengers=num_passengers
                )

                # Collect released seat IDs
                released_seat_ids = [p['seat_id'] for p in passengers if p['seat_id'] is not None]

                # 1. Update Booking status
                cursor.execute(
                    """
                    UPDATE bookings 
                    SET booking_status = 'CANCELLED', cancelled_at = NOW(), payment_status = 'REFUNDED' 
                    WHERE id = %s
                    """,
                    (booking_id,)
                )

                # 2. Update Passenger status
                cursor.execute(
                    "UPDATE passengers SET passenger_status = 'CANCELLED' WHERE booking_id = %s",
                    (booking_id,)
                )

                # 3. Release seat allocations
                cursor.execute(
                    "DELETE FROM seat_allocations WHERE booking_id = %s",
                    (booking_id,)
                )

                # 4. Cancel any waitlist entries belonging to this booking
                cursor.execute(
                    "UPDATE waitlist_entries SET current_status = 'CANCELLED' WHERE booking_id = %s",
                    (booking_id,)
                )

                # 5. Automatically promote queued RAC / WL passengers to released seats
                promoted_count = 0
                for s_id in released_seat_ids:
                    promoted, p_id = WaitlistService.promote_waitlist_on_seat_release(
                        cursor=cursor,
                        train_id=b['train_id'],
                        journey_date=journey_date_str,
                        travel_class=travel_class,
                        released_seat_id=s_id
                    )
                    if promoted:
                        promoted_count += 1

                # 6. Record official cancellation transaction
                cancellation_number = f"CAN-{uuid.uuid4().hex[:10].upper()}"
                cursor.execute(
                    """
                    INSERT INTO cancellations (
                        booking_id, cancellation_number, cancelled_by_user_id,
                        gross_amount, cancellation_charge, refund_amount, refund_status,
                        seats_released, waitlist_promoted_count
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, 'COMPLETED', %s, %s)
                    """,
                    (
                        booking_id, cancellation_number, user_id,
                        b['total_amount'], refund_calc['cancellation_fee'],
                        refund_calc['refund_amount'], len(released_seat_ids), promoted_count
                    )
                )

                # 7. Update payments status to REFUNDED
                cursor.execute(
                    "UPDATE payments SET status = 'REFUNDED' WHERE booking_id = %s",
                    (booking_id,)
                )

                return {
                    "success": True,
                    "pnr": pnr,
                    "cancellation_number": cancellation_number,
                    "gross_amount": b['total_amount'],
                    "cancellation_fee": refund_calc['cancellation_fee'],
                    "refund_amount": refund_calc['refund_amount'],
                    "seats_released": len(released_seat_ids),
                    "waitlist_promoted_count": promoted_count,
                    "message": f"Booking cancelled successfully. Refund of INR {refund_calc['refund_amount']:.2f} processed."
                }
        except Exception as e:
            return {"success": False, "error": f"Failed to cancel booking: {str(e)}"}
