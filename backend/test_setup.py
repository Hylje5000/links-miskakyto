#!/usr/bin/env python3
"""
Simple test script to verify the backend setup
"""

import asyncio
import aiosqlite
from main import init_db

async def test_setup():
    try:
        # Test database initialization
        await init_db()
        print("✅ Database initialized successfully")
        
        # Test database connection
        async with aiosqlite.connect("links.db") as db:
            cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = await cursor.fetchall()
            print(f"✅ Database tables created: {[table[0] for table in tables]}")
        
        print("✅ Backend setup verification complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error during setup verification: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_setup())
