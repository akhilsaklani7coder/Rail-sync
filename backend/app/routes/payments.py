from flask import Blueprint, request, jsonify
import time
import uuid
import random
from app.database.connection import get_db_connection

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/simulate', methods=['POST'])
def simulate_payment():
    data = request.get_json() or {}
    amount = float(data.get('amount', 0))
    outcome = data.get('outcome', 'SUCCESS').upper() # SUCCESS or FAILURE
    method = data.get('payment_method', 'UPI').upper()
    if method not in ['UPI', 'CARD', 'NET_BANKING']:
        method = 'UPI'
    booking_id = data.get('booking_id')

    # Simulate realistic gateway network handshake
    time.sleep(0.3)

    txn_id = f"TXN-SIM-{uuid.uuid4().hex[:12].upper()}"
    bank_ref = f"REF-{random.randint(10000000, 99999999)}"

    if outcome == 'FAILURE':
        return jsonify({
            "status": "FAILED",
            "transaction_id": txn_id,
            "bank_ref_number": bank_ref,
            "payment_method": method,
            "message": "Payment simulation was intentionally declined or marked as failed."
        }), 400

    # If booking_id provided, record into payments table
    if booking_id:
        try:
            with get_db_connection() as (conn, cursor):
                cursor.execute(
                    """
                    INSERT INTO payments (booking_id, transaction_id, payment_method, payment_gateway, amount, status, bank_ref_number)
                    VALUES (%s, %s, %s, 'Simulated Indian RailPay', %s, 'SUCCESS', %s)
                    """,
                    (booking_id, txn_id, method, amount, bank_ref)
                )
        except Exception:
            pass

    return jsonify({
        "status": "SUCCESS",
        "transaction_id": txn_id,
        "bank_ref_number": bank_ref,
        "amount": amount,
        "payment_method": method,
        "payment_gateway": "Simulated Indian RailPay Gateway",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "message": "Simulated payment captured successfully."
    })
