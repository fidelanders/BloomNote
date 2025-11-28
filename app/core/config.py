import os
from typing import Optional

class Settings:
    """Application settings configuration"""
    
    # App Configuration
    APP_TITLE: str = "Transcription API"
    APP_DESCRIPTION: str = "High-performance audio transcription service using OpenAI Whisper"
    APP_VERSION: str = "2.1.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8082"))
    
    # API Configuration
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    API_PREFIX: str = "/api/v1"
    
    # Model Configuration
    MODEL_SIZE: str = os.getenv("MODEL_SIZE", "small")
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    CHUNK_DURATION_MINUTES: int = 10
    MAX_TOTAL_DURATION: int = 240 * 60  # 4 hours
    
    # Rate Limiting
    RATE_LIMIT: str = os.getenv("RATE_LIMIT", "10/minute")
    
    # Supported Formats
    SUPPORTED_FORMATS: list = ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac', '.wma', '.mp4', '.m4v', '.mov']
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

settings = Settings()