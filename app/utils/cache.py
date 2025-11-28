from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Global cache storage
transcription_cache = {}

def cleanup_old_cache():
    """Remove cache entries older than 1 hour"""
    current_time = datetime.now()
    keys_to_remove = []
    
    for key, (timestamp, _) in transcription_cache.items():
        if current_time - timestamp > timedelta(hours=1):
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del transcription_cache[key]
    
    if keys_to_remove:
        logger.info(f"🧹 Cleaned up {len(keys_to_remove)} old cache entries")