#!/bin/bash

# Management script for Link Shortener backend-only deployment
# Use this when deploying alongside existing web services

set -e

APP_DIR="/opt/linkshortener"
COMPOSE_FILE="$APP_DIR/docker-compose.yml"

case "$1" in
    status)
        echo "🔍 Checking Link Shortener backend status..."
        cd $APP_DIR
        docker-compose ps
        echo ""
        echo "🌐 Testing backend health..."
        curl -s http://localhost:8000/api/health && echo "✅ Backend is healthy" || echo "❌ Backend is not responding"
        ;;
    
    start)
        echo "🚀 Starting Link Shortener backend..."
        cd $APP_DIR
        docker-compose up -d
        echo "✅ Backend started"
        ;;
    
    stop)
        echo "🛑 Stopping Link Shortener backend..."
        cd $APP_DIR
        docker-compose down
        echo "✅ Backend stopped"
        ;;
    
    restart)
        echo "🔄 Restarting Link Shortener backend..."
        cd $APP_DIR
        docker-compose down
        docker-compose up -d
        echo "✅ Backend restarted"
        ;;
    
    logs)
        echo "📋 Showing backend logs..."
        cd $APP_DIR
        docker-compose logs -f linkshortener-backend
        ;;
    
    update)
        echo "🔄 Updating Link Shortener from git..."
        cd $APP_DIR
        git pull
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
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
    
    health)
        echo "🏥 Performing health checks..."
        echo "Backend service:"
        curl -s http://localhost:8000/api/health | jq . || echo "❌ Backend not responding"
        echo ""
        echo "Container status:"
        cd $APP_DIR
        docker-compose ps
        ;;
    
    shell)
        echo "🐚 Opening shell in backend container..."
        cd $APP_DIR
        docker-compose exec linkshortener-backend /bin/bash
        ;;
    
    *)
        echo "Link Shortener Backend Management"
        echo ""
        echo "Usage: $0 {status|start|stop|restart|logs|update|backup|health|shell}"
        echo ""
        echo "Commands:"
        echo "  status   - Show service status and health"
        echo "  start    - Start the backend service"
        echo "  stop     - Stop the backend service"
        echo "  restart  - Restart the backend service"
        echo "  logs     - Show and follow backend logs"
        echo "  update   - Update from git and rebuild"
        echo "  backup   - Backup the database"
        echo "  health   - Perform detailed health checks"
        echo "  shell    - Open shell in backend container"
        echo ""
        echo "📁 Application directory: $APP_DIR"
        echo "🐳 Docker compose file: $COMPOSE_FILE"
        exit 1
        ;;
esac
