# Deployment Troubleshooting Guide

## Common Issues and Solutions

### 1. Health Check 404 Error ✅ FIXED

**Problem:** Deployment hangs on health check with 404 error for `/health` endpoint.

**Cause:** Backend was missing health check endpoints.

**Solution:** Consolidated to single health endpoint:
- `/api/health` - Primary health check endpoint (removed `/health` for simplicity)

**If still getting 404 for /api/health after pushing changes, the backend container needs to be rebuilt:**

#### Step 1: Force container rebuild (MOST COMMON SOLUTION)
```bash
# SSH into VM
ssh miska@4.210.156.244
cd /home/miska/linkshortener

# Stop containers and force rebuild backend
./manage-fullstack.sh stop
docker-compose -f docker-compose.fullstack.yml build --no-cache linkshortener-backend
./manage-fullstack.sh start

# Wait 30 seconds for startup
sleep 30

# Test - should now return 200 with health JSON
curl http://localhost:8080/api/health
```

#### Step 2: Verify backend has latest code
```bash
# Check what endpoints are available in the backend
curl http://localhost:8080/debug/routes

# Should show /api/health in the list
# If it doesn't, the container still has old code
```

#### Step 3: Debug backend directly
```bash
# Test backend container directly (bypassing nginx)
docker-compose -f docker-compose.fullstack.yml exec linkshortener-backend curl http://localhost:8000/api/health

# If this returns 404, the backend definitely needs rebuilding
# If this works but nginx returns 404, it's a routing issue
```

#### Step 1: Check if deployment completed
```bash
# SSH into VM
ssh miska@4.210.156.244
cd /home/miska/linkshortener

# Check if latest code is deployed
git log --oneline -3
# Should show your latest commit with health endpoints

# Check if containers restarted
docker-compose -f docker-compose.fullstack.yml ps
# All containers should show "Up" status
```

#### Step 2: Test backend directly inside Docker
```bash
# Get into the backend container
docker-compose -f docker-compose.fullstack.yml exec linkshortener-backend bash

# Test health endpoint directly inside container
curl http://localhost:8000/api/health
curl http://localhost:8000/  # Should return {"message": "Link Shortener API", "version": "1.0.0"}

# Exit container
exit
```

#### Step 3: Test internal Docker nginx routing
```bash
# Test internal Docker stack (port 8080)
curl -v http://localhost:8080/api/health

# Check what's actually responding on port 8080
curl -I http://localhost:8080/
```

#### Step 4: Check backend logs for errors
```bash
# Check if backend is starting properly
./manage-fullstack.sh logs backend

# Look for:
# - "Uvicorn running on http://0.0.0.0:8000"
# - Any startup errors
# - Health check requests in logs
```

#### Step 5: Manual container restart
```bash
# If containers show old code, force rebuild
./manage-fullstack.sh stop
docker-compose -f docker-compose.fullstack.yml build --no-cache backend
./manage-fullstack.sh start

# Wait 30 seconds, then test again
sleep 30
curl http://localhost:8080/api/health
```

#### Step 6: Check nginx routing configuration
```bash
# Check internal Docker nginx config
docker-compose -f docker-compose.fullstack.yml exec linkshortener-nginx cat /etc/nginx/conf.d/default.conf

# Should show routing from nginx to backend:8000
```

**Test the fix:**
```bash
# Test health endpoints after deployment
curl https://links.miskakyto.fi/api/health
```

### 2. API Redirect Loops (301/307) - ERR_TOO_MANY_REDIRECTS ✅ FIXED

**Problem:** Accessing `/api` causes redirect loops with 301 and 307 responses, browser shows ERR_TOO_MANY_REDIRECTS.

**Root Cause:** ✅ **IDENTIFIED AND FIXED** - Internal Docker nginx configuration had incorrect `proxy_pass` directive.

**The Fix:** Changed `nginx-docker.conf`:
```nginx
# BEFORE (caused redirects):
location /api/ {
    proxy_pass http://backend;  # Missing /api/ in target
}

# AFTER (fixed):
location /api/ {
    proxy_pass http://backend/api/;  # Correct path mapping
}
```

**What was happening:**
1. External nginx: `https://links.miskakyto.fi/api/` → `http://localhost:8080/api/` ✅
2. Internal Docker nginx: `http://localhost:8080/api/` → `http://backend` (redirected to `http://localhost/api`) ❌
3. This created an infinite redirect loop between the two nginx instances

**Test the fix after deployment:**
```bash
# These should now work without redirects:
curl -I https://links.miskakyto.fi/api/health
curl -I http://localhost:8080/api/health
```

**If still having issues, try manual restart:**
```bash
cd /home/miska/linkshortener
./manage-fullstack.sh stop
./manage-fullstack.sh start
# Wait for containers to rebuild with new nginx config
```

### 3. Docker Build Issues

**Problem:** Docker build fails with dependency errors.

**Solution:** ✅ Already fixed - moved Tailwind CSS to production dependencies.

### 4. Container Not Starting

**Debug Steps:**
```bash
# Check container status
./manage-fullstack.sh status

# Check specific container logs
docker-compose -f docker-compose.fullstack.yml logs backend
docker-compose -f docker-compose.fullstack.yml logs frontend
docker-compose -f docker-compose.fullstack.yml logs nginx

# Rebuild containers
./manage-fullstack.sh stop
./manage-fullstack.sh start
```

### 5. Environment Issues

**Problem:** Application starts but authentication doesn't work.

**Check:**
```bash
# Verify environment file
cat /home/miska/linkshortener/.env

# Should contain:
# AZURE_TENANT_ID=your-actual-tenant-id
# AZURE_CLIENT_ID=your-actual-client-id
# BASE_URL=https://links.miskakyto.fi
# ALLOWED_ORIGINS=https://links.miskakyto.fi
```

### 6. Database Issues

**Problem:** Application can't access database.

**Check:**
```bash
# Verify data directory exists and is writable
ls -la /home/miska/linkshortener/data/

# Should show links.db file
# Check permissions
stat /home/miska/linkshortener/data/links.db
```

## Quick Health Check Commands

```bash
# Full system check
cd /home/miska/linkshortener
./manage-fullstack.sh health

# Individual service checks
curl -I https://links.miskakyto.fi/                    # Frontend
curl -I https://links.miskakyto.fi/health              # Backend health
curl -I https://links.miskakyto.fi/api/health          # API health

# Internal Docker checks
curl -I http://localhost:8080/                         # Internal stack
curl -I http://localhost:8080/api/health               # Internal API
```

## Emergency Recovery

If deployment completely fails:

```bash
# SSH into VM
ssh miska@4.210.156.244
cd /home/miska/linkshortener

# Stop everything
./manage-fullstack.sh stop

# Reset to last working commit
git log --oneline -5  # Find working commit
git reset --hard <commit-hash>

# Restart
./manage-fullstack.sh start

# Check status
./manage-fullstack.sh health
```

## Monitoring

Set up monitoring for these endpoints:
- `https://links.miskakyto.fi/health` - Should return 200 with JSON status
- `https://links.miskakyto.fi/` - Should return frontend (200)
- `https://links.miskakyto.fi/api/health` - Should return API health (200)

The GitHub Actions workflow automatically checks these every 30 minutes.
