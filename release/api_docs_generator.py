#!/usr/bin/env python3
"""
🙏 API Documentation Generator
Blessed by Goddess Laxmi for Infinite Abundance

Generates version-specific API documentation optimized for AI agents.
Creates comprehensive usage guides with examples and best practices.
"""

import os
import json
import logging
import inspect
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import importlib.util

logger = logging.getLogger(__name__)

class APIDocsGenerator:
    """Generates version-specific API documentation for AI agents."""
    
    def __init__(self, base_path: str = "."):
        """Initialize API documentation generator."""
        self.base_path = Path(base_path)
        self.config_path = self.base_path / "config" / "api_versions.json"
        self.template_path = self.base_path / "docs" / "REST_API_USAGE_GUIDE.md"
        
    def generate_version_docs(self, version: str) -> str:
        """
        Generate comprehensive API documentation for a specific version.
        
        Args:
            version: API version (e.g., 'v1.0.0')
            
        Returns:
            Formatted documentation in Markdown
        """
        if not version.startswith('v'):
            version = f"v{version}"
            
        # Load version metadata
        metadata = self.get_version_metadata(version)
        endpoints = self.discover_version_endpoints(version)
        
        # Generate documentation sections
        header = self.generate_header(version, metadata)
        quickstart = self.generate_quickstart(version)
        endpoint_docs = self.generate_endpoint_documentation(version, endpoints)
        examples = self.generate_ai_agent_examples(version)
        error_handling = self.generate_error_handling_guide(version)
        best_practices = self.generate_ai_best_practices(version)
        troubleshooting = self.generate_troubleshooting_guide(version)
        response_samples = self.generate_response_samples(version)
        
        # Assemble complete documentation
        docs = f"""{header}

{quickstart}

{endpoint_docs}

{examples}

{error_handling}

{best_practices}

{troubleshooting}

{response_samples}

---

**🙏 Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Blessed by Goddess Laxmi for Infinite Abundance**
"""

        return docs
        
    def get_version_metadata(self, version: str) -> Dict:
        """Get metadata for specific version."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                
            version_metadata = config.get('version_metadata', {})
            return version_metadata.get(version, {})
            
        except Exception as e:
            logger.warning(f"Could not load version metadata: {e}")
            return {}
            
    def discover_version_endpoints(self, version: str) -> Dict:
        """Discover available endpoints for a version."""
        try:
            # Load version module to inspect endpoints
            version_dir = self.base_path / "api_versions" / version
            server_path = version_dir / "laxmi_mcp_server.py"
            
            if not server_path.exists():
                # Fallback to current server for development
                server_path = self.base_path / "mcp-server" / "laxmi_mcp_server.py"
                
            if server_path.exists():
                return self.extract_endpoints_from_server(server_path)
            else:
                return self.get_default_endpoints(version)
                
        except Exception as e:
            logger.warning(f"Could not discover endpoints for {version}: {e}")
            return self.get_default_endpoints(version)
            
    def extract_endpoints_from_server(self, server_path: Path) -> Dict:
        """Extract endpoints from server module."""
        try:
            # Read server file and look for @mcp.tool and @mcp.resource decorators
            with open(server_path, 'r') as f:
                content = f.read()
                
            tools = []
            resources = []
            
            # Find @mcp.tool decorators
            import re
            tool_pattern = r'@mcp\.tool\(["\']([^"\']+)["\']'
            resource_pattern = r'@mcp\.resource\(["\']([^"\']+)["\']'
            
            tools = re.findall(tool_pattern, content)
            resources = re.findall(resource_pattern, content)
            
            return {
                "tools": tools,
                "resources": resources
            }
            
        except Exception as e:
            logger.warning(f"Could not extract endpoints from {server_path}: {e}")
            return self.get_default_endpoints("")
            
    def get_default_endpoints(self, version: str) -> Dict:
        """Get default endpoints structure."""
        return {
            "tools": [
                "buy_stock",
                "sell_stock", 
                "execute_trade",
                "get_account_status",
                "get_recent_orders",
                "activate_kill_switch",
                "deactivate_kill_switch",
                "get_kill_switch_status"
            ],
            "resources": [
                "account_info",
                "current_positions",
                "portfolio_summary", 
                "strategy_summary",
                "system_health"
            ]
        }
        
    def generate_header(self, version: str, metadata: Dict) -> str:
        """Generate documentation header."""
        release_date = metadata.get('release_date', 'Unknown')
        status = metadata.get('status', 'stable')
        breaking_changes = metadata.get('breaking_changes', False)
        
        breaking_warning = ""
        if breaking_changes:
            breaking_warning = f"""
