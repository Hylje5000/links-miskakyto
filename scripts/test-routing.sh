#!/bin/bash

echo "🔍 Testing URL Shortener Routing"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test functions
test_endpoint() {
    local url=$1
    local description=$2
    local expected_status=${3:-200}
    
    echo -n "Testing $description: "
    
    if command -v curl >/dev/null 2>&1; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
        if [ "$response" = "$expected_status" ]; then
            echo -e "${GREEN}✅ $response${NC}"
            return 0
        else
            echo -e "${RED}❌ $response (expected $expected_status)${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  curl not available${NC}"
        return 1
    fi
}

test_with_content() {
    local url=$1
    local description=$2
    local expected_content=$3
    
    echo -n "Testing $description: "
    
    if command -v curl >/dev/null 2>&1; then
        response=$(curl -s "$url" 2>/dev/null)
        if echo "$response" | grep -q "$expected_content"; then
            echo -e "${GREEN}✅ Contains '$expected_content'${NC}"
            return 0
        else
            echo -e "${RED}❌ Missing '$expected_content'${NC}"
            echo "   Response: $response"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  curl not available${NC}"
        return 1
    fi
}

echo ""
echo "1. Direct Backend Tests (port 8000)"
echo "-----------------------------------"
test_with_content "http://localhost:8000/" "Root endpoint" "Link Shortener API"
test_with_content "http://localhost:8000/api/health" "Health endpoint" "healthy"

echo ""
echo "2. Through Docker Nginx (port 8080)"
echo "-----------------------------------"
test_with_content "http://localhost:8080/" "Frontend root" "<!DOCTYPE html"
test_with_content "http://localhost:8080/api/health" "API health" "healthy"

echo ""
echo "3. API Endpoints (through nginx)"
echo "-------------------------------"
test_endpoint "http://localhost:8080/api/links" "GET /api/links" 401  # Should require auth

echo ""
echo "4. Production URLs (if deployed)"
echo "-------------------------------"
test_with_content "https://links.miskakyto.fi/api/health" "Production health" "healthy"
test_endpoint "https://links.miskakyto.fi/api/links" "Production API" 401  # Should require auth

echo ""
echo "5. Short URL Test (6-character codes)"
echo "------------------------------------"
test_endpoint "http://localhost:8080/abc123" "Short URL" 404  # Should 404 for non-existent link
test_endpoint "http://localhost:8080/health" "Removed /health" 404  # Should 404 now

echo ""
echo "🔍 Routing Test Complete"
echo ""
echo "Expected results:"
echo "✅ /api/health should return 200 with 'healthy' status"
echo "✅ /api/links should return 401 (authentication required)"
echo "❌ /health should return 404 (removed endpoint)"
echo "✅ 6-char codes should return 404 for non-existent links"
echo "✅ Frontend root should return HTML"
