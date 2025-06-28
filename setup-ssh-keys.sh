#!/bin/bash

# Script to help set up SSH keys for GitHub Actions deployment

set -e

VM_IP="4.210.156.244"
VM_USER="miska"
KEY_NAME="linkshortener_deploy"

echo "🔐 Setting up SSH keys for GitHub Actions deployment"
echo "VM: $VM_USER@$VM_IP"
echo ""

# Check if key already exists
if [ -f ~/.ssh/$KEY_NAME ]; then
    echo "⚠️  SSH key ~/.ssh/$KEY_NAME already exists"
    read -p "Do you want to use the existing key? (y/n): " use_existing
    if [ "$use_existing" != "y" ]; then
        echo "❌ Aborting. Please remove the existing key or choose a different name."
        exit 1
    fi
else
    echo "🔑 Generating new SSH key pair..."
    ssh-keygen -t ed25519 -C "github-actions@linkshortener" -f ~/.ssh/$KEY_NAME -N ""
    echo "✅ SSH key pair generated"
fi

echo ""
echo "📤 Adding public key to VM..."
echo "You may be prompted for your VM password."

# Copy public key to VM
if ssh-copy-id -i ~/.ssh/$KEY_NAME.pub $VM_USER@$VM_IP; then
    echo "✅ Public key added to VM"
else
    echo "❌ Failed to add public key to VM"
    echo "Manual setup required:"
    echo "1. Copy this public key:"
    echo "$(cat ~/.ssh/$KEY_NAME.pub)"
    echo ""
    echo "2. SSH into your VM and run:"
    echo "   echo 'PUBLIC_KEY_CONTENT_HERE' >> ~/.ssh/authorized_keys"
    exit 1
fi

echo ""
echo "🧪 Testing SSH connection..."
if ssh -i ~/.ssh/$KEY_NAME -o ConnectTimeout=10 $VM_USER@$VM_IP "echo 'SSH connection successful!'"; then
    echo "✅ SSH connection test passed"
else
    echo "❌ SSH connection test failed"
    exit 1
fi

echo ""
echo "📋 GitHub Secret Setup Instructions:"
echo "=================================="
echo ""
echo "1. Copy the private key content below:"
echo "   (Select all and copy to clipboard)"
echo ""
echo "--- BEGIN PRIVATE KEY ---"
cat ~/.ssh/$KEY_NAME
echo "--- END PRIVATE KEY ---"
echo ""
echo "2. Go to your GitHub repository"
echo "3. Settings → Secrets and variables → Actions"
echo "4. Click 'New repository secret'"
echo "5. Name: VM_SSH_KEY"
echo "6. Value: Paste the private key content from above"
echo "7. Click 'Add secret'"
echo ""
echo "🚀 After adding the secret to GitHub:"
echo "   - Push any change to main branch"
echo "   - Check the Actions tab for automatic deployment"
echo ""
echo "🔧 Manual test command:"
echo "   ssh -i ~/.ssh/$KEY_NAME $VM_USER@$VM_IP 'cd /opt/linkshortener && ./manage-fullstack.sh status'"
echo ""
echo "✅ Setup complete! Don't forget to add the VM_SSH_KEY secret to GitHub."