> ⚠️ **Breaking Changes Alert**: This version includes breaking changes from previous versions. 
> Please review the migration guide carefully before upgrading.
"""
        
        return f"""# Laxmi-yantra Trading API {version} - AI Agent Usage Guide

**🎯 Purpose**: Complete guide for AI agents to optimally use the Laxmi-yantra Trading API {version}
**📅 Release Date**: {release_date}
**🔄 Status**: {status.title()}
**🤖 Optimized for**: AI Agents, Automated Trading, Algorithmic Systems

{breaking_warning}

> **Disclaimer**: This documentation is version-specific for {version}. 
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
"""

    def generate_quickstart(self, version: str) -> str:
        """Generate quick start guide."""
        return f"""## 🚀 Quick Start

### 1. Start the Server
```bash
# Start HTTP server with version support
./start-server.sh TRANSPORT=http HOST=127.0.0.1 PORT=8000 \\
  PORTFOLIO_EVENT_POLLING_ENABLED=true PORTFOLIO_EVENT_POLLING_INTERVAL=5m

# Verify server is running
curl -s http://127.0.0.1:8000/health
```

### 2. Check API Version Support
```bash
# List all available versions
curl -s http://127.0.0.1:8000/versions

# Check specific version health
curl -s http://127.0.0.1:8000/{version}/health
```

### 3. Basic Authentication Test
```bash
# Verify account access
curl -s -X POST http://127.0.0.1:8000/{version}/tools/get_account_status \\
  -H 'Content-Type: application/json' -d '{{}}'
```

### 4. First Trading Action
```bash
# Get current portfolio state
curl -s http://127.0.0.1:8000/{version}/resources/portfolio_summary

# Execute a small test trade
curl -s -X POST http://127.0.0.1:8000/{version}/tools/buy_stock \\
  -H 'Content-Type: application/json' \\
  -d '{{"ticker":"AAPL","quantity":1,"strategy_name":"test_strategy"}}'
```

### Base URL Structure
All endpoints use the pattern: `http://127.0.0.1:8000/{version}/{{endpoint_type}}/{{endpoint_name}}`

- **Tools** (Actions): `POST /{version}/tools/{{tool_name}}`
- **Resources** (Data): `GET /{version}/resources/{{resource_name}}`
- **Health**: `GET /{version}/health`
"""

    def generate_endpoint_documentation(self, version: str, endpoints: Dict) -> str:
        """Generate detailed endpoint documentation."""
        tools_doc = self.generate_tools_documentation(version, endpoints.get("tools", []))
        resources_doc = self.generate_resources_documentation(version, endpoints.get("resources", []))
        
        return f"""## 📋 Endpoints Reference

### Tools (POST - Actions)
{tools_doc}

### Resources (GET - Data Retrieval)  
{resources_doc}

