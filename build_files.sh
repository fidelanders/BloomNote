#!/bin/bash

echo "Installing system dependencies for Vercel..."
# Vercel might not allow apt-get, but we'll try
if command -v apt-get &> /dev/null; then
    apt-get update
    apt-get install -y ffmpeg
else
    echo "apt-get not available, using alternative methods..."
    # Download static ffmpeg binary
    wget https://github.com/ffbinaries/ffbinaries-prebuilt/releases/download/v4.2.1/ffmpeg-4.2.1-linux-64.zip
    unzip ffmpeg-4.2.1-linux-64.zip
    chmod +x ffmpeg
    export PATH=$PATH:$(pwd)
fi

echo "Build complete!"