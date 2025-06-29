#!/usr/bin/env python3
"""
Link Shortener Backend Server
Run this script to start the FastAPI development server.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
