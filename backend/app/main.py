from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import os

from app.config import settings
from app.database import init_firebase, close_firebase, create_initial_data
from app.services.timeout_service import TimeoutService
from app.services.notification_service import notification_service
from app.api.routes import help_requests, knowledge_base, websocket

# Lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("\n" + "="*60)
    print("🚀 Starting Frontdesk AI Server...")
    print("="*60)
    
    try:
        init_firebase()
        create_initial_data()
        print("✅ Firebase initialized and ready")
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        print("Make sure:")
        print("1. config/firebase_config.json exists")
        print("2. FIREBASE_DATABASE_URL is set in .env")
        raise
    
    # Start timeout service
    timeout_service = TimeoutService(notification_service)
    await timeout_service.start()
    
    print("="*60)
    print("✅ All services started")
    print("="*60 + "\n")
    
    yield
    
    # Shutdown
    print("\n" + "="*60)
    print("🛑 Shutting down...")
    print("="*60)
    await timeout_service.stop()
    await close_firebase()
    print("✅ Server shutdown complete\n")

# Create app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="Human-in-the-Loop AI Salon Receptionist",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      
        "http://localhost:3000",      
        "http://127.0.0.1:5173",      
        "http://127.0.0.1:3000",      
        "*"                            
    ],
    allow_credentials=True,
    allow_methods=["*"],              
    allow_headers=["*"],              
)

# Include routers
app.include_router(help_requests.router)
app.include_router(knowledge_base.router)
app.include_router(websocket.router)

# ======================== Root Routes ========================

@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "message": "🎤 Frontdesk AI - Human-in-the-Loop Receptionist",
        "version": "0.1.0",
        "status": "running",
        "database": "Firebase Realtime",
        "endpoints": {
            "help_requests": "/api/help-requests",
            "knowledge_base": "/api/knowledge-base",
            "websocket": "ws://localhost:8000/ws/supervisor",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "firebase",
        "environment": "development" if settings.DEBUG else "production"
    }

@app.get("/config")
async def get_config():
    """Get current configuration (non-sensitive)"""
    return {
        "project_name": settings.PROJECT_NAME,
        "debug": settings.DEBUG,
        "timeout_hours": settings.HELP_REQUEST_TIMEOUT_HOURS,
        "allowed_origins": settings.ALLOWED_ORIGINS,
        "firebase_database_url": settings.FIREBASE_DATABASE_URL
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
