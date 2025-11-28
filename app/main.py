# from fastapi import FastAPI
# from app.middleware.rate_limiter import limiter, RateLimitExceeded
# from app.middleware.cors import add_cors_middleware
# from app.routes import health, transcription, info
# from app.core.config import settings
# from app.core.models import load_whisper_model
# import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.rate_limiter import limiter
from app.routes import health, transcription, info
from app.core.config import settings
from app.core.models import load_whisper_model
import logging
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    """Application factory pattern"""
    app = FastAPI(
        title=settings.APP_TITLE,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOC_URL
    )
    
    # Add middleware
    # add_cors_middleware(app)
    # app.state.limiter = limiter
    # app.add_exception_handler(RateLimitExceeded, RateLimitExceeded._rate_limit_exceeded_handler)
    
        # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, prefix="/api/v1", tags=["Health"])
    app.include_router(info.router, prefix="/api/v1", tags=["Information"])
    app.include_router(transcription.router, prefix="/api/v1", tags=["Transcription"])
    
    # Add startup and shutdown events
    @app.on_event("startup")
    async def startup_event():
        logger.info("🚀 Starting Transcription API...")
        await load_whisper_model()
        logger.info("✅ Transcription API is ready!")
    
    @app.on_event("shutdown")
    def shutdown_event():
        logger.info("🛑 Shutting down Transcription API")
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "🎉 Transcription API",
            "status": "running",
            "version": settings.APP_VERSION,
            "docs": settings.DOCS_URL
        }
    
    return app

# Create app instance
app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL
    )