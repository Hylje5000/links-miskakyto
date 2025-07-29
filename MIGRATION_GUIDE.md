# Database Migration System - REPLACED WITH ALEMBIC

**⚠️ DEPRECATED: This guide describes our old custom migration system. We have now migrated to Alembic for database migrations.**

**For current migration practices, see [ALEMBIC_INTEGRATION.md](ALEMBIC_INTEGRATION.md)**

---

## Migration System Status: REPLACED ✅

This project originally used a custom database migration system, but we have successfully migrated to **Alembic**, the industry-standard migration tool for SQLAlchemy-based projects.

### What Changed

- **Old System**: Custom migration classes with version tracking
- **New System**: Alembic with SQLAlchemy models
- **Migration**: Completed successfully, all data preserved
- **Benefits**: Industry-standard tooling, better reliability, comprehensive features

### Current Migration Commands

Instead of our custom system, use these Alembic commands:

```bash
# Generate a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Check current version
alembic current

# View migration history
alembic history
```

### Database Schema

The database now uses Alembic-managed SQLAlchemy models:
- **Links table**: String-based IDs (using shortuuid)
- **Clicks table**: Integer IDs with foreign key to links
- **Alembic version table**: Tracks migration state

### Files Involved

- `backend/alembic/`: Alembic configuration and migrations
- `backend/app/models/database_models.py`: SQLAlchemy models
- `backend/app/core/alembic_integration.py`: Alembic manager
- `backend/app/core/database.py`: Database operations

---

## Historical Custom Migration System (DEPRECATED)

The following documentation is preserved for historical reference only.

**This system is no longer used and has been replaced by Alembic.**

## Original Key Features

✅ **Automatic Schema Migration**: Database schema is automatically updated on startup
✅ **Backward Compatibility**: Old data is preserved during schema changes  
✅ **Rollback Support**: Migrations can be rolled back if needed
✅ **Transaction Safety**: Each migration runs in a transaction - all or nothing
✅ **Backup Creation**: Automatic backups before applying migrations
✅ **Compatibility Checking**: Validates schema before and after migrations

## How It Prevents Breakdowns

### 1. **Safe Startup Process**
When the backend starts, it:
- Creates a backup of the existing database
- Checks current schema compatibility 
- Applies any pending migrations
- Verifies final schema is correct
- Only starts if everything is compatible

### 2. **Migration Tracking**
- Each migration has a version number and description
- Applied migrations are tracked in `schema_migrations` table
- Prevents duplicate application of migrations
- Checksums detect if migration SQL has changed

### 3. **Graceful Schema Evolution**
Current migrations include:
- **Migration 001**: Initial database schema (links, clicks tables)
- **Migration 002**: Enhanced analytics fields (if needed in future)

## Adding New Migrations

To add a new migration (e.g., adding a new column):

```python
# In app/core/migrations.py, add to create_migration_system():

manager.add_migration(DatabaseMigration(
    version="003",
    description="Add user preferences table",
    up_sql="""
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            theme TEXT DEFAULT 'light',
            notifications BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_user_prefs_user ON user_preferences(user_id);
    """,
    down_sql="""
        DROP TABLE IF EXISTS user_preferences;
    """
))
```

## Example Scenarios

### Scenario 1: Adding a New Column
```python
# Migration 004: Add 'category' to links
up_sql="""
    ALTER TABLE links ADD COLUMN category TEXT DEFAULT 'general';
    CREATE INDEX IF NOT EXISTS idx_links_category ON links(category);
"""
```

### Scenario 2: Creating a New Table
```python  
# Migration 005: Add analytics dashboard
up_sql="""
    CREATE TABLE IF NOT EXISTS dashboards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        config TEXT, -- JSON configuration
        created_by TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""
```

## Production Safety

### Before Deployment:
1. **Test migrations on staging** with production data copy
2. **Backup production database** (automatic, but verify)
3. **Monitor logs** during deployment for migration status

### After Deployment:
1. **Verify application starts successfully**
2. **Check all existing functionality works**
3. **Monitor for any database-related errors**

## Recovery Process

If something goes wrong:

1. **Check logs** for specific migration errors
2. **Use automatic backup** created before migration
3. **Rollback to previous version** if needed
4. **Fix migration SQL** and redeploy

## Best Practices

### ✅ DO:
- Always test migrations on staging first
- Include both `up_sql` and `down_sql` when possible
- Use `IF NOT EXISTS` for table/index creation
- Add appropriate database indexes
- Keep migrations small and focused
- Include descriptive migration descriptions

### ❌ DON'T:
- Modify existing migration SQL after it's been deployed
- Delete data without explicit confirmation
- Create migrations that depend on application code
- Skip testing migrations with real data

## Migration System Status

The system will log migration status on startup:

```
🔧 Starting safe database initialization...
📦 Database backup created: links.db.backup_20250729_130812
🔄 Applying 1 migrations...
✅ Applied migration 001: Create initial links and clicks tables
✅ Database successfully initialized and compatible
```

This ensures that **schema changes never break the production application** and that all data is safely preserved during updates.
