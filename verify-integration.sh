#!/bin/bash

# Link Shortener Integration Verification Script
# Use this to verify that the backend is properly integrated with your existing nginx

echo "🔍 Link Shortener Integration Verification"
echo "=========================================="
echo ""

# Check if backend is running
echo "1. Backend Service Status:"
if curl -s http://localhost:8000/health > /dev/null; then
    echo "   ✅ Backend is running on port 8000"
    curl -s http://localhost:8000/health | head -1
else
    echo "   ❌ Backend is not responding on port 8000"
    echo "   💡 Run: cd /opt/linkshortener && docker-compose up -d"
fi
echo ""

# Check nginx configuration
echo "2. Nginx Configuration:"
if sudo nginx -t 2>/dev/null; then
    echo "   ✅ Nginx configuration is valid"
else
    echo "   ❌ Nginx configuration has errors"
    echo "   💡 Run: sudo nginx -t"
fi
echo ""

# Check if domain resolves
echo "3. Domain Resolution:"
if dig +short links.miskakyto.fi > /dev/null 2>&1; then
    IP=$(dig +short links.miskakyto.fi | tail -1)
    echo "   ✅ links.miskakyto.fi resolves to: $IP"
    
    # Check if it's pointing to this server
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip)
    if [ "$IP" = "$SERVER_IP" ]; then
        echo "   ✅ Domain points to this server"
    else
        echo "   ⚠️  Domain points to $IP, but this server is $SERVER_IP"
    fi
else
    echo "   ❌ Could not resolve links.miskakyto.fi"
fi
echo ""

# Test API endpoints through nginx
echo "4. API Integration Test:"
if curl -s -k https://links.miskakyto.fi/health > /dev/null 2>&1; then
    echo "   ✅ HTTPS health check works"
elif curl -s http://links.miskakyto.fi/health > /dev/null 2>&1; then
    echo "   ⚠️  HTTP health check works (HTTPS might need setup)"
else
    echo "   ❌ Health check failed through nginx"
    echo "   💡 Check nginx configuration for /health location"
fi
echo ""

# Check SSL certificate
echo "5. SSL Certificate:"
if echo | openssl s_client -servername links.miskakyto.fi -connect links.miskakyto.fi:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null; then
    echo "   ✅ SSL certificate is present"
    EXPIRY=$(echo | openssl s_client -servername links.miskakyto.fi -connect links.miskakyto.fi:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null | grep notAfter | cut -d= -f2)
    echo "   📅 Certificate expires: $EXPIRY"
else
    echo "   ⚠️  SSL certificate not found or invalid"
    echo "   💡 Configure SSL in your nginx setup"
fi
echo ""

# Check ports
echo "6. Port Status:"
if netstat -tlnp 2>/dev/null | grep :8000 > /dev/null; then
    echo "   ✅ Port 8000 is listening (backend)"
else
    echo "   ❌ Port 8000 is not listening"
fi

if netstat -tlnp 2>/dev/null | grep :443 > /dev/null; then
    echo "   ✅ Port 443 is listening (HTTPS)"
else
    echo "   ❌ Port 443 is not listening"
fi

if netstat -tlnp 2>/dev/null | grep :80 > /dev/null; then
    echo "   ✅ Port 80 is listening (HTTP)"
else
    echo "   ❌ Port 80 is not listening"
fi
echo ""

# Test example short URL creation (if backend supports it)
echo "7. Backend Functionality Test:"
# Note: This would require authentication, so we just test the endpoint availability
if curl -s -X OPTIONS http://localhost:8000/api/links > /dev/null 2>&1; then
    echo "   ✅ API endpoints are accessible"
else
    echo "   ⚠️  API endpoints might require authentication"
fi
echo ""

echo "🎯 Integration Summary:"
echo "======================"
echo "Backend URL: http://localhost:8000"
echo "Public URL: https://links.miskakyto.fi"
echo "Health Check: https://links.miskakyto.fi/health"
echo "API Base: https://links.miskakyto.fi/api/"
echo ""
echo "💡 Next Steps:"
echo "- Test creating a short link through your frontend"
echo "- Monitor logs: ./manage-backend.sh logs"
echo "- Check backend status: ./manage-backend.sh status"
