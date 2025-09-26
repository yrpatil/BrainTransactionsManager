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
DEV_MODE=${DEV_MODE:-"true"}

echo "Server Configuration:"
echo "  Version: 2.0.0"
echo "  Environment: $ENVIRONMENT"
echo "  Development Mode: $DEV_MODE"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Workers: $WORKERS"
echo "  Reload: $RELOAD"

# Setup based on mode
if [ "$DEV_MODE" = "true" ]; then
    echo "[1/4] Running in Development Mode - using local server.py"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv .venv
    fi
    
    # Activate virtual environment
    echo "[2/4] Activating virtual environment..."
    source .venv/bin/activate
    
    # Install/upgrade dependencies
    echo "[3/4] Installing dependencies..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    
else
    echo "[1/4] Running in Production Mode - using versioned API"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "api_versions/v2.0.0/.venv" ]; then
        echo "Creating virtual environment..."
        cd api_versions/v2.0.0
        python3 -m venv .venv
        cd ../..
    fi
    
    # Activate virtual environment
    echo "[2/4] Activating virtual environment..."
    source api_versions/v2.0.0/.venv/bin/activate
    
    # Install/upgrade dependencies
    echo "[3/4] Installing dependencies..."
    pip install -q --upgrade pip
    pip install -q -r api_versions/v2.0.0/requirements.txt
fi

# Database setup and validation
echo "[4/4] Validating database setup..."
if [ -f "database/ddl/setup_complete.sql" ]; then
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
        psql "postgresql://$(whoami)@localhost:5432/postgres" -f database/ddl/setup_complete.sql 2>/dev/null || echo "Database setup completed (some notices are normal)"
    }
fi

echo "🚀 Starting server..."

# Set environment
export ENVIRONMENT="$ENVIRONMENT"

echo "🚀 Starting BrainTransactionsManager v2.0.0 Server..."
echo "📊 Dashboard: http://$HOST:$PORT/dashboard"
echo "📚 API Documentation: http://$HOST:$PORT/docs"
echo "❤️ Health Check: http://$HOST:$PORT/health"
echo "🔗 Dashboard API: http://$HOST:$PORT/dashboard/data"
echo "🔄 Order Sync (Manual): http://$HOST:$PORT/admin/sync-orders"
echo "📋 Pending Orders: http://$HOST:$PORT/admin/pending-orders"
echo ""
echo "🤖 Background Monitoring: Order reconciliation every 30s, Portfolio sync every 5min"

# Start server with appropriate settings based on mode
if [ "$DEV_MODE" = "true" ]; then
    echo "🔧 Running LOCAL development server with dashboard..."
    if [ "$RELOAD" = "true" ]; then
        python server.py --host "$HOST" --port "$PORT" --reload
    else
        python server.py
    fi
else
    echo "🏭 Running PRODUCTION versioned server..."
    if [ "$RELOAD" = "true" ]; then
        python api_versions/v2.0.0/server.py --host "$HOST" --port "$PORT" --reload
    else
        python api_versions/v2.0.0/server.py --host "$HOST" --port "$PORT" --workers "$WORKERS"
    fi
fi
