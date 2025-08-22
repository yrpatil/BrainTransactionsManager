#!/usr/bin/env python3
"""
🙏 Multi-Version Server
Blessed by Goddess Laxmi for Infinite Abundance

Main server that orchestrates multiple API versions on a single port.
Provides backward compatibility and development mode support.
"""

import logging
import asyncio
from typing import Dict, List, Optional
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from .version_router import VersionRouter
from .version_loader import VersionLoader

logger = logging.getLogger(__name__)

class MultiVersionServer:
    """Multi-version API server with single-port routing."""
    
    def __init__(self, config_path: str = "config/api_versions.json"):
        """Initialize multi-version server."""
        self.config_path = config_path
        self.router = VersionRouter(config_path)
        self.loader = VersionLoader(config_path)
        self.app = FastAPI(
            title="Laxmi-yantra Trading API",
            description="Multi-version trading API with backward compatibility - Blessed by Goddess Laxmi 🙏",
            version="Multi-Version"
        )
        self.version_apps: Dict[str, FastAPI] = {}
        self.setup_middleware()
        self.setup_main_routes()
        
    def setup_middleware(self) -> None:
        """Setup FastAPI middleware."""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
    def setup_main_routes(self) -> None:
        """Setup main server routes."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint with API information."""
            return {
                "message": "🙏 Welcome to Laxmi-yantra Trading API - Blessed by Goddess Laxmi for Infinite Abundance",
                "active_versions": self.router.get_active_versions(),
                "current_version": self.router.get_default_version(),
                "deprecated_versions": self.router.get_deprecated_versions(),
                "endpoints": {
                    "health": "/health",
                    "versions": "/versions",
                    "version_health": "/{version}/health",
                    "tools": "/{version}/tools/{tool_name}",
                    "resources": "/{version}/resources/{resource_name}"
                }
            }
            
        @self.app.get("/health")
        async def global_health():
            """Global health check for all versions."""
            health_status = {
                "status": "healthy",
                "timestamp": asyncio.get_event_loop().time(),
                "versions": {}
            }
            
            for version in self.router.get_active_versions():
                try:
                    if version in self.version_apps:
                        health_status["versions"][version] = {
                            "status": "healthy",
                            "loaded": True
                        }
                    else:
                        health_status["versions"][version] = {
                            "status": "not_loaded",
                            "loaded": False
                        }
                except Exception as e:
                    health_status["versions"][version] = {
                        "status": "error",
                        "error": str(e),
                        "loaded": False
                    }
                    
            # Check if development mode is active
            if self.router.config.get('development_mode', False):
                health_status["versions"]["development"] = {
                    "status": "healthy" if "development" in self.version_apps else "not_loaded",
                    "loaded": "development" in self.version_apps
                }
                
            return health_status
            
        @self.app.get("/versions")
        async def list_versions():
            """List all available API versions."""
            return {
                "active_versions": self.router.get_active_versions(),
                "deprecated_versions": self.router.get_deprecated_versions(),
                "current_version": self.router.get_default_version(),
                "development_mode": self.router.config.get('development_mode', False),
                "deprecation_policy": self.router.config.get('deprecation_policy', 'N-4'),
                "version_metadata": self.router.config.get('version_metadata', {})
            }
            
    async def load_version_apps(self) -> None:
        """Load all configured version applications."""
        active_versions = self.router.get_active_versions()
        
        # Load active versions
        for version in active_versions:
            try:
                await self.load_version_app(version)
            except Exception as e:
                logger.error(f"Failed to load version {version}: {e}")
                
        # Load development mode if enabled
        if self.router.config.get('development_mode', False):
            try:
                await self.load_version_app('development')
            except Exception as e:
                logger.error(f"Failed to load development version: {e}")
                
    async def load_version_app(self, version: str) -> None:
        """Load a specific version application."""
        if version in self.version_apps:
            logger.info(f"Version {version} already loaded")
            return
            
        try:
            # Create version app
            version_app = self.loader.create_version_app(version)
            
            # Mount the version app
            self.app.mount(f"/{version}", version_app)
            self.version_apps[version] = version_app
            
            logger.info(f"Successfully loaded and mounted version: {version}")
            
        except Exception as e:
            logger.error(f"Failed to load version {version}: {e}")
            raise
            
    async def unload_version_app(self, version: str) -> None:
        """Unload a specific version application."""
        if version not in self.version_apps:
            logger.warning(f"Version {version} not loaded")
            return
            
        try:
            # Remove from mounted apps
            del self.version_apps[version]
            self.loader.unload_version(version)
            
            logger.info(f"Successfully unloaded version: {version}")
            
        except Exception as e:
            logger.error(f"Failed to unload version {version}: {e}")
            raise
            
    async def reload_version_app(self, version: str) -> None:
        """Reload a specific version application."""
        logger.info(f"Reloading version: {version}")
        await self.unload_version_app(version)
        await self.load_version_app(version)
        
    def get_loaded_versions(self) -> List[str]:
        """Get list of currently loaded versions."""
        return list(self.version_apps.keys())
        
    async def startup(self) -> None:
        """Server startup tasks."""
        logger.info("🙏 Starting Laxmi-yantra Multi-Version Trading Server")
        logger.info("May Goddess Laxmi bless this session with infinite abundance and prosperity!")
        
        # Load all version applications
        await self.load_version_apps()
        
        # Log loaded versions
        loaded_versions = self.get_loaded_versions()
        logger.info(f"Loaded API versions: {loaded_versions}")
        
        if 'development' in loaded_versions:
            logger.info("🔧 Development mode is active")
        
        # Start lightweight background price poller for analytics current_price (optional)
        try:
            import asyncio
            import os
            interval_s = float(os.getenv('PRICE_POLL_INTERVAL_SECONDS', '60'))
            logger.info(f"Starting price poller (interval={interval_s}s)")
            # Do an immediate poll once at startup so analytics has fresh data
            try:
                await self._poll_and_update_latest_prices()
                logger.info("Initial price poll complete")
            except Exception as ie:
                logger.warning(f"Initial price poll failed: {ie}")
            
            async def price_poller():
                while True:
                    try:
                        await self._poll_and_update_latest_prices()
                    except Exception as e:
                        logger.warning(f"Price poller error: {e}")
                    await asyncio.sleep(interval_s)
            
            asyncio.create_task(price_poller())
        except Exception as e:
            logger.warning(f"Failed to start price poller: {e}")
            
    async def shutdown(self) -> None:
        """Server shutdown tasks."""
        logger.info("Shutting down Laxmi-yantra Multi-Version Trading Server")
        
        # Cleanup loaded versions
        for version in list(self.version_apps.keys()):
            await self.unload_version_app(version)
            
        logger.info("🙏 Server shutdown complete. May prosperity continue to flow!")
        
    def get_app(self) -> FastAPI:
        """Get the main FastAPI application."""
        # Setup startup and shutdown events
        @self.app.on_event("startup")
        async def startup_event():
            await self.startup()
            
        @self.app.on_event("shutdown") 
        async def shutdown_event():
            await self.shutdown()
            
        return self.app

    async def _poll_and_update_latest_prices(self) -> None:
        """Fetch latest prices for tickers in portfolio_positions and upsert into ohlc_data."""
        try:
            # Lazy imports to avoid heavy deps if unused
            import sys
            from pathlib import Path
            src_path = str(Path.cwd() / "src")
            if src_path not in sys.path:
                sys.path.insert(0, src_path)
            from braintransactions.core.config import BrainConfig
            from braintransactions.database.connection import DatabaseManager
            config = BrainConfig()
            db = DatabaseManager(config)
            # Ensure core tables (including ohlc_data) exist before polling
            try:
                db.create_tables()
            except Exception as e:
                logger.warning(f"Create tables failed (will continue): {e}")
            
            # Get unique tickers from positions
            rows = db.execute_query(
                f"SELECT DISTINCT ticker FROM {config.db_schema}.portfolio_positions WHERE quantity != 0"
            )
            tickers = [r['ticker'] for r in rows] if rows else []
            if not tickers:
                return
            logger.debug(f"Price poller: found {len(tickers)} tickers: {tickers}")
            
            # Basic price source using Alpaca if available
            latest_prices = {}
            try:
                import alpaca_trade_api as tradeapi
                api = tradeapi.REST(config.alpaca_api_key, config.alpaca_secret_key, config.alpaca_base_url, api_version='v2')
                for t in tickers:
                    price = 0.0
                    try:
                        # Build symbol candidates to handle crypto/equity notation
                        candidates = [t]
                        if '/' in t:
                            candidates.append(t.replace('/', ''))  # BTC/USD -> BTCUSD
                        elif t.endswith('USD'):
                            candidates.append(f"{t[:-3]}/USD")   # BTCUSD -> BTC/USD
                        logger.debug(f"Polling prices for {t} candidates={candidates}")

                        # Try minute bars first (equities)
                        for sym in candidates:
                            try:
                                barset = api.get_bars(sym, tradeapi.rest.TimeFrame.Minute, limit=1)
                                if hasattr(barset, 'df') and not barset.df.empty:
                                    price = float(barset.df.iloc[-1]['close'])
                                    logger.debug(f"Bars hit for {sym}: close={price}")
                                    if price > 0:
                                        break
                            except Exception:
                                logger.debug(f"Bars fetch failed for {sym}")
                                continue
                        # If still no price and looks like crypto, try crypto-specific endpoints
                        if price <= 0 and ("/" in t or t.endswith('USD')):
                            for sym in candidates:
                                # Try crypto bars (API supports get_crypto_bars in some versions)
                                try:
                                    crypto_bars = None
                                    try:
                                        crypto_bars = api.get_crypto_bars(sym, tradeapi.rest.TimeFrame.Minute, limit=1)
                                    except Exception:
                                        # Some versions use string timeframe
                                        crypto_bars = api.get_crypto_bars(sym, '1Min', limit=1)
                                    if crypto_bars is not None:
                                        df = getattr(crypto_bars, 'df', None)
                                        if df is not None and not df.empty:
                                            price = float(df.iloc[-1]['close'])
                                            logger.debug(f"Crypto bars hit for {sym}: close={price}")
                                            if price > 0:
                                                break
                                except Exception:
                                    logger.debug(f"Crypto bars fetch failed for {sym}")
                                    continue
                        # Fallback: last trade
                        if price <= 0:
                            for sym in candidates:
                                try:
                                    last_trade = api.get_last_trade(sym)
                                    price = float(getattr(last_trade, 'price', None) or 0)
                                    logger.debug(f"Last trade for {sym}: price={price}")
                                    if price > 0:
                                        break
                                except Exception:
                                    logger.debug(f"Last trade fetch failed for {sym}")
                                    continue
                        # Crypto last trade fallback (if available)
                        if price <= 0 and ("/" in t or t.endswith('USD')):
                            for sym in candidates:
                                try:
                                    crypto_last = None
                                    try:
                                        crypto_last = api.get_crypto_last_trade(sym)
                                    except Exception:
                                        pass
                                    if crypto_last is not None:
                                        price = float(getattr(crypto_last, 'price', None) or 0)
                                        logger.debug(f"Crypto last trade for {sym}: price={price}")
                                        if price > 0:
                                            break
                                except Exception:
                                    logger.debug(f"Crypto last trade fetch failed for {sym}")
                                    continue
                    except Exception:
                        price = 0.0
                        logger.debug(f"General error while fetching price for {t}")
                    logger.debug(f"Chosen price for {t}: {price}")
                    latest_prices[t] = price
            except Exception:
                # If Alpaca unavailable, skip silently
                logger.warning("Alpaca client not available; skipping price poll")
                return
            
            # Insert into ohlc_data with explicit timeframe and OHLC (Timescale hypertable compatibility)
            for t, p in latest_prices.items():
                if p is None or p <= 0:
                    logger.debug(f"Skipping insert for {t}: invalid price {p}")
                    continue
                try:
                    # Try to get full OHLCV for 1m bar
                    o = h = l = v = None
                    try:
                        import alpaca_trade_api as tradeapi
                        barset = api.get_bars(t, tradeapi.rest.TimeFrame.Minute, limit=1)
                        if hasattr(barset, 'df') and not barset.df.empty:
                            last = barset.df.iloc[-1]
                            o = float(last.get('open', p)) if last.get('open', None) is not None else p
                            h = float(last.get('high', p)) if last.get('high', None) is not None else p
                            l = float(last.get('low', p)) if last.get('low', None) is not None else p
                            v = float(last.get('volume', 0) or 0)
                    except Exception:
                        pass
                    params = {
                        't': t,
                        'tf': '1m',
                        'o': o if o is not None else p,
                        'h': h if h is not None else p,
                        'l': l if l is not None else p,
                        'c': p,
                        'v': v if v is not None else 0
                    }
                    # Insert for ticker variants to improve join hits
                    variants = {t}
                    if '/' in t:
                        variants.add(t.replace('/', ''))
                    elif t.endswith('USD'):
                        variants.add(f"{t[:-3]}/USD")
                    for tv in variants:
                        v_params = dict(params)
                        v_params['t'] = tv
                        logger.debug(f"Inserting OHLC for {tv}: {v_params}")
                        db.execute_action(
                            f"INSERT INTO {config.db_schema}.ohlc_data (timestamp, ticker, timeframe, open, high, low, close, volume) "
                            f"VALUES (NOW(), %(t)s, %(tf)s, %(o)s, %(h)s, %(l)s, %(c)s, %(v)s)",
                            v_params
                        )
                except Exception as ie:
                    logger.debug(f"Insert failed for {t}: {ie}")
                    continue
        except Exception as e:
            logger.warning(f"Price poller outer error: {e}")
