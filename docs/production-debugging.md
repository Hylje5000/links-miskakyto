# Production Deployment Debugging Guide

## Current Issue
- Frontend authentication is working (getting correct access tokens)
- Backend is returning 401 Unauthorized
- Production URL: https://links.miskakyto.fi

## Debug Steps

### 1. Check Backend Auth Configuration

Test your production backend's debug endpoint:

```bash
curl -s https://links.miskakyto.fi/api/debug/auth
```

Look for:
- `test_mode: false` (should be false in production)
- `azure_tenant_id: true` (should be true)
- `azure_client_id: true` (should be true)

### 2. Check Backend Environment Variables

Your production backend MUST have these environment variables set:

```bash
# Required for production
TEST_MODE=false
AZURE_TENANT_ID=d53dc26d-d4c3-47b9-aa62-ba032ee23f13
AZURE_CLIENT_ID=81f7c571-588d-4a13-be31-3cc8da4bf4fe

# Optional but recommended
ALLOWED_ORIGINS=https://links.miskakyto.fi
```

### 3. Test Token Validation

Get an ID token from your browser and test it:

1. Open browser DevTools > Console
2. Run: `localStorage.clear()` then refresh and sign in
3. Check the network requests in DevTools to see the Authorization header with the ID token
4. Test with the backend:

```bash
curl -X POST https://links.miskakyto.fi/api/links \
  -H "Authorization: Bearer YOUR_ID_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://example.com", "description": "test"}'
```

### 4. Check Backend Logs

Look at your production backend logs for error messages like:
- "Token validation failed"
- "Invalid token"
- "Azure AD configuration missing"

## Common Production Issues

### Issue 1: Backend in Test Mode
**Problem**: Backend has `TEST_MODE=true` in production
**Solution**: Set `TEST_MODE=false` and restart backend

### Issue 2: Missing Azure AD Environment Variables
**Problem**: `AZURE_TENANT_ID` or `AZURE_CLIENT_ID` not set in production
**Solution**: Add the environment variables to your production deployment

### Issue 3: CORS Issues
**Problem**: Backend doesn't allow requests from your production domain
**Solution**: Set `ALLOWED_ORIGINS=https://links.miskakyto.fi` in backend

### Issue 4: Token Audience Mismatch
**Problem**: Backend expects different audience than what frontend provides
**Solution**: Ensure both frontend and backend use the same `AZURE_CLIENT_ID`

## Frontend Production Configuration

Your frontend should have these environment variables:

```bash
# .env.production or deployment config
NEXT_PUBLIC_AZURE_CLIENT_ID=81f7c571-588d-4a13-be31-3cc8da4bf4fe
NEXT_PUBLIC_AZURE_TENANT_ID=d53dc26d-d4c3-47b9-aa62-ba032ee23f13
NEXT_PUBLIC_REDIRECT_URI=https://links.miskakyto.fi
NEXT_PUBLIC_API_URL=https://links.miskakyto.fi

# Make sure test mode is disabled
NEXT_PUBLIC_TEST_MODE=false
```

## Azure AD Production Setup

Ensure your Azure AD app registration has:

1. **Redirect URIs** including production domain:
   - `https://links.miskakyto.fi` (in Authentication section)

2. **CORS origins** if needed:
   - Some setups require adding the production domain to allowed origins

## Quick Diagnostic Script

Run this to check your production setup:

```bash
#!/bin/bash
echo "🔍 Production Diagnostics for links.miskakyto.fi"

# Test health endpoint
echo "1. Backend Health Check:"
curl -s https://links.miskakyto.fi/api/health | jq '.' || echo "Health check failed"

# Test auth debug
echo -e "\n2. Auth Configuration:"
curl -s https://links.miskakyto.fi/api/debug/auth | jq '.' || echo "Auth debug failed"

# Test anonymous access (should get 401)
echo -e "\n3. Anonymous API Access (should be 401):"
curl -s -w "HTTP_STATUS:%{http_code}" https://links.miskakyto.fi/api/links

echo -e "\n\n📋 Checklist:"
echo "□ Backend health endpoint returns 200"
echo "□ Auth debug shows test_mode: false"
echo "□ Auth debug shows azure credentials configured"
echo "□ Anonymous API access returns 401"
echo "□ Production environment variables are set"
echo "□ Azure AD redirect URI includes production domain"
```

## Next Steps

1. Run the diagnostic script above
2. Check your production backend logs
3. Verify environment variables are set correctly
4. Test with the actual access token from your browser

Let me know what the debug endpoint shows and we can fix the specific issue!
