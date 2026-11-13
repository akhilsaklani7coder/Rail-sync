from flask import Blueprint, request, jsonify
from app.services.train_service import TrainService
from app.database.connection import get_db_connection
import logging

logger = logging.getLogger(__name__)

stations_bp = Blueprint('stations', __name__)

@stations_bp.route('', methods=['GET'])
@stations_bp.route('/', methods=['GET'])
def get_stations():
    """
    Returns active railway stations from MySQL.
    Supports query parameter 'q' for live filtering and 'sort_by' for ordering.
    Never returns mock/dummy data.
    """
    query = request.args.get('q', '').strip()
    sort_by = request.args.get('sort_by', 'name').lower()
    order = request.args.get('order', 'asc').upper()

    try:
        stations = TrainService.get_all_stations(search_query=query, sort_by=sort_by, order=order)
        return jsonify({
            "stations": stations,
            "count": len(stations)
        }), 200
    except Exception as err:
        logger.error(f"Failed to fetch stations from MySQL: {err}")
        return jsonify({
            "error": "Failed to retrieve stations from database.",
            "message": "Database connection or query failure."
        }), 503

@stations_bp.route('/health', methods=['GET'])
def station_health():
    """
    Station diagnostic endpoint verifying MySQL connectivity without exposing credentials.
    """
    try:
        with get_db_connection() as (conn, cursor):
            cursor.execute("SELECT COUNT(*) AS active_count FROM stations WHERE is_active = TRUE")
            row = cursor.fetchone()
            count = row['active_count'] if row else 0
            return jsonify({
                "status": "HEALTHY",
                "database_connected": True,
                "active_stations_count": count
            }), 200
    except Exception as err:
        logger.error(f"Station health check failed: {err}")
        return jsonify({
            "status": "DEGRADED",
            "database_connected": False,
            "error": "Unable to communicate with MySQL database."
        }), 503

@stations_bp.route('/<int:station_id>', methods=['GET'])
def get_station_by_id(station_id):
    """
    Returns details for a single station by its primary key ID.
    """
    try:
        station = TrainService.get_station_by_id(station_id)
        if not station:
            return jsonify({"error": f"Station with ID {station_id} not found."}), 404
        return jsonify({"station": station}), 200
    except Exception as err:
        logger.error(f"Error fetching station {station_id}: {err}")
        return jsonify({"error": "Database error retrieving station details."}), 503
