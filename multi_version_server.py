#!/usr/bin/env python3
"""
🙏 Laxmi-yantra Multi-Version Trading Server
Blessed by Goddess Laxmi for Infinite Abundance

Main server entry point that orchestrates multiple API versions on a single port.
Provides backward compatibility, development mode, and comprehensive version management.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from server_manager.multi_version_server import MultiVersionServer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main server entry point."""
    logger.info("🙏 Starting Laxmi-yantra Multi-Version Trading Server")
    logger.info("May Goddess Laxmi bless this session with infinite abundance and prosperity!")
    
    # Get configuration from environment
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', '8000'))
    workers = int(os.getenv('WORKERS', '1'))
    reload = os.getenv('RELOAD', 'false').lower() == 'true'
    
    # Initialize multi-version server
    try:
        multi_server = MultiVersionServer()
        app = multi_server.get_app()
        
        logger.info(f"Server configuration:")
        logger.info(f"  Host: {host}")
        logger.info(f"  Port: {port}")
        logger.info(f"  Workers: {workers}")
        logger.info(f"  Reload: {reload}")
        
        # Start server
        uvicorn.run(
            app,
            host=host,
            port=port,
            workers=workers if not reload else 1,  # Single worker for reload mode
            reload=reload,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