### System Endpoints
- `GET /{version}/health` - Version-specific health check
- `GET /health` - Global multi-version health check
- `GET /versions` - List all available API versions
- `GET /` - API information and navigation
"""

    def generate_tools_documentation(self, version: str, tools: List[str]) -> str:
        """Generate tools documentation."""
        tools_docs = []
        
        tool_descriptions = {
            "buy_stock": {
                "description": "Execute stock purchase with market or limit orders",
                "required": ["ticker", "quantity", "strategy_name"],
                "optional": ["order_type", "price", "time_in_force"],
                "example": {
                    "ticker": "AAPL",
                    "quantity": 10,
                    "strategy_name": "ai_agent_strategy",
                    "order_type": "market"
                }
            },
            "sell_stock": {
                "description": "Execute stock sale with market or limit orders",
                "required": ["ticker", "quantity", "strategy_name"], 
                "optional": ["order_type", "price", "time_in_force"],
                "example": {
                    "ticker": "AAPL",
                    "quantity": 5,
                    "strategy_name": "ai_agent_strategy",
                    "order_type": "limit",
                    "price": 175.50
                }
            },
            "execute_trade": {
                "description": "Advanced trade execution with full control",
                "required": ["strategy_name", "ticker", "side", "quantity", "order_type"],
                "optional": ["price", "time_in_force", "extended_hours"],
                "example": {
                    "strategy_name": "ai_agent_strategy",
                    "ticker": "TSLA",
                    "side": "buy",
                    "quantity": 2,
                    "order_type": "limit",
                    "price": 250.00
                }
            },
            "get_account_status": {
                "description": "Retrieve account information and trading status",
                "required": [],
                "optional": [],
                "example": {}
            },
            "get_recent_orders": {
                "description": "Get recent order history with optional limit",
                "required": [],
                "optional": ["limit", "strategy_name"],
                "example": {"limit": 20}
            },
            "activate_kill_switch": {
                "description": "Emergency stop - halt all trading operations",
                "required": ["reason"],
                "optional": [],
                "example": {"reason": "Emergency stop requested by AI agent"}
            },
            "deactivate_kill_switch": {
                "description": "Resume trading operations after kill switch",
                "required": [],
                "optional": [],
                "example": {}
            },
            "get_kill_switch_status": {
                "description": "Check current kill switch status",
                "required": [],
                "optional": [],
                "example": {}
            }
        }
        
        for tool in tools:
            tool_info = tool_descriptions.get(tool, {
                "description": f"Execute {tool} operation",
                "required": [],
                "optional": [],
                "example": {}
            })
            
            required_params = ", ".join(tool_info["required"]) if tool_info["required"] else "None"
            optional_params = ", ".join(tool_info["optional"]) if tool_info["optional"] else "None"
            
            example_json = json.dumps(tool_info["example"], indent=2)
            
            tools_docs.append(f"""
#### `POST /{version}/tools/{tool}`
**Description**: {tool_info["description"]}
**Required Parameters**: {required_params}
**Optional Parameters**: {optional_params}

```bash
curl -s -X POST http://127.0.0.1:8000/{version}/tools/{tool} \\
  -H 'Content-Type: application/json' \\
  -d '{example_json}'
```
""")
            
        return "\n".join(tools_docs)
        
    def generate_resources_documentation(self, version: str, resources: List[str]) -> str:
        """Generate resources documentation."""
        resources_docs = []
        
        resource_descriptions = {
            "account_info": {
                "description": "Account details and trading permissions",
                "params": [],
                "example_url": f"/{version}/resources/account_info"
            },
            "current_positions": {
                "description": "Live positions from broker (real-time)",
                "params": [],
                "example_url": f"/{version}/resources/current_positions"
            },
            "portfolio_summary": {
                "description": "Portfolio overview from database with PnL calculations",
                "params": ["strategy_name (optional)"],
                "example_url": f"/{version}/resources/portfolio_summary?strategy_name=ai_strategy"
            },
            "strategy_summary": {
                "description": "Comprehensive strategy analytics with holdings and performance",
                "params": ["strategy_name (required)"],
                "example_url": f"/{version}/resources/strategy_summary?strategy_name=ai_strategy"
            },
            "system_health": {
                "description": "System status, connectivity, and health metrics",
                "params": [],
                "example_url": f"/{version}/resources/system_health"
            }
        }
        
        for resource in resources:
            resource_info = resource_descriptions.get(resource, {
                "description": f"Get {resource} information",
                "params": [],
                "example_url": f"/{version}/resources/{resource}"
            })
            
            params_info = ", ".join(resource_info["params"]) if resource_info["params"] else "None"
            
            resources_docs.append(f"""
#### `GET /{version}/resources/{resource}`
**Description**: {resource_info["description"]}
**Query Parameters**: {params_info}

```bash
curl -s http://127.0.0.1:8000{resource_info["example_url"]}
```
""")
            
        return "\n".join(resources_docs)
        
    def generate_ai_agent_examples(self, version: str) -> str:
        """Generate AI agent specific examples."""
        return f"""## 🤖 AI Agent Examples

