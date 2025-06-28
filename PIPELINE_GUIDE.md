# GitHub Actions Pipeline Summary

This document explains how the GitHub Actions workflows work with your manual HTTPS deployment setup.

## Overview

The pipeline is designed to work seamlessly with your manual deployment approach. It automates the deployment process while respecting your manually configured HTTPS setup.

## Workflows

### 1. `deploy.yml` - Main Deployment Pipeline

**Triggers:**
- Push to `main` branch
- Pull request merged to `main`

**Process:**
1. **Test Phase** (Runs on every PR and push)
   - Sets up Node.js 18
   - Installs frontend dependencies
   - Runs frontend tests
   - Sets up Python 3.11
   - Installs backend dependencies
   - Runs backend tests with pytest

2. **Deploy Phase** (Only on push to main)
   - Connects to VM via SSH
   - Creates/navigates to `/home/miska/linkshortener`
   - Stops running services safely
   - Initializes git repository if needed
   - Pulls latest code from main branch
   - Preserves existing `.env` file (your Azure AD config)
   - Starts services with `./manage-fullstack.sh start`
   - Runs health checks on both HTTP and HTTPS
   - Shows logs if anything fails

**Key Features:**
- ✅ Preserves your manually configured `.env` file
- ✅ Works with both HTTP and HTTPS setups
- ✅ Graceful failure handling with detailed logging
- ✅ No sudo required - uses user-writable directories

### 2. `health-check.yml` - Automated Monitoring

**Triggers:**
- Every 30 minutes (scheduled)
- Manual trigger from GitHub Actions tab

**Process:**
- Checks if Docker containers are running
- Tests health endpoints on both HTTP and HTTPS
- Tests frontend accessibility
- Reports detailed status and logs on failure

### 3. `rollback.yml` - Emergency Rollback

**Triggers:**
- Manual trigger only (for safety)

**Process:**
- Can rollback to a specific commit or previous commit
- Stops services, resets code, rebuilds containers
- Includes health checks after rollback

## Current Pipeline Status

✅ **Compatible with your setup:**
- Uses correct deployment path (`/home/miska/linkshortener`)
- Respects your HTTPS nginx configuration
- Preserves your Azure AD environment variables
- Works with your manual SSL certificate setup

✅ **Robust error handling:**
- Tests both HTTP (internal) and HTTPS (external) endpoints
- Shows detailed logs on failure
- Continues deployment even if some health checks fail
- Graceful handling of missing environment files

✅ **Security:**
- No sudo commands required
- Uses SSH key authentication
- Preserves existing sensitive configuration

## How It Works With Your Setup

### Your Manual Setup:
1. You manually configured HTTPS with certbot
2. You manually created nginx configuration for HTTPS
3. You manually set up Azure AD credentials in `.env`

### What the Pipeline Does:
1. **Respects your config** - Never overwrites your `.env` or nginx config
2. **Updates code only** - Pulls latest application code and rebuilds containers
3. **Health checks both protocols** - Tests the internal Docker stack (HTTP:8080) and external nginx (HTTPS:443)
4. **Safe deployment** - If anything fails, shows logs but doesn't break your existing setup

## Environment Variables Required

The pipeline requires only one GitHub secret:
- `VM_SSH_KEY` - Your SSH private key for VM access

On the VM, you need these in `/home/miska/linkshortener/.env`:
```bash
AZURE_TENANT_ID=your-actual-tenant-id
AZURE_CLIENT_ID=your-actual-client-id
BASE_URL=https://links.miskakyto.fi
ALLOWED_ORIGINS=https://links.miskakyto.fi
DATABASE_URL=sqlite:///data/links.db
PRODUCTION=true
```

## Manual Deployment vs Automated

**Manual Deployment Benefits:**
- Full control over environment setup
- Can troubleshoot issues step by step
- One-time SSL and nginx configuration

**Automated Pipeline Benefits:**
- Automatic testing before deployment
- Consistent deployment process
- Easy rollback capability
- Continuous health monitoring
- No manual intervention needed for code updates

## Monitoring and Troubleshooting

### View Pipeline Status:
1. Go to your GitHub repository
2. Click "Actions" tab
3. See status of deployments, tests, and health checks

### Manual Health Check:
```bash
ssh miska@4.210.156.244
cd /home/miska/linkshortener
./manage-fullstack.sh health
```

### View Logs:
```bash
./manage-fullstack.sh logs
./manage-fullstack.sh logs backend
./manage-fullstack.sh logs frontend
```

### Manual Deployment:
If the pipeline fails, you can always deploy manually:
```bash
ssh miska@4.210.156.244
cd /home/miska/linkshortener
git pull origin main
./manage-fullstack.sh restart
```

## Pipeline Safety Features

1. **Non-destructive** - Never removes your configuration
2. **Rollback ready** - Can revert to any previous commit
3. **Health monitoring** - Continuous monitoring with alerts
4. **Graceful failure** - Shows errors but doesn't break existing deployment
5. **Test-first** - Code is tested before deployment

The pipeline is now ready to use with your HTTPS setup! 🚀
