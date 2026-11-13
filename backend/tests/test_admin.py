import uuid

def test_admin_dashboard_metrics(admin_client):
    res = admin_client.get('/api/admin/dashboard')
    assert res.status_code == 200
    data = res.get_json()
    assert 'metrics' in data
    m = data['metrics']
    assert 'total_users' in m
    assert 'total_trains' in m
    assert 'total_bookings' in m
    assert 'total_revenue' in m
    assert 'recent_bookings' in data

def test_admin_train_crud(admin_client):
    # 1. List trains
    res = admin_client.get('/api/admin/trains')
    assert res.status_code == 200
    trains = res.get_json()['trains']
    assert len(trains) >= 1
    t_id = trains[0]['id']
    initial_active = trains[0]['is_active']

    # 2. Toggle active status
    res_toggle = admin_client.delete(f'/api/admin/trains/{t_id}')
    assert res_toggle.status_code == 200

    # 3. Verify status inverted
    res_after = admin_client.get('/api/admin/trains')
    t_after = next(t for t in res_after.get_json()['trains'] if t['id'] == t_id)
    assert t_after['is_active'] != initial_active

    # 4. Toggle back
    admin_client.delete(f'/api/admin/trains/{t_id}')

def test_admin_station_crud_and_toggle(admin_client):
    unique_code = f"T{uuid.uuid4().hex[:4].upper()}"

    # 1. Create Station
    res_add = admin_client.post('/api/admin/stations', json={
        "station_code": unique_code,
        "station_name": "Test Junction",
        "city": "Testville"
    })
    assert res_add.status_code == 201
    station_id = res_add.get_json()['station_id']

    # 2. Retrieve stations and verify is_active field
    res_list = admin_client.get('/api/admin/stations')
    assert res_list.status_code == 200
    stations = res_list.get_json()['stations']
    target = next((s for s in stations if s['id'] == station_id), None)
    assert target is not None
    assert target['is_active'] is True

    # 3. Update Station Name
    res_upd = admin_client.put(f'/api/admin/stations/{station_id}', json={
        "station_name": "Updated Test Central",
        "city": "Metro City"
    })
    assert res_upd.status_code == 200

    # 4. Toggle Station Active Status (Deactivate)
    res_toggle = admin_client.delete(f'/api/admin/stations/{station_id}')
    assert res_toggle.status_code == 200

    # 5. Verify Inactive in admin list
    res_after = admin_client.get('/api/admin/stations')
    target_after = next(s for s in res_after.get_json()['stations'] if s['id'] == station_id)
    assert target_after['is_active'] is False
    assert target_after['station_name'] == "Updated Test Central"

    # 6. Toggle back to active
    res_toggle_back = admin_client.delete(f'/api/admin/stations/{station_id}')
    assert res_toggle_back.status_code == 200

def test_admin_bookings_audit(admin_client):
    res = admin_client.get('/api/admin/bookings')
    assert res.status_code == 200
    data = res.get_json()
    assert 'bookings' in data
    assert isinstance(data['bookings'], list)

def test_admin_diagnostics(admin_client):
    res = admin_client.get('/api/admin/diagnostics')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'HEALTHY'
    assert 'database' in data
    assert 'cpp_engine' in data
    assert 'os_primitives' in data

def test_regular_user_denied_admin_endpoints(user_client):
    endpoints = [
        ('GET', '/api/admin/dashboard'),
        ('GET', '/api/admin/trains'),
        ('POST', '/api/admin/trains'),
        ('GET', '/api/admin/stations'),
        ('POST', '/api/admin/stations'),
        ('GET', '/api/admin/bookings'),
        ('GET', '/api/admin/diagnostics'),
    ]
    for method, ep in endpoints:
        if method == 'GET':
            res = user_client.get(ep)
        else:
            res = user_client.post(ep, json={})
        assert res.status_code == 403, f"Endpoint {ep} should return 403 for regular user"

