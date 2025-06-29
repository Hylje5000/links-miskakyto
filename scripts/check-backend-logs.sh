#!/bin/bash

# Script to check backend logs and debug authentication issues

echo "🔍 Backend Log Checker & Authentication Debugger"
echo "================================================="

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

# Check if containers are running
print_status "📋 Checking container status..."
BACKEND_CONTAINER=$(docker-compose -f docker/docker-compose.fullstack.yml ps -q linkshortener-backend)

if [ -z "$BACKEND_CONTAINER" ]; then
    print_error "❌ Backend container not found or not running"
    echo "💡 Start the application with: ./scripts/smart-deploy.sh"
    exit 1
fi

print_success "✅ Backend container found: $BACKEND_CONTAINER"

# Function to show logs
show_logs() {
    local lines=${1:-50}
    print_status "📄 Showing last $lines lines of backend logs..."
    docker-compose -f docker/docker-compose.fullstack.yml logs --tail=$lines linkshortener-backend
}

# Function to follow logs in real-time
follow_logs() {
    print_status "📡 Following backend logs in real-time (Ctrl+C to exit)..."
    docker-compose -f docker/docker-compose.fullstack.yml logs -f linkshortener-backend
}

# Function to test authentication endpoints
test_auth_endpoints() {
    print_status "🔑 Testing authentication debug endpoints..."
    
    # Test health endpoint first
    print_info "Testing health endpoint..."
    if curl -s http://localhost:8080/api/health > /dev/null; then
        print_success "✅ Health endpoint accessible"
    else
        print_error "❌ Health endpoint not accessible"
        return 1
    fi
    
    # Test auth status endpoint
    print_info "Testing auth status endpoint..."
    AUTH_STATUS=$(curl -s http://localhost:8080/api/debug/auth-status 2>/dev/null)
    if [ $? -eq 0 ]; then
        print_success "✅ Auth status endpoint accessible"
        echo "$AUTH_STATUS" | jq '.' 2>/dev/null || echo "$AUTH_STATUS"
    else
        print_error "❌ Auth status endpoint not accessible"
    fi
    
    # Test auth config endpoint  
    print_info "Testing auth config endpoint..."
    AUTH_CONFIG=$(curl -s http://localhost:8080/api/debug/auth-config 2>/dev/null)
    if [ $? -eq 0 ]; then
        print_success "✅ Auth config endpoint accessible"
        echo "$AUTH_CONFIG" | jq '.' 2>/dev/null || echo "$AUTH_CONFIG"
    else
        print_error "❌ Auth config endpoint not accessible"
    fi
}

# Function to search for authentication errors in logs
search_auth_errors() {
    print_status "🔍 Searching for authentication errors in logs..."
    
    print_info "Looking for JWT/token errors..."
    docker-compose -f docker/docker-compose.fullstack.yml logs linkshortener-backend 2>/dev/null | grep -i -E "(jwt|token|auth|401|403|unauthorized)" | tail -20
    
    print_info "Looking for validation errors..."
    docker-compose -f docker/docker-compose.fullstack.yml logs linkshortener-backend 2>/dev/null | grep -i -E "(validation|invalid|error|exception)" | tail -20
}

# Function to check environment variables
check_env_vars() {
    print_status "🔧 Checking environment variables in container..."
    docker exec $BACKEND_CONTAINER env | grep -E "(AZURE|AUTH|TEST_MODE|PRODUCTION)" | sort
}

# Main menu
while true; do
    echo ""
    print_info "Select an option:"
    echo "1. Show recent logs (last 50 lines)"
    echo "2. Show more logs (last 200 lines)"  
    echo "3. Follow logs in real-time"
    echo "4. Test authentication endpoints"
    echo "5. Search for authentication errors"
    echo "6. Check environment variables"
    echo "7. All of the above (comprehensive check)"
    echo "0. Exit"
    
    read -p "Enter choice [0-7]: " choice
    
    case $choice in
        1)
            show_logs 50
            ;;
        2)
            show_logs 200
            ;;
        3)
            follow_logs
            ;;
        4)
            test_auth_endpoints
            ;;
        5)
            search_auth_errors
            ;;
        6)
            check_env_vars
            ;;
        7)
            print_status "🔍 Running comprehensive check..."
            show_logs 100
            echo ""
            test_auth_endpoints
            echo ""
            search_auth_errors
            echo ""
            check_env_vars
            ;;
        0)
            print_success "👋 Goodbye!"
            exit 0
            ;;
        *)
            print_error "❌ Invalid option. Please enter 0-7."
            ;;
    esac
done
