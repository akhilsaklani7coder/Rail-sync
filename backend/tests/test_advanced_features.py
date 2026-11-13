import pytest
from datetime import date, timedelta
from app.services.fare_service import FareService

def test_fare_calculation_service():
    # AC Chair Car
    cc_quote = FareService.calculate_fare(train_base_fare=500.0, travel_class='CC', train_type='SUPERFAST', num_passengers=1)
    assert cc_quote['travel_class'] == 'CC'
    assert cc_quote['class_fare_per_passenger'] == 500.0
    assert cc_quote['reservation_fee_per_passenger'] == 40.0
    assert cc_quote['superfast_charge_per_passenger'] == 45.0
    # subtotal = 585; GST 5% = 29.25; total = 614.25
    assert cc_quote['gst_per_passenger'] == 29.25
    assert cc_quote['total_amount'] == 614.25

    # Sleeper Class (0% GST)
    sl_quote = FareService.calculate_fare(train_base_fare=500.0, travel_class='SL', train_type='EXPRESS', num_passengers=2)
    assert sl_quote['travel_class'] == 'SL'
    assert sl_quote['gst_per_passenger'] == 0.0
    assert sl_quote['total_reservation_fee'] == 40.0 # 20 * 2
    assert sl_quote['total_amount'] > 0

def test_cancellation_refund_rules():
    # Confirmed AC ticket cancellation
    refund_ac = FareService.calculate_cancellation_refund(total_amount=1000.0, booking_status='CONFIRMED', travel_class='3A', num_passengers=1)
    assert refund_ac['cancellation_fee'] == 120.0
    assert refund_ac['refund_amount'] == 880.0

    # Waitlisted ticket clerkage cancellation fee
    refund_wl = FareService.calculate_cancellation_refund(total_amount=1000.0, booking_status='WAITLISTED', travel_class='3A', num_passengers=2)
    assert refund_wl['cancellation_fee'] == 120.0 # 60 * 2
    assert refund_wl['refund_amount'] == 880.0

def test_fare_quote_api(client):
    res = client.get('/api/trains/fare-quote?train_id=1&class=3A&passengers=2')
    assert res.status_code == 200
    data = res.get_json()
    assert data['travel_class'] == '3A'
    assert data['num_passengers'] == 2
    assert 'total_amount' in data
    assert data['total_amount'] > 0

def test_train_intermediate_stops_api(client):
    res = client.get('/api/trains/1/stops')
    assert res.status_code == 200
    data = res.get_json()
    assert 'stops' in data
    assert isinstance(data['stops'], list)
    assert data['count'] >= 1
    first_stop = data['stops'][0]
    assert 'station_code' in first_stop
    assert 'stop_sequence' in first_stop

def test_booking_qr_code_stream(user_client):
    test_date = (date.today() + timedelta(days=25)).strftime("%Y-%m-%d")
    payload = {
        "train_id": 1,
        "journey_date": test_date,
        "travel_class": "CC",
        "passengers": [
            {"full_name": "Aarav Sharma", "age": 28, "gender": "MALE", "berth_preference": "WINDOW"}
        ]
    }
    b_res = user_client.post('/api/bookings', json=payload)
    assert b_res.status_code == 201
    pnr = b_res.get_json()['pnr']

    qr_res = user_client.get(f'/api/bookings/{pnr}/qr')
    assert qr_res.status_code == 200
    assert qr_res.content_type == 'image/png'
    assert len(qr_res.data) > 100

def test_user_profile_and_stats(user_client):
    # Get profile
    res_prof = user_client.get('/api/auth/profile')
    assert res_prof.status_code == 200
    prof = res_prof.get_json()['profile']
    assert 'email' in prof

    # Update profile
    res_upd = user_client.put('/api/auth/profile', json={
        "full_name": "Updated User Name",
        "phone": "9876543210",
        "address": "221B Baker Street, New Delhi"
    })
    assert res_upd.status_code == 200
    assert res_upd.get_json()['profile']['phone'] == "9876543210"

    # Get stats
    res_stats = user_client.get('/api/auth/stats')
    assert res_stats.status_code == 200
    stats = res_stats.get_json()['stats']
    assert 'total_bookings' in stats
    assert 'confirmed_bookings' in stats
    assert 'total_spent' in stats

def test_payment_simulation_endpoint(client):
    # Test success
    res_success = client.post('/api/payments/simulate', json={
        "amount": 1250.00,
        "payment_method": "UPI",
        "outcome": "SUCCESS"
    })
    assert res_success.status_code == 200
    data = res_success.get_json()
    assert data['status'] == 'SUCCESS'
    assert 'transaction_id' in data
    assert data['amount'] == 1250.00

    # Test failure outcome
    res_fail = client.post('/api/payments/simulate', json={
        "amount": 1250.00,
        "payment_method": "CARD",
        "outcome": "FAILURE"
    })
    assert res_fail.status_code == 400
    assert res_fail.get_json()['status'] == 'FAILED'

def test_admin_train_stops_management(admin_client):
    res_stops = admin_client.get('/api/admin/trains/1/stops')
    assert res_stops.status_code == 200
    assert 'stops' in res_stops.get_json()
