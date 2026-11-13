from datetime import date, timedelta

def test_full_booking_and_cancellation_workflow(user_client):
    test_date = (date.today() + timedelta(days=14)).strftime("%Y-%m-%d")

    # 1. Create a booking with 2 passengers
    payload = {
        "train_id": 1,
        "journey_date": test_date,
        "passengers": [
            {"full_name": "Rohan Sharma", "age": 28, "gender": "MALE"},
            {"full_name": "Pooja Sharma", "age": 26, "gender": "FEMALE"}
        ]
    }
    res = user_client.post('/api/bookings', json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    pnr = data['pnr']
    assert pnr.startswith("RS")
    assert len(data['assigned_seats']) == 2

    # 2. Query booking by PNR
    res_pnr = user_client.get(f'/api/bookings/{pnr}')
    assert res_pnr.status_code == 200
    b_data = res_pnr.get_json()['booking']
    assert b_data['pnr'] == pnr
    assert b_data['booking_status'] == 'CONFIRMED'
    assert len(b_data['passengers']) == 2

    # 3. Check Booking in User History
    res_my = user_client.get('/api/bookings/my')
    assert res_my.status_code == 200
    my_pnrs = [b['pnr'] for b in res_my.get_json()['bookings']]
    assert pnr in my_pnrs

    # 4. Generate PDF e-ticket
    res_pdf = user_client.get(f'/api/bookings/{pnr}/ticket.pdf')
    assert res_pdf.status_code == 200
    assert res_pdf.mimetype == 'application/pdf'
    assert len(res_pdf.data) > 1000

    # 5. Cancel Booking
    res_cancel = user_client.post(f'/api/bookings/{pnr}/cancel')
    assert res_cancel.status_code == 200
    assert res_cancel.get_json()['success'] is True

    # 6. Verify Status is now CANCELLED
    res_pnr_after = user_client.get(f'/api/bookings/{pnr}')
    assert res_pnr_after.get_json()['booking']['booking_status'] == 'CANCELLED'

    # 7. Repeated Cancellation is rejected
    res_cancel_again = user_client.post(f'/api/bookings/{pnr}/cancel')
    assert res_cancel_again.status_code == 400
    assert "already been cancelled" in res_cancel_again.get_json()['error']

def test_competing_bookings_same_seat(user_client):
    """
    Stage Five verification: Two competing requests targeting the exact same seat
    on the same train and journey date. The first commits, the second is rejected.
    """
    from app.database.connection import get_db_connection
    test_date = (date.today() + timedelta(days=35)).strftime("%Y-%m-%d")

    # Find an unallocated seat on train 1 for this date
    with get_db_connection() as (conn, cur):
        cur.execute("""
            SELECT s.id FROM seats s
            INNER JOIN coaches c ON s.coach_id = c.id
            WHERE c.train_id = 1 AND s.id NOT IN (
                SELECT seat_id FROM seat_allocations WHERE train_id = 1 AND journey_date = %s
            ) ORDER BY s.id ASC LIMIT 1
        """, (test_date,))
        target_seat_id = cur.fetchone()['id']

    payload_1 = {
        "train_id": 1,
        "journey_date": test_date,
        "requested_seat_ids": [target_seat_id],
        "passengers": [{"full_name": "Passenger Alpha", "age": 30, "gender": "MALE"}]
    }
    payload_2 = {
        "train_id": 1,
        "journey_date": test_date,
        "requested_seat_ids": [target_seat_id],
        "passengers": [{"full_name": "Passenger Beta", "age": 29, "gender": "FEMALE"}]
    }

    # First request books target seat
    res1 = user_client.post('/api/bookings', json=payload_1)
    assert res1.status_code == 201
    assert res1.get_json()['success'] is True

    # Second competing request targeting the same seat must be rejected
    res2 = user_client.post('/api/bookings', json=payload_2)
    assert res2.status_code == 400
    assert "no longer available" in res2.get_json()['error'].lower()

def test_pnr_status_masked_for_non_owner(user_client, client):
    """
    Verifies that an unauthenticated guest or non-owner can check PNR status,
    with passenger names masked for privacy and is_owner flag set to False.
    """
    test_date = (date.today() + timedelta(days=20)).strftime("%Y-%m-%d")
    payload = {
        "train_id": 1,
        "journey_date": test_date,
        "passengers": [
            {"full_name": "Vikramaditya Singhania", "age": 34, "gender": "MALE"}
        ]
    }
    # Create booking as user_client
    res = user_client.post('/api/bookings', json=payload)
    assert res.status_code == 201
    pnr = res.get_json()['pnr']

    # Query as unauthenticated guest client
    res_guest = client.get(f'/api/bookings/{pnr}')
    assert res_guest.status_code == 200
    b_data = res_guest.get_json()['booking']
    assert b_data['pnr'] == pnr
    assert b_data['is_owner'] is False
    assert 'user_id' not in b_data
    # Passenger name must be masked (e.g. Vikramaditya S***)
    pax = b_data['passengers'][0]
    assert '***' in pax['full_name']
    assert pax['age'] == '**'

def test_unauthorized_pdf_download_rejected(user_client, client):
    """
    Verifies that an unauthenticated guest or non-owner cannot download
    the PDF ticket and receives HTTP 403 Forbidden.
    """
    test_date = (date.today() + timedelta(days=22)).strftime("%Y-%m-%d")
    payload = {
        "train_id": 1,
        "journey_date": test_date,
        "passengers": [
            {"full_name": "Ananya Roy", "age": 27, "gender": "FEMALE"}
        ]
    }
    res = user_client.post('/api/bookings', json=payload)
    assert res.status_code == 201
    pnr = res.get_json()['pnr']

    # Attempt PDF download as guest (should be 403 Forbidden)
    res_guest_pdf = client.get(f'/api/bookings/{pnr}/ticket.pdf')
    assert res_guest_pdf.status_code == 403
    assert "Unauthorized" in res_guest_pdf.get_json()['error']

    # Attempt PDF download as owner (should be 200 OK)
    res_owner_pdf = user_client.get(f'/api/bookings/{pnr}/ticket.pdf')
    assert res_owner_pdf.status_code == 200
    assert res_owner_pdf.mimetype == 'application/pdf'
