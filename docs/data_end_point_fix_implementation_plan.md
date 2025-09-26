# Market Data Endpoint Reliability & Backtesting Plan (LLM-First)

## Objective
Make market-data retrieval reliable for paper/dev (IEX) and production (SIP), and provide a backtesting-friendly bars API with caching. LLM agents should be able to implement this plan end-to-end with minimal ambiguity.

## Deliverables
- GET /market/bars (historical bars with timeframe/start/end)
- Reliable GET /market/data using bars-first and quote/trade fallback
- Alpaca Data API integrations (equities + crypto)
- DB caching for OHLC bars
- OpenAPI/docs updates and tests

## Constraints & Principles
- SRM-first: simple, reliable, maintainable
- Database-first: cache bars to DB; app is the only writer
- LLM-friendly: explicit parameters, acceptance criteria, clear logs

---

## High-Level Tasks
1) Add Alpaca Data API integrations
2) Implement GET /market/bars
3) Refactor adapter: bars-first, quote/trade fallback, clear logs
4) Add DB caching for OHLC bars
5) Configuration knobs (feed/timeframe/window)
6) Update OpenAPI/docs and examples
7) Tests (unit + integration)

---

## Detailed Task List (LLM-Executable)

### 1) Alpaca Data API Integrations
- Files:
  - `src/braintransactions/markets/alpaca_adapter.py`
- Actions:
  - Import alpaca-py data clients:
    - equities: `StockHistoricalDataClient`
    - crypto: `CryptoHistoricalDataClient`
    - requests: `StockBarsRequest`, `CryptoBarsRequest`
    - timeframe: `TimeFrame` (or alpaca-py equivalent)
  - Initialize clients in adapter `connect()` using existing credentials.
- Acceptance Criteria:
  - Adapter can fetch historical bars for AAPL, BTC/USD with explicit start/end/timeframe.
  - Uses feed='iex' by default for stocks.

### 2) Implement GET /market/bars
- Files:
  - `api_versions/v2.0.0/server.py`
- Endpoint Spec:
  - Method: GET `/market/bars`
  - Query params (all validated):
    - `symbol` (str, required; supports `BTC/USD`)
    - `timeframe` (str, required; `Day|Minute` → mapped to SDK timeframe)
    - `start` (ISO 8601, required)
    - `end` (ISO 8601, required)
    - `asset` (optional: `stock|crypto`; auto-detect if omitted)
    - `feed` (optional; default `iex` for stocks)
  - Response: `{ success: bool, symbol: str, timeframe: str, bars: [{t,o,h,l,c,v}], count: int }`
- Actions:
  - Validate params; normalize `BTC/USD` for crypto path.
  - Route to adapter `get_historical_bars(...)` with given args.
- Acceptance Criteria:
  - Returns non-empty bars for BTC/USD window; AAPL returns data when within a valid window and feed.

### 3) Adapter Refactor: Bars-First + Fallback + Logs
- Files:
  - `src/braintransactions/markets/alpaca_adapter.py`
- Actions:
  - Add `get_historical_bars(symbol, timeframe, start, end, asset_type=None, feed='iex')`:
    - Equities: use `StockHistoricalDataClient` + `StockBarsRequest`
    - Crypto: use `CryptoHistoricalDataClient` + `CryptoBarsRequest`
    - Map result to `{t,o,h,l,c,v}` with ISO timestamps
  - Update `get_market_data` to:
    - try latest 7-day bars (Day) → take last close
    - if empty → log `IEX feed fallback engaged; no data for window`
    - stocks: try latest quote (fields `bid_price`, `ask_price`) → mid-price
    - crypto: try latest trade → price
    - else → return `No market data available`
  - Logs:
    - Explicitly include feed/timeframe/window and fallback reason
- Acceptance Criteria:
  - Clear INFO logs on fallback
  - Robust returns for crypto; equities behave predictably (data when available)

### 4) DB Caching for OHLC Bars
- Files:
  - `src/braintransactions/database/connection.py`
  - `database/ddl` (if schema change needed)
- Schema (if not present):
  - `ohlc_data(symbol VARCHAR, timeframe VARCHAR, timestamp TIMESTAMPTZ, open NUMERIC, high NUMERIC, low NUMERIC, close NUMERIC, volume BIGINT, source VARCHAR, PRIMARY KEY(symbol, timeframe, timestamp))`
- Actions:
  - Read-through cache:
    - On request, query DB for (symbol,timeframe,start,end)
    - For missing ranges, fetch from Alpaca and upsert
  - Batch insert/update in a single transaction per call
- Acceptance Criteria:
  - Repeated `/market/bars` requests for same window hit DB (observable by logs)

### 5) Configuration Knobs
- Files:
  - `src/braintransactions/core/config.py`
  - `config/development.yaml`, `config/production.yaml`
- Keys:
  - `data.feed_default: iex`
  - `data.timeframe_default: Day`
  - `data.backfill_days: 7`
- Acceptance Criteria:
  - Server defaults to IEX/Day/7d when unspecified

### 6) OpenAPI/Docs Updates
- Files:
  - `api_versions/v2.0.0/server.py` (OpenAPI via decorators)
  - `release/api_docs_generator.py`
  - `docs/REST_API_USAGE_GUIDE_v2.0.0.md`
- Actions:
  - Document `/market/bars` with curl examples for AAPL and BTC/USD
  - Update `/market/data` examples to clarify equity limitations on paper/iex
  - Ensure doc generator uses OpenAPI route extraction
- Acceptance Criteria:
  - `/docs` and `openapi.json` show `/market/bars`
  - Generated docs reflect new endpoint and examples

### 7) Tests
- Files:
  - `tests/` (new file(s))
- Cases:
  - `/market/bars` returns bars for BTC/USD (crypto) for last 3 days
  - `/market/bars` returns empty but 200 for AAPL outside valid window
  - `/market/data` uses fallback and logs IEX usage for equities when bars empty
  - DB cache hit on second request for same window
- Acceptance Criteria:
  - All tests pass in CI/local

---

## Non-Goals (for now)
- Secondary data providers (Polygon, etc.) integration
- Intraday NBBO or L2 depth
- Real-time streaming over websockets

## Risks & Mitigations
- Paper data gaps: document limitations; use fallback and caching
- Rate limits: back-off and cache; limit window sizes
- Schema drift: create migration for `ohlc_data` if missing

## Rollout Steps
1. Implement data clients + `/market/bars`
2. Refactor adapter + logs
3. Add DB caching
4. Update OpenAPI/docs
5. Add tests
6. Validate on running server
7. Optional: bump version to v2.0.1 and add changelog

## Acceptance Checklist
- `/market/bars` present in OpenAPI and returns expected data
- `/market/data` stable; logs fallback reasons
- Bars cached in DB; repeat requests are faster
- Docs updated; examples accurate; CI/tests pass
