import uuid

def test_login_success(client):
    res = client.post('/api/auth/login', json={
        "email": "user@railsync.com",
        "password": "User@123"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['user']['email'] == "user@railsync.com"
    assert data['user']['role'] == "USER"

def test_login_invalid_password(client):
    res = client.post('/api/auth/login', json={
        "email": "user@railsync.com",
        "password": "WrongPassword999"
    })
    assert res.status_code == 401
    assert "error" in res.get_json()

def test_register_and_duplicate_rejection(client):
    unique_email = f"passenger_{uuid.uuid4().hex[:6]}@test.com"
    
    # 1. Successful Registration
    res = client.post('/api/auth/register', json={
        "full_name": "Test Passenger",
        "email": unique_email,
        "password": "Password123!"
    })
    assert res.status_code == 201
    assert res.get_json()['user']['email'] == unique_email

    # 2. Duplicate Registration Rejection
    res_dup = client.post('/api/auth/register', json={
        "full_name": "Duplicate Tester",
        "email": unique_email,
        "password": "Password123!"
    })
    assert res_dup.status_code == 409
    assert "already exists" in res_dup.get_json()['error']

def test_protected_endpoint_without_login(client):
    # Logging out first
    client.post('/api/auth/logout')
    res = client.get('/api/bookings/my')
    assert res.status_code == 401
    assert "Authentication required" in res.get_json()['error']

def test_admin_authorization_enforcement(user_client):
    # Regular user attempting to access admin dashboard
    res = user_client.get('/api/admin/dashboard')
    assert res.status_code == 403
    assert "Admin privilege required" in res.get_json()['error']
