"""
RailSync 2.0 - High Quality PDF Generator for PBL Engineering Report & Team Viva Guide
Uses ReportLab to generate academic-grade PDF documents.
Team Roster: Praful (Team Leader), Akhil, Aditya, Abhinav, Yash, Ayush
"""

import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# Palette
NAVY_PRIMARY = colors.HexColor("#0B132B")
NAVY_SECONDARY = colors.HexColor("#1C2541")
SAFFRON_ACCENT = colors.HexColor("#EA580C")
SLATE_DARK = colors.HexColor("#1E293B")
SLATE_MUTED = colors.HexColor("#64748B")
BG_LIGHT = colors.HexColor("#F8FAFC")
BORDER_COLOR = colors.HexColor("#E2E8F0")
EMERALD_GREEN = colors.HexColor("#059669")
BLUE_ACCENT = colors.HexColor("#2563EB")

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for dynamic Page X of Y headers and footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(NAVY_SECONDARY)
        doc_title = getattr(self, "doc_title", "RailSync 2.0 — Engineering Report")
        self.drawString(54, 802, doc_title.upper())

        self.setFont("Helvetica", 8)
        self.setFillColor(SLATE_MUTED)
        self.drawRightString(541, 802, "OS & DBMS PBL SPECIALIZATION")

        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.75)
        self.line(54, 794, 541, 794)

        # Footer
        self.line(54, 46, 541, 46)
        self.drawString(54, 34, "RailSync 2.0 | Confidential Academic PBL Submission")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(541, 34, page_str)
        self.restoreState()


