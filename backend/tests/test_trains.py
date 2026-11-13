from datetime import date, timedelta

def test_get_stations(client):
    res = client.get('/api/trains/stations')
    assert res.status_code == 200
    stations = res.get_json()['stations']
    assert len(stations) >= 8
    codes = [s['station_code'] for s in stations]
    assert 'NDLS' in codes
    assert 'DDN' in codes

def test_search_trains_valid_route(client):
    # NDLS (1) to DDN (2)
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    res = client.get(f'/api/trains/search?source_id=1&dest_id=2&date={tomorrow}')
    assert res.status_code == 200
    data = res.get_json()
    assert data['count'] >= 1
    train = data['trains'][0]
    assert train['train_number'] == "12017"
    assert train['total_available_seats'] > 0

def test_search_trains_no_direct_route(client):
    # Non-existent pair, e.g. Haridwar (3) to Mumbai Central (6)
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    res = client.get(f'/api/trains/search?source_id=3&dest_id=6&date={tomorrow}')
    assert res.status_code == 200
    data = res.get_json()
    assert data['count'] == 0

def test_search_trains_past_date(client):
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    res = client.get(f'/api/trains/search?source_id=1&dest_id=2&date={yesterday}')
    assert res.status_code == 400
    assert "past" in res.get_json()['error'].lower()

def test_train_seat_availability_map(client):
    tomorrow = (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")
    res = client.get(f'/api/trains/1/availability?date={tomorrow}')
    assert res.status_code == 200
    data = res.get_json()
    assert 'coaches' in data
    assert len(data['coaches']) >= 1
    seats = data['coaches'][0]['seats']
    assert len(seats) >= 16
    assert seats[0]['status'] in ['AVAILABLE', 'BOOKED']

def test_search_trains_same_source_and_destination(client):
    res = client.get('/api/trains/search?source_id=1&dest_id=1&date=2026-11-20')
    assert res.status_code == 400
    assert "same" in res.get_json()['error'].lower()

def test_network_shortest_path_dijkstra(client):
    res = client.get('/api/trains/shortest-path?source_id=1&dest_id=7')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'SUCCESS'
    assert data['total_distance_km'] == 933
    assert len(data['path']) == 3
    assert 'C++' in data['engine']

def test_popular_and_featured_trains(client):
    res_pop = client.get('/api/trains/popular-routes')
    assert res_pop.status_code == 200
    assert len(res_pop.get_json()['routes']) >= 4

    res_feat = client.get('/api/trains/featured')
    assert res_feat.status_code == 200
    assert len(res_feat.get_json()['trains']) >= 4

def test_dedicated_stations_api_endpoint(client):
    res = client.get('/api/stations')
    assert res.status_code == 200
    data = res.get_json()
    assert 'stations' in data
    assert data['count'] >= 20
    
    # Test query filter
    res_filtered = client.get('/api/stations?q=mumbai')
    assert res_filtered.status_code == 200
    filtered_data = res_filtered.get_json()
    assert filtered_data['count'] >= 2
    for s in filtered_data['stations']:
        assert 'mumbai' in s['city'].lower() or 'mumbai' in s['station_name'].lower()

def test_station_health_endpoint(client):
    res = client.get('/api/stations/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'HEALTHY'
    assert data['database_connected'] is True
    assert data['active_stations_count'] >= 20

def test_search_trains_invalid_station_ids(client):
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    res = client.get(f'/api/trains/search?source_id=99999&dest_id=88888&date={tomorrow}')
    assert res.status_code == 400
    assert "not exist" in res.get_json()['error'].lower()

