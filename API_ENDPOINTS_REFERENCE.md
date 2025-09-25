# 🚀 BrainTransactionsManager v2.0.0 API Endpoints Reference
**Blessed by Goddess Laxmi for Infinite Abundance** 🙏

Complete reference for all available API endpoints with sample curl commands.

---

## 📋 **Quick Reference**

### **Base URL**: `http://localhost:8000`
### **API Documentation**: 
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 🏥 **Health & System Endpoints**

### **1. Basic Health Check**
```bash
curl -s http://localhost:8000/health | jq '.'
```
**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2025-01-27T10:00:00Z"
}
```

### **2. Detailed Health Check**
```bash
curl -s http://localhost:8000/health/detailed | jq '.'
```
**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "components": {
    "database": {
      "status": "healthy",
      "response_time_ms": 29.18,
      "active_connections": 0
    },
    "exchanges": {
      "adapters": {
        "alpaca": {
          "status": "healthy"
        }
      }
    },
    "monitoring": {
      "is_running": true,
      "total_tasks": 5,
      "active_tasks": 5
    }
  }
}
```

### **3. Configuration Status**
```bash
curl -s http://localhost:8000/config/status | jq '.'
```
**Response:**
```json
{
  "environment": "development",
  "config_file": "config/development.yaml",
  "database_configured": true,
  "alpaca_configured": true,
  "paper_trading": true,
  "timestamp": "2025-08-27T13:30:50.588484"
}
```

---

## 📊 **Market Data Endpoints**

### **4. Market Data for Stock**
```bash
curl -s http://localhost:8000/market/data/AAPL | jq '.'
```
**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "AAPL",
    "price": 175.43,
    "change": 2.15,
    "change_percent": 1.24,
    "volume": 45678900,
    "asset_type": "stock"
  }
}
```

### **5. Market Data for Crypto**
```bash
curl -s http://localhost:8000/market/data/BTCUSD | jq '.'
```
**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "BTCUSD",
    "price": 43250.75,
    "change": -1250.25,
    "change_percent": -2.81,
    "volume": 1234567.89,
    "asset_type": "crypto"
  }
}
```

### **6. Exchange Information**
```bash
curl -s http://localhost:8000/exchanges | jq '.'
```
**Response:**
```json
{
  "success": true,
  "exchanges": [
    {
      "name": "alpaca",
      "status": "connected",
      "supported_assets": ["stocks", "crypto"],
      "paper_trading": true
    }
  ]
}
```

---

## 💼 **Portfolio Endpoints**

### **7. Account Information**
```bash
curl -s http://localhost:8000/portfolio/account | jq '.'
```
**Response:**
```json
{
  "success": true,
  "account": {
    "account_id": "d1fadb28-640b-4134-913e-60067b65848f",
    "status": "ACTIVE",
    "buying_power": 155347.76,
    "cash": 64251.98,
    "portfolio_value": 101292.58,
    "equity": 101292.58,
    "day_trade_count": 0,
    "pattern_day_trader": true,
    "trading_blocked": false,
    "account_blocked": false,
    "transfers_blocked": false
  }
}
```

### **8. Portfolio Positions**
```bash
curl -s http://localhost:8000/portfolio/positions | jq '.'
```
**Response:**
```json
{
  "success": true,
  "positions": [
    {
      "symbol": "AAPL",
      "quantity": 31,
      "side": "long",
      "market_value": 7111.71,
      "cost_basis": 6999.51,
      "unrealized_pl": 112.20,
      "unrealized_plpc": 0.016,
      "avg_entry_price": 225.79,
      "asset_type": "stock",
      "strategy_name": "default"
    }
  ],
  "count": 12
}
```

### **9. Portfolio Summary**
```bash
curl -s http://localhost:8000/portfolio/summary | jq '.'
```
**Response:**
```json
{
  "success": true,
  "portfolio_summary": {
    "total_positions": 12,
    "total_market_value": 37040.60,
    "total_unrealized_pl": 1012.03,
    "account_cash": 64251.98,
    "account_buying_power": 155347.16,
    "portfolio_value": 101292.58,
    "asset_breakdown": {
      "stocks": {
        "count": 11,
        "market_value": 36652.13,
        "unrealized_pl": 1018.82
      },
      "crypto": {
        "count": 1,
        "market_value": 388.47,
        "unrealized_pl": -6.78
      }
    },
    "strategy_name": "all",
    "timestamp": "2025-08-27T13:31:36.232521"
  }
}
```

