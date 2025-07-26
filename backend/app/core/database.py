"""
Database operations and schema management.
"""
import aiosqlite
import os
from typing import Dict, Any, List, Optional
from app.core.config import settings


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
    """Initialize the database with required tables and handle schema migrations."""
    db_path = get_db_path()
    
    async with aiosqlite.connect(db_path) as db:
        # Check if we need to recreate the tables due to schema changes
        needs_recreation = await _check_schema_compatibility(db)
        
        if needs_recreation:
            print("🔄 Detected schema incompatibility. Recreating database tables...")
            await _recreate_tables(db)
        else:
            await _create_tables_if_not_exist(db)
        
        # Create indices for better performance
        await _create_indices(db)
        
        await db.commit()
        print("✅ Database initialization complete")


async def _check_schema_compatibility(db: aiosqlite.Connection) -> bool:
    """Check if the current schema is compatible with the expected schema."""
    try:
        # Check if links table exists
        cursor = await db.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='links'
        """)
        links_table = await cursor.fetchone()
        
        if not links_table:
            # Table doesn't exist, no recreation needed
            return False
        
        # Check if the table has all required columns
        cursor = await db.execute("PRAGMA table_info(links)")
        columns = await cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        required_columns = [
            'id', 'original_url', 'short_code', 'description', 
            'click_count', 'created_at', 'created_by', 
            'created_by_name', 'tenant_id'
        ]
        
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"⚠️  Missing columns in links table: {missing_columns}")
            return True
        
        return False
        
    except Exception as e:
        print(f"⚠️  Error checking schema compatibility: {e}")
        return True


async def _recreate_tables(db: aiosqlite.Connection) -> None:
    """Recreate all tables with the correct schema."""
    print("🗑️  Dropping existing tables...")
    
    # Drop existing tables
    await db.execute("DROP TABLE IF EXISTS clicks")
    await db.execute("DROP TABLE IF EXISTS links")
    
    print("🔨 Creating new tables with correct schema...")
    await _create_tables_if_not_exist(db)


async def _create_tables_if_not_exist(db: aiosqlite.Connection) -> None:
    """Create tables if they don't exist."""
    # Create links table with all required columns
    await db.execute("""
        CREATE TABLE IF NOT EXISTS links (
            id TEXT PRIMARY KEY,
            original_url TEXT NOT NULL,
            short_code TEXT UNIQUE NOT NULL,
            description TEXT,
            click_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT NOT NULL,
            created_by_name TEXT NOT NULL,
            tenant_id TEXT NOT NULL
        )
    """)
    
    # Create clicks table for analytics
    await db.execute("""
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link_id TEXT NOT NULL,
            clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (link_id) REFERENCES links (id)
        )
    """)


async def _create_indices(db: aiosqlite.Connection) -> None:
    """Create performance indices."""
    await db.execute("CREATE INDEX IF NOT EXISTS idx_links_short_code ON links(short_code)")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_links_tenant_id ON links(tenant_id)")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_clicks_link_id ON clicks(link_id)")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_clicks_clicked_at ON clicks(clicked_at)")


