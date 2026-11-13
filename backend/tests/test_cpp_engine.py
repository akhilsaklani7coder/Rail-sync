from app.services.cpp_engine_service import cpp_engine

def test_cpp_engine_status():
    status = cpp_engine.get_status()
    assert status['engine_version'] == 2026
    assert status['native_engine_active'] is True

def test_seat_allocation_contiguous_preference():
    # Available seats: 1, 2, 4, 5, 6, 9
    # Request 3 seats -> Should pick contiguous window [4, 5, 6]
    avail = [1, 2, 4, 5, 6, 9]
    chosen = cpp_engine.allocate_seats(avail, 3)
    assert chosen == [4, 5, 6]

def test_seat_allocation_insufficient_seats():
    avail = [10, 11]
    chosen = cpp_engine.allocate_seats(avail, 5)
    assert chosen is None

def test_dijkstra_shortest_path():
    edges = [(0, 1, 250), (1, 2, 52), (0, 2, 302)]
    res = cpp_engine.dijkstra_shortest_path(num_nodes=3, edges=edges, start_node=0, target_node=2)
    assert res['status'] == 'SUCCESS'
    assert res['distance_km'] == 302

def test_dijkstra_direct_connection():
    # Case 1: Direct single-hop edge
    edges = [(0, 1, 100)]
    res = cpp_engine.dijkstra_shortest_path(num_nodes=2, edges=edges, start_node=0, target_node=1)
    assert res['status'] == 'SUCCESS'
    assert res['distance_km'] == 100
    assert res['path'] == [0, 1]

def test_dijkstra_intermediate_stations():
    # Case 2: Multi-hop path 0 -> 1 -> 2
    edges = [(0, 1, 150), (1, 2, 200)]
    res = cpp_engine.dijkstra_shortest_path(num_nodes=3, edges=edges, start_node=0, target_node=2)
    assert res['status'] == 'SUCCESS'
    assert res['distance_km'] == 350
    assert res['path'] == [0, 1, 2]

def test_dijkstra_two_paths_different_distances():
    # Case 3: Path A (0->1->3: 400km) vs Path B (0->2->3: 250km)
    edges = [
        (0, 1, 100), (1, 3, 300), # Path A: 400
        (0, 2, 150), (2, 3, 100)  # Path B: 250 (Optimal)
    ]
    res = cpp_engine.dijkstra_shortest_path(num_nodes=4, edges=edges, start_node=0, target_node=3)
    assert res['status'] == 'SUCCESS'
    assert res['distance_km'] == 250
    assert res['path'] == [0, 2, 3]

def test_dijkstra_unreachable_destination():
    # Case 4: Disconnected graph component
    edges = [(0, 1, 100), (1, 2, 100)] # Node 3 is isolated
    res = cpp_engine.dijkstra_shortest_path(num_nodes=4, edges=edges, start_node=0, target_node=3)
    assert res['status'] in ['UNREACHABLE', 'FAILED']
    assert res['distance_km'] == -1
    assert res['path'] == []

def test_dijkstra_source_equals_destination():
    # Case 5: Identity routing
    edges = [(0, 1, 100)]
    res = cpp_engine.dijkstra_shortest_path(num_nodes=2, edges=edges, start_node=0, target_node=0)
    assert res['status'] == 'SUCCESS'
    assert res['distance_km'] == 0
    assert res['path'] == [0]

def test_dijkstra_invalid_station_input():
    # Case 6: Node out of bounds
    edges = [(0, 1, 100)]
    res = cpp_engine.dijkstra_shortest_path(num_nodes=2, edges=edges, start_node=-1, target_node=1)
    assert res['status'] in ['INVALID_INPUT', 'FAILED']
    assert res['distance_km'] == -1

def test_cpp_mutex_verification():
    res = cpp_engine.verify_mutex(iterations=1000)
    assert res['status'] == 'SUCCESS'
    assert res['iterations'] == 1000
