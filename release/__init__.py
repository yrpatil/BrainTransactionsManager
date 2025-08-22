#!/usr/bin/env python3
"""
🙏 Release Management Module
Blessed by Goddess Laxmi for Infinite Abundance

Automated release system for API versioning and GitHub integration.
Handles version snapshots, tagging, and backward compatibility.
"""

__version__ = "1.0.0"
__author__ = "AlgoChemist Team"

from .release_manager import ReleaseManager
from .version_snapshot import VersionSnapshot
from .github_publisher import GitHubPublisher

__all__ = [
    "ReleaseManager",
    "VersionSnapshot", 
    "GitHubPublisher"
]
