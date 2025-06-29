from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import aiosqlite
import shortuuid
import validators
from datetime import datetime, timezone
import httpx
import json
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional, List
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test mode configuration
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

app = FastAPI(title="Link Shortener API", version="1.0.0")

# CORS configuration
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
# Security configuration
security = HTTPBearer(auto_error=not TEST_MODE)

# Environment variables
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./links.db")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# Pydantic models
class LinkCreate(BaseModel):
    original_url: str
    custom_short_code: Optional[str] = None
    description: Optional[str] = None

class LinkResponse(BaseModel):
    id: str
    original_url: str
    short_code: str
    short_url: str
    description: Optional[str]
    click_count: int
    created_at: str
    created_by: str
    created_by_name: Optional[str]
    tenant_id: str

class LinkUpdate(BaseModel):
    description: Optional[str] = None

class AnalyticsResponse(BaseModel):
    link_id: str
    click_count: int
    recent_clicks: List[dict]

# Database path helper
def get_db_path():
    # Use test database if environment variable is set
    test_db = os.getenv('TEST_DB_PATH')
    if test_db:
        return test_db
    
    # In production, use /app/data directory for persistence
    if os.getenv('PRODUCTION', 'false').lower() == 'true':
        os.makedirs('/app/data', exist_ok=True)
        return '/app/data/links.db'
    
    # Default to local directory for development
    return 'links.db'

# Database initialization
async def init_db():
    async with aiosqlite.connect(get_db_path()) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS links (
                id TEXT PRIMARY KEY,
                original_url TEXT NOT NULL,
                short_code TEXT UNIQUE NOT NULL,
                description TEXT,
                click_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT NOT NULL,
                created_by_name TEXT,
                tenant_id TEXT NOT NULL
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                link_id TEXT NOT NULL,
                clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (link_id) REFERENCES links (id)
            )
        """)
        
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_links_tenant ON links(tenant_id)
        """)
        
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_links_created_by ON links(created_by)
        """)
        
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_clicks_link_id ON clicks(link_id)
        """)
        
        await db.commit()

# Import authentication helper
from auth import token_validator

# Authentication helper
async def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if TEST_MODE:
        # In test mode, return mock user data regardless of credentials
        logger.info("🧪 Using test mode authentication")
        return {
            "oid": "test-user-id",
            "name": "Test User",
            "email": "test@example.com",
            "tid": "test-tenant-id"
        }
    
    if not credentials:
        logger.warning("❌ No credentials provided")
        raise HTTPException(status_code=403, detail="Authentication required")
    
    token = credentials.credentials
    logger.info(f"🔑 Validating token (length: {len(token)})")
    
    try:
        user_data = token_validator.validate_token(token)
        logger.info(f"✅ Token validation successful for user: {user_data.get('email', 'unknown')}")
        return user_data
    except HTTPException as e:
        logger.error(f"❌ Token validation failed: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"💥 Unexpected error during token validation: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

# Helper functions
def generate_short_code():
    return shortuuid.ShortUUID().random(length=6)

async def get_link_by_short_code(short_code: str):
    async with aiosqlite.connect(get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM links WHERE short_code = ?", (short_code,)
        )
        return await cursor.fetchone()

async def increment_click_count(link_id: str, ip_address: str, user_agent: str):
    async with aiosqlite.connect(get_db_path()) as db:
        await db.execute(
            "UPDATE links SET click_count = click_count + 1 WHERE id = ?", (link_id,)
        )
        await db.execute(
            "INSERT INTO clicks (link_id, ip_address, user_agent) VALUES (?, ?, ?)",
            (link_id, ip_address, user_agent)
        )
        await db.commit()

# API Routes
@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"message": "Link Shortener API", "version": "1.0.0"}

@app.get("/debug/routes")
async def debug_routes():
    """Debug endpoint to list all registered routes"""
    return {
        "message": "Routes debug endpoint",
        "available_endpoints": [
            "GET /",
            "GET /api/health", 
            "GET /debug/routes",
            "POST /api/links",
            "GET /api/links",
            "GET /api/links/{link_id}",
            "PUT /api/links/{link_id}",
            "DELETE /api/links/{link_id}",
            "GET /api/links/{link_id}/analytics",
            "GET /{short_code}"
        ]
    }

