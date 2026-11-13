import concurrent.futures
from datetime import date, timedelta
from app.database.connection import get_db_transaction, get_db_connection
from app.services.booking_service import BookingService

def test_innodb_acid_rollback():
    """
    Verifies that an unhandled exception inside get_db_transaction()
    rolls back all intermediate writes to MySQL InnoDB, preserving atomicity.
    """
    test_email = "rollback_tester@test.com"
    
    # Ensure clean starting state
    with get_db_connection() as (conn, cur):
        cur.execute("DELETE FROM users WHERE email = %s", (test_email,))

    try:
        with get_db_transaction() as (conn, cur):
            cur.execute(
                "INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, 'USER')",
                ("Temp Rollback User", test_email, "dummyhash")
            )
            # Raise exception mid-transaction to force automatic rollback
            raise RuntimeError("Intentional mid-transaction failure for ACID rollback test")
    except RuntimeError:
        pass

    # Verify atomicity: 0 rows persisted in MySQL
    with get_db_connection() as (conn, cur):
        cur.execute("SELECT id FROM users WHERE email = %s", (test_email,))
        row = cur.fetchone()
        assert row is None, "Record must not persist after rollback"

def test_row_level_locking_concurrency():
    """
    Tests that simultaneous concurrent threads attempting to book the exact same seat
    result in exactly 1 successful booking and 0 duplicate allocations in MySQL.
    """
    test_date = (date.today() + timedelta(days=40)).strftime("%Y-%m-%d")

    # Find an available seat
    with get_db_connection() as (conn, cur):
        cur.execute("""
            SELECT s.id FROM seats s
            INNER JOIN coaches c ON s.coach_id = c.id
            WHERE c.train_id = 1 AND s.is_active = TRUE
              AND s.id NOT IN (
                  SELECT seat_id FROM seat_allocations WHERE train_id = 1 AND journey_date = %s
              )
            ORDER BY s.id ASC LIMIT 1
        """, (test_date,))
        target_seat = cur.fetchone()['id']

    num_threads = 6
    def attempt_booking(thread_idx):
        return BookingService.create_booking(
            user_id=2, # Demo Passenger
            train_id=1,
            journey_date_str=test_date,
            passengers=[{"full_name": f"Concurrent Traveler {thread_idx}", "age": 25, "gender": "MALE"}],
            requested_seat_ids=[target_seat]
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(attempt_booking, i) for i in range(num_threads)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    success_count = sum(1 for r in results if r.get('success') is True)
    failure_count = sum(1 for r in results if r.get('success') is False)

    assert success_count == 1, f"Exactly 1 booking must succeed, got {success_count}"
    assert failure_count == num_threads - 1

    # Verify seat_allocations table has exactly 1 row for target_seat on test_date
    with get_db_connection() as (conn, cur):
        cur.execute(
            "SELECT COUNT(*) AS c FROM seat_allocations WHERE seat_id = %s AND journey_date = %s",
            (target_seat, test_date)
        )
        persisted = cur.fetchone()['c']
        assert persisted == 1
