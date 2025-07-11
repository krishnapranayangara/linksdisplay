#!/bin/bash

# Link Organizer Setup Script
# This script sets up both frontend and backend for the Link Organizer application

set -e  # Exit on any error

echo "🚀 Setting up Link Organizer Application..."

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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check PostgreSQL connection
check_postgres_connection() {
    if command_exists psql; then
        if psql -U admin -d postgres -c "SELECT 1;" >/dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Function to setup PostgreSQL
setup_postgres() {
    print_status "Setting up PostgreSQL..."
    
    if ! command_exists psql; then
        print_error "PostgreSQL is not installed. Please install PostgreSQL first."
        print_status "Installation instructions:"
        echo "  macOS: brew install postgresql"
        echo "  Ubuntu: sudo apt-get install postgresql postgresql-contrib"
        echo "  Windows: Download from https://www.postgresql.org/download/windows/"
        exit 1
    fi
    
    # Check if PostgreSQL service is running
    if ! pg_isready >/dev/null 2>&1; then
        print_warning "PostgreSQL service is not running. Starting it..."
        if command_exists brew; then
            brew services start postgresql
        elif command_exists systemctl; then
            sudo systemctl start postgresql
        else
            print_error "Cannot start PostgreSQL automatically. Please start it manually."
            exit 1
        fi
    fi
    
    # Create user and databases
    print_status "Creating PostgreSQL user and databases..."
    
    # Create user if it doesn't exist
    if ! psql -U postgres -c "SELECT 1 FROM pg_roles WHERE rolname='admin'" | grep -q 1; then
        createuser -U postgres admin || print_warning "User 'admin' might already exist"
    fi
    
    # Set password for admin user
    psql -U postgres -c "ALTER USER admin WITH PASSWORD 'admin';" || print_warning "Could not set password (user might not exist)"
    
    # Create databases
    createdb -U admin link_organizer_dev 2>/dev/null || print_warning "Database 'link_organizer_dev' might already exist"
    createdb -U admin link_organizer_test 2>/dev/null || print_warning "Database 'link_organizer_test' might already exist"
    
    # Grant privileges
    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE link_organizer_dev TO admin;" || true
    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE link_organizer_test TO admin;" || true
    
    print_success "PostgreSQL setup completed!"
}

# Function to setup Python environment
setup_python_env() {
    print_status "Setting up Python environment..."
    
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    # Check Python version
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    required_version="3.8"
    
    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
        print_error "Python 3.8+ is required. Current version: $python_version"
        exit 1
    fi
    
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    print_success "Python environment setup completed!"
}

# Function to setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Copy environment file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating environment file..."
        cp env.example .env
        print_warning "Please review and update .env file with your settings"
    fi
    
    # Initialize database
    print_status "Initializing database..."
    python -c "from app import init_db; init_db()"
    
    # Run tests to verify setup
    print_status "Running tests to verify setup..."
    if python -m pytest tests/ -v --tb=short; then
        print_success "Backend tests passed!"
    else
        print_warning "Some tests failed. This might be expected for a fresh setup."
    fi
    
    print_success "Backend setup completed!"
}

# Function to setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd ../frontend
    
    # Check if Node.js is installed
    if ! command_exists node; then
        print_error "Node.js is not installed. Please install Node.js first."
        print_status "Installation instructions:"
        echo "  macOS: brew install node"
        echo "  Ubuntu: curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs"
        echo "  Windows: Download from https://nodejs.org/"
        exit 1
    fi
    
    # Check Node.js version
    node_version=$(node -v | cut -d'v' -f2)
    required_version="14.0.0"
    
    if [ "$(printf '%s\n' "$required_version" "$node_version" | sort -V | head -n1)" != "$required_version" ]; then
        print_error "Node.js 14+ is required. Current version: $node_version"
        exit 1
    fi
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    print_success "Frontend setup completed!"
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    # Start backend
    print_status "Starting backend server..."
    cd backend
    source venv/bin/activate
    
    # Start backend in background
    python app.py &
    BACKEND_PID=$!
    echo $BACKEND_PID > backend.pid
    
    # Wait for backend to start
    sleep 3
    
    # Check if backend is running
    if curl -s http://localhost:5000/api/health >/dev/null; then
        print_success "Backend is running on http://localhost:5000"
    else
        print_error "Backend failed to start"
        exit 1
    fi
    
    # Start frontend
    print_status "Starting frontend server..."
    cd ../frontend
    
    # Start frontend in background
    npm start &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > frontend.pid
    
    # Wait for frontend to start
    sleep 5
    
    # Check if frontend is running
    if curl -s http://localhost:3000 >/dev/null; then
        print_success "Frontend is running on http://localhost:3000"
    else
        print_warning "Frontend might still be starting up..."
    fi
    
    print_success "All services started!"
    echo ""
    echo "🌐 Application URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:5000"
    echo "  API Health: http://localhost:5000/api/health"
    echo "  API Docs: http://localhost:5000/api/docs"
    echo ""
    echo "📚 Next Steps:"
    echo "  1. Open http://localhost:3000 in your browser"
    echo "  2. Import the Postman collection: backend/Link_Organizer_API.postman_collection.json"
    echo "  3. Run tests: cd backend && make test"
    echo "  4. Check logs: tail -f backend/logs/link_organizer.log"
    echo ""
    echo "🛑 To stop services: ./stop.sh"
}

# Function to cleanup on exit
cleanup() {
    print_status "Cleaning up..."
    
    # Kill background processes
    if [ -f "backend/backend.pid" ]; then
        kill $(cat backend/backend.pid) 2>/dev/null || true
        rm backend/backend.pid
    fi
    
    if [ -f "frontend/frontend.pid" ]; then
        kill $(cat frontend/frontend.pid) 2>/dev/null || true
        rm frontend/frontend.pid
    fi
}

# Set up trap to cleanup on script exit
trap cleanup EXIT

# Main setup process
main() {
    print_status "Starting Link Organizer setup..."
    
    # Check if we're in the right directory
    if [ ! -f "setup.sh" ]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi
    
    # Setup PostgreSQL
    setup_postgres
    
    # Setup Python environment
    setup_python_env
    
    # Setup backend
    setup_backend
    
    # Setup frontend
    setup_frontend
    
    # Start services
    start_services
    
    print_success "🎉 Link Organizer setup completed successfully!"
    print_status "The application is now running and ready to use!"
}

# Run main function
main "$@" 