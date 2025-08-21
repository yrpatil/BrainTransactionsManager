## REST API Usage Guide

Purpose: Enable AI agents to use BrainTransactionsManager over simple HTTP (REST). This guide is concise, reliable, and copy-paste friendly. It mirrors the MCP capabilities with stable REST routes.

> Disclaimer: This document may become partially outdated at any time as the system evolves. Endpoints, fields, and example payloads are subject to change without notice. Treat examples as illustrative, and always validate against the live server responses.

### 1) Start the server (HTTP + background polling)

Use the launcher. It installs deps, ensures DB/schema/tables, and starts the REST server. Polling keeps DB in sync with the broker.

```bash
# Start HTTP server (recommended for API-style use)
./start-server.sh TRANSPORT=http HOST=127.0.0.1 PORT=8000 MCP_PATH=/mcp \
  PORTFOLIO_EVENT_POLLING_ENABLED=true PORTFOLIO_EVENT_POLLING_INTERVAL=5m

# Health
curl -s http://127.0.0.1:8000/health
```

Notes:
- The launcher auto-picks the next free port if the one you provide is busy and prints the final URL.
- Requires ALPACA_API_KEY / ALPACA_SECRET_KEY via .env or environment.
- Poller env vars:
  - `PORTFOLIO_EVENT_POLLING_ENABLED`: true|false (default true)
  - `PORTFOLIO_EVENT_POLLING_INTERVAL`: e.g., 5m, 30s, 1h (default 5m)

### 2) REST Endpoints Overview

Base: `http://127.0.0.1:8000`

- Health: `GET /health`
- Tools (actions): `POST /mcp/tools/{tool_name}` with JSON body
- Resources (read-only): `GET /mcp/resources/{resource_name}` (query params optional)

Errors:
- 200 OK on success
- 400 Bad Request for business/validation errors (e.g., insufficient position)
- 404 Not Found for unknown route/tool/resource
- 500 Internal Server Error for unexpected errors

### 3) Tools (POST)

- Buy stock (market):
```bash
curl -s -X POST http://127.0.0.1:8000/mcp/tools/buy_stock \
  -H 'Content-Type: application/json' \
  -d '{"ticker":"AAPL","quantity":1,"strategy_name":"agent_strategy"}'
```

- Buy stock (limit):
```bash
curl -s -X POST http://127.0.0.1:8000/mcp/tools/buy_stock \
  -H 'Content-Type: application/json' \
  -d '{"ticker":"AAPL","quantity":1,"strategy_name":"agent_strategy","order_type":"limit","price":175.25}'
```

- Sell stock (market):
```bash
curl -s -X POST http://127.0.0.1:8000/mcp/tools/sell_stock \
  -H 'Content-Type: application/json' \
  -d '{"ticker":"AAPL","quantity":1,"strategy_name":"agent_strategy"}'
```

- Execute trade (full control):
```bash
curl -s -X POST http://127.0.0.1:8000/mcp/tools/execute_trade \
  -H 'Content-Type: application/json' \
  -d '{"strategy_name":"agent_strategy","ticker":"AAPL","side":"buy","quantity":1,"order_type":"market"}'
```

- Account status:
```bash
curl -s -X POST http://127.0.0.1:8000/mcp/tools/get_account_status -H 'Content-Type: application/json' -d '{}'
```

- Recent orders:
```bash
curl -s -X POST http://127.0.0.1:8000/mcp/tools/get_recent_orders -H 'Content-Type: application/json' -d '{"limit": 20}'
```

- Kill switch (safety):
```bash
curl -s -X POST http://127.0.0.1:8000/mcp/tools/activate_kill_switch -H 'Content-Type: application/json' -d '{"reason":"emergency"}'
curl -s -X POST http://127.0.0.1:8000/mcp/tools/deactivate_kill_switch -H 'Content-Type: application/json' -d '{}'
curl -s -X POST http://127.0.0.1:8000/mcp/tools/get_kill_switch_status -H 'Content-Type: application/json' -d '{}'
```

Convenience GET aliases:
```bash
curl -s http://127.0.0.1:8000/mcp/tools/get_account_status
curl -s 'http://127.0.0.1:8000/mcp/tools/get_recent_orders?limit=10'
```

### 4) Resources (GET)

- Account info:
```bash
curl -s http://127.0.0.1:8000/mcp/resources/account_info
```

- Current positions (live from Alpaca):
```bash
curl -s http://127.0.0.1:8000/mcp/resources/current_positions
```

- Portfolio summary (DB snapshot; optional strategy filter):
```bash
curl -s http://127.0.0.1:8000/mcp/resources/portfolio_summary
curl -s 'http://127.0.0.1:8000/mcp/resources/portfolio_summary?strategy_name=default'
```

- Strategy summary (enriched, best for agents):
```bash
curl -s 'http://127.0.0.1:8000/mcp/resources/strategy_summary?strategy_name=default'
```

