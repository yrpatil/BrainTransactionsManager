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
                    sys.path.insert(0, str(Path.cwd() / "mcp-server"))
                    import laxmi_mcp_server
                    
                    trading_manager = await laxmi_mcp_server.get_trading_manager()
                    result = await self.get_account_data(trading_manager)
                    return self.serialize_result(result)
                except Exception as e:
                    logger.error(f"Development account status error: {e}")
                    return {"error": str(e), "version": "development"}
                    
            @app.get("/resources/account_info")
            async def account_info():
                try:
                    sys.path.insert(0, str(Path.cwd() / "mcp-server"))
                    import laxmi_mcp_server
                    
                    trading_manager = await laxmi_mcp_server.get_trading_manager()
                    result = await self.get_account_data(trading_manager)
                    return self.serialize_result(result)
                except Exception as e:
                    logger.error(f"Development account info error: {e}")
                    return {"error": str(e), "version": "development"}
                    
            # Add portfolio summary endpoint
            @app.get("/resources/portfolio_summary")
            async def portfolio_summary():
                try:
                    sys.path.insert(0, str(Path.cwd() / "mcp-server"))
                    import laxmi_mcp_server
                    
                    trading_manager = await laxmi_mcp_server.get_trading_manager()
                    
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
                sys.path.insert(0, str(Path.cwd() / "mcp-server"))
                import laxmi_mcp_server
                
                trading_manager = await laxmi_mcp_server.get_trading_manager()
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
                sys.path.insert(0, str(Path.cwd() / "mcp-server"))
                import laxmi_mcp_server
                
                trading_manager = await laxmi_mcp_server.get_trading_manager()
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
                sys.path.insert(0, str(Path.cwd() / "mcp-server"))
                import laxmi_mcp_server
                
                trading_manager = await laxmi_mcp_server.get_trading_manager()
                
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
