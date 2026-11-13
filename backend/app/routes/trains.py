from flask import Blueprint, request, jsonify
from app.services.train_service import TrainService

trains_bp = Blueprint('trains', __name__)

@trains_bp.route('/stations', methods=['GET'])
def get_stations():
    query = request.args.get('q', '').strip()
    sort_by = request.args.get('sort_by', 'name').lower()
    order = request.args.get('order', 'asc').upper()
    stations = TrainService.get_all_stations(search_query=query, sort_by=sort_by, order=order)
    return jsonify({"stations": stations, "count": len(stations)})

@trains_bp.route('/popular-routes', methods=['GET'])
def get_popular_routes():
    routes = TrainService.get_popular_routes()
    return jsonify({"routes": routes})

@trains_bp.route('/featured', methods=['GET'])
def get_featured_trains():
    trains = TrainService.get_featured_trains()
    return jsonify({"trains": trains})

@trains_bp.route('/shortest-path', methods=['GET'])
def get_shortest_path():
    src_id = request.args.get('source_id', type=int)
    dst_id = request.args.get('dest_id', type=int)
    if not src_id or not dst_id:
        return jsonify({"error": "source_id and dest_id parameters are required."}), 400
    if src_id == dst_id:
        return jsonify({"error": "Source and destination stations cannot be the same."}), 400

    result = TrainService.get_network_shortest_path(src_id, dst_id)
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)

@trains_bp.route('/search', methods=['GET'])
def search():
    src_id = request.args.get('source_id', type=int)
    dst_id = request.args.get('dest_id', type=int)
    j_date = request.args.get('date', type=str)
    travel_class = request.args.get('class', type=str)
    train_type = request.args.get('train_type', type=str)
    departure_slot = request.args.get('departure_slot', type=str)

    if not src_id or not dst_id:
        return jsonify({"error": "Source station and Destination station are required."}), 400
    if src_id == dst_id:
        return jsonify({"error": "Source and destination stations cannot be the same."}), 400

    results = TrainService.search_trains(
        source_id=src_id,
        destination_id=dst_id,
        journey_date_str=j_date,
        travel_class=travel_class,
        train_type=train_type,
        departure_slot=departure_slot
    )
    if isinstance(results, dict) and 'error' in results:
        return jsonify(results), 400

    # Also compute Dijkstra shortest path between these two stations via C++ engine
    dijkstra_path = TrainService.get_network_shortest_path(src_id, dst_id)

    return jsonify({
        "trains": results,
        "count": len(results),
        "dijkstra_path": dijkstra_path if dijkstra_path.get('status') == 'SUCCESS' else None
    })

@trains_bp.route('/<int:train_id>', methods=['GET'])
def get_train(train_id):
    train = TrainService.get_train_details(train_id)
    if not train:
        return jsonify({"error": "Train not found."}), 404
    return jsonify({"train": train})

@trains_bp.route('/<int:train_id>/stops', methods=['GET'])
def get_train_stops(train_id):
    """
    Returns the ordered intermediate timetable schedule for a train.
    """
    stops = TrainService.get_train_stops(train_id)
    return jsonify({"train_id": train_id, "stops": stops, "count": len(stops)})

@trains_bp.route('/fare-quote', methods=['GET'])
def get_fare_quote():
    """
    Returns dynamic multi-class fare quote with base fare, reservation fee, superfast charge, and GST.
    """
    train_id = request.args.get('train_id', type=int)
    travel_class = request.args.get('class', default='CC', type=str)
    passengers = request.args.get('passengers', default=1, type=int)

    if not train_id:
        return jsonify({"error": "train_id parameter is required."}), 400

    quote = TrainService.get_fare_quote(train_id, travel_class=travel_class, num_passengers=passengers)
    if 'error' in quote:
        return jsonify(quote), 400

    return jsonify(quote)

@trains_bp.route('/<int:train_id>/availability', methods=['GET'])
def get_availability(train_id):
    j_date = request.args.get('date')
    if not j_date:
        return jsonify({"error": "Journey date parameter 'date' (YYYY-MM-DD) is required."}), 400

    seat_map = TrainService.get_train_seat_map(train_id, j_date)
    return jsonify({"train_id": train_id, "journey_date": j_date, "coaches": seat_map})
