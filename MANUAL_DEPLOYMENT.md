# Manual Deployment Guide for LinkShortener

This guide will walk you through manually setting up your LinkShortener application on your Azure VM.

## Prerequisites

- SSH access to your VM: `ssh miska@4.210.156.244`
- Domain `links.miskakyto.fi` pointing to your VM's IP address
- Basic familiarity with Linux command line

## Phase 1: Initial Setup (HTTP Only)

### Step 1: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER

# Install nginx
sudo apt install -y nginx

# Install git and other tools
sudo apt install -y git curl htop nano
```

**Important:** After adding yourself to the docker group, you need to log out and log back in for the changes to take effect:
```bash
logout
# Then SSH back in
ssh miska@4.210.156.244
```

### Step 2: Create Application Directory

```bash
# Create the application directory
mkdir -p /home/miska/linkshortener
cd /home/miska/linkshortener

# Clone the repository
git clone https://github.com/Hylje5000/links-miskakyto.git .

# Make scripts executable
chmod +x manage-fullstack.sh
```

### Step 3: Configure Environment

```bash
# Create environment file from template
cp backend/.env.production .env

# Edit the environment file
nano .env
```

**Required environment variables:**
```bash
# Azure AD Configuration (Required)
AZURE_TENANT_ID=your-actual-tenant-id
AZURE_CLIENT_ID=your-actual-client-id

# Production settings
BASE_URL=http://links.miskakyto.fi  # Note: HTTP for now
ALLOWED_ORIGINS=http://links.miskakyto.fi
DATABASE_URL=sqlite:///data/links.db
PRODUCTION=true
```

### Step 4: Configure Nginx (HTTP Only)

```bash
# Copy the HTTP-only nginx configuration
sudo cp nginx-http-only.conf /etc/nginx/sites-available/linkshortener

# Enable the site
sudo ln -s /etc/nginx/sites-available/linkshortener /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx
```

### Step 5: Start the Application

```bash
# Start the Docker services
./manage-fullstack.sh start

# Check if services are running
./manage-fullstack.sh status

# View logs if needed
./manage-fullstack.sh logs
```

### Step 6: Test HTTP Deployment

Open your browser and go to `http://links.miskakyto.fi`

You should see your LinkShortener application running!

## Phase 2: Enable HTTPS

### Step 7: Install Certbot

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Stop nginx temporarily
sudo systemctl stop nginx
```

### Step 8: Obtain SSL Certificate

```bash
# Get SSL certificate for your domain
sudo certbot certonly --standalone -d links.miskakyto.fi

# Follow the prompts to enter your email and agree to terms
```

### Step 9: Switch to HTTPS Configuration

```bash
# Copy the HTTPS nginx configuration
sudo cp /home/miska/linkshortener/nginx-https.conf /etc/nginx/sites-available/linkshortener

# Test nginx configuration
sudo nginx -t

# If test passes, start nginx
sudo systemctl start nginx
```

### Step 10: Update Environment for HTTPS

```bash
# Edit environment file to use HTTPS URLs
nano .env
```

Update these lines:
```bash
BASE_URL=https://links.miskakyto.fi  # Change to HTTPS
ALLOWED_ORIGINS=https://links.miskakyto.fi  # Change to HTTPS
```

### Step 11: Restart Application

```bash
# Restart the application with new HTTPS settings
./manage-fullstack.sh restart

# Check status
./manage-fullstack.sh status
```

### Step 12: Set Up Auto-Renewal

```bash
# Test automatic renewal
sudo certbot renew --dry-run

# If successful, the cron job is already set up automatically
```

## Phase 3: Configure Azure AD

### Step 13: Update Azure AD Redirect URIs

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to "Azure Active Directory" > "App registrations"
3. Select your application
4. Go to "Authentication"
5. Update redirect URIs to use HTTPS:
   - `https://links.miskakyto.fi`
   - `https://links.miskakyto.fi/auth/callback` (if needed)

## Management Commands

Once everything is set up, you can use these commands to manage your application:

```bash
# Navigate to application directory
cd /home/miska/linkshortener

# Start services
./manage-fullstack.sh start

# Stop services
./manage-fullstack.sh stop

# Restart services
./manage-fullstack.sh restart

# View status
./manage-fullstack.sh status

# View logs
./manage-fullstack.sh logs

# View logs for specific service
./manage-fullstack.sh logs backend
./manage-fullstack.sh logs frontend

# Health check
./manage-fullstack.sh health

# Update application (pull latest code and restart)
git pull origin main
./manage-fullstack.sh restart
```

## Troubleshooting

### Check if services are running:
```bash
docker ps
./manage-fullstack.sh status
```

### View application logs:
```bash
./manage-fullstack.sh logs
```

### Check nginx status:
```bash
sudo systemctl status nginx
sudo nginx -t
```

### Check disk space:
```bash
df -h
```

### Check if ports are in use:
```bash
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
sudo netstat -tlnp | grep :8080
```

### Restart everything:
```bash
# Restart application
./manage-fullstack.sh restart

# Restart nginx
sudo systemctl restart nginx
```

## Security Notes

- The application runs on port 8080 internally and nginx proxies to it
- SSL certificates auto-renew via certbot
- Only required environment variables are AZURE_TENANT_ID and AZURE_CLIENT_ID
- Database is SQLite stored in the `data/` directory
- Logs are available via `./manage-fullstack.sh logs`

## Backup

To backup your data:
```bash
# Backup the database
cp /home/miska/linkshortener/data/links.db /home/miska/linkshortener-backup-$(date +%Y%m%d).db

# Backup environment config
cp /home/miska/linkshortener/.env /home/miska/linkshortener-env-backup-$(date +%Y%m%d)
```
