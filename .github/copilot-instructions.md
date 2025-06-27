<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

This is a URL shortener application with the following architecture:

## Frontend (Next.js + TypeScript)
- Built with Next.js 15 using App Router
- Uses Tailwind CSS for styling
- Implements Microsoft Entra ID authentication using @azure/msal-react
- Uses @tanstack/react-query for API state management
- Includes components for link creation, management, and analytics

## Backend (Python + FastAPI)
- FastAPI REST API with async/await
- SQLite database for storing links and analytics
- JWT token validation for Entra ID authentication
- Implements click tracking and analytics
- CORS enabled for frontend communication

## Key Features
- Entra ID authentication with tenant-based access control
- URL shortening with optional custom short codes
- Click tracking and analytics
- Tenant-based link history
- User attribution for created links

## Development Guidelines
- Use TypeScript with strict typing
- Follow React best practices with hooks
- Implement proper error handling
- Use Tailwind CSS classes for styling
- Maintain security best practices for authentication
- Follow RESTful API design patterns

## Database Schema
- `links` table: stores shortened links with metadata
- `clicks` table: tracks individual click events
- Proper indexing for performance
