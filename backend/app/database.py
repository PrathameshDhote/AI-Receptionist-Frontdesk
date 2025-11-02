import firebase_admin
from firebase_admin import credentials, db
from typing import Optional
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json

from app.config import settings

# Initialize Firebase
_app: Optional[firebase_admin.App] = None
_executor = ThreadPoolExecutor(max_workers=10)

def init_firebase():
    """Initialize Firebase Admin SDK"""
    global _app
    
    cred_path = settings.FIREBASE_CREDENTIALS_PATH
    
    if not os.path.exists(cred_path):
        raise FileNotFoundError(
            f"❌ Firebase credentials not found at {cred_path}. "
            f"Download from Firebase Console and place it at that path.\n"
            f"Steps:\n"
            f"1. Go to Firebase Console\n"
            f"2. Project Settings → Service Accounts\n"
            f"3. Generate new private key\n"
            f"4. Save as {cred_path}"
        )
    
    try:
        cred = credentials.Certificate(cred_path)
        _app = firebase_admin.initialize_app(cred, {
            'databaseURL': settings.FIREBASE_DATABASE_URL
        })
        print("✅ Firebase initialized successfully")
        print(f"📍 Database URL: {settings.FIREBASE_DATABASE_URL}")
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        raise

def get_db_ref(path: str = "/"):
    """Get Firebase database reference"""
    if not _app:
        raise RuntimeError("Firebase not initialized. Call init_firebase() first")
    return db.reference(path, app=_app)

async def run_async(func, *args, **kwargs):
    """Run sync Firebase operations in thread pool (for async compatibility)"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, func, *args, **kwargs)

async def close_firebase():
    """Close Firebase connection"""
    global _app
    if _app:
        firebase_admin.delete_app(_app)
        _app = None
        print("🔌 Firebase connection closed")
        _executor.shutdown(wait=True)

def create_initial_data():
    """Create initial data structure in Firebase"""
    try:
        from datetime import datetime
        
        # Create help_requests node
        ref = get_db_ref("/help_requests")
        ref.set({
            "initialized": True,
            "created_at": datetime.utcnow().isoformat()  
        })
        
        # Create knowledge_base node
        ref = get_db_ref("/knowledge_base")
        ref.set({
            "initialized": True,
            "created_at": datetime.utcnow().isoformat()  
        })
        
        print("✅ Initial Firebase structure created")
    except Exception as e:
        print(f"⚠️ Note: Firebase structure may already exist: {e}")
