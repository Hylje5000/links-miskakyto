#!/bin/bash

# Production Database Fix Script
echo "🔧 LinkShortener Production Database Fix"
echo "========================================"

# Stop any running containers
echo "📋 Stopping containers..."
docker-compose -f docker/docker-compose.fullstack.yml down 2>/dev/null || true
docker stop $(docker ps -q) 2>/dev/null || true

# Clean up old data
echo "📋 Cleaning up problematic database files..."
rm -rf backend/data/*
mkdir -p backend/data

# Check if Alembic files exist
echo "📋 Checking Alembic configuration..."
if [ ! -f backend/alembic.ini ]; then
    echo "⚠️ alembic.ini missing - fallback initialization will be used"
fi

if [ ! -d backend/alembic/versions ] || [ -z "$(ls -A backend/alembic/versions 2>/dev/null)" ]; then
    echo "⚠️ Alembic migration files missing - fallback initialization will be used"
fi

# Pull latest code to ensure we have all files
echo "📋 Pulling latest code..."
git pull origin main || echo "⚠️ Git pull failed - continuing with current files"

# Rebuild containers with no cache to ensure clean build
echo "📋 Rebuilding containers..."
docker-compose -f docker/docker-compose.fullstack.yml build --no-cache backend

# Start containers
echo "📋 Starting containers..."
docker-compose -f docker/docker-compose.fullstack.yml up -d

# Wait a moment for startup
echo "📋 Waiting for services to start..."
sleep 10

# Check logs
echo "📋 Checking backend logs..."
docker logs linkshortener-backend --tail=20

echo ""
echo "📋 Testing health endpoint..."
curl -s http://localhost:8080/api/health | grep -q "ok" && echo "✅ Health check passed" || echo "❌ Health check failed"

echo ""
echo "📋 Quick connectivity test..."
docker exec linkshortener-nginx curl -s http://linkshortener-backend:8000/api/health > /dev/null 2>&1 && echo "✅ Network connectivity OK" || echo "❌ Network connectivity failed"

echo ""
echo "🎉 Production database fix complete!"
echo "If issues persist, check logs with: docker logs linkshortener-backend"
