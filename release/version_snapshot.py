#!/usr/bin/env python3
"""
🙏 Version Snapshot Manager
Blessed by Goddess Laxmi for Infinite Abundance

Creates and manages version snapshots for API backward compatibility.
Preserves code, dependencies, and configuration for each release.
"""

import os
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class VersionSnapshot:
    """Manages version snapshots for API backward compatibility."""
    
    def __init__(self, base_path: str = "."):
        """Initialize version snapshot manager."""
        self.base_path = Path(base_path)
        self.api_versions_dir = self.base_path / "api_versions"
        self.config_path = self.base_path / "config" / "api_versions.json"
        
        # Ensure directories exist
        self.api_versions_dir.mkdir(exist_ok=True)
        
    def create_snapshot(self, version: str, source_files: Optional[List[str]] = None) -> None:
        """
        Create a snapshot of the current codebase for the given version.
        
        Args:
            version: Version string (e.g., 'v1.0.0')
            source_files: List of files to include (if None, uses defaults)
        """
        if not version.startswith('v'):
            version = f"v{version}"
            
        version_dir = self.api_versions_dir / version
        
        if version_dir.exists():
            logger.warning(f"Version {version} already exists. Overwriting...")
            shutil.rmtree(version_dir)
            
        version_dir.mkdir(parents=True, exist_ok=True)
        
        # Default files to snapshot
        if source_files is None:
            source_files = [
                "mcp-server/laxmi_mcp_server.py",
                "mcp-server/requirements.txt",
                "src/braintransactions/",
                "setup.py",
                "VERSION",
                ".env.example"
            ]
            
        # Copy source files
        for source_file in source_files:
            source_path = self.base_path / source_file
            
            if not source_path.exists():
                logger.warning(f"Source file not found: {source_path}")
                continue
                
            dest_path = version_dir / source_file
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if source_path.is_file():
                shutil.copy2(source_path, dest_path)
            elif source_path.is_dir():
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                shutil.copytree(source_path, dest_path)
                
        # Create version-specific server entry point
        self.create_version_server(version)
        
        # Create version metadata
        self.create_version_metadata(version)
        
        logger.info(f"Created version snapshot: {version}")
        
    def create_version_server(self, version: str) -> None:
        """Create a version-specific server entry point."""
        version_dir = self.api_versions_dir / version
        server_path = version_dir / "server.py"
        
        # Read the original server file
        original_server = self.base_path / "mcp-server" / "laxmi_mcp_server.py"
        
        if not original_server.exists():
            logger.error(f"Original server file not found: {original_server}")
            return
            
        # Create version-specific server
        server_content = f'''#!/usr/bin/env python3
"""
🙏 Laxmi-yantra MCP Server {version}
Blessed by Goddess Laxmi for Infinite Abundance

Version-specific frozen server for backward compatibility.
This is a snapshot created on {datetime.now().isoformat()}
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
'''
        
        with open(server_path, 'w') as f:
            f.write(server_content)
            
        # Copy the actual server code as a module
        server_module_path = version_dir / "laxmi_mcp_server.py"
        shutil.copy2(original_server, server_module_path)
        
        # Make server executable
        server_path.chmod(0o755)
        
    def create_version_metadata(self, version: str) -> None:
        """Create metadata file for the version."""
        version_dir = self.api_versions_dir / version
        metadata_path = version_dir / "metadata.json"
        
        metadata = {
            "version": version,
            "created_date": datetime.now().isoformat(),
            "status": "stable",
            "breaking_changes": self.has_breaking_changes(version),
            "dependencies": self.get_dependencies(version),
            "api_endpoints": self.get_api_endpoints(version),
            "compatibility": {
                "python_version": ">=3.8",
                "api_compatibility": self.get_api_compatibility(version)
            }
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
            
    def has_breaking_changes(self, version: str) -> bool:
        """Determine if version has breaking changes."""
        # Parse version to check for major version change
        try:
            parts = version.lstrip('v').split('.')
            major = int(parts[0])
            
            # Check previous version
            config = self.load_config()
            active_versions = config.get('active_versions', [])
            
            for active_version in active_versions:
                active_parts = active_version.lstrip('v').split('.')
                active_major = int(active_parts[0])
                
                if major > active_major:
                    return True
                    
            return False
            
        except (ValueError, IndexError):
            return False
            
    def get_dependencies(self, version: str) -> Dict:
        """Get dependency information for the version."""
        version_dir = self.api_versions_dir / version
        requirements_path = version_dir / "mcp-server" / "requirements.txt"
        
        dependencies = {}
        
        if requirements_path.exists():
            with open(requirements_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '==' in line:
                            pkg, ver = line.split('==', 1)
                            dependencies[pkg] = ver
                        else:
                            dependencies[line] = "latest"
                            
        return dependencies
        
    def get_api_endpoints(self, version: str) -> List[str]:
        """Get list of API endpoints for the version."""
        # This could be enhanced to parse the server file and extract endpoints
        return [
            "/health",
            "/tools/buy_stock",
            "/tools/sell_stock", 
            "/tools/get_account_status",
            "/tools/get_portfolio_summary",
            "/resources/system_health",
            "/resources/current_positions"
        ]
        
    def get_api_compatibility(self, version: str) -> str:
        """Get API compatibility level."""
        try:
            parts = version.lstrip('v').split('.')
            major = int(parts[0])
            minor = int(parts[1])
            
            return f"v{major}.{minor}.x"
            
        except (ValueError, IndexError):
            return "unknown"
            
    def load_config(self) -> Dict:
        """Load API versions configuration."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}
            
    def update_config(self, version: str) -> None:
        """Update API versions configuration with new version."""
        config = self.load_config()
        
        # Add to active versions if not present
        active_versions = config.get('active_versions', [])
        if version not in active_versions:
            active_versions.append(version)
            
        # Sort versions
        active_versions.sort(key=lambda v: [int(x) for x in v.lstrip('v').split('.')])
        
        # Update current version
        config['current_version'] = version
        config['active_versions'] = active_versions
        
        # Add version metadata
        version_metadata = config.get('version_metadata', {})
        version_metadata[version] = {
            "release_date": datetime.now().strftime("%Y-%m-%d"),
            "status": "stable",
            "breaking_changes": self.has_breaking_changes(version),
            "deprecation_date": None,
            "end_of_life_date": None
        }
        config['version_metadata'] = version_metadata
        
        # Update version handlers
        version_handlers = config.get('version_handlers', {})
        version_handlers[version] = f"api_versions/{version}/server.py"
        config['version_handlers'] = version_handlers
        
        # Apply deprecation policy (N-4)
        if len(active_versions) > 5:  # Keep current + 4 previous
            deprecated_version = active_versions[0]
            active_versions.remove(deprecated_version)
            
            deprecated_versions = config.get('deprecated_versions', [])
            if deprecated_version not in deprecated_versions:
                deprecated_versions.append(deprecated_version)
                
            config['deprecated_versions'] = deprecated_versions
            config['active_versions'] = active_versions
            
        # Save updated config
        self.config_path.parent.mkdir(exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        logger.info(f"Updated API versions config with {version}")
        
    def get_version_list(self) -> List[str]:
        """Get list of available version snapshots."""
        if not self.api_versions_dir.exists():
            return []
            
        versions = []
        for item in self.api_versions_dir.iterdir():
            if item.is_dir() and item.name.startswith('v'):
                versions.append(item.name)
                
        return sorted(versions, key=lambda v: [int(x) for x in v.lstrip('v').split('.')])
        
    def delete_version(self, version: str) -> None:
        """Delete a version snapshot."""
        if not version.startswith('v'):
            version = f"v{version}"
            
        version_dir = self.api_versions_dir / version
        
        if not version_dir.exists():
            logger.warning(f"Version {version} not found")
            return
            
        shutil.rmtree(version_dir)
        logger.info(f"Deleted version snapshot: {version}")
        
        # Update config to remove version
        config = self.load_config()
        active_versions = config.get('active_versions', [])
        if version in active_versions:
            active_versions.remove(version)
            config['active_versions'] = active_versions
            
        version_handlers = config.get('version_handlers', {})
        if version in version_handlers:
            del version_handlers[version]
            
        version_metadata = config.get('version_metadata', {})
        if version in version_metadata:
            del version_metadata[version]
            
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
    def validate_snapshot(self, version: str) -> bool:
        """Validate that a version snapshot is complete and valid."""
        if not version.startswith('v'):
            version = f"v{version}"
            
        version_dir = self.api_versions_dir / version
        
        if not version_dir.exists():
            return False
            
        required_files = [
            "server.py",
            "laxmi_mcp_server.py",
            "metadata.json"
        ]
        
        for required_file in required_files:
            if not (version_dir / required_file).exists():
                logger.error(f"Missing required file in {version}: {required_file}")
                return False
                
        return True
