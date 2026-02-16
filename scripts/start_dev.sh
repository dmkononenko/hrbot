#!/bin/bash

# HR Bot Development Startup Script
# This script starts the FastAPI server

echo "🚀 HR Bot Development Startup"
echo "=============================="

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "❌ Error: backend/.env file not found!"
    echo "Please copy backend/.env.example to backend/.env and fill in your values."
    exit 1
fi

# Load environment variables
export $(cat backend/.env | grep -v '^#' | xargs)

# Check if BOT_TOKEN is set
if [ -z "$BOT_TOKEN" ]; then
    echo "❌ Error: BOT_TOKEN not set in backend/.env"
    exit 1
fi

# Kill any existing processes on port 8000
echo "🧹 Cleaning up existing processes..."
pkill -f "uvicorn.*8000" 2>/dev/null || true

# Wait a moment for processes to terminate
sleep 2

echo ""
echo "=============================="
echo "🎉 Development server ready!"
echo ""
echo "📡 API Server:  http://localhost:8000"
echo "📚 API Docs:     http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=============================="
echo ""

# Start FastAPI server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
