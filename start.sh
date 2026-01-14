#!/bin/bash
# Start both backend and frontend

echo "Starting EIA Renewable Energy Dashboard..."

# Kill any existing processes on ports 8000 and 5173
fuser -k 8000/tcp 2>/dev/null
fuser -k 5173/tcp 2>/dev/null

# Start backend
echo "Starting backend on port 8000..."
cd /home/llm/jordan/backend
python3 main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 2

# Start frontend
echo "Starting frontend on port 5173..."
cd /home/llm/jordan/frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Dashboard is running!"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
