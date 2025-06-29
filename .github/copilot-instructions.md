<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

This is a URL shortener application with the following architecture:

## Frontend (Next.js + TypeScript)
- Built with Next.js 15 using App Router
- Uses Tailwind CSS for styling
- Implements Microsoft Entra ID authentication using @azure/msal-react
- Uses @tanstack/react-query for API state management
- Includes components for link creation, management, and analytics

## Backend (Python + FastAPI) - Clean Architecture
- FastAPI REST API with async/await following clean architecture principles
- SQLite database for storing links and analytics
- JWT token validation for Entra ID authentication
- Implements click tracking and analytics
- CORS enabled for frontend communication

### Backend Structure:
- `main.py`: FastAPI app orchestration and startup
- `app/core/`: Configuration, database operations, and dependencies
  - `config.py`: Application settings and environment configuration
  - `database.py`: Database initialization and operations
  - `dependencies.py`: FastAPI dependency injection (auth, etc.)
- `app/models/`: Pydantic models and schemas
  - `schemas.py`: Request/response models and validation
- `app/services/`: Business logic layer
  - `link_service.py`: Core link management business logic
- `app/api/`: API route handlers
  - `links.py`: Link CRUD operations (/api/links)
  - `system.py`: Health checks and debug endpoints
  - `redirect.py`: Short code redirection handling
- `auth.py`: Authentication utilities and token validation
- `tests/`: Comprehensive test suite with pytest

## Key Features
- Entra ID authentication with tenant-based access control
- URL shortening with optional custom short codes
- Click tracking and analytics with detailed metrics
- Tenant-based link history and isolation
- User attribution for created links
- Health monitoring at `/api/health`

## Development Guidelines
- Use TypeScript with strict typing for frontend
- Follow React best practices with hooks
- Implement proper error handling and logging
- Use Tailwind CSS classes for styling
- Maintain security best practices for authentication
- Follow RESTful API design patterns
- Maintain clean architecture separation of concerns
- Write comprehensive tests for all new features
- Use dependency injection for testability
- Follow async/await patterns consistently

## Backend Architecture Principles
- **Separation of Concerns**: Each module has a single responsibility
- **Dependency Injection**: Use FastAPI's dependency system
- **Testability**: All components are easily testable in isolation
- **Configuration Management**: Environment-based configuration
- **Error Handling**: Consistent error responses and logging
- **Database Layer**: Centralized database operations
- **Service Layer**: Business logic separated from API handlers

## Database Schema
- `links` table: stores shortened links with metadata (id, original_url, short_code, description, click_count, created_at, created_by, tenant_id)
- `clicks` table: tracks individual click events (id, link_id, clicked_at, ip_address, user_agent)
- Proper indexing for performance on short_code and tenant_id

## Testing
- Unit tests for business logic and models
- Integration tests for API endpoints
- Authentication tests for security
- Comprehensive test fixtures and utilities
- Test mode with authentication bypass for development