### Complete Trading Workflow
```bash
#!/bin/bash
# AI Agent Trading Workflow for API {version}

BASE_URL="http://127.0.0.1:8000/{version}"

# 1. Health and connectivity check
echo "Checking system health..."
curl -s "$BASE_URL/health" | jq .

# 2. Verify account access and status
echo "Getting account status..."
ACCOUNT=$(curl -s -X POST "$BASE_URL/tools/get_account_status" \\
  -H 'Content-Type: application/json' -d '{{}}')
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
TRADE_RESULT=$(curl -s -X POST "$BASE_URL/tools/buy_stock" \\
  -H 'Content-Type: application/json' \\
  -d '{{"ticker":"AAPL","quantity":1,"strategy_name":"ai_agent","order_type":"market"}}')
echo $TRADE_RESULT | jq .

# 6. Monitor order status
echo "Checking recent orders..."
ORDERS=$(curl -s -X POST "$BASE_URL/tools/get_recent_orders" \\
  -H 'Content-Type: application/json' -d '{{"limit":5}}')
echo $ORDERS | jq .
```

### AI Decision Making Pattern
```python
import requests
import json

class LaxmiYantraAgent:
    def __init__(self, base_url="http://127.0.0.1:8000/{version}"):
        self.base_url = base_url
        self.strategy_name = "ai_agent"
        
    def health_check(self):
        \"\"\"Verify system is healthy before trading.\"\"\"
        response = requests.get(f"{{self.base_url}}/health")
        return response.json()
        
    def get_portfolio_state(self):
        \"\"\"Get comprehensive portfolio analysis.\"\"\"
        url = f"{{self.base_url}}/resources/strategy_summary"
        params = {{"strategy_name": self.strategy_name}}
        response = requests.get(url, params=params)
        return response.json()
        
    def execute_trade_decision(self, ticker, side, quantity):
        \"\"\"Execute trading decision with proper error handling.\"\"\"
        url = f"{{self.base_url}}/tools/execute_trade"
        payload = {{
            "strategy_name": self.strategy_name,
            "ticker": ticker,
            "side": side,
            "quantity": quantity,
            "order_type": "market"
        }}
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 400:
                # Business logic error - handle gracefully
                error_info = response.json()
                print(f"Trading error: {{error_info.get('error', 'Unknown error')}}")
                return None
            else:
                raise
                
    def monitor_positions(self):
        \"\"\"Monitor position performance with PnL analysis.\"\"\"
        portfolio = self.get_portfolio_state()
        
        for holding in portfolio.get('holdings', []):
            pnl_pct = holding.get('unrealized_pl_pct', 0)
            print(f"{{holding['ticker']}}: {{pnl_pct:.2f}}% PnL")
            
            # Example: Simple stop-loss at -5%
            if pnl_pct < -5.0:
                print(f"Stop-loss triggered for {{holding['ticker']}}")
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
BASE_URL="http://127.0.0.1:8000/{version}"

# 1. Check kill switch status before any trades
KILL_STATUS=$(curl -s -X POST "$BASE_URL/tools/get_kill_switch_status" \\
  -H 'Content-Type: application/json' -d '{{}}')
echo "Kill switch status: $KILL_STATUS"

# 2. Activate emergency stop if needed
if [ "$EMERGENCY_DETECTED" = "true" ]; then
  curl -s -X POST "$BASE_URL/tools/activate_kill_switch" \\
    -H 'Content-Type: application/json' \\
    -d '{{"reason":"AI agent detected market anomaly"}}'
fi

# 3. Portfolio risk check
PORTFOLIO=$(curl -s "$BASE_URL/resources/portfolio_summary")
NET_PNL=$(echo $PORTFOLIO | jq '.totals.net_unrealized_pl_pct')

# Activate kill switch if portfolio loss > 10%
if (( $(echo "$NET_PNL < -10" | bc -l) )); then
  curl -s -X POST "$BASE_URL/tools/activate_kill_switch" \\
    -H 'Content-Type: application/json' \\
    -d '{{"reason":"Portfolio loss limit exceeded"}}'
fi
```
"""

    def generate_error_handling_guide(self, version: str) -> str:
        """Generate error handling guide."""
        return f"""## ⚠️ Error Handling

### HTTP Status Codes
- **200 OK**: Successful operation
- **400 Bad Request**: Business logic errors (insufficient funds, invalid parameters)
- **404 Not Found**: Endpoint or resource not found
- **406 Not Acceptable**: Content negotiation failed
- **500 Internal Server Error**: Unexpected server errors

