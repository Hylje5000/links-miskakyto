# Production Environment Checklist - Alembic Ready ✅

## Pre-Deployment Verification

Run this checklist before deploying to production to ensure Alembic integration works correctly.

### ✅ Environment Setup

- [ ] **Azure AD App Registration**
  - [ ] Client ID configured
  - [ ] Tenant ID configured  
  - [ ] Redirect URIs include production domain
  - [ ] API permissions granted

- [ ] **Environment Variables** (`.env` file)
  ```env
  AZURE_TENANT_ID=your-tenant-id
  AZURE_CLIENT_ID=your-client-id
  BASE_URL=https://your-domain.com
  ALLOWED_ORIGINS=https://your-domain.com
  DATABASE_URL=sqlite:///data/links.db
  ENVIRONMENT=production
  PRODUCTION=true
  ```

- [ ] **Domain and SSL**
  - [ ] Domain name configured
  - [ ] SSL certificates installed
  - [ ] DNS pointing to server

### ✅ Database Migration Validation

Run the validation script:
```bash
./scripts/validate-migrations.sh
```

This verifies:
- [ ] Alembic configuration is correct
- [ ] Migration files are present and valid
- [ ] Database schema can be created successfully
- [ ] Application starts with migrated database
- [ ] Docker configuration includes Alembic support

### ✅ Server Prerequisites

- [ ] **Docker and Docker Compose** installed
- [ ] **Git** installed for deployment
- [ ] **Sufficient disk space** (at least 5GB free)
- [ ] **Network ports open** (80, 443)
- [ ] **Backup strategy** planned

### ✅ Data Directory Setup

```bash
# Create data directory with correct permissions
mkdir -p data
sudo chown -R 1000:1000 data/
sudo chmod -R 755 data/
```

### ✅ Deployment Process

1. **Initial Setup**
   ```bash
   git clone https://github.com/yourusername/LinkShortener.git
   cd LinkShortener
   ```

2. **Configure Environment**
   ```bash
   cp backend/.env.production .env
   # Edit .env with your values
   ```

3. **Run Validation**
   ```bash
   ./scripts/validate-migrations.sh
   ```

4. **Deploy**
   ```bash
   ./scripts/smart-deploy.sh
   ```

### ✅ Post-Deployment Verification

After deployment, verify:

- [ ] **Health Check Passes**
  ```bash
  curl -f http://localhost:8080/api/health
  ```

- [ ] **Database Migration Applied**
  ```bash
  docker exec linkshortener-backend alembic current
  ```

- [ ] **Frontend Loads**
  ```bash
  curl -s http://localhost:8080/ | grep -q "<!DOCTYPE html"
  ```

- [ ] **Authentication Works**
  - [ ] Can log in with Azure AD
  - [ ] JWT tokens are validated
  - [ ] User info displayed correctly

- [ ] **Core Functionality**
  - [ ] Can create shortened links
  - [ ] Links redirect correctly
  - [ ] Analytics are tracked
  - [ ] Click counting works

### ✅ Monitoring Setup

- [ ] **Log Monitoring**
  ```bash
  # Monitor application logs
  docker logs -f linkshortener-backend
  ```

- [ ] **Database Backups**
  ```bash
  # Set up daily backup cron job
  0 2 * * * cp /path/to/data/links.db /path/to/backups/links.db.$(date +\%Y\%m\%d)
  ```

- [ ] **Health Check Monitoring**
  ```bash
  # Monitor health endpoint
  */5 * * * * curl -f http://localhost:8080/api/health || echo "Health check failed" | mail -s "LinkShortener Alert" admin@example.com
  ```

### ✅ Troubleshooting Commands

#### Database Issues
```bash
# Check current migration
docker exec linkshortener-backend alembic current

# Check migration history
docker exec linkshortener-backend alembic history

# Manual migration (if needed)
docker exec linkshortener-backend alembic upgrade head

# Rollback (use with caution!)
docker exec linkshortener-backend alembic downgrade -1
```

#### Container Issues
```bash
# Check container status
docker ps
docker-compose ps

# View logs
docker logs linkshortener-backend
docker logs linkshortener-frontend
docker logs linkshortener-nginx

# Restart services
docker-compose restart
```

#### Database Recovery
```bash
# List available backups
ls -la data/links.db.backup_*

# Restore from backup (stop containers first)
docker-compose down
cp data/links.db.backup_TIMESTAMP data/links.db
docker-compose up -d
```

### ✅ Production Updates

For future updates:

1. **Pull Changes**
   ```bash
   git pull origin main
   ```

2. **Validate Migrations** (automatically runs if backend changed)
   ```bash
   ./scripts/smart-deploy.sh
   ```

3. **Monitor Deployment**
   ```bash
   # The smart deploy script will:
   # - Run validation if backend changed
   # - Rebuild only changed components
   # - Run health checks
   # - Report deployment status
   ```

### ✅ Emergency Rollback

If deployment fails:

1. **Stop containers**
   ```bash
   docker-compose down
   ```

2. **Restore database**
   ```bash
   cp data/links.db.backup_LATEST data/links.db
   ```

3. **Revert code**
   ```bash
   git reset --hard PREVIOUS_COMMIT
   ```

4. **Redeploy**
   ```bash
   ./scripts/smart-deploy.sh
   ```

## ✅ Checklist Summary

Before going live:
- [ ] All environment variables configured
- [ ] Migration validation passes
- [ ] Health checks work
- [ ] Authentication functional
- [ ] Core features tested
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] Emergency procedures documented

**Status**: ✅ Production Ready with Alembic Integration

The LinkShortener application is now production-ready with a robust, industry-standard database migration system!
