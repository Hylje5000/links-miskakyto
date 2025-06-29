#!/bin/bash

# One-time VM Setup Script for LinkShortener
# Run this script once on your VM to set up the deployment environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_status "Setting up LinkShortener deployment environment on VM..."

# Check if running as the correct user
if [ "$USER" != "miska" ]; then
    print_warning "This script should be run as user 'miska'"
fi

# Create deployment directory in user's home
DEPLOY_PATH="/home/miska/linkshortener"
print_status "Creating deployment directory: $DEPLOY_PATH"
mkdir -p "$DEPLOY_PATH"

# Create data directory for SQLite database
print_status "Creating data directory for database..."
mkdir -p "$DEPLOY_PATH/data"

# Set proper permissions
print_status "Setting proper permissions..."
chmod 755 "$DEPLOY_PATH"
chmod 755 "$DEPLOY_PATH/data"

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker miska
    rm get-docker.sh
    print_success "Docker installed successfully"
else
    print_success "Docker is already installed"
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    print_status "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_success "Docker Compose installed successfully"
else
    print_success "Docker Compose is already installed"
fi

# Add user to docker group if not already added
if ! groups miska | grep &>/dev/null '\bdocker\b'; then
    print_status "Adding user to docker group..."
    sudo usermod -aG docker miska
    print_warning "You may need to log out and log back in for docker group membership to take effect"
fi

# Optional: Create symbolic link from /opt/linkshortener to user directory
print_status "Creating symbolic link for easier access..."
if [ ! -L "/opt/linkshortener" ]; then
    sudo ln -sf "$DEPLOY_PATH" /opt/linkshortener
    print_success "Created symbolic link: /opt/linkshortener -> $DEPLOY_PATH"
fi

# Create nginx configuration directory if it doesn't exist
print_status "Setting up nginx configuration..."
sudo mkdir -p /etc/nginx/sites-available
sudo mkdir -p /etc/nginx/sites-enabled

# Create nginx configuration for the application
cat << 'EOF' | sudo tee /etc/nginx/sites-available/linkshortener > /dev/null
server {
    listen 80;
    server_name links.miskakyto.fi;

    # Redirect all HTTP traffic to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name links.miskakyto.fi;

    # SSL configuration (you'll need to configure SSL certificates)
    # ssl_certificate /path/to/your/certificate.crt;
    # ssl_certificate_key /path/to/your/private.key;

    # For now, comment out SSL and use HTTP only for testing
    # listen 80;
    # server_name links.miskakyto.fi;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# Enable the site
if [ ! -L "/etc/nginx/sites-enabled/linkshortener" ]; then
    sudo ln -sf /etc/nginx/sites-available/linkshortener /etc/nginx/sites-enabled/
    print_success "Nginx configuration created and enabled"
fi

# Test nginx configuration
sudo nginx -t && print_success "Nginx configuration is valid" || print_error "Nginx configuration has errors"

# Create environment file template
print_status "Creating environment file template..."
cat << 'EOF' > "$DEPLOY_PATH/.env"
# LinkShortener Environment Configuration
# Edit this file with your actual values

# Azure AD Configuration (Required)
AZURE_TENANT_ID=your-tenant-id-here
AZURE_CLIENT_ID=your-client-id-here

# Production settings
BASE_URL=https://links.miskakyto.fi
ALLOWED_ORIGINS=https://links.miskakyto.fi
DATABASE_URL=sqlite:///data/links.db
PRODUCTION=true
EOF

print_success "Environment file template created at $DEPLOY_PATH/.env"

print_status "Setup completed successfully!"
echo ""
print_warning "Next steps:"
echo "1. Edit $DEPLOY_PATH/.env with your Azure AD credentials"
echo "2. Configure SSL certificates for nginx (optional for testing)"
echo "3. Restart nginx: sudo systemctl restart nginx"
echo "4. Test the deployment by pushing to your main branch"
echo ""
print_success "Your LinkShortener is ready for deployment!"
