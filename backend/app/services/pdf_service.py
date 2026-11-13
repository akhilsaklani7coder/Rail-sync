import io
import threading
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Threading Semaphore (max 5 simultaneous CPU-heavy PDF vector renderings)
pdf_render_semaphore = threading.Semaphore(value=5)

def generate_ticket_pdf(booking, passengers):
    """
    Generates an official-style e-Ticket PDF in-memory using ReportLab.
    Includes dynamic passenger manifest, travel class, fare breakdown, and
    an embedded real QR code for digital validation.
    Guarded by a counting semaphore to bound concurrent PDF rendering threads.
    """
    with pdf_render_semaphore:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=32,
            bottomMargin=32
        )
        story = []
        styles = getSampleStyleSheet()

        # Custom typography styles
        title_style = ParagraphStyle(
            'TicketTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#0f172a'),
            alignment=1, # Center
            spaceAfter=2
        )
        subtitle_style = ParagraphStyle(
            'TicketSubtitle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#ea580c'),
            alignment=1,
            spaceAfter=12
        )
        meta_label = ParagraphStyle(
            'TicketMetaLabel',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#64748b')
        )
        bold_val = ParagraphStyle(
            'TicketBoldVal',
            parent=styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#0f172a')
        )
        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#0f172a'),
            spaceBefore=8,
            spaceAfter=4
        )

        # 1. Header Banner
        story.append(Paragraph("RAILSYNC ELECTRONIC RESERVATION SLIP (ERS)", title_style))
        story.append(Paragraph("Indian Railway Reservation Simulation Platform", subtitle_style))

        # 2. QR Code Generation
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=4,
            border=1
        )
        verify_url = f"https://railsync.local/verify?pnr={booking.get('pnr')}&train={booking.get('train_number')}&date={booking.get('journey_date')}"
        qr.add_data(verify_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#0f172a", back_color="white")
        qr_buffer = io.BytesIO()
        img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)
        qr_image = Image(qr_buffer, width=68, height=68)

        # Header Details Table with embedded QR
        header_table_data = [
            [
                Paragraph("<b>PNR NUMBER</b>", meta_label),
                Paragraph(f"<b>{booking.get('pnr')}</b>", bold_val),
                Paragraph("<b>STATUS</b>", meta_label),
                Paragraph(f"<b>{booking.get('booking_status')}</b>", bold_val),
                qr_image
            ],
            [
                Paragraph("<b>TRAIN</b>", meta_label),
                Paragraph(f"{booking.get('train_number')} - {booking.get('train_name')}", bold_val),
                Paragraph("<b>CLASS</b>", meta_label),
                Paragraph(f"<b>{booking.get('travel_class', 'CC')}</b>", bold_val),
                ""
            ],
            [
                Paragraph("<b>FROM</b>", meta_label),
                Paragraph(f"{booking.get('source_station')} ({booking.get('source_code')})", bold_val),
                Paragraph("<b>TO</b>", meta_label),
                Paragraph(f"{booking.get('dest_station')} ({booking.get('dest_code')})", bold_val),
                ""
            ],
            [
                Paragraph("<b>DATE OF JOURNEY</b>", meta_label),
                Paragraph(str(booking.get('journey_date')), bold_val),
                Paragraph("<b>DEPARTURE</b>", meta_label),
                Paragraph(str(booking.get('departure_time')), bold_val),
                ""
            ]
        ]

        t_header = Table(header_table_data, colWidths=[90, 160, 80, 130, 80])
        t_header.setStyle(TableStyle([
            ('SPAN', (4, 0), (4, 3)), # Span QR code over all 4 rows
            ('ALIGN', (4, 0), (4, 3), 'CENTER'),
            ('VALIGN', (4, 0), (4, 3), 'MIDDLE'),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (3,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t_header)
        story.append(Spacer(1, 8))

        # 3. Passenger Details Table
        story.append(Paragraph("PASSENGER DETAILS", section_heading))
        pax_table_data = [
            ["#", "Passenger Name", "Age", "Gender", "Preference", "Coach", "Seat/Berth", "Status"]
        ]
        for idx, p in enumerate(passengers, start=1):
            coach_str = p.get('coach_number') or (p.get('allocated_berth', '').split('-')[0] if '-' in p.get('allocated_berth', '') else '-')
            seat_str = str(p.get('seat_number') or '-')
            berth_str = p.get('allocated_berth') or p.get('berth_type') or 'CONFIRMED'
            status_str = p.get('passenger_status') or 'CONFIRMED'

            pax_table_data.append([
                str(idx),
                p.get('full_name', ''),
                str(p.get('age', '')),
                p.get('gender', ''),
                p.get('berth_preference', 'NO_PREF')[:7],
                coach_str,
                berth_str,
                status_str
            ])

        t_pax = Table(pax_table_data, colWidths=[20, 140, 36, 48, 64, 46, 110, 76])
        t_pax.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 8),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ALIGN', (1,1), (1,-1), 'LEFT'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t_pax)
        story.append(Spacer(1, 8))

        # 4. Fare Summary Table
        story.append(Paragraph("FARE BREAKDOWN & PAYMENT DETAILS", section_heading))
        base_amt = float(booking.get('base_amount') or 0.0)
        res_fee = float(booking.get('reservation_fee') or 0.0)
        sf_fee = float(booking.get('superfast_charge') or 0.0)
        gst = float(booking.get('gst_amount') or 0.0)
        total_fare = float(booking.get('total_amount') or 0.0)

        fare_data = [
            [
                Paragraph("<b>Base Fare:</b>", meta_label), Paragraph(f"INR {base_amt:.2f}", bold_val),
                Paragraph("<b>Reservation Fee:</b>", meta_label), Paragraph(f"INR {res_fee:.2f}", bold_val),
            ],
            [
                Paragraph("<b>Superfast Surcharge:</b>", meta_label), Paragraph(f"INR {sf_fee:.2f}", bold_val),
                Paragraph("<b>GST (5% on AC):</b>", meta_label), Paragraph(f"INR {gst:.2f}", bold_val),
            ],
            [
                Paragraph("<b>Total Amount Paid:</b>", meta_label), Paragraph(f"<b>INR {total_fare:.2f}</b>", bold_val),
                Paragraph("<b>Payment Status:</b>", meta_label), Paragraph(f"<b>{booking.get('payment_status', 'SUCCESS')}</b>", bold_val),
            ]
        ]
        t_fare = Table(fare_data, colWidths=[135, 135, 135, 135])
        t_fare.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(t_fare)
        story.append(Spacer(1, 10))

        # 5. Terms & Instructions
        disclaimer = (
            "<b>Important Travel Instructions:</b><br/>"
            "1. This is a computer-generated simulated Electronic Reservation Slip (ERS).<br/>"
            "2. Passengers must carry an original government-issued photo identity proof during travel.<br/>"
            "3. RAC passengers are allotted sitting accommodation and are promoted to full berths upon cancellations in sequence.<br/>"
            "4. For cancellation rules and refund calculations, visit the RailSync portal."
        )
        story.append(Paragraph(disclaimer, meta_label))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
