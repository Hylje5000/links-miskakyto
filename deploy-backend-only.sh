#!/bin/bash

# Deploy Link Shortener backend to existing server setup
# This script deploys only the backend service on port 8000

set -e

echo "🚀 Deploying Link Shortener Backend to existing server..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "⚠️  Please run this script as a regular user with sudo privileges, not as root"
   exit 1
fi

# Get the current directory (should be the cloned repo)
REPO_DIR=$(pwd)
echo "📁 Working from repository: $REPO_DIR"

# Ensure we own the repository files
echo "🔧 Fixing repository permissions..."
sudo chown -R $USER:$USER $REPO_DIR

# Install Docker and Docker Compose if needed
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "⚠️  Docker installed. You may need to log out and back in for Docker group membership to take effect."
    echo "   Or run: newgrp docker"
fi

if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create application directory
APP_DIR="/opt/linkshortener"
if [ ! -d "$APP_DIR" ]; then
    echo "📁 Creating application directory..."
    sudo mkdir -p $APP_DIR
    sudo chown $USER:$USER $APP_DIR
fi

# Create data directory for database
echo "📁 Creating data directory..."
sudo mkdir -p $APP_DIR/data
sudo chown $USER:$USER $APP_DIR/data
sudo chmod 755 $APP_DIR/data

# Copy deployment files
echo "📋 Setting up configuration..."
sudo cp docker-compose.standalone.yml $APP_DIR/docker-compose.yml
sudo cp backend/.env.production $APP_DIR/.env.example
sudo cp manage-backend.sh $APP_DIR/manage.sh
sudo chmod +x $APP_DIR/manage.sh
sudo chown $USER:$USER $APP_DIR/manage.sh

# Copy additional files
sudo cp nginx-integration.conf $APP_DIR/
sudo cp verify-integration.sh $APP_DIR/
sudo chmod +x $APP_DIR/verify-integration.sh
sudo chown $USER:$USER $APP_DIR/verify-integration.sh

# Ensure all files in the app directory are owned by the user
sudo chown -R $USER:$USER $APP_DIR

# Create systemd service for auto-start
echo "⚙️  Creating systemd service..."
sudo tee /etc/systemd/system/linkshortener.service > /dev/null <<EOF
[Unit]
Description=Link Shortener Backend
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$APP_DIR
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Enable the service
sudo systemctl daemon-reload
sudo systemctl enable linkshortener

echo "✅ Backend deployment setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Copy and configure environment variables:"
echo "   cp $APP_DIR/.env.example $APP_DIR/.env"
echo "   nano $APP_DIR/.env"
echo ""
echo "2. Configure your existing nginx to proxy to port 8000:"
echo "   - Review the template: cat $APP_DIR/nginx-integration.conf"
echo "   - Add the configuration to your existing nginx setup"
echo "   - Test: sudo nginx -t"
echo "   - Reload: sudo systemctl reload nginx"
echo ""
echo "3. Start the backend service:"
echo "   cd $APP_DIR && docker-compose up -d"
echo ""
echo "4. Verify the integration:"
echo "   cd $APP_DIR && ./verify-integration.sh"
echo ""
echo "5. Check status:"
echo "   cd $APP_DIR && ./manage.sh status"
echo ""
echo "🌐 Backend will be available at: http://localhost:8000"
echo "🔗 Configure your nginx to proxy links.miskakyto.fi to port 8000"
echo "📁 All files are in: $APP_DIR"
