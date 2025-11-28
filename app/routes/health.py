from fastapi import APIRouter, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from app.core.models import model
from app.utils.cache import cleanup_old_cache, transcription_cache
from datetime import datetime

router = APIRouter()
limiter = Limiter(key_func=lambda: "health")  # Simple limiter for health checks

@router.get("/health")
@limiter.limit("30/minute")
async def health(request: Request):
    """Health check endpoint"""
    cache_size = len(transcription_cache)
    cleanup_old_cache()
    
    return {
        "status": "healthy" if model is not None else "unhealthy",
        "model_loaded": model is not None,
        "device": "cuda" if model and hasattr(model, 'device') and 'cuda' in str(model.device) else "cpu",
        "cache_entries": cache_size,
        "timestamp": datetime.now().isoformat(),
        "service": "Transcription API"
    }

@router.get("/ready")
async def readiness_probe():
    """Kubernetes-style readiness probe"""
    if model is None:
        return {"status": "not ready", "message": "Model not loaded"}, 503
    return {"status": "ready", "message": "Service is ready to accept requests"}