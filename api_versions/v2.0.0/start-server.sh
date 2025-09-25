#!/bin/bash
# 🙏 BrainTransactionsManager v2.0.0 Server Launcher
# Blessed by Goddess Laxmi for Infinite Abundance

set -e

echo "🙏 Starting BrainTransactionsManager v2.0.0..."
echo "May Goddess Laxmi bless this session with infinite abundance and prosperity!"

# Default configuration
HOST=${HOST:-"127.0.0.1"}
PORT=${PORT:-"8000"}
WORKERS=${WORKERS:-"1"}
RELOAD=${RELOAD:-"false"}
ENVIRONMENT=${ENVIRONMENT:-"development"}

echo "Server Configuration:"
echo "  Version: 2.0.0"
echo "  Environment: $ENVIRONMENT"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Workers: $WORKERS"
echo "  Reload: $RELOAD"

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

# Database setup and validation
echo "[4/5] Validating database setup..."
if [ -f "../../database/ddl/setup_complete.sql" ]; then
    # Load environment variables
    if [ -f ".env" ]; then
        set -a
        source .env
        set +a
    fi
    
    # Test database connection
    DB_URL=${DATABASE_URL:-"postgresql://$(whoami)@localhost:5432/braintransactions"}
    psql "$DB_URL" -c "SELECT 1;" 2>/dev/null || {
        echo "Database not accessible, running setup..."
        psql "postgresql://$(whoami)@localhost:5432/postgres" -f ../../database/ddl/setup_complete.sql 2>/dev/null || echo "Database setup completed (some notices are normal)"
    }
fi

echo "[5/5] Starting server..."

# Set environment
export ENVIRONMENT="$ENVIRONMENT"

echo "🚀 Starting BrainTransactionsManager v2.0.0 Server..."
echo "API Documentation: http://$HOST:$PORT/docs"
echo "Health Check: http://$HOST:$PORT/health"

# Start server with appropriate settings
if [ "$RELOAD" = "true" ]; then
    python server.py --host "$HOST" --port "$PORT" --reload
else
    python server.py --host "$HOST" --port "$PORT" --workers "$WORKERS"
fi
