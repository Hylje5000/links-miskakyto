# Deployment Troubleshooting Guide

## Common Issues and Solutions

### 1. Health Check 404 Error ✅ FIXED

**Problem:** Deployment hangs on health check with 404 error for `/health` endpoint.

**Cause:** Backend was missing health check endpoints.

**Solution:** Added health endpoints to backend:
- `/health` - Main health check endpoint
- `/api/health` - Alias for compatibility

**Test the fix:**
```bash
# Test health endpoints after deployment
curl https://links.miskakyto.fi/health
curl https://links.miskakyto.fi/api/health
```

### 2. API Redirect Loops (301/307)

**Problem:** Accessing `/api` causes redirect loops with 301 and 307 responses.

**Possible Causes:**
1. **Nginx redirect loop** - External nginx redirecting to internal nginx
2. **Trailing slash issues** - Nginx adding/removing trailing slashes
3. **HTTPS/HTTP mixed routing** - Protocol mismatches

**Debug Steps:**
```bash
# SSH into VM
ssh miska@4.210.156.244

# Check nginx logs
sudo tail -f /var/log/nginx/linkshortener_access.log
sudo tail -f /var/log/nginx/linkshortener_error.log

# Check Docker logs
cd /home/miska/linkshortener
./manage-fullstack.sh logs backend
./manage-fullstack.sh logs nginx

# Test internal Docker routing
curl -I http://localhost:8080/api/
curl -I http://localhost:8080/api/health

# Test external nginx routing  
curl -I https://links.miskakyto.fi/api/
curl -I https://links.miskakyto.fi/api/health
```

**Possible Solutions:**

#### Option 1: Fix Nginx Configuration
```bash
# Edit nginx configuration
sudo nano /etc/nginx/sites-available/linkshortener

# Look for redirect loops in location blocks
# Ensure API routes are properly proxied:
location /api/ {
    proxy_pass http://127.0.0.1:8080/api/;
    # ... proxy headers
}
```

#### Option 2: Check Docker Internal Nginx
```bash
# Check internal nginx configuration
cat /home/miska/linkshortener/nginx-docker.conf

# Ensure internal routing is correct:
# Frontend: port 3000
# Backend: port 8000
# Nginx: port 80 (inside Docker)
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
