#!/bin/bash

# Deploy Link Shortener frontend to nginx on the same VM as backend
# This serves the frontend from links.miskakyto.fi while backend APIs are on /api/

set -e

echo "🚀 Setting up Frontend deployment on VM..."

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "⚠️  Please run this script as a regular user with sudo privileges, not as root"
   exit 1
fi

# Get the current directory (should be the cloned repo)
REPO_DIR=$(pwd)
echo "📁 Working from repository: $REPO_DIR"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "📦 Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Install dependencies
echo "📦 Installing frontend dependencies..."
npm install

# Create production environment file
echo "⚙️  Setting up environment configuration..."
cat > .env.production.local <<EOF
NEXT_PUBLIC_API_URL=https://links.miskakyto.fi
NEXT_PUBLIC_AZURE_CLIENT_ID=${AZURE_CLIENT_ID:-your-client-id-here}
NEXT_PUBLIC_AZURE_TENANT_ID=${AZURE_TENANT_ID:-your-tenant-id-here}
NEXT_PUBLIC_REDIRECT_URI=https://links.miskakyto.fi
EOF

echo "📝 Please edit .env.production.local with your Azure AD credentials:"
echo "   nano .env.production.local"
echo ""
read -p "Press Enter after you've configured the environment file..."

# Build the frontend
echo "🏗️  Building frontend for production..."
npm run build

# Create web directory
WEB_DIR="/var/www/linkshortener"
echo "📁 Creating web directory..."
sudo mkdir -p $WEB_DIR
sudo chown www-data:www-data $WEB_DIR

# Copy built files
echo "📋 Copying built files to web directory..."
sudo cp -r .next/static $WEB_DIR/
sudo cp -r public/* $WEB_DIR/ 2>/dev/null || true
sudo cp -r .next/standalone/* $WEB_DIR/ 2>/dev/null || true

# For Next.js static export (alternative approach)
echo "🔄 Creating static export..."
cat > next.config.js <<EOF
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  },
  assetPrefix: '',
  basePath: ''
}

module.exports = nextConfig
EOF

npm run build
sudo cp -r out/* $WEB_DIR/
sudo chown -R www-data:www-data $WEB_DIR

echo "✅ Frontend build complete!"
echo ""
echo "📝 Next steps:"
echo "1. Update your nginx configuration to serve the frontend"
echo "2. Test the configuration: sudo nginx -t"
echo "3. Reload nginx: sudo systemctl reload nginx"
echo ""
echo "📁 Frontend files are in: $WEB_DIR"
echo "🌐 Frontend will be available at: https://links.miskakyto.fi"
