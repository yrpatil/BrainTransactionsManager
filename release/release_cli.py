#!/usr/bin/env python3
"""
🙏 Release CLI
Blessed by Goddess Laxmi for Infinite Abundance

Command-line interface for managing API releases and versioning.
"""

import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from release.release_manager import ReleaseManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="🙏 Laxmi-yantra Release Management CLI - Blessed by Goddess Laxmi"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create release command
    create_parser = subparsers.add_parser('create', help='Create a new release')
    create_parser.add_argument('version', help='Version to release (e.g., 1.1.0 or v1.1.0)')
    create_parser.add_argument('--type', choices=['major', 'minor', 'patch'], default='minor',
                              help='Type of release (default: minor)')
    create_parser.add_argument('--no-github', action='store_true',
                              help='Skip GitHub publishing')
    create_parser.add_argument('--prerelease', action='store_true',
                              help='Mark as pre-release')
    create_parser.add_argument('--dry-run', action='store_true',
                              help='Simulate release without making changes')
    
    # List releases command
    list_parser = subparsers.add_parser('list', help='List all releases')
    list_parser.add_argument('--format', choices=['table', 'json'], default='table',
                            help='Output format')
    
    # Release info command
    info_parser = subparsers.add_parser('info', help='Get release information')
    info_parser.add_argument('version', help='Version to get info for')
    
    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback a release')
    rollback_parser.add_argument('version', help='Version to rollback')
    
    # Generate docs command
    docs_parser = subparsers.add_parser('docs', help='Generate documentation')
    docs_parser.add_argument('version', nargs='?', help='Version to generate docs for (default: all)')
    docs_parser.add_argument('--all', action='store_true', help='Generate docs for all versions')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate release setup')
    validate_parser.add_argument('version', nargs='?', help='Version to validate')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    # Initialize release manager
    release_manager = ReleaseManager()
    
    try:
        if args.command == 'create':
            create_release(release_manager, args)
        elif args.command == 'list':
            list_releases(release_manager, args)
        elif args.command == 'info':
            show_release_info(release_manager, args)
        elif args.command == 'rollback':
            rollback_release(release_manager, args)
        elif args.command == 'docs':
            generate_docs(release_manager, args)
        elif args.command == 'validate':
            validate_setup(release_manager, args)
            
    except Exception as e:
        logger.error(f"Command failed: {e}")
        sys.exit(1)

def create_release(release_manager: ReleaseManager, args):
    """Create a new release."""
    logger.info(f"🚀 Creating release {args.version}")
    
    if args.dry_run:
        logger.info("🧪 DRY RUN MODE - No changes will be made")
        
    try:
        result = release_manager.create_release(
            version=args.version,
            release_type=args.type,
            push_to_github=not args.no_github,
            prerelease=args.prerelease,
            dry_run=args.dry_run
        )
        
        print("\n" + "="*60)
        print(f"🎉 Release {result['version']} {result['status'].upper()}!")
        print("="*60)
        
        # Print step summary
        for step, info in result['steps'].items():
            status_emoji = "✅" if info['status'] == 'completed' else "⏭️" if info['status'] == 'skipped' else "❌"
            print(f"{status_emoji} {step.replace('_', ' ').title()}: {info['status']}")
            
        if result.get('steps', {}).get('github_release', {}).get('release_url'):
            print(f"\n🌐 GitHub Release: {result['steps']['github_release']['release_url']}")
            
        print(f"\n📊 Release Summary:")
        print(f"   Version: {result['version']}")
        print(f"   Type: {result['release_type']}")
        print(f"   Timestamp: {result['timestamp']}")
        
        if args.dry_run:
            print("\n⚠️  This was a dry run - no actual changes were made")
            
    except Exception as e:
        logger.error(f"Release creation failed: {e}")
        sys.exit(1)

