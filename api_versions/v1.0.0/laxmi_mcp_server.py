#!/usr/bin/env python3
"""
🙏 Laxmi-yantra MCP Server
Blessed by Goddess Laxmi for Infinite Abundance

FastMCP server exposing all Laxmi-yantra trading functionality via MCP protocol.
Supports STDIO, HTTP, and SSE transports for maximum compatibility.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP, Context
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse
import uvicorn
import inspect
import os
from src.braintransactions.modules.laxmi_yantra.trading_manager import LaxmiYantra
from src.braintransactions.core.exceptions import (
    BrainTransactionError,
    KillSwitchActiveError,
    TransactionExecutionError,
    OrderValidationError,
    InsufficientFundsError,
    APIConnectionError,
    InvalidConfigurationError
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Laxmi-yantra Trading Server")

# Global trading manager instance
trading_manager: Optional[LaxmiYantra] = None


async def get_trading_manager() -> LaxmiYantra:
    """Get or initialize the trading manager."""
    global trading_manager
    if trading_manager is None:
        trading_manager = LaxmiYantra()
        logger.info("🙏 Laxmi-yantra trading manager initialized")
    return trading_manager


# ----------------------
# Lightweight HTTP Logic
# ----------------------

async def http_get_account_status() -> Dict[str, Any]:
    manager = await get_trading_manager()
    account = manager.account_info
    return {
        "account_status": account.status,
        "trading_blocked": account.trading_blocked,
        "buying_power": float(account.buying_power),
        "cash": float(account.cash),
        "portfolio_value": float(account.portfolio_value),
        "paper_trading": manager.config.paper_trading,
    }


async def http_get_recent_orders(limit: int = 10) -> List[Dict[str, Any]]:
    manager = await get_trading_manager()
    return manager.order_manager.get_recent_orders(limit)


async def http_execute_trade(
    strategy_name: str,
    ticker: str,
    side: str,
    quantity: float,
    order_type: str = "market",
) -> Dict[str, Any]:
    manager = await get_trading_manager()
    transaction_data = {
        "strategy_name": strategy_name,
        "ticker": ticker.upper(),
        "side": side.lower(),
        "quantity": float(quantity),
        "order_type": order_type.lower(),
        "action": side.lower(),
    }
    return manager.execute_transaction(transaction_data)


async def http_buy_stock(
    ticker: str,
    quantity: float,
    strategy_name: str = "mcp_strategy",
    order_type: str = "market",
    price: Optional[float] = None,
) -> Dict[str, Any]:
    manager = await get_trading_manager()
    if order_type == "limit" and (price is None or price <= 0):
        raise HTTPException(status_code=400, detail="Limit orders require positive price")
    transaction_data = {
        "strategy_name": strategy_name,
        "ticker": ticker.upper(),
        "side": "buy",
        "quantity": float(quantity),
        "order_type": order_type.lower(),
        "action": "buy",
    }
    if order_type == "limit":
        transaction_data["limit_price"] = float(price)
    return manager.execute_transaction(transaction_data)


async def http_sell_stock(
    ticker: str,
    quantity: float,
    strategy_name: str = "mcp_strategy",
    order_type: str = "market",
    price: Optional[float] = None,
) -> Dict[str, Any]:
    manager = await get_trading_manager()
    if order_type == "limit" and (price is None or price <= 0):
        raise HTTPException(status_code=400, detail="Limit orders require positive price")
    transaction_data = {
        "strategy_name": strategy_name,
        "ticker": ticker.upper(),
        "side": "sell",
        "quantity": float(quantity),
        "order_type": order_type.lower(),
        "action": "sell",
    }
    if order_type == "limit":
        transaction_data["limit_price"] = float(price)
    return manager.execute_transaction(transaction_data)


async def http_activate_kill_switch(reason: str = "Manual activation") -> Dict[str, Any]:
    manager = await get_trading_manager()
    return {"activated": manager.activate_kill_switch(reason, "HTTP_User"), "reason": reason}


async def http_deactivate_kill_switch() -> Dict[str, Any]:
    manager = await get_trading_manager()
    return {"deactivated": manager.deactivate_kill_switch("HTTP_User")}


async def http_get_kill_switch_status() -> Dict[str, Any]:
    manager = await get_trading_manager()
    return manager.get_kill_switch_status()


async def http_get_system_health() -> Dict[str, Any]:
    manager = await get_trading_manager()
    try:
        db_status = manager.portfolio_manager.db_manager.execute_query("SELECT 1 as test")
        db_healthy = len(db_status) > 0
    except Exception:
        db_healthy = False
    account = manager.account_info
    return {
        "account_status": account.status,
        "trading_blocked": account.trading_blocked,
        "kill_switch_active": manager.get_kill_switch_status().get("is_active", False),
        "database_healthy": db_healthy,
        "paper_trading": manager.config.paper_trading,
        "alpaca_connected": True,
        "buying_power": float(account.buying_power),
        "cash": float(account.cash),
    }


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime,)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(v) for v in value]
    return value


# ----------------------
# HTTP Resource Wrappers
# ----------------------

async def http_account_info() -> Dict[str, Any]:
    manager = await get_trading_manager()
    account = manager.account_info
    return {
        "account_id": account.id,
        "status": account.status,
        "trading_blocked": account.trading_blocked,
        "transfers_blocked": account.transfers_blocked,
        "account_blocked": account.account_blocked,
        "pattern_day_trader": account.pattern_day_trader,
        "daytrading_buying_power": float(account.daytrading_buying_power),
        "buying_power": float(account.buying_power),
        "cash": float(account.cash),
        "portfolio_value": float(account.portfolio_value),
        "equity": float(account.equity),
        "last_equity": float(account.last_equity),
        "currency": account.currency,
        "created_at": str(account.created_at),
    }


async def http_current_positions() -> List[Dict[str, Any]]:
    manager = await get_trading_manager()
    positions = manager.api.list_positions()
    results: List[Dict[str, Any]] = []
    for pos in positions or []:
        results.append({
            "symbol": pos.symbol,
            "quantity": float(getattr(pos, "qty", 0) or 0),
            "side": getattr(pos, "side", None),
            "market_value": float(getattr(pos, "market_value", 0) or 0),
            "avg_entry_price": float(getattr(pos, "avg_entry_price", 0) or 0),
            "unrealized_pl": float(getattr(pos, "unrealized_pl", 0) or 0),
            "unrealized_pl_pct": float(getattr(pos, "unrealized_plpc", 0) or 0) * 100.0,
            "current_price": float(getattr(pos, "current_price", 0) or 0),
        })
    return results


async def http_portfolio_summary(strategy_name: Optional[str] = None) -> Dict[str, Any]:
    manager = await get_trading_manager()
    df = manager.portfolio_manager.get_all_positions(strategy_name)
    try:
        records_base = df.to_dict(orient="records") if hasattr(df, "to_dict") else []
    except Exception:
        records_base = []

    # Enrich each position with valuation and PnL metrics
    enriched: List[Dict[str, Any]] = []
    total_cost_basis = 0.0
    total_market_value = 0.0

    # Live price helper
    try:
        from alpaca_trade_api.rest import TimeFrame, TimeFrameUnit
        timeframe = TimeFrame(1, TimeFrameUnit.Minute)
    except Exception:
        timeframe = None

    for row in records_base:
        try:
            ticker = row.get("ticker")
            qty = float(row.get("quantity") or 0)
            avg_price = float(row.get("avg_entry_price") or 0)

            current_price = None
            if timeframe is not None and ticker:
                try:
                    bars = manager.api.get_bars(ticker, timeframe, limit=1)
                    price_val = None
                    if hasattr(bars, "df"):
                        if not bars.df.empty:
                            price_val = float(bars.df.iloc[-1]["close"])  # type: ignore[index]
                    elif isinstance(bars, list) and bars:
                        price_val = float(getattr(bars[-1], "c", None) or getattr(bars[-1], "close", 0))
                    if price_val is not None:
                        current_price = price_val
                except Exception:
                    current_price = None

            cost_basis = qty * avg_price
            market_value = qty * (current_price if current_price is not None else avg_price)
            pnl = market_value - cost_basis
            pnl_pct = (pnl / cost_basis * 100.0) if cost_basis > 0 else 0.0
            abs_pnl_pct = abs(pnl_pct)

            total_cost_basis += cost_basis
            total_market_value += market_value

            enriched.append({
                **row,
                "current_price": current_price,
                "cost_basis": cost_basis,
                "market_value": market_value,
                # canonical naming
                "unrealized_pl": pnl,
                "unrealized_pl_pct": pnl_pct,
                "abs_unrealized_pl_pct": abs_pnl_pct,
                # aliases per request
                "pln": pnl,
                "pln_pct": pnl_pct,
                "abs_pln_pct": abs_pnl_pct,
            })
        except Exception:
            continue

    net_pnl = total_market_value - total_cost_basis
    net_pnl_pct = (net_pnl / total_cost_basis * 100.0) if total_cost_basis > 0 else 0.0
    abs_net_pnl_pct = abs(net_pnl_pct)

    return {
        "database_positions": len(enriched),
        "positions": enriched,
        "totals": {
            "total_positions": len(enriched),
            "total_quantity": float(sum(p.get("quantity", 0) for p in enriched)),
            "total_cost_basis": total_cost_basis,
            "total_market_value": total_market_value,
            "net_unrealized_pl": net_pnl,
            "net_unrealized_pl_pct": net_pnl_pct,
            "abs_net_unrealized_pl_pct": abs_net_pnl_pct,
            # aliases
            "net_pln": net_pnl,
            "net_pln_pct": net_pnl_pct,
            "abs_net_pln_pct": abs_net_pnl_pct,
        }
    }


async def http_strategy_summary(strategy_name: str) -> Dict[str, Any]:
    manager = await get_trading_manager()
    base_summary = manager.portfolio_manager.get_strategy_summary(strategy_name)

    # Pull current positions from DB
    df = manager.portfolio_manager.get_all_positions(strategy_name)
    records = []
    try:
        records = df.to_dict(orient="records") if hasattr(df, "to_dict") else []
    except Exception:
        records = []

    # Enrich each holding with live price and PnL
    enriched_holdings: List[Dict[str, Any]] = []
    total_cost_basis = 0.0
    total_market_value = 0.0

    # Import here to avoid global dependency if HTTP-only
    try:
        from alpaca_trade_api.rest import TimeFrame, TimeFrameUnit
        timeframe = TimeFrame(1, TimeFrameUnit.Minute)
    except Exception:
        timeframe = None  # Fallback: no live pricing

    for pos in records:
        try:
            ticker = pos.get("ticker")
            qty = float(pos.get("quantity") or 0)
            avg_price = float(pos.get("avg_entry_price") or 0)

            current_price = None
            if timeframe is not None and ticker:
                try:
                    bars = manager.api.get_bars(ticker, timeframe, limit=1)
                    # Support both DataFrame API and list
                    price_val = None
                    if hasattr(bars, "df"):
                        if not bars.df.empty:
                            price_val = float(bars.df.iloc[-1]["close"])  # type: ignore[index]
                    elif isinstance(bars, list) and bars:
                        price_val = float(getattr(bars[-1], "c", None) or getattr(bars[-1], "close", 0))
                    if price_val is not None:
                        current_price = price_val
                except Exception:
                    current_price = None

            cost_basis = qty * avg_price
            market_value = qty * (current_price if current_price is not None else avg_price)
            unrealized_pl = market_value - cost_basis
            unrealized_pl_pct = (unrealized_pl / cost_basis * 100.0) if cost_basis > 0 else 0.0

            total_cost_basis += cost_basis
            total_market_value += market_value

            enriched_holdings.append({
                "ticker": ticker,
                "quantity": qty,
                "avg_entry_price": avg_price,
                "current_price": current_price,
                "cost_basis": cost_basis,
                "market_value": market_value,
                "unrealized_pl": unrealized_pl,
                "unrealized_pl_pct": unrealized_pl_pct,
                "abs_unrealized_pl_pct": abs(unrealized_pl_pct),
                # aliases
                "pln": unrealized_pl,
                "pln_pct": unrealized_pl_pct,
                "abs_pln_pct": abs(unrealized_pl_pct),
                "last_updated": pos.get("last_updated")
            })
        except Exception:
            continue

    net_unrealized_pl = total_market_value - total_cost_basis
    net_unrealized_pl_pct = (net_unrealized_pl / total_cost_basis * 100.0) if total_cost_basis > 0 else 0.0

    enriched_summary: Dict[str, Any] = {
        **base_summary,
        "strategy_name": strategy_name,
        "holdings": enriched_holdings,
        "totals": {
            "total_positions": len(enriched_holdings),
            "total_quantity": float(sum(h.get("quantity", 0) for h in enriched_holdings)),
            "total_cost_basis": total_cost_basis,
            "total_market_value": total_market_value,
            "net_unrealized_pl": net_unrealized_pl,
            "net_unrealized_pl_pct": net_unrealized_pl_pct,
            "abs_net_unrealized_pl_pct": abs(net_unrealized_pl_pct),
            # aliases
            "net_pln": net_unrealized_pl,
            "net_pln_pct": net_unrealized_pl_pct,
            "abs_net_pln_pct": abs(net_unrealized_pl_pct),
        },
        "timestamp": datetime.now().isoformat(),
    }

    return enriched_summary


@mcp.resource("laxmi://account_info")
async def get_account_info(ctx: Context) -> str:
    """Get current Alpaca account information and status."""
    try:
        manager = await get_trading_manager()
        account = manager.account_info
        
        account_data = {
            "account_id": account.id,
            "status": account.status,
            "trading_blocked": account.trading_blocked,
            "transfers_blocked": account.transfers_blocked,
            "account_blocked": account.account_blocked,
            "pattern_day_trader": account.pattern_day_trader,
            "daytrading_buying_power": float(account.daytrading_buying_power),
            "buying_power": float(account.buying_power),
            "cash": float(account.cash),
            "portfolio_value": float(account.portfolio_value),
            "equity": float(account.equity),
            "last_equity": float(account.last_equity),
            "currency": account.currency,
            "created_at": str(account.created_at)
        }
        
        await ctx.info("Account info retrieved successfully")
        return f"Alpaca Account Information:\n{account_data}"
        
    except Exception as e:
        await ctx.error(f"Failed to get account info: {str(e)}")
        return f"Error: {str(e)}"


@mcp.resource("laxmi://current_positions")
async def get_current_positions(ctx: Context) -> str:
    """Get current portfolio positions from Alpaca."""
    try:
        manager = await get_trading_manager()
        positions = manager.api.list_positions()
        
        if not positions:
            return "No current positions"
        
        positions_data = []
        for pos in positions:
            positions_data.append({
                "symbol": pos.symbol,
                "quantity": float(pos.qty),
                "side": pos.side,
                "market_value": float(pos.market_value),
                "avg_entry_price": float(pos.avg_entry_price),
                "unrealized_pl": float(pos.unrealized_pl),
                "unrealized_pl_pct": float(pos.unrealized_plpc) * 100.0 if getattr(pos, "unrealized_plpc", None) is not None else None,
                "current_price": float(pos.current_price) if pos.current_price else None
            })
        
        await ctx.info(f"Retrieved {len(positions)} positions")
        return f"Current Positions:\n{positions_data}"
        
    except Exception as e:
        await ctx.error(f"Failed to get positions: {str(e)}")
        return f"Error: {str(e)}"


@mcp.resource("laxmi://portfolio_summary")
async def get_portfolio_summary(ctx: Context) -> str:
    """Get portfolio summary from database."""
    try:
        manager = await get_trading_manager()
        
        # Get positions from portfolio manager
        portfolio_positions = manager.portfolio_manager.get_all_positions()
        
        summary = {
            "database_positions": len(portfolio_positions),
            "positions": portfolio_positions
        }
        
        await ctx.info("Portfolio summary retrieved")
        return f"Portfolio Summary:\n{summary}"
        
    except Exception as e:
        await ctx.error(f"Failed to get portfolio summary: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def execute_trade(
    strategy_name: str,
    ticker: str,
    side: str,
    quantity: float,
    order_type: str = "market",
    ctx: Context = None
) -> str:
    """
    Execute a trade using Laxmi-yantra trading system.
    
    Args:
        strategy_name: Name of the trading strategy
        ticker: Stock symbol (e.g., 'AAPL', 'TSLA')
        side: 'buy' or 'sell'
        quantity: Number of shares to trade
        order_type: Order type ('market', 'limit', etc.)
    """
    try:
        await ctx.info(f"🚀 Executing {side} order for {quantity} shares of {ticker}")
        
        manager = await get_trading_manager()
        
        transaction_data = {
            "strategy_name": strategy_name,
            "ticker": ticker.upper(),
            "side": side.lower(),
            "quantity": float(quantity),
            "order_type": order_type.lower(),
            "action": side.lower()  # Add the missing action field
        }
        
        # Execute the transaction
        result = manager.execute_transaction(transaction_data)
        
        await ctx.info(f"✅ Trade executed successfully: {result.get('order_id', 'N/A')}")
        return f"Trade executed successfully!\nResult: {result}"
        
    except KillSwitchActiveError as e:
        await ctx.error(f"❌ Kill switch is active: {str(e)}")
        return f"Error: Kill switch is active - {str(e)}"
    except OrderValidationError as e:
        await ctx.error(f"❌ Order validation failed: {str(e)}")
        return f"Error: Invalid order - {str(e)}"
    except InsufficientFundsError as e:
        await ctx.error(f"❌ Insufficient funds: {str(e)}")
        return f"Error: Insufficient funds - {str(e)}"
    except TransactionExecutionError as e:
        await ctx.error(f"❌ Transaction failed: {str(e)}")
        return f"Error: Transaction failed - {str(e)}"
    except Exception as e:
        await ctx.error(f"❌ Unexpected error: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def buy_stock(
    ticker: str,
    quantity: float,
    strategy_name: str = "mcp_strategy",
    order_type: str = "market",
    price: float = None,
    ctx: Context = None
) -> str:
    """
    🛡️ ENHANCED Buy shares of a stock with comprehensive validation and safety checks.
    
    Args:
        ticker: Stock symbol (e.g., 'AAPL', 'TSLA') - must be valid US stock symbol
        quantity: Number of shares to buy (must be > 0, supports fractional shares)
        strategy_name: Trading strategy name (default: 'mcp_strategy')
        order_type: Order type ('market' or 'limit', default: 'market')
        price: Limit price (required for limit orders, ignored for market orders)
    
    Returns:
        Detailed execution result with order ID, status, and audit trail
    """
    transaction_id = None
    
    try:
        # 🔐 PHASE 1: Pre-execution validation and logging
        await ctx.info(f"🚀 [BUY] Initiating buy order: {quantity} shares of {ticker.upper()}")
        await ctx.info(f"📊 [BUY] Strategy: {strategy_name}, Order Type: {order_type}")
        
        # Enhanced input validation
        if not ticker or not isinstance(ticker, str):
            raise OrderValidationError("Ticker must be a non-empty string")
        
        ticker = ticker.upper().strip()
        if len(ticker) < 1 or len(ticker) > 5 or not ticker.isalpha():
            raise OrderValidationError(f"Invalid ticker format: {ticker}. Must be 1-5 letters")
        
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            raise OrderValidationError(f"Quantity must be positive number, got: {quantity}")
        
        if quantity > 10000:  # Safety limit
            raise OrderValidationError(f"Quantity {quantity} exceeds safety limit of 10,000 shares")
        
        if not strategy_name or not isinstance(strategy_name, str):
            raise OrderValidationError("Strategy name must be a non-empty string")
        
        order_type = order_type.lower().strip()
        if order_type not in ['market', 'limit']:
            raise OrderValidationError(f"Order type must be 'market' or 'limit', got: {order_type}")
        
        if order_type == 'limit':
            if price is None or not isinstance(price, (int, float)) or price <= 0:
                raise OrderValidationError("Limit price is required and must be positive for limit orders")
            if price > 100000:  # Safety limit
                raise OrderValidationError(f"Limit price {price} exceeds safety limit of $100,000")
        
        # 🏗️ PHASE 2: Get trading manager and pre-flight checks
        manager = await get_trading_manager()
        
        # Check account status
        account = manager.account_info
        if account.trading_blocked:
            raise TransactionExecutionError("Account trading is blocked")
        
        # Check buying power for market orders (approximate)
        if order_type == 'market':
            available_buying_power = float(account.buying_power)
            # Rough estimate: assume $500 per share max for market orders
            estimated_cost = quantity * 500
            if estimated_cost > available_buying_power:
                raise InsufficientFundsError(
                    f"Estimated cost ${estimated_cost:,.2f} exceeds buying power ${available_buying_power:,.2f}",
                    required_amount=estimated_cost,
                    available_amount=available_buying_power
                )
        elif order_type == 'limit':
            required_cash = quantity * price
            available_cash = float(account.cash)
            if required_cash > available_cash:
                raise InsufficientFundsError(
                    f"Required cash ${required_cash:,.2f} exceeds available cash ${available_cash:,.2f}",
                    required_amount=required_cash,
                    available_amount=available_cash
                )
        
        # 📝 PHASE 3: Prepare transaction data with full audit trail
        transaction_data = {
            "strategy_name": strategy_name,
            "ticker": ticker,
            "side": "buy",
            "quantity": float(quantity),
            "order_type": order_type,
            "action": "buy",
            "pre_execution_checks": {
                "account_status": account.status,
                "buying_power": float(account.buying_power),
                "cash": float(account.cash),
                "timestamp": datetime.now().isoformat()
            }
        }
        
        if order_type == 'limit':
            transaction_data["limit_price"] = float(price)
        
        await ctx.info(f"✅ [BUY] Pre-execution validation passed")
        
        # 🎯 PHASE 4: Execute transaction with full error handling
        result = manager.execute_transaction(transaction_data)
        transaction_id = result.get('transaction_id')
        
        # 📊 PHASE 5: Post-execution validation and reporting
        order_id = result.get('order_id', 'N/A')
        order_status = result.get('status', 'unknown')
        
        await ctx.info(f"✅ [BUY] Order executed successfully!")
        await ctx.info(f"📋 [BUY] Order ID: {order_id}")
        await ctx.info(f"📊 [BUY] Status: {order_status}")
        await ctx.info(f"🔍 [BUY] Transaction ID: {transaction_id}")
        
        # Return comprehensive result
        execution_summary = {
            "status": "SUCCESS",
            "order_id": order_id,
            "transaction_id": transaction_id,
            "ticker": ticker,
            "quantity": quantity,
            "order_type": order_type,
            "strategy_name": strategy_name,
            "execution_timestamp": datetime.now().isoformat(),
            "order_status": order_status
        }
        
        if order_type == 'limit':
            execution_summary["limit_price"] = price
        
        return f"🎉 Buy order executed successfully!\n\n📊 Execution Summary:\n{execution_summary}"
        
    except KillSwitchActiveError as e:
        await ctx.error(f"🛑 [BUY] Kill switch is active: {str(e)}")
        return f"❌ Error: Kill switch is active - Trading operations are blocked. Reason: {str(e)}"
    except OrderValidationError as e:
        await ctx.error(f"📋 [BUY] Order validation failed: {str(e)}")
        return f"❌ Error: Order validation failed - {str(e)}\n\nPlease check:\n• Ticker format (1-5 letters)\n• Quantity > 0 and < 10,000\n• Valid order type (market/limit)\n• Limit price if using limit orders"
    except InsufficientFundsError as e:
        await ctx.error(f"💰 [BUY] Insufficient funds: {str(e)}")
        return f"❌ Error: Insufficient funds - {str(e)}\n\nPlease check your account balance and buying power."
    except TransactionExecutionError as e:
        await ctx.error(f"⚡ [BUY] Transaction execution failed: {str(e)}")
        if transaction_id:
            await ctx.error(f"🔍 [BUY] Transaction ID for troubleshooting: {transaction_id}")
        return f"❌ Error: Transaction execution failed - {str(e)}\n\nTransaction ID: {transaction_id or 'N/A'}"
    except APIConnectionError as e:
        await ctx.error(f"🌐 [BUY] API connection error: {str(e)}")
        return f"❌ Error: Trading API connection failed - {str(e)}\n\nPlease try again in a few moments."
    except Exception as e:
        await ctx.error(f"💥 [BUY] Unexpected error: {str(e)}")
        if transaction_id:
            await ctx.error(f"🔍 [BUY] Transaction ID for troubleshooting: {transaction_id}")
        return f"❌ Error: Unexpected system error - {str(e)}\n\nTransaction ID: {transaction_id or 'N/A'}\n\nPlease contact support if this persists."


@mcp.tool()
async def sell_stock(
    ticker: str,
    quantity: float,
    strategy_name: str = "mcp_strategy",
    order_type: str = "market",
    price: float = None,
    ctx: Context = None
) -> str:
    """
    🛡️ ENHANCED Sell shares of a stock with comprehensive position validation and safety checks.
    
    Args:
        ticker: Stock symbol (e.g., 'AAPL', 'TSLA') - must be valid US stock symbol
        quantity: Number of shares to sell (must be > 0, cannot exceed current position)
        strategy_name: Trading strategy name (default: 'mcp_strategy')
        order_type: Order type ('market' or 'limit', default: 'market')
        price: Limit price (required for limit orders, ignored for market orders)
    
    Returns:
        Detailed execution result with order ID, status, and position update
    """
    transaction_id = None
    current_position = None
    
    try:
        # 🔐 PHASE 1: Pre-execution validation and logging
        await ctx.info(f"📉 [SELL] Initiating sell order: {quantity} shares of {ticker.upper()}")
        await ctx.info(f"📊 [SELL] Strategy: {strategy_name}, Order Type: {order_type}")
        
        # Enhanced input validation
        if not ticker or not isinstance(ticker, str):
            raise OrderValidationError("Ticker must be a non-empty string")
        
        ticker = ticker.upper().strip()
        if len(ticker) < 1 or len(ticker) > 5 or not ticker.isalpha():
            raise OrderValidationError(f"Invalid ticker format: {ticker}. Must be 1-5 letters")
        
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            raise OrderValidationError(f"Quantity must be positive number, got: {quantity}")
        
        if quantity > 10000:  # Safety limit
            raise OrderValidationError(f"Quantity {quantity} exceeds safety limit of 10,000 shares")
        
        if not strategy_name or not isinstance(strategy_name, str):
            raise OrderValidationError("Strategy name must be a non-empty string")
        
        order_type = order_type.lower().strip()
        if order_type not in ['market', 'limit']:
            raise OrderValidationError(f"Order type must be 'market' or 'limit', got: {order_type}")
        
        if order_type == 'limit':
            if price is None or not isinstance(price, (int, float)) or price <= 0:
                raise OrderValidationError("Limit price is required and must be positive for limit orders")
            if price > 100000:  # Safety limit
                raise OrderValidationError(f"Limit price {price} exceeds safety limit of $100,000")
        
        # 🏗️ PHASE 2: Get trading manager and critical position validation
        manager = await get_trading_manager()
        
        # Check account status
        account = manager.account_info
        if account.trading_blocked:
            raise TransactionExecutionError("Account trading is blocked")
        
        # CRITICAL: Validate current position before allowing sell
        current_position = manager.portfolio_manager.get_position(strategy_name, ticker)
        
        if not current_position:
            raise InsufficientFundsError(
                f"No position found for {ticker} in strategy {strategy_name}",
                required_amount=quantity,
                available_amount=0
            )
        
        available_quantity = float(current_position.get('quantity', 0))
        if available_quantity < quantity:
            raise InsufficientFundsError(
                f"Insufficient position: trying to sell {quantity} shares but only have {available_quantity}",
                required_amount=quantity,
                available_amount=available_quantity
            )
        
        # Additional safety check: warn about selling entire position
        if quantity >= available_quantity * 0.95:  # Selling 95%+ of position
            await ctx.info(f"⚠️ [SELL] WARNING: Selling {quantity}/{available_quantity} shares ({(quantity/available_quantity)*100:.1f}% of position)")
        
        # 📝 PHASE 3: Prepare transaction data with position context
        transaction_data = {
            "strategy_name": strategy_name,
            "ticker": ticker,
            "side": "sell",
            "quantity": float(quantity),
            "order_type": order_type,
            "action": "sell",
            "pre_execution_checks": {
                "account_status": account.status,
                "current_position": {
                    "quantity": available_quantity,
                    "avg_entry_price": float(current_position.get('avg_entry_price', 0)),
                    "last_updated": str(current_position.get('last_updated', ''))
                },
                "remaining_after_sell": available_quantity - quantity,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        if order_type == 'limit':
            transaction_data["limit_price"] = float(price)
        
        await ctx.info(f"✅ [SELL] Position validation passed - {available_quantity} shares available")
        
        # 🎯 PHASE 4: Execute transaction with enhanced position tracking
        result = manager.execute_transaction(transaction_data)
        transaction_id = result.get('transaction_id')
        
        # 📊 PHASE 5: Post-execution validation and position update confirmation
        order_id = result.get('order_id', 'N/A')
        order_status = result.get('status', 'unknown')
        
        # Verify position was updated correctly
        updated_position = manager.portfolio_manager.get_position(strategy_name, ticker)
        final_quantity = float(updated_position.get('quantity', 0)) if updated_position else 0
        
        await ctx.info(f"✅ [SELL] Order executed successfully!")
        await ctx.info(f"📋 [SELL] Order ID: {order_id}")
        await ctx.info(f"📊 [SELL] Status: {order_status}")
        await ctx.info(f"🔍 [SELL] Transaction ID: {transaction_id}")
        await ctx.info(f"📉 [SELL] Position updated: {available_quantity} → {final_quantity} shares")
        
        # Return comprehensive result with position tracking
        execution_summary = {
            "status": "SUCCESS",
            "order_id": order_id,
            "transaction_id": transaction_id,
            "ticker": ticker,
            "quantity_sold": quantity,
            "order_type": order_type,
            "strategy_name": strategy_name,
            "execution_timestamp": datetime.now().isoformat(),
            "order_status": order_status,
            "position_before": available_quantity,
            "position_after": final_quantity,
            "position_change": -quantity
        }
        
        if order_type == 'limit':
            execution_summary["limit_price"] = price
        
        if final_quantity == 0:
            execution_summary["position_status"] = "CLOSED"
            await ctx.info(f"🏁 [SELL] Position CLOSED for {ticker}")
        else:
            execution_summary["position_status"] = "PARTIAL"
        
        return f"🎉 Sell order executed successfully!\n\n📊 Execution Summary:\n{execution_summary}"
        
    except KillSwitchActiveError as e:
        await ctx.error(f"🛑 [SELL] Kill switch is active: {str(e)}")
        return f"❌ Error: Kill switch is active - Trading operations are blocked. Reason: {str(e)}"
    except OrderValidationError as e:
        await ctx.error(f"📋 [SELL] Order validation failed: {str(e)}")
        return f"❌ Error: Order validation failed - {str(e)}\n\nPlease check:\n• Ticker format (1-5 letters)\n• Quantity > 0 and < 10,000\n• Valid order type (market/limit)\n• Limit price if using limit orders"
    except InsufficientFundsError as e:
        await ctx.error(f"📉 [SELL] Insufficient position: {str(e)}")
        position_info = ""
        if current_position:
            available = float(current_position.get('quantity', 0))
            position_info = f"\n\nCurrent position: {available} shares"
        return f"❌ Error: Insufficient position - {str(e)}{position_info}\n\nCannot sell more shares than you own."
    except TransactionExecutionError as e:
        await ctx.error(f"⚡ [SELL] Transaction execution failed: {str(e)}")
        if transaction_id:
            await ctx.error(f"🔍 [SELL] Transaction ID for troubleshooting: {transaction_id}")
        return f"❌ Error: Transaction execution failed - {str(e)}\n\nTransaction ID: {transaction_id or 'N/A'}"
    except APIConnectionError as e:
        await ctx.error(f"🌐 [SELL] API connection error: {str(e)}")
        return f"❌ Error: Trading API connection failed - {str(e)}\n\nPlease try again in a few moments."
    except Exception as e:
        await ctx.error(f"💥 [SELL] Unexpected error: {str(e)}")
        if transaction_id:
            await ctx.error(f"🔍 [SELL] Transaction ID for troubleshooting: {transaction_id}")
        return f"❌ Error: Unexpected system error - {str(e)}\n\nTransaction ID: {transaction_id or 'N/A'}\n\nPlease contact support if this persists."


@mcp.tool()
async def get_account_status(ctx: Context = None) -> str:
    """Get current account status and trading capabilities."""
    try:
        manager = await get_trading_manager()
        account = manager.account_info
        
        status = {
            "account_status": account.status,
            "trading_blocked": account.trading_blocked,
            "buying_power": float(account.buying_power),
            "cash": float(account.cash),
            "portfolio_value": float(account.portfolio_value),
            "paper_trading": manager.config.paper_trading
        }
        
        await ctx.info("Account status retrieved")
        return f"Account Status: {status}"
        
    except Exception as e:
        await ctx.error(f"Failed to get account status: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def activate_kill_switch(reason: str = "Manual activation", ctx: Context = None) -> str:
    """
    Activate the emergency kill switch to stop all trading.
    
    Args:
        reason: Reason for activation
    """
    try:
        manager = await get_trading_manager()
        success = manager.activate_kill_switch(reason, "MCP_User")
        
        if success:
            await ctx.info(f"🛑 Kill switch activated: {reason}")
            return f"Kill switch activated successfully. Reason: {reason}"
        else:
            return "Kill switch was already active"
            
    except Exception as e:
        await ctx.error(f"Failed to activate kill switch: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def deactivate_kill_switch(ctx: Context = None) -> str:
    """Deactivate the kill switch to resume trading."""
    try:
        manager = await get_trading_manager()
        success = manager.deactivate_kill_switch("MCP_User")
        
        if success:
            await ctx.info("✅ Kill switch deactivated")
            return "Kill switch deactivated successfully. Trading can resume."
        else:
            return "Kill switch was already inactive"
            
    except Exception as e:
        await ctx.error(f"Failed to deactivate kill switch: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def get_kill_switch_status(ctx: Context = None) -> str:
    """Get current kill switch status."""
    try:
        manager = await get_trading_manager()
        status = manager.get_kill_switch_status()
        
        await ctx.info("Kill switch status retrieved")
        return f"Kill Switch Status: {status}"
        
    except Exception as e:
        await ctx.error(f"Failed to get kill switch status: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def get_recent_orders(limit: int = 10, ctx: Context = None) -> str:
    """
    Get recent order history.
    
    Args:
        limit: Maximum number of orders to retrieve (default: 10)
    """
    try:
        manager = await get_trading_manager()
        orders = manager.order_manager.get_recent_orders(limit)
        
        await ctx.info(f"Retrieved {len(orders)} recent orders")
        return f"Recent Orders ({len(orders)}): {orders}"
        
    except Exception as e:
        await ctx.error(f"Failed to get recent orders: {str(e)}")
        return f"Error: {str(e)}"


@mcp.tool()
async def get_system_health(ctx: Context = None) -> str:
    """Get comprehensive system health status."""
    try:
        manager = await get_trading_manager()
        
        # Get account info
        account = manager.account_info
        
        # Get kill switch status
        kill_switch_status = manager.get_kill_switch_status()
        
        # Get database status
        try:
            db_status = manager.portfolio_manager.db_manager.execute_query("SELECT 1 as test")
            db_healthy = len(db_status) > 0
        except:
            db_healthy = False
        
        health_status = {
            "timestamp": str(asyncio.get_event_loop().time()),
            "account_status": account.status,
            "trading_blocked": account.trading_blocked,
            "kill_switch_active": kill_switch_status.get("is_active", False),
            "database_healthy": db_healthy,
            "paper_trading": manager.config.paper_trading,
            "alpaca_connected": True,  # If we got here, it's connected
            "buying_power": float(account.buying_power),
            "cash": float(account.cash)
        }
        
        await ctx.info("System health check completed")
        return f"System Health: {health_status}"
        
    except Exception as e:
        await ctx.error(f"System health check failed: {str(e)}")
        return f"Error: {str(e)}"


@mcp.resource("laxmi://system_health")
async def system_health_resource(ctx: Context) -> str:
    """Backward-compatible resource endpoint mirroring get_system_health tool."""
    try:
        manager = await get_trading_manager()
        account = manager.account_info
        try:
            db_status = manager.portfolio_manager.db_manager.execute_query("SELECT 1 as test")
            db_healthy = len(db_status) > 0
        except Exception:
            db_healthy = False

        health_status = {
            "timestamp": str(asyncio.get_event_loop().time()),
            "account_status": account.status,
            "trading_blocked": account.trading_blocked,
            "kill_switch_active": manager.get_kill_switch_status().get("is_active", False),
            "database_healthy": db_healthy,
            "paper_trading": manager.config.paper_trading,
            "alpaca_connected": True,
            "buying_power": float(account.buying_power),
            "cash": float(account.cash),
        }

        await ctx.info("System health (resource) check completed")
        return f"System Health: {health_status}"
    except Exception as e:
        await ctx.error(f"System health (resource) check failed: {str(e)}")
        return f"Error: {str(e)}"

# Note: HTTP GET will be available at /mcp/resources/system_health

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Laxmi-yantra MCP Server")
    parser.add_argument("--transport", choices=["stdio", "http", "sse"], default="stdio",
                      help="Transport protocol (default: stdio)")
    parser.add_argument("--host", default="127.0.0.1", help="Host for HTTP/SSE (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port for HTTP/SSE (default: 8000)")
    parser.add_argument("--path", default="/mcp", help="Path for HTTP transport (default: /mcp)")
    
    args = parser.parse_args()
    
    print("🙏 Starting Laxmi-yantra MCP Server - May Goddess Laxmi bless this service!")
    print(f"Transport: {args.transport}")
    
    if args.transport == "stdio":
        mcp.run(transport="stdio")
    elif args.transport == "http":
        print(f"HTTP server will be available at: http://{args.host}:{args.port}{args.path}")

        # Lightweight FastAPI app to provide stable, simple HTTP endpoints
        app = FastAPI(title="Laxmi-yantra HTTP API")

        class DummyCtx:
            async def info(self, msg: str) -> None:
                logger.info(msg)
            async def error(self, msg: str) -> None:
                logger.error(msg)

        # Tool dispatch map
        tool_map = {
            # Lightweight HTTP wrappers (stable)
            "get_account_status": http_get_account_status,
            "get_recent_orders": http_get_recent_orders,
            "execute_trade": http_execute_trade,
            "buy_stock": http_buy_stock,
            "sell_stock": http_sell_stock,
            "activate_kill_switch": http_activate_kill_switch,
            "deactivate_kill_switch": http_deactivate_kill_switch,
            "get_kill_switch_status": http_get_kill_switch_status,
            "get_system_health": http_get_system_health,
        }

        # Resource dispatch map
        resource_map = {
            # Use HTTP wrappers to avoid MCP wrapper objects
            "account_info": http_account_info,
            "current_positions": http_current_positions,
            "portfolio_summary": http_portfolio_summary,
            "strategy_summary": http_strategy_summary,
            "system_health": http_get_system_health,
        }

        @app.get("/health")
        async def health_root():
            return {"status": "ok"}

        # -----------------------------
        # Background poller (env-driven)
        # -----------------------------
        def _parse_interval_to_seconds(raw: str) -> float:
            try:
                s = raw.strip().lower()
                if s.endswith('ms'):
                    return float(s[:-2]) / 1000.0
                if s.endswith('s'):
                    return float(s[:-1])
                if s.endswith('m'):
                    return float(s[:-1]) * 60.0
                if s.endswith('h'):
                    return float(s[:-1]) * 3600.0
                return float(s)
            except Exception:
                return 300.0  # default 5 minutes

        POLLING_ENABLED_ENV = os.getenv('PORTFOLIO_EVENT_POLLING_ENABLED', 'false').lower() == 'true'
        POLLING_INTERVAL_SECONDS = _parse_interval_to_seconds(os.getenv('PORTFOLIO_EVENT_POLLING_INTERVAL', '5m'))
        DEFAULT_STRATEGY = os.getenv('POLLING_STRATEGY', 'default')

        if POLLING_ENABLED_ENV:
            @app.on_event("startup")
            async def _start_background_poller():
                async def _loop():
                    import asyncio
                    logger.info(f"Starting background poller: interval={POLLING_INTERVAL_SECONDS}s strategy={DEFAULT_STRATEGY}")
                    while True:
                        try:
                            mgr = await get_trading_manager()
                            # Reconcile orders
                            try:
                                orders = mgr.api.list_orders(status='all')
                                mgr.order_manager.reconcile_order_statuses(orders)
                            except Exception as e:
                                logger.warning(f"Background order reconcile error: {e}")
                            # Reconcile positions
                            try:
                                positions = mgr.api.list_positions()
                                mgr.portfolio_manager.reconcile_positions_from_alpaca(positions, DEFAULT_STRATEGY)
                            except Exception as e:
                                logger.warning(f"Background position reconcile error: {e}")
                        except Exception as e:
                            logger.error(f"Background poller error: {e}")
                        await asyncio.sleep(POLLING_INTERVAL_SECONDS)

                import asyncio
                asyncio.create_task(_loop())

        # -----------------------------
        # JSON-RPC bridge for MCP (/mcp)
        # -----------------------------
        @app.get(f"{args.path}")
        async def mcp_get_root():
            return {"status": "mcp-jsonrpc", "path": args.path}

        @app.post(f"{args.path}")
        async def mcp_jsonrpc(request: Request):
            try:
                body = await request.json()
            except Exception:
                return JSONResponse(status_code=400, content={
                    "jsonrpc": "2.0", "id": "server-error",
                    "error": {"code": -32600, "message": "Invalid JSON"}
                })

            jsonrpc = body.get("jsonrpc")
            req_id = body.get("id")
            method = body.get("method")
            params = body.get("params", {}) or {}

            if jsonrpc != "2.0" or not method:
                return JSONResponse(status_code=400, content={
                    "jsonrpc": "2.0", "id": req_id or "server-error",
                    "error": {"code": -32600, "message": "Invalid Request"}
                })

            try:
                if method == "tools/call":
                    name = params.get("name")
                    arguments = params.get("arguments", {}) or {}
                    if not name or name not in tool_map:
                        return JSONResponse(content={
                            "jsonrpc": "2.0", "id": req_id,
                            "error": {"code": -32601, "message": f"Unknown tool: {name}"}
                        })

                    func = tool_map[name]
                    # Unwrap and call similar to REST handler
                    call_target = func
                    for attr in ("callback", "function", "func"):
                        if hasattr(call_target, attr):
                            call_target = getattr(call_target, attr)
                            break
                    kwargs = arguments
                    sig = None
                    try:
                        sig = inspect.signature(call_target)
                    except Exception:
                        pass
                    if sig and "ctx" in sig.parameters:
                        kwargs = {**kwargs, "ctx": DummyCtx()}
                    if inspect.iscoroutinefunction(call_target):
                        result = await call_target(**kwargs)
                    else:
                        result = call_target(**kwargs)
                    return JSONResponse(content={"jsonrpc": "2.0", "id": req_id, "result": _to_jsonable(result)})

                if method == "resources/read":
                    uri = params.get("uri") or params.get("name")
                    # Accept either full uri like laxmi://system_health or plain name
                    name = uri.split("://", 1)[-1] if "://" in (uri or "") else uri
                    if not name or name not in resource_map:
                        return JSONResponse(content={
                            "jsonrpc": "2.0", "id": req_id,
                            "error": {"code": -32601, "message": f"Unknown resource: {uri}"}
                        })
                    func = resource_map[name]
                    call_target = func
                    for attr in ("callback", "function", "func"):
                        if hasattr(call_target, attr):
                            call_target = getattr(call_target, attr)
                            break
                    kwargs = {}
                    sig = None
                    try:
                        sig = inspect.signature(call_target)
                    except Exception:
                        pass
                    if sig and "ctx" in sig.parameters:
                        kwargs["ctx"] = DummyCtx()
                    if inspect.iscoroutinefunction(call_target):
                        result = await call_target(**kwargs)
                    else:
                        result = call_target(**kwargs)
                    return JSONResponse(content={"jsonrpc": "2.0", "id": req_id, "result": _to_jsonable(result)})

                if method == "tools/list":
                    names = sorted(list(tool_map.keys()))
                    return JSONResponse(content={"jsonrpc": "2.0", "id": req_id, "result": names})

                if method == "resources/list":
                    names = sorted(list(resource_map.keys()))
                    return JSONResponse(content={"jsonrpc": "2.0", "id": req_id, "result": names})

                if method in ("health", "get_health"):
                    return JSONResponse(content={"jsonrpc": "2.0", "id": req_id, "result": {"status": "ok"}})

                return JSONResponse(content={
                    "jsonrpc": "2.0", "id": req_id,
                    "error": {"code": -32601, "message": f"Unknown method: {method}"}
                })

            except (OrderValidationError, InsufficientFundsError, TransactionExecutionError) as e:
                return JSONResponse(status_code=400, content={
                    "jsonrpc": "2.0", "id": req_id,
                    "error": {"code": -32602, "message": str(e)}
                })
            except Exception as e:
                logger.exception("JSON-RPC error")
                return JSONResponse(status_code=500, content={
                    "jsonrpc": "2.0", "id": req_id or "server-error",
                    "error": {"code": -32603, "message": str(e)}
                })

        @app.post(f"{args.path}/tools/{{tool_name}}")
        async def call_tool(tool_name: str, request: Request):
            func = tool_map.get(tool_name)
            if not func:
                raise HTTPException(status_code=404, detail=f"Unknown tool: {tool_name}")
            try:
                payload = await request.json()
            except Exception:
                payload = {}
            try:
                # Unwrap MCP tool objects if needed
                call_target = func
                for attr in ("callback", "function", "func"):
                    if hasattr(call_target, attr):
                        call_target = getattr(call_target, attr)
                        break

                kwargs = payload or {}
                sig = None
                try:
                    sig = inspect.signature(call_target)
                except Exception:
                    pass
                if sig and "ctx" in sig.parameters:
                    kwargs = {**kwargs, "ctx": DummyCtx()}

                if inspect.iscoroutinefunction(call_target):
                    result = await call_target(**kwargs)
                else:
                    result = call_target(**kwargs)
                # Return plain JSON or text depending on result
                if isinstance(result, (dict, list)):
                    return JSONResponse(content=_to_jsonable(result))
                return PlainTextResponse(str(result))
            except TypeError as e:
                # Argument mismatch
                raise HTTPException(status_code=400, detail=f"Invalid arguments: {e}")
            except (OrderValidationError, InsufficientFundsError, TransactionExecutionError) as e:
                # Business errors → 400 with clear message
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logger.exception("Tool execution error")
                raise HTTPException(status_code=500, detail=str(e))

        # Convenience GET aliases for read-only tools
        @app.get(f"{args.path}/tools/get_account_status")
        async def get_account_status_get():
            try:
                result = await http_get_account_status()
                return JSONResponse(content=_to_jsonable(result))
            except Exception as e:
                logger.exception("GET get_account_status error")
                raise HTTPException(status_code=500, detail=str(e))

        @app.get(f"{args.path}/tools/get_recent_orders")
        async def get_recent_orders_get(limit: int = 10):
            try:
                result = await http_get_recent_orders(limit)
                return JSONResponse(content=_to_jsonable(result))
            except Exception as e:
                logger.exception("GET get_recent_orders error")
                raise HTTPException(status_code=500, detail=str(e))

        @app.get(f"{args.path}/resources/{{resource_name}}")
        async def read_resource(resource_name: str, request: Request):
            func = resource_map.get(resource_name)
            if not func:
                raise HTTPException(status_code=404, detail=f"Unknown resource: {resource_name}")
            try:
                # Unwrap MCP resource objects if needed
                call_target = func
                for attr in ("callback", "function", "func"):
                    if hasattr(call_target, attr):
                        call_target = getattr(call_target, attr)
                        break

                # Pass ctx only if requested
                # Merge query params into kwargs
                kwargs = dict(request.query_params)
                sig = None
                try:
                    sig = inspect.signature(call_target)
                except Exception:
                    pass
                if sig and "ctx" in sig.parameters and "ctx" not in kwargs:
                    kwargs["ctx"] = DummyCtx()

                if inspect.iscoroutinefunction(call_target):
                    result = await call_target(**kwargs)
                else:
                    result = call_target(**kwargs)

                # Prefer text for resources; support JSON too
                if isinstance(result, (dict, list)):
                    return JSONResponse(content=_to_jsonable(result))
                return PlainTextResponse(str(result))
            except TypeError as e:
                raise HTTPException(status_code=400, detail=f"Invalid arguments: {e}")
            except Exception as e:
                logger.exception("Resource read error")
                raise HTTPException(status_code=500, detail=str(e))

        # Run FastAPI app via uvicorn
        uvicorn.run(app, host=args.host, port=args.port)
    elif args.transport == "sse":
        print(f"SSE server will be available at: http://{args.host}:{args.port}/sse")
        mcp.run(transport="sse", host=args.host, port=args.port)
