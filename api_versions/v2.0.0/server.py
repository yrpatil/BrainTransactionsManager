"""
BrainTransactionsManager v2.0.0 Server
Blessed by Goddess Laxmi for Infinite Abundance 🙏

Production-ready server with unified configuration, multi-exchange support,
and comprehensive monitoring. Built following SRM principles.
"""

import asyncio
import logging
import os
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Import v2.0.0 components
from src.braintransactions import (
    BrainConfig, init_config,
    DatabaseManager, MigrationManager,
    ExchangeManager, BackgroundMonitor
)

# Import sophisticated logging
from src.braintransactions.core.logging_config import setup_logging, get_logger

# Setup logging system
system_logger = setup_logging(
    debug_mode=os.getenv('DEBUG', 'false').lower() == 'true',
    log_level=os.getenv('LOG_LEVEL', 'INFO')
)
logger = get_logger("server")

# Global instances
config: Optional[BrainConfig] = None
db_manager: Optional[DatabaseManager] = None
exchange_manager: Optional[ExchangeManager] = None
background_monitor: Optional[BackgroundMonitor] = None
migration_manager: Optional[MigrationManager] = None


# Pydantic models for API
class OrderRequest(BaseModel):
    symbol: str = Field(..., description="Trading symbol")
    side: str = Field(..., description="Order side: buy or sell")
    order_type: str = Field(default="market", description="Order type")
    quantity: float = Field(..., gt=0, description="Order quantity")
    price: Optional[float] = Field(None, description="Order price for limit orders")
    strategy_name: str = Field(default="default", description="Strategy identifier")
    exchange: Optional[str] = Field(None, description="Specific exchange")


class OrderResponse(BaseModel):
    success: bool
    order_id: Optional[str] = None
    message: str
    data: Optional[Dict[str, Any]] = None


# Request models for trading
class BuyOrderRequest(BaseModel):
    symbol: str
    quantity: float
    strategy_name: str = "default"
    order_type: str = "market"
    price: Optional[float] = None
    exchange: Optional[str] = None

class SellOrderRequest(BaseModel):
    symbol: str
    quantity: float
    strategy_name: str = "default"
    order_type: str = "market"
    price: Optional[float] = None
    exchange: Optional[str] = None

# Additional request models for missing functionalities
class PortfolioSummaryRequest(BaseModel):
    strategy_name: Optional[str] = None

class OrderStatisticsRequest(BaseModel):
    strategy_name: Optional[str] = None
    days: Optional[int] = 30

class EmergencyStopRequest(BaseModel):
    reason: str = "Emergency stop requested"
    strategy_name: Optional[str] = None

class KillSwitchRequest(BaseModel):
    action: str = Field(..., description="Action: 'activate' or 'deactivate'")
    reason: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup sequence
    system_logger.startup_sequence()
    
    try:
        # Initialize global instances
        await initialize_system()
        
        logger.success("System initialization complete")
        yield
        
    except Exception as e:
        logger.critical(f"System initialization failed: {e}")
        raise
    
    finally:
        # Shutdown sequence
        system_logger.shutdown_sequence()
        await shutdown_system()


async def initialize_system():
    """Initialize all system components."""
    global config, db_manager, exchange_manager, background_monitor, migration_manager
    
    # Initialize configuration
    environment = os.getenv('ENVIRONMENT', 'development')
    config = init_config(environment=environment)
    logger.info(f"Configuration loaded for environment: {environment}")
    
    # Initialize database manager
    db_manager = DatabaseManager(config)
    
    # Perform database startup validation
    if not await db_manager.startup_validation():
        raise RuntimeError("Database startup validation failed")
    
    # Initialize migration manager
    migration_manager = MigrationManager(config)
    if not migration_manager.initialize():
        logger.warning("Migration system initialization failed")
    
    # Run pending migrations
    if not migration_manager.run_migrations():
        logger.warning("Migration execution failed")
    
    # Initialize exchange manager
    exchange_manager = ExchangeManager(config)
    
    # Connect to exchanges
    connection_results = await exchange_manager.connect_all()
    logger.info(f"Exchange connections: {connection_results}")
    
    # Initialize background monitoring
    background_monitor = BackgroundMonitor(config, exchange_manager, db_manager)
    await background_monitor.start()


