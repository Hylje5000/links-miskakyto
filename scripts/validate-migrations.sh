#!/bin/bash

# Pre-deployment migration validation script
# This script validates that Alembic migrations are safe to run in production

set -e

echo "🔍 Pre-deployment Migration Validation"
echo "===================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${YELLOW}$1${NC}"; }
print_success() { echo -e "${GREEN}$1${NC}"; }
print_info() { echo -e "${BLUE}$1${NC}"; }
print_error() { echo -e "${RED}$1${NC}"; }

# Load environment
if [ -f .env ]; then
    print_info "📋 Loading environment variables from .env"
    set -a
    source .env
    set +a
fi

# Check if we're in the right directory
if [ ! -f "backend/alembic.ini" ]; then
    print_error "❌ Error: Must be run from project root directory"
    print_error "   Expected to find backend/alembic.ini"
    exit 1
fi

print_status "🧪 Validating Alembic configuration..."

# Check Alembic configuration
cd backend

# Verify alembic.ini exists and is properly configured
if [ ! -f "alembic.ini" ]; then
    print_error "❌ alembic.ini not found"
    exit 1
fi

print_success "✅ alembic.ini found"

# Check that migration directory exists
if [ ! -d "alembic/versions" ]; then
    print_error "❌ Migration directory alembic/versions not found"
    exit 1
fi

print_success "✅ Migration directory exists"

# Count migration files
MIGRATION_COUNT=$(find alembic/versions -name "*.py" -not -name "__*" | wc -l)
print_info "📊 Found $MIGRATION_COUNT migration files"

if [ $MIGRATION_COUNT -eq 0 ]; then
    print_error "❌ No migration files found"
    exit 1
fi

# Test Alembic commands work
print_status "🧪 Testing Alembic commands..."

# Create a temporary database for testing
TEST_DB_PATH="/tmp/alembic_test_$(date +%s).db"
export DATABASE_URL="sqlite:///${TEST_DB_PATH}"

# Test migration on clean database
print_info "🔄 Testing migration on clean database..."

# Set test environment variables
export AZURE_TENANT_ID="test-tenant"
export AZURE_CLIENT_ID="test-client"
export ENVIRONMENT="test"

# Detect Python command
PYTHON_CMD="python"

# First check for virtual environment
if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
elif [ -f "../.venv/bin/python" ]; then
    PYTHON_CMD="../.venv/bin/python"
elif [ -f "venv/bin/python" ]; then
    PYTHON_CMD="venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    print_error "❌ No Python interpreter found"
    exit 1
fi

print_info "🐍 Using Python: $PYTHON_CMD"

# Test that Python can import our modules
if ! $PYTHON_CMD -c "import fastapi, alembic, sqlalchemy" 2>/dev/null; then
    print_error "❌ Required Python packages not available with $PYTHON_CMD"
    print_error "   Make sure you're running from the correct directory with a virtual environment"
    exit 1
fi

# Test database initialization (which runs Alembic)
$PYTHON_CMD -c "
import asyncio
import sys
import os
import logging

# Set up logging to capture Alembic output
logging.basicConfig(level=logging.INFO)

async def test_migration():
    try:
        from app.core.database import init_db
        await init_db()
        print('✅ Migration test completed successfully')
        return True
    except Exception as e:
        print(f'❌ Migration test failed: {e}')
        return False

result = asyncio.run(test_migration())
if not result:
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    print_success "✅ Alembic migration test passed"
else
    print_error "❌ Alembic migration test failed"
    rm -f "$TEST_DB_PATH"
    exit 1
fi

# Verify migration created expected tables
print_status "🔍 Validating database schema..."

$PYTHON_CMD -c "
import sqlite3
import sys

db_path = '${TEST_DB_PATH}'
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check for expected tables
    cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")
    tables = [row[0] for row in cursor.fetchall()]
    
    expected_tables = ['links', 'clicks', 'alembic_version']
    missing_tables = [t for t in expected_tables if t not in tables]
    
    if missing_tables:
        print(f'❌ Missing tables: {missing_tables}')
        sys.exit(1)
    
    print(f'✅ All expected tables found: {tables}')
    
    # Check alembic_version table has a revision
    cursor.execute('SELECT version_num FROM alembic_version')
    version = cursor.fetchone()
    if not version:
        print('❌ No migration version recorded')
        sys.exit(1)
    
    print(f'✅ Database at migration version: {version[0]}')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Schema validation failed: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    print_success "✅ Database schema validation passed"
else
    print_error "❌ Database schema validation failed"
    rm -f "$TEST_DB_PATH"
    exit 1
fi

# Test that application can start with the migrated database
print_status "🧪 Testing application startup with migrated database..."

$PYTHON_CMD -c "
import asyncio
import sys
import os

async def test_app_startup():
    try:
        # Test that the application can start with the migrated database
        from app.core.database import DatabaseManager
        
        # Test basic database operations
        links = await DatabaseManager.get_links_by_tenant('test-tenant')
        print(f'✅ Database operations work: {len(links)} links found')
        
        return True
    except Exception as e:
        print(f'❌ Application startup test failed: {e}')
        return False

result = asyncio.run(test_app_startup())
if not result:
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    print_success "✅ Application startup test passed"
else
    print_error "❌ Application startup test failed"
    rm -f "$TEST_DB_PATH"
    exit 1
fi

# Clean up test database
rm -f "$TEST_DB_PATH"

# Final validation
print_status "🔍 Final production readiness checks..."

# Check that production environment variables are documented
if [ ! -f "../PRODUCTION_DEPLOYMENT_ALEMBIC.md" ]; then
    print_error "❌ Production deployment guide not found"
    exit 1
fi

print_success "✅ Production deployment guide available"

# Check that Docker configuration is updated
if ! grep -q "alembic.ini" ../backend/Dockerfile; then
    print_error "❌ Dockerfile not updated for Alembic"
    exit 1
fi

print_success "✅ Dockerfile configured for Alembic"

# Check that requirements include Alembic
if ! grep -q "alembic" requirements.txt; then
    print_error "❌ Alembic not in requirements.txt"
    exit 1
fi

if ! grep -q "sqlalchemy" requirements.txt; then
    print_error "❌ SQLAlchemy not in requirements.txt"
    exit 1
fi

print_success "✅ Dependencies correctly configured"

cd ..

print_success "🎉 All pre-deployment validation checks passed!"
print_info "📋 Summary:"
print_info "   ✅ Alembic configuration valid"
print_info "   ✅ Migration files present and working"
print_info "   ✅ Database schema validation passed"
print_info "   ✅ Application startup test passed"
print_info "   ✅ Docker configuration updated"
print_info "   ✅ Production documentation available"
print_info ""
print_success "🚀 Ready for production deployment!"
print_info "   Run: ./scripts/smart-deploy.sh"
