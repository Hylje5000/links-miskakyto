# Production Database Troubleshooting Guide

## Quick Fix Commands

If your LinkShortener is experiencing 502 errors or database initialization failures, run these commands on your production VM:

### 1. Automated Fix (Recommended)
```bash
cd ~/linkshortener
./scripts/fix-production-db.sh
```

### 2. Manual Fix Steps
If the automated script doesn't work, run these commands step by step:

```bash
# Stop containers
docker-compose -f docker/docker-compose.fullstack.yml down

# Clean database
rm -rf backend/data/*
mkdir -p backend/data

# Pull latest code
git pull origin main

# Rebuild and start
docker-compose -f docker/docker-compose.fullstack.yml build --no-cache backend
docker-compose -f docker/docker-compose.fullstack.yml up -d

# Check logs
docker logs linkshortener-backend --tail=20
```

## How the Fix Works

The system now includes a robust fallback mechanism:

1. **Primary**: Tries to use Alembic for database migrations
2. **Fallback**: If Alembic fails (missing files, configuration issues), creates database using direct SQL

This ensures your application will start successfully even if:
- `alembic.ini` is missing
- Migration files are corrupted or missing
- Alembic configuration has errors

## Expected Log Output

After the fix, you should see logs like:
```
🚀 Starting Link Shortener API v1.0.0
Environment: production
Debug mode: False
✅ Database initialized successfully
```

The health endpoint should also show:
```bash
curl http://localhost:8080/api/health
# Should return: {"status":"healthy",...,"environment":"production"}
```

## Verification Commands

Test that your application is working:

```bash
# Health check
curl http://localhost:8080/api/health

# Test 401 response (expected without auth)
curl http://localhost:8080/api/links
```

## If Issues Persist

1. Check container logs:
   ```bash
   docker logs linkshortener-backend --tail=50
   docker logs linkshortener-nginx --tail=20
   ```

2. Verify network connectivity:
   ```bash
   docker exec linkshortener-nginx curl http://linkshortener-backend:8000/api/health
   ```

3. Check disk space and resources:
   ```bash
   df -h
   free -h
   docker stats --no-stream
   ```

4. Complete rebuild:
   ```bash
   docker system prune -f
   ./scripts/fix-production-db.sh
   ```

## Key Improvements Made

- **Robust fallback**: System works even without Alembic files
- **Better error handling**: More informative logs and graceful degradation
- **Production-focused**: Container restarts properly on failures
- **Self-healing**: Automatically handles missing configuration files
- **Comprehensive logging**: Easy to diagnose issues

The application is now much more resilient and should handle production deployment issues automatically.