- System health:
```bash
curl -s http://127.0.0.1:8000/mcp/resources/system_health
```

### 5) Data Fields (PnL and valuation)

Per holding/position (portfolio_summary.positions[], strategy_summary.holdings[]):
- `current_price`: number (live quote if available)
- `cost_basis`: quantity × avg_entry_price
- `market_value`: quantity × current_price (fallback to avg price if no quote)
- `unrealized_pl`: market_value − cost_basis
- `unrealized_pl_pct`: (unrealized_pl / cost_basis) × 100 (0–100)
- `abs_unrealized_pl_pct`: absolute value of `unrealized_pl_pct`
- Aliases: `pln`, `pln_pct`, `abs_pln_pct`

Totals (portfolio_summary.totals, strategy_summary.totals):
- `total_cost_basis`, `total_market_value`
- `net_unrealized_pl`
- `net_unrealized_pl_pct` (0–100), `abs_net_unrealized_pl_pct`
- Aliases: `net_pln`, `net_pln_pct`, `abs_net_pln_pct`

### 6) Behavior, safety and errors

- Business rules return 400 with clear messages (e.g., insufficient position, invalid ticker/order type, missing limit price for limit orders).
- Unexpected errors return 500; logs provide context in `logs/braintransactions.log`.
- Paper trading by default; set credentials for Alpaca paper API. Live mode is not recommended without explicit review.
- Kill switch prevents all trading writes when active; read-only endpoints remain available.

### 7) Minimal agent workflow

1) Check health and account status
```bash
curl -s http://127.0.0.1:8000/health
curl -s -X POST http://127.0.0.1:8000/mcp/tools/get_account_status -H 'Content-Type: application/json' -d '{}'
```
2) Read state
```bash
curl -s http://127.0.0.1:8000/mcp/resources/portfolio_summary
curl -s 'http://127.0.0.1:8000/mcp/resources/strategy_summary?strategy_name=default'
```
3) Place order(s)
```bash
curl -s -X POST http://127.0.0.1:8000/mcp/tools/buy_stock -H 'Content-Type: application/json' \
  -d '{"ticker":"BTC/USD","quantity":0.001,"strategy_name":"agent_strategy"}'
```
4) Poll orders and positions via summaries (poller also keeps DB in sync)
```bash
curl -s -X POST http://127.0.0.1:8000/mcp/tools/get_recent_orders -H 'Content-Type: application/json' -d '{"limit": 10}'
curl -s 'http://127.0.0.1:8000/mcp/resources/strategy_summary?strategy_name=agent_strategy'
```

### 8) Troubleshooting

- 400 Insufficient position on sell → buy first or verify holdings via `strategy_summary`.
- 404 on /mcp → ensure `TRANSPORT=http` and `MCP_PATH=/mcp` were used to start, and you include the `/mcp` prefix.
- DB sync → ensure `PORTFOLIO_EVENT_POLLING_ENABLED=true`; check logs for “Order updated …” and “Position updated …”.
- Credentials → ensure `.env` contains Alpaca keys; verify startup logs show the paper endpoint.

### 9) Security & config

- Do not log secrets; provide via environment variables or .env (ignored by VCS).
- Centralized config at `src/braintransactions/core/config.py` validates required env.
- Poller env: `PORTFOLIO_EVENT_POLLING_ENABLED`, `PORTFOLIO_EVENT_POLLING_INTERVAL`.

---

This REST surface is designed for simplicity, reliability, and maintainability. Use summaries for high-level reasoning; use tools for actions.


### 10) Sample responses (for agents)

Disclaimer: These are representative, anonymized examples to help agents parse responses. Identifiers are masked and numeric values are illustrative only. Actual fields/values may vary at runtime based on market conditions, configuration, and future improvements.

- Tool: get_account_status
```json
{
  "account_status": "ACTIVE",
  "trading_blocked": false,
  "buying_power": 99750.23,
  "cash": 100000.00,
  "portfolio_value": 100250.75,
  "paper_trading": true
}
```

- Tool: get_recent_orders (limit=2)
```json
[
  {
    "order_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "client_order_id": "masked",
    "strategy_name": "agent_strategy",
    "ticker": "AAPL",
    "side": "buy",
    "order_type": "market",
    "quantity": 1.0,
    "filled_quantity": 1.0,
    "price": null,
    "filled_avg_price": 172.15,
    "status": "filled",
    "submitted_at": "2025-08-21T23:07:22.646589",
    "filled_at": "2025-08-21T23:07:22.900000",
    "canceled_at": null,
    "created_at": "2025-08-21T23:07:22.650000"
  },
  {
    "order_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "client_order_id": "masked",
    "strategy_name": "agent_strategy",
    "ticker": "BTC/USD",
    "side": "buy",
    "order_type": "market",
    "quantity": 0.001,
    "filled_quantity": 0.001,
    "price": null,
    "filled_avg_price": 60050.0,
    "status": "filled",
    "submitted_at": "2025-08-21T23:05:05.120000",
    "filled_at": "2025-08-21T23:05:05.300000",
    "canceled_at": null,
    "created_at": "2025-08-21T23:05:05.130000"
  }
]
```