async def shutdown_system():
    """Shutdown all system components."""
    global background_monitor, exchange_manager
    
    # Stop background monitoring
    if background_monitor:
        await background_monitor.stop()
    
    # Disconnect from exchanges
    if exchange_manager:
        await exchange_manager.disconnect_all()


# Create FastAPI app
app = FastAPI(
    title="BrainTransactionsManager v2.0.0",
    description="""
# 🚀 BrainTransactionsManager v2.0.0 API
    
**Blessed by Goddess Laxmi for Infinite Abundance** 🙏

## Overview
Production-ready trading API with multi-exchange support, comprehensive monitoring, and robust database management.

## Features
- **Multi-Exchange Support**: Unified interface for stocks and crypto trading
- **Real-time Market Data**: Live price feeds and market information
- **Portfolio Management**: Position tracking and account management
- **Order Management**: Complete order lifecycle management
- **Background Monitoring**: Automated KPI updates and health checks
- **Database Migration**: Robust schema evolution system
- **Security**: CORS protection and input validation

## Quick Start
1. **Health Check**: `GET /health`
2. **Account Info**: `GET /portfolio/account`
3. **Market Data**: `GET /market/data?symbol=BTC/USD`
4. **Place Order**: `POST /buy` or `POST /orders`

## Authentication
Currently configured for development. Production deployment requires proper authentication setup.

## Rate Limits
- Development: 1000 requests/hour
- Production: Configurable via environment variables

---
*Built with FastAPI, PostgreSQL, and Alpaca Trading API*
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    servers=[
        {"url": "http://localhost:8000", "description": "Development server"},
        {"url": "https://api.braintransactions.com", "description": "Production server"}
    ],
    contact={
        "name": "BrainTransactionsManager Support",
        "email": "support@braintransactions.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Add CORS middleware
@app.on_event("startup")
async def setup_cors():
    """Setup CORS middleware after config is loaded."""
    if config:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.security.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


# Dependency to get current config
def get_current_config() -> BrainConfig:
    """Dependency to get current configuration."""
    if not config:
        raise HTTPException(status_code=500, detail="System not initialized")
    return config


# Health endpoints
@app.get("/health")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": "2025-01-27T10:00:00Z"
    }


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check."""
    try:
        health_data = {
            "status": "healthy",
            "version": "2.0.0",
            "components": {}
        }
        
        # Database health
        if db_manager:
            health_data["components"]["database"] = db_manager.get_health_status()
        
        # Exchange health
        if exchange_manager:
            health_data["components"]["exchanges"] = await exchange_manager.health_check()
        
        # Monitoring health
        if background_monitor:
            health_data["components"]["monitoring"] = background_monitor.get_monitoring_status()
        
        return health_data
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "version": "2.0.0"
        }


# Configuration endpoints
@app.get("/config/status")
async def config_status(config: BrainConfig = Depends(get_current_config)):
    """Get configuration status."""
    return config.get_system_status()


# Trading endpoints
@app.post("/orders", response_model=OrderResponse)
async def place_order(order: OrderRequest, config: BrainConfig = Depends(get_current_config)):
    """Place a trading order."""
    try:
        if not exchange_manager:
            raise HTTPException(status_code=500, detail="Exchange manager not initialized")
        
        # Convert string values to enums
        from src.braintransactions.markets.base import OrderSide, OrderType
        
        side_enum = OrderSide(order.side.lower())
        order_type_enum = OrderType(order.order_type.lower())
        
        result = await exchange_manager.place_order(
            symbol=order.symbol,
            side=side_enum,
            order_type=order_type_enum,
            quantity=order.quantity,
            price=order.price,
            strategy_name=order.strategy_name,
            exchange=order.exchange
        )
        
        return OrderResponse(
            success=True,
            order_id=result.get("order_id"),
            message="Order placed successfully",
            data=result
        )
        
    except Exception as e:
        logger.error(f"Order placement error: {e}")
        return OrderResponse(
            success=False,
            message=f"Order placement failed: {str(e)}"
        )


