import logging
from app.database.connection import get_db_connection

logger = logging.getLogger(__name__)

class WaitlistService:
    """
    Manages RAC (Reservation Against Cancellation) and Waiting List (WL) queues.
    Handles queue allocation and automatic FIFO promotion when confirmed seats become available.
    """

    MAX_RAC_CAPACITY = 8  # Maximum passengers eligible for RAC before moving to WL

    @classmethod
    def get_next_queue_position(cls, cursor, train_id, journey_date, travel_class):
        """
        Calculates next RAC or WL position for a journey date and class.
        Returns tuple: (entry_type, queue_number, label) e.g. ('RAC', 3, 'RAC-3') or ('WL', 2, 'WL-2')
        """
        cursor.execute("""
            SELECT entry_type, COUNT(*) AS count
            FROM waitlist_entries
            WHERE train_id = %s AND journey_date = %s AND travel_class = %s
              AND current_status = 'WAITING'
            GROUP BY entry_type
        """, (train_id, journey_date, travel_class))
        rows = cursor.fetchall()
        
        counts = {r['entry_type']: r['count'] for r in rows}
        rac_count = counts.get('RAC', 0)
        wl_count = counts.get('WL', 0)

        if rac_count < cls.MAX_RAC_CAPACITY:
            q_num = rac_count + 1
            return 'RAC', q_num, f"RAC {q_num}"
        else:
            q_num = wl_count + 1
            return 'WL', q_num, f"WL {q_num}"

    @classmethod
    def promote_waitlist_on_seat_release(cls, cursor, train_id, journey_date, travel_class, released_seat_id):
        """
        Called inside an InnoDB transaction when a confirmed seat is released via cancellation.
        Finds the highest priority RAC or WL passenger and promotes them to CONFIRMED.
        """
        # 1. Look for the earliest WAITING entry in RAC
        cursor.execute("""
            SELECT id, booking_id, passenger_id, entry_type, queue_number
            FROM waitlist_entries
            WHERE train_id = %s AND journey_date = %s AND travel_class = %s
              AND current_status = 'WAITING' AND entry_type = 'RAC'
            ORDER BY queue_number ASC, id ASC
            LIMIT 1
            FOR UPDATE
        """, (train_id, journey_date, travel_class))
        candidate = cursor.fetchone()

        # If no RAC waiting, look for earliest WL waiting
        if not candidate:
            cursor.execute("""
                SELECT id, booking_id, passenger_id, entry_type, queue_number
                FROM waitlist_entries
                WHERE train_id = %s AND journey_date = %s AND travel_class = %s
                  AND current_status = 'WAITING' AND entry_type = 'WL'
                ORDER BY queue_number ASC, id ASC
                LIMIT 1
                FOR UPDATE
            """, (train_id, journey_date, travel_class))
            candidate = cursor.fetchone()

        if not candidate:
            # No waiting passengers to promote
            return False, None

        wl_entry_id = candidate['id']
        b_id = candidate['booking_id']
        p_id = candidate['passenger_id']

        # 2. Allocate the released seat to this passenger
        cursor.execute("""
            INSERT INTO seat_allocations (train_id, seat_id, journey_date, booking_id, passenger_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (train_id, released_seat_id, journey_date, b_id, p_id))

        # 3. Lookup coach and seat number for berth label
        cursor.execute("""
            SELECT s.seat_number, s.berth_type, c.coach_number
            FROM seats s
            INNER JOIN coaches c ON s.coach_id = c.id
            WHERE s.id = %s
        """, (released_seat_id,))
        s_info = cursor.fetchone()
        berth_str = f"{s_info['coach_number']}-{s_info['seat_number']} ({s_info['berth_type']})" if s_info else f"Seat {released_seat_id}"

        # 4. Update Passenger record to CONFIRMED
        cursor.execute("""
            UPDATE passengers
            SET passenger_status = 'CONFIRMED', seat_id = %s, allocated_berth = %s
            WHERE id = %s
        """, (released_seat_id, berth_str, p_id))

        # 5. Check if all passengers in this booking are now CONFIRMED
        cursor.execute("""
            SELECT COUNT(*) AS total_non_confirmed
            FROM passengers
            WHERE booking_id = %s AND passenger_status != 'CONFIRMED'
        """, (b_id,))
        rem = cursor.fetchone()['total_non_confirmed']
        if rem == 0:
            cursor.execute("UPDATE bookings SET booking_status = 'CONFIRMED' WHERE id = %s", (b_id,))

        # 6. Mark waitlist entry as PROMOTED
        cursor.execute("UPDATE waitlist_entries SET current_status = 'PROMOTED' WHERE id = %s", (wl_entry_id,))

        logger.info(f"Promoted passenger {p_id} from {candidate['entry_type']} to CONFIRMED on seat {released_seat_id}")
        return True, p_id