### **10. Strategy Portfolio**
```bash
curl -s http://localhost:8000/portfolio/strategy/default | jq '.'
```
**Response:**
```json
{
  "success": true,
  "strategy_summary": {
    "strategy_name": "default",
    "positions": {
      "total": 12,
      "market_value": 37045.87,
      "unrealized_pl": 1017.30
    },
    "orders": {
      "total": 5,
      "filled": 0,
      "pending": 5,
      "fill_rate": 0
    },
    "positions_detail": [...],
    "recent_orders": [...],
    "timestamp": "2025-08-27T13:33:44.487343"
  }
}
```

---

## 📈 **Order Management Endpoints**

### **11. Get Orders (Pending by Default)**
```bash
curl -s http://localhost:8000/orders | jq '.'
```
**Response:**
```json
{
  "success": true,
  "orders": [
    {
      "order_id": "cf22c722-52d5-4af4-8f94-5400cdc4e338",
      "client_order_id": "development-default-RGTI-a1b2c3d4e5f6",
      "symbol": "RGTI",
      "side": "buy",
      "quantity": 38,
      "filled_quantity": 0,
      "status": "pending",
      "order_type": "market",
      "submitted_at": "2025-08-27T11:16:35.712065398+00:00",
      "filled_at": null,
      "filled_avg_price": 0,
      "asset_type": "stock"
    }
  ],
  "count": 26
}
```

### **12. Get Specific Order**
```bash
curl -s http://localhost:8000/orders/cf22c722-52d5-4af4-8f94-5400cdc4e338 | jq '.'
```
**Response:**
```json
{
  "success": true,
  "order": {
    "order_id": "cf22c722-52d5-4af4-8f94-5400cdc4e338",
      "client_order_id": "development-default-RGTI-a1b2c3d4e5f6",
    "symbol": "RGTI",
    "side": "buy",
    "quantity": 38,
    "filled_quantity": 0,
    "status": "pending",
    "order_type": "market",
    "submitted_at": "2025-08-27T11:16:35.712065398+00:00",
    "filled_at": null,
    "filled_avg_price": 0,
    "asset_type": "stock"
  }
}
```

### **13. Order Statistics**
```bash
# (Removed) /orders/statistics – endpoint no longer available
```
**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_orders": 150,
    "filled_orders": 124,
    "pending_orders": 26,
    "cancelled_orders": 0,
    "fill_rate": 82.67,
    "average_fill_time_seconds": 45.2,
    "total_volume": 1250.5,
    "total_value": 125000.75,
    "by_asset_type": {
      "stocks": {
        "count": 140,
        "volume": 1200.0,
        "value": 120000.0
      },
      "crypto": {
        "count": 10,
        "volume": 50.5,
        "value": 5000.75
      }
    },
    "timestamp": "2025-08-27T13:35:00.000000"
  }
}
```

---

## 💰 **Trading Endpoints**

### **14. Buy Order**
```bash
curl -s -X POST http://localhost:8000/buy \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "quantity": 10,
    "strategy_name": "my_strategy",
    "order_type": "market",
    "price": null,
    "exchange": null
  }' | jq '.'
```
**Response:**
```json
{
  "success": true,
  "order_id": "bd547678-5369-4d69-bc8d-23fc5416cc41",
  "message": "Order placed successfully",
  "data": {
    "order_id": "bd547678-5369-4d69-bc8d-23fc5416cc41",
    "client_order_id": "development-my_strategy-AAPL-a1b2c3d4e5f6",
    "symbol": "AAPL",
    "side": "buy",
    "quantity": 10,
    "order_type": "market",
    "status": "pending",
    "submitted_at": "2025-08-27T11:32:58.048738236+00:00",
    "asset_type": "stock",
    "strategy_name": "my_strategy"
  }
}
```

### **15. Sell Order**
```bash
curl -s -X POST http://localhost:8000/sell \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "TSLA",
    "quantity": 5,
    "strategy_name": "my_strategy",
    "order_type": "limit",
    "price": 250.00,
    "exchange": null
  }' | jq '.'
