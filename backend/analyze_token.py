#!/usr/bin/env python3
"""
Token analyzer script to help debug authentication issues.
Run this to decode and analyze tokens from the frontend.
"""

import jwt
import json
import sys

def analyze_token(token_string):
    """Analyze a JWT token without validation."""
    try:
        # Decode header
        header = jwt.get_unverified_header(token_string)
        print("🔍 TOKEN HEADER:")
        print(json.dumps(header, indent=2))
        print()
        
        # Decode payload
        payload = jwt.decode(token_string, options={"verify_signature": False})
        print("🔍 TOKEN PAYLOAD:")
        print(json.dumps(payload, indent=2))
        print()
        
        # Analysis
        print("📊 TOKEN ANALYSIS:")
        audience = payload.get('aud', 'not set')
        token_type = payload.get('idtyp', payload.get('token_use', 'not set'))
        
        print(f"  Audience (aud): {audience}")
        print(f"  Token Type: {token_type}")
        print(f"  Issuer: {payload.get('iss', 'not set')}")
        print(f"  Subject: {payload.get('sub', 'not set')}")
        print(f"  User ID (oid): {payload.get('oid', 'not set')}")
        print(f"  Email: {payload.get('email', payload.get('upn', 'not set'))}")
        print(f"  Name: {payload.get('name', 'not set')}")
        print()
        
        # Determine token type
        if audience == "00000003-0000-0000-c000-000000000000":
            print("🚨 PROBLEM: This is a Microsoft Graph ACCESS TOKEN")
            print("   The frontend is sending the wrong token type!")
            print("   Expected: ID token with your app's client ID as audience")
        elif audience and len(audience) == 36:  # GUID format
            print("✅ GOOD: This appears to be an ID TOKEN")
            print("   This is the correct token type for authentication")
        else:
            print("❓ UNKNOWN: Token type unclear")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing token: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_token.py <token>")
        print("Example: python analyze_token.py eyJ0eXAiOiJKV1QiLCJhbGc...")
        sys.exit(1)
    
    token = sys.argv[1]
    if not analyze_token(token):
        sys.exit(1)
