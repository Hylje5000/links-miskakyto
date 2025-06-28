#!/bin/bash

# Complete Docker deployment for Link Shortener (Frontend + Backend)
# This deploys everything in Docker containers on your VM

set -e

echo "🚀 Deploying Complete Link Shortener Stack with Docker..."

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

# Copy all necessary files
echo "📋 Setting up configuration..."
sudo cp -r . $APP_DIR/
sudo chown -R $USER:$USER $APP_DIR

# Create environment file if it doesn't exist
ENV_FILE="$APP_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "⚙️  Creating environment file..."
    cat > $ENV_FILE <<EOF
# Azure AD Configuration
AZURE_TENANT_ID=your-tenant-id-here
AZURE_CLIENT_ID=your-client-id-here

# Application Configuration
BASE_URL=https://links.miskakyto.fi
ALLOWED_ORIGINS=https://links.miskakyto.fi

# Database Configuration
DATABASE_URL=sqlite:///data/links.db

# Security
SECRET_KEY=$(openssl rand -hex 32)

# Frontend Environment Variables
NEXT_PUBLIC_API_URL=https://links.miskakyto.fi
NEXT_PUBLIC_AZURE_CLIENT_ID=your-client-id-here
NEXT_PUBLIC_AZURE_TENANT_ID=your-tenant-id-here
NEXT_PUBLIC_REDIRECT_URI=https://links.miskakyto.fi
EOF

    echo "📝 Environment file created at: $ENV_FILE"
    echo "⚠️  Please edit this file with your Azure AD credentials:"
    echo "   nano $ENV_FILE"
    echo ""
    read -p "Press Enter after you've configured the environment file..."
fi

# Create systemd service for auto-start
echo "⚙️  Creating systemd service..."
sudo tee /etc/systemd/system/linkshortener-fullstack.service > /dev/null <<EOF
[Unit]
Description=Link Shortener Full Stack (Frontend + Backend)
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$APP_DIR
ExecStart=/usr/local/bin/docker-compose -f docker-compose.fullstack.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.fullstack.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Enable the service
sudo systemctl daemon-reload
sudo systemctl enable linkshortener-fullstack

# Create management script
cat > $APP_DIR/manage-fullstack.sh <<'EOF'
#!/bin/bash

# Management script for Link Shortener Full Stack deployment

set -e

APP_DIR="/opt/linkshortener"
COMPOSE_FILE="$APP_DIR/docker-compose.fullstack.yml"

case "$1" in
    status)
        echo "🔍 Checking Link Shortener full stack status..."
        cd $APP_DIR
        docker-compose -f docker-compose.fullstack.yml ps
        echo ""
        echo "🌐 Testing services..."
        curl -s http://localhost:8080/health && echo "✅ Backend is healthy" || echo "❌ Backend is not responding"
        curl -s -I http://localhost:8080 && echo "✅ Frontend is accessible" || echo "❌ Frontend is not responding"
        ;;
    
    start)
        echo "🚀 Starting Link Shortener full stack..."
        cd $APP_DIR
        docker-compose -f docker-compose.fullstack.yml up -d
        echo "✅ Full stack started"
        ;;
    
    stop)
        echo "🛑 Stopping Link Shortener full stack..."
        cd $APP_DIR
        docker-compose -f docker-compose.fullstack.yml down
        echo "✅ Full stack stopped"
        ;;
    
    restart)
        echo "🔄 Restarting Link Shortener full stack..."
        cd $APP_DIR
        docker-compose -f docker-compose.fullstack.yml down
        docker-compose -f docker-compose.fullstack.yml up -d
        echo "✅ Full stack restarted"
        ;;
    
    logs)
        echo "📋 Showing full stack logs..."
        cd $APP_DIR
        docker-compose -f docker-compose.fullstack.yml logs -f
        ;;
    
    logs-backend)
        echo "📋 Showing backend logs..."
        cd $APP_DIR
        docker-compose -f docker-compose.fullstack.yml logs -f linkshortener-backend
        ;;
    
    logs-frontend)
        echo "📋 Showing frontend logs..."
        cd $APP_DIR
        docker-compose -f docker-compose.fullstack.yml logs -f linkshortener-frontend
        ;;
    
    logs-nginx)
        echo "📋 Showing nginx logs..."
        cd $APP_DIR
        docker-compose -f docker-compose.fullstack.yml logs -f linkshortener-nginx
        ;;
    
    update)
        echo "🔄 Updating Link Shortener from git..."
        cd $APP_DIR
        git pull
        docker-compose -f docker-compose.fullstack.yml down
        docker-compose -f docker-compose.fullstack.yml build --no-cache
        docker-compose -f docker-compose.fullstack.yml up -d
        echo "✅ Update complete"
        ;;
    
    backup)
        echo "💾 Backing up database..."
        BACKUP_DIR="$APP_DIR/backups"
        mkdir -p $BACKUP_DIR
        BACKUP_FILE="$BACKUP_DIR/links_$(date +%Y%m%d_%H%M%S).db"
        cp $APP_DIR/data/links.db $BACKUP_FILE
        echo "✅ Database backed up to: $BACKUP_FILE"
        
        # Keep only last 7 backups
        find $BACKUP_DIR -name "links_*.db" -type f -mtime +7 -delete
        ;;
    
    build)
        echo "🏗️ Building containers..."
        cd $APP_DIR
        docker-compose -f docker-compose.fullstack.yml build
        ;;
    
    *)
        echo "Link Shortener Full Stack Management"
        echo ""
        echo "Usage: $0 {status|start|stop|restart|logs|logs-backend|logs-frontend|logs-nginx|update|backup|build}"
        echo ""
        echo "Commands:"
        echo "  status        - Show service status and health"
        echo "  start         - Start all services"
        echo "  stop          - Stop all services"
        echo "  restart       - Restart all services"
        echo "  logs          - Show and follow all logs"
        echo "  logs-backend  - Show backend logs only"
        echo "  logs-frontend - Show frontend logs only"
        echo "  logs-nginx    - Show nginx logs only"
        echo "  update        - Update from git and rebuild"
        echo "  backup        - Backup the database"
        echo "  build         - Build containers"
        echo ""
        echo "📁 Application directory: $APP_DIR"
        echo "🐳 Docker compose file: $COMPOSE_FILE"
        echo "🌐 Application available at: http://localhost:8080"
        exit 1
        ;;
esac
EOF

chmod +x $APP_DIR/manage-fullstack.sh

echo "✅ Full stack deployment setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Configure your environment variables (if not done already):"
echo "   nano $APP_DIR/.env"
echo ""
echo "2. Build and start the services:"
echo "   cd $APP_DIR && ./manage-fullstack.sh build"
echo "   cd $APP_DIR && ./manage-fullstack.sh start"
echo ""
echo "3. Configure your existing nginx to proxy to port 8080:"
echo "   location / {"
echo "       proxy_pass http://127.0.0.1:8080;"
echo "       proxy_set_header Host \$host;"
echo "       proxy_set_header X-Real-IP \$remote_addr;"
echo "       proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;"
echo "       proxy_set_header X-Forwarded-Proto \$scheme;"
echo "   }"
echo ""
echo "4. Check status:"
echo "   cd $APP_DIR && ./manage-fullstack.sh status"
echo ""
echo "🌐 Application will be available at: http://localhost:8080"
echo "🔗 Configure your nginx to proxy links.miskakyto.fi to port 8080"
echo "📁 All files are in: $APP_DIR"
