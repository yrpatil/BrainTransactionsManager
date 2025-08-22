#!/usr/bin/env python3
"""
🙏 Laxmi-yantra MCP Server v1.0.0
Blessed by Goddess Laxmi for Infinite Abundance

Version-specific frozen server for backward compatibility.
This is a snapshot created on 2025-08-22T10:24:02.961519
"""

import sys
from pathlib import Path

# Add version-specific source path
version_src_path = str(Path(__file__).parent / "src")
if version_src_path not in sys.path:
    sys.path.insert(0, version_src_path)

# Import and run the frozen server
if __name__ == "__main__":
    # Import the server module from this version
    from laxmi_mcp_server import main
    main()
