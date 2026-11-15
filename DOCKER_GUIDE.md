# RailSync — Docker & Containerization Guide

This guide details the container architecture, orchestration configuration, execution procedures, and troubleshooting steps for running **RailSync** using Docker and Docker Compose.

---

## 1. Container Topology & Architecture

RailSync is organized into three networked container services communicating over an isolated bridge network (`railsync-network`):

```
                     ┌───────────────────────────────┐
                     │          HOST MACHINE         │
                     │  Browser: http://localhost:8080│
                     └───────────────┬───────────────┘
                                     │ Port 8080 (HTTP)
                                     ▼
 ┌───────────────────────────────────────────────────────────────────────────┐
 │ DOCKER COMPOSE NETWORK: railsync-network                                  │
 │                                                                           │
 │  ┌─────────────────────────────────────────────────────────────────────┐  │
 │  │ Service: frontend (container: railsync-frontend)                    │  │
 │  │ • Base Image: nginx:alpine                                          │  │
 │  │ • Built from: node:20-alpine (multi-stage Vite build)               │  │
 │  │ • Port: 8080:80 (Nginx web server)                                  │  │
 │  │ • Features: SPA fallback routing ($uri /index.html)                │  │
 │  │ • Reverse Proxy: /api/ -> http://backend:5001/api/                  │  │
 │  └──────────────────────────────────┬──────────────────────────────────┘  │
 │                                     │ Internal DNS: http://backend:5001   │
 │                                     ▼                                     │
 │  ┌─────────────────────────────────────────────────────────────────────┐  │
 │  │ Service: backend (container: railsync-backend)                      │  │
 │  │ • Base Image: python:3.11-slim                                      │  │
 │  │ • Build: Compiles C++17 engine -> librailsync_engine.so (g++)       │  │
 │  │ • Port: 5001:5001 (Flask REST API)                                  │  │
 │  │ • Healthcheck: curl -f http://127.0.0.1:5001/api/health             │  │
 │  └──────────────────────────────────┬──────────────────────────────────┘  │
 │                                     │ Internal DNS: db:3306               │
 │                                     ▼                                     │
 │  ┌─────────────────────────────────────────────────────────────────────┐  │
 │  │ Service: db (container: railsync-mysql)                             │  │
 │  │ • Image: mysql:8.4                                                  │  │
 │  │ • Port: 3306:3306                                                   │  │
 │  │ • Storage Engine: InnoDB (Row-level locking)                        │  │
 │  │ • Volumes: mysql_data (persistent volume)                           │  │
 │  │ • Init Scripts: 01_schema.sql (14 tables), 02_seed.sql (dataset)    │  │
 │  │ • Healthcheck: mysqladmin ping                                      │  │
 │  └─────────────────────────────────────────────────────────────────────┘  │
 └───────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Prerequisites

To run RailSync via Docker, ensure the following are installed on your host system:
1. **Docker Engine:** Version 24.0 or higher.
2. **Docker Compose:** Version 2.20 or higher.
3. Available local ports: `8080` (Frontend), `5001` (Backend API), and `3306` (MySQL database).

> [!NOTE]
> If a local MySQL server is already running on port `3306`, either stop the local service or change the host port mapping in `.env` (e.g. `DB_PORT=3307`).

---

## 3. Quickstart: Launching the Application

### Step 1: Clone the Repository & Prepare Environment
```bash
git clone https://github.com/akhilsaklani7coder/Rail-sync.git
cd Rail-sync

# Copy environment variables template
cp .env.example .env
```

### Step 2: Build and Start Containers
```bash
docker compose up --build -d
```

### Step 3: Verify Container Health & Status
```bash
docker compose ps
```
Expected output:
```
NAME                IMAGE               COMMAND                  SERVICE             STATUS              PORTS
railsync-mysql      mysql:8.4           "docker-entrypoint.s…"   db                  healthy             0.0.0.0:3306->3306/tcp
railsync-backend    railsync-backend    "python main.py"         backend             healthy             0.0.0.0:5001->5001/tcp
railsync-frontend   railsync-frontend   "nginx -g 'daemon of…"   frontend            healthy             0.0.0.0:8080->80/tcp
```

### Step 4: Access the Application
- **Frontend User Portal:** [http://localhost:8080](http://localhost:8080)
- **Backend API Health Check:** [http://localhost:5001/api/health](http://localhost:5001/api/health)
- **Admin Dashboard:** [http://localhost:8080/admin](http://localhost:8080/admin)
  - Demo Admin: `admin@railsync.com` / `Admin@123`
  - Demo Passenger: `user@railsync.com` / `User@123`

---

## 4. Environment Variables Reference

| Variable | Default Value | Description |
|---|---|---|
| `FLASK_ENV` | `production` | Flask runtime mode |
| `DB_HOST` | `db` | Docker internal hostname for MySQL |
| `DB_PORT` | `3306` | Internal MySQL port |
| `DB_USER` | `root` | Database username |
| `DB_PASSWORD` | `rootpassword` | Database root password |
| `DB_NAME` | `railsync_db` | Primary database name |
| `SECRET_KEY` | `railsync_secret_...` | Flask session cryptographic key |
| `CORS_ORIGINS`| `http://localhost:8080` | Allowed browser origins |

---

## 5. Persistence & Data Lifecycle

- **Database Volume:** The named volume `mysql_data` persists all database modifications (new bookings, payments, and cancellations) across container restarts.
- **Repeatable Initialization:** When launching on a clean system with no existing volume, MySQL automatically executes `./database/schema.sql` followed by `./database/seed_data.sql` to populate the complete 55 stations, 48 trains, and 206 stops.
- **Restarting Without Data Loss:**
  ```bash
  docker compose restart
  ```
- **Resetting to Fresh Factory State:**
  ```bash
  # Stops containers and removes the persistent volume
  docker compose down -v
  # Re-launch and auto-seed cleanly
  docker compose up --build -d
  ```

---

## 6. Inspecting Logs & Debugging

- **Stream All Logs:**
  ```bash
  docker compose logs -f
  ```
- **Stream Backend Service Logs:**
  ```bash
  docker compose logs -f backend
  ```
- **Open a Shell Inside the Backend Container:**
  ```bash
  docker compose exec backend bash
  # Verify C++ engine shared library
  ls -lh /app/cpp_engine/librailsync_engine.so
  # Run test suite inside container
  pytest /app/tests/ -v
  ```
- **Open MySQL CLI Inside Database Container:**
  ```bash
  docker compose exec db mysql -u root -prootpassword railsync_db
  ```

---

## 7. Troubleshooting Common Issues

1. **Port 8080 or 3306 Already in Use:**
   - Solution: Stop local services holding those ports, or adjust port mappings in `docker-compose.yml` (e.g. `"8081:80"`).
2. **Backend Fails to Connect to Database on Startup:**
   - Docker Compose handles this via `condition: service_healthy` on `db`. The backend will only start once MySQL responds successfully to `mysqladmin ping`.
3. **C++ Engine Fails to Build on Host Architecture:**
   - The `backend/Dockerfile` installs `build-essential` and `g++` directly inside Debian Linux to compile `librailsync_engine.so` natively, eliminating cross-compilation incompatibilities.
