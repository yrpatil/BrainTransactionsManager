#!/usr/bin/env python3
"""
🙏 Version Loader
Blessed by Goddess Laxmi for Infinite Abundance

Dynamic loading of API version handlers and FastAPI sub-applications.
Supports both frozen version snapshots and live development code.
"""

import sys
import json
import logging
import importlib.util
from pathlib import Path
from typing import Dict, Optional, Any
from fastapi import FastAPI

logger = logging.getLogger(__name__)

class VersionLoader:
    """Dynamically loads and manages API version handlers."""
    
    def __init__(self, config_path: str = "config/api_versions.json"):
        """Initialize version loader with configuration."""
        self.config_path = Path(config_path)
        self.config: Dict = {}
        self.loaded_apps: Dict[str, FastAPI] = {}
        self.load_config()
        
    def load_config(self) -> None:
        """Load API versions configuration."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise
            
    def get_version_handler_path(self, version: str) -> Optional[str]:
        """Get file path for version handler."""
        handlers = self.config.get('version_handlers', {})
        return handlers.get(version)
        
    def create_version_app(self, version: str) -> FastAPI:
        """
        Create FastAPI application for specific version.
        
        Args:
            version: API version to load
            
        Returns:
            FastAPI application instance
        """
        if version in self.loaded_apps:
            return self.loaded_apps[version]
            
        try:
            # For development mode, use current server
            if version == 'development':
                return self.create_development_app()
            
            # For versioned releases, create wrapper with basic endpoints
            app = self.create_basic_version_app(version)
            
            # Cache the loaded app
            self.loaded_apps[version] = app
            
            logger.info(f"Created FastAPI app for version: {version}")
            return app
            
        except Exception as e:
            logger.error(f"Failed to create app for version {version}: {e}")
            raise
            
    async def get_account_data(self, trading_manager):
        """Get account data using the correct method based on trading manager structure."""
        try:
            # Try the standard get_account_info method first
            if hasattr(trading_manager, 'get_account_info'):
                result = trading_manager.get_account_info()
                if hasattr(result, '__await__'):
                    result = await result
                return result
                
            # Try accessing through different client attributes
            client = None
            if hasattr(trading_manager, 'alpaca_client'):
                client = trading_manager.alpaca_client
            elif hasattr(trading_manager, 'client'):
                client = trading_manager.client  
            elif hasattr(trading_manager, 'alpaca'):
                client = trading_manager.alpaca
            elif hasattr(trading_manager, '_client'):
                client = trading_manager._client
                
            if client and hasattr(client, 'get_account'):
                account = client.get_account()
                result = account._raw if hasattr(account, '_raw') else dict(account)
                return result
                
            # If no client found, try to get account through portfolio manager
            if hasattr(trading_manager, 'portfolio_manager'):
                pm = trading_manager.portfolio_manager
                if hasattr(pm, 'get_account_info'):
                    result = pm.get_account_info()
                    if hasattr(result, '__await__'):
                        result = await result
                    return result
                    
            # Last resort - check what attributes the trading manager actually has
            attrs = [attr for attr in dir(trading_manager) if not attr.startswith('_')]
            logger.warning(f"Trading manager attributes: {attrs}")
            
            return {"error": "No account access method found", "available_attributes": attrs}
            
        except Exception as e:
            logger.error(f"Account data access error: {e}")
            return {"error": str(e)}
    
    def _get_trading_manager(self):
        """Create and return a trading manager from core modules without MCP."""
        try:
            # Ensure 'src' is on sys.path to import project modules
            src_path = str(Path.cwd() / "src")
            if src_path not in sys.path:
                sys.path.insert(0, src_path)
            # Import from core packages
            from braintransactions.core.config import BrainConfig
            from braintransactions.modules.laxmi_yantra.trading_manager import LaxmiYantra
            config = BrainConfig()
            return LaxmiYantra(config)
        except Exception as e:
            logger.error(f"Failed to initialize trading manager: {e}")
            raise

    def _get_db_manager(self):
        """Create and return a database manager."""
        try:
            src_path = str(Path.cwd() / "src")
            if src_path not in sys.path:
                sys.path.insert(0, src_path)
            from braintransactions.core.config import BrainConfig
            from braintransactions.database.connection import DatabaseManager
            config = BrainConfig()
            return DatabaseManager(config)
        except Exception as e:
            logger.error(f"Failed to initialize database manager: {e}")
            raise
            
    def create_development_app(self) -> FastAPI:
        """Create development app that mirrors current server functionality."""
        try:
            from fastapi import FastAPI
            from fastapi.responses import JSONResponse
            
            app = FastAPI(
                title="Laxmi-yantra Trading API Development",
                description="Development version - Live code",
                version="development"
            )
            
            # Add basic health check
            @app.get("/health")
            async def health_check():
                return {"status": "healthy", "version": "development", "mode": "live"}
                
            # Add basic tools endpoints
            @app.post("/tools/get_account_status")
            async def get_account_status():
                try:
                    trading_manager = self._get_trading_manager()
                    result = await self.get_account_data(trading_manager)
                    return self.serialize_result(result)
                except Exception as e:
                    logger.error(f"Development account status error: {e}")
                    return {"error": str(e), "version": "development"}
                    
            @app.get("/resources/account_info")
            async def account_info():
                try:
                    trading_manager = self._get_trading_manager()
                    result = await self.get_account_data(trading_manager)
                    return self.serialize_result(result)
                except Exception as e:
                    logger.error(f"Development account info error: {e}")
                    return {"error": str(e), "version": "development"}
                    
            # Add portfolio summary endpoint
            @app.get("/resources/portfolio_summary")
            async def portfolio_summary():
                try:
                    trading_manager = self._get_trading_manager()
                    
                    if hasattr(trading_manager, 'portfolio_manager'):
                        result = trading_manager.portfolio_manager.get_portfolio_summary()
                        if hasattr(result, '__await__'):
                            result = await result
                    else:
                        result = {"error": "Portfolio summary not available"}
                        
                    return self.serialize_result(result)
                except Exception as e:
                    logger.error(f"Development portfolio summary error: {e}")
                    return {"error": str(e), "version": "development"}
            
            # Add strategy summary endpoint
            @app.get("/resources/strategy_summary")
            async def strategy_summary(strategy_name: str):
                try:
                    trading_manager = self._get_trading_manager()
                    if hasattr(trading_manager, 'portfolio_manager'):
                        result = trading_manager.portfolio_manager.get_strategy_summary(strategy_name)
                        if hasattr(result, '__await__'):
                            result = await result
                    else:
                        result = {"error": "Strategy summary not available"}
                    return self.serialize_result(result)
                except Exception as e:
                    logger.error(f"Development strategy summary error: {e}")
                    return {"error": str(e), "version": "development"}

            # Analytics: performance portfolio summary with PnL
            @app.get("/analytics/performance/portfolio_summary")
            async def analytics_portfolio_summary(strategy_name: str | None = None):
                try:
                    db = self._get_db_manager()
                    # Enrich positions with latest price if available; fallback to avg_entry_price
                    query = (
                        "SELECT pp.strategy_name, pp.ticker, pp.quantity, pp.avg_entry_price, "
                        "COALESCE(od.close, pp.avg_entry_price) AS current_price, "
                        "CASE WHEN COALESCE(od.close, pp.avg_entry_price) > 0 AND pp.avg_entry_price > 0 "
                        "THEN ROUND(((COALESCE(od.close, pp.avg_entry_price) - pp.avg_entry_price) / pp.avg_entry_price * 100)::numeric, 4) "
                        "ELSE 0 END AS unrealized_pnl_percent, "
                        "ROUND((pp.quantity * (COALESCE(od.close, pp.avg_entry_price) - pp.avg_entry_price))::numeric, 8) AS unrealized_pnl_amount, "
                        "ROUND((pp.quantity * COALESCE(od.close, pp.avg_entry_price))::numeric, 8) AS market_value, "
                        "pp.last_updated, pp.created_at, od.price_ts "
                        "FROM portfolio_positions pp "
                        "LEFT JOIN LATERAL ("
                        "    SELECT close, timestamp AS price_ts FROM ohlc_data "
                        "    WHERE ticker = pp.ticker "
                        "       OR ticker = REPLACE(pp.ticker, '/', '') "
                        "       OR REPLACE(ticker, '/', '') = pp.ticker "
                        "    ORDER BY timestamp DESC LIMIT 1"
                        ") od ON true "
                        "WHERE pp.quantity != 0 "
                    )
                    params = {}
                    if strategy_name:
                        query += "AND pp.strategy_name = %(strategy_name)s "
                        params['strategy_name'] = strategy_name
                    query += "ORDER BY pp.strategy_name, pp.ticker"
                    rows = db.execute_query(query, params) or []

                    by_strategy: Dict[str, Dict[str, Any]] = {}
                    total_mv = 0.0
                    total_upnl = 0.0
                    avg_upnl_pct_acc = 0.0
                    total_annual_weighted = 0.0
                    last_price_ts = None
                    from datetime import datetime
                    for r in rows:
                        sn = r.get('strategy_name')
                        by = by_strategy.setdefault(sn, {
                            'strategy_name': sn,
                            'positions_count': 0,
                            'total_market_value': 0.0,
                            'total_unrealized_pnl': 0.0,
                            'annual_weighted_sum': 0.0
                        })
                        by['positions_count'] += 1
                        mv = float(r.get('market_value') or 0)
                        upnl = float(r.get('unrealized_pnl_amount') or 0)
                        upnl_pct = float(r.get('unrealized_pnl_percent') or 0)
                        avg_upnl_pct_acc += upnl_pct
                        by['total_market_value'] += mv
                        by['total_unrealized_pnl'] += upnl
                        total_mv += mv
                        total_upnl += upnl
                        ts = r.get('price_ts')
                        if ts and (last_price_ts is None or ts > last_price_ts):
                            last_price_ts = ts
                        # Annualize simple PnL% based on holding period
                        try:
                            ct = r.get('created_at')
                            # If values are strings, attempt parse
                            if isinstance(ts, str):
                                ts_dt = datetime.fromisoformat(ts)
                            else:
                                ts_dt = ts or datetime.now()
                            if isinstance(ct, str):
                                ct_dt = datetime.fromisoformat(ct)
                            else:
                                ct_dt = ct or ts_dt
                            days = max((ts_dt - ct_dt).total_seconds() / 86400.0, 1.0)
                        except Exception:
                            days = 365.0
                        annualized_pct_pos = upnl_pct * (365.0 / days)
                        by['annual_weighted_sum'] += annualized_pct_pos * mv
                        total_annual_weighted += annualized_pct_pos * mv
                    for s in by_strategy.values():
                        mv = s['total_market_value']
                        pct = (s['total_unrealized_pnl'] / mv * 100) if mv else 0.0
                        s['net_unrealized_pnl_pct'] = pct
                        s['net_unrealized_anual_pnl_pct'] = (s['annual_weighted_sum'] / mv) if mv else 0.0

                    result = {
                        'positions': rows,
                        'by_strategy': list(by_strategy.values()),
                        'totals': {
                            'total_positions': len(rows),
                            'total_market_value': total_mv,
                            'net_unrealized_pnl': total_upnl,
                            'net_unrealized_pnl_pct': (total_upnl / total_mv * 100) if total_mv else 0.0,
                            'net_unrealized_anual_pnl_pct': (total_annual_weighted / total_mv) if total_mv else 0.0,
                            'strategies_count': len(by_strategy),
                            'avg_unrealized_pnl_pct': (avg_upnl_pct_acc / len(rows)) if rows else 0.0,
                            'position_concentration_top_pct': (max([float(r.get('market_value') or 0) for r in rows]) / total_mv * 100) if rows and total_mv else 0.0,
                            'last_price_timestamp': last_price_ts
                        }
                    }
                    return self.serialize_result(result)
                except Exception as e:
                    logger.error(f"Development analytics portfolio summary error: {e}")
                    return {"error": str(e), "version": "development"}

            # Analytics: strategy summary (same fields, filtered by strategy)
            @app.get("/analytics/performance/strategy_summary")
            async def analytics_strategy_summary(strategy_name: str):
                try:
                    db = self._get_db_manager()
                    query = (
                        "SELECT pp.strategy_name, pp.ticker, pp.quantity, pp.avg_entry_price, "
                        "COALESCE(od.close, pp.avg_entry_price) AS current_price, "
                        "CASE WHEN COALESCE(od.close, pp.avg_entry_price) > 0 AND pp.avg_entry_price > 0 "
                        "THEN ROUND(((COALESCE(od.close, pp.avg_entry_price) - pp.avg_entry_price) / pp.avg_entry_price * 100)::numeric, 4) "
                        "ELSE 0 END AS unrealized_pnl_percent, "
                        "ROUND((pp.quantity * (COALESCE(od.close, pp.avg_entry_price) - pp.avg_entry_price))::numeric, 8) AS unrealized_pnl_amount, "
                        "ROUND((pp.quantity * COALESCE(od.close, pp.avg_entry_price))::numeric, 8) AS market_value, "
                        "pp.last_updated, pp.created_at, od.price_ts "
                        "FROM portfolio_positions pp "
                        "LEFT JOIN LATERAL ("
                        "    SELECT close, timestamp AS price_ts FROM ohlc_data "
                        "    WHERE ticker = pp.ticker "
                        "       OR ticker = REPLACE(pp.ticker, '/', '') "
                        "       OR REPLACE(ticker, '/', '') = pp.ticker "
                        "    ORDER BY timestamp DESC LIMIT 1"
                        ") od ON true "
                        "WHERE pp.quantity != 0 AND pp.strategy_name = %(s)s "
                        "ORDER BY pp.ticker"
                    )
                    rows = db.execute_query(query, {'s': strategy_name}) or []

                    by_strategy: Dict[str, Dict[str, Any]] = {}
                    total_mv = 0.0
                    total_upnl = 0.0
                    avg_upnl_pct_acc = 0.0
                    total_annual_weighted = 0.0
                    last_price_ts = None
                    from datetime import datetime
                    for r in rows:
                        sn = r.get('strategy_name')
                        by = by_strategy.setdefault(sn, {
                            'strategy_name': sn,
                            'positions_count': 0,
                            'total_market_value': 0.0,
                            'total_unrealized_pnl': 0.0,
                            'annual_weighted_sum': 0.0
                        })
                        by['positions_count'] += 1
                        mv = float(r.get('market_value') or 0)
                        upnl = float(r.get('unrealized_pnl_amount') or 0)
                        upnl_pct = float(r.get('unrealized_pnl_percent') or 0)
                        avg_upnl_pct_acc += upnl_pct
                        by['total_market_value'] += mv
                        by['total_unrealized_pnl'] += upnl
                        total_mv += mv
                        total_upnl += upnl
                        ts = r.get('price_ts')
                        if ts and (last_price_ts is None or ts > last_price_ts):
                            last_price_ts = ts
                        try:
                            ct = r.get('created_at')
                            if isinstance(ts, str):
                                ts_dt = datetime.fromisoformat(ts)
                            else:
                                ts_dt = ts or datetime.now()
                            if isinstance(ct, str):
                                ct_dt = datetime.fromisoformat(ct)
                            else:
                                ct_dt = ct or ts_dt
                            days = max((ts_dt - ct_dt).total_seconds() / 86400.0, 1.0)
                        except Exception:
                            days = 365.0
                        annualized_pct_pos = upnl_pct * (365.0 / days)
                        by['annual_weighted_sum'] += annualized_pct_pos * mv
                        total_annual_weighted += annualized_pct_pos * mv

                    for s in by_strategy.values():
                        mv = s['total_market_value']
                        pct = (s['total_unrealized_pnl'] / mv * 100) if mv else 0.0
                        s['net_unrealized_pnl_pct'] = pct
                        s['net_unrealized_anual_pnl_pct'] = (s['annual_weighted_sum'] / mv) if mv else 0.0

                    result = {
                        'positions': rows,
                        'by_strategy': list(by_strategy.values()),
                        'totals': {
                            'total_positions': len(rows),
                            'total_market_value': total_mv,
                            'net_unrealized_pnl': total_upnl,
                            'net_unrealized_pnl_pct': (total_upnl / total_mv * 100) if total_mv else 0.0,
                            'net_unrealized_anual_pnl_pct': (total_annual_weighted / total_mv) if total_mv else 0.0,
                            'strategies_count': len(by_strategy),
                            'avg_unrealized_pnl_pct': (avg_upnl_pct_acc / len(rows)) if rows else 0.0,
                            'position_concentration_top_pct': (max([float(r.get('market_value') or 0) for r in rows]) / total_mv * 100) if rows and total_mv else 0.0,
                            'last_price_timestamp': last_price_ts
                        }
                    }
                    return self.serialize_result(result)
                except Exception as e:
                    logger.error(f"Development analytics strategy summary error: {e}")
                    return {"error": str(e), "version": "development"}

            # Analytics: KPIs for quick monitoring (simple approximations)
            @app.get("/analytics/performance/kpis")
            async def analytics_kpis(strategy_name: str | None = None):
                try:
                    # Reuse portfolio summary analytics to compute KPIs
                    resp = await analytics_portfolio_summary(strategy_name)
                    # resp is already JSON-safe; compute additional KPIs
                    def safe(val, default=0.0):
                        try:
                            return float(val)
                        except Exception:
                            return default
                    totals = resp.get('totals', {}) if isinstance(resp, dict) else {}
                    mv = safe(totals.get('total_market_value'))
                    net_upnl = safe(totals.get('net_unrealized_pnl'))
                    net_upnl_pct = safe(totals.get('net_unrealized_pnl_pct'))
                    avg_upnl_pct = safe(totals.get('avg_unrealized_pnl_pct')) if totals else 0.0
                    # Simple Sharpe proxy: annualized return divided by proxy of volatility
                    # Here, volatility proxy uses MAD of position PnL% (very rough, avoids heavy time-series)
                    positions = resp.get('positions', []) if isinstance(resp, dict) else []
                    pnl_pcts = [safe(p.get('unrealized_pnl_percent')) for p in positions if p]
                    if pnl_pcts:
                        mean = sum(pnl_pcts) / len(pnl_pcts)
                        mad = sum(abs(x - mean) for x in pnl_pcts) / len(pnl_pcts)
                    else:
                        mad = 0.0
                    annual_ret_pct = safe(totals.get('net_unrealized_anual_pnl_pct'))
                    sharpe_proxy = (annual_ret_pct / (mad if mad > 0 else 1.0))
                    result = {
                        'kpis': {
                            'portfolio_market_value': mv,
                            'net_unrealized_pnl': net_upnl,
                            'net_unrealized_pnl_pct': net_upnl_pct,
                            'annualized_unrealized_pnl_pct': annual_ret_pct,
                            'avg_position_unrealized_pnl_pct': avg_upnl_pct,
                            'sharpe_ratio_proxy': sharpe_proxy,
                        },
                        'source': 'analytics_portfolio_summary'
                    }
                    return self.serialize_result(result)
                except Exception as e:
                    logger.error(f"Development analytics KPIs error: {e}")
                    return {"error": str(e), "version": "development"}

            # Analytics: Top movers by absolute PnL%
            @app.get("/analytics/performance/top_movers")
            async def analytics_top_movers(limit: int = 5, strategy_name: str | None = None):
                try:
                    summary = await analytics_portfolio_summary(strategy_name)
                    positions = summary.get('positions', []) if isinstance(summary, dict) else []
                    # Sort by absolute unrealized_pnl_percent desc
                    positions.sort(key=lambda p: abs(float(p.get('unrealized_pnl_percent', 0) or 0)), reverse=True)
                    return self.serialize_result({
                        'top_movers': positions[:max(0, min(limit, 100))]
                    })
                except Exception as e:
                    logger.error(f"Development analytics top movers error: {e}")
                    return {"error": str(e), "version": "development"}
                    
            return app
            
        except Exception as e:
            logger.error(f"Failed to create development app: {e}")
            # Fallback to basic app
            return self.create_basic_version_app("development")
            
    def create_basic_version_app(self, version: str) -> FastAPI:
        """Create a basic version app with standard endpoints."""
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        
        app = FastAPI(
            title=f"Laxmi-yantra Trading API {version}",
            description=f"Trading API version {version} - Blessed by Goddess Laxmi",
            version=version
        )
        
        # Add basic health check
        @app.get("/health")
        async def health_check():
            return {"status": "healthy", "version": version}
            
        # Add basic account info endpoint
        @app.get("/resources/account_info")
        async def account_info():
            try:
                trading_manager = self._get_trading_manager()
                result = await self.get_account_data(trading_manager)
                return self.serialize_result(result)
            except Exception as e:
                logger.error(f"Version {version} account info error: {e}")
                return {
                    "error": f"Account info not available in {version}",
                    "details": str(e),
                    "version": version
                }
                
        # Add basic tool endpoints
        @app.post("/tools/get_account_status")
        async def get_account_status():
            try:
                trading_manager = self._get_trading_manager()
                result = await self.get_account_data(trading_manager)
                return self.serialize_result(result)
            except Exception as e:
                logger.error(f"Version {version} account status error: {e}")
                return {
                    "error": f"Account status not available in {version}",
                    "details": str(e),
                    "version": version
                }
                
        # Add basic portfolio summary
        @app.get("/resources/portfolio_summary")
        async def portfolio_summary():
            try:
                trading_manager = self._get_trading_manager()
                
                if hasattr(trading_manager, 'portfolio_manager'):
                    result = trading_manager.portfolio_manager.get_portfolio_summary()
                    if hasattr(result, '__await__'):
                        result = await result
                else:
                    result = {"message": f"Portfolio summary not available in {version}"}
                    
                return self.serialize_result(result)
            except Exception as e:
                logger.error(f"Version {version} portfolio summary error: {e}")
                return {
                    "error": f"Portfolio summary not available in {version}",
                    "details": str(e),
                    "version": version
                }
                
        # Add strategy summary endpoint
        @app.get("/resources/strategy_summary")
        async def strategy_summary(strategy_name: str):
            try:
                trading_manager = self._get_trading_manager()
                if hasattr(trading_manager, 'portfolio_manager'):
                    result = trading_manager.portfolio_manager.get_strategy_summary(strategy_name)
                    if hasattr(result, '__await__'):
                        result = await result
                else:
                    result = {"message": f"Strategy summary not available in {version}"}
                return self.serialize_result(result)
            except Exception as e:
                logger.error(f"Version {version} strategy summary error: {e}")
                return {
                    "error": f"Strategy summary not available in {version}",
                    "details": str(e),
                    "version": version
                }

        # Agent guide endpoint: return latest generated guide for this version
        @app.get("/get_agent_guide")
        async def get_agent_guide():
            try:
                from pathlib import Path
                docs_path = Path.cwd() / "api_versions" / version / "AI_AGENT_USAGE_GUIDE.md"
                if not docs_path.exists():
                    # Generate on-demand if missing
                    try:
                        from release.api_docs_generator import APIDocsGenerator
                        g = APIDocsGenerator(str(Path.cwd()))
                        docs = g.generate_version_docs(version)
                        g.save_version_docs(version, docs)
                    except Exception as ge:
                        logger.warning(f"On-demand guide generation failed: {ge}")
                # Read and return as text/markdown
                if docs_path.exists():
                    with open(docs_path, 'r') as f:
                        content = f.read()
                    return content
                return {"error": "Guide not available", "version": version}
            except Exception as e:
                logger.error(f"Failed to load agent guide: {e}")
                return {"error": str(e), "version": version}

        # Analytics: performance portfolio summary with PnL
        @app.get("/analytics/performance/portfolio_summary")
        async def analytics_portfolio_summary(strategy_name: str | None = None):
            try:
                db = self._get_db_manager()
                query = (
                    "SELECT pp.strategy_name, pp.ticker, pp.quantity, pp.avg_entry_price, "
                    "COALESCE(od.close, pp.avg_entry_price) AS current_price, "
                    "CASE WHEN COALESCE(od.close, pp.avg_entry_price) > 0 AND pp.avg_entry_price > 0 "
                    "THEN ROUND(((COALESCE(od.close, pp.avg_entry_price) - pp.avg_entry_price) / pp.avg_entry_price * 100)::numeric, 4) "
                    "ELSE 0 END AS unrealized_pnl_percent, "
                    "ROUND((pp.quantity * (COALESCE(od.close, pp.avg_entry_price) - pp.avg_entry_price))::numeric, 8) AS unrealized_pnl_amount, "
                    "ROUND((pp.quantity * COALESCE(od.close, pp.avg_entry_price))::numeric, 8) AS market_value, "
                    "pp.last_updated, pp.created_at, od.price_ts "
                    "FROM portfolio_positions pp "
                    "LEFT JOIN LATERAL ("
                    "    SELECT close, timestamp AS price_ts FROM ohlc_data "
                    "    WHERE ticker = pp.ticker "
                    "       OR ticker = REPLACE(pp.ticker, '/', '') "
                    "       OR REPLACE(ticker, '/', '') = pp.ticker "
                    "    ORDER BY timestamp DESC LIMIT 1"
                    ") od ON true "
                    "WHERE pp.quantity != 0 "
                )
                params = {}
                if strategy_name:
                    query += "AND pp.strategy_name = %(strategy_name)s "
                    params['strategy_name'] = strategy_name
                query += "ORDER BY pp.strategy_name, pp.ticker"
                rows = db.execute_query(query, params) or []

                by_strategy: Dict[str, Dict[str, Any]] = {}
                total_mv = 0.0
                total_upnl = 0.0
                avg_upnl_pct_acc = 0.0
                total_annual_weighted = 0.0
                last_price_ts = None
                from datetime import datetime
                for r in rows:
                    sn = r.get('strategy_name')
                    by = by_strategy.setdefault(sn, {
                        'strategy_name': sn,
                        'positions_count': 0,
                        'total_market_value': 0.0,
                        'total_unrealized_pnl': 0.0,
                        'annual_weighted_sum': 0.0
                    })
                    by['positions_count'] += 1
                    mv = float(r.get('market_value') or 0)
                    upnl = float(r.get('unrealized_pnl_amount') or 0)
                    upnl_pct = float(r.get('unrealized_pnl_percent') or 0)
                    avg_upnl_pct_acc += upnl_pct
                    by['total_market_value'] += mv
                    by['total_unrealized_pnl'] += upnl
                    total_mv += mv
                    total_upnl += upnl
                    ts = r.get('price_ts')
                    if ts and (last_price_ts is None or ts > last_price_ts):
                        last_price_ts = ts
                    # Annualize simple PnL% based on holding period
                    try:
                        ct = r.get('created_at')
                        if isinstance(ts, str):
                            ts_dt = datetime.fromisoformat(ts)
                        else:
                            ts_dt = ts or datetime.now()
                        if isinstance(ct, str):
                            ct_dt = datetime.fromisoformat(ct)
                        else:
                            ct_dt = ct or ts_dt
                        days = max((ts_dt - ct_dt).total_seconds() / 86400.0, 1.0)
                    except Exception:
                        days = 365.0
                    annualized_pct_pos = upnl_pct * (365.0 / days)
                    by['annual_weighted_sum'] += annualized_pct_pos * mv
                    total_annual_weighted += annualized_pct_pos * mv
                for s in by_strategy.values():
                    mv = s['total_market_value']
                    pct = (s['total_unrealized_pnl'] / mv * 100) if mv else 0.0
                    s['net_unrealized_pnl_pct'] = pct
                    s['net_unrealized_anual_pnl_pct'] = (s['annual_weighted_sum'] / mv) if mv else 0.0

                result = {
                    'positions': rows,
                    'by_strategy': list(by_strategy.values()),
                    'totals': {
                        'total_positions': len(rows),
                        'total_market_value': total_mv,
                        'net_unrealized_pnl': total_upnl,
                        'net_unrealized_pnl_pct': (total_upnl / total_mv * 100) if total_mv else 0.0,
                        'net_unrealized_anual_pnl_pct': (total_annual_weighted / total_mv) if total_mv else 0.0,
                        'strategies_count': len(by_strategy),
                        'avg_unrealized_pnl_pct': (avg_upnl_pct_acc / len(rows)) if rows else 0.0,
                        'position_concentration_top_pct': (max([float(r.get('market_value') or 0) for r in rows]) / total_mv * 100) if rows and total_mv else 0.0,
                        'last_price_timestamp': last_price_ts
                    }
                }
                return self.serialize_result(result)
            except Exception as e:
                logger.error(f"Version {version} analytics portfolio summary error: {e}")
                return {
                    "error": f"Analytics portfolio summary not available in {version}",
                    "details": str(e),
                    "version": version
                }

        # Analytics: strategy summary (same fields, filtered by strategy)
        @app.get("/analytics/performance/strategy_summary")
        async def analytics_strategy_summary(strategy_name: str):
            try:
                db = self._get_db_manager()
                query = (
                    "SELECT pp.strategy_name, pp.ticker, pp.quantity, pp.avg_entry_price, "
                    "COALESCE(od.close, pp.avg_entry_price) AS current_price, "
                    "CASE WHEN COALESCE(od.close, pp.avg_entry_price) > 0 AND pp.avg_entry_price > 0 "
                    "THEN ROUND(((COALESCE(od.close, pp.avg_entry_price) - pp.avg_entry_price) / pp.avg_entry_price * 100)::numeric, 4) "
                    "ELSE 0 END AS unrealized_pnl_percent, "
                    "ROUND((pp.quantity * (COALESCE(od.close, pp.avg_entry_price) - pp.avg_entry_price))::numeric, 8) AS unrealized_pnl_amount, "
                    "ROUND((pp.quantity * COALESCE(od.close, pp.avg_entry_price))::numeric, 8) AS market_value, "
                    "pp.last_updated, pp.created_at, od.price_ts "
                    "FROM portfolio_positions pp "
                    "LEFT JOIN LATERAL ("
                    "    SELECT close, timestamp AS price_ts FROM ohlc_data "
                    "    WHERE ticker = pp.ticker "
                    "       OR ticker = REPLACE(pp.ticker, '/', '') "
                    "       OR REPLACE(ticker, '/', '') = pp.ticker "
                    "    ORDER BY timestamp DESC LIMIT 1"
                    ") od ON true "
                    "WHERE pp.quantity != 0 AND pp.strategy_name = %(s)s "
                    "ORDER BY pp.ticker"
                )
                rows = db.execute_query(query, {'s': strategy_name}) or []

                by_strategy: Dict[str, Dict[str, Any]] = {}
                total_mv = 0.0
                total_upnl = 0.0
                avg_upnl_pct_acc = 0.0
                total_annual_weighted = 0.0
                last_price_ts = None
                from datetime import datetime
                for r in rows:
                    sn = r.get('strategy_name')
                    by = by_strategy.setdefault(sn, {
                        'strategy_name': sn,
                        'positions_count': 0,
                        'total_market_value': 0.0,
                        'total_unrealized_pnl': 0.0,
                        'annual_weighted_sum': 0.0
                    })
                    by['positions_count'] += 1
                    mv = float(r.get('market_value') or 0)
                    upnl = float(r.get('unrealized_pnl_amount') or 0)
                    upnl_pct = float(r.get('unrealized_pnl_percent') or 0)
                    avg_upnl_pct_acc += upnl_pct
                    by['total_market_value'] += mv
                    by['total_unrealized_pnl'] += upnl
                    total_mv += mv
                    total_upnl += upnl
                    ts = r.get('price_ts')
                    if ts and (last_price_ts is None or ts > last_price_ts):
                        last_price_ts = ts
                    try:
                        ct = r.get('created_at')
                        if isinstance(ts, str):
                            ts_dt = datetime.fromisoformat(ts)
                        else:
                            ts_dt = ts or datetime.now()
                        if isinstance(ct, str):
                            ct_dt = datetime.fromisoformat(ct)
                        else:
                            ct_dt = ct or ts_dt
                        days = max((ts_dt - ct_dt).total_seconds() / 86400.0, 1.0)
                    except Exception:
                        days = 365.0
                    annualized_pct_pos = upnl_pct * (365.0 / days)
                    by['annual_weighted_sum'] += annualized_pct_pos * mv
                    total_annual_weighted += annualized_pct_pos * mv
                for s in by_strategy.values():
                    mv = s['total_market_value']
                    pct = (s['total_unrealized_pnl'] / mv * 100) if mv else 0.0
                    s['net_unrealized_pnl_pct'] = pct
                    s['net_unrealized_anual_pnl_pct'] = (s['annual_weighted_sum'] / mv) if mv else 0.0

                result = {
                    'positions': rows,
                    'by_strategy': list(by_strategy.values()),
                    'totals': {
                        'total_positions': len(rows),
                        'total_market_value': total_mv,
                        'net_unrealized_pnl': total_upnl,
                        'net_unrealized_pnl_pct': (total_upnl / total_mv * 100) if total_mv else 0.0,
                        'net_unrealized_anual_pnl_pct': (total_annual_weighted / total_mv) if total_mv else 0.0,
                        'strategies_count': len(by_strategy),
                        'avg_unrealized_pnl_pct': (avg_upnl_pct_acc / len(rows)) if rows else 0.0,
                        'position_concentration_top_pct': (max([float(r.get('market_value') or 0) for r in rows]) / total_mv * 100) if rows and total_mv else 0.0,
                        'last_price_timestamp': last_price_ts
                    }
                }
                return self.serialize_result(result)
            except Exception as e:
                logger.error(f"Version {version} analytics strategy summary error: {e}")
                return {
                    "error": f"Analytics strategy summary not available in {version}",
                    "details": str(e),
                    "version": version
                }

        # Analytics: KPIs for quick monitoring (simple approximations)
        @app.get("/analytics/performance/kpis")
        async def analytics_kpis(strategy_name: str | None = None):
            try:
                resp = await analytics_portfolio_summary(strategy_name)
                def safe(val, default=0.0):
                    try:
                        return float(val)
                    except Exception:
                        return default
                totals = resp.get('totals', {}) if isinstance(resp, dict) else {}
                mv = safe(totals.get('total_market_value'))
                net_upnl = safe(totals.get('net_unrealized_pnl'))
                net_upnl_pct = safe(totals.get('net_unrealized_pnl_pct'))
                avg_upnl_pct = safe(totals.get('avg_unrealized_pnl_pct')) if totals else 0.0
                positions = resp.get('positions', []) if isinstance(resp, dict) else []
                pnl_pcts = [safe(p.get('unrealized_pnl_percent')) for p in positions if p]
                if pnl_pcts:
                    mean = sum(pnl_pcts) / len(pnl_pcts)
                    mad = sum(abs(x - mean) for x in pnl_pcts) / len(pnl_pcts)
                else:
                    mad = 0.0
                annual_ret_pct = safe(totals.get('net_unrealized_anual_pnl_pct'))
                sharpe_proxy = (annual_ret_pct / (mad if mad > 0 else 1.0))
                result = {
                    'kpis': {
                        'portfolio_market_value': mv,
                        'net_unrealized_pnl': net_upnl,
                        'net_unrealized_pnl_pct': net_upnl_pct,
                        'annualized_unrealized_pnl_pct': annual_ret_pct,
                        'avg_position_unrealized_pnl_pct': avg_upnl_pct,
                        'sharpe_ratio_proxy': sharpe_proxy,
                    },
                    'source': 'analytics_portfolio_summary'
                }
                return self.serialize_result(result)
            except Exception as e:
                logger.error(f"Version {version} analytics KPIs error: {e}")
                return {
                    "error": f"Analytics KPIs not available in {version}",
                    "details": str(e),
                    "version": version
                }

        # Analytics: Top movers by absolute PnL%
        @app.get("/analytics/performance/top_movers")
        async def analytics_top_movers(limit: int = 5, strategy_name: str | None = None):
            try:
                summary = await analytics_portfolio_summary(strategy_name)
                positions = summary.get('positions', []) if isinstance(summary, dict) else []
                positions.sort(key=lambda p: abs(float(p.get('unrealized_pnl_percent', 0) or 0)), reverse=True)
                return self.serialize_result({
                    'top_movers': positions[:max(0, min(limit, 100))]
                })
            except Exception as e:
                logger.error(f"Version {version} analytics top movers error: {e}")
                return {
                    "error": f"Analytics top movers not available in {version}",
                    "details": str(e),
                    "version": version
                }
        
        
        return app
        
    def serialize_result(self, result: Any) -> Any:
        """Serialize result for JSON response."""
        from decimal import Decimal
        from datetime import datetime
        import json
        
        def json_serializer(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif hasattr(obj, '__dict__'):
                return obj.__dict__
            else:
                return str(obj)
                
        # Convert to JSON-safe format
        try:
            json_str = json.dumps(result, default=json_serializer)
            return json.loads(json_str)
        except Exception:
            return {"result": str(result)}
            
    def get_loaded_versions(self) -> list:
        """Get list of currently loaded versions."""
        return list(self.loaded_apps.keys())
        
    def unload_version(self, version: str) -> None:
        """Unload a specific version."""
        if version in self.loaded_apps:
            del self.loaded_apps[version]
            logger.info(f"Unloaded version: {version}")
            
    def reload_version(self, version: str) -> FastAPI:
        """Reload a specific version."""
        self.unload_version(version)
        return self.create_version_app(version)
