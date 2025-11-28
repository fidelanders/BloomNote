import tempfile
import os
import uuid
import logging
from pydub import AudioSegment
from typing import Dict, Any, Optional
from app.core.models import get_model
from app.core.config import settings

logger = logging.getLogger(__name__)

def transcribe_large_audio(audio_path: str, language: Optional[str] = None, task: str = "transcribe") -> Dict[str, Any]:
    """Transcribe long audio in chunks and combine results seamlessly"""
    try:
        model = get_model()
        audio = AudioSegment.from_file(audio_path)
        total_duration_ms = len(audio)
        total_duration_minutes = total_duration_ms / 1000 / 60
        
        logger.info(f"📊 Audio length: {total_duration_minutes:.1f} minutes")
        
        # Safety limit
        if total_duration_ms > settings.MAX_TOTAL_DURATION * 1000:
            raise ValueError(f"Audio too long: {total_duration_minutes:.1f} minutes exceeds maximum {settings.MAX_TOTAL_DURATION/60:.1f} minutes")
        
        chunk_length_ms = settings.CHUNK_DURATION_MINUTES * 60 * 1000
        chunks = []
        
        # Split audio into chunks with 1-second overlap
        for i in range(0, total_duration_ms, chunk_length_ms - 1000):
            chunk_end = min(i + chunk_length_ms, total_duration_ms)
            chunk = audio[i:chunk_end]
            chunks.append(chunk)
        
        logger.info(f"📦 Splitting into {len(chunks)} chunks...")
        
        all_segments = []
        full_text = []
        
        for i, chunk in enumerate(chunks):
            chunk_start_minutes = (i * (chunk_length_ms - 1000)) / 1000 / 60
            logger.info(f"🔊 Processing chunk {i+1}/{len(chunks)}...")
            
            chunk_path = f"temp_chunk_{i}_{uuid.uuid4().hex}.wav"
            chunk.export(chunk_path, format="wav")
            
            # Transcribe chunk
            options = {
                "fp16": False,
                "language": language,
                "task": task
            }
            options = {k: v for k, v in options.items() if v is not None}
            
            result = model.transcribe(chunk_path, **options)
            
            # Adjust timestamps for chunk position
            chunk_offset = i * ((chunk_length_ms - 1000) / 1000)
            for segment in result["segments"]:
                segment["start"] += chunk_offset
                segment["end"] += chunk_offset
                all_segments.append(segment)
            
            full_text.append(result["text"].strip())
            
            # Cleanup chunk file
            os.remove(chunk_path)
        
        combined_text = " ".join(full_text)
        logger.info(f"✅ Successfully processed {total_duration_minutes:.1f} minutes of audio")
        
        return {
            "text": combined_text,
            "segments": all_segments,
            "language": result.get("language", "unknown")
        }
        
    except Exception as e:
        logger.error(f"❌ Chunked transcription failed: {e}")
        raise e

def transcribe_short_audio(audio_path: str, language: Optional[str] = None, task: str = "transcribe") -> Dict[str, Any]:
    """Transcribe short audio files in one go"""
    model = get_model()
    options = {
        "fp16": False,
        "language": language,
        "task": task
    }
    options = {k: v for k, v in options.items() if v is not None}
    
    return model.transcribe(audio_path, **options)