```
**Response:**
```json
{
  "success": true,
  "order_id": "a1b2c3d4-5678-9abc-def0-123456789abc",
  "message": "Order placed successfully",
  "data": {
    "order_id": "a1b2c3d4-5678-9abc-def0-123456789abc",
    "client_order_id": "development-my_strategy-TSLA-a7b8c9d0e1f2",
    "symbol": "TSLA",
    "side": "sell",
    "quantity": 5,
    "order_type": "limit",
    "status": "pending",
    "submitted_at": "2025-08-27T11:33:00.123456789+00:00",
    "asset_type": "stock",
    "strategy_name": "my_strategy"
  }
}
```

### **16. Place Custom Order**
```bash
curl -s -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSD",
    "side": "buy",
    "order_type": "market",
    "quantity": 0.01,
    "price": null,
    "strategy_name": "crypto_strategy",
    "exchange": "alpaca"
  }' | jq '.'
```
**Response:**
```json
{
  "success": true,
  "order_id": "crypto123-4567-89ab-cdef-0123456789ab",
  "message": "Order placed successfully",
  "data": {
    "order_id": "crypto123-4567-89ab-cdef-0123456789ab",
    "client_order_id": "development-crypto_strategy-BTCUSD-b1c2d3e4f5a6",
    "symbol": "BTCUSD",
    "side": "buy",
    "quantity": 0.01,
    "order_type": "market",
    "status": "pending",
    "submitted_at": "2025-08-27T11:33:05.987654321+00:00",
    "asset_type": "crypto",
    "strategy_name": "crypto_strategy"
  }
}
```

---

## 🎯 **Position Management Endpoints**

### **17. Close Position**
```bash
curl -s -X POST http://localhost:8000/close/AAPL | jq '.'
```
**Response:**
```json
{
  "success": true,
  "message": "Position closed successfully",
  "order_id": "close123-4567-89ab-cdef-0123456789ab",
  "data": {
    "symbol": "AAPL",
    "quantity": 31,
    "side": "sell",
    "order_type": "market",
    "status": "pending",
    "submitted_at": "2025-08-27T11:35:00.000000000+00:00",
    "asset_type": "stock"
  }
}
```

### **18. Close All Positions**
```bash
curl -s -X POST http://localhost:8000/portfolio/close-all | jq '.'
```
**Response:**
```json
{
  "success": true,
  "message": "All positions closed successfully",
  "orders": [
    {
      "symbol": "AAPL",
      "order_id": "close_aapl_123",
      "status": "pending"
    },
    {
      "symbol": "TSLA",
      "order_id": "close_tsla_456",
      "status": "pending"
    }
  ],
  "total_positions": 12,
  "timestamp": "2025-08-27T11:36:00.000000"
}
```

---

## 🚨 **Emergency Control Endpoints**

### **19. Kill Switch Status**
```bash
curl -s http://localhost:8000/kill-switch/status | jq '.'
```
**Response:**
```json
{
  "success": true,
  "kill_switch_status": {
    "active": false,
    "reason": null,
    "timestamp": "2025-08-27T13:33:21.405735"
  }
}
```

### **20. Activate Kill Switch**
```bash
curl -s -X POST http://localhost:8000/kill-switch \
  -H "Content-Type: application/json" \
  -d '{
    "action": "activate",
    "reason": "Emergency stop - market volatility"
  }' | jq '.'
```
**Response:**
```json
{
  "success": true,
  "kill_switch": {
    "status": "activated",
    "reason": "Emergency stop - market volatility",
    "timestamp": "2025-08-27T13:33:32.740747"
  }
}
```

### **21. Deactivate Kill Switch**
```bash
curl -s -X POST http://localhost:8000/kill-switch \
  -H "Content-Type: application/json" \
  -d '{
    "action": "deactivate",
    "reason": "Market conditions normalized"
  }' | jq '.'
