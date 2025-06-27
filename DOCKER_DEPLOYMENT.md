# 🚀 Docker Deployment Guide

This guide covers deploying the Link Shortener backend using Docker on your Azure VM.

## 📋 Prerequisites

- Azure VM running Ubuntu 20.04+ or similar Linux distribution
- Domain `links.miskakyto.fi` pointing to your VM's public IP
- SSH access to your VM
- Azure AD app registration configured

## 🔧 Quick Deployment

### 1. Clone Repository on VM

```bash
# SSH into your Azure VM
ssh user@your-vm-ip

# Clone the repository
git clone <your-repo-url> /opt/linkshortener
cd /opt/linkshortener

# Run deployment script
sudo ./deploy.sh
```

### 2. Configure Environment

```bash
# Copy and edit environment file
cp backend/.env.production .env
nano .env
```

Fill in your Azure AD details:
```env
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
BASE_URL=https://links.miskakyto.fi
ALLOWED_ORIGINS=https://links.miskakyto.fi
```

### 3. Start Services

```bash
# Start with Docker Compose
docker-compose up -d

# Check status
./manage.sh status
```

## 🏗️ Architecture

```
Internet → Nginx (Port 80/443) → FastAPI Backend (Port 8000) → SQLite Database
```

### Components:
- **Nginx**: Reverse proxy, SSL termination, rate limiting
- **FastAPI**: Backend API with authentication
- **SQLite**: Database (mounted as volume for persistence)

## 🔒 SSL Configuration

### Option 1: Let's Encrypt (Recommended)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d links.miskakyto.fi

# Update nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/linkshortener
sudo ln -s /etc/nginx/sites-available/linkshortener /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### Option 2: Existing SSL Certificate

```bash
# Copy your certificates
sudo mkdir -p /opt/linkshortener/ssl
sudo cp your-certificate.crt /opt/linkshortener/ssl/links.miskakyto.fi.crt
sudo cp your-private-key.key /opt/linkshortener/ssl/links.miskakyto.fi.key
```

## 🛠️ Management Commands

```bash
# Service management
./manage.sh status    # Check status
./manage.sh restart   # Restart services
./manage.sh update    # Update from git
./manage.sh backup    # Backup database
./manage.sh logs      # View logs

# Docker commands
docker-compose ps     # List containers
docker-compose logs   # View logs
docker-compose down   # Stop services
docker-compose up -d  # Start services
```

## 🔐 Azure AD Configuration

Update your Azure AD app registration:

1. **Redirect URIs**: Add `https://links.miskakyto.fi`
2. **API Permissions**: Ensure proper scopes
3. **Authentication**: Configure for web application

## 🌐 DNS Configuration

Point your domain to the VM:
```
A Record: links.miskakyto.fi → YOUR_VM_PUBLIC_IP
```

## 📊 Monitoring

### Health Checks
```bash
# API health
curl https://links.miskakyto.fi/health

# Container health
docker-compose ps
```

### Logs
```bash
# Backend logs
docker-compose logs linkshortener-backend

# Nginx logs
docker-compose logs nginx

# Follow logs
./manage.sh logs
```

## 🔧 Troubleshooting

### Common Issues

1. **Port 80/443 not accessible**
   ```bash
   sudo ufw allow 80
   sudo ufw allow 443
   ```

2. **Database permissions**
   ```bash
   sudo chown -R 1000:1000 /opt/linkshortener/data
   ```

3. **SSL certificate issues**
   ```bash
   sudo certbot renew --dry-run
   ```

4. **Container won't start**
   ```bash
   docker-compose logs linkshortener-backend
   docker-compose down && docker-compose up -d
   ```

## 📈 Scaling Options

### PostgreSQL Upgrade
```yaml
# Add to docker-compose.yml
postgres:
  image: postgres:15
  environment:
    POSTGRES_DB: linkshortener
    POSTGRES_USER: linkuser
    POSTGRES_PASSWORD: yourpassword
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

### Load Balancing
- Use Azure Load Balancer
- Multiple VM instances
- Shared database backend

## 🔄 Updates

```bash
# Update application
cd /opt/linkshortener
git pull
./manage.sh update

# Update system
sudo apt update && sudo apt upgrade -y
sudo reboot
```

## 📱 Frontend Deployment

Deploy frontend to Vercel with environment variables:
```env
NEXT_PUBLIC_API_URL=https://links.miskakyto.fi
NEXT_PUBLIC_AZURE_CLIENT_ID=your-client-id
NEXT_PUBLIC_AZURE_TENANT_ID=your-tenant-id
```

## 🎯 Final Setup

1. Backend: `https://links.miskakyto.fi/api/`
2. Short URLs: `https://links.miskakyto.fi/{code}`
3. Frontend: Deploy to Vercel or Azure Static Web Apps
4. Database: Automatic backups with `./manage.sh backup`

Your Link Shortener will be available at `https://links.miskakyto.fi`!
