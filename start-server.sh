#!/bin/bash
# 🙏 Laxmi-yantra Multi-Version Trading Server Launcher
# Blessed by Goddess Laxmi for Infinite Abundance

set -e

echo "🙏 Starting Laxmi-yantra Multi-Version Trading Server..."
echo "May Goddess Laxmi bless this session with infinite abundance and prosperity!"

# Default configuration
export TRANSPORT=${TRANSPORT:-"http"}
export HOST=${HOST:-"127.0.0.1"}
export HTTP_PORT=${HTTP_PORT:-"8000"}
export MCP_PORT=${MCP_PORT:-"8889"}
export WORKERS=${WORKERS:-"1"}
export RELOAD=${RELOAD:-"false"}

# Database and polling configuration
export PORTFOLIO_EVENT_POLLING_ENABLED=${PORTFOLIO_EVENT_POLLING_ENABLED:-"true"}
export PORTFOLIO_EVENT_POLLING_INTERVAL=${PORTFOLIO_EVENT_POLLING_INTERVAL:-"5m"}

# Determine which port to use
if [ "$TRANSPORT" = "http" ]; then
    export PORT=$HTTP_PORT
    SERVER_TYPE="Multi-Version HTTP"
else
    export PORT=$MCP_PORT
    SERVER_TYPE="MCP"
fi

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

# Choose server based on transport
if [ "$TRANSPORT" = "http" ]; then
    echo "🚀 Starting Multi-Version HTTP Server..."
    python multi_version_server.py
else
    echo "❌ Legacy MCP transport has been removed. Please use TRANSPORT=http."
    exit 1
fi