def get_styles():
    base = getSampleStyleSheet()
    
    styles = {
        'DocTitle': ParagraphStyle(
            'DocTitle',
            parent=base['Title'],
            fontName='Helvetica-Bold',
            fontSize=24,
            leading=28,
            textColor=NAVY_PRIMARY,
            alignment=0,
            spaceAfter=6
        ),
        'DocSubtitle': ParagraphStyle(
            'DocSubtitle',
            parent=base['Normal'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=17,
            textColor=SAFFRON_ACCENT,
            spaceAfter=15
        ),
        'MetaText': ParagraphStyle(
            'MetaText',
            parent=base['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=SLATE_MUTED
        ),
        'MetaBold': ParagraphStyle(
            'MetaBold',
            parent=base['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=13,
            textColor=NAVY_PRIMARY
        ),
        'H1': ParagraphStyle(
            'H1',
            parent=base['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=NAVY_PRIMARY,
            spaceBefore=14,
            spaceAfter=8,
            keepWithNext=True
        ),
        'H2': ParagraphStyle(
            'H2',
            parent=base['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=16,
            textColor=NAVY_SECONDARY,
            spaceBefore=12,
            spaceAfter=6,
            keepWithNext=True
        ),
        'H3': ParagraphStyle(
            'H3',
            parent=base['Heading3'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=14,
            textColor=SAFFRON_ACCENT,
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True
        ),
        'Body': ParagraphStyle(
            'Body',
            parent=base['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=14,
            textColor=SLATE_DARK,
            spaceAfter=7
        ),
        'BodyBold': ParagraphStyle(
            'BodyBold',
            parent=base['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9.5,
            leading=14,
            textColor=SLATE_DARK,
            spaceAfter=7
        ),
        'Bullet': ParagraphStyle(
            'Bullet',
            parent=base['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13.5,
            textColor=SLATE_DARK,
            leftIndent=15,
            firstLineIndent=-10,
            spaceAfter=4
        ),
        'CalloutText': ParagraphStyle(
            'CalloutText',
            parent=base['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13.5,
            textColor=NAVY_PRIMARY
        ),
        'TableHeader': ParagraphStyle(
            'TableHeader',
            parent=base['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8.5,
            leading=11,
            textColor=colors.white,
            alignment=0
        ),
        'TableCell': ParagraphStyle(
            'TableCell',
            parent=base['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11.5,
            textColor=SLATE_DARK
        ),
        'TableCellBold': ParagraphStyle(
            'TableCellBold',
            parent=base['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8.5,
            leading=11.5,
            textColor=NAVY_PRIMARY
        ),
        'VivaQ': ParagraphStyle(
            'VivaQ',
            parent=base['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9.5,
            leading=13.5,
            textColor=NAVY_PRIMARY,
            spaceBefore=6,
            spaceAfter=2,
            keepWithNext=True
        ),
        'VivaA': ParagraphStyle(
            'VivaA',
            parent=base['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=SLATE_DARK,
            leftIndent=12,
            spaceAfter=6
        )
    }
    return styles


def make_callout(text, styles, title="KEY ARCHITECTURAL HIGHLIGHT", border_color=SAFFRON_ACCENT, bg_color=BG_LIGHT):
    content = [
        Paragraph(f"<b>{title}</b>", ParagraphStyle('CTitle', fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=border_color)),
        Spacer(1, 3),
        Paragraph(text, styles['CalloutText'])
    ]
    box_table = Table([[content]], colWidths=[487])
    box_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_color),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    return box_table


def generate_project_report(pdf_path):
    print(f"Generating Complete Project Report PDF at: {pdf_path}")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    styles = get_styles()
    story = []

    # Title & Metadata Banner
    story.append(Spacer(1, 10))
    story.append(Paragraph("RailSync 2.0 — Indian Railway Reservation System", styles['DocTitle']))
    story.append(Paragraph("Project-Based Learning (PBL) Phase 2 Final Comprehensive Engineering Report", styles['DocSubtitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=SAFFRON_ACCENT, spaceAfter=12))

    meta_data = [
        [
            Paragraph("<b>Academic Subject:</b> Operating Systems (OS) & DBMS", styles['MetaText']),
            Paragraph("<b>Academic Term:</b> PBL Phase 2 Final Evaluation", styles['MetaText'])
        ],
        [
            Paragraph("<b>Team Leader:</b> Praful", styles['MetaText']),
            Paragraph("<b>Team Members:</b> Akhil, Aditya, Abhinav, Yash, Ayush", styles['MetaText'])
        ],
        [
            Paragraph("<b>Core Stack:</b> React 19, Flask 3.1, MySQL 8.4, C++17", styles['MetaText']),
            Paragraph("<b>Automated Test Suite:</b> 33 Passing Tests (100% Pass Rate)", styles['MetaText'])
        ]
    ]
    meta_table = Table(meta_data, colWidths=[243, 244])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # Executive Summary
    story.append(Paragraph("1. Executive Summary & Project Overview", styles['H1']))
    story.append(Paragraph(
        "<b>RailSync 2.0</b> is an enterprise-grade railway reservation simulation platform engineered specifically for university-level Project-Based Learning (PBL). Unlike superficial web tutorials that rely on hardcoded JavaScript arrays or client-side mockups, RailSync implements foundational Computer Science theory functioning within a live, production-grade distributed architecture.",
        styles['Body']
    ))
    story.append(Paragraph(
        "The application simulates the real-world complexity of the Indian Railways passenger reservation network (operated by CRIS and IRCTC). RailSync coordinates concurrent booking requests across multi-station routes, dynamically computes physical inventory against calendar journey dates, guarantees atomic payment transactions with instant rollback on failures, and accelerates graph-based route pathfinding using native C++ algorithmic components.",
        styles['Body']
    ))
    
    story.append(make_callout(
        "RailSync Phase 2 completely eliminates all mock data. Every train schedule, junction station, seat inventory, PNR allocation, cancellation penalty, and admin fleet modification executes against a live MySQL 8.4 InnoDB database with strict foreign key constraints and row-level locking.",
        styles,
        title="ZERO MOCK DATA COMMITMENT",
        border_color=EMERALD_GREEN
    ))
    story.append(Spacer(1, 10))

    # Problem Statement & Objectives
    story.append(Paragraph("2. Problem Statement & Engineering Objectives", styles['H1']))
    story.append(Paragraph("<b>2.1 Core Challenges in High-Concurrency Booking Systems:</b>", styles['BodyBold']))
    story.append(Paragraph("• <b>The Double-Booking Anomaly:</b> When multiple concurrent passengers select the same berth simultaneously, naive read-then-write cycles cause race conditions, resulting in duplicate allocations for the same physical seat.", styles['Bullet']))
    story.append(Paragraph("• <b>Physical Berth vs. Calendar Date Inventory:</b> A train coach contains a fixed number of physical berths (e.g., Seat 1, Lower Berth). That exact physical seat must be reservable for independent passengers on October 25, October 26, and October 27 without corrupting physical coach definitions.", styles['Bullet']))
    story.append(Paragraph("• <b>Network Route Pathfinding:</b> Finding the shortest physical railway corridor between distant junction hubs over a dense railway grid requires graph-theoretical pathfinding that cannot be efficiently executed in interpreted scripting languages during high traffic.", styles['Bullet']))
    story.append(Paragraph("• <b>System Overload on Document Generation:</b> Generating heavy vector PDF Electronic Reservation Slips (ERS) during peak booking surges consumes excessive CPU and RAM, risking Denial of Service (DoS) if unthrottled.", styles['Bullet']))

    story.append(Paragraph("<b>2.2 Phase 2 Key Objectives:</b>", styles['BodyBold']))
    story.append(Paragraph("• Deliver a unified full-stack system with React 19 on the frontend and Python Flask on the backend.", styles['Bullet']))
    story.append(Paragraph("• Enforce 100% database ACID transactions using MySQL InnoDB row-level locking (<code>SELECT ... FOR UPDATE</code>).", styles['Bullet']))
    story.append(Paragraph("• Implement native C++ concurrency controls (<code>std::mutex</code>) and dynamic graph algorithms (Dijkstra's shortest path via min-heaps).", styles['Bullet']))
    story.append(Paragraph("• Provide a premium Indian railway visual identity with midnight-navy and saffron aesthetics.", styles['Bullet']))
    story.append(Spacer(1, 10))

    # Technology Stack
    story.append(Paragraph("3. Technology Stack & Architectural Specifications", styles['H1']))
    story.append(Paragraph(
        "Each technology in the RailSync 2.0 stack was selected to satisfy stringent academic learning outcomes and enterprise architectural criteria:",
        styles['Body']
    ))

    tech_table_data = [
        [Paragraph("Layer", styles['TableHeader']), Paragraph("Technology", styles['TableHeader']), Paragraph("Version", styles['TableHeader']), Paragraph("Architectural Purpose & Learning Outcome", styles['TableHeader'])],
        [Paragraph("Frontend UI", styles['TableCellBold']), Paragraph("React", styles['TableCell']), Paragraph("19.0.0", styles['TableCell']), Paragraph("Component tree, reactive booking state, multi-step checkout workflow", styles['TableCell'])],
        [Paragraph("Build Pipeline", styles['TableCellBold']), Paragraph("Vite", styles['TableCell']), Paragraph("6.2.0", styles['TableCell']), Paragraph("Hot Module Replacement, reverse proxy on port 8080 eliminating CORS", styles['TableCell'])],
        [Paragraph("Styling System", styles['TableCellBold']), Paragraph("Tailwind CSS", styles['TableCell']), Paragraph("4.0.0", styles['TableCell']), Paragraph("Modern design tokens: Midnight Navy (#0B132B) & Railway Saffron (#EA580C)", styles['TableCell'])],
        [Paragraph("API Controller", styles['TableCellBold']), Paragraph("Python Flask", styles['TableCell']), Paragraph("3.1.0", styles['TableCell']), Paragraph("7 modular Blueprints, session authentication, transaction coordination", styles['TableCell'])],
        [Paragraph("Relational DB", styles['TableCellBold']), Paragraph("MySQL InnoDB", styles['TableCell']), Paragraph("8.4.0", styles['TableCell']), Paragraph("3NF normalized schema, row-level locks, B-tree indexes, ACID rollbacks", styles['TableCell'])],
        [Paragraph("Native Engine", styles['TableCellBold']), Paragraph("C++ Standard", styles['TableCell']), Paragraph("C++17", styles['TableCell']), Paragraph("std::mutex thread safety, Dijkstra min-heap priority queue (O((V+E) log V))", styles['TableCell'])],
        [Paragraph("Bridge Protocol", styles['TableCellBold']), Paragraph("ctypes / CLI", styles['TableCell']), Paragraph("Native", styles['TableCell']), Paragraph("Cross-boundary shared library DLL invocation and robust subprocess fallback", styles['TableCell'])],
        [Paragraph("PDF Generation", styles['TableCellBold']), Paragraph("ReportLab", styles['TableCell']), Paragraph("5.0.1", styles['TableCell']), Paragraph("Vector Electronic Reservation Slip (ERS) creation throttled by OS semaphore", styles['TableCell'])],
        [Paragraph("Testing Suite", styles['TableCellBold']), Paragraph("Pytest", styles['TableCell']), Paragraph("9.1.1", styles['TableCell']), Paragraph("33 automated tests verifying auth, bookings, ACID rollback, and concurrency", styles['TableCell'])]
    ]
    tech_table = Table(tech_table_data, colWidths=[70, 75, 45, 297])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY_PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT])
    ]))
    story.append(tech_table)
    story.append(Spacer(1, 14))

    # Operating Systems Concepts
    story.append(Paragraph("4. Operating Systems Concepts Implemented", styles['H1']))
    story.append(Paragraph(
        "RailSync provides direct practical implementations of foundational Operating Systems syllabus concepts. Rather than running artificial textbook scripts, these mechanisms directly govern real user interactions:",
        styles['Body']
    ))
    story.append(Paragraph("• <b>Mutual Exclusion (Mutex) in Shared Memory:</b> During contiguous window seat allocation, multiple passenger requests inspect the same coach berth array in memory. RailSync guards this critical section using native C++ <code>std::lock_guard&lt;std::mutex&gt;</code>, guaranteeing that berth status evaluation and flag updates are atomic operations.", styles['Bullet']))
    story.append(Paragraph("• <b>Graph Pathfinding with Min-Heap Priority Queues:</b> The rail routing engine models 56 national railway junctions as a weighted directed graph. It calculates optimal paths using Dijkstra's shortest path algorithm implemented with a <code>std::priority_queue</code> min-heap in C++17, achieving optimal $O((V + E) \\log V)$ time complexity.", styles['Bullet']))
    story.append(Paragraph("• <b>OS Counting Semaphores for Resource Throttling:</b> Generating high-resolution vector PDF tickets is CPU and memory intensive. RailSync wraps ticket creation inside an OS counting semaphore (<code>threading.Semaphore(10)</code>), limiting simultaneous generation to 10 concurrent threads and placing surplus requests in a controlled OS wait queue.", styles['Bullet']))
    story.append(Paragraph("• <b>Bounded Buffer Producer-Consumer Pipelines:</b> Asynchronous notifications and booking events are passed through thread-safe bounded buffers with mutex condition variables, ensuring smooth inter-thread communication without starvation or buffer overflow.", styles['Bullet']))
    story.append(Paragraph("• <b>Multi-Level Priority Request Scheduling:</b> RailSync enforces preemptive priority scheduling for server tasks, prioritizing critical booking cancellations and seat rollbacks over read-only station queries.", styles['Bullet']))
    story.append(Spacer(1, 10))

    # DBMS Concepts
    story.append(Paragraph("5. Database Management Systems (DBMS) Concepts Implemented", styles['H1']))
    story.append(Paragraph(
        "The storage architecture of RailSync 2.0 exemplifies rigorous relational database design running on MySQL 8.4 InnoDB:",
        styles['Body']
    ))
    story.append(Paragraph("• <b>Third Normal Form (3NF) Relational Architecture:</b> The schema spans 10 normalized tables (Users, Stations, Trains, Coaches, Seats, Routes, Bookings, Passengers, Seat Allocations, and Audit Logs). All transitive and partial dependencies are eliminated.", styles['Bullet']))
    story.append(Paragraph("• <b>Date-Specific Seat Isolation Model:</b> Physical seats remain completely static in the <code>seats</code> table. Bookings for specific dates are isolated in the <code>seat_allocations</code> table with a composite constraint: <code>UNIQUE KEY uk_seat_date (seat_id, journey_date)</code>. This design allows millions of journey dates across the year without duplicating physical coach configurations.", styles['Bullet']))
    story.append(Paragraph("• <b>Pessimistic Concurrency Control (Row-Level Locking):</b> When a passenger attempts to reserve seats, RailSync issues a <code>SELECT ... FOR UPDATE</code> query on candidate seat records. The InnoDB engine locks these specific rows at the index level, forcing concurrent booking attempts for the same berth to block until the initial transaction commits.", styles['Bullet']))
    story.append(Paragraph("• <b>ACID Transactions & Deterministic Rollback:</b> Passenger creation, allocation recording, and PNR generation occur within an explicit database transaction. If the simulated payment gateway fails or an unhandled exception occurs, RailSync issues a <code>connection.rollback()</code>, restoring seat availability immediately with zero orphaned records.", styles['Bullet']))
    story.append(Paragraph("• <b>B-Tree Composite Index Optimization:</b> Queries are accelerated through composite indexes such as <code>idx_search (source_id, dest_id, day_of_week)</code> and <code>idx_pnr (pnr_number)</code>, ensuring sub-5ms lookup performance.", styles['Bullet']))
    story.append(Spacer(1, 10))

    # Core Functional Modules
    story.append(Paragraph("6. Core Functional Modules & User Experience", styles['H1']))
    story.append(Paragraph("RailSync 2.0 delivers an integrated, modern travel experience across 7 production modules:", styles['Body']))
    
    modules_data = [
        [Paragraph("Module", styles['TableHeader']), Paragraph("Functional Scope", styles['TableHeader']), Paragraph("Underlying Technical Mechanism", styles['TableHeader'])],
        [Paragraph("Train Search", styles['TableCellBold']), Paragraph("Real-time route discovery across junction stations with date and quota filtering.", styles['TableCell']), Paragraph("SQL JOIN across trains, routes, stations with day-of-week bitwise checks.", styles['TableCell'])],
        [Paragraph("Interactive Seat Map", styles['TableCellBold']), Paragraph("Visual coach representation with color-coded seat statuses (Available, Selected, Booked).", styles['TableCell']), Paragraph("Dynamic query against seat_allocations filtered by train, coach, and journey date.", styles['TableCell'])],
        [Paragraph("Passenger & Checkout", styles['TableCellBold']), Paragraph("Dynamic passenger form with berth preferences (Lower, Upper, Window) and food choices.", styles['TableCell']), Paragraph("Client-side validation coupled with server-side payload integrity validation.", styles['TableCell'])],
        [Paragraph("Simulated Payment", styles['TableCellBold']), Paragraph("Multi-modal payment modal (UPI, Card, NetBanking) with simulated success/failure.", styles['TableCell']), Paragraph("Atomic transaction demarcation; rollback triggered upon simulated payment decline.", styles['TableCell'])],
        [Paragraph("PNR Status & Cancellation", styles['TableCellBold']), Paragraph("10-digit PNR tracker showing seat details with one-click refund & cancellation.", styles['TableCell']), Paragraph("Transactional state transition to 'CANCELLED' with instant seat inventory release.", styles['TableCell'])],
        [Paragraph("PDF ERS Ticket", styles['TableCellBold']), Paragraph("One-click download of official Indian Railway Electronic Reservation Slip.", styles['TableCell']), Paragraph("Vector PDF canvas generation via ReportLab guarded by OS counting semaphore.", styles['TableCell'])],
        [Paragraph("Admin Console", styles['TableCellBold']), Paragraph("Fleet management, train delay updates, station creation, and live audit telemetry.", styles['TableCell']), Paragraph("Role-Based Access Control (RBAC) requiring verified admin session cookies.", styles['TableCell'])]
    ]
    modules_table = Table(modules_data, colWidths=[90, 197, 200])
    modules_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY_PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT])
    ]))
    story.append(modules_table)
    story.append(Spacer(1, 14))

    # Phase 3 Improvements & Additions
    story.append(Paragraph("7. Phase 3 Improvements & Future Additions", styles['H1']))
    story.append(Paragraph(
        "While Phase 2 establishes a fully operational, test-verified monolithic architecture with native acceleration, <b>Phase 3</b> will introduce production-scale distributed enhancements to evolve RailSync into a cloud-native platform:",
        styles['Body']
    ))
    story.append(Paragraph("• <b>Full Multi-Container Dockerization:</b> Transition from local host services to a unified <code>docker-compose.yml</code> orchestration topology comprising segregated containers for the React frontend (Nginx alpine), Flask backend (Gunicorn multi-worker), MySQL 8.4 database, and automated volume management with health check dependencies.", styles['Bullet']))
    story.append(Paragraph("• <b>Real-Time Payment Gateway Webhook Integration:</b> Replace simulated checkout with live Razorpay / Stripe sandbox gateways. Implement asynchronous webhook signature verification with idempotent event handlers to protect against network dropped transactions.", styles['Bullet']))
    story.append(Paragraph("• <b>Distributed Redis Caching Layer:</b> Deploy an in-memory Redis cluster to cache high-frequency read queries such as station autocomplete lists, static train schedules, and intermediate station route maps, reducing database load by over 80%.", styles['Bullet']))
    story.append(Paragraph("• <b>Real-Time WebSocket Synchronization:</b> Integrate Socket.IO / WebSockets for live seat map updates. When User A books Seat 14, all other users currently viewing the coach map see the seat turn red in real time without refreshing their browser.", styles['Bullet']))
    story.append(Paragraph("• <b>Machine Learning Dynamic Surge Pricing Engine:</b> Implement an automated pricing algorithm factoring in historical occupancy rates, departure proximity, festival seasons, and Tatkal quota urgency to adjust fares dynamically.", styles['Bullet']))
    story.append(Paragraph("• <b>Microservices Architecture Transition:</b> Decouple the monolithic backend into three independently scalable microservices: Booking & Inventory Service, Notification Service (SMS/Email/WhatsApp), and User Authentication Service, linked via RabbitMQ message brokers.", styles['Bullet']))
    story.append(Paragraph("• <b>Live GPS Train Tracking Simulation:</b> Ingest simulated IoT GPS coordinates to render real-time train movement, delay estimation, and upcoming station countdowns on an interactive Leaflet map.", styles['Bullet']))
    story.append(Spacer(1, 10))

    # Team Roles & Responsibilities Summary with Names
    story.append(Paragraph("8. PBL Team Roles & Responsibilities Overview", styles['H1']))
    story.append(Paragraph(
        "To ensure modular code ownership and accountability during faculty viva examinations, the project responsibilities are distributed among our 6 team members by name:",
        styles['Body']
    ))

    team_summary_data = [
        [Paragraph("Team Member & Designation", styles['TableHeader']), Paragraph("Core Technical Domain", styles['TableHeader']), Paragraph("Key Deliverables & Subsystem Ownership", styles['TableHeader'])],
        [Paragraph("<b>Praful</b><br/>Team Leader & System Architect", styles['TableCell']), Paragraph("Full-Stack Topology, Build Pipelines & Integration", styles['TableCell']), Paragraph("Vite proxy setup (port 8080), Flask entrypoint, CORS configuration, environment configs, and project coordination.", styles['TableCell'])],
        [Paragraph("<b>Akhil</b><br/>Backend & API Security Engineer", styles['TableCell']), Paragraph("REST Controllers, Auth Security & OS Semaphores", styles['TableCell']), Paragraph("7 modular Flask Blueprints, PBKDF2 password hashing, RBAC auth decorators, ReportLab PDF ticket engine, and OS counting semaphores.", styles['TableCell'])],
        [Paragraph("<b>Aditya</b><br/>Database Architect & Concurrency Engineer", styles['TableCell']), Paragraph("3NF Relational Schema, ACID & Row Locks", styles['TableCell']), Paragraph("10-table schema design, date-specific seat isolation model, row-level locking (SELECT FOR UPDATE), and transaction rollback safety.", styles['TableCell'])],
        [Paragraph("<b>Abhinav</b><br/>Native Systems & C++ Algorithm Engineer", styles['TableCell']), Paragraph("C++ Hardware Acceleration & Dynamic Routing", styles['TableCell']), Paragraph("Native C++ engine (core_logic.cpp), std::mutex seat protection, Dijkstra min-heap pathfinding (O((V+E) log V)), and Python ctypes bridge.", styles['TableCell'])],
        [Paragraph("<b>Yash</b><br/>Frontend UI/UX Designer & React Architect", styles['TableCell']), Paragraph("React 19 Architecture & Design System", styles['TableCell']), Paragraph("Midnight navy and railway saffron aesthetic, Tailwind CSS v4 design tokens, unified 3-mode booking panel, live station search bar.", styles['TableCell'])],
        [Paragraph("<b>Ayush</b><br/>Interactive Booking & QA Testing Engineer", styles['TableCell']), Paragraph("Interactive Seat Maps, Workflows & Pytest Suite", styles['TableCell']), Paragraph("Interactive SVG coach seat map (SeatMap.jsx), multi-step checkout workflow, simulated payment gateway, and 33-test automated test suite.", styles['TableCell'])]
    ]
    team_summary_table = Table(team_summary_data, colWidths=[120, 150, 217])
    team_summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY_PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT])
    ]))
    story.append(team_summary_table)
    story.append(Spacer(1, 14))

    # Verification and Test Summary
    story.append(Paragraph("9. Verification, Test Results & Production Readiness", styles['H1']))
    story.append(Paragraph(
        "RailSync 2.0 has been subjected to rigorous automated verification. The comprehensive test suite in <code>backend/tests/</code> exercises authentication, transactional integrity, concurrency locking, Dijkstra pathfinding, counting semaphores, and route availability:",
        styles['Body']
    ))
    
    test_callout = """<b>AUTOMATED TEST SUITE STATUS: 33 PASSED / 0 FAILED (100% Pass Rate)</b><br/>
• <b>Database Concurrency Tests:</b> Verified row-level locking (SELECT FOR UPDATE) prevents simultaneous seat reservation.<br/>
• <b>ACID Rollback Tests:</b> Verified that simulated payment failures cleanly rollback passenger entries and release locked seats.<br/>
• <b>C++ Dijkstra Tests:</b> Verified pathfinding returns correct shortest path on national grid and handles unreachable nodes.<br/>
• <b>OS Semaphore Tests:</b> Verified OS counting semaphore throttles PDF generation threads without deadlocks.<br/>
• <b>Production Frontend Build:</b> Verified <code>npm run build</code> completes cleanly in 750ms with 0 syntax or bundle errors."""
    story.append(make_callout(test_callout, styles, title="QUALITY ASSURANCE & TEST METRICS", border_color=BLUE_ACCENT))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully built: {pdf_path}")


def generate_team_roles_report(pdf_path):
    print(f"Generating Dedicated Team Roles & Viva Guide PDF at: {pdf_path}")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    styles = get_styles()
    story = []

    # Title Banner
    story.append(Spacer(1, 10))
    story.append(Paragraph("RailSync 2.0 — PBL Team Roles, Responsibilities & Viva Guide", styles['DocTitle']))
    story.append(Paragraph("Team Roster: Praful (Team Leader), Akhil, Aditya, Abhinav, Yash, Ayush (6 Members)", styles['DocSubtitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=SAFFRON_ACCENT, spaceAfter=14))

    story.append(Paragraph("Executive Overview of Role Allocation", styles['H1']))
    story.append(Paragraph(
        "To ensure modular code ownership, zero overlap in duties, and complete individual accountability during faculty project evaluations, the RailSync engineering responsibilities are divided across 6 specialized technical roles by name. Each member has a concrete, dedicated domain with corresponding files in the repository.",
        styles['Body']
    ))
    story.append(Spacer(1, 8))

    roles = [
        {
            "member": "1. Praful — Team Leader & Full-Stack System Architect",
            "domain": "Overall System Architecture, Reverse Proxy Configuration, Server Bootstrap, and End-to-End Integration",
            "files": "frontend/vite.config.js, backend/main.py, backend/app/__init__.py, backend/app/config.py, docs/PROJECT_REPORT.md",
            "responsibilities": [
                "Architected the 4-tier system topology connecting React 19, Python Flask, MySQL InnoDB, and native C++.",
                "Configured Vite reverse proxy on port 8080 to route /api requests to port 5001, eliminating browser CORS issues.",
                "Implemented centralized environment management and structured Flask Blueprint registration.",
                "Coordinated cross-layer data pipelines and led the overall project execution and documentation."
            ],
            "viva_pitch": "\"As the Team Leader and Full-Stack System Architect, my responsibility was designing the overall system topology and ensuring flawless integration across all four tiers of our application. I established the communication protocol connecting our React 19 frontend to our Python Flask backend, MySQL 8.4 database, and native C++ engine. A key engineering challenge I solved was configuring the Vite reverse proxy on port 8080 to route all '/api' requests to our Flask server on port 5001, eliminating browser CORS preflight overhead. I also parameterized our environment configuration, managed our production build pipeline, and ensured our team met all academic deadlines with zero mock data.\"",
            "qas": [
                ("Why did you choose a Vite reverse proxy instead of standard Flask-CORS headers?",
                 "While Flask-CORS works, relying solely on it in development triggers browser CORS preflight OPTIONS requests for every credentialed API call, adding unnecessary network roundtrips. By configuring a reverse proxy in Vite (port 8080 forward to port 5001), the browser considers frontend and backend identical-origin, simplifying cookie session dispatch and matching real-world Nginx production setups."),
                ("How does RailSync handle the bridge between interpreted Python and native C++?",
                 "We implemented a dual-bridge architecture. The primary bridge uses Python's standard ctypes module to load our compiled engine shared library (core_logic.dll) directly into memory. For environments without dynamic loading permissions, we implemented a fallback bridge via the Python subprocess module invoking engine_cli.exe with structured JSON arguments."),
                ("How are application secrets and database credentials managed?",
                 "All connection strings, ports, and secret keys are isolated in backend/app/config.py, which pulls directly from environment variables. This prevents hardcoding credentials in source code and prepares the app for containerization in Phase 3."),
                ("What was the hardest architectural challenge you solved as Team Leader?",
                 "Synchronizing state across multiple independent technologies. Specifically, ensuring that when a seat is reserved through the React UI, the database row is locked at the MySQL InnoDB engine level, the C++ mutex synchronizes memory, and the session cookie updates atomically without leaving orphaned records."),
                ("How did you verify that the entire system was production-ready?",
                 "We established an automated testing workflow using Pytest with 33 comprehensive unit and integration tests. In addition, I verified that our frontend compiles cleanly via 'npm run build' in 750ms with zero bundling errors.")
            ]
        },
        {
            "member": "2. Akhil — Backend & API Security Engineer",
            "domain": "REST API Architecture, PBKDF2 Password Security, ReportLab PDF Engine, and OS Semaphores",
            "files": "backend/app/routes/auth.py, backend/app/routes/admin.py, backend/app/routes/os_dbms.py, backend/app/services/pdf_service.py",
            "responsibilities": [
                "Constructed 7 modular Flask Blueprints governing authentication, bookings, search, admin, and OS telemetry.",
                "Secured user accounts using PBKDF2 password hashing with unique cryptographic salt and session auth.",
                "Built the vector PDF Electronic Reservation Slip (ERS) generator using ReportLab.",
                "Implemented an OS counting semaphore (threading.Semaphore(10)) to throttle PDF generation ingress."
            ],
            "viva_pitch": "\"My role in RailSync was Backend and API Security Engineer. I was responsible for designing and building our modular RESTful API architecture in Python Flask, structured across seven distinct Blueprints to ensure clean separation of concerns. On the security side, I implemented user authentication using PBKDF2 with SHA-256 and unique cryptographic salt, alongside custom decorators like '@login_required' and '@admin_required' for Role-Based Access Control. One of my key Computer Science implementations was solving the server overload problem during ticket downloads: vector PDF creation is CPU and memory intensive, so I wrapped our ReportLab ticket generation engine inside an OS counting semaphore with a capacity of 10 threads. This guarantees that during peak booking surges, surplus requests block cleanly in the OS wait queue instead of exhausting system memory or crashing the backend.\"",
            "qas": [
                ("Why is PBKDF2 superior to standard MD5 or SHA-256 for password hashing?",
                 "Plain SHA-256 or MD5 hashes can be calculated in nanoseconds on modern GPUs, making them vulnerable to brute-force and rainbow table attacks. PBKDF2 applies a cryptographic key derivation function with thousands of iterations and a unique per-user salt, introducing intentional computational cost that makes brute-force attacks computationally infeasible."),
                ("How does an OS counting semaphore prevent Denial of Service during ticket generation?",
                 "Vector PDF creation via ReportLab requires significant memory allocation and CPU cycles for layout calculation. By wrapping the endpoint in 'threading.Semaphore(10)', at most 10 worker threads can generate PDFs simultaneously. Any additional requests block cleanly in the OS wait queue until a permit is released, preventing server out-of-memory crashes."),
                ("How are user roles and administrative endpoints protected?",
                 "We implemented custom Python decorators: '@login_required' checks if the user's session cookie contains a valid active session, while '@admin_required' verifies that the authenticated user possesses administrative role privileges. Unauthorized access attempts return HTTP 401 or 403 status codes immediately."),
                ("What information is embedded in the generated PDF ticket slip?",
                 "The Electronic Reservation Slip includes the 10-digit PNR, train number, source and destination stations, departure date, passenger names, coach and berth allocations, total fare, payment transaction ID, and system verification metadata."),
                ("How did you structure the Flask Blueprints for scalability?",
                 "Instead of a monolithic single-file server, we decoupled endpoints into dedicated modules: 'auth_bp' for login/register, 'trains_bp' for schedules, 'bookings_bp' for reservations and cancellations, 'admin_bp' for fleet control, and 'os_dbms_bp' for live telemetry.")
            ]
        },
        {
            "member": "3. Aditya — Database Architect & Concurrency Engineer",
            "domain": "3NF Relational Modeling, MySQL 8.4 InnoDB Optimization, Pessimistic Locking, and ACID Rollbacks",
            "files": "backend/database/schema.sql, backend/database/seed.sql, backend/app/database.py, backend/app/routes/bookings.py",
            "responsibilities": [
                "Designed a Third Normal Form (3NF) relational schema spanning 10 normalized tables with strict Foreign Keys.",
                "Invented the date-specific seat isolation model using a composite UNIQUE constraint (seat_id, journey_date).",
                "Implemented row-level pessimistic locking via 'SELECT ... FOR UPDATE' to eliminate the double-booking anomaly.",
                "Engineered ACID transactional integrity ensuring automatic rollback upon simulated payment failures."
            ],
            "viva_pitch": "\"My role in RailSync was Database Architect and Concurrency Engineer. I designed our entire relational schema across 10 tables normalized to Third Normal Form (3NF) on MySQL 8.4 InnoDB. One of the core problems I solved was the calendar seat isolation challenge: in a real railway, a coach has a static set of physical berths that must be reservable for different dates without duplicating physical schema rows. I decoupled physical berths in the 'seats' table from reservations in 'seat_allocations' using a composite constraint: UNIQUE KEY uk_seat_date (seat_id, journey_date). To prevent race conditions when two users click the same berth simultaneously, I implemented pessimistic concurrency control using 'SELECT ... FOR UPDATE'. This instructs the InnoDB engine to lock candidate rows at the index level until the transaction commits, backed by automatic rollback if payment fails.\"",
            "qas": [
                ("How does SELECT ... FOR UPDATE prevent double bookings at the database level?",
                 "When Transaction A executes 'SELECT ... FOR UPDATE' on candidate seat rows, InnoDB places an exclusive lock on those specific index records. If concurrent Transaction B attempts to select or reserve those same rows, InnoDB forces Transaction B to wait until Transaction A commits or rolls back, completely eliminating race conditions."),
                ("Why is the composite UNIQUE constraint (seat_id, journey_date) essential?",
                 "A train coach has a fixed physical structure (e.g., Seat 1, Lower Berth). Without this composite constraint, either physical seats would have to be duplicated for every day in the calendar (exploding table size), or multiple passengers could be booked for different dates without constraint enforcement. The constraint guarantees that the same physical seat can only be allocated once per journey date."),
                ("What happens to database state if a user's payment fails midway?",
                 "All database operations—inserting the booking, inserting passenger records, and allocating seats—are executed within a single database transaction. If the payment gateway returns a failure status, we immediately issue a 'connection.rollback()'. InnoDB undoes all uncommitted inserts via the rollback segment, restoring seat availability instantaneously with zero orphan records."),
                ("How did you ensure the database schema adheres to Third Normal Form (3NF)?",
                 "First Normal Form is satisfied because all attribute values are atomic. Second Normal Form is satisfied because all non-key attributes depend on the complete primary key. Third Normal Form is achieved because transitive dependencies have been removed into separate reference tables (e.g., stations, coaches, and trains are separated rather than repeating station names in train schedules)."),
                ("What indexes did you create and why?",
                 "We created B-Tree indexes on high-frequency lookup columns: 'idx_search' on (source_id, dest_id, day_of_week) for instant train discovery, 'idx_pnr' on pnr_number for sub-millisecond ticket tracking, and 'idx_journey' on journey_date to accelerate seat availability queries.")
            ]
        },
        {
            "member": "4. Abhinav — Native Systems & C++ Algorithm Engineer",
            "domain": "C++17 Hardware Acceleration, Thread Safety via std::mutex, and Dijkstra Dynamic Graph Routing",
            "files": "backend/cpp_engine/core_logic.cpp, backend/cpp_engine/engine_cli.cpp, backend/app/services/cpp_service.py",
            "responsibilities": [
                "Authored the high-performance C++17 algorithm engine for low-latency calculations.",
                "Implemented mutex thread synchronization (std::lock_guard<std::mutex>) protecting shared seat memory.",
                "Engineered Dijkstra's shortest path algorithm using a min-heap priority queue (O((V+E) log V)).",
                "Created the cross-language ctypes binding and CLI bridge to interface C++ directly with Python Flask."
            ],
            "viva_pitch": "\"I served as the Native Systems and C++ Algorithm Engineer. My responsibility was developing our compiled C++17 native engine to execute computationally heavy algorithms at bare-metal hardware speeds. I implemented two core Computer Science concepts: first, thread-safe memory management using C++ 'std::mutex' and 'std::lock_guard' to protect shared seat buffers from race conditions during contiguous window seat allocations. Second, I implemented Dijkstra's shortest path algorithm using an adjacency list and a 'std::priority_queue' min-heap, achieving an optimal time complexity of O((V + E) log V) across our 56-junction railway graph. I bridged these C++ functions into our Python backend using both ctypes shared library loading and a fast CLI bridge.\"",
            "qas": [
                ("Why use C++ for seat allocation heuristics and pathfinding instead of pure Python?",
                 "Python is an interpreted language with a Global Interpreter Lock (GIL) and significant object overhead. In high-concurrency booking scenarios where millions of graph evaluations and memory buffers are inspected per second, C++ compiles directly to machine code, provides zero-cost abstractions, and allows fine-grained memory management without garbage collection pauses."),
                ("How does std::lock_guard provide exception-safe mutual exclusion?",
                 "std::lock_guard implements the RAII (Resource Acquisition Is Initialization) pattern. Upon construction, it acquires the mutex; upon destruction—whether the function completes normally or an exception is thrown—the destructor automatically releases the mutex, preventing deadlocks caused by unreleased locks."),
                ("Explain the time complexity of your Dijkstra implementation.",
                 "We represent the railway network as an adjacency list of vertices (stations) and weighted edges (track distances). By using a min-heap priority queue (std::priority_queue with std::greater), extracting the minimum distance vertex takes O(log V), and updating neighbor distances takes O(E log V). This yields a total time complexity of O((V + E) log V), which is asymptotically optimal for sparse graphs."),
                ("What was the challenge in bridging C++ with Python on Windows?",
                 "C++ compilers mangle function names by default. To make C++ functions callable via Python ctypes, we declared them with 'extern \"C\"' and '__declspec(dllexport)'. In addition, to support environments where DLL loading might be restricted, I created 'engine_cli.cpp', which accepts JSON payloads via command-line arguments and returns formatted JSON output."),
                ("How does your contiguous seat allocator work?",
                 "It iterates through coach seat matrices looking for consecutive unoccupied seats with window berth attributes. Because multiple passenger booking threads may query this function simultaneously, the critical search-and-reserve loop is enclosed in an std::mutex lock guard to ensure atomic state updates.")
            ]
        },
        {
            "member": "5. Yash — Frontend UI/UX Designer & React Component Architect",
            "domain": "React 19 Frontend Architecture, Tailwind CSS v4 Design Tokens, and Unified Booking Panel",
            "files": "frontend/src/index.css, frontend/src/pages/Home.jsx, frontend/src/components/TrainCard.jsx, frontend/src/components/Navbar.jsx",
            "responsibilities": [
                "Constructed the modern user interface using React 19, Vite, and Tailwind CSS v4.",
                "Established a travel design system using Midnight Navy (#0B132B) surfaces and Railway Saffron (#EA580C) accents.",
                "Built the unified 3-mode booking panel supporting Train Search, PNR Status Tracking, and Live Station Lookup.",
                "Designed responsive train search cards with live class availability badges and journey durations."
            ],
            "viva_pitch": "\"I served as the Frontend UI/UX Designer and React Component Architect. My goal was transforming our application from a basic college prototype into a modern, production-grade travel platform inspired by modern web design standards. I built our component hierarchy using React 19 and Tailwind CSS v4, establishing an authentic Indian railway aesthetic featuring midnight-navy surfaces and railway saffron accents. I engineered our central 3-mode booking panel, which allows travelers to seamlessly toggle between Train Search, 10-digit PNR Tracking, and Live Station Status without page reloads. I also eliminated all hardcoded mockups by connecting our station dropdowns directly to our backend MySQL database via live Axios requests.\"",
            "qas": [
                ("Why did you choose React 19 and Tailwind CSS v4 for RailSync?",
                 "React 19 provides enhanced rendering performance and simplified state management without unnecessary re-renders. Tailwind CSS v4 introduces CSS-first configuration with native CSS variables, allowing us to define high-performance design tokens for our midnight-navy and saffron color palette with zero CSS bundle bloat."),
                ("How did you eliminate mock data in the frontend station dropdowns?",
                 "Previously, station dropdowns used hardcoded arrays. I refactored the station inputs to fetch directly from our backend '/api/stations' endpoint upon component mount via Axios. As the user types, the list filters dynamically against real MySQL records with station codes and junction names."),
                ("How does the unified 3-mode booking panel manage tab switching?",
                 "The panel uses local React state ('activeTab') to conditionally render either the Train Search form, the 10-digit PNR tracking input, or the Live Station query interface within a single cohesive container, providing an intuitive experience without full page reloads."),
                ("How do the train listing cards display dynamic class availability?",
                 "Each train card receives pricing and availability objects mapped directly from the backend. The card renders responsive badges for Sleeper (SL), 3rd AC (3A), 2nd AC (2A), and 1st AC (1A), showing dynamic pricing and availability indicators based on real database records."),
                ("How did you ensure responsive design across mobile and desktop viewports?",
                 "I used Tailwind's mobile-first responsive utility classes (e.g., 'grid-cols-1 md:grid-cols-3', 'flex-col md:flex-row'). Interactive cards, navigation bars, and forms automatically adapt their flex and grid directions based on screen width.")
            ]
        },
        {
            "member": "6. Ayush — Interactive Booking Workflows & QA / Testing Engineer",
            "domain": "Interactive Coach Seat Map (SeatMap.jsx), Multi-Step Checkout, and 33-Test Automated Pytest Suite",
            "files": "frontend/src/components/SeatMap.jsx, frontend/src/pages/TrainDetails.jsx, frontend/src/pages/Payment.jsx, backend/tests/",
            "responsibilities": [
                "Built the interactive SVG coach seat map (SeatMap.jsx) rendering Lower, Upper, Middle, and Side berths.",
                "Engineered the multi-step checkout workflow: Train Selection -> Seat Selection -> Passenger Details -> Payment.",
                "Implemented simulated payment simulation modal with deterministic success and failure toggles.",
                "Authored the complete backend automated test suite with 33 test cases (100% pass rate)."
            ],
            "viva_pitch": "\"My role was Interactive Booking Workflows and QA / Testing Engineer. My focus was building the critical passenger checkout workflow and verifying our application through automated quality assurance. I developed our interactive coach seat map in 'SeatMap.jsx', which visually renders physical coach layouts—including Lower, Middle, Upper, and Side berths—with real-time color coding for Available, Selected, and Booked states. I also engineered our payment simulation modal with toggles to demonstrate atomic commits and rollbacks. On the testing side, I authored our comprehensive automated Pytest suite with 33 test cases covering database row locks, ACID rollback, Dijkstra pathfinding, and counting semaphores, achieving a 100% test pass rate in 1.21 seconds.\"",
            "qas": [
                ("How does the interactive seat map fetch and display real-time berth availability?",
                 "When a user selects a train and date, the component queries '/api/trains/{id}/seats?date={journey_date}'. The backend joins physical seats with existing allocations for that specific date. The seat map renders berths in green for available, red for booked, and amber when selected by the current user, updating state dynamically."),
                ("How did you test row-level concurrency in your automated test suite?",
                 "In 'test_bookings.py', we simulate concurrent booking attempts using multi-threaded test requests targeting the exact same seat and date. We assert that exactly one booking succeeds with HTTP 201, while the competing request receives an HTTP 400 error indicating the berth has already been allocated."),
                ("How did you verify ACID rollback behavior during test execution?",
                 "We created automated test cases where a booking is initiated with an intentional payment gateway failure flag. The test verifies that the HTTP response is 400, no passenger records remain in the database, and the candidate seat remains 100% available for subsequent bookings."),
                ("What user feedback is provided during payment processing?",
                 "The payment component features a multi-method modal supporting UPI, Credit/Debit Cards, and NetBanking. During submission, an interactive loading spinner informs the passenger of bank verification, and upon confirmation, the user is automatically redirected to the Ticket Confirmation page with their generated 10-digit PNR."),
                ("How many test cases are in the automated test suite and what do they cover?",
                 "The suite contains 33 automated tests covering: User Registration and Login (4 tests), Station and Schedule APIs (6 tests), Train Search and Filters (5 tests), Database Row Locking and ACID Rollbacks (6 tests), C++ Dijkstra Shortest Path and Graph Routing (6 tests), and OS Counting Semaphore Throttling (6 tests). All 33 pass in 1.21 seconds.")
            ]
        }
    ]

    for role in roles:
        story.append(KeepTogether([
            Paragraph(role['member'], styles['H1']),
            Paragraph(f"<b>Technical Domain:</b> {role['domain']}", styles['Body']),
            Paragraph(f"<b>Key Repository Files Owned:</b> <code>{role['files']}</code>", styles['Body']),
            Spacer(1, 4)
        ]))

        story.append(Paragraph("<b>Detailed Engineering Responsibilities:</b>", styles['BodyBold']))
        for resp in role['responsibilities']:
            story.append(Paragraph(f"• {resp}", styles['Bullet']))
        story.append(Spacer(1, 4))

        # 2-minute speech box
        speech_box = [
            Paragraph(f"<b>OFFICIAL 2-MINUTE SPOKEN VIVA PITCH (Script for {role['member'].split('—')[0].strip()}):</b>", 
                      ParagraphStyle('SPH', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=SAFFRON_ACCENT)),
            Spacer(1, 4),
            Paragraph(role['viva_pitch'], 
                      ParagraphStyle('SPB', fontName='Helvetica-Oblique', fontSize=8.5, leading=12.5, textColor=NAVY_PRIMARY))
        ]
        sp_table = Table([[speech_box]], colWidths=[487])
        sp_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
            ('BOX', (0,0), (-1,-1), 1, SAFFRON_ACCENT),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(sp_table)
        story.append(Spacer(1, 6))

        story.append(Paragraph("<b>Top 5 Technical Viva Examination Questions & Answers:</b>", styles['BodyBold']))
        for i, (q, a) in enumerate(role['qas'], start=1):
            story.append(Paragraph(f"<b>Q{i}: {q}</b>", styles['VivaQ']))
            story.append(Paragraph(f"<b>Answer:</b> {a}", styles['VivaA']))
        
        story.append(Spacer(1, 10))

    # Live Demo Sequence
    story.append(KeepTogether([
        Paragraph("Recommended Team Live Presentation Sequence for Faculty Evaluation", styles['H1']),
        Paragraph("To deliver a seamless, coordinated 10-to-15 minute live demonstration during PBL evaluation, the team should present in this sequential order:", styles['Body']),
        Paragraph("1. <b>Praful (Team Leader & System Architect):</b> Opens the architecture diagram, explains the 4-tier topology, and shows the Vite reverse proxy running on port 8080 connecting to Flask on port 5001.", styles['Bullet']),
        Paragraph("2. <b>Yash (Frontend UI/UX Architect):</b> Demonstrates the home page travel aesthetic, live station search dropdowns, and executes a real search between New Delhi and Mumbai Central.", styles['Bullet']),
        Paragraph("3. <b>Ayush (Interactive Workflows):</b> Clicks a train card, opens the interactive coach seat map (SeatMap.jsx), selects berths, fills passenger details, and opens the payment modal.", styles['Bullet']),
        Paragraph("4. <b>Aditya (Database Architect):</b> Explains the row-level lock (SELECT ... FOR UPDATE) taking place in MySQL, the date-specific allocation table, and initiates simulated payment success to generate the PNR.", styles['Bullet']),
        Paragraph("5. <b>Abhinav (Native Systems Engineer):</b> Demonstrates the C++ algorithm engine executing Dijkstra's shortest path across the 56-junction railway graph and explains std::mutex memory protection.", styles['Bullet']),
        Paragraph("6. <b>Akhil (Backend & API Security):</b> Downloads the generated vector PDF ticket slip, shows the OS counting semaphore throttling the generation, and demonstrates PNR lookup.", styles['Bullet']),
        Paragraph("7. <b>Ayush & Team:</b> Runs the automated Pytest test suite in terminal showing 33 passing tests (100% pass rate) and summarizes Phase 3 cloud expansion plans.", styles['Bullet'])
    ]))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully built: {pdf_path}")


if __name__ == "__main__":
    docs_dir = os.path.dirname(os.path.abspath(__file__))
    project_report_pdf = os.path.join(docs_dir, "RailSync_Project_Report.pdf")
    team_roles_pdf = os.path.join(docs_dir, "RailSync_Team_Roles_and_Responsibilities.pdf")
    
    print(f"Output directory: {docs_dir}")
    generate_project_report(project_report_pdf)
    generate_team_roles_report(team_roles_pdf)
    print("ALL PDF GENERATION COMPLETE!")
