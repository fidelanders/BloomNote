from fastapi import APIRouter, UploadFile, File, HTTPException, Request, BackgroundTasks
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
import os
import tempfile
import aiofiles
from datetime import datetime
from app.core.config import settings
from app.core.models import get_model, model
from app.core.transcribe import transcribe_large_audio, transcribe_short_audio
from app.utils.file_utils import convert_to_wav, get_file_hash
from app.utils.cache import transcription_cache, cleanup_old_cache
import logging

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)

@router.post("/transcribe")
@limiter.limit(settings.RATE_LIMIT)
async def transcribe_audio(
    request: Request,
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(..., description="Audio file to transcribe"),
    language: str = None,
    task: str = "transcribe",
    use_cache: bool = True
):
    """Transcribe audio file to text - supports unlimited length"""
    if model is None:
        raise HTTPException(status_code=503, detail="Service unavailable: Model not loaded")
    
    # Validate file type
    if not audio.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_ext = os.path.splitext(audio.filename.lower())[1]
    if file_ext not in settings.SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail=f"Unsupported file format")
    
    # Read and validate file
    content = await audio.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Cache check
    file_hash = get_file_hash(content)
    if use_cache and file_hash in transcription_cache:
        logger.info("♻️ Using cached transcription")
        _, cached_result = transcription_cache[file_hash]
        return cached_result
    
    temp_input = temp_wav = None
    
    try:
        # Save uploaded file
        temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
        async with aiofiles.open(temp_input.name, 'wb') as f:
            await f.write(content)
        
        # Convert to WAV if needed
        if file_ext != '.wav':
            temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_wav.close()
            if not convert_to_wav(temp_input.name, temp_wav.name):
                raise HTTPException(status_code=400, detail="Failed to process audio file")
            audio_path = temp_wav.name
        else:
            audio_path = temp_input.name
        
        # Get audio duration and decide processing method
        from pydub import AudioSegment
        audio_duration = len(AudioSegment.from_file(audio_path)) / 1000
        use_chunked_processing = audio_duration > 5 * 60  # 5 minutes
        
        # Transcribe
        logger.info(f"🎙️ Starting transcription for {audio.filename}")
        
        if use_chunked_processing:
            result = transcribe_large_audio(audio_path, language, task)
        else:
            result = transcribe_short_audio(audio_path, language, task)
        
        logger.info("✅ Transcription completed")
        
        # Build response
        response_data = {
            "text": result["text"].strip(),
            "language": result.get("language", "unknown"),
            "duration_seconds": audio_duration,
            "chunked_processing": use_chunked_processing,
            "segments": result.get("segments", []),
            "metadata": {
                "filename": audio.filename,
                "model_size": settings.MODEL_SIZE,
                "device": "cuda" if get_model().device.type == "cuda" else "cpu",
                "file_size_mb": round(len(content) / 1024 / 1024, 2),
            }
        }
        
        # Cache result
        if use_cache:
            transcription_cache[file_hash] = (datetime.now(), response_data)
        
        return response_data
        
    except Exception as e:
        logger.error(f"❌ Transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        # Cleanup
        for temp_file in [temp_input, temp_wav]:
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to delete temp file: {e}")