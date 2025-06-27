#!/bin/bash
# Deploy script for Azure VM

set -e

echo "🚀 Deploying Link Shortener Backend to Azure VM..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "Please log out and back in to use Docker without sudo"
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create application directory
sudo mkdir -p /opt/linkshortener
cd /opt/linkshortener

# Download or copy your application files here
# git clone your-repo-url .

# Create data directory
mkdir -p data

# Copy environment file
if [ ! -f ".env" ]; then
    cp backend/.env.production .env
    echo "⚠️  Please edit .env file with your configuration!"
fi

# Build and start containers
docker-compose down
docker-compose build
docker-compose up -d

echo "✅ Deployment complete!"
echo "Backend API: http://$(curl -s ifconfig.me):8000"
echo "Health check: curl http://$(curl -s ifconfig.me):8000/"

# Show logs
echo "📋 Recent logs:"
docker-compose logs --tail=50