```
**Response:**
```json
{
  "success": true,
  "kill_switch": {
    "status": "deactivated",
    "timestamp": "2025-08-27T13:33:38.189524"
  }
}
```

### **22. Emergency Stop**
```bash
curl -s -X POST http://localhost:8000/emergency/stop \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Critical system error detected",
    "strategy_name": "all"
  }' | jq '.'
```
**Response:**
```json
{
  "success": true,
  "emergency_stop": {
    "status": "activated",
    "reason": "Critical system error detected",
    "timestamp": "2025-08-27T13:34:00.000000",
    "affected_strategies": ["all"],
    "actions_taken": [
      "Kill switch activated",
      "All pending orders cancelled",
      "Background monitoring stopped"
    ]
  }
}
```

---

## 🗄️ **Database Migration Endpoints**

### **23. Migration Status**
```bash
curl -s http://localhost:8000/migrations/status | jq '.'
```
**Response:**
```json
{
  "status": "valid",
  "current_revision": null,
  "pending_migrations": 0,
  "total_migrations": 0,
  "needs_migration": false,
  "timestamp": "2025-08-27T13:33:50.219753"
}
```

### **24. Run Migrations**
```bash
curl -s -X POST http://localhost:8000/migrations/run | jq '.'
```
**Response:**
```json
{
  "success": true,
  "message": "Migrations completed successfully",
  "migrations_run": 0,
  "current_revision": null,
  "timestamp": "2025-08-27T13:34:10.000000"
}
```

---

## 🧪 **Test Endpoints**

### **25. Test Orders**
```bash
curl -s http://localhost:8000/test/orders | jq '.'
```
**Response:**
```json
{
  "success": true,
  "status": "filled",
  "orders_count": 50,
  "orders": [
    {
      "order_id": "94499e45-b445-4521-9175-733191766305",
      "client_order_id": "357e05e2-a73f-45dc-b4a3-71a73106711a",
      "symbol": "RGTI",
      "side": "buy",
      "quantity": 38,
      "filled_quantity": 38,
      "status": "filled",
      "order_type": "market",
      "submitted_at": "2025-08-26T19:25:56.541290+00:00",
      "filled_at": "2025-08-26T19:25:57.061088+00:00",
      "filled_avg_price": 15.29,
      "asset_type": "stock"
    }
  ]
}
```

---

## 📚 **API Documentation**

### **26. Swagger UI**
```bash
# Open in browser: http://localhost:8000/docs
curl -s http://localhost:8000/docs | head -10
```

### **27. ReDoc**
```bash
# Open in browser: http://localhost:8000/redoc
curl -s http://localhost:8000/redoc | head -10
```

---

## 🎯 **Quick Reference Commands**

### **Health Check**
```bash
curl -s http://localhost:8000/health | jq '.status'
```

### **Account Balance**
```bash
curl -s http://localhost:8000/portfolio/account | jq '.account | {buying_power, portfolio_value, cash}'
```

### **Current Positions**
```bash
curl -s http://localhost:8000/portfolio/positions | jq '.positions | length'
```

### **Pending Orders**
```bash
curl -s http://localhost:8000/orders | jq '.orders | length'
```

### **Kill Switch Status**
```bash
curl -s http://localhost:8000/kill-switch/status | jq '.kill_switch_status.active'
```

---

## 🚀 **Usage Examples**

### **Quick Buy Order**
```bash
curl -s -X POST http://localhost:8000/buy \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "quantity": 1}' | jq '.success'
```

### **Check Portfolio Value**
```bash
curl -s http://localhost:8000/portfolio/summary | jq '.portfolio_summary.total_market_value'
```

### **Emergency Stop**
```bash
curl -s -X POST http://localhost:8000/kill-switch \
  -H "Content-Type: application/json" \
  -d '{"action": "activate", "reason": "Emergency"}' | jq '.success'
```

---

## 📝 **Notes**

- **Base URL**: All endpoints use `http://localhost:8000`
- **Authentication**: Currently using paper trading mode
- **Rate Limiting**: 1000 requests per hour
- **Response Format**: All responses are JSON
- **Error Handling**: Errors return appropriate HTTP status codes
- **Logging**: All requests are logged with sophisticated logging system

---

**🙏 Blessed by Goddess Laxmi for Infinite Abundance!**
