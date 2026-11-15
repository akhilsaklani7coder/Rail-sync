"""
Script to generate the official academic RailSync Project & Team Specification PDF
using ReportLab.
"""
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
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
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (Pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "RailSync — Academic Project Specification & Team Task Distribution")
            self.drawRightString(letter[0] - 54, letter[1] - 36, "PBL: OS & DBMS (2026)")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)
            
        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 30, footer_text)
        self.drawString(54, 30, "Confidential — Submitted for College PBL Academic Assessment | GitHub: akhilsaklani7coder/Rail-sync")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 40, letter[0] - 54, 40)
        
        self.restoreState()

def build_pdf():
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    pdf_path = os.path.join(out_dir, "RailSync_Project_Specification_and_Team_Task_Division.pdf")
    
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#0F172A")    # Slate 900
    c_saffron = colors.HexColor("#EA580C")    # Saffron Orange 600
    c_blue = colors.HexColor("#2563EB")       # Blue 600
    c_teal = colors.HexColor("#0D9488")       # Teal 600
    c_text = colors.HexColor("#334155")       # Slate 700
    c_light = colors.HexColor("#F8FAFC")      # Slate 50
    c_border = colors.HexColor("#E2E8F0")     # Slate 200
    
    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=c_primary,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=c_saffron,
        spaceAfter=14
    )
    
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=c_saffron,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_text,
        spaceAfter=6
    )
    
    bold_body = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3
    )
    
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_text
    )
    
    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.white
    )
    
    story = []
    
    # =========================================================================
    # HEADER BANNER & PROJECT TITLE
    # =========================================================================
    story.append(Paragraph("RAILSYNC — PROJECT ARCHITECTURE & TEAM SPECIFICATION", title_style))
    story.append(Paragraph("Academic Capstone Project-Based Learning (PBL) | Operating Systems & Database Management Systems", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_saffron, spaceBefore=0, spaceAfter=12))
    
    # Metadata Box Table
    meta_data = [
        [
            Paragraph("<b>Academic Year:</b> 2026<br/><b>Evaluation:</b> OS & DBMS PBL Course", table_cell),
            Paragraph("<b>Repository:</b> github.com/akhilsaklani7coder/Rail-sync<br/><b>Branches:</b> main (default), master", table_cell),
            Paragraph("<b>Total Team Members:</b> 6<br/><b>Verification Status:</b> 52/52 Tests Passed (100%)", table_cell)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[2.2*inch, 2.8*inch, 2.0*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_light),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))
    
    # =========================================================================
    # SECTION 1: COMPLETE PROJECT OVERVIEW
    # =========================================================================
    story.append(Paragraph("1. Complete Project Overview", h1_style))
    story.append(Paragraph(
        "<b>RailSync</b> is an educational railway reservation simulation platform designed to simulate "
        "the passenger booking and scheduling workflows of national rail transit networks. Rather than presenting "
        "theoretical concepts in isolation, RailSync unifies full-stack web engineering with systems-level "
        "computer science disciplines across Operating Systems (OS) and Database Management Systems (DBMS):",
        body_style
    ))
    
    story.append(Paragraph("<b>• Operating Systems (OS) Engineering Pillars:</b>", bold_body))
    story.append(Paragraph("<b>1. Mutual Exclusion & Critical Sections:</b> Native C++17 memory allocators protected by <code>std::mutex</code> to eliminate concurrent allocation anomalies in multi-threaded runtime environments.", bullet_style))
    story.append(Paragraph("<b>2. Graph Algorithms & Priority Queues:</b> Route discovery implemented via Dijkstra's shortest path algorithm using a min-heap priority queue (<code>std::priority_queue</code>) executing in optimal O((V+E) log V) time.", bullet_style))
    story.append(Paragraph("<b>3. CPU Resource Throttling:</b> Counting semaphores (<code>threading.Semaphore(value=5)</code>) bounding heavy vector ReportLab PDF rendering threads to prevent server denial of service.", bullet_style))
    story.append(Paragraph("<b>4. In-Memory Native ABI Bridge:</b> Direct 64-bit C-ABI integration linking Python address space to compiled C++ shared libraries via <code>ctypes</code> with microsecond execution.", bullet_style))
    
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>• Database Management Systems (DBMS) Engineering Pillars:</b>", bold_body))
    story.append(Paragraph("<b>1. Relational 3NF Schema:</b> 14 normalized tables in MySQL 8.4 operating under the InnoDB storage engine with strict foreign key constraints and cascade actions.", bullet_style))
    story.append(Paragraph("<b>2. ACID Transactional Integrity:</b> Multi-statement transactions ensuring booking creation, payment records, seat locking, and inventory deductions commit atomically or roll back completely.", bullet_style))
    story.append(Paragraph("<b>3. Pessimistic Row-Level Locking:</b> Concurrency serialized using <code>SELECT ... FOR UPDATE</code> on the <code>seats</code> table, preventing race conditions and double bookings under concurrent demand.", bullet_style))
    story.append(Paragraph("<b>4. Intermediate Timetable Sequencing:</b> 206 sequenced timetable stops supporting multi-station intermediate passenger queries and distance-based fare calculations.", bullet_style))
    
    story.append(Spacer(1, 10))
    
    # =========================================================================
    # SECTION 2: SYSTEM WORKFLOWS
    # =========================================================================
    story.append(Paragraph("2. Core System Workflows", h1_style))
    
    story.append(Paragraph("2.1 End-to-End User Reservation Workflow", h2_style))
    story.append(Paragraph(
        "The reservation pipeline progresses through four synchronized steps: "
        "<b>Step 1 (Search & Filter):</b> Passenger queries origin, destination, and journey date. The backend queries <code>train_stops</code> "
        "to resolve direct and intermediate connections. "
        "<b>Step 2 (Seat Selection):</b> Passenger selects a travel class (e.g. 3A) and views the interactive Coach Seat Map. Clicking seats locks specific "
        "physical seat IDs (e.g. B1-17, B1-18) or enables C++ contiguous auto-allocation. "
        "<b>Step 3 (Passenger Manifest):</b> Passenger enters details (up to 6 passengers). The backend fare service calculates the authoritative fare. "
        "<b>Step 4 (Simulated Payment & Confirmation):</b> The passenger triggers payment authorization with an active idempotency token. On 200 OK, "
        "an atomic InnoDB transaction commits the reservation, issues a unique 10-character PNR (e.g. RS57631878), and generates a vector QR e-Ticket.",
        body_style
    ))
    
    story.append(Paragraph("2.2 Payment State Machine & Idempotency Protocol", h2_style))
    story.append(Paragraph(
        "The checkout system operates as a finite state machine: <code>IDLE</code> -> <code>PROCESSING</code> -> <code>SUCCESS</code> or <code>FAILED</code>. "
        "During processing, the submission button is disabled to prevent duplicate submissions. A unique UUID token (<code>idempotency_key</code>) is cached; "
        "subsequent clicks return the existing reservation without duplicate charges. In the event of a simulated bank decline, active seat locks are released via <code>ROLLBACK</code>, "
        "and the user is provided a state-preserving retry card.",
        body_style
    ))
    
    story.append(Paragraph("2.3 Automatic Waitlist (WL) & RAC Promotion Workflow", h2_style))
    story.append(Paragraph(
        "When confirmed seats are exhausted, bookings are placed in RAC or Waiting List (WL). When any confirmed passenger cancels, a transactional trigger "
        "queries <code>waitlist_entries</code> in strict FIFO order: an RAC passenger is promoted to <b>CONFIRMED</b> and assigned the vacated seat, while a WL passenger "
        "advances to RAC. All promotions commit atomically within the cancellation transaction.",
        body_style
    ))
    
    story.append(Spacer(1, 10))
    
    # =========================================================================
    # SECTION 3: FULL-STACK TECHNOLOGY STACK
    # =========================================================================
    story.append(Paragraph("3. Full-Stack Technology Stack", h1_style))
    
    tech_data = [
        [Paragraph("<b>Tier</b>", table_header), Paragraph("<b>Technologies</b>", table_header), Paragraph("<b>Key Responsibilities</b>", table_header)],
        [
            Paragraph("<b>Frontend SPA</b>", table_cell),
            Paragraph("React 18, Vite 8, Tailwind CSS, React Router v7, Axios, Lucide Icons", table_cell),
            Paragraph("Faceted search, interactive coach seat map, 4-step payment modal, PNR tracking, responsive UI", table_cell)
        ],
        [
            Paragraph("<b>Backend REST API</b>", table_cell),
            Paragraph("Python 3.11, Flask 3.0, Flask-CORS, Werkzeug 3.1, ReportLab 4.0, QRCode", table_cell),
            Paragraph("REST routing, authoritative fare calculation, PDF ticket generator, waitlist promotion, auth", table_cell)
        ],
        [
            Paragraph("<b>Algorithmic Engine</b>", table_cell),
            Paragraph("C++17, GCC/MinGW-w64, std::priority_queue, std::mutex, ctypes CDLL", table_cell),
            Paragraph("O((V+E) log V) Dijkstra route engine, contiguous seat allocation, hardware mutual exclusion", table_cell)
        ],
        [
            Paragraph("<b>Database Tier</b>", table_cell),
            Paragraph("MySQL 8.4 Server, InnoDB Engine, Pessimistic Row Locking (FOR UPDATE)", table_cell),
            Paragraph("14 relational 3NF tables, ACID transactions, 55 stations, 48 trains, 206 stops dataset", table_cell)
        ],
        [
            Paragraph("<b>DevOps & Containers</b>", table_cell),
            Paragraph("Docker Engine 24+, Docker Compose 2.20+, Alpine Nginx, Multi-Stage Builds", table_cell),
            Paragraph("Multi-container orchestration, persistent volume (mysql_data), health checks, reverse proxy", table_cell)
        ],
    ]
    
    tech_table = Table(tech_data, colWidths=[1.3*inch, 2.7*inch, 3.0*inch])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light])
    ]))
    story.append(tech_table)
    
    story.append(PageBreak())
    
    # =========================================================================
    # SECTION 4: TEAM TASK DIVISION & MODULE OWNERSHIP
    # =========================================================================
    story.append(Paragraph("4. Team Roles, Task Distribution & Module Ownership", h1_style))
    story.append(Paragraph(
        "The project scope was strategically apportioned among six team members. Below is the complete roster, followed by "
        "detailed individual module ownership, source file mappings, and presentation viva topics for each member:",
        body_style
    ))
    
    roster_data = [
        [Paragraph("<b>Member</b>", table_header), Paragraph("<b>Role</b>", table_header), Paragraph("<b>Primary Domain</b>", table_header), Paragraph("<b>Key Modules Owned</b>", table_header)],
        [
            Paragraph("<b>Umanga</b><br/><i>(Leader)</i>", table_cell),
            Paragraph("DevOps Architect & System Lead", table_cell),
            Paragraph("Containerization & Orchestration", table_cell),
            Paragraph("Docker Compose, Nginx Reverse Proxy, Health Checks, Git Governance", table_cell)
        ],
        [
            Paragraph("<b>Akhil</b>", table_cell),
            Paragraph("Core Backend Architect", table_cell),
            Paragraph("Flask REST API & Services", table_cell),
            Paragraph("Booking Engine, Payment State Machine, Fare Calculator, Waitlist FIFO", table_cell)
        ],
        [
            Paragraph("<b>Vedansh</b><br/><i>(Swapped)</i>", table_cell),
            Paragraph("Frontend Architect & UI/UX", table_cell),
            Paragraph("React 18 SPA Client Tier", table_cell),
            Paragraph("Faceted Search, SeatMap Picker, Checkout Modal, PNR UI, Tailwind", table_cell)
        ],
        [
            Paragraph("<b>Aditya</b><br/><i>(Swapped)</i>", table_cell),
            Paragraph("Database Architect", table_cell),
            Paragraph("MySQL 8.4 InnoDB Concurrency", table_cell),
            Paragraph("14 3NF Tables, Row Locking (FOR UPDATE), 206 Stops Dataset, Seed SQL", table_cell)
        ],
        [
            Paragraph("<b>Yash</b>", table_cell),
            Paragraph("Systems & Algorithms Lead", table_cell),
            Paragraph("C++17 Engine & OS Mutex", table_cell),
            Paragraph("Min-Heap Dijkstra Engine, Contiguous Allocator, Python ctypes Bridge", table_cell)
        ],
        [
            Paragraph("<b>Abhinav</b><br/><i>(Expanded)</i>", table_cell),
            Paragraph("Security, Diagnostics & QA", table_cell),
            Paragraph("RBAC, Telemetry & Testing", table_cell),
            Paragraph("Diagnostics API, Vector QR Verification, 52 Pytest Tests, Project Report", table_cell)
        ],
    ]
    
    roster_table = Table(roster_data, colWidths=[1.1*inch, 1.8*inch, 1.6*inch, 2.5*inch])
    roster_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light])
    ]))
    story.append(roster_table)
    story.append(Spacer(1, 12))
    
    # -------------------------------------------------------------------------
    # MEMBER 1: UMANGA
    # -------------------------------------------------------------------------
    story.append(Paragraph("4.1 Umanga — Team Leader & DevOps Architect", h2_style))
    story.append(Paragraph("<b>• Primary Role:</b> Project Leader, Containerization Engineer & System Orchestration Specialist.", body_style))
    story.append(Paragraph("<b>• Specific Modules & Source Files Worked On:</b>", bold_body))
    story.append(Paragraph("1. <code>docker-compose.yml</code>: Orchestrated multi-tier container network (MySQL 8.4, Flask backend, Nginx frontend).", bullet_style))
    story.append(Paragraph("2. <code>frontend/Dockerfile</code>: Authored multi-stage build (Node.js builder -> Alpine Nginx runner).", bullet_style))
    story.append(Paragraph("3. <code>frontend/nginx.conf</code>: Production Nginx web server configuration with SPA routing and API proxy.", bullet_style))
    story.append(Paragraph("4. <code>backend/Dockerfile</code>: Python 3.11 container with native g++ compilation of C++17 shared library.", bullet_style))
    story.append(Paragraph("5. <code>DOCKER_GUIDE.md</code>: Container operations, persistent volumes, and deployment documentation.", bullet_style))
    story.append(Paragraph("<b>• Core Technical Contributions:</b> Configured <code>railsync-network</code> bridge, container health checks with startup dependencies (<code>condition: service_healthy</code>), persistent volume (<code>mysql_data</code>), and automated database seeding.", body_style))
    story.append(Paragraph("<b>• Key Viva / Defense Question & Answer:</b><br/>"
                           "<i>Q: Why use a multi-stage Dockerfile for the frontend instead of running Vite dev server?</i><br/>"
                           "<b>A:</b> Multi-stage builds compile static bundles with Node and serve them via an Alpine Nginx image (~30MB vs 600MB+), eliminating Node.js runtime memory overhead and providing high-concurrency static delivery.", body_style))
    story.append(Spacer(1, 8))
    
    # -------------------------------------------------------------------------
    # MEMBER 2: AKHIL
    # -------------------------------------------------------------------------
    story.append(Paragraph("4.2 Akhil — Core Backend Architect & Flask REST API Engineer", h2_style))
    story.append(Paragraph("<b>• Primary Role:</b> Backend Application Architect, Payment State Machine & Transactional Services Engineer.", body_style))
    story.append(Paragraph("<b>• Specific Modules & Source Files Worked On:</b>", bold_body))
    story.append(Paragraph("1. <code>backend/app/routes/bookings.py</code> & <code>services/booking_service.py</code>: Atomic booking transactions, PNR generation, and seat locking.", bullet_style))
    story.append(Paragraph("2. <code>backend/app/routes/payments.py</code>: Simulated payment gateway with idempotency tokens and state machine transitions.", bullet_style))
    story.append(Paragraph("3. <code>backend/app/services/fare_service.py</code>: Authoritative dynamic fare engine (base fare, class multipliers, surcharges, GST).", bullet_style))
    story.append(Paragraph("4. <code>backend/app/services/waitlist_service.py</code>: FIFO queue manager for RAC and Waiting List (WL) auto-promotion.", bullet_style))
    story.append(Paragraph("5. <code>backend/app/services/pdf_service.py</code>: Vector PDF e-ticket generator with ReportLab and OS Semaphore (<code>value=5</code>).", bullet_style))
    story.append(Paragraph("6. <code>backend/app/services/train_service.py</code> & <code>routes/trains.py</code>: Multi-criteria search and intermediate stop routing.", bullet_style))
    story.append(Paragraph("<b>• Core Technical Contributions:</b> Overhauled Step 4 payment authorization with idempotency tokens, built authoritative backend fare calculation preventing client tampering, and implemented counting semaphores protecting backend CPU during PDF rendering.", body_style))
    story.append(Paragraph("<b>• Key Viva / Defense Question & Answer:</b><br/>"
                           "<i>Q: What problem does the idempotency key solve in the payment workflow?</i><br/>"
                           "<b>A:</b> It prevents duplicate bookings and charges if a user double-clicks or encounters network lag; the backend recognizes the duplicate key and returns the existing confirmed reservation without re-executing seat deductions.", body_style))
    story.append(Spacer(1, 8))
    
    # -------------------------------------------------------------------------
    # MEMBER 3: VEDANSH (SWAPPED TO FRONTEND)
    # -------------------------------------------------------------------------
    story.append(Paragraph("4.3 Vedansh — Frontend Architect & UI/UX Specialist (Swapped)", h2_style))
    story.append(Paragraph("<b>• Primary Role:</b> React 18 Single Page Application Developer, Component Architect & UI/UX Specialist.", body_style))
    story.append(Paragraph("<b>• Specific Modules & Source Files Worked On:</b>", bold_body))
    story.append(Paragraph("1. <code>frontend/src/pages/SearchTrains.jsx</code> & <code>components/TrainCard.jsx</code>: Faceted search filters, 9 categories, and 3-train comparison.", bullet_style))
    story.append(Paragraph("2. <code>frontend/src/pages/TrainDetails.jsx</code> & <code>components/SeatMap.jsx</code>: Interactive Coach Seat Map, available/occupied states, class sync.", bullet_style))
    story.append(Paragraph("3. <code>frontend/src/pages/PassengerDetails.jsx</code>: Multi-passenger dynamic manifest form (up to 6 passengers) with berth preferences.", bullet_style))
    story.append(Paragraph("4. <code>frontend/src/pages/Payment.jsx</code>: 4-step payment modal with state transitions (IDLE -> PROCESSING -> SUCCESS/FAILED).", bullet_style))
    story.append(Paragraph("5. <code>frontend/src/pages/PNRStatus.jsx</code> & <code>TicketDetails.jsx</code>: PNR tracking, printable ticket view, and embedded vector QR code.", bullet_style))
    story.append(Paragraph("6. <code>frontend/src/context/AuthContext.jsx</code> & <code>ToastContext.jsx</code>: Global authentication state and floating notification toasts.", bullet_style))
    story.append(Paragraph("<b>• Core Technical Contributions:</b> Fixed the search-to-seat navigation flow so clicking 'Select Seats & Book' takes passengers to the interactive coach map, synchronized selected classes to auto-open corresponding coaches (e.g. Coach B1 for 3A), and built the responsive Tailwind UI.", body_style))
    story.append(Paragraph("<b>• Key Viva / Defense Question & Answer:</b><br/>"
                           "<i>Q: How does the frontend handle seat selection state across multiple components?</i><br/>"
                           "<b>A:</b> Seat state is maintained in <code>TrainDetails.jsx</code>, rendered interactively in <code>SeatMap.jsx</code>, and passed via React Router location state to <code>PassengerDetails.jsx</code>, where each passenger is assigned their respective physical seat ID.", body_style))
    story.append(Spacer(1, 8))
    
    story.append(PageBreak())
    
    # -------------------------------------------------------------------------
    # MEMBER 4: ADITYA (SWAPPED TO DATABASE)
    # -------------------------------------------------------------------------
    story.append(Paragraph("4.4 Aditya — Database Architect & SQL Concurrency Engineer (Swapped)", h2_style))
    story.append(Paragraph("<b>• Primary Role:</b> Database Architect, MySQL InnoDB Relational Modeling, ACID Transactions & Concurrency Specialist.", body_style))
    story.append(Paragraph("<b>• Specific Modules & Source Files Worked On:</b>", bold_body))
    story.append(Paragraph("1. <code>database/schema.sql</code>: Full DDL defining 14 normalized tables operating under the MySQL 8.4 InnoDB engine.", bullet_style))
    story.append(Paragraph("2. <code>database/seed_data.sql</code>: Repeatable 139 KB SQL dataset seeding 55 stations, 48 trains, 206 stops, and 3,072 seats.", bullet_style))
    story.append(Paragraph("3. <code>backend/scripts/generate_seed_sql.py</code>: Automated database export script synchronizing live data to seed files.", bullet_style))
    story.append(Paragraph("4. <code>DATABASE_DOCUMENTATION.md</code>: Schema dictionary, ER diagram, foreign keys, and indexing documentation.", bullet_style))
    story.append(Paragraph("<b>• Core Technical Contributions:</b> Normalized database schema to Third Normal Form (3NF), implemented row-level locking (<code>SELECT ... FOR UPDATE</code>) on seats preventing double booking, and built composite indexes (<code>(train_id, stop_sequence)</code>) for sub-millisecond timetable lookups.", body_style))
    story.append(Paragraph("<b>• Key Viva / Defense Question & Answer:</b><br/>"
                           "<i>Q: What is the difference between table-level locking and row-level locking in high-concurrency booking systems?</i><br/>"
                           "<b>A:</b> Table-level locking locks the entire <code>seats</code> table, serializing all users and destroying throughput. Row-level locking in InnoDB (<code>FOR UPDATE</code>) locks only the specific requested seat rows, allowing other passengers to book different seats concurrently.", body_style))
    story.append(Spacer(1, 8))
    
    # -------------------------------------------------------------------------
    # MEMBER 5: YASH
    # -------------------------------------------------------------------------
    story.append(Paragraph("4.5 Yash — Systems & Algorithms Engineer (C++17 Core)", h2_style))
    story.append(Paragraph("<b>• Primary Role:</b> C++17 Systems Programmer, Graph Algorithm Designer & Operating System Synchronization Specialist.", body_style))
    story.append(Paragraph("<b>• Specific Modules & Source Files Worked On:</b>", bold_body))
    story.append(Paragraph("1. <code>backend/cpp_engine/core_logic.cpp</code> & <code>core_logic.h</code>: Native C++17 Min-Heap Dijkstra algorithm and contiguous seat allocator.", bullet_style))
    story.append(Paragraph("2. <code>backend/cpp_engine/engine_cli.cpp</code>: Standalone native CLI execution bridge.", bullet_style))
    story.append(Paragraph("3. <code>backend/cpp_engine/Makefile</code>: Cross-platform build script generating <code>railsync_engine.dll</code> and <code>librailsync_engine.so</code>.", bullet_style))
    story.append(Paragraph("4. <code>backend/app/services/cpp_engine_service.py</code>: In-memory 64-bit ABI bridge using Python <code>ctypes.CDLL</code>.", bullet_style))
    story.append(Paragraph("5. <code>backend/scripts/build_cpp.py</code>: Automated compilation script supporting Windows and Linux.", bullet_style))
    story.append(Paragraph("<b>• Core Technical Contributions:</b> Modeled railway graph as an adjacency list and implemented Dijkstra's algorithm with <code>std::priority_queue</code> in O((V+E) log V) time, implemented hardware mutual exclusion with <code>std::mutex</code>, and configured in-process Python ctypes CDLL integration.", body_style))
    story.append(Paragraph("<b>• Key Viva / Defense Question & Answer:</b><br/>"
                           "<i>Q: Why is a binary min-heap priority queue used in Dijkstra's algorithm instead of a simple array?</i><br/>"
                           "<b>A:</b> An array requires O(V) time to extract the minimum distance node, giving O(V^2) total time. A binary min-heap reduces extract-min operations to O(log V), lowering overall complexity to O((V+E) log V).", body_style))
    story.append(Spacer(1, 8))
    
    # -------------------------------------------------------------------------
    # MEMBER 6: ABHINAV (EXPANDED ROLE)
    # -------------------------------------------------------------------------
    story.append(Paragraph("4.6 Abhinav — Security, Diagnostics, QR Cryptography & QA Lead (Expanded)", h2_style))
    story.append(Paragraph("<b>• Primary Role:</b> Security Engineer, System Diagnostics Architect, Digital QR Cryptographer & Test Automation Lead.", body_style))
    story.append(Paragraph("<b>• Specific Modules & Source Files Worked On:</b>", bold_body))
    story.append(Paragraph("1. <code>backend/app/routes/admin.py</code>: System Diagnostics API (<code>/api/admin/diagnostics</code>) inspecting MySQL rows, ACID checks, and C++ telemetry.", bullet_style))
    story.append(Paragraph("2. <code>backend/app/services/pdf_service.py</code>: Vector QR code generation, SHA-256 digital booking verification (<code>/api/tickets/<pnr>/verify</code>).", bullet_style))
    story.append(Paragraph("3. <code>backend/app/routes/auth.py</code> & Security: Role-Based Access Control (RBAC: USER vs ADMIN), session hardening, parameterized SQL (%s).", bullet_style))
    story.append(Paragraph("4. <code>backend/tests/</code>: Designed and executed 52 automated tests across 8 suites (admin, advanced, auth, bookings, concurrency, C++, payments, trains).", bullet_style))
    story.append(Paragraph("5. <code>PROJECT_REPORT.md</code> & <code>FINAL_TEST_REPORT.md</code>: Comprehensive academic project report and test execution matrices.", bullet_style))
    story.append(Paragraph("<b>• Core Technical Contributions:</b> Hardened endpoints against unauthorized access, built real-time telemetry inspecting live database health, integrated dynamic vector QR codes for offline verification, and designed multithreaded concurrency tests simulating simultaneous seat collisions.", body_style))
    story.append(Paragraph("<b>• Key Viva / Defense Question & Answer:</b><br/>"
                           "<i>Q: How did you test concurrency and race conditions in the automated test suite?</i><br/>"
                           "<b>A:</b> In <code>test_concurrency.py</code>, we simulate two concurrent threads executing transactions competing for the exact same physical seat ID; the test verifies that the first transaction commits atomically with HTTP 201, while the second receives an immediate HTTP 409 Conflict rejection with zero duplicate allocations.", body_style))
    
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=1, color=c_border, spaceBefore=0, spaceAfter=10))
    story.append(Paragraph("<b>Project Verification Summary:</b> 52/52 automated tests passed | MySQL InnoDB ACID atomicity verified | C++17 engine active via 64-bit ctypes | Docker Compose multi-container stack operational.", bold_body))
    
    # Build Document with NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated official PDF at: {pdf_path}")
    return pdf_path

if __name__ == '__main__':
    build_pdf()
