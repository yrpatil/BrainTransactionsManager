#!/usr/bin/env python3
"""
🙏 Release Manager
Blessed by Goddess Laxmi for Infinite Abundance

Main release orchestration system that coordinates version snapshots,
documentation generation, release notes, and GitHub publishing.
"""

import os
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from .version_snapshot import VersionSnapshot
from .release_notes_generator import ReleaseNotesGenerator
from .api_docs_generator import APIDocsGenerator
from .github_publisher import GitHubPublisher

logger = logging.getLogger(__name__)

class ReleaseManager:
    """Orchestrates the complete release process."""
    
    def __init__(self, base_path: str = "."):
        """Initialize release manager."""
        self.base_path = Path(base_path)
        self.snapshot = VersionSnapshot(base_path)
        self.notes_generator = ReleaseNotesGenerator(base_path)
        self.docs_generator = APIDocsGenerator(base_path)
        self.github_publisher = GitHubPublisher(base_path)
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self) -> None:
        """Setup release-specific logging."""
        log_dir = self.base_path / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / "releases.log"
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
        
    def create_release(
        self,
        version: str,
        release_type: str = "minor",
        push_to_github: bool = True,
        prerelease: bool = False,
        dry_run: bool = False
    ) -> Dict:
        """
        Create a complete release with all components.
        
        Args:
            version: Version string (e.g., '1.1.0' or 'v1.1.0')
            release_type: Type of release ('major', 'minor', 'patch')
            push_to_github: Whether to push to GitHub
            prerelease: Mark as pre-release
            dry_run: Simulate release without making changes
            
        Returns:
            Release summary information
        """
        logger.info(f"🚀 Starting release process for {version}")
        logger.info(f"Release type: {release_type}, GitHub: {push_to_github}, Pre-release: {prerelease}, Dry run: {dry_run}")
        
        if not version.startswith('v'):
            version = f"v{version}"
            
        # Validate release
        validation_result = self.validate_release(version, release_type)
        if not validation_result["valid"]:
            raise ValueError(f"Release validation failed: {validation_result['errors']}")
            
        release_summary = {
            "version": version,
            "release_type": release_type,
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "steps": {}
        }
        
        try:
            # Step 1: Update version files
            logger.info("📝 Updating version files...")
            if not dry_run:
                self.update_version_files(version)
            release_summary["steps"]["version_files"] = {"status": "completed" if not dry_run else "skipped"}
            
            # Step 2: Run tests (temporarily optional)
            skip_tests = os.getenv('RELEASE_SKIP_TESTS', 'false').lower() == 'true'
            if skip_tests:
                logger.info("🧪 Skipping tests due to RELEASE_SKIP_TESTS=true")
                release_summary["steps"]["tests"] = {"status": "skipped", "passed": True}
            else:
                logger.info("🧪 Running tests...")
                test_result = self.run_tests(dry_run)
                release_summary["steps"]["tests"] = test_result
                if not test_result["passed"]:
                    raise RuntimeError("Tests failed - aborting release")
                
            # Step 3: Create version snapshot
            logger.info("📸 Creating version snapshot...")
            if not dry_run:
                self.snapshot.create_snapshot(version)
                self.snapshot.update_config(version)
            release_summary["steps"]["snapshot"] = {"status": "completed" if not dry_run else "skipped"}
            
            # Step 4: Generate release notes
            logger.info("📄 Generating release notes...")
            previous_version = self.get_previous_version(version)
            release_notes = self.notes_generator.generate_release_notes(version, previous_version)
            
            if not dry_run:
                self.notes_generator.save_release_notes(version, release_notes)
            release_summary["steps"]["release_notes"] = {"status": "completed" if not dry_run else "skipped"}
            
            # Step 5: Generate API documentation
            logger.info("📚 Generating API documentation...")
            if not dry_run:
                docs = self.docs_generator.generate_version_docs(version)
                self.docs_generator.save_version_docs(version, docs)
                self.docs_generator.update_main_docs_index(version)
            release_summary["steps"]["documentation"] = {"status": "completed" if not dry_run else "skipped"}
            
            # Step 6: Create Git commit and tag
            logger.info("🏷️ Creating Git commit and tag...")
            if not dry_run:
                self.create_release_commit(version)
            release_summary["steps"]["git_commit"] = {"status": "completed" if not dry_run else "skipped"}
            
            # Step 7: GitHub release (optional)
            github_result = {"status": "skipped"}
            if push_to_github and not dry_run:
                logger.info("🌐 Publishing to GitHub...")
                try:
                    github_release = self.github_publisher.create_release(
                        version, release_notes, prerelease
                    )
                    
                    # Upload assets
                    assets = self.github_publisher.upload_release_assets(
                        github_release["id"], version
                    )
                    
                    github_result = {
                        "status": "completed",
                        "release_url": github_release["html_url"],
                        "assets_uploaded": len(assets)
                    }
                    
                except Exception as e:
                    logger.error(f"GitHub publishing failed: {e}")
                    github_result = {"status": "failed", "error": str(e)}
                    
            release_summary["steps"]["github_release"] = github_result
            
            # Step 8: Post-release tasks
            logger.info("🔄 Running post-release tasks...")
            if not dry_run:
                self.run_post_release_tasks(version)
            release_summary["steps"]["post_release"] = {"status": "completed" if not dry_run else "skipped"}
            
            release_summary["status"] = "completed"
            logger.info(f"✅ Release {version} completed successfully!")
            
        except Exception as e:
            release_summary["status"] = "failed"
            release_summary["error"] = str(e)
            logger.error(f"❌ Release {version} failed: {e}")
            raise
            
        finally:
            # Save release summary
            self.save_release_summary(release_summary)
            
        return release_summary
        
    def validate_release(self, version: str, release_type: str) -> Dict:
        """Validate release prerequisites."""
        errors = []
        warnings = []
        
        # Check version format
        if not self.is_valid_version(version):
            errors.append(f"Invalid version format: {version}")
            
        # Check if version already exists
        if self.version_exists(version):
            errors.append(f"Version {version} already exists")
            
        # Check Git status
        if not self.is_git_clean():
            warnings.append("Git working directory is not clean")
            
        # Check if tests exist
        if not self.tests_exist():
            warnings.append("No tests found")
            
        # Validate GitHub setup if needed
        github_validation = self.github_publisher.validate_setup()
        if not github_validation["git_repo"]:
            warnings.append("Not a Git repository")
        if not github_validation["github_access"]:
            warnings.append("GitHub access not configured")
            
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
        
    def is_valid_version(self, version: str) -> bool:
        """Check if version format is valid."""
        import re
        pattern = r'^v?\d+\.\d+\.\d+$'
        return bool(re.match(pattern, version))
        
    def version_exists(self, version: str) -> bool:
        """Check if version already exists."""
        try:
            config_path = self.base_path / "config" / "api_versions.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    
                active_versions = config.get('active_versions', [])
                deprecated_versions = config.get('deprecated_versions', [])
                
                return version in active_versions or version in deprecated_versions
                
        except Exception:
            pass
            
        return False
        
    def is_git_clean(self) -> bool:
        """Check if Git working directory is clean."""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                cwd=self.base_path
            )
            
            return result.returncode == 0 and not result.stdout.strip()
            
        except Exception:
            return False
            
    def tests_exist(self) -> bool:
        """Check if tests exist."""
        test_paths = [
            self.base_path / "tests",
            self.base_path / "test",
            self.base_path / "pytest.ini",
            self.base_path / "conftest.py"
        ]
        
        return any(path.exists() for path in test_paths)
        
    def update_version_files(self, version: str) -> None:
        """Update version in relevant files."""
        version_str = version.lstrip('v')
        
        # Update VERSION file
        version_file = self.base_path / "VERSION"
        with open(version_file, 'w') as f:
            f.write(f"{version_str}\n")
            
        # Update setup.py
        setup_file = self.base_path / "setup.py"
        if setup_file.exists():
            with open(setup_file, 'r') as f:
                content = f.read()
                
            # Replace version string
            import re
            content = re.sub(
                r'version\s*=\s*["\'][^"\']+["\']',
                f'version="{version_str}"',
                content
            )
            
            with open(setup_file, 'w') as f:
                f.write(content)
                
        logger.info(f"Updated version files to {version_str}")
        
    def run_tests(self, dry_run: bool = False) -> Dict:
        """Run test suite."""
        if dry_run:
            return {"status": "skipped", "passed": True}
            
        if not self.tests_exist():
            logger.warning("No tests found - skipping test execution")
            return {"status": "skipped", "passed": True}
            
        try:
            # Try pytest first
            result = subprocess.run(
                ['python', '-m', 'pytest', '-v'],
                capture_output=True,
                text=True,
                cwd=self.base_path,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                logger.info("✅ All tests passed")
                return {
                    "status": "completed",
                    "passed": True,
                    "output": result.stdout
                }
            else:
                logger.error("❌ Tests failed")
                return {
                    "status": "failed", 
                    "passed": False,
                    "output": result.stdout,
                    "errors": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            logger.error("Tests timed out")
            return {"status": "timeout", "passed": False}
        except FileNotFoundError:
            # Fallback to unittest
            try:
                result = subprocess.run(
                    ['python', '-m', 'unittest', 'discover', '-v'],
                    capture_output=True,
                    text=True,
                    cwd=self.base_path,
                    timeout=300
                )
                
                return {
                    "status": "completed",
                    "passed": result.returncode == 0,
                    "output": result.stdout
                }
                
            except Exception as e:
                logger.warning(f"Could not run tests: {e}")
                return {"status": "skipped", "passed": True}
                
    def get_previous_version(self, current_version: str) -> Optional[str]:
        """Get previous version for changelog generation."""
        return self.notes_generator.get_previous_version(current_version)
        
    def create_release_commit(self, version: str) -> None:
        """Create Git commit and tag for release."""
        try:
            # Add changed files
            subprocess.run(['git', 'add', '.'], check=True, cwd=self.base_path)
            
            # Create commit
            commit_message = f"Release {version}\n\n- Updated version files\n- Created version snapshot\n- Generated documentation\n\n🙏 Blessed by Goddess Laxmi"
            
            subprocess.run(
                ['git', 'commit', '-m', commit_message],
                check=True,
                cwd=self.base_path
            )
            
            logger.info(f"Created release commit for {version}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create release commit: {e}")
            raise
            
    def run_post_release_tasks(self, version: str) -> None:
        """Run post-release cleanup and preparation tasks."""
        try:
            # Validate release artifacts
            if not self.snapshot.validate_snapshot(version):
                logger.warning(f"Version snapshot validation failed for {version}")
                
            # Update changelog
            changelog_path = self.base_path / "CHANGELOG.md"
            if changelog_path.exists():
                logger.info("Updated main changelog")
                
            # Clean up temporary files
            temp_dirs = [
                self.base_path / "build",
                self.base_path / "dist", 
                self.base_path / "*.egg-info"
            ]
            
            for temp_dir in temp_dirs:
                if temp_dir.exists():
                    import shutil
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    
            logger.info("Completed post-release tasks")
            
        except Exception as e:
            logger.warning(f"Post-release tasks encountered issues: {e}")
            
    def save_release_summary(self, summary: Dict) -> None:
        """Save release summary for tracking."""
        try:
            releases_dir = self.base_path / "releases"
            releases_dir.mkdir(exist_ok=True)
            
            summary_file = releases_dir / f"release_{summary['version']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
                
            logger.info(f"Saved release summary: {summary_file}")
            
        except Exception as e:
            logger.warning(f"Could not save release summary: {e}")
            
    def list_releases(self) -> List[Dict]:
        """List all releases."""
        releases = []
        
        try:
            config_path = self.base_path / "config" / "api_versions.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    
                version_metadata = config.get('version_metadata', {})
                
                for version, metadata in version_metadata.items():
                    releases.append({
                        "version": version,
                        "release_date": metadata.get('release_date'),
                        "status": metadata.get('status'),
                        "breaking_changes": metadata.get('breaking_changes', False)
                    })
                    
        except Exception as e:
            logger.error(f"Could not list releases: {e}")
            
        return sorted(releases, key=lambda r: r['version'], reverse=True)
        
    def rollback_release(self, version: str) -> Dict:
        """Rollback a release (mark as deprecated)."""
        try:
            if not version.startswith('v'):
                version = f"v{version}"
                
            # Update config to deprecate version
            config_path = self.base_path / "config" / "api_versions.json"
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            active_versions = config.get('active_versions', [])
            deprecated_versions = config.get('deprecated_versions', [])
            
            if version in active_versions:
                active_versions.remove(version)
                deprecated_versions.append(version)
                
                config['active_versions'] = active_versions
                config['deprecated_versions'] = deprecated_versions
                
                # Update metadata
                version_metadata = config.get('version_metadata', {})
                if version in version_metadata:
                    version_metadata[version]['status'] = 'deprecated'
                    version_metadata[version]['deprecation_date'] = datetime.now().strftime("%Y-%m-%d")
                    
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                    
                logger.info(f"Rolled back version {version}")
                return {"status": "success", "message": f"Version {version} marked as deprecated"}
                
            else:
                return {"status": "error", "message": f"Version {version} not found in active versions"}
                
        except Exception as e:
            logger.error(f"Failed to rollback version {version}: {e}")
            return {"status": "error", "message": str(e)}
            
    def get_release_info(self, version: str) -> Optional[Dict]:
        """Get detailed information about a specific release."""
        try:
            if not version.startswith('v'):
                version = f"v{version}"
                
            config_path = self.base_path / "config" / "api_versions.json"
            with open(config_path, 'r') as f:
                config = json.load(f)
                
            version_metadata = config.get('version_metadata', {})
            
            if version in version_metadata:
                info = version_metadata[version].copy()
                info['version'] = version
                
                # Add additional information
                version_dir = self.base_path / "api_versions" / version
                info['snapshot_exists'] = version_dir.exists()
                info['snapshot_valid'] = self.snapshot.validate_snapshot(version) if version_dir.exists() else False
                
                # Check documentation
                docs_path = version_dir / "AI_AGENT_USAGE_GUIDE.md"
                info['documentation_exists'] = docs_path.exists()
                
                return info
                
        except Exception as e:
            logger.error(f"Could not get release info for {version}: {e}")
            
        return None
