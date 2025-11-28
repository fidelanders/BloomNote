import os
import hashlib
import logging
from pydub import AudioSegment
from app.core.config import settings

logger = logging.getLogger(__name__)

def get_file_hash(file_content: bytes) -> str:
    """Generate a hash for caching"""
    return hashlib.md5(file_content).hexdigest()

def convert_to_wav(in_path: str, out_path: str) -> bool:
    """Convert any audio file to WAV format"""
    try:
        audio = AudioSegment.from_file(in_path)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(out_path, format="wav")
        logger.info(f"✅ Successfully converted {in_path} to WAV")
        return True
    except Exception as e:
        logger.error(f"❌ Audio conversion failed: {e}")
        return False