import pytest
from datetime import date, timedelta
import uuid

def test_payment_simulation_success(client):
    """
    Verifies that simulated payment with outcome=SUCCESS captures funds and returns gateway references.
    """
    res = client.post('/api/payments/simulate', json={
        "amount": 1450.00,
        "payment_method": "UPI",
        "outcome": "SUCCESS"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'SUCCESS'
    assert 'transaction_id' in data
    assert 'bank_ref_number' in data
    assert data['payment_method'] == 'UPI'

def test_payment_simulation_decline(client):
    """
    Verifies that simulated payment with outcome=FAILURE gracefully returns decline metadata and retry flag.
    """
    res = client.post('/api/payments/simulate', json={
        "amount": 1450.00,
        "payment_method": "CARD",
        "outcome": "FAILURE"
    })
    assert res.status_code == 400
    data = res.get_json()
    assert data['status'] == 'FAILED'
    assert data['can_retry'] is True
    assert 'transaction_id' in data

def test_booking_idempotency_prevents_duplicate_reservations(user_client):
    """
    Verifies that submitting the same transaction_id twice does not create duplicate
    records or allocate duplicate seats (idempotent checkout).
    """
    test_date = (date.today() + timedelta(days=28)).strftime("%Y-%m-%d")
    unique_txn_id = f"TXN-TEST-IDEMP-{uuid.uuid4().hex[:8].upper()}"

    booking_payload = {
        "train_id": 1,
        "journey_date": test_date,
        "travel_class": "CC",
        "passengers": [
            {"full_name": "Idempotent Passenger", "age": 30, "gender": "MALE"}
        ],
        "payment_details": {
            "transaction_id": unique_txn_id,
            "payment_method": "UPI",
            "bank_ref_number": "REF-IDEMP-001"
        }
    }

    # First attempt: Initial booking creation
    res1 = user_client.post('/api/bookings', json=booking_payload)
    assert res1.status_code == 201
    data1 = res1.get_json()
    assert data1['success'] is True
    pnr1 = data1['pnr']

    # Second attempt: Duplicate submission with same transaction_id
    res2 = user_client.post('/api/bookings', json=booking_payload)
    assert res2.status_code in [200, 201]
    data2 = res2.get_json()
    assert data2['success'] is True
    assert data2.get('is_duplicate') is True
    assert data2['pnr'] == pnr1

def test_keyword_search_for_expanded_categories(client):
    """
    Verifies searching by keyword for newly added categories (Duronto, Garib Rath, Intercity).
    """
    res_duronto = client.get('/api/trains/search?train_query=Duronto')
    assert res_duronto.status_code == 200
    duronto_data = res_duronto.get_json()
    assert duronto_data['count'] >= 4
    for t in duronto_data['trains']:
        assert t['train_type'] == 'DURONTO'

    res_gr = client.get('/api/trains/search?train_query=Garib%20Rath')
    assert res_gr.status_code == 200
    gr_data = res_gr.get_json()
    assert gr_data['count'] >= 2
    for t in gr_data['trains']:
        assert t['train_type'] == 'GARIB_RATH'

def test_intermediate_station_route_matching(client):
    """
    Verifies that searching between intermediate stops (e.g. Kanpur Central 40 -> Prayagraj 41)
    returns trains that halt at those stations in order.
    """
    res = client.get('/api/trains/search?source_id=40&dest_id=41')
    assert res.status_code == 200
    data = res.get_json()
    assert data['count'] >= 1
    # Vande Bharat or Howrah Rajdhani stops at both Kanpur and Prayagraj
    train_numbers = [t['train_number'] for t in data['trains']]
    assert any(num in ['22436', '12302'] for num in train_numbers)