- Resource: current_positions
```json
[
  {
    "symbol": "AAPL",
    "quantity": 30.0,
    "side": "long",
    "market_value": 5160.0,
    "avg_entry_price": 168.00,
    "unrealized_pl": 120.0,
    "unrealized_pl_pct": 2.38,
    "current_price": 172.0
  },
  {
    "symbol": "BTCUSD",
    "quantity": 0.00349125,
    "side": "long",
    "market_value": 210.0,
    "avg_entry_price": 60000.0,
    "unrealized_pl": -0.5,
    "unrealized_pl_pct": -0.24,
    "current_price": 60100.0
  }
]
```

- Resource: portfolio_summary (strategy filter optional)
```json
{
  "database_positions": 2,
  "positions": [
    {
      "strategy_name": "default",
      "ticker": "AAPL",
      "quantity": 30.0,
      "avg_entry_price": 168.0,
      "last_updated": "2025-08-21T23:55:40.878000",
      "created_at": "2025-08-20T12:00:00.000000",
      "current_price": 172.0,
      "cost_basis": 5040.0,
      "market_value": 5160.0,
      "unrealized_pl": 120.0,
      "unrealized_pl_pct": 2.38,
      "abs_unrealized_pl_pct": 2.38,
      "pln": 120.0,
      "pln_pct": 2.38,
      "abs_pln_pct": 2.38
    },
    {
      "strategy_name": "default",
      "ticker": "BTCUSD",
      "quantity": 0.00349125,
      "avg_entry_price": 60000.0,
      "last_updated": "2025-08-21T23:55:40.899000",
      "created_at": "2025-08-20T12:10:00.000000",
      "current_price": 60100.0,
      "cost_basis": 209.475,
      "market_value": 209.5575,
      "unrealized_pl": 0.0825,
      "unrealized_pl_pct": 0.0394,
      "abs_unrealized_pl_pct": 0.0394,
      "pln": 0.0825,
      "pln_pct": 0.0394,
      "abs_pln_pct": 0.0394
    }
  ],
  "totals": {
    "total_positions": 2,
    "total_quantity": 30.00349125,
    "total_cost_basis": 5249.475,
    "total_market_value": 5369.5575,
    "net_unrealized_pl": 120.0825,
    "net_unrealized_pl_pct": 2.29,
    "abs_net_unrealized_pl_pct": 2.29,
    "net_pln": 120.0825,
    "net_pln_pct": 2.29,
    "abs_net_pln_pct": 2.29
  }
}
```

- Resource: strategy_summary
```json
{
  "strategy_name": "default",
  "total_positions": 2,
  "total_quantity": 30.00349125,
  "avg_entry_price": 0.0,
  "last_position_update": "2025-08-21T23:55:40.908000",
  "pending_orders": 0,
  "filled_orders": 4,
  "cancelled_orders": 0,
  "total_orders": 4,
  "last_order_time": "2025-08-21T23:07:22.646589",
  "fills_24h": 0,
  "holdings": [
    { "ticker": "AAPL", "quantity": 30.0, "avg_entry_price": 168.0, "current_price": 172.0,
      "cost_basis": 5040.0, "market_value": 5160.0, "unrealized_pl": 120.0, "unrealized_pl_pct": 2.38,
      "abs_unrealized_pl_pct": 2.38, "pln": 120.0, "pln_pct": 2.38, "abs_pln_pct": 2.38 },
    { "ticker": "BTCUSD", "quantity": 0.00349125, "avg_entry_price": 60000.0, "current_price": 60100.0,
      "cost_basis": 209.475, "market_value": 209.5575, "unrealized_pl": 0.0825, "unrealized_pl_pct": 0.0394,
      "abs_unrealized_pl_pct": 0.0394, "pln": 0.0825, "pln_pct": 0.0394, "abs_pln_pct": 0.0394 }
  ],
  "totals": {
    "total_positions": 2,
    "total_quantity": 30.00349125,
    "total_cost_basis": 5249.475,
    "total_market_value": 5369.5575,
    "net_unrealized_pl": 120.0825,
    "net_unrealized_pl_pct": 2.29,
    "abs_net_unrealized_pl_pct": 2.29,
    "net_pln": 120.0825,
    "net_pln_pct": 2.29,
    "abs_net_pln_pct": 2.29
  },
  "timestamp": "2025-08-21T23:44:42.865575"
}
```

- Resource: system_health
```json
{
  "account_status": "ACTIVE",
  "trading_blocked": false,
  "kill_switch_active": false,
  "database_healthy": true,
  "paper_trading": true,
  "alpaca_connected": true,
  "buying_power": 99750.23,
  "cash": 100000.0
}
```