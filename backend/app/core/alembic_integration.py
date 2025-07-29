"""
Alembic database migration integration.
Replaces our custom migration system with industry-standard Alembic.
"""
import os
import logging
from typing import Optional
from pathlib import Path
from alembic.config import Config
from alembic import command
from alembic.runtime import migration
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)


class AlembicManager:
    """Manages database migrations using Alembic."""
    
    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or "sqlite:///./links.db"
        
        # Get the backend directory (where alembic.ini is located)
        current_dir = Path(__file__).parent.parent.parent  # Go up from app/core/ to backend/
        alembic_ini_path = current_dir / "alembic.ini"
        
        # Check if alembic.ini exists, if not, we'll use fallback
        if not alembic_ini_path.exists():
            logger.warning(f"⚠️ Alembic configuration not found at {alembic_ini_path}")
            logger.warning("This will trigger fallback database initialization")
            raise FileNotFoundError(f"Alembic configuration not found at {alembic_ini_path}")
        
        try:
            self.alembic_cfg = Config(str(alembic_ini_path))
            # Override the database URL if provided
            if db_url:
                self.alembic_cfg.set_main_option("sqlalchemy.url", db_url)
        except Exception as e:
            logger.error(f"❌ Failed to load Alembic configuration: {e}")
            raise
    
    def upgrade_to_head(self) -> bool:
        """
        Apply all pending migrations to bring database up to latest version.
        Returns True if successful, False otherwise.
        """
        try:
            logger.info("🔄 Running Alembic migrations...")
            command.upgrade(self.alembic_cfg, "head")
            logger.info("✅ All migrations applied successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False
    
    def downgrade_by_one(self) -> bool:
        """
        Rollback one migration.
        Returns True if successful, False otherwise.
        """
        try:
            logger.info("🔄 Rolling back one migration...")
            command.downgrade(self.alembic_cfg, "-1")
            logger.info("✅ Rollback completed successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            return False
    
    def get_current_revision(self) -> str:
        """Get the current database revision."""
        try:
            engine = create_engine(self.db_url)
            with engine.connect() as connection:
                context = migration.MigrationContext.configure(connection)
                current_rev = context.get_current_revision()
                return current_rev or "No migrations applied"
        except Exception as e:
            logger.error(f"Failed to get current revision: {e}")
            return "Unknown"
    
    def get_head_revision(self) -> str:
        """Get the latest available revision."""
        try:
            script_dir = ScriptDirectory.from_config(self.alembic_cfg)
            head = script_dir.get_current_head()
            return head or "No migrations found"
        except Exception as e:
            logger.error(f"Failed to get head revision: {e}")
            return "Unknown"
    
    def is_up_to_date(self) -> bool:
        """Check if database is up to date with latest migrations."""
        current = self.get_current_revision()
        head = self.get_head_revision()
        return current == head and current != "Unknown"
    
    def create_migration(self, message: str, autogenerate: bool = True) -> bool:
        """
        Create a new migration file.
        
        Args:
            message: Description of the migration
            autogenerate: Whether to auto-generate from model changes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if autogenerate:
                logger.info(f"🔄 Creating auto-generated migration: {message}")
                command.revision(self.alembic_cfg, message=message, autogenerate=True)
            else:
                logger.info(f"🔄 Creating empty migration: {message}")
                command.revision(self.alembic_cfg, message=message)
            
            logger.info("✅ Migration file created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create migration: {e}")
            return False
    
    def show_history(self):
        """Show migration history."""
        try:
            command.history(self.alembic_cfg)
        except Exception as e:
            logger.error(f"Failed to show history: {e}")
    
    def validate_database(self) -> dict:
        """
        Validate database state and return status information.
        
        Returns:
            Dictionary with validation results
        """
        status = {
            "valid": True,
            "current_revision": self.get_current_revision(),
            "head_revision": self.get_head_revision(),
            "up_to_date": self.is_up_to_date(),
            "issues": []
        }
        
        if status["current_revision"] == "Unknown":
            status["valid"] = False
            status["issues"].append("Cannot determine current database revision")
        
        if status["head_revision"] == "Unknown":
            status["valid"] = False
            status["issues"].append("Cannot determine latest migration version")
        
        if not status["up_to_date"] and status["valid"]:
            status["issues"].append("Database is not up to date with latest migrations")
        
        return status


def safe_database_startup_alembic(db_url: Optional[str] = None) -> bool:
    """
    Initialize database using Alembic migrations.
    Replaces our custom migration system.
    
    Args:
        db_url: Database URL (defaults to sqlite:///./links.db)
        
    Returns:
        True if successful, False if critical issues found
    """
    logger.info("🔧 Starting Alembic-based database initialization...")
    
    try:
        # Create Alembic manager
        alembic_manager = AlembicManager(db_url)
        
        # Validate current state
        status = alembic_manager.validate_database()
        
        if not status["up_to_date"]:
            logger.info("🔄 Database needs migration updates...")
            
            # Create backup if database file exists
            if db_url and "sqlite:///" in db_url:
                db_file = db_url.replace("sqlite:///", "")
                if os.path.exists(db_file):
                    backup_file = f"{db_file}.backup_{int(__import__('time').time())}"
                    try:
                        import shutil
                        shutil.copy2(db_file, backup_file)
                        logger.info(f"📦 Database backup created: {backup_file}")
                    except Exception as e:
                        logger.warning(f"⚠️  Could not create backup: {e}")
            
            # Apply migrations
            success = alembic_manager.upgrade_to_head()
            if not success:
                logger.error("❌ Migration upgrade failed")
                return False
        
        # Final validation
        final_status = alembic_manager.validate_database()
        
        if final_status["valid"] and final_status["up_to_date"]:
            logger.info("✅ Database successfully initialized with Alembic")
            logger.info(f"   Current revision: {final_status['current_revision']}")
            return True
        else:
            logger.error("❌ Database validation failed after migrations")
            for issue in final_status["issues"]:
                logger.error(f"   - {issue}")
            return False
            
    except FileNotFoundError as e:
        logger.error(f"❌ Alembic configuration missing: {e}")
        logger.info("This will trigger fallback database initialization")
        return False
    except Exception as e:
        logger.error(f"❌ Alembic database initialization failed: {e}")
        logger.info("This will trigger fallback database initialization")
        import traceback
        logger.debug(f"Full traceback: {traceback.format_exc()}")
        return False


# Global manager instance
_alembic_manager = None

def get_alembic_manager(db_url: Optional[str] = None) -> AlembicManager:
    """Get singleton Alembic manager instance."""
    global _alembic_manager
    if _alembic_manager is None:
        _alembic_manager = AlembicManager(db_url)
    return _alembic_manager
