#!/bin/bash

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing system dependencies..."
apt-get update
apt-get install -y ffmpeg

echo "Build complete!"