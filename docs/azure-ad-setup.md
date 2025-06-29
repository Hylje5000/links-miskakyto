# Azure AD (Entra ID) App Registration Setup Guide

This guide walks you through setting up Azure AD app registration for the Link Shortener application to resolve 401 authentication errors.

## Prerequisites

- Azure AD tenant with admin privileges
- Access to Azure Portal (portal.azure.com)

## Step-by-Step Setup

### 1. Create App Registration

1. Go to Azure Portal > Azure Active Directory > App registrations
2. Click "New registration"
3. Fill in:
   - **Name**: Link Shortener
   - **Supported account types**: Choose based on your needs
   - **Redirect URI**: Platform: Single-page application (SPA), URI: `http://localhost:3000`
4. Click "Register"

### 2. Configure Authentication

1. Go to your app registration > Authentication
2. Under "Implicit grant and hybrid flows", ensure these are checked:
   - ✅ **Access tokens** (used for implicit flows)
   - ✅ **ID tokens** (used for implicit and hybrid flows)
3. Add redirect URIs for all environments:
   - `http://localhost:3000` (development)
   - `https://links.miskakyto.fi` (production)
   - Any other domains where your app will be hosted
4. Click "Save"

### 3. Configure Token Settings (Simplified Approach)

Since we're using ID tokens for authentication (a simpler, best-practice approach), you don't need to expose a custom API. The app will use standard OpenID Connect scopes.

1. Go to your app registration > Token configuration
2. Click "Add optional claim"
3. Select "ID" token type
4. Add these claims if not already present:
   - ✅ **email** - user's email address  
   - ✅ **name** - user's display name
   - ✅ **upn** - user principal name
5. Click "Add"

**Why ID tokens instead of access tokens?**
- ID tokens contain user identity information and are perfect for authentication
- They're simpler to validate and don't require custom API scopes
- This follows Azure AD best practices for single-page applications
- No need to expose custom APIs or manage complex permission flows

### 4. Configure API Permissions (Minimal Setup)

With ID tokens, you only need basic Microsoft Graph permissions:

1. Go to your app registration > "API permissions"
2. You should see:
   - Microsoft Graph (User.Read) - this was added automatically
   
3. **You will NOT see your custom API listed here** - this is normal and expected when using a single app registration for both frontend and backend.

4. Click "Grant admin consent for [your organization]" for the Microsoft Graph permission.

**Why don't I see my API here?** 
An Azure AD app registration cannot request permissions to itself. Since your frontend and backend use the same app registration, the frontend automatically has access to the backend's scopes. This is the recommended approach for simple applications.

**Alternative: Two separate app registrations**
If you want to separate concerns, you can create:
- One app for the frontend (SPA)  
- One app for the backend (API)
Then the frontend app would request permissions to the backend app's exposed API.

### 5. Get Configuration Values

From your app registration overview page, copy these values to your `.env` file:

```bash
# Frontend (Development)
NEXT_PUBLIC_AZURE_CLIENT_ID=your-application-client-id
NEXT_PUBLIC_AZURE_TENANT_ID=your-directory-tenant-id
NEXT_PUBLIC_REDIRECT_URI=http://localhost:3000

# Frontend (Production)
NEXT_PUBLIC_AZURE_CLIENT_ID=81f7c571-588d-4a13-be31-3cc8da4bf4fe
NEXT_PUBLIC_AZURE_TENANT_ID=d53dc26d-d4c3-47b9-aa62-ba032ee23f13
NEXT_PUBLIC_REDIRECT_URI=https://links.miskakyto.fi
NEXT_PUBLIC_API_URL=https://links.miskakyto.fi

# Backend (Both environments)
AZURE_CLIENT_ID=your-application-client-id
AZURE_TENANT_ID=your-directory-tenant-id
TEST_MODE=false
```

## Verify Configuration

### Test Token Acquisition

1. Start your frontend application
2. Sign in with Azure AD
3. Open browser dev tools > Console
4. Look for these log messages:
   - ✅ `🔑 Using access token for custom API authentication`
   - ✅ `🎯 Token audience should be: 81f7c571-588d-4a13-be31-3cc8da4bf4fe`

If you see:
- ❌ `⚠️ Using ID token as fallback` - Your API isn't properly exposed or scope format is incorrect
- ❌ `❌ Custom API access token acquisition failed` - Check permissions and consent

**Note**: When using a single app registration for both frontend and backend, the frontend requests tokens using the scope `{client-id}/.default` (without the `api://` prefix).

### Debug API Authentication

Use the debug endpoint to verify tokens:

```bash
# Get auth status
curl http://localhost:8000/api/debug/auth

# Create a link (this should work after proper setup)
curl -X POST http://localhost:8000/api/links \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://example.com", "description": "test"}'
```

## Troubleshooting

### 401 Unauthorized Errors

**Problem**: Frontend gets 401 when calling backend APIs

**Solution**: 
1. Verify you completed step 3 (Expose an API) correctly
2. Check that your app registration has "Access tokens" enabled in Authentication
3. Grant admin consent for all permissions
4. Verify the Application ID URI is `api://your-client-id`

### Token Audience Mismatch

**Problem**: Access token has `aud: 00000003-0000-0000-c000-000000000000` (Microsoft Graph)

**Solution**: This means your frontend is requesting a token for Microsoft Graph instead of your custom API. Check:
1. Your API is properly exposed (step 3)
2. Frontend is requesting the correct scope: `{client-id}/.default` (without `api://` prefix)
3. Permission was granted for your custom API

**Note**: When an app requests a token for itself, use the GUID format (`{client-id}/.default`) rather than the URI format (`api://{client-id}/.default`).

### Consent Required Errors

**Problem**: `consent_required` or `interaction_required` errors

**Solution**: 
1. Admin consent wasn't granted - go to API permissions and click "Grant admin consent"
2. User consent is required - the app will automatically show a popup for consent

### Test Mode for Development

If you're having trouble with Azure AD setup, enable test mode for local development:

```bash
# .env
TEST_MODE=true
NEXT_PUBLIC_TEST_MODE=true
```

This bypasses authentication and lets you develop without Azure AD configuration.

## Security Considerations

1. **Never expose client secrets** in frontend applications
2. **Use HTTPS in production** for all redirect URIs
3. **Validate tokens properly** in the backend (already implemented)
4. **Grant minimal permissions** - only the scopes your app actually needs
5. **Regular token rotation** - Azure AD handles this automatically

## Production Checklist

- [ ] App registration created and configured
- [ ] API properly exposed with Application ID URI
- [ ] Access tokens enabled in Authentication settings
- [ ] All necessary permissions granted with admin consent
- [ ] Production redirect URIs added
- [ ] HTTPS configured for production environment
- [ ] Environment variables properly set
- [ ] Token acquisition working (check browser console logs)
- [ ] Backend successfully validating tokens (check `/api/debug/auth`)
