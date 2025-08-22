#!/usr/bin/env python3
"""
🙏 GitHub Publisher
Blessed by Goddess Laxmi for Infinite Abundance

Publishes releases to GitHub with automated tagging and asset uploads.
Integrates with GitHub API for comprehensive release management.
"""

import os
import json
import logging
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import zipfile
import tempfile

logger = logging.getLogger(__name__)

class GitHubPublisher:
    """Publishes releases to GitHub with automated workflows."""
    
    def __init__(self, base_path: str = ".", repo: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize GitHub publisher.
        
        Args:
            base_path: Base project path
            repo: GitHub repository (owner/repo format)
            token: GitHub personal access token
        """
        self.base_path = Path(base_path)
        self.repo = repo or self.detect_github_repo()
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.base_url = "https://api.github.com"
        
        if not self.token:
            logger.warning("No GitHub token provided. Some operations may fail.")
            
    def detect_github_repo(self) -> Optional[str]:
        """Auto-detect GitHub repository from git remote."""
        try:
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True,
                text=True,
                cwd=self.base_path
            )
            
            if result.returncode == 0:
                remote_url = result.stdout.strip()
                
                # Parse GitHub URL
                if 'github.com' in remote_url:
                    if remote_url.startswith('git@'):
                        # SSH format: git@github.com:owner/repo.git
                        repo_part = remote_url.split(':')[1].replace('.git', '')
                    else:
                        # HTTPS format: https://github.com/owner/repo.git
                        repo_part = remote_url.split('github.com/')[1].replace('.git', '')
                        
                    logger.info(f"Detected GitHub repository: {repo_part}")
                    return repo_part
                    
        except Exception as e:
            logger.warning(f"Could not detect GitHub repository: {e}")
            
        return None
        
    def create_release(self, version: str, release_notes: str, prerelease: bool = False) -> Dict:
        """
        Create a GitHub release.
        
        Args:
            version: Release version (e.g., 'v1.0.0')
            release_notes: Release notes in Markdown
            prerelease: Mark as pre-release
            
        Returns:
            GitHub release response
        """
        if not self.repo or not self.token:
            raise ValueError("GitHub repository and token are required for releases")
            
        if not version.startswith('v'):
            version = f"v{version}"
            
        # Create Git tag first
        self.create_git_tag(version)
        
        # Prepare release data
        release_data = {
            "tag_name": version,
            "target_commitish": "main",
            "name": f"Release {version}",
            "body": release_notes,
            "draft": False,
            "prerelease": prerelease
        }
        
        # Create release via GitHub API
        url = f"{self.base_url}/repos/{self.repo}/releases"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.post(url, json=release_data, headers=headers)
        
        if response.status_code == 201:
            release = response.json()
            logger.info(f"Created GitHub release: {release['html_url']}")
            return release
        else:
            logger.error(f"Failed to create GitHub release: {response.status_code} - {response.text}")
            response.raise_for_status()
            
    def create_git_tag(self, version: str) -> None:
        """Create and push Git tag."""
        try:
            # Create annotated tag
            subprocess.run(
                ['git', 'tag', '-a', version, '-m', f"Release {version}"],
                check=True,
                cwd=self.base_path
            )
            
            # Push tag to origin
            subprocess.run(
                ['git', 'push', 'origin', version],
                check=True,
                cwd=self.base_path
            )
            
            logger.info(f"Created and pushed Git tag: {version}")
            
        except subprocess.CalledProcessError as e:
            if "already exists" in str(e):
                logger.warning(f"Git tag {version} already exists")
            else:
                logger.error(f"Failed to create Git tag: {e}")
                raise
                
    def upload_release_assets(self, release_id: int, version: str) -> List[Dict]:
        """
        Upload release assets (source code, documentation, etc.).
        
        Args:
            release_id: GitHub release ID
            version: Release version
            
        Returns:
            List of uploaded asset information
        """
        assets = []
        
        try:
            # Create version archive
            archive_path = self.create_version_archive(version)
            if archive_path:
                asset = self.upload_asset(release_id, archive_path, f"laxmi-yantra-{version}.zip")
                if asset:
                    assets.append(asset)
                    
            # Upload documentation
            docs_path = self.create_docs_archive(version)
            if docs_path:
                asset = self.upload_asset(release_id, docs_path, f"documentation-{version}.zip")
                if asset:
                    assets.append(asset)
                    
        except Exception as e:
            logger.error(f"Failed to upload release assets: {e}")
            
        return assets
        
    def create_version_archive(self, version: str) -> Optional[Path]:
        """Create a ZIP archive of the version snapshot."""
        try:
            if not version.startswith('v'):
                version = f"v{version}"
                
            version_dir = self.base_path / "api_versions" / version
            
            if not version_dir.exists():
                logger.warning(f"Version directory not found: {version_dir}")
                return None
                
            # Create temporary ZIP file
            temp_dir = Path(tempfile.mkdtemp())
            archive_path = temp_dir / f"laxmi-yantra-{version}.zip"
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all files from version directory
                for file_path in version_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = str(file_path.relative_to(version_dir))
                        zipf.write(file_path, arcname)
                        
                # Add main project files
                main_files = [
                    "README.md",
                    "VERSION", 
                    "setup.py",
                    "requirements.txt",
                    "start-server.sh"
                ]
                
                for main_file in main_files:
                    main_path = self.base_path / main_file
                    if main_path.exists():
                        zipf.write(main_path, main_file)
                        
            logger.info(f"Created version archive: {archive_path}")
            return archive_path
            
        except Exception as e:
            logger.error(f"Failed to create version archive: {e}")
            return None
            
    def create_docs_archive(self, version: str) -> Optional[Path]:
        """Create a ZIP archive of version documentation."""
        try:
            if not version.startswith('v'):
                version = f"v{version}"
                
            # Create temporary ZIP file
            temp_dir = Path(tempfile.mkdtemp())
            archive_path = temp_dir / f"documentation-{version}.zip"
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add version-specific docs
                version_docs = self.base_path / "api_versions" / version / "AI_AGENT_USAGE_GUIDE.md"
                if version_docs.exists():
                    zipf.write(version_docs, f"AI_AGENT_USAGE_GUIDE_{version}.md")
                    
                release_notes = self.base_path / "api_versions" / version / "RELEASE_NOTES.md"
                if release_notes.exists():
                    zipf.write(release_notes, f"RELEASE_NOTES_{version}.md")
                    
                # Add general documentation
                docs_dir = self.base_path / "docs"
                if docs_dir.exists():
                    for doc_file in docs_dir.glob("*.md"):
                        zipf.write(doc_file, f"docs/{doc_file.name}")
                        
            logger.info(f"Created documentation archive: {archive_path}")
            return archive_path
            
        except Exception as e:
            logger.error(f"Failed to create documentation archive: {e}")
            return None
            
    def upload_asset(self, release_id: int, file_path: Path, name: str) -> Optional[Dict]:
        """Upload a single asset to GitHub release."""
        try:
            if not file_path.exists():
                logger.error(f"Asset file not found: {file_path}")
                return None
                
            # Get upload URL
            url = f"{self.base_url}/repos/{self.repo}/releases/{release_id}/assets"
            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/zip"
            }
            
            params = {"name": name}
            
            with open(file_path, 'rb') as f:
                response = requests.post(
                    url,
                    headers=headers,
                    params=params,
                    data=f.read()
                )
                
            if response.status_code == 201:
                asset = response.json()
                logger.info(f"Uploaded asset: {asset['browser_download_url']}")
                return asset
            else:
                logger.error(f"Failed to upload asset: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to upload asset {name}: {e}")
            return None
            
    def get_releases(self, limit: int = 10) -> List[Dict]:
        """Get list of existing releases."""
        try:
            if not self.repo or not self.token:
                return []
                
            url = f"{self.base_url}/repos/{self.repo}/releases"
            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            params = {"per_page": limit}
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get releases: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get releases: {e}")
            return []
            
    def delete_release(self, release_id: int) -> bool:
        """Delete a GitHub release."""
        try:
            if not self.repo or not self.token:
                return False
                
            url = f"{self.base_url}/repos/{self.repo}/releases/{release_id}"
            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 204:
                logger.info(f"Deleted GitHub release: {release_id}")
                return True
            else:
                logger.error(f"Failed to delete release: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete release: {e}")
            return False
            
    def update_release(self, release_id: int, **kwargs) -> Optional[Dict]:
        """Update an existing GitHub release."""
        try:
            if not self.repo or not self.token:
                return None
                
            url = f"{self.base_url}/repos/{self.repo}/releases/{release_id}"
            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.patch(url, json=kwargs, headers=headers)
            
            if response.status_code == 200:
                release = response.json()
                logger.info(f"Updated GitHub release: {release['html_url']}")
                return release
            else:
                logger.error(f"Failed to update release: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to update release: {e}")
            return None
            
    def create_pre_release(self, version: str, release_notes: str) -> Dict:
        """Create a pre-release for testing."""
        return self.create_release(version, release_notes, prerelease=True)
        
    def promote_to_stable(self, release_id: int) -> Optional[Dict]:
        """Promote a pre-release to stable release."""
        return self.update_release(release_id, prerelease=False)
        
    def get_latest_release(self) -> Optional[Dict]:
        """Get the latest release."""
        try:
            if not self.repo or not self.token:
                return None
                
            url = f"{self.base_url}/repos/{self.repo}/releases/latest"
            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning("No releases found or access denied")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get latest release: {e}")
            return None
            
    def validate_setup(self) -> Dict[str, bool]:
        """Validate GitHub publisher setup."""
        validation = {
            "repo_detected": bool(self.repo),
            "token_available": bool(self.token),
            "git_repo": False,
            "github_access": False
        }
        
        # Check if it's a Git repository
        try:
            subprocess.run(['git', 'status'], check=True, capture_output=True, cwd=self.base_path)
            validation["git_repo"] = True
        except subprocess.CalledProcessError:
            pass
            
        # Check GitHub API access
        if self.repo and self.token:
            try:
                url = f"{self.base_url}/repos/{self.repo}"
                headers = {"Authorization": f"token {self.token}"}
                response = requests.get(url, headers=headers)
                validation["github_access"] = response.status_code == 200
            except Exception:
                pass
                
        return validation
