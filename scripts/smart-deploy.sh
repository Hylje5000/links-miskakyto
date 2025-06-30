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

# Get the last deployment commit (or use last 1 commit if file doesn't exist)
LAST_DEPLOYMENT_FILE="$HOME/.linkshortener_last_deployment"
if [ -f "$LAST_DEPLOYMENT_FILE" ]; then
    LAST_COMMIT=$(cat "$LAST_DEPLOYMENT_FILE")
    print_info "📋 Last deployment commit: $LAST_COMMIT"
    
    # Verify the commit exists
    if ! git cat-file -e "$LAST_COMMIT" 2>/dev/null; then
        print_error "⚠️ Stored commit $LAST_COMMIT doesn't exist, falling back to HEAD~1"
        LAST_COMMIT=$(git rev-parse HEAD~1)
    fi
else
    # If no previous deployment, check last 1 commit (not 5!)
    LAST_COMMIT=$(git rev-parse HEAD~1)
    print_info "📋 No previous deployment found, checking last 1 commit: $LAST_COMMIT"
fi

CURRENT_COMMIT=$(git rev-parse HEAD)

# Function to check if a path has changes
has_changes() {
    local path=$1
    local last_commit="$LAST_COMMIT"
    local current_commit="$CURRENT_COMMIT"
    
    # Debug output for troubleshooting
    # print_info "Checking changes in: $path (from $last_commit to $current_commit)"
    
    git diff --quiet "$last_commit" "$current_commit" -- "$path" 2>/dev/null
    local result=$?
    
    # More explicit debugging
    if [ $result -eq 0 ]; then
        # No changes (return 1 = false in bash if conditions)
        return 1
    elif [ $result -eq 1 ]; then
        # Has changes (return 0 = true in bash if conditions)  
        return 0
    else
        # Error case (treat as no changes to be safe)
        print_error "⚠️ Error checking changes for $path (exit code: $result)"
        return 1
    fi
}

# Check what needs rebuilding
REBUILD_BACKEND=false
REBUILD_FRONTEND=false
REBUILD_NGINX=false

print_status "🔍 Analyzing changes..."
print_info "Comparing $LAST_COMMIT -> $CURRENT_COMMIT"

# Show what files actually changed
CHANGED_FILES=$(git diff --name-only "$LAST_COMMIT" "$CURRENT_COMMIT" 2>/dev/null || echo "Error getting changed files")
print_info "Changed files: $CHANGED_FILES"

# Check backend changes
if has_changes "backend/" || has_changes "requirements.txt"; then
    REBUILD_BACKEND=true
    print_info "🔄 Backend changes detected"
    # Show specific backend changes
    BACKEND_CHANGES=$(git diff --name-only "$LAST_COMMIT" "$CURRENT_COMMIT" -- backend/ requirements.txt 2>/dev/null || echo "none")
    print_info "   Backend files changed: $BACKEND_CHANGES"
else
    print_success "✅ Backend unchanged"
fi

# Check frontend changes
if has_changes "src/" || has_changes "package.json" || has_changes "package-lock.json" || has_changes "next.config.js" || has_changes "tailwind.config.js"; then
    REBUILD_FRONTEND=true
    print_info "🔄 Frontend changes detected"
    # Show specific frontend changes
    FRONTEND_CHANGES=$(git diff --name-only "$LAST_COMMIT" "$CURRENT_COMMIT" -- src/ package.json package-lock.json next.config.js tailwind.config.js 2>/dev/null || echo "none")
    print_info "   Frontend files changed: $FRONTEND_CHANGES"
else
    print_success "✅ Frontend unchanged"
fi

# Check nginx changes
if has_changes "docker/nginx-docker.conf" || has_changes "docker/Dockerfile.nginx"; then
    REBUILD_NGINX=true
    print_info "🔄 Nginx changes detected"
    # Show specific nginx changes
    NGINX_CHANGES=$(git diff --name-only "$LAST_COMMIT" "$CURRENT_COMMIT" -- docker/nginx-docker.conf docker/Dockerfile.nginx 2>/dev/null || echo "none")
    print_info "   Nginx files changed: $NGINX_CHANGES"
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
