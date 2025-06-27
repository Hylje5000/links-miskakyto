#!/bin/bash
# Production management script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function show_status() {
    echo -e "${GREEN}📊 Container Status:${NC}"
    docker-compose ps
    echo ""
    echo -e "${GREEN}📋 Recent Logs:${NC}"
    docker-compose logs --tail=20
}

function restart_service() {
    echo -e "${YELLOW}🔄 Restarting services...${NC}"
    docker-compose restart
    echo -e "${GREEN}✅ Services restarted${NC}"
}

function update_service() {
    echo -e "${YELLOW}📥 Updating services...${NC}"
    git pull
    docker-compose build
    docker-compose up -d
    echo -e "${GREEN}✅ Services updated${NC}"
}

function backup_database() {
    echo -e "${YELLOW}💾 Creating database backup...${NC}"
    timestamp=$(date +%Y%m%d_%H%M%S)
    cp data/links.db "backups/links_backup_${timestamp}.db"
    echo -e "${GREEN}✅ Backup created: backups/links_backup_${timestamp}.db${NC}"
}

function show_logs() {
    docker-compose logs -f
}

function stop_service() {
    echo -e "${YELLOW}⏹️  Stopping services...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Services stopped${NC}"
}

function start_service() {
    echo -e "${YELLOW}▶️  Starting services...${NC}"
    docker-compose up -d
    echo -e "${GREEN}✅ Services started${NC}"
}

case "$1" in
    status)
        show_status
        ;;
    restart)
        restart_service
        ;;
    update)
        update_service
        ;;
    backup)
        mkdir -p backups
        backup_database
        ;;
    logs)
        show_logs
        ;;
    stop)
        stop_service
        ;;
    start)
        start_service
        ;;
    *)
        echo "Usage: $0 {status|restart|update|backup|logs|stop|start}"
        echo ""
        echo "Commands:"
        echo "  status  - Show service status and recent logs"
        echo "  restart - Restart all services"
        echo "  update  - Pull latest code and rebuild"
        echo "  backup  - Create database backup"
        echo "  logs    - Follow live logs"
        echo "  stop    - Stop all services"
        echo "  start   - Start all services"
        exit 1
        ;;
esac
