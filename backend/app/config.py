from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = "Frontdesk AI"
    DEBUG: bool = True
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = os.getenv(
        "FIREBASE_CREDENTIALS_PATH", 
        "config/firebase_config.json"
    )
    FIREBASE_DATABASE_URL: str = os.getenv(
        "FIREBASE_DATABASE_URL",
        "https://your-project.firebaseio.com"
    )
    
    # LiveKit
    LIVEKIT_URL: str = "ws://localhost:7880"
    LIVEKIT_API_KEY: str = os.getenv("LIVEKIT_API_KEY", "")
    LIVEKIT_API_SECRET: str = os.getenv("LIVEKIT_API_SECRET", "")
    
    # AI/LLM
    MEGALLM_API_KEY: str = os.getenv("MEGALLM_API_KEY", "")
    MEGALLM_BASE_URL: str = os.getenv(
        "MEGALLM_BASE_URL", 
        "https://ai.megallm.io/v1"
    )
    MEGALLM_MODEL: str = os.getenv("MEGALLM_MODEL", "gpt-5")
    DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY", "")
    ELEVEN_API_KEY: str = os.getenv("ELEVEN_API_KEY", "")
    
    # System
    HELP_REQUEST_TIMEOUT_HOURS: int = 2
    CUSTOMER_FOLLOWUP_TEMPLATE: str = "Hi! Your question was: {question}. Answer: {answer}"
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    # CORS
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
