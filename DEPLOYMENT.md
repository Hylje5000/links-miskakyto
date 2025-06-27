# Deployment Guide for Link Shortener

## 🌐 Production Deployment

### Frontend Deployment (Vercel)

1. **Push to GitHub** (if not already done):
   ```bash
   git remote add origin https://github.com/yourusername/linkshortener.git
   git push -u origin main
   ```

2. **Deploy to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Configure environment variables:
     ```
     NEXT_PUBLIC_AZURE_CLIENT_ID=your_azure_client_id
     NEXT_PUBLIC_AZURE_TENANT_ID=your_azure_tenant_id
     NEXT_PUBLIC_API_URL=https://your-backend-url.com
     ```

3. **Configure Custom Domain**:
   - In Vercel dashboard, go to Project Settings → Domains
   - Add `links.miskakyto.fi`
   - Configure DNS records (see DNS section below)

### Backend Deployment Options

#### Option A: Railway (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### Option B: Render
- Create account at render.com
- Connect GitHub repository
- Deploy as Web Service

#### Option C: DigitalOcean App Platform
- Create account at digitalocean.com
- Use App Platform to deploy from GitHub

### Environment Variables for Production

**Frontend (.env.local)**:
```env
NEXT_PUBLIC_AZURE_CLIENT_ID=your_azure_app_client_id
NEXT_PUBLIC_AZURE_TENANT_ID=your_azure_tenant_id
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

**Backend (.env)**:
```env
AZURE_TENANT_ID=your_azure_tenant_id
BASE_URL=https://links.miskakyto.fi
ALLOWED_ORIGINS=https://links.miskakyto.fi
DATABASE_URL=postgresql://user:pass@host:port/db  # Optional: upgrade from SQLite
```

### DNS Configuration

Add these DNS records to your domain:

```
Type: CNAME
Name: links
Value: cname.vercel-dns.com
TTL: 300
```

### Azure AD Configuration

1. **Register Application**:
   - Go to Azure Portal → Azure Active Directory → App registrations
   - Create new registration
   - Set Redirect URI: `https://links.miskakyto.fi`

2. **Configure Authentication**:
   - Add platform: Single-page application
   - Redirect URIs: `https://links.miskakyto.fi`
   - Logout URL: `https://links.miskakyto.fi`

### Security Checklist

- [ ] Configure CORS for production domain
- [ ] Set up HTTPS (automatic with Vercel)
- [ ] Configure proper Azure AD scopes
- [ ] Set up environment variables
- [ ] Test authentication flow
- [ ] Configure rate limiting (optional)

### Database Options

**Current (SQLite)**:
- ✅ Simple deployment
- ⚠️ Limited scalability

**Upgrade to PostgreSQL**:
- Use Railway/Render/Supabase for managed PostgreSQL
- Update connection string in backend

### Monitoring

Consider adding:
- Error tracking (Sentry)
- Analytics (Vercel Analytics)
- Uptime monitoring
