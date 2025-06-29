#!/bin/bash

# LinkShortener Docker Management Script
# Usage: ./manage-fullstack.sh [start|stop|restart|status|logs|update]

set -e

COMPOSE_FILE="docker/docker-compose.fullstack.yml"
PROJECT_NAME="linkshortener"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Docker and Docker Compose are available
check_dependencies() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
}

# Check if environment file exists
check_env() {
    if [ ! -f ".env" ]; then
        print_warning "No .env file found. Creating from template..."
        if [ -f "backend/.env.production" ]; then
            cp backend/.env.production .env
            print_warning "Please edit .env file with your actual values before starting services"
        else
            print_error "No environment template found. Please create .env file manually."
            exit 1
        fi
    fi
}

# Start services
start_services() {
    print_status "Starting LinkShortener services..."
    check_env
    
    # Create data directory if it doesn't exist
    mkdir -p data
    
    # Load environment variables
    if [ -f .env ]; then
        set -a
        source .env
        set +a
    fi
    
    # Build and start containers (always pull latest and rebuild)
    export BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
    export VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d --build
    
    if [ $? -eq 0 ]; then
        print_success "Services started successfully!"
        print_status "Frontend: http://localhost:8080"
        print_status "Backend API: http://localhost:8080/api"
        print_status "Health check: http://localhost:8080/api/health"
    else
        print_error "Failed to start services"
        exit 1
    fi
}

# Stop services
stop_services() {
    print_status "Stopping LinkShortener services..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down
    
    if [ $? -eq 0 ]; then
        print_success "Services stopped successfully!"
    else
        print_error "Failed to stop services"
        exit 1
    fi
}

# Restart services
restart_services() {
    print_status "Restarting LinkShortener services..."
    stop_services
    sleep 2
    start_services
}

# Force rebuild services (clean rebuild)
rebuild_services() {
    print_status "Force rebuilding LinkShortener services..."
    check_env
    
    # Stop and remove everything
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down --rmi local --volumes --remove-orphans 2>/dev/null || true
    
    # Remove dangling images
    docker image prune -f
    
    # Load environment variables
    if [ -f .env ]; then
        set -a
        source .env
        set +a
    fi
    
    # Set build variables
    export BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
    export VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    
    print_status "Building containers from scratch (no cache)..."
    
    # Create data directory if it doesn't exist
    mkdir -p data
    
    # Build and start with no cache
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" build --no-cache
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d
    
    if [ $? -eq 0 ]; then
        print_success "Services rebuilt and started successfully!"
        print_status "Frontend: http://localhost:8080"
        print_status "Backend API: http://localhost:8080/api"
        print_status "Health check: http://localhost:8080/api/health"
        
        print_status "Waiting for services to be ready..."
        sleep 10
        
        # Test health endpoint
        if curl -f -s http://localhost:8080/api/health > /dev/null; then
            print_success "Health check passed!"
        else
            print_error "Health check failed - services may need more time to start"
        fi
    else
        print_error "Failed to rebuild services"
        exit 1
    fi
}

# Show service status
show_status() {
    print_status "LinkShortener service status:"
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps
}

# Show logs
show_logs() {
    SERVICE=${2:-""}
    if [ -n "$SERVICE" ]; then
        print_status "Showing logs for $SERVICE..."
        docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f "$SERVICE"
    else
        print_status "Showing logs for all services..."
        docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f
    fi
}

# Update and restart services
update_services() {
    print_status "Updating LinkShortener services..."
    
    # Pull latest images
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" pull
    
    # Rebuild and restart
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d --build
    
    if [ $? -eq 0 ]; then
        print_success "Services updated successfully!"
    else
        print_error "Failed to update services"
        exit 1
    fi
}

# Health check
health_check() {
    print_status "Performing health check..."
    
    # Check if containers are running
    if ! docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps | grep -q "Up"; then
        print_error "No services are running"
        return 1
    fi
    
    # Check backend health endpoint
    if curl -f -s http://localhost:8080/api/health > /dev/null; then
        print_success "Backend health check passed"
    else
        print_error "Backend health check failed"
        return 1
    fi
    
    # Check frontend
    if curl -f -s http://localhost:8080/ > /dev/null; then
        print_success "Frontend health check passed"
    else
        print_error "Frontend health check failed"
        return 1
    fi
    
    print_success "All health checks passed!"
}

# Cleanup (remove containers, networks, volumes)
cleanup() {
    print_status "Cleaning up LinkShortener resources..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down -v --remove-orphans
    
    # Remove unused images
    print_status "Removing unused Docker images..."
    docker image prune -f
    
    print_success "Cleanup completed!"
}

# Show usage
show_usage() {
    echo "LinkShortener Docker Management Script"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  start           Start all services"
    echo "  stop            Stop all services"
    echo "  restart         Restart all services"
    echo "  rebuild         Force rebuild all containers (clean build)"
    echo "  status          Show service status"
    echo "  logs [service]  Show logs (optionally for specific service)"
    echo "  update          Update and restart services"
    echo "  health          Perform health check"
    echo "  cleanup         Stop services and remove all resources"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Start all services"
    echo "  $0 rebuild                  # Force clean rebuild (fixes cache issues)"
    echo "  $0 logs                     # Show all logs"
    echo "  $0 logs backend             # Show backend logs only"
    echo "  $0 status                   # Show service status"
}

# Main script logic
main() {
    check_dependencies
    
    case "${1:-help}" in
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        rebuild)
            rebuild_services
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "$@"
            ;;
        update)
            update_services
            ;;
        health)
            health_check
            ;;
        cleanup)
            cleanup
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
