## 1.0.0 - Initial V1 Release

- REST + MCP hybrid server with FastAPI and JSON-RPC bridge
- Laxmi-yantra trading tools (buy, sell, execute_trade)
- Safety: kill switch tools and status
- Resources: account_info, current_positions, portfolio_summary, strategy_summary, system_health
- PnL fields added to summaries (unrealized_pl, unrealized_pl_pct, abs_*, totals)
- Background portfolio event poller (orders/positions) controlled via env
- Start script with defaults (HTTP:8888, MCP SSE:8889) and auto-port selection
- Database schema setup (TimescaleDB hypertable for ohlc_data)
- REST API usage guide with anonymized samples

