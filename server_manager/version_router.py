#!/usr/bin/env python3
"""
🙏 Version Router
Blessed by Goddess Laxmi for Infinite Abundance

Single-port version routing for API backward compatibility.
Routes requests to appropriate version handlers based on URL path.
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse

logger = logging.getLogger(__name__)

class VersionRouter:
    """Routes requests to appropriate API version handlers."""
    
    def __init__(self, config_path: str = "config/api_versions.json"):
        """Initialize version router with configuration."""
        self.config_path = Path(config_path)
        self.config: Dict = {}
        self.version_pattern = re.compile(r'^/v(\d+)\.(\d+)\.(\d+)(/.*)?$')
        self.load_config()
        
    def load_config(self) -> None:
        """Load API versions configuration."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            logger.info(f"Loaded API versions config: {list(self.config.get('active_versions', []))}")
        except FileNotFoundError:
            logger.error(f"Config file not found: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise
            
    def reload_config(self) -> None:
        """Reload configuration from file."""
        self.load_config()
        
    def parse_version_from_path(self, path: str) -> Tuple[Optional[str], str]:
        """
        Extract version and remaining path from request path.
        
        Args:
            path: Request path (e.g., '/v1.0.0/tools/buy_stock')
            
        Returns:
            Tuple of (version, remaining_path)
        """
        # Handle development mode
        if path.startswith('/development'):
            remaining_path = path[len('/development'):] or '/'
            return 'development', remaining_path
            
        # Handle versioned paths
        match = self.version_pattern.match(path)
        if match:
            major, minor, patch = match.groups()[:3]
            version = f"v{major}.{minor}.{patch}"
            remaining_path = match.group(4) or '/'
            return version, remaining_path
            
        # Handle health check at root
        if path in ['/health', '/']:
            return None, path
            
        # Unversioned path - needs redirect if configured
        return None, path
        
    def validate_version(self, version: str) -> bool:
        """Check if version is active and supported."""
        if version == 'development':
            return self.config.get('development_mode', False)
            
        active_versions = self.config.get('active_versions', [])
        return version in active_versions
        
    def get_version_handler_path(self, version: str) -> Optional[str]:
        """Get handler path for specific version."""
        handlers = self.config.get('version_handlers', {})
        return handlers.get(version)
        
    def should_redirect_unversioned(self) -> bool:
        """Check if unversioned requests should be redirected."""
        routing_config = self.config.get('routing', {})
        return routing_config.get('redirect_unversioned', True)
        
    def get_default_version(self) -> str:
        """Get default version for redirects."""
        routing_config = self.config.get('routing', {})
        default = routing_config.get('default_version')
        if not default:
            default = self.config.get('current_version', 'v1.0.0')
        return default
        
    def route_request(self, request: Request) -> Tuple[Optional[str], str, bool]:
        """
        Route incoming request to appropriate version.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Tuple of (version, path, needs_redirect)
        """
        path = request.url.path
        version, remaining_path = self.parse_version_from_path(path)
        
        # Handle health check
        if path == '/health':
            return None, '/health', False
            
        # Handle versioned requests
        if version:
            if not self.validate_version(version):
                logger.warning(f"Invalid version requested: {version}")
                raise HTTPException(
                    status_code=404, 
                    detail=f"API version '{version}' is not supported. "
                           f"Available versions: {self.config.get('active_versions', [])}"
                )
            return version, remaining_path, False
            
        # Handle unversioned requests
        if self.should_redirect_unversioned():
            default_version = self.get_default_version()
            redirect_path = f"/{default_version}{path}" if path != '/' else f"/{default_version}/"
            return default_version, redirect_path, True
            
        # Allow unversioned for specific paths
        return None, path, False
        
    def get_active_versions(self) -> List[str]:
        """Get list of currently active versions."""
        return self.config.get('active_versions', [])
        
    def get_deprecated_versions(self) -> List[str]:
        """Get list of deprecated versions."""
        return self.config.get('deprecated_versions', [])
        
    def get_version_metadata(self, version: str) -> Dict:
        """Get metadata for specific version."""
        metadata = self.config.get('version_metadata', {})
        return metadata.get(version, {})
        
    def is_version_deprecated(self, version: str) -> bool:
        """Check if version is deprecated."""
        return version in self.get_deprecated_versions()
        
    def get_port(self) -> int:
        """Get configured server port."""
        return self.config.get('port', 8000)
        
    def get_host(self) -> str:
        """Get configured server host."""
        server_config = self.config.get('server_config', {})
        return server_config.get('host', '127.0.0.1')
