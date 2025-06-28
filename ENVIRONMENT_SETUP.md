# Environment Setup Guide

## Required Environment Variables

Your URL shortener application only requires **2 environment variables** to function:

### Backend (.env file)
```bash
# Azure AD Configuration (Required)
AZURE_TENANT_ID=your-tenant-id-here
AZURE_CLIENT_ID=your-client-id-here
```

### Frontend (.env.local file)
```bash
# Azure AD Configuration (Required)
NEXT_PUBLIC_AZURE_TENANT_ID=your-tenant-id-here
NEXT_PUBLIC_AZURE_CLIENT_ID=your-client-id-here
```

## Optional Environment Variables

These have sensible defaults and only need to be set if you want to customize them:

### Backend (Optional)
```bash
# Database (defaults to sqlite:///./links.db)
DATABASE_URL=sqlite:///data/links.db

# Application URLs (defaults to localhost)
BASE_URL=https://your-domain.com
ALLOWED_ORIGINS=https://your-domain.com

# Logging (defaults to INFO)
LOG_LEVEL=DEBUG

# Production mode (defaults to false)
PRODUCTION=true

# Test mode (defaults to false)
TEST_MODE=false
```

## Getting Your Azure AD Values

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to "Azure Active Directory"
3. Go to "App registrations"
4. Find or create your application
5. Copy the following values:
   - **Application (client) ID** → `AZURE_CLIENT_ID`
   - **Directory (tenant) ID** → `AZURE_TENANT_ID`

## Deployment Environment File

For your VM deployment, create `/home/miska/linkshortener/.env` with:

```bash
# Minimum required configuration
AZURE_TENANT_ID=your-actual-tenant-id
AZURE_CLIENT_ID=your-actual-client-id

# Production settings
BASE_URL=https://links.miskakyto.fi
ALLOWED_ORIGINS=https://links.miskakyto.fi
DATABASE_URL=sqlite:///data/links.db
PRODUCTION=true
```

## Notes

- `SECRET_KEY` was removed as it's not used in the application code
- `AZURE_CLIENT_SECRET` is not needed for frontend-only Azure AD authentication
- All other environment variables have sensible defaults and are optional
