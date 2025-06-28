# GitHub Actions Deployment Setup

This document explains how to configure GitHub Actions for automatic deployment to your Azure VM.

## 🔐 Required Secrets

You need to configure these secrets in your GitHub repository:

### 1. VM_SSH_KEY

This is your SSH private key for accessing the VM.

#### Generate SSH Key Pair (if you don't have one):

```bash
# On your local machine
ssh-keygen -t ed25519 -C "github-actions@linkshortener" -f ~/.ssh/linkshortener_deploy

# This creates:
# ~/.ssh/linkshortener_deploy (private key - for GitHub secret)
# ~/.ssh/linkshortener_deploy.pub (public key - for VM)
```

#### Add Public Key to VM:

```bash
# Copy public key to VM
ssh-copy-id -i ~/.ssh/linkshortener_deploy.pub miska@4.210.156.244

# Or manually:
# 1. Copy content of ~/.ssh/linkshortener_deploy.pub
# 2. On VM: echo "public-key-content" >> ~/.ssh/authorized_keys
```

#### Add Private Key to GitHub:

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `VM_SSH_KEY`
5. Value: Content of `~/.ssh/linkshortener_deploy` (the private key)

```bash
# Copy private key content
cat ~/.ssh/linkshortener_deploy
```

## 🚀 Workflows Overview

### 1. Deploy Workflow (`.github/workflows/deploy.yml`)

**Triggers:**
- Push to `main` branch
- Closed pull request to `main` branch

**Actions:**
- Runs frontend and backend tests
- SSH into VM and deploy latest code
- Stops existing services
- Pulls latest changes
- Builds Docker containers
- Starts services
- Runs health checks

### 2. Rollback Workflow (`.github/workflows/rollback.yml`)

**Triggers:**
- Manual trigger only (workflow_dispatch)

**Actions:**
- Rollback to previous commit or specified commit
- Creates backup branch before rollback
- Rebuilds and restarts services
- Runs health checks

**Usage:**
1. Go to Actions tab in GitHub
2. Select "Rollback Deployment"
3. Click "Run workflow"
4. Optionally specify commit SHA to rollback to

### 3. Health Check Workflow (`.github/workflows/health-check.yml`)

**Triggers:**
- Every 30 minutes (scheduled)
- Manual trigger

**Actions:**
- Checks if containers are running
- Tests health endpoints
- Monitors disk usage
- Reports status

## 🔧 Manual Setup on VM

### 1. Ensure SSH Access

```bash
# Test SSH access from your local machine
ssh -i ~/.ssh/linkshortener_deploy miska@4.210.156.244

# On VM, ensure the application is properly set up
cd /opt/linkshortener
ls -la  # Should show your application files
```

### 2. Initial Deployment

If this is the first time setting up, run the initial deployment manually:

```bash
# On VM
cd /opt/linkshortener
sudo ./deploy-fullstack.sh

# Configure environment
nano .env

# Build and start
./manage-fullstack.sh build
./manage-fullstack.sh start
```

### 3. Verify GitHub Actions Can Access

Test that GitHub Actions can access your VM:

```bash
# Add GitHub's SSH host keys to known_hosts (on VM)
ssh-keyscan github.com >> ~/.ssh/known_hosts
```

## 🎯 Deployment Process

### Automatic Deployment

1. **Push to main branch:**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   git push origin main
   ```

2. **GitHub Actions will:**
   - Run tests
   - Deploy to VM if tests pass
   - Verify deployment health

### Manual Rollback

If something goes wrong:

1. Go to GitHub → Actions
2. Select "Rollback Deployment"
3. Click "Run workflow"
4. Optionally specify commit to rollback to

### Emergency Manual Fix

If GitHub Actions fails, you can always deploy manually:

```bash
# SSH into VM
ssh miska@4.210.156.244

# Navigate to app directory
cd /opt/linkshortener

# Pull latest changes
git pull

# Rebuild and restart
./manage-fullstack.sh stop
./manage-fullstack.sh build
./manage-fullstack.sh start

# Check status
./manage-fullstack.sh status
```

## 📊 Monitoring

### GitHub Actions Monitoring

- Check the Actions tab for deployment status
- Health checks run every 30 minutes
- Failed deployments will show in the Actions log

### VM Monitoring

```bash
# Check application status
./manage-fullstack.sh status

# View logs
./manage-fullstack.sh logs

# Check resource usage
docker stats
df -h
```

## 🔒 Security Notes

1. **SSH Key Security:**
   - Use a dedicated SSH key for GitHub Actions
   - Limit the key to only necessary operations
   - Regularly rotate SSH keys

2. **VM Security:**
   - Keep VM updated: `sudo apt update && sudo apt upgrade`
   - Monitor SSH access logs: `sudo tail -f /var/log/auth.log`
   - Consider using SSH key restrictions

3. **Environment Variables:**
   - Keep sensitive data in `.env` file (not in git)
   - Backup `.env` file separately
   - Use Azure Key Vault for production secrets (optional)

## 🚨 Troubleshooting

### Common Issues

1. **SSH Connection Failed:**
   - Check if SSH key is correct
   - Verify VM IP address (4.210.156.244)
   - Check if VM is accessible

2. **Deployment Failed:**
   - Check Actions logs for specific error
   - SSH into VM and check manually
   - Look at container logs: `./manage-fullstack.sh logs`

3. **Health Check Failed:**
   - Check if containers are running: `docker ps`
   - Check nginx proxy configuration
   - Verify port 8080 is accessible

### Emergency Commands

```bash
# Force restart everything
./manage-fullstack.sh stop
docker system prune -f
./manage-fullstack.sh start

# Check what's using port 8080
sudo netstat -tlnp | grep 8080

# View detailed logs
./manage-fullstack.sh logs-backend
./manage-fullstack.sh logs-frontend
./manage-fullstack.sh logs-nginx
```

## ✅ Verification

After setting up, verify everything works:

1. **Test SSH access:**
   ```bash
   ssh -i ~/.ssh/linkshortener_deploy miska@4.210.156.244 "cd /opt/linkshortener && ./manage-fullstack.sh status"
   ```

2. **Test manual trigger:**
   - Go to GitHub Actions
   - Run "Health Check" workflow manually
   - Should complete successfully

3. **Test automatic deployment:**
   - Make a small change to README
   - Push to main branch
   - Watch Actions tab for automatic deployment

Once everything is set up, every push to main will automatically deploy to your VM! 🚀
