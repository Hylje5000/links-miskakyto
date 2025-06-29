#!/bin/bash

# Smart deployment script that only rebuilds changed components
set -e

echo "🔍 Smart Deployment - Detecting Changes"
echo "======================================="

# Load environment variables from .env file at the start
if [ -f .env ]; then
    echo "📋 Loading environment variables from .env"
    set -a  # automatically export all variables
    source .env
    set +a  # stop automatically exporting
else
    echo "⚠️ No .env file found, using defaults"
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${YELLOW}$1${NC}"; }
print_success() { echo -e "${GREEN}$1${NC}"; }
print_info() { echo -e "${BLUE}$1${NC}"; }
print_error() { echo -e "${RED}$1${NC}"; }

# Get the last deployment commit (or use last 5 commits if file doesn't exist)
LAST_DEPLOYMENT_FILE="/tmp/last_deployment_commit"
if [ -f "$LAST_DEPLOYMENT_FILE" ]; then
    LAST_COMMIT=$(cat "$LAST_DEPLOYMENT_FILE")
    print_info "📋 Last deployment commit: $LAST_COMMIT"
else
    # If no previous deployment, check last 5 commits to be safe
    LAST_COMMIT=$(git rev-parse HEAD~5)
    print_info "📋 No previous deployment found, checking last 5 commits"
fi

CURRENT_COMMIT=$(git rev-parse HEAD)

# Function to check if a path has changes
has_changes() {
    local path=$1
    git diff --quiet "$LAST_COMMIT" "$CURRENT_COMMIT" -- "$path" 2>/dev/null
    return $?
}

# Check what needs rebuilding
REBUILD_BACKEND=false
REBUILD_FRONTEND=false
REBUILD_NGINX=false

print_status "🔍 Analyzing changes..."

# Check backend changes
if has_changes "backend/" || has_changes "requirements.txt"; then
    REBUILD_BACKEND=true
    print_info "🔄 Backend changes detected"
else
    print_success "✅ Backend unchanged"
fi

# Check frontend changes
if has_changes "src/" || has_changes "package.json" || has_changes "package-lock.json" || has_changes "next.config.js" || has_changes "tailwind.config.js"; then
    REBUILD_FRONTEND=true
    print_info "🔄 Frontend changes detected"
else
    print_success "✅ Frontend unchanged"
fi

# Check nginx changes
if has_changes "docker/nginx-docker.conf" || has_changes "docker/Dockerfile.nginx"; then
    REBUILD_NGINX=true
    print_info "🔄 Nginx changes detected"
else
    print_success "✅ Nginx unchanged"
fi

# If nothing changed, check if containers are running
if [ "$REBUILD_BACKEND" = false ] && [ "$REBUILD_FRONTEND" = false ] && [ "$REBUILD_NGINX" = false ]; then
    print_success "🎉 No changes detected!"
    
    # Check if containers are running
    if docker-compose -f docker/docker-compose.fullstack.yml ps | grep -q "Up"; then
        print_success "✅ Containers are already running"
        print_info "🧪 Running health check..."
        
        if curl -s http://localhost:8080/api/health > /dev/null; then
            print_success "✅ Application is healthy"
            exit 0
        else
            print_error "❌ Application health check failed, forcing rebuild"
            REBUILD_BACKEND=true
            REBUILD_FRONTEND=true
            REBUILD_NGINX=true
        fi
    else
        print_info "🚀 Containers not running, starting existing images..."
        docker-compose -f docker/docker-compose.fullstack.yml up -d
        sleep 30
        
        if curl -s http://localhost:8080/api/health > /dev/null; then
            print_success "✅ Application started successfully"
            exit 0
        else
            print_error "❌ Failed to start, rebuilding..."
            REBUILD_BACKEND=true
            REBUILD_FRONTEND=true
            REBUILD_NGINX=true
        fi
    fi
fi

# Stop containers before rebuilding
print_status "🛑 Stopping containers..."
docker-compose -f docker/docker-compose.fullstack.yml down

# Selective rebuild
BUILD_ARGS=""

if [ "$REBUILD_BACKEND" = true ]; then
    print_status "🔨 Rebuilding backend..."
    BUILD_ARGS="$BUILD_ARGS linkshortener-backend"
fi

if [ "$REBUILD_FRONTEND" = true ]; then
    print_status "🔨 Rebuilding frontend..."
    BUILD_ARGS="$BUILD_ARGS linkshortener-frontend"
fi

if [ "$REBUILD_NGINX" = true ]; then
    print_status "🔨 Rebuilding nginx..."
    BUILD_ARGS="$BUILD_ARGS linkshortener-nginx"
fi

# Set cache-busting environment variables for changed components
export BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
export VCS_REF=$CURRENT_COMMIT

if [ -n "$BUILD_ARGS" ]; then
    print_status "🔨 Building changed services: $BUILD_ARGS"
    docker-compose -f docker/docker-compose.fullstack.yml build $BUILD_ARGS
fi

# Start all containers
print_status "🚀 Starting containers..."
docker-compose -f docker/docker-compose.fullstack.yml up -d

# Wait for startup
print_status "⏱️  Waiting for services to start..."
sleep 30

# Health check
print_status "🧪 Running health checks..."

# Test backend health
if curl -s http://localhost:8080/api/health > /dev/null; then
    print_success "✅ Backend health check passed"
else
    print_error "❌ Backend health check failed"
    exit 1
fi

# Test frontend
if curl -s http://localhost:8080/ | grep -q "<!DOCTYPE html"; then
    print_success "✅ Frontend health check passed"
else
    print_error "❌ Frontend health check failed"
    exit 1
fi

# Save current commit as last deployment
echo "$CURRENT_COMMIT" > "$LAST_DEPLOYMENT_FILE"

print_success "🎉 Smart deployment completed successfully!"
print_info "📊 Deployment summary:"
print_info "   Backend rebuilt: $REBUILD_BACKEND"
print_info "   Frontend rebuilt: $REBUILD_FRONTEND"
print_info "   Nginx rebuilt: $REBUILD_NGINX"
print_info "   Commit: $CURRENT_COMMIT"
