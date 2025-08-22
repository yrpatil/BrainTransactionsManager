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