@app.get("/api/debug/auth")
async def debug_auth():
    """Debug endpoint to check authentication status (public access)"""
    return {
        "test_mode": TEST_MODE,
        "azure_tenant_id": AZURE_TENANT_ID is not None,
        "azure_client_id": os.getenv("AZURE_CLIENT_ID") is not None,
        "azure_tenant_id_value": AZURE_TENANT_ID[:8] + "..." if AZURE_TENANT_ID else None,
        "azure_client_id_value": (os.getenv("AZURE_CLIENT_ID") or "")[:8] + "..." if os.getenv("AZURE_CLIENT_ID") else None,
        "base_url": BASE_URL,
        "cors_origins": os.getenv("ALLOWED_ORIGINS", "http://localhost:3000"),
        "environment": "production" if os.getenv('PRODUCTION', 'false').lower() == 'true' else "development"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring and deployment"""
    try:
        # Test database connection
        async with aiosqlite.connect(get_db_path()) as db:
            await db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "service": "Link Shortener API",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail={
            "status": "unhealthy",
            "service": "Link Shortener API", 
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

@app.post("/api/links", response_model=LinkResponse)
async def create_link(
    link_data: LinkCreate,
    user: dict = Depends(verify_token)
):
    # Validate URL
    if not validators.url(link_data.original_url):
        raise HTTPException(status_code=400, detail="Invalid URL")
    
    # Generate or use custom short code
    short_code = link_data.custom_short_code or generate_short_code()
    
    # Check if custom short code already exists
    if link_data.custom_short_code:
        existing_link = await get_link_by_short_code(short_code)
        if existing_link:
            raise HTTPException(status_code=400, detail="Custom short code already exists")
    
    # Create link
    link_id = shortuuid.uuid()
    created_at = datetime.now(timezone.utc).isoformat()
    
    async with aiosqlite.connect(get_db_path()) as db:
        await db.execute("""
            INSERT INTO links (id, original_url, short_code, description, created_by, created_by_name, tenant_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            link_id,
            link_data.original_url,
            short_code,
            link_data.description,
            user["oid"],
            user.get("name", "Unknown User"),
            user["tid"]
        ))
        await db.commit()
    
    return LinkResponse(
        id=link_id,
        original_url=link_data.original_url,
        short_code=short_code,
        short_url=f"{BASE_URL}/{short_code}",
        description=link_data.description,
        click_count=0,
        created_at=created_at,
        created_by=user["oid"],
        created_by_name=user.get("name", "Unknown User"),
        tenant_id=user["tid"]
    )

@app.get("/api/links", response_model=List[LinkResponse])
async def get_links(
    user: dict = Depends(verify_token)
):
    async with aiosqlite.connect(get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT * FROM links 
            WHERE tenant_id = ? 
            ORDER BY created_at DESC
        """, (user["tid"],))
        
        links = await cursor.fetchall()
        
        return [
            LinkResponse(
                id=link["id"],
                original_url=link["original_url"],
                short_code=link["short_code"],
                short_url=f"{BASE_URL}/{link['short_code']}",
                description=link["description"],
                click_count=link["click_count"],
                created_at=link["created_at"],
                created_by=link["created_by"],
                created_by_name=link["created_by_name"],
                tenant_id=link["tenant_id"]
            )
            for link in links
        ]

@app.get("/api/links/{link_id}", response_model=LinkResponse)
async def get_link(
    link_id: str,
    user: dict = Depends(verify_token)
):
    async with aiosqlite.connect(get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT * FROM links 
            WHERE id = ? AND tenant_id = ?
        """, (link_id, user["tid"]))
        
        link = await cursor.fetchone()
        
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")
        
        return LinkResponse(
            id=link["id"],
            original_url=link["original_url"],
            short_code=link["short_code"],
            short_url=f"{BASE_URL}/{link['short_code']}",
            description=link["description"],
            click_count=link["click_count"],
            created_at=link["created_at"],
            created_by=link["created_by"],
            created_by_name=link["created_by_name"],
            tenant_id=link["tenant_id"]
        )

