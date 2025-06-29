#!/bin/bash

# Quick script to check auth status and diagnose Azure AD configuration issues

echo "🔍 Checking authentication status..."

# Check if the app is running
if ! curl -s http://localhost:8000/api/health > /dev/null; then
    echo "❌ Backend not running on localhost:8000"
    echo "💡 Start the backend with: cd backend && uvicorn main:app --reload"
    exit 1
fi

echo "✅ Backend is running"

# Check auth debug endpoint
echo "🔑 Checking auth configuration..."
AUTH_RESPONSE=$(curl -s http://localhost:8000/api/debug/auth)
echo "$AUTH_RESPONSE" | jq '.' 2>/dev/null || echo "$AUTH_RESPONSE"

# Check if in test mode
if echo "$AUTH_RESPONSE" | grep -q "test_mode.*true"; then
    echo -e "\n✅ Running in test mode - authentication is bypassed"
    echo "💡 To test production auth, set TEST_MODE=false in your .env"
else
    echo -e "\n🔍 Running in production mode - checking Azure AD configuration..."
    
    # Check environment variables
    if [ -z "$NEXT_PUBLIC_AZURE_CLIENT_ID" ]; then
        echo "❌ NEXT_PUBLIC_AZURE_CLIENT_ID not set"
    else
        echo "✅ NEXT_PUBLIC_AZURE_CLIENT_ID is set"
    fi
    
    if [ -z "$NEXT_PUBLIC_AZURE_TENANT_ID" ]; then
        echo "❌ NEXT_PUBLIC_AZURE_TENANT_ID not set"
    else
        echo "✅ NEXT_PUBLIC_AZURE_TENANT_ID is set"
    fi
    
    echo -e "\n🎯 Expected access token audience: api://$NEXT_PUBLIC_AZURE_CLIENT_ID"
    echo "📖 See docs/azure-ad-setup.md for complete Azure AD configuration guide"
fi

echo -e "\n📝 To enable test mode for development:"
echo "1. Create/edit .env file with:"
echo "   TEST_MODE=true"
echo "   NEXT_PUBLIC_TEST_MODE=true"
echo "2. Restart both frontend and backend"

echo -e "\n� Quick commands:"
echo "Frontend: npm run dev"
echo "Backend:  cd backend && uvicorn main:app --reload"

echo -e "\n📋 Authentication troubleshooting checklist:"
echo "□ Azure AD app registration created"
echo "□ API exposed with Application ID URI: api://your-client-id"
echo "□ Access tokens enabled in Authentication settings"
echo "□ Admin consent granted for all permissions"
echo "□ Frontend requesting correct scope: api://your-client-id/.default"
echo "□ Browser console shows: 'Using access token for custom API authentication'"
