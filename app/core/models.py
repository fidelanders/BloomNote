import whisper
import torch
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Global model instance
model = None

async def load_whisper_model():
    """Load the Whisper model on startup"""
    global model
    try:
        logger.info("📥 Loading Whisper model...")
        
        # Use GPU if available, otherwise CPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"🔧 Using device: {device}")
        
        if device == "cuda":
            logger.info(f"🎯 GPU: {torch.cuda.get_device_name()}")
            logger.info(f"💾 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
        
        # Load the model
        model = whisper.load_model(settings.MODEL_SIZE, device=device)
        logger.info(f"✅ Whisper model '{settings.MODEL_SIZE}' loaded successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to load model: {str(e)}", exc_info=True)
        model = None
        raise e

def get_model():
    """Get the loaded model instance"""
    if model is None:
        raise RuntimeError("Model not loaded. Please wait for startup to complete.")
    return model