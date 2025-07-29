"""
Database operations with Alembic migration support.
"""
import aiosqlite
import os
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.core.alembic_integration import safe_database_startup_alembic


def get_db_path() -> str:
    """Get the database file path.""" 
    # Extract path from DATABASE_URL
    db_url = settings.database.url
    if db_url.startswith("sqlite:///"):
        db_path = db_url[10:]  # Remove "sqlite:///" prefix
        
        # Create directory if it doesn't exist (except for in-memory)
        if db_path != ":memory:":
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
        
        return db_path
    else:
        # Default fallback
        return "./links.db"


async def init_db() -> None:
    """Initialize the database with Alembic migration support and fallback."""
    db_path = get_db_path()
    
    # Try Alembic first
    try:
        success = safe_database_startup_alembic(f"sqlite:///{db_path}")
        if success:
            print("✅ Alembic database initialization successful")
        else:
            raise Exception("Alembic initialization returned False")
    except Exception as e:
        print(f"⚠️ Alembic failed ({e}), using fallback database initialization...")
        
        # Fallback to simple database creation
        await _create_database_fallback(db_path)
        print("✅ Fallback database initialization successful")
    
    # Ensure database optimizations are applied
    async with aiosqlite.connect(db_path) as db:
        await _ensure_performance_optimizations(db)
        await db.commit()


