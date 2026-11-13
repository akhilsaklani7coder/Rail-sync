from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.database.connection import get_db_connection
from app.security.auth_helpers import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    full_name = data.get('full_name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    phone = data.get('phone', '').strip()
    address = data.get('address', '').strip()

    if not full_name or not email or not password:
        return jsonify({"error": "Full name, email, and password are required."}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long."}), 400

    with get_db_connection() as (conn, cursor):
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"error": "An account with this email address already exists."}), 409

        password_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (full_name, email, password_hash, role, phone, address) VALUES (%s, %s, %s, 'USER', %s, %s)",
            (full_name, email, password_hash, phone or None, address or None)
        )
        user_id = cursor.lastrowid

    session['user_id'] = user_id
    session['user_name'] = full_name
    session['user_email'] = email
    session['role'] = 'USER'

    return jsonify({
        "message": "Registration successful.",
        "user": {
            "id": user_id,
            "full_name": full_name,
            "email": email,
            "role": "USER",
            "phone": phone,
            "address": address
        }
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    with get_db_connection() as (conn, cursor):
        cursor.execute(
            "SELECT id, full_name, email, password_hash, role, phone, address FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()

        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({"error": "Invalid email or password."}), 401

    session['user_id'] = user['id']
    session['user_name'] = user['full_name']
    session['user_email'] = user['email']
    session['role'] = user['role']

    return jsonify({
        "message": "Login successful.",
        "user": {
            "id": user['id'],
            "full_name": user['full_name'],
            "email": user['email'],
            "role": user['role'],
            "phone": user.get('phone'),
            "address": user.get('address')
        }
    })

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Successfully logged out."})

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    if 'user_id' not in session:
        return jsonify({"user": None})

    with get_db_connection() as (conn, cursor):
        cursor.execute(
            "SELECT id, full_name, email, role, phone, address, created_at FROM users WHERE id = %s",
            (session['user_id'],)
        )
        user = cursor.fetchone()
        if not user:
            session.clear()
            return jsonify({"user": None})

        return jsonify({
            "user": {
                "id": user['id'],
                "full_name": user['full_name'],
                "email": user['email'],
                "role": user['role'],
                "phone": user.get('phone'),
                "address": user.get('address'),
                "created_at": str(user['created_at'])
            }
        })

@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    with get_db_connection() as (conn, cursor):
        cursor.execute(
            "SELECT id, full_name, email, role, phone, address, created_at FROM users WHERE id = %s",
            (session['user_id'],)
        )
        user = cursor.fetchone()
        if not user:
            return jsonify({"error": "User not found."}), 404

        user['created_at'] = str(user['created_at'])
        return jsonify({"profile": user})

@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    data = request.get_json() or {}
    full_name = data.get('full_name', '').strip()
    phone = data.get('phone', '').strip()
    address = data.get('address', '').strip()

    if not full_name:
        return jsonify({"error": "Full name cannot be empty."}), 400

    with get_db_connection() as (conn, cursor):
        cursor.execute(
            "UPDATE users SET full_name = %s, phone = %s, address = %s WHERE id = %s",
            (full_name, phone or None, address or None, session['user_id'])
        )
        session['user_name'] = full_name

        cursor.execute(
            "SELECT id, full_name, email, role, phone, address, created_at FROM users WHERE id = %s",
            (session['user_id'],)
        )
        updated = cursor.fetchone()
        updated['created_at'] = str(updated['created_at'])

    return jsonify({"message": "Profile updated successfully.", "profile": updated})

@auth_bp.route('/stats', methods=['GET'])
@login_required
def get_user_stats():
    user_id = session['user_id']
    with get_db_connection() as (conn, cursor):
        cursor.execute("SELECT COUNT(*) AS total_bookings FROM bookings WHERE user_id = %s", (user_id,))
        total_bookings = cursor.fetchone()['total_bookings']

        cursor.execute("SELECT COUNT(*) AS confirmed_bookings FROM bookings WHERE user_id = %s AND booking_status = 'CONFIRMED'", (user_id,))
        confirmed_bookings = cursor.fetchone()['confirmed_bookings']

        cursor.execute("SELECT COUNT(*) AS cancelled_bookings FROM bookings WHERE user_id = %s AND booking_status = 'CANCELLED'", (user_id,))
        cancelled_bookings = cursor.fetchone()['cancelled_bookings']

        cursor.execute("SELECT COALESCE(SUM(total_amount), 0) AS total_spent FROM bookings WHERE user_id = %s AND booking_status = 'CONFIRMED'", (user_id,))
        total_spent = float(cursor.fetchone()['total_spent'])

    return jsonify({
        "stats": {
            "total_bookings": total_bookings,
            "confirmed_bookings": confirmed_bookings,
            "cancelled_bookings": cancelled_bookings,
            "total_spent": total_spent
        }
    })
