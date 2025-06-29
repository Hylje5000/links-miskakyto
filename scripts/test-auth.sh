#!/bin/bash

# Test script to verify Azure AD token acquisition and API access

echo "🧪 Testing Azure AD authentication and API access..."

# Check if both services are running
echo "🔍 Checking services..."

if ! curl -s http://localhost:8000/api/health > /dev/null; then
    echo "❌ Backend not running on localhost:8000"
    echo "💡 Start with: cd backend && uvicorn main:app --reload"
    exit 1
fi

if ! curl -s http://localhost:3000 > /dev/null; then
    echo "❌ Frontend not running on localhost:3000"
    echo "💡 Start with: npm run dev"
    exit 1
fi

echo "✅ Both services are running"

# Check auth configuration
echo -e "\n🔑 Checking authentication configuration..."
AUTH_DEBUG=$(curl -s http://localhost:8000/api/debug/auth)
echo "$AUTH_DEBUG" | jq '.' 2>/dev/null || echo "$AUTH_DEBUG"

# Test anonymous API access (should fail with 401)
echo -e "\n🚫 Testing anonymous API access (should return 401)..."
RESPONSE=$(curl -s -w "HTTP_STATUS:%{http_code}" http://localhost:8000/api/links)
HTTP_STATUS=$(echo "$RESPONSE" | grep -o "HTTP_STATUS:.*" | cut -d: -f2)

if [ "$HTTP_STATUS" = "401" ]; then
    echo "✅ Anonymous access correctly blocked (401)"
else
    echo "❌ Expected 401, got $HTTP_STATUS"
    echo "$RESPONSE" | sed 's/HTTP_STATUS:.*//'
fi

# Instructions for manual testing
echo -e "\n📋 Manual testing steps:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Sign in with Azure AD"
echo "3. Open browser DevTools > Console"
echo "4. Try to create a shortened link"
echo "5. Check console logs for token acquisition messages:"
echo "   ✅ Look for: '🔑 Using access token for custom API authentication'"
echo "   ❌ Avoid: '⚠️ Using ID token as fallback'"

echo -e "\n🔍 What to check in browser console:"
echo "- Token acquisition messages"
echo "- Network tab: Check Authorization header in API requests"
echo "- Look for 401 errors in failed requests"

echo -e "\n📖 If you see 401 errors, check:"
echo "- docs/azure-ad-setup.md for complete setup guide"
echo "- Azure AD app registration has exposed API"
echo "- Access tokens are enabled in Authentication settings"
echo "- Admin consent is granted for all permissions"

echo -e "\n💡 Enable test mode if Azure AD setup is incomplete:"
echo "Add to .env file:"
echo "TEST_MODE=true"
echo "NEXT_PUBLIC_TEST_MODE=true"