async def _create_database_fallback(db_path: str) -> None:
    """Create database with basic schema as fallback when Alembic fails."""
    import sqlite3
    
    # Ensure data directory exists
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    # Create database with simple schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create tables with the same schema as Alembic migration
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id TEXT PRIMARY KEY,
            original_url TEXT NOT NULL,
            short_code TEXT UNIQUE NOT NULL,
            description TEXT,
            click_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT NOT NULL,
            created_by_name TEXT NOT NULL,
            tenant_id TEXT NOT NULL
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link_id TEXT NOT NULL,
            clicked_at TEXT DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (link_id) REFERENCES links (id) ON DELETE CASCADE
        )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_links_short_code ON links(short_code)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_links_tenant_id ON links(tenant_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_clicks_link_id ON clicks(link_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_clicks_clicked_at ON clicks(clicked_at)')
        
        # Create a simple version tracking table to indicate this was created by fallback
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS _database_info (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Insert version info
        cursor.execute('''
        INSERT OR REPLACE INTO _database_info (key, value) 
        VALUES ('schema_version', 'fallback_v1.0')
        ''')
        
        cursor.execute('''
        INSERT OR REPLACE INTO _database_info (key, value) 
        VALUES ('created_by', 'fallback_initialization')
        ''')
        
        conn.commit()
        print("📊 Database schema created successfully with fallback method")
        
    except Exception as schema_error:
        print(f"❌ Failed to create database schema: {schema_error}")
        raise
    finally:
        conn.close()


async def _ensure_performance_optimizations(db: aiosqlite.Connection) -> None:
    """Ensure database has performance optimizations."""
    # Enable WAL mode for better concurrency
    await db.execute("PRAGMA journal_mode=WAL")
    
    # Enable foreign key constraints  
    await db.execute("PRAGMA foreign_keys=ON")
    
    # Optimize SQLite settings
    await db.execute("PRAGMA synchronous=NORMAL")
    await db.execute("PRAGMA cache_size=10000")
    await db.execute("PRAGMA temp_store=memory")


class DatabaseManager:
    """Database operations manager using Alembic-managed schema."""

    @staticmethod
    async def get_link_by_short_code(short_code: str) -> Optional[Dict[str, Any]]:
        """Get a link by its short code (case-insensitive)."""
        async with aiosqlite.connect(get_db_path()) as db:
            # Try exact match first (for backward compatibility)
            cursor = await db.execute("""
                SELECT * FROM links WHERE short_code = ?
            """, (short_code,))
            
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            
            # If no exact match, try case-insensitive match
            cursor = await db.execute("""
                SELECT * FROM links WHERE LOWER(short_code) = LOWER(?)
            """, (short_code,))
            
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            
            return None

    @staticmethod
    async def get_link_by_id(link_id: str) -> Optional[Dict[str, Any]]:
        """Get a link by its ID."""
        async with aiosqlite.connect(get_db_path()) as db:
            cursor = await db.execute("""
                SELECT * FROM links WHERE id = ?
            """, (link_id,))
            
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None

    @staticmethod
    async def get_links_by_tenant(tenant_id: str) -> List[Dict[str, Any]]:
        """Get all links for a tenant."""
        async with aiosqlite.connect(get_db_path()) as db:
            cursor = await db.execute("""
                SELECT * FROM links WHERE tenant_id = ? ORDER BY created_at DESC
            """, (tenant_id,))
            
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    @staticmethod
    async def create_link(
        link_id: str,
        original_url: str,
        short_code: str,
        description: Optional[str],
        created_by: str,
        created_by_name: str,
        tenant_id: str
    ) -> str:
        """Create a new link."""
        async with aiosqlite.connect(get_db_path()) as db:
            await db.execute("""
                INSERT INTO links (id, original_url, short_code, description, click_count, created_at, created_by, created_by_name, tenant_id)
                VALUES (?, ?, ?, ?, 0, datetime('now'), ?, ?, ?)
            """, (link_id, original_url, short_code, description, created_by, created_by_name, tenant_id))
            await db.commit()
            return link_id

    @staticmethod
    async def update_link(link_id: str, description: Optional[str]) -> Optional[Dict[str, Any]]:
        """Update a link's description."""
        async with aiosqlite.connect(get_db_path()) as db:
            await db.execute("""
                UPDATE links SET description = ? WHERE id = ?
            """, (description, link_id))
            await db.commit()
            
            # Return updated link
            cursor = await db.execute("""
                SELECT * FROM links WHERE id = ?
            """, (link_id,))
            
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None

    @staticmethod
    async def delete_link(link_id: str) -> bool:
        """Delete a link and its associated clicks."""
        async with aiosqlite.connect(get_db_path()) as db:
            # Delete the link (clicks will be deleted due to CASCADE)
            cursor = await db.execute("""
                DELETE FROM links WHERE id = ?
            """, (link_id,))
            await db.commit()
            return cursor.rowcount > 0

    @staticmethod
    async def increment_click_count(link_id: str, ip_address: str, user_agent: str) -> None:
        """Increment click count and record click details."""
        async with aiosqlite.connect(get_db_path()) as db:
            # Increment click count
            await db.execute("""
                UPDATE links SET click_count = click_count + 1 WHERE id = ?
            """, (link_id,))
            
            # Record click details
            await db.execute("""
                INSERT INTO clicks (link_id, clicked_at, ip_address, user_agent)
                VALUES (?, datetime('now'), ?, ?)
            """, (link_id, ip_address, user_agent))
            
            await db.commit()

    @staticmethod
    async def get_link_analytics(link_id: str) -> Dict[str, Any]:
        """Get analytics for a specific link."""
        async with aiosqlite.connect(get_db_path()) as db:
            # Get link details
            cursor = await db.execute("""
                SELECT * FROM links WHERE id = ?
            """, (link_id,))
            
            row = await cursor.fetchone()
            if not row:
                return {}
            
            columns = [description[0] for description in cursor.description]
            link_data = dict(zip(columns, row))
            
            # Get total clicks
            cursor = await db.execute("""
                SELECT COUNT(*) FROM clicks WHERE link_id = ?
            """, (link_id,))
            result = await cursor.fetchone()
            total_clicks = result[0] if result else 0
            
            # Get clicks today
            cursor = await db.execute("""
                SELECT COUNT(*) FROM clicks 
                WHERE link_id = ? AND DATE(clicked_at) = DATE('now')
            """, (link_id,))
            result = await cursor.fetchone()
            clicks_today = result[0] if result else 0
            
            # Get clicks this week
            cursor = await db.execute("""
                SELECT COUNT(*) FROM clicks 
                WHERE link_id = ? AND DATE(clicked_at) >= DATE('now', '-7 days')
            """, (link_id,))
            result = await cursor.fetchone()
            clicks_this_week = result[0] if result else 0
            
            # Get clicks this month
            cursor = await db.execute("""
                SELECT COUNT(*) FROM clicks 
                WHERE link_id = ? AND DATE(clicked_at) >= DATE('now', 'start of month')
            """, (link_id,))
            result = await cursor.fetchone()
            clicks_this_month = result[0] if result else 0
            
            # Get recent clicks
            cursor = await db.execute("""
                SELECT id, clicked_at, ip_address, user_agent
                FROM clicks 
                WHERE link_id = ? 
                ORDER BY clicked_at DESC
                LIMIT 10
            """, (link_id,))
            
            recent_clicks = []
            for click_row in await cursor.fetchall():
                recent_clicks.append({
                    "id": str(click_row[0]),
                    "link_id": link_id,
                    "clicked_at": click_row[1],
                    "ip_address": click_row[2],
                    "user_agent": click_row[3]
                })
            
            return {
                "total_clicks": total_clicks,
                "clicks_today": clicks_today,
                "clicks_this_week": clicks_this_week,
                "clicks_this_month": clicks_this_month,
                "recent_clicks": recent_clicks
            }