@app.get("/orders")
async def get_orders(
    status: Optional[str] = None,
    strategy_name: Optional[str] = None,
    exchange: Optional[str] = None
):
    """
    Get orders.
    
    Args:
        status: Order status filter (pending, filled, cancelled, rejected). Defaults to 'pending'.
        strategy_name: Filter by strategy name
        exchange: Specific exchange to query
    """
    try:
        if not exchange_manager:
            raise HTTPException(status_code=500, detail="Exchange manager not initialized")
        
        orders = await exchange_manager.get_orders(
            status=status,
            strategy_name=strategy_name,
            exchange=exchange
        )
        
        return {
            "success": True,
            "orders": orders,
            "count": len(orders)
        }
        
    except Exception as e:
        logger.error(f"Get orders error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Test endpoint to isolate the issue
@app.get("/test/orders")
async def test_get_orders(status: str = "filled"):
    """Test endpoint to isolate get_orders issue."""
    try:
        if not exchange_manager:
            raise HTTPException(status_code=500, detail="Exchange manager not initialized")
        
        logger.info(f"Testing get_orders with status: {status}")
        
        # Get orders directly from the adapter
        adapter = exchange_manager.get_adapter()
        orders = await adapter.get_orders(status=status)
        
        return {
            "success": True,
            "status": status,
            "orders_count": len(orders),
            "orders": orders[:5]  # Return first 5 orders
        }
        
    except Exception as e:
        logger.error(f"Test get_orders error: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": str(type(e))
        }


@app.get("/orders/{order_id}")
async def get_order_status(order_id: str, exchange: Optional[str] = None):
    """Get order status."""
    try:
        if not exchange_manager:
            raise HTTPException(status_code=500, detail="Exchange manager not initialized")
        
        order_status = await exchange_manager.get_order_status(order_id, exchange)
        
        return {
            "success": True,
            "order": order_status
        }
        
    except Exception as e:
        logger.error(f"Get order status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/orders/{order_id}")
async def cancel_order(order_id: str, exchange: Optional[str] = None):
    """Cancel an order."""
    try:
        if not exchange_manager:
            raise HTTPException(status_code=500, detail="Exchange manager not initialized")
        
        result = await exchange_manager.cancel_order(order_id, exchange)
        
        return {
            "success": True,
            "message": "Order cancelled successfully",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Cancel order error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Portfolio endpoints
@app.get("/portfolio/positions")
async def get_positions(strategy_name: Optional[str] = None, exchange: Optional[str] = None):
    """Get portfolio positions."""
    try:
        if not exchange_manager:
            raise HTTPException(status_code=500, detail="Exchange manager not initialized")
        
        positions = await exchange_manager.get_positions(strategy_name, exchange)
        
        return {
            "success": True,
            "positions": positions,
            "count": len(positions)
        }
        
    except Exception as e:
        logger.error(f"Get positions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio/account")
async def get_account_info(exchange: Optional[str] = None):
    """Get account information."""
    try:
        if not exchange_manager:
            raise HTTPException(status_code=500, detail="Exchange manager not initialized")
        
        account_info = await exchange_manager.get_account_info(exchange)
        
        return {
            "success": True,
            "account": account_info
        }
        
    except Exception as e:
        logger.error(f"Get account info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Market data endpoint (query parameter only; supports symbols like BTC/USD)
@app.get("/market/data")
async def get_market_data(symbol: str, exchange: Optional[str] = None):
    """Get market data for symbol (query parameter form).

    Notes:
        - Supports crypto symbols containing '/': e.g., BTC/USD
        - Path variant is intentionally not supported to avoid '/' routing issues
    """
    try:
        if not exchange_manager:
            raise HTTPException(status_code=500, detail="Exchange manager not initialized")

        # Pass through exactly as provided (no alternative formats)
        market_data = await exchange_manager.get_market_data(symbol, exchange)

        return {
            "success": True,
            "data": market_data
        }

    except Exception as e:
        logger.error(f"Get market data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Exchange management endpoints
@app.get("/exchanges")
async def get_exchanges():
    """Get supported exchanges."""
    try:
        if not exchange_manager:
            raise HTTPException(status_code=500, detail="Exchange manager not initialized")
        
        return {
            "success": True,
            "exchanges": exchange_manager.get_supported_exchanges(),
            "adapter_info": exchange_manager.get_adapter_info()
        }
        
    except Exception as e:
        logger.error(f"Get exchanges error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Convenience trading endpoints
@app.post("/buy")
async def buy_order(request: BuyOrderRequest):
    """Convenience endpoint for buy orders."""
    order = OrderRequest(
        symbol=request.symbol,
        side="buy",
        order_type=request.order_type,
        quantity=request.quantity,
        price=request.price,
        strategy_name=request.strategy_name,
        exchange=request.exchange
    )
    return await place_order(order)


@app.post("/sell")
async def sell_order(request: SellOrderRequest):
    """Convenience endpoint for sell orders."""
    order = OrderRequest(
        symbol=request.symbol,
        side="sell",
        order_type=request.order_type,
        quantity=request.quantity,
        price=request.price,
        strategy_name=request.strategy_name,
        exchange=request.exchange
    )
    return await place_order(order)


@app.post("/close/{symbol}")
async def close_position(symbol: str, strategy_name: str = "default", exchange: Optional[str] = None):
    """Close entire position for symbol."""
    try:
        if not exchange_manager:
            raise HTTPException(status_code=500, detail="Exchange manager not initialized")
        
        result = await exchange_manager.close_position(symbol, strategy_name, exchange)
        
        return {
            "success": True,
            "message": f"Position closed for {symbol}",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"Close position error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Migration endpoints
@app.get("/migrations/status")
async def migration_status():
    """Get migration status."""
    try:
        if not migration_manager:
            raise HTTPException(status_code=500, detail="Migration manager not initialized")
        
        return migration_manager.validate_migrations()
        
    except Exception as e:
        logger.error(f"Migration status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/migrations/run")
async def run_migrations():
    """Run pending migrations."""
    try:
        if not migration_manager:
            raise HTTPException(status_code=500, detail="Migration manager not initialized")
        
        success = migration_manager.run_migrations()
        
        return {
            "success": success,
            "message": "Migrations completed" if success else "Migration failed"
        }
        
    except Exception as e:
        logger.error(f"Run migrations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Additional portfolio endpoints
@app.get("/portfolio/summary")
async def get_portfolio_summary(
    strategy_name: Optional[str] = None,
    exchange: Optional[str] = None
):
    """
    Get portfolio summary with P&L, positions, and performance metrics.
    
    Args:
        strategy_name: Filter by strategy name
        exchange: Specific exchange to query
    """
    try:
        if not exchange_manager:
            raise HTTPException(status_code=500, detail="Exchange manager not initialized")
        
        # Get positions
        positions = await exchange_manager.get_positions(strategy_name, exchange)
        
        # Get account info
        account_info = await exchange_manager.get_account_info(exchange)
        
        # Calculate summary metrics
        total_positions = len(positions)
        total_market_value = sum(pos.get('market_value', 0) for pos in positions)
        total_unrealized_pl = sum(pos.get('unrealized_pl', 0) for pos in positions)
        
        # Group by asset type
        stock_positions = [p for p in positions if p.get('asset_type') == 'stock']
        crypto_positions = [p for p in positions if p.get('asset_type') == 'crypto']
        
        summary = {
            "success": True,
            "portfolio_summary": {
                "total_positions": total_positions,
                "total_market_value": total_market_value,
                "total_unrealized_pl": total_unrealized_pl,
                "account_cash": account_info.get('cash', 0),
                "account_buying_power": account_info.get('buying_power', 0),
                "portfolio_value": account_info.get('portfolio_value', 0),
                "asset_breakdown": {
                    "stocks": {
                        "count": len(stock_positions),
                        "market_value": sum(p.get('market_value', 0) for p in stock_positions),
                        "unrealized_pl": sum(p.get('unrealized_pl', 0) for p in stock_positions)
                    },
                    "crypto": {
                        "count": len(crypto_positions),
                        "market_value": sum(p.get('market_value', 0) for p in crypto_positions),
                        "unrealized_pl": sum(p.get('unrealized_pl', 0) for p in crypto_positions)
                    }
                },
                "strategy_name": strategy_name or "all",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Portfolio summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/portfolio/strategy/{strategy_name}")
async def get_strategy_summary(strategy_name: str, exchange: Optional[str] = None):
    """
    Get detailed summary for a specific strategy.
    
    Args:
        strategy_name: Strategy name to analyze
        exchange: Specific exchange to query
    """
    try:
        if not exchange_manager:
            raise HTTPException(status_code=500, detail="Exchange manager not initialized")
        
        # Get positions for specific strategy
        positions = await exchange_manager.get_positions(strategy_name, exchange)
        
        # Get orders for strategy
        orders = await exchange_manager.get_orders(strategy_name=strategy_name, exchange=exchange)
        
        # Calculate strategy metrics
        total_positions = len(positions)
        total_market_value = sum(pos.get('market_value', 0) for pos in positions)
        total_unrealized_pl = sum(pos.get('unrealized_pl', 0) for pos in positions)
        
        # Calculate order statistics
        total_orders = len(orders)
        filled_orders = len([o for o in orders if o.get('status') == 'filled'])
        pending_orders = len([o for o in orders if o.get('status') == 'pending'])
        
        strategy_summary = {
            "success": True,
            "strategy_summary": {
                "strategy_name": strategy_name,
                "positions": {
                    "total": total_positions,
                    "market_value": total_market_value,
                    "unrealized_pl": total_unrealized_pl
                },
                "orders": {
                    "total": total_orders,
                    "filled": filled_orders,
                    "pending": pending_orders,
                    "fill_rate": filled_orders / total_orders if total_orders > 0 else 0
                },
                "positions_detail": positions,
                "recent_orders": orders[:10],  # Last 10 orders
                "timestamp": datetime.now().isoformat()
            }
        }
        
        return strategy_summary
        
    except Exception as e:
        logger.error(f"Strategy summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/strategies")
async def list_strategies():
    """List distinct strategy names from the database."""
    try:
        if not db_manager or not config:
            raise HTTPException(status_code=500, detail="System not initialized")

        schema = config.database.schema
        query = f"SELECT DISTINCT strategy_name FROM {schema}.portfolio_positions ORDER BY strategy_name"

        # Execute synchronously via thread to avoid blocking loop
        results = await asyncio.get_event_loop().run_in_executor(
            None, lambda: db_manager.execute_query(query)
        )

        strategies = [row.get("strategy_name") for row in results if row.get("strategy_name")]

        return {
            "success": True,
            "strategies": strategies,
            "count": len(strategies)
        }

    except Exception as e:
        logger.error(f"List strategies error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


"""
NOTE: /orders/statistics endpoint removed in v2.0.0 due to instability and limited value.
"""


# Emergency stop endpoint
@app.post("/emergency/stop")
async def emergency_stop(request: EmergencyStopRequest):
    """
    Emergency stop all trading activities.
    
    Args:
        request: Emergency stop request with reason and optional strategy
    """
    try:
        if not exchange_manager:
            raise HTTPException(status_code=500, detail="Exchange manager not initialized")
        
        # Cancel all pending orders
        pending_orders = await exchange_manager.get_orders(status='pending')
        cancelled_count = 0
        
        for order in pending_orders:
            try:
                await exchange_manager.cancel_order(order['order_id'])
                cancelled_count += 1
            except Exception as e:
                logger.warning(f"Failed to cancel order {order['order_id']}: {e}")
        
        # Stop background monitoring
        if background_monitor:
            background_monitor.stop()
        
        result = {
            "success": True,
            "emergency_stop": {
                "status": "activated",
                "reason": request.reason,
                "strategy_name": request.strategy_name or "all",
                "cancelled_orders": cancelled_count,
                "background_monitoring_stopped": background_monitor is not None,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        logger.warning(f"🚨 EMERGENCY STOP ACTIVATED: {request.reason}")
        return result
        
    except Exception as e:
        logger.error(f"Emergency stop error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Kill switch endpoints
@app.post("/kill-switch")
async def manage_kill_switch(request: KillSwitchRequest):
    """
    Manage kill switch for emergency control.
    
    Args:
        request: Kill switch action (activate/deactivate)
    """
    try:
        if request.action == "activate":
            # Activate kill switch
            if hasattr(exchange_manager, 'activate_kill_switch'):
                exchange_manager.activate_kill_switch(request.reason or "Kill switch activated")
            
            result = {
                "success": True,
                "kill_switch": {
                    "status": "activated",
                    "reason": request.reason or "Kill switch activated",
                    "timestamp": datetime.now().isoformat()
                }
            }
            logger.warning(f"🚨 KILL SWITCH ACTIVATED: {request.reason}")
            
        elif request.action == "deactivate":
            # Deactivate kill switch
            if hasattr(exchange_manager, 'deactivate_kill_switch'):
                exchange_manager.deactivate_kill_switch()
            
            result = {
                "success": True,
                "kill_switch": {
                    "status": "deactivated",
                    "timestamp": datetime.now().isoformat()
                }
            }
            logger.info("✅ Kill switch deactivated")
            
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Use 'activate' or 'deactivate'")
        
        return result
        
    except Exception as e:
        logger.error(f"Kill switch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/kill-switch/status")
async def get_kill_switch_status():
    """Get current kill switch status."""
    try:
        if not exchange_manager:
            raise HTTPException(status_code=500, detail="Exchange manager not initialized")
        
        is_active = False
        if hasattr(exchange_manager, 'is_kill_switch_active'):
            is_active = exchange_manager.is_kill_switch_active()
        
        return {
            "success": True,
            "kill_switch_status": {
                "active": is_active,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Kill switch status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Close all positions endpoint
@app.post("/portfolio/close-all")
async def close_all_positions(
    strategy_name: Optional[str] = None,
    exchange: Optional[str] = None
):
    """
    Close all positions for a strategy or all strategies.
    
    Args:
        strategy_name: Strategy name to close positions for (optional)
        exchange: Specific exchange to use
    """
    try:
        if not exchange_manager:
            raise HTTPException(status_code=500, detail="Exchange manager not initialized")
        
        # Get current positions
        positions = await exchange_manager.get_positions(strategy_name, exchange)
        
        closed_positions = []
        failed_positions = []
        
        for position in positions:
            try:
                result = await exchange_manager.close_position(
                    position['symbol'], 
                    strategy_name or position.get('strategy_name', 'default'),
                    exchange
                )
                closed_positions.append({
                    "symbol": position['symbol'],
                    "quantity": position['quantity'],
                    "result": result
                })
            except Exception as e:
                failed_positions.append({
                    "symbol": position['symbol'],
                    "error": str(e)
                })
        
        return {
            "success": True,
            "close_all_positions": {
                "strategy_name": strategy_name or "all",
                "total_positions": len(positions),
                "closed_positions": len(closed_positions),
                "failed_positions": len(failed_positions),
                "closed_details": closed_positions,
                "failed_details": failed_positions,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Close all positions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc) if config and not config.trading.paper_trading else "Internal server error"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Get configuration
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    
    logger.info(f"🚀 Starting BrainTransactionsManager v2.0.0 on {host}:{port}")
    
    uvicorn.run(
        "server:app",
        host=host,
        port=port,
        reload=os.getenv("RELOAD", "false").lower() == "true",
        log_level="info"
    )
