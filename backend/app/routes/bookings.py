from flask import Blueprint, request, jsonify, session, send_file, Response
import io
import qrcode
from app.services.booking_service import BookingService
from app.services.pdf_service import generate_ticket_pdf
from app.security.auth_helpers import login_required

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('', methods=['POST'])
@login_required
def create_booking():
    data = request.get_json() or {}
    train_id = data.get('train_id')
    journey_date = data.get('journey_date')
    passengers = data.get('passengers', [])
    travel_class = data.get('travel_class', 'CC')
    requested_seat_ids = data.get('seat_ids') or data.get('requested_seat_ids')
    payment_details = data.get('payment_details')

    if not train_id or not journey_date or not passengers:
        return jsonify({"error": "train_id, journey_date, and passengers are required."}), 400

    result = BookingService.create_booking(
        user_id=session['user_id'],
        train_id=train_id,
        journey_date_str=journey_date,
        passengers=passengers,
        travel_class=travel_class,
        requested_seat_ids=requested_seat_ids,
        payment_details=payment_details
    )

    if not result.get('success'):
        return jsonify({"error": result.get('error')}), 400

    return jsonify(result), 201

@bookings_bp.route('/my', methods=['GET'])
@login_required
def get_my_bookings():
    bookings = BookingService.get_user_bookings(session['user_id'])
    return jsonify({"bookings": bookings})

@bookings_bp.route('/<string:pnr>', methods=['GET'])
def get_booking_details(pnr):
    user_id = session.get('user_id')
    is_admin = session.get('role') == 'ADMIN'
    
    booking = BookingService.get_booking_by_pnr(pnr, user_id=user_id, is_admin=is_admin)
    if not booking:
        return jsonify({"error": "No booking found with this PNR."}), 404
    if isinstance(booking, dict) and 'error' in booking:
        return jsonify({"error": booking['error']}), booking.get('status_code', 400)

    return jsonify({"booking": booking})

@bookings_bp.route('/<string:pnr>/qr', methods=['GET'])
def get_booking_qr(pnr):
    """
    Generates and returns dynamic QR code image for a booking PNR.
    """
    user_id = session.get('user_id')
    is_admin = session.get('role') == 'ADMIN'
    booking = BookingService.get_booking_by_pnr(pnr, user_id=user_id, is_admin=is_admin)
    if not booking:
        return jsonify({"error": "Booking not found."}), 404

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=2
    )
    payload = f"https://railsync.local/verify?pnr={booking['pnr']}&train={booking['train_number']}&date={booking['journey_date']}&status={booking['booking_status']}"
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0f172a", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return Response(buffer.getvalue(), mimetype='image/png')

@bookings_bp.route('/<string:pnr>/cancel', methods=['POST'])
@login_required
def cancel_booking(pnr):
    user_id = session['user_id']
    is_admin = session.get('role') == 'ADMIN'

    result = BookingService.cancel_booking(pnr, user_id=user_id, is_admin=is_admin)
    if not result.get('success'):
        return jsonify({"error": result.get('error')}), 400

    return jsonify(result)

@bookings_bp.route('/<string:pnr>/ticket.pdf', methods=['GET'])
def download_pdf(pnr):
    user_id = session.get('user_id')
    is_admin = session.get('role') == 'ADMIN'

    booking = BookingService.get_booking_by_pnr(pnr, user_id=user_id, is_admin=is_admin)
    if not booking or (isinstance(booking, dict) and 'error' in booking):
        return jsonify({"error": "Booking not found."}), 404

    # Strictly enforce that only the booking owner or an administrator can download the PDF
    if not booking.get('is_owner'):
        return jsonify({"error": "Unauthorized. Only the booking owner or an administrator can download the ticket PDF."}), 403

    passengers = booking.get('passengers', [])
    pdf_bytes = generate_ticket_pdf(booking, passengers)

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"RailSync_Ticket_{pnr}.pdf"
    )
