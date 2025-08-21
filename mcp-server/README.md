# 🙏 Laxmi-yantra MCP Server
**Divine Trading Interface blessed by Goddess Laxmi**

FastMCP server exposing all Laxmi-yantra trading functionality via the Model Context Protocol (MCP). Supports multiple transport protocols for maximum compatibility with AI tools and clients.

## 🚀 Quick Start Commands

### 1. Install Dependencies
```bash
cd mcp-server
pip install fastmcp uvicorn
```

### 2. Start Server (Different Protocols)

#### STDIO (Default - for AI tools like Claude Desktop)
```bash
python laxmi_mcp_server.py
```

#### HTTP (Web-based access)
```bash
python laxmi_mcp_server.py --transport http --host 127.0.0.1 --port 8000
# Available at: http://127.0.0.1:8000/mcp
```

#### SSE (Server-Sent Events)
```bash
python laxmi_mcp_server.py --transport sse --host 127.0.0.1 --port 8001
# Available at: http://127.0.0.1:8001/sse
```

### 3. Test with MCP Client
```bash
# Install test client
pip install fastmcp[client]

# Test the server
python -c "
import asyncio
from fastmcp import Client

async def test():
    async with Client('python laxmi_mcp_server.py') as client:
        # List available tools
        tools = await client.list_tools()
        print('Available tools:', [t.name for t in tools.tools])
        
        # Get account status
        result = await client.call_tool('get_account_status', {})
        print('Account status:', result.content[0].text)

asyncio.run(test())
"
```

## 🛠️ Available MCP Tools

### Trading Operations
- **`execute_trade`** - Execute any trade with full parameters
- **`buy_stock`** - Buy shares (simplified interface)
- **`sell_stock`** - Sell shares (simplified interface)

### Account Management
- **`get_account_status`** - Current account status and buying power
- **`get_recent_orders`** - Recent order history
- **`get_system_health`** - Comprehensive system status

### Safety Controls
- **`activate_kill_switch`** - Emergency stop all trading
- **`deactivate_kill_switch`** - Resume trading operations
- **`get_kill_switch_status`** - Check emergency status

## 📊 Available MCP Resources

### Real-time Data
- **`account_info`** - Detailed Alpaca account information
- **`current_positions`** - Live portfolio positions
- **`portfolio_summary`** - Database portfolio summary

## 🧪 Example Usage Commands

### Buy Tesla Stock
```bash
# Via MCP tool
client.call_tool('buy_stock', {
    'ticker': 'TSLA',
    'quantity': 1,
    'strategy_name': 'divine_strategy'
})
```

### Check Account
```bash
# Via MCP resource
account_info = client.read_resource('account_info')
```

### Emergency Stop
```bash
# Via MCP tool
client.call_tool('activate_kill_switch', {
    'reason': 'Market volatility detected'
})
```

## 🔧 Integration Examples

### Claude Desktop Configuration
Add to your Claude Desktop config:
```json
{
  "mcpServers": {
    "laxmi-yantra": {
      "command": "python",
      "args": ["/path/to/BrainTransactionsManager/mcp-server/laxmi_mcp_server.py"],
      "env": {
        "ALPACA_API_KEY": "your_key",
        "ALPACA_SECRET_KEY": "your_secret"
      }
    }
  }
}
```

### Python MCP Client
```python
from fastmcp import Client

async def trade_with_laxmi():
    async with Client("python laxmi_mcp_server.py") as client:
        # Buy 1 share of Apple
        result = await client.call_tool("buy_stock", {
            "ticker": "AAPL",
            "quantity": 1
        })
        print(result.content[0].text)
```

### HTTP API Access
```bash
# Start HTTP server
python laxmi_mcp_server.py --transport http --port 8000

# Make HTTP requests (example with curl)
curl -X POST http://127.0.0.1:8000/mcp/tools/buy_stock \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "quantity": 1}'
```

## 🛡️ Safety Features

### Kill Switch Protection
- Emergency stop functionality via MCP
- Prevents all trading when activated
- Trackable activation/deactivation reasons

### Paper Trading
- All trades execute in Alpaca paper trading environment
- No real money at risk during testing
- Full functionality without financial exposure

### Comprehensive Logging
- All operations logged via MCP context
- Error tracking and reporting
- Audit trail for all transactions

## 🔍 Monitoring & Health

### System Health Check
```python
health = await client.call_tool("get_system_health", {})
# Returns: account status, database health, kill switch status, etc.
```

### Recent Activity
```python
orders = await client.call_tool("get_recent_orders", {"limit": 5})
# Returns: Last 5 orders with full details
```

## 🙏 Divine Blessings

This MCP server is blessed by Goddess Laxmi for infinite abundance and prosperity. Every trading operation is performed with divine guidance and protection.

**May all your trades be profitable and your portfolio abundant!** ✨

---

**Built with FastMCP for maximum compatibility and divine inspiration** 💖