class DatabaseManager:
    """Database manager for common operations."""
    
    @staticmethod
    async def get_link_by_short_code(short_code: str) -> Optional[Dict[str, Any]]:
        """Get a link by its short code."""
        async with aiosqlite.connect(get_db_path()) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM links WHERE short_code = ?", 
                (short_code,)
            )
            result = await cursor.fetchone()
            return dict(result) if result else None
    
    @staticmethod
    async def get_link_by_id(link_id: str) -> Optional[Dict[str, Any]]:
        """Get a link by its ID."""
        async with aiosqlite.connect(get_db_path()) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM links WHERE id = ?", 
                (link_id,)
            )
            result = await cursor.fetchone()
            return dict(result) if result else None
    
    @staticmethod
    async def get_links_by_tenant(tenant_id: str) -> List[Dict[str, Any]]:
        """Get all links for a tenant."""
        async with aiosqlite.connect(get_db_path()) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM links WHERE tenant_id = ? ORDER BY created_at DESC",
                (tenant_id,)
            )
            results = await cursor.fetchall()
            return [dict(row) for row in results]
    
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
                INSERT INTO links (id, original_url, short_code, description, created_by, created_by_name, tenant_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (link_id, original_url, short_code, description, created_by, created_by_name, tenant_id))
            await db.commit()
            return link_id
    
    @staticmethod
    async def update_link(link_id: str, description: Optional[str]) -> Optional[Dict[str, Any]]:
        """Update a link's description."""
        async with aiosqlite.connect(get_db_path()) as db:
            db.row_factory = aiosqlite.Row
            await db.execute(
                "UPDATE links SET description = ? WHERE id = ?",
                (description, link_id)
            )
            await db.commit()
            
            # Return updated link
            cursor = await db.execute(
                "SELECT * FROM links WHERE id = ?",
                (link_id,)
            )
            result = await cursor.fetchone()
            return dict(result) if result else None
    
    @staticmethod
    async def delete_link(link_id: str) -> bool:
        """Delete a link and its associated clicks."""
        async with aiosqlite.connect(get_db_path()) as db:
            # Delete associated clicks first
            await db.execute("DELETE FROM clicks WHERE link_id = ?", (link_id,))
            
            # Delete the link
            cursor = await db.execute("DELETE FROM links WHERE id = ?", (link_id,))
            await db.commit()
            
            return cursor.rowcount > 0
    
    @staticmethod
    async def increment_click_count(link_id: str, ip_address: str, user_agent: str) -> None:
        """Increment click count and record analytics."""
        async with aiosqlite.connect(get_db_path()) as db:
            # Increment click count
            await db.execute(
                "UPDATE links SET click_count = click_count + 1 WHERE id = ?",
                (link_id,)
            )
            
            # Record click for analytics
            await db.execute("""
                INSERT INTO clicks (link_id, ip_address, user_agent)
                VALUES (?, ?, ?)
            """, (link_id, ip_address, user_agent))
            
            await db.commit()
    
    @staticmethod
    async def get_link_analytics(link_id: str) -> Dict[str, Any]:
        """Get analytics for a specific link."""
        async with aiosqlite.connect(get_db_path()) as db:
            db.row_factory = aiosqlite.Row
            
            # Get total clicks
            cursor = await db.execute(
                "SELECT click_count FROM links WHERE id = ?",
                (link_id,)
            )
            link_data = await cursor.fetchone()
            total_clicks = link_data["click_count"] if link_data else 0
            
            # Get clicks today
            cursor = await db.execute("""
                SELECT COUNT(*) as count FROM clicks 
                WHERE link_id = ? AND DATE(clicked_at) = DATE('now')
            """, (link_id,))
            today_result = await cursor.fetchone()
            clicks_today = today_result["count"] if today_result else 0
            
            # Get clicks this week
            cursor = await db.execute("""
                SELECT COUNT(*) as count FROM clicks 
                WHERE link_id = ? AND DATE(clicked_at) >= DATE('now', '-7 days')
            """, (link_id,))
            week_result = await cursor.fetchone()
            clicks_this_week = week_result["count"] if week_result else 0
            
            # Get clicks this month
            cursor = await db.execute("""
                SELECT COUNT(*) as count FROM clicks 
                WHERE link_id = ? AND DATE(clicked_at) >= DATE('now', '-30 days')
            """, (link_id,))
            month_result = await cursor.fetchone()
            clicks_this_month = month_result["count"] if month_result else 0
            
            # Get recent clicks
            cursor = await db.execute("""
                SELECT id, link_id, clicked_at, ip_address, user_agent FROM clicks 
                WHERE link_id = ? 
                ORDER BY clicked_at DESC 
                LIMIT 10
            """, (link_id,))
            recent_clicks = [dict(row) for row in await cursor.fetchall()]
            
            return {
                "total_clicks": total_clicks,
                "clicks_today": clicks_today,
                "clicks_this_week": clicks_this_week,
                "clicks_this_month": clicks_this_month,
                "recent_clicks": recent_clicks
            }
