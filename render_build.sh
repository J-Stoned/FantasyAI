#!/usr/bin/env bash
# Build script for Render deployment

echo "Starting Render build..."

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs models

echo "Build complete!"