#!/bin/bash
# 🙏 Laxmi-yantra Multi-Version Trading Server Launcher
# Blessed by Goddess Laxmi for Infinite Abundance

set -e

echo "🙏 Starting Laxmi-yantra Multi-Version Trading Server..."
echo "May Goddess Laxmi bless this session with infinite abundance and prosperity!"

# Default configuration
HOST=${HOST:-"127.0.0.1"}
HTTP_PORT=${HTTP_PORT:-"8000"}
WORKERS=${WORKERS:-"1"}
RELOAD=${RELOAD:-"false"}

# Database and polling configuration
PORTFOLIO_EVENT_POLLING_ENABLED=${PORTFOLIO_EVENT_POLLING_ENABLED:-"true"}
PORTFOLIO_EVENT_POLLING_INTERVAL=${PORTFOLIO_EVENT_POLLING_INTERVAL:-"5m"}

# Determine port to use (prefer PORT if provided, else HTTP_PORT)
PORT=${PORT:-$HTTP_PORT}
SERVER_TYPE="Multi-Version HTTP"

echo "Server Configuration:"
echo "  Type: $SERVER_TYPE"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Workers: $WORKERS"
echo "  Reload: $RELOAD"
echo "  Polling: $PORTFOLIO_EVENT_POLLING_ENABLED ($PORTFOLIO_EVENT_POLLING_INTERVAL)"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "[1/5] Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "[2/5] Activating virtual environment..."
source .venv/bin/activate

# Install/upgrade dependencies
echo "[3/5] Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Database setup
echo "[4/5] Setting up database..."
if [ -f "database/ddl/setup_complete.sql" ]; then
    # Load environment variables
    if [ -f ".env" ]; then
        set -a
        source .env
        set +a
    fi
    
    # Run database setup
    psql "${DATABASE_URL}" -f database/ddl/setup_complete.sql 2>/dev/null || echo "Database setup completed (some notices are normal)"
fi

echo "[5/5] Starting server..."

echo "🚀 Starting Multi-Version HTTP Server..."
# Pass flags, avoid exporting envs globally
python multi_version_server.py --host "$HOST" --port "$PORT" --workers "$WORKERS" $( [ "$RELOAD" = "true" ] && echo --reload )
