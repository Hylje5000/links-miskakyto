# LinkShortener 🔗

A modern, secure URL shortener application with Microsoft Entra ID authentication, built with Next.js and Python FastAPI.

![Architecture](https://img.shields.io/badge/Architecture-Microservices-blue) ![Frontend](https://img.shields.io/badge/Frontend-Next.js%2015-black) ![Backend](https://img.shields.io/badge/Backend-FastAPI-green) ![Database](https://img.shields.io/badge/Database-SQLite-orange) ![Auth](https://img.shields.io/badge/Auth-Microsoft%20Entra%20ID-blue)

## ✨ Features

- 🔐 **Microsoft Entra ID Authentication** - Enterprise-grade security
- 🔗 **Smart URL Shortening** - Custom short codes and auto-generation
- 📊 **Real-time Analytics** - Click tracking, geographic data, and statistics
- 👥 **Multi-tenant Support** - Tenant-based link organization and access control
- 🎨 **Modern UI/UX** - Responsive design with Tailwind CSS
- ⚡ **High Performance** - Optimized with caching and async operations
- 🐋 **Containerized Deployment** - Docker-based with smart rebuilding
- 🚀 **CI/CD Ready** - GitHub Actions with automated deployments

## 🏗️ Architecture

### Frontend (Next.js 15)
```
📁 src/
├── app/          # App Router pages
├── components/   # Reusable UI components
├── lib/          # Utilities and API clients
└── types/        # TypeScript type definitions
```

**Tech Stack:**
- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript with strict typing
- **Styling**: Tailwind CSS + shadcn/ui components
- **Authentication**: @azure/msal-react
- **State Management**: @tanstack/react-query
- **Icons**: Lucide React

### Backend (FastAPI) - Clean Architecture
```
📁 backend/
├── main.py                 # FastAPI app orchestration
├── auth.py                 # Authentication utilities
├── app/
│   ├── core/              # Core application components
│   │   ├── config.py      # Configuration management
│   │   ├── database.py    # Database operations
│   │   └── dependencies.py # FastAPI dependencies
│   ├── models/            # Data models
│   │   └── schemas.py     # Pydantic models
│   ├── services/          # Business logic layer
│   │   └── link_service.py # Link management logic
│   └── api/               # API route handlers
│       ├── links.py       # Link CRUD endpoints
│       ├── system.py      # Health & debug endpoints
│       └── redirect.py    # Redirect handling
└── tests/                 # Comprehensive test suite
```

**Tech Stack:**
- **Framework**: FastAPI with async/await and clean architecture
- **Database**: SQLite with aiosqlite for async operations
- **Authentication**: JWT token validation with Microsoft Entra ID
- **Testing**: pytest with comprehensive fixtures
- **API Docs**: Automatic OpenAPI/Swagger generation
- **Architecture**: Clean separation of concerns with dependency injection

### Infrastructure
```
📁 Project Structure
├── docker/           # Docker configurations
├── scripts/          # Management scripts
├── deployment/       # Production deployment configs
├── docs/            # Documentation
└── .github/         # CI/CD workflows
```

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.11+
- **Docker** and Docker Compose
- **Azure AD** application registration

### 1. Clone and Setup
```bash
git clone <repository-url>
cd LinkShortener

# Install frontend dependencies
npm install

# Setup backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### 2. Environment Configuration

Create `.env` in the project root:
```env
# Azure AD Configuration (Required)
AZURE_TENANT_ID=your-tenant-id-here
AZURE_CLIENT_ID=your-client-id-here

# Application Configuration
BASE_URL=http://localhost:8080
ALLOWED_ORIGINS=http://localhost:8080
DATABASE_URL=sqlite:///data/links.db

# Optional: Logging
LOG_LEVEL=INFO
```

Create `.env.local` for frontend:
```env
NEXT_PUBLIC_AZURE_CLIENT_ID=your-client-id-here
NEXT_PUBLIC_AZURE_TENANT_ID=your-tenant-id-here
NEXT_PUBLIC_REDIRECT_URI=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Development Mode

#### Option A: Docker (Recommended)
```bash
# Start all services with Docker
./scripts/manage-fullstack.sh start

# View logs
./scripts/manage-fullstack.sh logs

# Stop services
./scripts/manage-fullstack.sh stop
```

#### Option B: Separate Processes
```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
npm run dev
```

Access the application at **http://localhost:8080** (Docker) or **http://localhost:3000** (dev mode).

## 🐋 Docker Deployment

### Local Development
```bash
# Start services
./scripts/manage-fullstack.sh start

# Force rebuild (after changes)
./scripts/manage-fullstack.sh rebuild

# Check status
./scripts/manage-fullstack.sh status

# View logs
./scripts/manage-fullstack.sh logs [backend|frontend|nginx]
```

### Production Deployment

#### Smart Deployment
The project includes intelligent deployment that only rebuilds changed components:

```bash
# Deploy with change detection
./scripts/smart-deploy.sh

# Deploy specific components
./scripts/manage-fullstack.sh rebuild
```

#### Manual Production Setup
```bash
# 1. Set up environment
cp backend/.env.production .env
# Edit .env with your production values

# 2. Deploy with Docker Compose
docker-compose -f docker/docker-compose.fullstack.yml up -d --build

# 3. Verify deployment
curl http://localhost:8080/api/health
```

## 📡 API Reference

### Authentication
All API endpoints require a valid Azure AD JWT token in the `Authorization` header:
```http
Authorization: Bearer <jwt-token>
```

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/links` | Create a new short link |
| `GET` | `/api/links` | List all links for tenant |
| `GET` | `/api/links/{id}` | Get specific link details |
| `PUT` | `/api/links/{id}` | Update link |
| `DELETE` | `/api/links/{id}` | Delete link |
| `GET` | `/api/links/{id}/analytics` | Get link analytics |
| `GET` | `/{short_code}` | Redirect to original URL |
| `GET` | `/api/health` | Health check endpoint |

### Example API Usage

**Create a Short Link:**
```http
POST /api/links
Content-Type: application/json
Authorization: Bearer <token>

{
  "original_url": "https://example.com/very/long/url",
  "short_code": "custom123",
  "description": "Example link"
}
```

**Response:**
```json
{
  "id": 1,
  "original_url": "https://example.com/very/long/url",
  "short_code": "custom123",
  "short_url": "http://localhost:8080/custom123",
  "description": "Example link",
  "click_count": 0,
  "created_at": "2025-06-29T12:00:00Z",
  "created_by": "user@example.com",
  "tenant_id": "tenant-uuid"
}
```

## 🗄️ Database Schema

### Links Table
```sql
CREATE TABLE links (
    id INTEGER PRIMARY KEY,
    original_url TEXT NOT NULL,
    short_code TEXT UNIQUE NOT NULL,
    description TEXT,
    click_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT NOT NULL,
    tenant_id TEXT NOT NULL
);
```

### Clicks Table
```sql
CREATE TABLE clicks (
    id INTEGER PRIMARY KEY,
    link_id INTEGER REFERENCES links(id),
    clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,
    user_agent TEXT
);
```

## 🔒 Security Features

- **Authentication**: Microsoft Entra ID with JWT validation
- **Authorization**: Tenant-based access control
- **CORS Protection**: Configurable origins
- **Input Validation**: Pydantic models with validation
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **Rate Limiting**: Built-in FastAPI rate limiting
- **HTTPS Support**: SSL/TLS configuration ready

## 🛠️ Development

### Available Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start Next.js development server |
| `npm run build` | Build production frontend |
| `npm run lint` | Run ESLint |
| `npm run type-check` | TypeScript type checking |
| `npm test` | Run frontend tests |

### Management Scripts

| Script | Description |
|--------|-------------|
| `./scripts/manage-fullstack.sh start` | Start all services |
| `./scripts/manage-fullstack.sh stop` | Stop all services |
| `./scripts/manage-fullstack.sh rebuild` | Force rebuild containers |
| `./scripts/manage-fullstack.sh logs` | View service logs |
| `./scripts/smart-deploy.sh` | Smart deployment (production) |

### Code Quality
```bash
# Frontend
npm run lint        # ESLint
npm run type-check  # TypeScript

# Backend
cd backend
black .            # Code formatting
mypy .             # Type checking
pytest             # Run tests
```

## 🚀 Production Deployment

### Azure VM Deployment
The project includes automated deployment to Azure VMs via GitHub Actions:

1. **Setup VM**: Use `deployment/vm-setup.sh`
2. **Configure Secrets**: Add `VM_SSH_KEY` to GitHub secrets
3. **Deploy**: Push to main branch triggers deployment
4. **Monitor**: GitHub Actions provides deployment status

### Manual Production Setup
```bash
# 1. Clone repository on server
git clone <repo-url> /path/to/app
cd /path/to/app

# 2. Configure environment
cp backend/.env.production .env
# Edit .env with production values

# 3. Deploy
./scripts/smart-deploy.sh

# 4. Setup reverse proxy (nginx)
# Use deployment/nginx-https.conf for SSL setup
```

## 📚 Documentation

- **[Deployment Guide](docs/DEPLOYMENT.md)** - Detailed deployment instructions
- **[Smart Deployment](docs/SMART_DEPLOYMENT.md)** - Intelligent rebuild system
- **[Environment Setup](docs/ENVIRONMENT_SETUP.md)** - Configuration guide
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)
- **Documentation**: [docs/](docs/)

---

**Built with ❤️ using Next.js, FastAPI, and modern DevOps practices.**
