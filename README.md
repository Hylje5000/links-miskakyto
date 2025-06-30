# LinkShortener 🔗

A modern URL shortener with memorable word-based short codes and Microsoft Entra ID authentication.

![Frontend](https://img.shields.io/badge/Frontend-Next.js%2015-black) ![Backend](https://img.shields.io/badge/Backend-FastAPI-green) ![Auth](https://img.shields.io/badge/Auth-Microsoft%20Entra%20ID-blue)

## ✨ Features

- 🔐 **Microsoft Entra ID Authentication** - Secure enterprise login
- 🎯 **Memorable Short Codes** - Word-based codes like `fastrun` and `happycat` instead of random characters
- � **Click Analytics** - Track clicks and view detailed statistics  
- 👥 **Multi-tenant** - Secure tenant-based access control
- ⚡ **Fast & Modern** - Built with Next.js 15 and FastAPI
- 🐋 **Easy Deployment** - Docker-based setup

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- Azure AD app registration

### 1. Setup
```bash
git clone <repository-url>
cd LinkShortener
npm install
```

### 2. Environment Configuration

Create `.env` file:
```env
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
BASE_URL=http://localhost:8080
```

Create `.env.local` file:
```env
NEXT_PUBLIC_AZURE_CLIENT_ID=your-client-id
NEXT_PUBLIC_AZURE_TENANT_ID=your-tenant-id
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run with Docker
```bash
# Start all services
docker-compose -f docker/docker-compose.fullstack.yml up -d

# View logs
docker-compose -f docker/docker-compose.fullstack.yml logs -f

# Stop services  
docker-compose -f docker/docker-compose.fullstack.yml down
```

Access the app at **http://localhost:8080**

### 4. Development Mode (Alternative)
```bash
# Terminal 1: Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py

# Terminal 2: Frontend  
npm run dev
```

Access at **http://localhost:3000**

## 📡 API Examples

### Create a Short Link
```bash
curl -X POST "http://localhost:8080/api/links" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "original_url": "https://example.com/very/long/url",
    "description": "My example link"
  }'
```

### Use the Short Link
Navigate to `http://localhost:8080/happycat` → redirects to your original URL

## 🏗️ Architecture

**Frontend:** Next.js 15 + TypeScript + Tailwind CSS + Azure MSAL  
**Backend:** FastAPI + SQLite + JWT validation  
**Infrastructure:** Docker + Nginx reverse proxy

```
Frontend (Next.js)  →  Nginx  →  Backend (FastAPI)  →  SQLite
     ↓                   ↓              ↓              ↓
  Port 3000          Port 8080      Port 8000      Database
```

## � Key Files

- `src/` - Next.js frontend application
- `backend/` - FastAPI backend application  
- `docker/` - Docker configurations
- `.env` - Environment variables
- `docker-compose.fullstack.yml` - Full stack deployment

## 📚 Learn More

- **Backend API Docs:** http://localhost:8000/docs (when running)
- **Health Check:** http://localhost:8080/api/health
- **Architecture Details:** See `backend/` folder structure for clean architecture implementation

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

---

**Built with ❤️ - Create memorable short links like `fastrun` instead of `7HAga6XA`!**
