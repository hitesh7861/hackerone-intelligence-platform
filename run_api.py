#!/usr/bin/env python3
"""
Start the FastAPI server
"""
import uvicorn

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║   HackerOne Intelligence Platform - API Server            ║
    ╚═══════════════════════════════════════════════════════════╝
    
    Starting API server...
    API Documentation: http://localhost:8000/docs
    Authentication required for most endpoints
    
    Demo Users:
    - admin / admin123 (full access)
    - mailru / mailru123 (customer access)
    - shopify / shopify123 (customer access)
    """)
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