### Error Response Format
```json
{{
  "error": "Descriptive error message",
  "details": "Additional context when available",
  "timestamp": "2025-01-21T12:00:00Z",
  "version": "{version}"
}}
```

### Common Business Errors (400)
```bash
# Insufficient position for sell
curl -s -X POST http://127.0.0.1:8000/{version}/tools/sell_stock \\
  -H 'Content-Type: application/json' \\
  -d '{{"ticker":"AAPL","quantity":1000,"strategy_name":"test"}}'
# Response: {{"error": "Insufficient position. Current: 0, Requested: 1000"}}

# Invalid ticker
curl -s -X POST http://127.0.0.1:8000/{version}/tools/buy_stock \\
  -H 'Content-Type: application/json' \\
  -d '{{"ticker":"INVALID","quantity":1,"strategy_name":"test"}}'
# Response: {{"error": "Invalid ticker symbol: INVALID"}}

# Missing required parameter
curl -s -X POST http://127.0.0.1:8000/{version}/tools/buy_stock \\
  -H 'Content-Type: application/json' \\
  -d '{{"ticker":"AAPL","quantity":1}}'
# Response: {{"error": "Missing required parameter: strategy_name"}}
```

### Kill Switch Errors
```bash
# Trading when kill switch is active
curl -s -X POST http://127.0.0.1:8000/{version}/tools/buy_stock \\
  -H 'Content-Type: application/json' \\
  -d '{{"ticker":"AAPL","quantity":1,"strategy_name":"test"}}'
# Response: {{"error": "Trading is currently disabled due to active kill switch"}}
```

### AI Agent Error Handling Pattern
```python
def safe_api_call(url, method='GET', **kwargs):
    \"\"\"Safe API call with comprehensive error handling.\"\"\"
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
            return None, f"Business error: {{error_info.get('error')}}"
        elif response.status_code == 404:
            return None, "Endpoint not found - check API version"
        elif response.status_code == 500:
            return None, "Server error - retry later"
        else:
            return None, f"HTTP error {{response.status_code}}: {{e}}"
            
    except requests.exceptions.ConnectionError:
        return None, "Connection failed - check if server is running"
    except requests.exceptions.Timeout:
        return None, "Request timeout - server may be overloaded"
    except Exception as e:
        return None, f"Unexpected error: {{e}}"

# Usage in AI agent
result, error = safe_api_call(f"{{base_url}}/tools/buy_stock", 
                             method='POST', 
                             json=trade_params)
if error:
    logger.warning(f"Trade failed: {{error}}")
    # Implement retry logic or alternative strategy
else:
    logger.info(f"Trade successful: {{result}}")
```
"""

    def generate_ai_best_practices(self, version: str) -> str:
        """Generate AI agent best practices."""
        return f"""## 💡 Best Practices for AI Agents

### 1. Always Check Health First
```bash
# Never start trading without health verification
curl -s http://127.0.0.1:8000/{version}/health
```

### 2. Use Strategy-Specific Operations
```bash
# Always specify strategy_name for tracking and risk management
STRATEGY="ai_agent_$(date +%Y%m%d)"
curl -s -X POST http://127.0.0.1:8000/{version}/tools/buy_stock \\
  -d '{{"ticker":"AAPL","quantity":1,"strategy_name":"'$STRATEGY'"}}'
```

### 3. Monitor Portfolio State Continuously
```bash
# Get comprehensive strategy analytics before major decisions
curl -s "http://127.0.0.1:8000/{version}/resources/strategy_summary?strategy_name=$STRATEGY"
```

### 4. Implement Position Sizing
```python
def calculate_position_size(portfolio_value, risk_per_trade=0.02):
    \"\"\"Calculate position size based on portfolio value and risk tolerance.\"\"\"
    max_risk_amount = portfolio_value * risk_per_trade
    # Additional position sizing logic...
    return position_size
```

### 5. Use Limit Orders for Better Control
```bash
# Prefer limit orders over market orders for better price control
curl -s -X POST http://127.0.0.1:8000/{version}/tools/buy_stock \\
  -d '{{
    "ticker": "AAPL",
    "quantity": 10,
    "strategy_name": "ai_agent",
    "order_type": "limit",
    "price": 175.50
  }}'
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
    \"\"\"API call with exponential backoff.\"\"\"
    for attempt in range(max_retries):
        try:
            return func()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limited
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
            else:
                raise
    raise Exception(f"Max retries ({{max_retries}}) exceeded")
```

