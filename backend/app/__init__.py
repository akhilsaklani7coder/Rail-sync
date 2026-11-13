import time
from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config
from app.database.connection import init_connection_pool

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize MySQL Connection Pool
    init_connection_pool()

    # Configure CORS for local development with frontend credentials
    CORS(
        app,
        supports_credentials=True,
        origins=config_class.CORS_ORIGINS,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-CSRFToken"]
    )

    # Health Check Endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "UP",
            "service": "RailSync Backend API",
            "environment": "development",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.trains import trains_bp
    from app.routes.stations import stations_bp
    from app.routes.bookings import bookings_bp
    from app.routes.payments import payments_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(trains_bp, url_prefix='/api/trains')
    app.register_blueprint(stations_bp, url_prefix='/api/stations')
    app.register_blueprint(bookings_bp, url_prefix='/api/bookings')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    return app
