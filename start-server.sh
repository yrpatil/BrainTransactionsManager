#!/usr/bin/env bash
set -euo pipefail

# BrainTransactionsManager bootstrap and server launcher
# - Creates Python venv and installs requirements
# - Ensures PostgreSQL is running and schema is present
# - Starts the Laxmi-yantra MCP server
# Keep this script up-to-date with any future setup changes

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Configurable via env (defaults shown)
: "${PYTHON:=python3}"
: "${VENV_DIR:=.venv}"
: "${TRANSPORT:=http}"
: "${HOST:=127.0.0.1}"
: "${MCP_PATH:=/mcp}"
: "${HTTP_PORT:=8888}"
: "${MCP_PORT:=8889}"
: "${PORTFOLIO_EVENT_POLLING_ENABLED:=true}"
: "${PORTFOLIO_EVENT_POLLING_INTERVAL:=5m}"
: "${DB_NAME:=braintransactions}"
: "${DB_HOST:=localhost}"
: "${DB_PORT:=5432}"
: "${DB_USER:=$(whoami)}"
: "${DB_SCHEMA:=laxmiyantra}"

echo "[1/5] Checking Python and virtual environment..."
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "Error: $PYTHON not found. Please install Python 3." >&2
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  "$PYTHON" -m venv "$VENV_DIR"
fi
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip >/dev/null

echo "[2/5] Installing Python dependencies..."
if [ -f "$ROOT_DIR/requirements.txt" ]; then
  pip install -r "$ROOT_DIR/requirements.txt"
fi
if [ -f "$ROOT_DIR/mcp-server/requirements.txt" ]; then
  pip install -r "$ROOT_DIR/mcp-server/requirements.txt"
fi

echo "[3/5] Ensuring PostgreSQL is running..."
if ! command -v psql >/dev/null 2>&1; then
  echo "Warning: psql not found. Skipping DB start; ensure PostgreSQL is available at $DB_HOST:$DB_PORT." >&2
else
  # Quick ping
  if ! PGPASSWORD="${DB_PASSWORD:-}" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "SELECT 1;" >/dev/null 2>&1; then
    # macOS Homebrew attempt
    if command -v brew >/dev/null 2>&1 && brew list | grep -q "postgresql@"; then
      echo "Trying to start PostgreSQL via Homebrew..."
      brew services start postgresql@17 >/dev/null 2>&1 || true
      sleep 2
    else
      echo "Warning: Could not verify/start PostgreSQL. Proceeding; DB steps may fail." >&2
    fi
  fi
fi

echo "[4/5] Ensuring database and schema exist..."
if command -v psql >/dev/null 2>&1; then
  # Create DB if missing
  DB_EXISTS=$(PGPASSWORD="${DB_PASSWORD:-}" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME';" || echo "")
  if [ "$DB_EXISTS" != "1" ]; then
    echo "Creating database $DB_NAME..."
    PGPASSWORD="${DB_PASSWORD:-}" createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" || true
  fi
  # Enable TimescaleDB if available (ignore failures)
  PGPASSWORD="${DB_PASSWORD:-}" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS timescaledb;" >/dev/null 2>&1 || true
  # Run full setup DDL if present
  if [ -f "$ROOT_DIR/database/ddl/setup_complete.sql" ]; then
    echo "Applying schema DDL..."
    PGPASSWORD="${DB_PASSWORD:-}" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$ROOT_DIR/database/ddl/setup_complete.sql" >/dev/null || true
  fi
  # Create schema if still missing
  PGPASSWORD="${DB_PASSWORD:-}" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "CREATE SCHEMA IF NOT EXISTS $DB_SCHEMA;" >/dev/null || true
fi

echo "[5/5] Verifying application prerequisites..."

# .env presence (non-fatal)
if [ ! -f "$ROOT_DIR/.env" ]; then
  echo "Warning: .env not found at project root. Ensure required env vars (e.g., ALPACA keys) are set."
fi

# Ensure required tables exist via application layer (respects schema/search_path)
echo "Ensuring application tables (via DatabaseManager)..."
PYTHONPATH="$ROOT_DIR/src" "$VENV_DIR/bin/python" - <<'PY' >/dev/null 2>&1 || true
from braintransactions.database.connection import DatabaseManager
from braintransactions.core.config import BrainConfig
db = DatabaseManager(BrainConfig())
db.create_tables()
PY

echo "Launching MCP server ($TRANSPORT)..."
export PYTHONPATH="$ROOT_DIR/src"
export TRANSPORT
export HOST
export PORTFOLIO_EVENT_POLLING_ENABLED
export PORTFOLIO_EVENT_POLLING_INTERVAL

# Select default port by transport if PORT not explicitly provided
if [ -z "${PORT:-}" ]; then
  if [ "$TRANSPORT" = "http" ]; then
    PORT="$HTTP_PORT"
  elif [ "$TRANSPORT" = "sse" ]; then
    PORT="$MCP_PORT"
  fi
fi

# Auto-pick free port for HTTP/SSE if requested port is in use
if [ "$TRANSPORT" != "stdio" ]; then
  if command -v lsof >/dev/null 2>&1; then
    TRY_PORT="$PORT"
    for i in $(seq 0 20); do
      if lsof -iTCP:"$TRY_PORT" -sTCP:LISTEN -P -n >/dev/null 2>&1; then
        TRY_PORT=$((TRY_PORT+1))
      else
        break
      fi
    done
    if [ "$TRY_PORT" != "$PORT" ]; then
      echo "Port $PORT is in use. Switching to $TRY_PORT."
      PORT="$TRY_PORT"
    fi
  fi
fi

CMD=("$VENV_DIR/bin/python" "$ROOT_DIR/mcp-server/laxmi_mcp_server.py")
case "$TRANSPORT" in
  stdio)
    echo "Running MCP server (stdio)..."
    exec "${CMD[@]}" --transport stdio
    ;;
  http)
    echo "Server: http://$HOST:$PORT$MCP_PATH"
    exec "${CMD[@]}" --transport http --host "$HOST" --port "$PORT" --path "$MCP_PATH"
    ;;
  sse)
    echo "Server (SSE): http://$HOST:$PORT/sse"
    exec "${CMD[@]}" --transport sse --host "$HOST" --port "$PORT"
    ;;
  *)
    echo "Unknown TRANSPORT='$TRANSPORT' (use stdio|http|sse)" >&2
    exit 1
    ;;
esac