### 8. Log All Trading Decisions
```python
import logging

trading_logger = logging.getLogger('ai_trading')
trading_logger.setLevel(logging.INFO)

def log_trade_decision(action, ticker, quantity, reasoning):
    trading_logger.info(f"TRADE_DECISION: {{action}} {{quantity}} {{ticker}} - {{reasoning}}")

# Usage
log_trade_decision("BUY", "AAPL", 10, "Technical breakout above resistance")
```

### 9. Validate Market Hours
```python
from datetime import datetime
import pytz

def is_market_open():
    \"\"\"Check if market is currently open.\"\"\"
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
emergency_stop() {{
  curl -s -X POST http://127.0.0.1:8000/{version}/tools/activate_kill_switch \\
    -H 'Content-Type: application/json' \\
    -d '{{"reason":"AI agent emergency stop - unusual market conditions"}}'
}}

# Call during market anomalies or system errors
```
"""

    def generate_troubleshooting_guide(self, version: str) -> str:
        """Generate troubleshooting guide."""
        return f"""## 🔧 Troubleshooting

### Connection Issues
```bash
# Test basic connectivity
curl -s http://127.0.0.1:8000/health
# Expected: {{"status": "healthy", ...}}

# Test version-specific endpoint
curl -s http://127.0.0.1:8000/{version}/health
# Expected: Version-specific health data
```

### Authentication Issues
```bash
# Check if credentials are loaded
curl -s -X POST http://127.0.0.1:8000/{version}/tools/get_account_status \\
  -H 'Content-Type: application/json' -d '{{}}'
# Look for "ALPACA_API_KEY not found" or similar errors
```

### Trading Issues
```bash
# Check kill switch status
curl -s -X POST http://127.0.0.1:8000/{version}/tools/get_kill_switch_status \\
  -H 'Content-Type: application/json' -d '{{}}'

# Verify account has buying power
curl -s http://127.0.0.1:8000/{version}/resources/account_info
```

### Version Issues
```bash
# List all available versions
curl -s http://127.0.0.1:8000/versions

# Check if your version is active
curl -s http://127.0.0.1:8000/versions | jq '.active_versions[]' | grep "{version}"
```

### Database Sync Issues
```bash
# Check if background polling is enabled
# Look for "PORTFOLIO_EVENT_POLLING_ENABLED=true" in logs

# Compare broker vs database positions
curl -s http://127.0.0.1:8000/{version}/resources/current_positions > broker_positions.json
curl -s http://127.0.0.1:8000/{version}/resources/portfolio_summary > db_positions.json
```

### Common Error Solutions

#### "404 Not Found"
- Verify API version is correct and active
- Check endpoint spelling and method (GET vs POST)
- Ensure server is running on correct port

#### "400 Bad Request: Insufficient position"
```bash
# Check current holdings before selling
curl -s "http://127.0.0.1:8000/{version}/resources/strategy_summary?strategy_name=your_strategy"
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
echo "=== Laxmi-yantra API {version} Diagnostics ==="

echo "1. Basic connectivity..."
curl -s http://127.0.0.1:8000/health | jq .

echo "2. Version health..."
curl -s http://127.0.0.1:8000/{version}/health | jq .

echo "3. Account status..."
curl -s -X POST http://127.0.0.1:8000/{version}/tools/get_account_status \\
  -H 'Content-Type: application/json' -d '{{}}' | jq .

echo "4. Kill switch status..."
curl -s -X POST http://127.0.0.1:8000/{version}/tools/get_kill_switch_status \\
  -H 'Content-Type: application/json' -d '{{}}' | jq .

echo "5. Recent orders..."
curl -s -X POST http://127.0.0.1:8000/{version}/tools/get_recent_orders \\
  -H 'Content-Type: application/json' -d '{{"limit":5}}' | jq .

echo "=== Diagnostics Complete ==="
```
"""

    def generate_response_samples(self, version: str) -> str:
        """Generate response samples with current version paths."""
        # Read the template and update paths for this version
        try:
            with open(self.template_path, 'r') as f:
                template_content = f.read()
                
            # Extract the response samples section
            start_marker = "### 10) Sample responses (for agents)"
            if start_marker in template_content:
                samples_section = template_content.split(start_marker)[1]
                
                # Update all URLs to use the specific version
                updated_samples = samples_section.replace("/mcp/", f"/{version}/")
                updated_samples = updated_samples.replace("http://127.0.0.1:8000/", f"http://127.0.0.1:8000/{version}/")
                
                return f"""## 📊 Response Samples

