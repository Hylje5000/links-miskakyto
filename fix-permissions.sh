#!/bin/bash

# Quick fix for Link Shortener deployment permissions
# Run this if you get permission errors

echo "🔧 Fixing Link Shortener deployment permissions..."

# Fix ownership of the current directory (repository)
echo "📁 Fixing repository permissions..."
sudo chown -R $USER:$USER .

# Create and fix /opt/linkshortener if it exists
if [ -d "/opt/linkshortener" ]; then
    echo "📁 Fixing /opt/linkshortener permissions..."
    sudo chown -R $USER:$USER /opt/linkshortener
fi

echo "✅ Permissions fixed!"
echo ""
echo "🚀 Now you can run the deployment:"
echo "   ./deploy-backend-only.sh"
