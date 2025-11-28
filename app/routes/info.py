from fastapi import APIRouter, Request
import torch
from app.core.config import settings
from app.core.models import model

router = APIRouter()

@router.get("/info")
async def get_info(request: Request):
    """Get detailed API information"""
    gpu_info = None
    if torch.cuda.is_available():
        gpu_info = {
            "name": torch.cuda.get_device_name(),
            "memory_gb": round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 1)
        }
    
    return {
        "service": settings.APP_TITLE,
        "version": settings.APP_VERSION,
        "model_loaded": model is not None,
        "model_size": settings.MODEL_SIZE,
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "gpu_info": gpu_info,
        "supported_formats": settings.SUPPORTED_FORMATS,
        "max_file_size_mb": settings.MAX_FILE_SIZE / 1024 / 1024,
        "chunk_duration_minutes": settings.CHUNK_DURATION_MINUTES,
        "max_audio_duration_hours": settings.MAX_TOTAL_DURATION / 60 / 60,
        "rate_limit": settings.RATE_LIMIT,
        "features": ["unlimited_audio", "chunked_processing", "caching"]
    }

@router.get("/stats")
async def get_stats(request: Request):
    """Get API statistics"""
    from app.utils.cache import transcription_cache
    import json
    
    cache_size_mb = sum(len(json.dumps(result).encode('utf-8')) for _, (_, result) in transcription_cache.items()) / 1024 / 1024
    
    return {
        "cache_entries": len(transcription_cache),
        "cache_size_mb": round(cache_size_mb, 2),
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "model_size": settings.MODEL_SIZE
    }