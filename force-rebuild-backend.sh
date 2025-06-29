#!/bin/bash

echo "🔧 Force Backend Rebuild Script"
echo "==============================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to print status
print_status() {
    echo -e "${YELLOW}$1${NC}"
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

# Check if we're in the right directory
if [ ! -f "docker-compose.fullstack.yml" ]; then
    print_error "❌ docker-compose.fullstack.yml not found. Please run from the project root."
    exit 1
fi

print_status "🛑 Stopping all containers..."
./manage-fullstack.sh stop

print_status "🗑️  Removing old backend image..."
docker rmi linkshortener-linkshortener-backend:latest 2>/dev/null || true

print_status "🔨 Rebuilding backend container from scratch (no cache)..."
docker-compose -f docker-compose.fullstack.yml build --no-cache linkshortener-backend

print_status "🚀 Starting all containers..."
./manage-fullstack.sh start

print_status "⏱️  Waiting 30 seconds for containers to fully start..."
sleep 30

print_status "🧪 Testing endpoints..."

echo ""
echo "1. Testing backend directly:"
if docker-compose -f docker-compose.fullstack.yml exec -T linkshortener-backend curl -s http://localhost:8000/api/health > /dev/null; then
    print_success "✅ Backend /api/health works directly"
else
    print_error "❌ Backend /api/health still fails directly"
fi

echo ""
echo "2. Testing through nginx:"
if curl -s http://localhost:8080/api/health > /dev/null; then
    print_success "✅ Nginx routing to /api/health works"
    echo "Response:"
    curl -s http://localhost:8080/api/health | head -3
else
    print_error "❌ Nginx routing to /api/health still fails"
fi

echo ""
echo "3. Testing debug endpoint:"
if curl -s http://localhost:8080/debug/routes > /dev/null; then
    print_success "✅ Debug endpoint available"
    echo "Available endpoints:"
    curl -s http://localhost:8080/debug/routes | grep -o '"GET [^"]*"' | head -10
else
    print_error "❌ Debug endpoint not available"
fi

echo ""
print_status "🏁 Rebuild complete!"
echo ""
echo "If /api/health still returns 404:"
echo "1. Check GitHub Actions deployment logs"
echo "2. Verify the latest code was pulled: git log --oneline -3"
echo "3. Try manual pull: git pull origin main"
echo "4. Run this script again"
