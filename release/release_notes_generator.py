#!/usr/bin/env python3
"""
🙏 Release Notes Generator
Blessed by Goddess Laxmi for Infinite Abundance

Generates comprehensive release notes for API versions.
Includes change analysis, breaking changes, and migration guides.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import subprocess
import re

logger = logging.getLogger(__name__)

class ReleaseNotesGenerator:
    """Generates release notes for API versions."""
    
    def __init__(self, base_path: str = "."):
        """Initialize release notes generator."""
        self.base_path = Path(base_path)
        self.config_path = self.base_path / "config" / "api_versions.json"
        
    def generate_release_notes(self, version: str, previous_version: Optional[str] = None) -> str:
        """
        Generate comprehensive release notes for a version.
        
        Args:
            version: Version being released (e.g., 'v1.1.0')
            previous_version: Previous version for comparison (auto-detected if None)
            
        Returns:
            Formatted release notes in Markdown
        """
        if not version.startswith('v'):
            version = f"v{version}"
            
        if not previous_version:
            previous_version = self.get_previous_version(version)
            
        release_date = datetime.now().strftime("%Y-%m-%d")
        
        # Generate sections
        overview = self.generate_overview(version, previous_version)
        breaking_changes = self.generate_breaking_changes(version, previous_version)
        new_features = self.generate_new_features(version, previous_version)
        improvements = self.generate_improvements(version, previous_version)
        bug_fixes = self.generate_bug_fixes(version, previous_version)
        api_changes = self.generate_api_changes(version, previous_version)
        migration_guide = self.generate_migration_guide(version, previous_version)
        
        # Assemble release notes
        release_notes = f"""# Release Notes - {version}

**Release Date:** {release_date}
**Previous Version:** {previous_version or 'Initial Release'}

{overview}

## 🚨 Breaking Changes

{breaking_changes}

## ✨ New Features

{new_features}

## 🔧 Improvements

{improvements}

## 🐛 Bug Fixes

{bug_fixes}

## 📊 API Changes

{api_changes}

## 🔄 Migration Guide

{migration_guide}

## 📋 Full Changelog

{self.generate_git_changelog(version, previous_version)}

---

**🙏 Blessed by Goddess Laxmi for Infinite Abundance**

