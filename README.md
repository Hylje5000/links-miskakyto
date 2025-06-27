# Link Shortener

A modern, secure URL shortener application with Microsoft Entra ID authentication, built with Next.js and Python FastAPI.

## Features

- 🔐 **Entra ID Authentication** - Secure enterprise authentication
- 🔗 **URL Shortening** - Create short links with custom codes
- 📊 **Analytics & Tracking** - Detailed click tracking and analytics
- 👥 **Tenant-based Management** - Multi-tenant link organization
- 🎨 **Modern UI** - Clean, responsive interface built with Tailwind CSS
- ⚡ **Real-time Updates** - Live analytics and link management

## Architecture

### Frontend (Next.js)
- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: @azure/msal-react
- **State Management**: @tanstack/react-query
- **Icons**: lucide-react

### Backend (Python)
- **Framework**: FastAPI
- **Database**: SQLite with async support
- **Authentication**: JWT token validation
- **Dependencies**: See `backend/requirements.txt`

## Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- Azure AD application registration

## Setup Instructions

### 1. Azure AD Configuration

1. Register an application in Azure AD
2. Configure redirect URIs (http://localhost:3000 for development)
3. Note down the Client ID and Tenant ID

### 2. Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env
# Edit .env with your Azure AD credentials
```

### 3. Frontend Setup

```bash
# Install dependencies
npm install

# Copy environment file and configure
cp .env.local.example .env.local
# Edit .env.local with your Azure AD credentials
```

### 4. Running the Application

#### Start the Backend
```bash
cd backend
python main.py
```
The API will be available at http://localhost:8000

#### Start the Frontend
```bash
npm run dev
```
The application will be available at http://localhost:3000

## Environment Variables

### Backend (.env)
```env
AZURE_CLIENT_ID=your_azure_client_id_here
AZURE_CLIENT_SECRET=your_azure_client_secret_here  
AZURE_TENANT_ID=your_azure_tenant_id_here
DATABASE_URL=sqlite:///./links.db
SECRET_KEY=your_secret_key_here
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
BASE_URL=http://localhost:8000
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_AZURE_CLIENT_ID=your_azure_client_id_here
NEXT_PUBLIC_AZURE_TENANT_ID=your_azure_tenant_id_here
NEXT_PUBLIC_REDIRECT_URI=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Endpoints

- `POST /api/links` - Create a new short link
- `GET /api/links` - Get all links for the authenticated user's tenant
- `GET /api/links/{id}` - Get a specific link
- `PUT /api/links/{id}` - Update a link
- `DELETE /api/links/{id}` - Delete a link
- `GET /api/links/{id}/analytics` - Get link analytics
- `GET /{short_code}` - Redirect to original URL (tracks clicks)

## Database Schema

### Links Table
- `id` - Unique identifier
- `original_url` - The original long URL
- `short_code` - The shortened code
- `description` - Optional description
- `click_count` - Number of clicks
- `created_at` - Creation timestamp
- `created_by` - User who created the link
- `tenant_id` - Azure AD tenant ID

### Clicks Table
- `id` - Auto-increment ID
- `link_id` - Reference to links table
- `clicked_at` - Click timestamp
- `ip_address` - Client IP address
- `user_agent` - Client user agent

## Security Features

- JWT token validation
- Tenant-based access control
- CORS protection
- Input validation and sanitization
- SQL injection prevention

## Development

### Frontend Development
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking
```

### Backend Development
```bash
# Install development dependencies
pip install pytest httpx

# Run tests (if implemented)
pytest

# Format code
black .

# Type checking
mypy .
```

## Deployment

### Frontend Deployment (Vercel)
1. Connect your repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on git push

### Backend Deployment
1. Use a cloud provider (AWS, Azure, GCP)
2. Set up environment variables
3. Configure domain and SSL
4. Update CORS settings for production domain

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
