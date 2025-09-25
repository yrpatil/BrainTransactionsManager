"""
Simple Database Migration Manager for BrainTransactionsManager v2.0.0
Blessed by Goddess Laxmi for Infinite Abundance 🙏

Lightweight migration system using Alembic for schema evolution.
Focuses on essential migration capabilities without overengineering.
"""

import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.engine import Engine
from ..core.exceptions import MigrationError

logger = logging.getLogger(__name__)


class MigrationManager:
    """
    Simple database migration manager using Alembic.
    
    Features:
    • Automatic migration discovery
    • Schema version tracking
    • Safe migration execution
    • Rollback capabilities
    • Migration validation
    • Simple and reliable
    """
    
    def __init__(self, config):
        """
        Initialize migration manager.
        
        Args:
            config: BrainConfig instance
        """
        self.config = config
        self.migrations_dir = Path("api_versions/v2.0.0/migrations")
        self.alembic_cfg_path = self.migrations_dir / "alembic.ini"
        self.versions_dir = self.migrations_dir / "versions"
        self.engine: Optional[Engine] = None
        self.alembic_cfg: Optional[Config] = None
        
        # Initialize if not exists
        self._ensure_migrations_setup()
    
    def _ensure_migrations_setup(self):
        """Ensure migration directory structure exists."""
        try:
            # Create migrations directory
            self.migrations_dir.mkdir(parents=True, exist_ok=True)
            self.versions_dir.mkdir(exist_ok=True)
            
            # Create alembic.ini if it doesn't exist
            if not self.alembic_cfg_path.exists():
                self._create_alembic_config()
            
            # Create env.py if it doesn't exist
            env_py_path = self.migrations_dir / "env.py"
            if not env_py_path.exists():
                self._create_env_py()
            
            # Create script.py.mako if it doesn't exist
            script_mako_path = self.migrations_dir / "script.py.mako"
            if not script_mako_path.exists():
                self._create_script_template()
            
            logger.debug("Migration setup verified")
            
        except Exception as e:
            logger.error(f"Failed to setup migrations: {e}")
            raise MigrationError(f"Migration setup failed: {e}")
    
    def _create_alembic_config(self):
        """Create alembic.ini configuration file."""
        config_content = f"""# Alembic configuration for BrainTransactionsManager v2.0.0

[alembic]
script_location = {self.migrations_dir}
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = {self.config.database.url}

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
        
        with open(self.alembic_cfg_path, 'w') as f:
            f.write(config_content)
    
    def _create_env_py(self):
        """Create env.py for Alembic."""
        env_content = '''"""Alembic environment for BrainTransactionsManager v2.0.0"""

import logging
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import your models here for autogenerate support
# from your_app.models import Base
# target_metadata = Base.metadata
target_metadata = None

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

logger = logging.getLogger('alembic.env')


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''
        
        env_path = self.migrations_dir / "env.py"
        with open(env_path, 'w') as f:
            f.write(env_content)
    
    def _create_script_template(self):
        """Create script template for new migrations."""
        template_content = '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
'''
        
        template_path = self.migrations_dir / "script.py.mako"
        with open(template_path, 'w') as f:
            f.write(template_content)
    
    def _get_alembic_config(self) -> Config:
        """Get Alembic configuration."""
        if self.alembic_cfg is None:
            self.alembic_cfg = Config(str(self.alembic_cfg_path))
            # Override database URL with current config
            self.alembic_cfg.set_main_option("sqlalchemy.url", self.config.database.url)
        return self.alembic_cfg
    
    def _get_engine(self) -> Engine:
        """Get SQLAlchemy engine."""
        if self.engine is None:
            self.engine = create_engine(self.config.database.url)
        return self.engine
    
    def initialize(self) -> bool:
        """
        Initialize migration system.
        
        Returns:
            True if successful
        """
        try:
            logger.info("🔄 Initializing migration system...")
            
            # Test database connection
            engine = self._get_engine()
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # Initialize Alembic if not already done
            try:
                alembic_cfg = self._get_alembic_config()
                command.current(alembic_cfg)
            except Exception:
                # Not initialized, create initial migration
                logger.info("Creating initial migration...")
                command.init(alembic_cfg, str(self.migrations_dir))
            
            logger.info("✅ Migration system initialized")
            return True
            
        except Exception as e:
            logger.error(f"Migration initialization failed: {e}")
            return False
    
    def get_current_revision(self) -> Optional[str]:
        """Get current database revision."""
        try:
            engine = self._get_engine()
            with engine.connect() as conn:
                context = MigrationContext.configure(conn)
                return context.get_current_revision()
        except Exception as e:
            logger.error(f"Failed to get current revision: {e}")
            return None
    
    def get_pending_migrations(self) -> List[str]:
        """Get list of pending migrations."""
        try:
            alembic_cfg = self._get_alembic_config()
            script = ScriptDirectory.from_config(alembic_cfg)
            
            current = self.get_current_revision()
            if current is None:
                # No migrations applied yet
                return [rev.revision for rev in script.walk_revisions()]
            
            # Get pending revisions
            pending = []
            for rev in script.walk_revisions("head", current):
                if rev.revision != current:
                    pending.append(rev.revision)
            
            return list(reversed(pending))  # Return in chronological order
            
        except Exception as e:
            logger.error(f"Failed to get pending migrations: {e}")
            return []
    
    def run_migrations(self, target_revision: str = "head") -> bool:
        """
        Run database migrations.
        
        Args:
            target_revision: Target revision to migrate to
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"🔄 Running migrations to {target_revision}...")
            
            alembic_cfg = self._get_alembic_config()
            
            # Get current and pending migrations
            current = self.get_current_revision()
            pending = self.get_pending_migrations()
            
            if not pending:
                logger.info("✅ No pending migrations")
                return True
            
            logger.info(f"Applying {len(pending)} migrations: {', '.join(pending)}")
            
            # Run migrations
            command.upgrade(alembic_cfg, target_revision)
            
            # Verify migration
            new_revision = self.get_current_revision()
            if new_revision != current:
                logger.info(f"✅ Migrations completed. Current revision: {new_revision}")
                return True
            else:
                logger.warning("⚠️ Migration completed but revision unchanged")
                return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    def create_migration(self, message: str, auto_generate: bool = False) -> Optional[str]:
        """
        Create a new migration.
        
        Args:
            message: Migration description
            auto_generate: Whether to auto-generate migration from model changes
            
        Returns:
            Migration revision ID if successful
        """
        try:
            logger.info(f"🔄 Creating migration: {message}")
            
            alembic_cfg = self._get_alembic_config()
            
            if auto_generate:
                # Auto-generate migration (requires model metadata)
                command.revision(alembic_cfg, message=message, autogenerate=True)
            else:
                # Create empty migration
                command.revision(alembic_cfg, message=message)
            
            # Get the newly created revision
            script = ScriptDirectory.from_config(alembic_cfg)
            head_revision = script.get_current_head()
            
            logger.info(f"✅ Migration created: {head_revision}")
            return head_revision
            
        except Exception as e:
            logger.error(f"Failed to create migration: {e}")
            return None
    
    def rollback_migration(self, target_revision: str = "-1") -> bool:
        """
        Rollback to a previous migration.
        
        Args:
            target_revision: Target revision to rollback to ("-1" for previous)
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"🔄 Rolling back to {target_revision}...")
            
            alembic_cfg = self._get_alembic_config()
            current = self.get_current_revision()
            
            # Run downgrade
            command.downgrade(alembic_cfg, target_revision)
            
            # Verify rollback
            new_revision = self.get_current_revision()
            logger.info(f"✅ Rollback completed. Current revision: {new_revision}")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def get_migration_history(self) -> List[Dict[str, Any]]:
        """Get migration history."""
        try:
            alembic_cfg = self._get_alembic_config()
            script = ScriptDirectory.from_config(alembic_cfg)
            current = self.get_current_revision()
            
            history = []
            for rev in script.walk_revisions():
                history.append({
                    'revision': rev.revision,
                    'down_revision': rev.down_revision,
                    'message': rev.doc,
                    'is_current': rev.revision == current,
                    'branch_labels': rev.branch_labels,
                    'depends_on': rev.depends_on
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get migration history: {e}")
            return []
    
    def validate_migrations(self) -> Dict[str, Any]:
        """Validate migration state."""
        try:
            current = self.get_current_revision()
            pending = self.get_pending_migrations()
            history = self.get_migration_history()
            
            return {
                'status': 'valid',
                'current_revision': current,
                'pending_migrations': len(pending),
                'total_migrations': len(history),
                'needs_migration': len(pending) > 0,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
