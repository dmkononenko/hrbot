#!/bin/bash

# HR Bot Development Startup Script
# This script starts ngrok for tunneling and the FastAPI server

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

# Kill any existing processes on ports 8000 and 4040
echo "🧹 Cleaning up existing processes..."
pkill -f "uvicorn.*8000" 2>/dev/null || true
pkill -f "ngrok" 2>/dev/null || true

# Wait a moment for processes to terminate
sleep 2

# Start ngrok in background
echo "� Starting ngrok..."
ngrok http 8000 > /dev/null &
NGROK_PID=$!

# Wait for ngrok to start
sleep 3

# Get ngrok URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*' | cut -d'"' -f4 | head -n 1)

if [ -z "$NGROK_URL" ]; then
    echo "❌ Error: Could not get ngrok URL"
    echo "Make sure ngrok is installed and running"
    kill $NGROK_PID
    exit 1
fi

echo "✅ Ngrok tunnel created: $NGROK_URL"

# Set webhook
WEBHOOK_URL="${NGROK_URL}/api/v1/bot/webhook"
echo "🔗 Setting Telegram webhook: $WEBHOOK_URL"

curl -X POST "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook?url=${WEBHOOK_URL}" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Webhook set successfully"
else
    echo "⚠️  Warning: Webhook setup may have failed"
fi

echo ""
echo "=============================="
echo "🎉 Development server ready!"
echo ""
echo "📡 API Server:  http://localhost:8000"
echo "📚 API Docs:     http://localhost:8000/docs"
echo "🔗 Ngrok URL:    $NGROK_URL"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=============================="
echo ""

# Start FastAPI server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Cleanup on exit
trap "echo ''; echo '🛑 Stopping ngrok...'; kill $NGROK_PID; exit" INT TERM