@app.put("/api/links/{link_id}", response_model=LinkResponse)
async def update_link(
    link_id: str,
    link_update: LinkUpdate,
    user: dict = Depends(verify_token)
):
    async with aiosqlite.connect(get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        
        # Check if link exists and belongs to user's tenant
        cursor = await db.execute("""
            SELECT * FROM links 
            WHERE id = ? AND tenant_id = ?
        """, (link_id, user["tid"]))
        
        link = await cursor.fetchone()
        
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")
        
        # Update link
        await db.execute("""
            UPDATE links 
            SET description = ? 
            WHERE id = ?
        """, (link_update.description, link_id))
        
        await db.commit()
        
        # Return updated link
        cursor = await db.execute("SELECT * FROM links WHERE id = ?", (link_id,))
        updated_link = await cursor.fetchone()
        
        if not updated_link:
            raise HTTPException(status_code=500, detail="Failed to retrieve updated link")
        
        return LinkResponse(
            id=updated_link["id"],
            original_url=updated_link["original_url"],
            short_code=updated_link["short_code"],
            short_url=f"{BASE_URL}/{updated_link['short_code']}",
            description=updated_link["description"],
            click_count=updated_link["click_count"],
            created_at=updated_link["created_at"],
            created_by=updated_link["created_by"],
            created_by_name=updated_link["created_by_name"],
            tenant_id=updated_link["tenant_id"]
        )

@app.delete("/api/links/{link_id}")
async def delete_link(
    link_id: str,
    user: dict = Depends(verify_token)
):
    async with aiosqlite.connect(get_db_path()) as db:
        # Check if link exists and belongs to user's tenant
        cursor = await db.execute("""
            SELECT * FROM links 
            WHERE id = ? AND tenant_id = ?
        """, (link_id, user["tid"]))
        
        link = await cursor.fetchone()
        
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")
        
        # Delete associated clicks first
        await db.execute("DELETE FROM clicks WHERE link_id = ?", (link_id,))
        
        # Delete link
        await db.execute("DELETE FROM links WHERE id = ?", (link_id,))
        await db.commit()
        
        return {"message": "Link deleted successfully"}

@app.get("/api/links/{link_id}/analytics", response_model=AnalyticsResponse)
async def get_link_analytics(
    link_id: str,
    user: dict = Depends(verify_token)
):
    async with aiosqlite.connect(get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        
        # Check if link exists and belongs to user's tenant
        cursor = await db.execute("""
            SELECT * FROM links 
            WHERE id = ? AND tenant_id = ?
        """, (link_id, user["tid"]))
        
        link = await cursor.fetchone()
        
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")
        
        # Get recent clicks
        cursor = await db.execute("""
            SELECT clicked_at, ip_address 
            FROM clicks 
            WHERE link_id = ? 
            ORDER BY clicked_at DESC 
            LIMIT 100
        """, (link_id,))
        
        clicks = await cursor.fetchall()
        
        return AnalyticsResponse(
            link_id=link_id,
            click_count=link["click_count"],
            recent_clicks=[
                {
                    "clicked_at": click["clicked_at"],
                    "ip_address": click["ip_address"]
                }
                for click in clicks
            ]
        )

# URL redirection endpoint
@app.get("/{short_code}")
async def redirect_to_original(short_code: str, request: Request):
    link = await get_link_by_short_code(short_code)
    
    if not link:
        raise HTTPException(status_code=404, detail="Short link not found")
    
    # Get client info
    client_ip = getattr(request.client, 'host', 'unknown') if request.client else 'unknown'
    user_agent = request.headers.get("user-agent", "")
    
    # Increment click count
    await increment_click_count(link["id"], client_ip, user_agent)
    
    return RedirectResponse(url=link["original_url"], status_code=302)

@app.post("/api/debug/token")
async def debug_token_validation(token_data: dict):
    """Debug endpoint to test token validation with detailed logging"""
    if not token_data.get("token"):
        return {"error": "No token provided", "usage": "POST with JSON: {\"token\": \"your_token_here\"}"}
    
    token = token_data["token"]
    
    try:
        # Import here to avoid issues
        from auth import token_validator
        
        logger.info(f"🔍 Debug: Validating token (length: {len(token)})")
        logger.info(f"🔍 Debug: Token starts with: {token[:20]}...")
        
        user_data = token_validator.validate_token(token)
        
        return {
            "success": True,
            "message": "Token validation successful",
            "user_data": user_data,
            "token_length": len(token),
            "token_preview": token[:20] + "..."
        }
        
    except HTTPException as e:
        logger.error(f"🔍 Debug: HTTPException during validation: {e.detail}")
        return {
            "success": False,
            "error_type": "HTTPException",
            "error_detail": e.detail,
            "status_code": e.status_code,
            "token_length": len(token),
            "token_preview": token[:20] + "..."
        }
        
    except Exception as e:
        logger.error(f"🔍 Debug: Unexpected error: {str(e)}")
        return {
            "success": False,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "token_length": len(token),
            "token_preview": token[:20] + "..."
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
