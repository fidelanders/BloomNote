import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.main import app

# Vercel requires this
if __name__ == "__main__":
    # This won't run on Vercel, but keeps the file valid
    pass