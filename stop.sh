#!/bin/bash

# Link Organizer Stop Script
# This script stops all running services

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_status "Stopping Link Organizer services..."

# Stop backend
if [ -f "backend/backend.pid" ]; then
    BACKEND_PID=$(cat backend/backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        print_status "Stopping backend server (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        sleep 2
        if kill -0 $BACKEND_PID 2>/dev/null; then
            print_warning "Backend didn't stop gracefully, force killing..."
            kill -9 $BACKEND_PID
        fi
        print_success "Backend stopped"
    else
        print_warning "Backend process not running"
    fi
    rm -f backend/backend.pid
else
    print_warning "Backend PID file not found"
fi

# Stop frontend
if [ -f "frontend/frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend/frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        print_status "Stopping frontend server (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        sleep 2
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            print_warning "Frontend didn't stop gracefully, force killing..."
            kill -9 $FRONTEND_PID
        fi
        print_success "Frontend stopped"
    else
        print_warning "Frontend process not running"
    fi
    rm -f frontend/frontend.pid
else
    print_warning "Frontend PID file not found"
fi

# Kill any remaining Node.js processes on port 3000
NODE_PID=$(lsof -ti:3000 2>/dev/null)
if [ ! -z "$NODE_PID" ]; then
    print_status "Killing remaining Node.js process on port 3000..."
    kill -9 $NODE_PID
    print_success "Node.js process killed"
fi

# Kill any remaining Python processes on port 5000
PYTHON_PID=$(lsof -ti:5000 2>/dev/null)
if [ ! -z "$PYTHON_PID" ]; then
    print_status "Killing remaining Python process on port 5000..."
    kill -9 $PYTHON_PID
    print_success "Python process killed"
fi

print_success "🎉 All services stopped successfully!" 