def list_releases(release_manager: ReleaseManager, args):
    """List all releases."""
    releases = release_manager.list_releases()
    
    if args.format == 'json':
        print(json.dumps(releases, indent=2))
    else:
        print("\n📋 Laxmi-yantra API Releases")
        print("="*60)
        print(f"{'Version':<12} {'Release Date':<12} {'Status':<12} {'Breaking':<10}")
        print("-"*60)
        
        for release in releases:
            breaking = "Yes" if release.get('breaking_changes') else "No"
            print(f"{release['version']:<12} {release['release_date']:<12} {release['status']:<12} {breaking:<10}")
            
        if not releases:
            print("No releases found.")
            
        print(f"\nTotal releases: {len(releases)}")

def show_release_info(release_manager: ReleaseManager, args):
    """Show detailed release information."""
    info = release_manager.get_release_info(args.version)
    
    if not info:
        logger.error(f"Release {args.version} not found")
        sys.exit(1)
        
    print(f"\n📊 Release Information: {info['version']}")
    print("="*50)
    print(f"Release Date: {info.get('release_date', 'Unknown')}")
    print(f"Status: {info.get('status', 'Unknown')}")
    print(f"Breaking Changes: {'Yes' if info.get('breaking_changes') else 'No'}")
    print(f"Deprecation Date: {info.get('deprecation_date', 'N/A')}")
    print(f"End of Life: {info.get('end_of_life_date', 'N/A')}")
    
    print(f"\n📁 Artifacts:")
    print(f"Snapshot Exists: {'✅' if info.get('snapshot_exists') else '❌'}")
    print(f"Snapshot Valid: {'✅' if info.get('snapshot_valid') else '❌'}")
    print(f"Documentation: {'✅' if info.get('documentation_exists') else '❌'}")

def rollback_release(release_manager: ReleaseManager, args):
    """Rollback a release."""
    logger.info(f"🔄 Rolling back release {args.version}")
    
    result = release_manager.rollback_release(args.version)
    
    if result['status'] == 'success':
        print(f"✅ {result['message']}")
    else:
        print(f"❌ {result['message']}")
        sys.exit(1)

def generate_docs(release_manager: ReleaseManager, args):
    """Generate documentation."""
    if args.all or not args.version:
        logger.info("📚 Generating documentation for all versions")
        release_manager.docs_generator.generate_all_versions_docs()
        print("✅ Generated documentation for all versions")
    else:
        logger.info(f"📚 Generating documentation for {args.version}")
        docs = release_manager.docs_generator.generate_version_docs(args.version)
        docs_path = release_manager.docs_generator.save_version_docs(args.version, docs)
        release_manager.docs_generator.update_main_docs_index(args.version)
        print(f"✅ Generated documentation: {docs_path}")

def validate_setup(release_manager: ReleaseManager, args):
    """Validate release setup."""
    print("\n🔍 Validating Release Setup")
    print("="*40)
    
    # GitHub validation
    github_validation = release_manager.github_publisher.validate_setup()
    
    print(f"Git Repository: {'✅' if github_validation['git_repo'] else '❌'}")
    print(f"GitHub Repo Detected: {'✅' if github_validation['repo_detected'] else '❌'}")
    print(f"GitHub Token: {'✅' if github_validation['token_available'] else '❌'}")
    print(f"GitHub Access: {'✅' if github_validation['github_access'] else '❌'}")
    
    # Test validation
    tests_exist = release_manager.tests_exist()
    git_clean = release_manager.is_git_clean()
    
    print(f"Tests Available: {'✅' if tests_exist else '⚠️'}")
    print(f"Git Working Directory Clean: {'✅' if git_clean else '⚠️'}")
    
    # Version validation (if provided)
    if args.version:
        print(f"\n🔍 Validating Version: {args.version}")
        print("-"*30)
        
        validation = release_manager.validate_release(args.version, 'minor')
        
        if validation['valid']:
            print("✅ Version validation passed")
        else:
            print("❌ Version validation failed:")
            for error in validation['errors']:
                print(f"   - {error}")
                
        if validation['warnings']:
            print("⚠️  Warnings:")
            for warning in validation['warnings']:
                print(f"   - {warning}")
                
    # Overall status
    print(f"\n📊 Overall Status:")
    all_good = (github_validation['git_repo'] and 
                github_validation['repo_detected'] and 
                git_clean)
    
    if all_good:
        print("✅ Ready for releases!")
    else:
        print("⚠️  Some issues detected - check above for details")

if __name__ == "__main__":
    main()
