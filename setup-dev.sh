#!/bin/bash

# Development setup script for Link Shortener

echo "🚀 Setting up Link Shortener development environment..."

# Check if required tools are installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Frontend setup
echo "📦 Installing frontend dependencies..."
npm install

# Backend setup
echo "🐍 Setting up Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "📦 Installing backend dependencies..."
pip install -r backend/requirements.txt

# Create environment files if they don't exist
if [ ! -f .env.local ]; then
    echo "📄 Creating frontend environment file..."
    cp .env.local.example .env.local
    echo "⚠️  Please edit .env.local with your Azure AD credentials"
fi

if [ ! -f backend/.env ]; then
    echo "📄 Creating backend environment file..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env with your Azure AD credentials"
fi

# Test backend setup
echo "🧪 Testing backend setup..."
cd backend && ../.venv/bin/python test_setup.py
cd ..

echo "✅ Development environment setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env.local and backend/.env with your Azure AD credentials"
echo "2. Run 'npm run dev' to start the frontend"
echo "3. Run '.venv/bin/python backend/main.py' to start the backend"
echo "4. Or use VS Code tasks to start both simultaneously"
