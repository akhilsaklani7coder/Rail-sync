# RailSync Backend Dockerfile
# Python 3.11 with C++17 Dijkstra Engine compilation
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# Install system build dependencies for C++17 engine compilation and health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    g++ \
    make \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . /app/

# Build C++17 route engine for Linux (produces librailsync_engine.so)
WORKDIR /app/cpp_engine
RUN make clean && make
WORKDIR /app

# Add unprivileged user for security
RUN useradd -m -u 1000 railsync && \
    chown -R railsync:railsync /app

USER railsync

EXPOSE 5001

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5001/api/health || exit 1

CMD ["python", "main.py"]