> **Note**: These samples are specific to API {version}. Field names, values, and structure may vary between versions.

{updated_samples}"""
            
        except Exception as e:
            logger.warning(f"Could not load response samples from template: {e}")
            
        # Fallback to basic samples
        return f"""## 📊 Response Samples

### Tool Response: get_account_status
```json
{{
  "account_status": "ACTIVE",
  "trading_blocked": false,
  "buying_power": 99750.23,
  "cash": 100000.00,
  "portfolio_value": 100250.75,
  "paper_trading": true,
  "api_version": "{version}"
}}
```

### Resource Response: strategy_summary
```json
{{
  "strategy_name": "ai_agent",
  "total_positions": 2,
  "holdings": [
    {{
      "ticker": "AAPL",
      "quantity": 10.0,
      "current_price": 172.0,
      "cost_basis": 1680.0,
      "market_value": 1720.0,
      "unrealized_pl": 40.0,
      "unrealized_pl_pct": 2.38
    }}
  ],
  "totals": {{
    "total_cost_basis": 1680.0,
    "total_market_value": 1720.0,
    "net_unrealized_pl": 40.0,
    "net_unrealized_pl_pct": 2.38
  }},
  "api_version": "{version}",
  "timestamp": "2025-01-21T12:00:00Z"
}}
```
"""

    def save_version_docs(self, version: str, docs: str) -> Path:
        """Save version-specific documentation."""
        if not version.startswith('v'):
            version = f"v{version}"
            
        # Create version directory
        version_dir = self.base_path / "api_versions" / version
        version_dir.mkdir(parents=True, exist_ok=True)
        
        # Save version-specific documentation
        docs_path = version_dir / "AI_AGENT_USAGE_GUIDE.md"
        with open(docs_path, 'w') as f:
            f.write(docs)
            
        # Also create a symlink/copy in docs directory
        docs_dir = self.base_path / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        version_docs_path = docs_dir / f"REST_API_USAGE_GUIDE_{version}.md"
        with open(version_docs_path, 'w') as f:
            f.write(docs)
            
        logger.info(f"Saved API documentation: {docs_path} and {version_docs_path}")
        return docs_path
        
    def update_main_docs_index(self, version: str) -> None:
        """Update main documentation index with new version."""
        docs_dir = self.base_path / "docs"
        index_path = docs_dir / "API_VERSIONS_INDEX.md"
        
        # Load existing index or create new
        existing_content = ""
        if index_path.exists():
            with open(index_path, 'r') as f:
                existing_content = f.read()
                
        # Add new version to index
        new_entry = f"- [{version}](REST_API_USAGE_GUIDE_{version}.md) - AI Agent Usage Guide for {version}"
        
        if new_entry not in existing_content:
            index_content = f"""# API Documentation Versions

This directory contains version-specific API documentation optimized for AI agents.

## Available Versions

{new_entry}
{existing_content.replace('## Available Versions', '').strip()}

## Latest Version

The latest stable API version documentation is available at: [Current](REST_API_USAGE_GUIDE.md)

---

**🙏 All documentation blessed by Goddess Laxmi for infinite abundance**
"""
            
            with open(index_path, 'w') as f:
                f.write(index_content)
                
            logger.info(f"Updated API documentation index: {index_path}")
            
    def generate_all_versions_docs(self) -> None:
        """Generate documentation for all active versions."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                
            active_versions = config.get('active_versions', [])
            
            for version in active_versions:
                logger.info(f"Generating documentation for {version}")
                docs = self.generate_version_docs(version)
                self.save_version_docs(version, docs)
                self.update_main_docs_index(version)
                
        except Exception as e:
            logger.error(f"Failed to generate documentation for all versions: {e}")
            raise
