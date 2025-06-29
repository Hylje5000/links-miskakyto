#!/usr/bin/env python3
"""
Database migration script to ensure all required columns exist.
This handles cases where the production database might be missing the created_by_name column.
"""

import asyncio
import aiosqlite
import os
from app.core.database import get_db_path
from app.core.config import settings


async def check_and_migrate_database():
    """Check if database needs migration and apply if needed."""
    db_path = get_db_path()
    
    print(f"Checking database at: {db_path}")
    
    if not os.path.exists(db_path):
        print("Database does not exist. Running full initialization...")
        from app.core.database import init_db
        await init_db()
        print("Database initialized successfully")
        return
    
    async with aiosqlite.connect(db_path) as db:
        # Check if links table exists
        cursor = await db.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='links'
        """)
        table_exists = await cursor.fetchone()
        
        if not table_exists:
            print("Links table does not exist. Creating...")
            from app.core.database import init_db
            await init_db()
            print("Database initialized successfully")
            return
        
        # Check current schema
        cursor = await db.execute("PRAGMA table_info(links)")
        columns = await cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Current columns: {column_names}")
        
        # Check if created_by_name column exists
        if 'created_by_name' not in column_names:
            print("Missing created_by_name column. Adding...")
            
            try:
                # Add the column with a default value
                await db.execute("""
                    ALTER TABLE links 
                    ADD COLUMN created_by_name TEXT NOT NULL DEFAULT 'Unknown User'
                """)
                await db.commit()
                print("Successfully added created_by_name column")
            except Exception as e:
                print(f"Error adding column: {e}")
                print("This might be expected if the column already exists")
        
        # Check if tenant_id column exists (another important column)
        if 'tenant_id' not in column_names:
            print("Missing tenant_id column. Adding...")
            
            try:
                await db.execute("""
                    ALTER TABLE links 
                    ADD COLUMN tenant_id TEXT NOT NULL DEFAULT ''
                """)
                await db.commit()
                print("Successfully added tenant_id column")
            except Exception as e:
                print(f"Error adding tenant_id column: {e}")
        
        # Verify final schema
        cursor = await db.execute("PRAGMA table_info(links)")
        final_columns = await cursor.fetchall()
        final_column_names = [col[1] for col in final_columns]
        
        print(f"Final columns: {final_column_names}")
        
        # Check if we have any data
        cursor = await db.execute("SELECT COUNT(*) FROM links")
        count_result = await cursor.fetchone()
        count = count_result[0] if count_result else 0
        print(f"Total links in database: {count}")
        
        # Sample a few records to check data integrity
        if count > 0:
            cursor = await db.execute("SELECT id, short_code, created_by_name, tenant_id FROM links LIMIT 3")
            samples = await cursor.fetchall()
            print("Sample records:")
            for sample in samples:
                print(f"  ID: {sample[0]}, Short: {sample[1]}, Created by: {sample[2]}, Tenant: {sample[3]}")


if __name__ == "__main__":
    asyncio.run(check_and_migrate_database())
