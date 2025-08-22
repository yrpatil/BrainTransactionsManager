## AI Agent Usage Guide

Purpose: Enable an AI agent to safely use BrainTransactionsManager to create/manage portfolios and perform read-only analysis. This guide covers both HTTP and MCP usage. Do not modify schemas or write directly to the database beyond the system’s own writes.

### 1) Start the server (bootstrap + health checks)

Use the launcher. It installs deps, ensures DB/schema/tables, and starts the server.

```bash
# stdio (for local MCP clients)
./start-server.sh TRANSPORT=stdio

# http (recommended for API-style use)
./start-server.sh TRANSPORT=http HOST=127.0.0.1 PORT=8000

# sse
./start-server.sh TRANSPORT=sse HOST=127.0.0.1 PORT=8001
```

Notes:
- If PORT is busy, the script auto-increments to the next free port and prints the final URL.
- Requires environment variables for broker access (e.g., ALPACA_API_KEY/ALPACA_SECRET_KEY via .env).

### 2) Capabilities (tools/resources)

MCP tools exposed by the server:
- buy_stock, sell_stock, execute_trade
- get_account_status, get_recent_orders, get_system_health
- activate_kill_switch, deactivate_kill_switch, get_kill_switch_status

MCP resources:
- account_info, current_positions, portfolio_summary

The system auto-reconciles order statuses and broker positions via internal polling helpers; the DB is updated by the app only.

### 3) Use over HTTP (simple JSON calls)

Assume server = http://127.0.0.1:8000/v1.0.0

Place buy order (paper by default):
```bash
curl -X POST \
  http://127.0.0.1:8000/v1.0.0/tools/buy_stock \
  -H 'Content-Type: application/json' \
  -d '{"ticker": "BTC/USD", "quantity": 0.001, "strategy_name": "agent_strategy"}'
```

Place sell order:
```bash
curl -X POST \
  http://127.0.0.1:8000/v1.0.0/tools/sell_stock \
  -H 'Content-Type: application/json' \
  -d '{"ticker": "BTC/USD", "quantity": 0.0005, "strategy_name": "agent_strategy"}'
```

Account status:
```bash
curl -X POST http://127.0.0.1:8000/v1.0.0/tools/get_account_status -H 'Content-Type: application/json' -d '{}'
```

Recent orders (limit N):
```bash
curl -X POST http://127.0.0.1:8000/v1.0.0/tools/get_recent_orders -H 'Content-Type: application/json' -d '{"limit": 10}'
```

Portfolio snapshot (DB-based):
```bash
curl -X GET http://127.0.0.1:8000/v1.0.0/resources/portfolio_summary
```

Kill switch (safety):
```bash
curl -X POST http://127.0.0.1:8000/v1.0.0/tools/activate_kill_switch \
  -H 'Content-Type: application/json' -d '{"reason": "emergency"}'
```

### 4) Python usage example

```python
import requests

BASE_URL = "http://127.0.0.1:8000/v1.0.0"

def get_account_status():
    r = requests.post(f"{BASE_URL}/tools/get_account_status", json={})
    r.raise_for_status()
    return r.json()
```

### 5) Market support

- US equities and Crypto are supported via Alpaca. Crypto requires `time_in_force=gtc` (handled automatically).
- Indian markets can be added by implementing a new adapter and registering it with the trading facade (not required for current usage).

### 6) Read-only database access for analysis

Read-only policy: Never change schemas or write data directly. Use SELECT queries only.

Connection (psql):
```bash
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME
```

Useful queries (schema: laxmiyantra):
```sql
-- Current positions
SELECT strategy_name, ticker, quantity, avg_entry_price, last_updated
FROM laxmiyantra.portfolio_positions
ORDER BY strategy_name, ticker;

-- Recent orders
SELECT order_id, strategy_name, ticker, side, order_type, quantity, status, submitted_at
FROM laxmiyantra.order_history
ORDER BY submitted_at DESC
LIMIT 50;

-- Transaction log (if enabled)
SELECT transaction_id, module_name, transaction_type, status, created_at
FROM laxmiyantra.transaction_log
ORDER BY created_at DESC
LIMIT 50;
```

Do not run DDL (CREATE/ALTER/DROP) or DML writes (INSERT/UPDATE/DELETE). All writes must go through the application.

### 7) Portfolio management pattern for agents

1. Place order (buy/sell)
2. Poll system health and recent orders until order status transitions to filled/cancelled
3. Read `portfolio_summary` (resource) to confirm DB reflects holdings
4. For crypto, prefer symbols like `BTC/USD`, `ETH/USD` (server sets correct TIF)
5. Use kill switch tool for emergency halt

### 8) Troubleshooting

- HTTP port busy: the launcher auto-picks the next free port and prints the final URL.
- Missing .env: provide ALPACA_API_KEY / ALPACA_SECRET_KEY.
- Database errors: ensure PostgreSQL is reachable and that the user has permissions. The launcher attempts to create DB/schema/tables.

### 9) Safety and compliance

- Treat all DB access as read-only unless routed through the app’s tools.
- Use kill switch on anomaly detection.
- Logging is enabled; avoid sending secrets over tool inputs.