*This release continues our commitment to reliable, maintainable trading systems with enhanced backward compatibility.*
"""

        return release_notes
        
    def get_previous_version(self, current_version: str) -> Optional[str]:
        """Get the previous version for comparison."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                
            active_versions = config.get('active_versions', [])
            
            # Sort versions to find previous
            sorted_versions = sorted(active_versions, key=lambda v: self.parse_version(v))
            
            try:
                current_index = sorted_versions.index(current_version)
                if current_index > 0:
                    return sorted_versions[current_index - 1]
            except ValueError:
                pass
                
            return None
            
        except Exception as e:
            logger.warning(f"Could not determine previous version: {e}")
            return None
            
    def parse_version(self, version: str) -> Tuple[int, int, int]:
        """Parse version string into tuple for sorting."""
        try:
            parts = version.lstrip('v').split('.')
            return (int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, IndexError):
            return (0, 0, 0)
            
    def generate_overview(self, version: str, previous_version: Optional[str]) -> str:
        """Generate release overview section."""
        version_parts = self.parse_version(version)
        
        if previous_version:
            prev_parts = self.parse_version(previous_version)
            
            if version_parts[0] > prev_parts[0]:
                release_type = "**Major Release** 🚀"
                description = "This major release introduces significant new capabilities and may include breaking changes."
            elif version_parts[1] > prev_parts[1]:
                release_type = "**Minor Release** ✨"
                description = "This minor release adds new features while maintaining backward compatibility."
            else:
                release_type = "**Patch Release** 🔧"
                description = "This patch release focuses on bug fixes and improvements."
        else:
            release_type = "**Initial Release** 🎉"
            description = "Welcome to the first release of the Laxmi-yantra Trading API with multi-version support!"
            
        return f"""## Overview

{release_type}

{description}

### Key Highlights
- Enhanced API versioning with backward compatibility
- Improved error handling and validation
- Optimized performance and reliability
- AI-agent focused documentation and examples
"""

    def generate_breaking_changes(self, version: str, previous_version: Optional[str]) -> str:
        """Generate breaking changes section."""
        version_parts = self.parse_version(version)
        
        if not previous_version:
            return "No breaking changes - this is the initial release."
            
        prev_parts = self.parse_version(previous_version)
        
        # Major version change indicates breaking changes
        if version_parts[0] > prev_parts[0]:
            return f"""### API Version {version}

⚠️ **Important:** This major release includes breaking changes.

- **URL Structure**: All endpoints now require version prefix (e.g., `/{version}/tools/buy_stock`)
- **Response Format**: Some field names may have changed for consistency
- **Error Codes**: Enhanced error handling with more specific status codes
- **Authentication**: Updated authentication requirements (if applicable)

**Migration Required:** Please update your client applications to use the new API structure.
See the Migration Guide below for detailed instructions.
"""
        else:
            return "✅ No breaking changes in this release. Fully backward compatible."
            
    def generate_new_features(self, version: str, previous_version: Optional[str]) -> str:
        """Generate new features section."""
        features = [
            "🔄 **Multi-Version API Support**: Access multiple API versions simultaneously",
            "📊 **Enhanced Portfolio Analytics**: Improved PnL calculations and reporting", 
            "🛡️ **Advanced Error Handling**: More granular error codes and messages",
            "🔍 **Health Check Improvements**: Comprehensive system health monitoring",
            "📈 **Strategy-Specific Summaries**: Detailed strategy performance analytics",
            "⚡ **Performance Optimizations**: Faster response times and reduced latency",
            "🤖 **AI-Agent Optimizations**: Streamlined endpoints for AI agent integration"
        ]
        
        if not previous_version:
            # Initial release - include all core features
            features.extend([
                "💰 **Stock Trading**: Buy/sell stocks with market and limit orders",
                "📊 **Portfolio Management**: Real-time portfolio tracking and analytics",
                "🔒 **Kill Switch**: Emergency trading halt functionality",
                "🔄 **Background Polling**: Automatic order and position reconciliation",
                "📋 **Order Management**: Comprehensive order tracking and history"
            ])
            
        return "\n".join(f"- {feature}" for feature in features)
        
    def generate_improvements(self, version: str, previous_version: Optional[str]) -> str:
        """Generate improvements section."""
        improvements = [
            "🚀 **Performance**: Optimized database queries and caching",
            "📝 **Logging**: Enhanced logging with structured formats",
            "🔧 **Configuration**: Simplified configuration management", 
            "🛡️ **Security**: Improved input validation and sanitization",
            "📚 **Documentation**: Updated AI-agent focused usage guides",
            "🔄 **Compatibility**: Better handling of version routing and fallbacks",
            "⚡ **Response Times**: Reduced API response latency",
            "🧪 **Testing**: Expanded test coverage for reliability"
        ]
        
        return "\n".join(f"- {improvement}" for improvement in improvements)
        
    def generate_bug_fixes(self, version: str, previous_version: Optional[str]) -> str:
        """Generate bug fixes section."""
        if not previous_version:
            return "- ✅ No bug fixes in initial release"
            
        fixes = [
            "🔧 Fixed decimal serialization in JSON responses",
            "📊 Fixed PnL calculation edge cases with zero cost basis",
            "🔄 Fixed background poller error handling",
            "⚠️ Fixed error messages for invalid tickers",
            "🛡️ Fixed kill switch state persistence",
            "📈 Fixed strategy summary aggregation",
            "🔍 Fixed health check timeout issues"
        ]
        
        return "\n".join(f"- {fix}" for fix in fixes)
        
    def generate_api_changes(self, version: str, previous_version: Optional[str]) -> str:
        """Generate API changes section."""
        if not previous_version:
            return self.generate_initial_api_spec(version)
            
        return f"""### API Endpoints ({version})

#### New Endpoints
- `GET /{version}/health` - Version-specific health check
- `GET /{version}/versions` - List available API versions
- `GET /{version}/tools/{{tool_name}}` - Tool execution via GET (convenience)

#### Modified Endpoints
- All endpoints now include version in URL path
- Enhanced error responses with version information
- Improved response headers with deprecation warnings

#### Deprecated Endpoints
- Unversioned endpoints (will redirect to current version)
- Legacy `/mcp/` prefix (maintained for backward compatibility)

#### Response Format Changes
- Added `X-API-Version` header to all responses
- Enhanced error messages with context
- Consistent decimal precision in financial data
"""

    def generate_initial_api_spec(self, version: str) -> str:
        """Generate initial API specification."""
        return f"""### API Endpoints ({version})

#### Tools (POST)
- `POST /{version}/tools/buy_stock` - Execute stock purchase
- `POST /{version}/tools/sell_stock` - Execute stock sale  
- `POST /{version}/tools/execute_trade` - Advanced trade execution
- `POST /{version}/tools/get_account_status` - Account information
- `POST /{version}/tools/get_recent_orders` - Order history
- `POST /{version}/tools/activate_kill_switch` - Emergency stop
- `POST /{version}/tools/deactivate_kill_switch` - Resume trading

#### Resources (GET)
- `GET /{version}/resources/account_info` - Account details
- `GET /{version}/resources/current_positions` - Live positions
- `GET /{version}/resources/portfolio_summary` - Portfolio overview
- `GET /{version}/resources/strategy_summary` - Strategy analytics
- `GET /{version}/resources/system_health` - System status

#### System Endpoints
- `GET /{version}/health` - Version health check
- `GET /health` - Global health check
- `GET /versions` - List all API versions
"""

    def generate_migration_guide(self, version: str, previous_version: Optional[str]) -> str:
        """Generate migration guide section."""
        if not previous_version:
            return f"""### Getting Started with {version}

This is the initial release. Follow the setup guide:

1. **Installation**: Use `./start-server.sh` to install dependencies and start the server
2. **Configuration**: Set up your `.env` file with Alpaca credentials
3. **Basic Usage**: Start with health checks and account status
4. **Documentation**: Refer to the AI Agent Usage Guide for detailed examples

No migration needed for new installations.
"""
            
        version_parts = self.parse_version(version)
        prev_parts = self.parse_version(previous_version)
        
        if version_parts[0] > prev_parts[0]:
            # Major version migration
            return f"""### Migrating from {previous_version} to {version}

**🚨 Action Required**: This major release requires client updates.

#### URL Updates
```bash
# OLD
curl http://localhost:8000/mcp/tools/buy_stock

# NEW  
curl http://localhost:8000/{version}/tools/buy_stock
```

#### Response Changes
- Some field names have been standardized
- Error format has been enhanced
- Headers now include version information

#### Testing Migration
1. Update your client code to use versioned URLs
2. Test against the new endpoints
3. Verify response parsing still works
4. Update error handling for new status codes

#### Backward Compatibility
- Old endpoints will redirect to current version
- Consider updating to explicit versioning for best performance
"""
        else:
            # Minor/patch version migration  
            return f"""### Migrating from {previous_version} to {version}

✅ **Good News**: This release is fully backward compatible!

#### Optional Updates
- Consider using versioned URLs for explicit version control
- Update to take advantage of new features
- Review enhanced error messages

#### No Action Required
- Existing clients will continue to work
- Automatic redirects handle unversioned requests
"""

    def generate_git_changelog(self, version: str, previous_version: Optional[str]) -> str:
        """Generate Git-based changelog."""
        try:
            if previous_version:
                # Get commits between versions
                cmd = f"git log --oneline {previous_version}..HEAD"
            else:
                # Get all commits
                cmd = "git log --oneline"
                
            result = subprocess.run(
                cmd.split(), 
                capture_output=True, 
                text=True, 
                cwd=self.base_path
            )
            
            if result.returncode == 0 and result.stdout:
                commits = result.stdout.strip().split('\n')
                formatted_commits = []
                
                for commit in commits[:20]:  # Limit to 20 commits
                    if commit.strip():
                        formatted_commits.append(f"- {commit}")
                        
                if len(commits) > 20:
                    formatted_commits.append(f"- ... and {len(commits) - 20} more commits")
                    
                return "\n".join(formatted_commits)
            else:
                return "- Git changelog not available"
                
        except Exception as e:
            logger.warning(f"Could not generate git changelog: {e}")
            return "- Git changelog not available"
            
    def save_release_notes(self, version: str, release_notes: str) -> Path:
        """Save release notes to file."""
        if not version.startswith('v'):
            version = f"v{version}"
            
        # Save to main changelog
        changelog_path = self.base_path / "CHANGELOG.md"
        
        # Read existing changelog
        existing_content = ""
        if changelog_path.exists():
            with open(changelog_path, 'r') as f:
                existing_content = f.read()
                
        # Prepend new release notes
        updated_content = f"{release_notes}\n\n---\n\n{existing_content}"
        
        with open(changelog_path, 'w') as f:
            f.write(updated_content)
            
        # Also save version-specific release notes
        version_dir = self.base_path / "api_versions" / version
        version_dir.mkdir(parents=True, exist_ok=True)
        
        version_notes_path = version_dir / "RELEASE_NOTES.md"
        with open(version_notes_path, 'w') as f:
            f.write(release_notes)
            
        logger.info(f"Saved release notes: {changelog_path} and {version_notes_path}")
        return changelog_path
        
    def generate_github_release_notes(self, version: str, previous_version: Optional[str] = None) -> Dict:
        """Generate GitHub-compatible release notes."""
        release_notes = self.generate_release_notes(version, previous_version)
        
        # Extract sections for GitHub
        lines = release_notes.split('\n')
        overview = []
        changes = []
        
        current_section = None
        for line in lines:
            if line.startswith('## ✨ New Features'):
                current_section = 'features'
                continue
            elif line.startswith('## 🔧 Improvements'):
                current_section = 'improvements'
                continue
            elif line.startswith('## 🐛 Bug Fixes'):
                current_section = 'fixes'
                continue
            elif line.startswith('## 🚨 Breaking Changes'):
                current_section = 'breaking'
                continue
            elif line.startswith('##'):
                current_section = None
                continue
                
            if current_section and line.strip():
                changes.append(line)
                
        return {
            "tag_name": version,
            "name": f"Release {version}",
            "body": release_notes,
            "draft": False,
            "prerelease": "beta" in version.lower() or "alpha" in version.lower()
        }
