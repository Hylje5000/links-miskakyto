# Deployment Troubleshooting Guide

## Common Issues and Solutions

### 1. Health Check 404 Error ✅ FIXED

**Problem:** Deployment hangs on health check with 404 error for `/health` endpoint.

**Cause:** Backend was missing health check endpoints.

**Solution:** Added health endpoints to backend:
- `/health` - Main health check endpoint
- `/api/health` - Alias for compatibility

**If still getting 404 after pushing changes, follow these debug steps:**

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
curl http://localhost:8000/health
curl http://localhost:8000/api/health
curl http://localhost:8000/  # Should return {"message": "Link Shortener API", "version": "1.0.0"}

# Exit container
exit
```

#### Step 3: Test internal Docker nginx routing
```bash
# Test internal Docker stack (port 8080)
curl -v http://localhost:8080/health
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
curl http://localhost:8080/health
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
curl https://links.miskakyto.fi/health
curl https://links.miskakyto.fi/api/health
```

### 2. API Redirect Loops (301/307) - ERR_TOO_MANY_REDIRECTS

**Problem:** Accessing `/api` causes redirect loops with 301 and 307 responses, browser shows ERR_TOO_MANY_REDIRECTS.

**Root Cause:** Likely nginx configuration conflict between external nginx and internal Docker nginx.

**Immediate Debug Steps:**

#### Step 1: Check external nginx configuration
```bash
# SSH into VM
ssh miska@4.210.156.244

# Check current nginx config
sudo cat /etc/nginx/sites-available/linkshortener

# Look for problematic patterns:
# 1. Missing trailing slash handling
# 2. Conflicting location blocks
# 3. Incorrect proxy_pass URLs
```

#### Step 2: Test internal vs external routing
```bash
cd /home/miska/linkshortener

# Test internal Docker stack (should work)
curl -v http://localhost:8080/api/ 2>&1 | grep -E "HTTP|Location"

# Test external nginx (problematic)
curl -v https://links.miskakyto.fi/api/ 2>&1 | grep -E "HTTP|Location"

# Compare the responses - look for redirect chains
```

#### Step 3: Check for trailing slash issues
```bash
# Test different API path variations
curl -I http://localhost:8080/api          # No trailing slash
curl -I http://localhost:8080/api/         # With trailing slash
curl -I http://localhost:8080/api/health   # Specific endpoint

# Test same on external
curl -I https://links.miskakyto.fi/api     # Likely causes redirects
curl -I https://links.miskakyto.fi/api/    # Might work
curl -I https://links.miskakyto.fi/api/health  # Should work if routing is correct
```

**Common Fix - Update external nginx config:**

```bash
# Edit nginx configuration
sudo nano /etc/nginx/sites-available/linkshortener

# Find the API location block and fix it:
# WRONG (causes redirects):
location /api {
    proxy_pass http://127.0.0.1:8080/api;
}

# CORRECT (prevents redirects):
location /api/ {
    proxy_pass http://127.0.0.1:8080/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# Also add a redirect for /api without trailing slash:
location = /api {
    return 301 $scheme://$server_name/api/;
}

# Test and reload nginx
sudo nginx -t
sudo systemctl reload nginx
```

**Alternative Quick Fix - Check current config:**

```bash
# Show current nginx config
sudo grep -A 10 -B 2 "location.*api" /etc/nginx/sites-available/linkshortener

# If the above shows problems, you can temporarily disable API routing:
# Comment out the problematic location block, reload nginx, then fix it properly
```

**Possible Causes:**
1. **Nginx redirect loop** - External nginx redirecting to internal nginx incorrectly
2. **Trailing slash issues** - Nginx adding/removing trailing slashes in a loop
3. **HTTPS/HTTP mixed routing** - Protocol mismatches causing redirect chains
4. **Conflicting location blocks** - Multiple rules trying to handle /api

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
