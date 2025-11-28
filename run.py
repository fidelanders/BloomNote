import uvicorn
import sys
import shutil
from app.main import app
from app.core.config import settings

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    # Check FFmpeg
    if not shutil.which("ffmpeg"):
        missing_deps.append("ffmpeg")
    
    # Check Python packages
    try:
        import fastapi
        import uvicorn
        import whisper
        import torch
        import pydub
        import aiofiles
        import slowapi
    except ImportError as e:
        missing_deps.append(f"Python package: {e.name if hasattr(e, 'name') else str(e)}")
    
    if missing_deps:
        print("❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\n🔧 Installation instructions:")
        print("   System dependencies (Linux/macOS):")
        print("     sudo apt-get install -y ffmpeg  # Ubuntu/Debian")
        print("     brew install ffmpeg             # macOS")
        print("   Python dependencies:")
        print("     pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are available")
    return True

if __name__ == "__main__":
    if check_dependencies():
        print(f"🚀 Starting Transcription API on {settings.HOST}:{settings.PORT}")
        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level=settings.LOG_LEVEL
        )
    else:
        sys.exit(1)