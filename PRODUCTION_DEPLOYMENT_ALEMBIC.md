# Production Deployment Guide - Alembic Integration

This guide ensures that the Alembic migration system works correctly in production deployments.

## ✅ Production-Ready Alembic Setup

### Key Features
- **Automatic Migrations**: Migrations run automatically on container startup
- **Production Database**: Uses persistent volume for database storage
- **Zero-Downtime**: Migrations are atomic and safe for production
- **Backup Support**: Database backups created before migrations

### Production Environment Variables

The following environment variables control the database configuration:

```env
# Production database configuration
DATABASE_URL=sqlite:///data/links.db    # Persistent data volume
ENVIRONMENT=production                  # Production mode
PRODUCTION=true                        # Production flag

# Azure AD configuration (required for auth)
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id

# Application configuration
BASE_URL=https://your-domain.com
ALLOWED_ORIGINS=https://your-domain.com
```

### Container Configuration

The Docker setup is optimized for production:

```dockerfile
# Alembic.ini is automatically configured for container paths
RUN sed -i 's|sqlalchemy.url = sqlite:///./links.db|sqlalchemy.url = sqlite:///data/links.db|g' alembic.ini

# Database directory is created and mounted as volume
RUN mkdir -p /app/data
VOLUME ["/app/data"]
```

### Migration Process

1. **Container Startup**: Application starts with `init_db()` call
2. **Alembic Check**: Current database version is verified
3. **Auto-Migration**: Any pending migrations are applied
4. **Backup Creation**: Database backup created before migration
5. **Validation**: Final schema validation performed

### Database Persistence

The production setup uses Docker volumes for persistence:

```yaml
# docker-compose.fullstack.yml
volumes:
  - ../data:/app/data  # Host directory mapped to container
```

This ensures:
- ✅ Database survives container restarts
- ✅ Migrations are preserved across deployments
- ✅ Data is backed up with the host system

## 🚀 Deployment Commands

### Initial Production Setup

```bash
# 1. Clone repository on production server
git clone https://github.com/yourusername/LinkShortener.git
cd LinkShortener

# 2. Configure environment
cp backend/.env.production .env
# Edit .env with your Azure AD credentials

# 3. Deploy with smart script
chmod +x scripts/smart-deploy.sh
./scripts/smart-deploy.sh
```

### Regular Updates

```bash
# Pull latest changes and auto-deploy
git pull origin main
./scripts/smart-deploy.sh
```

The smart deploy script automatically:
- ✅ Detects backend changes
- ✅ Rebuilds only changed containers
- ✅ Runs health checks after deployment
- ✅ Preserves database and configuration

### Manual Migration Commands

For advanced scenarios, you can run Alembic commands manually:

```bash
# Enter backend container
docker exec -it linkshortener-backend bash

# Check current migration
alembic current

# Apply all pending migrations
alembic upgrade head

# View migration history
alembic history

# Rollback one migration (use with caution!)
alembic downgrade -1
```

## 🔧 Production Troubleshooting

### Migration Issues

**Problem**: Migration fails on startup
```
❌ Migration failed: [error details]
```

**Solution**: 
1. Check database file permissions in `/data` directory
2. Verify `alembic.ini` database URL is correct
3. Check container logs: `docker logs linkshortener-backend`

**Recovery**:
```bash
# Restore from automatic backup
cd data
ls -la *.backup_*  # Find latest backup
cp links.db.backup_TIMESTAMP links.db
```

### Database Corruption

**Problem**: Database file corrupted or missing

**Solution**:
1. Stop containers: `docker-compose down`
2. Check backup files in `/data` directory
3. Restore from backup: `cp links.db.backup_latest links.db`
4. Restart: `docker-compose up -d`

### Permission Issues

**Problem**: Container cannot access `/data` directory

**Solution**:
```bash
# Fix directory permissions
sudo chown -R 1000:1000 data/
sudo chmod -R 755 data/
```

## 📊 Production Monitoring

### Health Checks

The container includes health checks that verify:
- ✅ Database accessibility
- ✅ API endpoints responding
- ✅ Migration status

### Logs

Monitor application logs:
```bash
# Follow backend logs
docker logs -f linkshortener-backend

# Check for migration messages
docker logs linkshortener-backend | grep -i alembic
```

### Backup Strategy

Automated backups are created:
- **Before migrations**: `links.db.backup_TIMESTAMP`
- **Location**: `/data` directory on host
- **Retention**: Manual cleanup recommended

Implement regular backups:
```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp data/links.db data/links.db.daily_backup_$DATE

# Keep only last 7 days
find data/ -name "links.db.daily_backup_*" -mtime +7 -delete
```

## ✅ Production Checklist

Before deploying to production:

- [ ] Environment variables configured in `.env`
- [ ] Azure AD app registration completed
- [ ] Domain name and SSL certificates configured
- [ ] Data directory has correct permissions
- [ ] Backup strategy implemented
- [ ] Health monitoring set up
- [ ] Test deployment on staging environment

After deployment:

- [ ] Health checks passing
- [ ] Database migrations applied successfully
- [ ] Authentication working with Azure AD
- [ ] URL shortening functionality operational
- [ ] Analytics tracking working
- [ ] Monitoring and logging active

## 🔄 Rollback Plan

If issues occur during deployment:

1. **Stop containers**: `docker-compose down`
2. **Restore database**: `cp data/links.db.backup_LATEST data/links.db`
3. **Revert code**: `git reset --hard PREVIOUS_COMMIT`
4. **Rebuild**: `./scripts/smart-deploy.sh`

## 📞 Support

For production issues:
1. Check container logs first
2. Verify environment configuration
3. Test migration commands manually
4. Restore from backups if needed

The Alembic integration is production-tested and ready for deployment!
