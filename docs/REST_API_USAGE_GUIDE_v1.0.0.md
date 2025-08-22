# Laxmi-yantra Trading API v1.0.0 - AI Agent Usage Guide

**🎯 Purpose**: Complete guide for AI agents to optimally use the Laxmi-yantra Trading API v1.0.0
**📅 Release Date**: 2025-08-22
**🔄 Status**: Stable
**🤖 Optimized for**: AI Agents, Automated Trading, Algorithmic Systems



> **Disclaimer**: This documentation is version-specific for v1.0.0. 
> Endpoints, fields, and behaviors may differ between API versions. 
> Always verify against live server responses for the most accurate information.

## Quick Navigation
- [🚀 Quick Start](#quick-start)
- [📋 Endpoints Reference](#endpoints-reference)  
- [🤖 AI Agent Examples](#ai-agent-examples)
- [⚠️ Error Handling](#error-handling)
- [💡 Best Practices](#best-practices)
- [🔧 Troubleshooting](#troubleshooting)
- [📊 Response Samples](#response-samples)


## 🚀 Quick Start

### 1. Start the Server
```bash
# Start HTTP server with version support
./start-server.sh TRANSPORT=http HOST=127.0.0.1 PORT=8000 \
  PORTFOLIO_EVENT_POLLING_ENABLED=true PORTFOLIO_EVENT_POLLING_INTERVAL=5m

# Verify server is running
curl -s http://127.0.0.1:8000/health
```

### 2. Check API Version Support
```bash
# List all available versions
curl -s http://127.0.0.1:8000/versions

# Check specific version health
curl -s http://127.0.0.1:8000/v1.0.0/health
```

### 3. Basic Authentication Test
```bash
# Verify account access
curl -s -X POST http://127.0.0.1:8000/v1.0.0/tools/get_account_status \
  -H 'Content-Type: application/json' -d '{}'
```

### 4. First Trading Action
```bash
# Get current portfolio state
curl -s http://127.0.0.1:8000/v1.0.0/resources/portfolio_summary

# Execute a small test trade
curl -s -X POST http://127.0.0.1:8000/v1.0.0/tools/buy_stock \
  -H 'Content-Type: application/json' \
  -d '{"ticker":"AAPL","quantity":1,"strategy_name":"test_strategy"}'
```

### Base URL Structure
All endpoints use the pattern: `http://127.0.0.1:8000/v1.0.0/{endpoint_type}/{endpoint_name}`

- **Tools** (Actions): `POST /v1.0.0/tools/{tool_name}`
- **Resources** (Data): `GET /v1.0.0/resources/{resource_name}`
- **Health**: `GET /v1.0.0/health`


## 📋 Endpoints Reference

### Tools (POST - Actions)


### Resources (GET - Data Retrieval)  

#### `GET /v1.0.0/resources/laxmi://account_info`
**Description**: Get laxmi://account_info information
**Query Parameters**: None

```bash
curl -s http://127.0.0.1:8000/v1.0.0/resources/laxmi://account_info
```


#### `GET /v1.0.0/resources/laxmi://current_positions`
**Description**: Get laxmi://current_positions information
**Query Parameters**: None

```bash
curl -s http://127.0.0.1:8000/v1.0.0/resources/laxmi://current_positions
```


#### `GET /v1.0.0/resources/laxmi://portfolio_summary`
**Description**: Get laxmi://portfolio_summary information
**Query Parameters**: None

```bash
curl -s http://127.0.0.1:8000/v1.0.0/resources/laxmi://portfolio_summary
```


#### `GET /v1.0.0/resources/laxmi://system_health`
**Description**: Get laxmi://system_health information
**Query Parameters**: None

```bash
curl -s http://127.0.0.1:8000/v1.0.0/resources/laxmi://system_health
```


### System Endpoints
- `GET /v1.0.0/health` - Version-specific health check
- `GET /health` - Global multi-version health check
- `GET /versions` - List all available API versions
- `GET /` - API information and navigation


## 🤖 AI Agent Examples

### Complete Trading Workflow
```bash
#!/bin/bash
# AI Agent Trading Workflow for API v1.0.0

BASE_URL="http://127.0.0.1:8000/v1.0.0"

# 1. Health and connectivity check
echo "Checking system health..."
curl -s "$BASE_URL/health" | jq .

# 2. Verify account access and status
echo "Getting account status..."
ACCOUNT=$(curl -s -X POST "$BASE_URL/tools/get_account_status" \
  -H 'Content-Type: application/json' -d '{}')
echo $ACCOUNT | jq .

# 3. Get current portfolio state
echo "Checking portfolio..."
PORTFOLIO=$(curl -s "$BASE_URL/resources/portfolio_summary")
echo $PORTFOLIO | jq .

# 4. Analyze specific strategy performance
echo "Strategy analysis..."
STRATEGY=$(curl -s "$BASE_URL/resources/strategy_summary?strategy_name=ai_agent")
echo $STRATEGY | jq .

# 5. Execute trade based on analysis
echo "Executing trade..."
TRADE_RESULT=$(curl -s -X POST "$BASE_URL/tools/buy_stock" \
  -H 'Content-Type: application/json' \
  -d '{"ticker":"AAPL","quantity":1,"strategy_name":"ai_agent","order_type":"market"}')
echo $TRADE_RESULT | jq .

# 6. Monitor order status
echo "Checking recent orders..."
ORDERS=$(curl -s -X POST "$BASE_URL/tools/get_recent_orders" \
  -H 'Content-Type: application/json' -d '{"limit":5}')
echo $ORDERS | jq .
```

### AI Decision Making Pattern
```python
import requests
import json

class LaxmiYantraAgent:
    def __init__(self, base_url="http://127.0.0.1:8000/v1.0.0"):
        self.base_url = base_url
        self.strategy_name = "ai_agent"
        
    def health_check(self):
        """Verify system is healthy before trading."""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
        
    def get_portfolio_state(self):
        """Get comprehensive portfolio analysis."""
        url = f"{self.base_url}/resources/strategy_summary"
        params = {"strategy_name": self.strategy_name}
        response = requests.get(url, params=params)
        return response.json()
        
    def execute_trade_decision(self, ticker, side, quantity):
        """Execute trading decision with proper error handling."""
        url = f"{self.base_url}/tools/execute_trade"
        payload = {
            "strategy_name": self.strategy_name,
            "ticker": ticker,
            "side": side,
            "quantity": quantity,
            "order_type": "market"
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 400:
                # Business logic error - handle gracefully
                error_info = response.json()
                print(f"Trading error: {error_info.get('error', 'Unknown error')}")
                return None
            else:
                raise
                
    def monitor_positions(self):
        """Monitor position performance with PnL analysis."""
        portfolio = self.get_portfolio_state()
        
        for holding in portfolio.get('holdings', []):
            pnl_pct = holding.get('unrealized_pl_pct', 0)
            print(f"{holding['ticker']}: {pnl_pct:.2f}% PnL")
            
            # Example: Simple stop-loss at -5%
            if pnl_pct < -5.0:
                print(f"Stop-loss triggered for {holding['ticker']}")
                self.execute_trade_decision(
                    holding['ticker'], 
                    'sell', 
                    holding['quantity']
                )

# Usage
agent = LaxmiYantraAgent()
if agent.health_check()['status'] == 'healthy':
    portfolio = agent.get_portfolio_state()
    agent.monitor_positions()
```

### Risk Management Pattern
```bash
# Emergency procedures for AI agents
BASE_URL="http://127.0.0.1:8000/v1.0.0"

# 1. Check kill switch status before any trades
KILL_STATUS=$(curl -s -X POST "$BASE_URL/tools/get_kill_switch_status" \
  -H 'Content-Type: application/json' -d '{}')
echo "Kill switch status: $KILL_STATUS"

# 2. Activate emergency stop if needed
if [ "$EMERGENCY_DETECTED" = "true" ]; then
  curl -s -X POST "$BASE_URL/tools/activate_kill_switch" \
    -H 'Content-Type: application/json' \
    -d '{"reason":"AI agent detected market anomaly"}'
fi

# 3. Portfolio risk check
PORTFOLIO=$(curl -s "$BASE_URL/resources/portfolio_summary")
NET_PNL=$(echo $PORTFOLIO | jq '.totals.net_unrealized_pl_pct')

# Activate kill switch if portfolio loss > 10%
if (( $(echo "$NET_PNL < -10" | bc -l) )); then
  curl -s -X POST "$BASE_URL/tools/activate_kill_switch" \
    -H 'Content-Type: application/json' \
    -d '{"reason":"Portfolio loss limit exceeded"}'
fi
```


## ⚠️ Error Handling

### HTTP Status Codes
- **200 OK**: Successful operation
- **400 Bad Request**: Business logic errors (insufficient funds, invalid parameters)
- **404 Not Found**: Endpoint or resource not found
- **406 Not Acceptable**: Content negotiation failed
- **500 Internal Server Error**: Unexpected server errors

### Error Response Format
```json
{
  "error": "Descriptive error message",
  "details": "Additional context when available",
  "timestamp": "2025-01-21T12:00:00Z",
  "version": "v1.0.0"
}
```

### Common Business Errors (400)
```bash
# Insufficient position for sell
curl -s -X POST http://127.0.0.1:8000/v1.0.0/tools/sell_stock \
  -H 'Content-Type: application/json' \
  -d '{"ticker":"AAPL","quantity":1000,"strategy_name":"test"}'
# Response: {"error": "Insufficient position. Current: 0, Requested: 1000"}

# Invalid ticker
curl -s -X POST http://127.0.0.1:8000/v1.0.0/tools/buy_stock \
  -H 'Content-Type: application/json' \
  -d '{"ticker":"INVALID","quantity":1,"strategy_name":"test"}'
# Response: {"error": "Invalid ticker symbol: INVALID"}

# Missing required parameter
curl -s -X POST http://127.0.0.1:8000/v1.0.0/tools/buy_stock \
  -H 'Content-Type: application/json' \
  -d '{"ticker":"AAPL","quantity":1}'
# Response: {"error": "Missing required parameter: strategy_name"}
```

### Kill Switch Errors
```bash
# Trading when kill switch is active
curl -s -X POST http://127.0.0.1:8000/v1.0.0/tools/buy_stock \
  -H 'Content-Type: application/json' \
  -d '{"ticker":"AAPL","quantity":1,"strategy_name":"test"}'
# Response: {"error": "Trading is currently disabled due to active kill switch"}
```

### AI Agent Error Handling Pattern
```python
def safe_api_call(url, method='GET', **kwargs):
    """Safe API call with comprehensive error handling."""
    try:
        if method == 'GET':
            response = requests.get(url, **kwargs)
        else:
            response = requests.post(url, **kwargs)
            
        response.raise_for_status()
        return response.json(), None
        
    except requests.exceptions.HTTPError as e:
        if response.status_code == 400:
            # Business logic error - recoverable
            error_info = response.json()
            return None, f"Business error: {error_info.get('error')}"
        elif response.status_code == 404:
            return None, "Endpoint not found - check API version"
        elif response.status_code == 500:
            return None, "Server error - retry later"
        else:
            return None, f"HTTP error {response.status_code}: {e}"
            
    except requests.exceptions.ConnectionError:
        return None, "Connection failed - check if server is running"
    except requests.exceptions.Timeout:
        return None, "Request timeout - server may be overloaded"
    except Exception as e:
        return None, f"Unexpected error: {e}"

# Usage in AI agent
result, error = safe_api_call(f"{base_url}/tools/buy_stock", 
                             method='POST', 
                             json=trade_params)
if error:
    logger.warning(f"Trade failed: {error}")
    # Implement retry logic or alternative strategy
else:
    logger.info(f"Trade successful: {result}")
```


## 💡 Best Practices for AI Agents

### 1. Always Check Health First
```bash
# Never start trading without health verification
curl -s http://127.0.0.1:8000/v1.0.0/health
```

### 2. Use Strategy-Specific Operations
```bash
# Always specify strategy_name for tracking and risk management
STRATEGY="ai_agent_$(date +%Y%m%d)"
curl -s -X POST http://127.0.0.1:8000/v1.0.0/tools/buy_stock \
  -d '{"ticker":"AAPL","quantity":1,"strategy_name":"'$STRATEGY'"}'
```

### 3. Monitor Portfolio State Continuously
```bash
# Get comprehensive strategy analytics before major decisions
curl -s "http://127.0.0.1:8000/v1.0.0/resources/strategy_summary?strategy_name=$STRATEGY"
```

### 4. Implement Position Sizing
```python
def calculate_position_size(portfolio_value, risk_per_trade=0.02):
    """Calculate position size based on portfolio value and risk tolerance."""
    max_risk_amount = portfolio_value * risk_per_trade
    # Additional position sizing logic...
    return position_size
```

### 5. Use Limit Orders for Better Control
```bash
# Prefer limit orders over market orders for better price control
curl -s -X POST http://127.0.0.1:8000/v1.0.0/tools/buy_stock \
  -d '{
    "ticker": "AAPL",
    "quantity": 10,
    "strategy_name": "ai_agent",
    "order_type": "limit",
    "price": 175.50
  }'
```

### 6. Implement Circuit Breakers
```python
class TradingCircuitBreaker:
    def __init__(self, max_daily_loss_pct=5.0):
        self.max_daily_loss_pct = max_daily_loss_pct
        self.start_of_day_value = None
        
    def check_daily_loss_limit(self, current_portfolio_value):
        if self.start_of_day_value is None:
            self.start_of_day_value = current_portfolio_value
            return False
            
        daily_loss_pct = ((current_portfolio_value - self.start_of_day_value) 
                         / self.start_of_day_value) * 100
                         
        return daily_loss_pct < -self.max_daily_loss_pct
```

### 7. Handle Rate Limiting Gracefully
```python
import time
import random

def api_call_with_backoff(func, max_retries=3):
    """API call with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limited
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
            else:
                raise
    raise Exception(f"Max retries ({max_retries}) exceeded")
```

### 8. Log All Trading Decisions
```python
import logging

trading_logger = logging.getLogger('ai_trading')
trading_logger.setLevel(logging.INFO)

def log_trade_decision(action, ticker, quantity, reasoning):
    trading_logger.info(f"TRADE_DECISION: {action} {quantity} {ticker} - {reasoning}")

# Usage
log_trade_decision("BUY", "AAPL", 10, "Technical breakout above resistance")
```

### 9. Validate Market Hours
```python
from datetime import datetime
import pytz

def is_market_open():
    """Check if market is currently open."""
    now = datetime.now(pytz.timezone('US/Eastern'))
    weekday = now.weekday()
    
    # Monday = 0, Sunday = 6
    if weekday >= 5:  # Weekend
        return False
        
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    return market_open <= now <= market_close

# Only trade during market hours
if is_market_open():
    # Execute trading logic
    pass
```

### 10. Implement Emergency Procedures
```bash
# Emergency kill switch activation
emergency_stop() {
  curl -s -X POST http://127.0.0.1:8000/v1.0.0/tools/activate_kill_switch \
    -H 'Content-Type: application/json' \
    -d '{"reason":"AI agent emergency stop - unusual market conditions"}'
}

# Call during market anomalies or system errors
```


## 🔧 Troubleshooting

### Connection Issues
```bash
# Test basic connectivity
curl -s http://127.0.0.1:8000/health
# Expected: {"status": "healthy", ...}

# Test version-specific endpoint
curl -s http://127.0.0.1:8000/v1.0.0/health
# Expected: Version-specific health data
```

### Authentication Issues
```bash
# Check if credentials are loaded
curl -s -X POST http://127.0.0.1:8000/v1.0.0/tools/get_account_status \
  -H 'Content-Type: application/json' -d '{}'
# Look for "ALPACA_API_KEY not found" or similar errors
```

### Trading Issues
```bash
# Check kill switch status
curl -s -X POST http://127.0.0.1:8000/v1.0.0/tools/get_kill_switch_status \
  -H 'Content-Type: application/json' -d '{}'

# Verify account has buying power
curl -s http://127.0.0.1:8000/v1.0.0/resources/account_info
```

### Version Issues
```bash
# List all available versions
curl -s http://127.0.0.1:8000/versions

# Check if your version is active
curl -s http://127.0.0.1:8000/versions | jq '.active_versions[]' | grep "v1.0.0"
```

### Database Sync Issues
```bash
# Check if background polling is enabled
# Look for "PORTFOLIO_EVENT_POLLING_ENABLED=true" in logs

# Compare broker vs database positions
curl -s http://127.0.0.1:8000/v1.0.0/resources/current_positions > broker_positions.json
curl -s http://127.0.0.1:8000/v1.0.0/resources/portfolio_summary > db_positions.json
```

### Common Error Solutions

#### "404 Not Found"
- Verify API version is correct and active
- Check endpoint spelling and method (GET vs POST)
- Ensure server is running on correct port

#### "400 Bad Request: Insufficient position"
```bash
# Check current holdings before selling
curl -s "http://127.0.0.1:8000/v1.0.0/resources/strategy_summary?strategy_name=your_strategy"
```

#### "500 Internal Server Error"
- Check server logs: `tail -f logs/braintransactions.log`
- Verify database connectivity
- Restart server if needed

#### Rate Limiting (429)
- Implement exponential backoff
- Reduce request frequency
- Use batch operations where possible

### Debug Mode
```bash
# Start server with debug logging
DEBUG=true ./start-server.sh

# Check detailed logs
tail -f logs/braintransactions.log | grep -i error
```

### Health Check Diagnostics
```bash
# Comprehensive health check script
#!/bin/bash
echo "=== Laxmi-yantra API v1.0.0 Diagnostics ==="

echo "1. Basic connectivity..."
curl -s http://127.0.0.1:8000/health | jq .

echo "2. Version health..."
curl -s http://127.0.0.1:8000/v1.0.0/health | jq .

echo "3. Account status..."
curl -s -X POST http://127.0.0.1:8000/v1.0.0/tools/get_account_status \
  -H 'Content-Type: application/json' -d '{}' | jq .

echo "4. Kill switch status..."
curl -s -X POST http://127.0.0.1:8000/v1.0.0/tools/get_kill_switch_status \
  -H 'Content-Type: application/json' -d '{}' | jq .

echo "5. Recent orders..."
curl -s -X POST http://127.0.0.1:8000/v1.0.0/tools/get_recent_orders \
  -H 'Content-Type: application/json' -d '{"limit":5}' | jq .

echo "=== Diagnostics Complete ==="
```


## 📊 Response Samples

> **Note**: These samples are specific to API v1.0.0. Field names, values, and structure may vary between versions.



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

---

**🙏 Generated on 2025-08-22 10:27:00 - Blessed by Goddess Laxmi for Infinite Abundance**
