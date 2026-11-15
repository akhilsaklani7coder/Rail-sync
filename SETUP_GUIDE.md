# RailSync — Complete Installation & Setup Guide

This guide provides instructions for deploying and running **RailSync** on your local machine using either **Docker Compose** (recommended for production-like evaluation) or **Bare-Metal Local Execution** (ideal for active development).

---

## Method A: Quick Deployment via Docker Compose (Recommended)

### Prerequisites
- Docker Engine 24.0+ & Docker Compose 2.20+
- Host ports available: `8080`, `5001`, `3306`

### Step 1: Clone Repository
```bash
git clone https://github.com/akhilsaklani7coder/Rail-sync.git
cd Rail-sync
```

### Step 2: Configure Environment
```bash
cp .env.example .env
```
*(Optionally review `.env` and adjust database passwords or port numbers if necessary.)*

### Step 3: Launch Containers
```bash
docker compose up --build -d
```
Docker Compose will automatically:
1. Build the production React frontend using a multi-stage Nginx container.
2. Compile the C++17 route engine (`librailsync_engine.so`) inside Python 3.11 Debian Linux.
3. Start MySQL 8.4, initialize the 14-table schema (`schema.sql`), and seed the complete dataset (`seed_data.sql`).

### Step 4: Access Application
- Web UI: [http://localhost:8080](http://localhost:8080)
- API Health Check: [http://localhost:5001/api/health](http://localhost:5001/api/health)
- Admin Login: `admin@railsync.com` / `Admin@123`

---

## Method B: Bare-Metal Local Development Setup

### Prerequisites
- **Node.js:** v18.0.0 or higher (v20+ recommended)
- **Python:** v3.11 or v3.12 (64-bit)
- **MySQL Server:** v8.0 or v8.4 Community Server
- **C++ Compiler:** `g++` (MinGW-w64 on Windows, or GCC on Linux/macOS) supporting C++17

---

### Step 1: Database Setup (MySQL 8.4)
1. Ensure your local MySQL server is running on `127.0.0.1:3306`.
2. Connect to MySQL and create the database:
   ```sql
   CREATE DATABASE IF NOT EXISTS railsync_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. Initialize the schema and seed dataset:
   ```bash
   # On Windows PowerShell
   Get-Content database/schema.sql | mysql -u root -p railsync_db
   Get-Content database/seed_data.sql | mysql -u root -p railsync_db

   # On Linux / macOS
   mysql -u root -p railsync_db < database/schema.sql
   mysql -u root -p railsync_db < database/seed_data.sql
   ```

---

### Step 2: C++ Route Engine Compilation
Build the shared dynamic library for your operating system:
```bash
# Using the automated cross-platform build script:
python backend/scripts/build_cpp.py

# Or manually using make / g++:
cd backend/cpp_engine
make clean && make
cd ../..
```
- On Windows: Generates `backend/cpp_engine/railsync_engine.dll`.
- On Linux: Generates `backend/cpp_engine/librailsync_engine.so`.

---

### Step 3: Backend Setup (Python + Flask)
1. Create and activate a Python virtual environment:
   ```bash
   # Windows PowerShell
   python -m venv backend/venv
   .\backend\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv backend/venv
   source backend/venv/bin/activate
   ```
2. Install Python dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r backend/requirements.txt
   ```
3. Run the Flask API server:
   ```bash
   # Set PYTHONPATH to include backend directory
   $env:PYTHONPATH="backend"    # Windows PowerShell
   export PYTHONPATH="backend"  # Linux / macOS

   python backend/main.py
   ```
   *The backend will start and listen on `http://127.0.0.1:5001`.*

---

### Step 4: Frontend Setup (React + Vite)
1. In a separate terminal, navigate to the `frontend` folder:
   ```bash
   cd frontend
   npm install
   ```
2. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *The frontend application will start on `http://localhost:8080`.*

---

## Method C: Running Automated Tests

To run the complete 52-test automated verification suite:
```bash
# Ensure virtual environment is activated and PYTHONPATH is set:
$env:PYTHONPATH="backend"   # Windows
export PYTHONPATH="backend" # Linux/macOS

pytest backend/tests/ -v
```
All 52 tests covering admin access, C++ Dijkstra algorithms, ACID transactions, seat allocations, and Step 4 payment authorization will run and pass.

---

## Default Evaluation Accounts

| Role | Email | Password | Permissions |
|---|---|---|---|
| **Administrator** | `admin@railsync.com` | `Admin@123` | Full Admin Dashboard, Station/Train CRUD, Diagnostics |
| **Demo Passenger** | `user@railsync.com` | `User@123` | Search, Seat Selection, Booking, Cancellations, Tickets |
