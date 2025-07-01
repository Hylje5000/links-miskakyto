# LinkShortener 🔗

A production-ready URL shortening service with Microsoft Entra ID authentication and memorable word-based short codes.

![Frontend](https://img.shields.io/badge/Frontend-Next.js%2015-black) ![Backend](https://img.shields.io/badge/Backend-FastAPI-green) ![Auth](https://img.shields.io/badge/Auth-Microsoft%20Entra%20ID-blue)

## ✨ Features

- 🔐 **Microsoft Entra ID Authentication** - Secure enterprise login
- 🎯 **Memorable Short Codes** - Word-based codes like `fastrun` and `happycat`
- 📊 **Click Analytics** - Real IP tracking and detailed statistics  
- ⚡ **Production Ready** - Docker-based deployment with smart builds
- 🌐 **SSL Support** - HTTPS configuration included

## 🚀 Deployment Guide

### Prerequisites
- Linux server with Docker & Docker Compose
- Domain name pointed to your server
- Microsoft Entra ID tenant access

### Step 1: Setup Microsoft Entra ID App Registration

1. **Go to Azure Portal** → Entra ID → App registrations → New registration

2. **Configure the App:**
   - **Name:** `LinkShortener`
   - **Supported account types:** Accounts in this organizational directory only
   - **Redirect URI:** `https://yourdomain.com` (replace with your domain)

3. **Note these values:**
   - **Application (client) ID** 
   - **Directory (tenant) ID**

4. **Configure Authentication:**
   - Go to Authentication → Add platform → Single-page application
   - Add redirect URI: `https://yourdomain.com`
   - Enable ID tokens checkbox

5. **Set API Permissions:**
   - Microsoft Graph → Delegated permissions → `openid`, `profile`
   - Grant admin consent

### Step 2: Server Setup

```bash
# Clone the repository
git clone <your-repository-url>
cd LinkShortener

# Create environment files
cp .env.example .env
cp .env.local.example .env.local
```

### Step 3: Configure Environment Variables

**Edit `.env` (Backend):**
```env
AZURE_TENANT_ID=your-directory-tenant-id
AZURE_CLIENT_ID=your-application-client-id
BASE_URL=https://yourdomain.com
PRODUCTION=true
```

**Edit `.env.local` (Frontend):**
```env
NEXT_PUBLIC_AZURE_CLIENT_ID=your-application-client-id
NEXT_PUBLIC_AZURE_TENANT_ID=your-directory-tenant-id
NEXT_PUBLIC_API_URL=https://yourdomain.com
```

### Step 4: SSL Certificate Setup

**Option A: Let's Encrypt (Recommended)**
```bash
# Install certbot
sudo apt update
sudo apt install certbot

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com

# Certificate files will be at:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

**Option B: Use your own SSL certificate**
- Place certificate files in `deployment/ssl/`
- Update paths in `deployment/nginx-https.conf`

### Step 5: Deploy

**Production deployment with SSL:**
```bash
# Deploy with HTTPS
docker-compose -f docker/docker-compose.fullstack.yml up -d

# Or use the smart deployment script
./scripts/smart-deploy.sh
```

**HTTP-only deployment (not recommended for production):**
```bash
# Copy HTTP-only nginx config
cp deployment/nginx-http-only.conf deployment/nginx-https.conf

# Deploy
docker-compose -f docker/docker-compose.fullstack.yml up -d
```

### Step 6: Verify Deployment

1. **Health Check:** `https://yourdomain.com/api/health`
2. **Frontend:** `https://yourdomain.com`
3. **API Docs:** `https://yourdomain.com/api/docs`

## 🔧 Post-Deployment

### Update SSL Certificates (Let's Encrypt)
```bash
# Add to crontab for automatic renewal
0 12 * * * /usr/bin/certbot renew --quiet && docker-compose -f /path/to/LinkShortener/docker/docker-compose.fullstack.yml restart linkshortener-nginx
```

### Monitoring
```bash
# View logs
docker-compose -f docker/docker-compose.fullstack.yml logs -f

# Check container status
docker-compose -f docker/docker-compose.fullstack.yml ps

# Restart services
docker-compose -f docker/docker-compose.fullstack.yml restart
```

### Updates
```bash
# Pull latest changes
git pull origin main

# Smart deployment (only rebuilds changed components)
./scripts/smart-deploy.sh
```

## 🏗️ Architecture

**Frontend:** Next.js 15 + TypeScript + Tailwind CSS + Azure MSAL  
**Backend:** FastAPI + SQLite + JWT validation  
**Infrastructure:** Docker + Nginx reverse proxy + SSL termination

```
Internet → Nginx (SSL) → Frontend (Next.js) → Backend (FastAPI) → SQLite
  443/80      8080           3000              8000           Database
```

## 📝 Configuration Files

### Key Files Structure
```
LinkShortener/
├── .env                    # Backend environment variables
├── .env.local             # Frontend environment variables  
├── docker/
│   └── docker-compose.fullstack.yml  # Production deployment
├── deployment/
│   ├── nginx-https.conf   # SSL nginx configuration
│   └── nginx-http-only.conf  # HTTP-only configuration
└── scripts/
    └── smart-deploy.sh    # Intelligent deployment script
```

### Environment Variables Reference

| Variable | File | Description |
|----------|------|-------------|
| `AZURE_TENANT_ID` | `.env`, `.env.local` | Your Entra ID tenant/directory ID |
| `AZURE_CLIENT_ID` | `.env`, `.env.local` | Your app registration client ID |
| `BASE_URL` | `.env` | Your domain (https://yourdomain.com) |
| `NEXT_PUBLIC_API_URL` | `.env.local` | API endpoint for frontend |
| `PRODUCTION` | `.env` | Set to `true` for production mode |

## 🚨 Security Notes

- Always use HTTPS in production
- Keep your Entra ID client secret secure (not used in this SPA setup)
- Regularly update SSL certificates
- Monitor authentication logs in Azure Portal
- Use proper firewall rules to restrict access

## 🆘 Troubleshooting

### Authentication Issues
1. Verify Entra ID app registration redirect URIs
2. Check tenant and client IDs in environment files
3. Ensure user has access to the application

### Deployment Issues
```bash
# Check container logs
docker-compose -f docker/docker-compose.fullstack.yml logs linkshortener-backend
docker-compose -f docker/docker-compose.fullstack.yml logs linkshortener-frontend
docker-compose -f docker/docker-compose.fullstack.yml logs linkshortener-nginx

# Restart specific service
docker-compose -f docker/docker-compose.fullstack.yml restart linkshortener-backend
```

### SSL Certificate Issues
```bash
# Test certificate
sudo certbot certificates

# Renew certificate
sudo certbot renew

# Check nginx configuration
docker exec linkshortener-nginx nginx -t
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

**🔗 Create memorable short links like `fastrun` instead of random characters!**
