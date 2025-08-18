#!/bin/bash

# Nutrigence Local Development Setup Script
# This script will help you set up the project on your local machine

set -e  # Exit on any error

echo "🚀 Nutrigence Local Development Setup"
echo "====================================="

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

# Check prerequisites
print_status "Checking prerequisites..."

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -ge 20 ]; then
        print_success "Node.js $(node --version) found"
    else
        print_error "Node.js version 20+ required. Found: $(node --version)"
        exit 1
    fi
else
    print_error "Node.js not found. Please install Node.js 20+ from https://nodejs.org/"
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f2)
    if [ "$PYTHON_VERSION" -ge 9 ]; then
        print_success "Python $(python3 --version) found"
    else
        print_error "Python 3.9+ required. Found: $(python3 --version)"
        exit 1
    fi
else
    print_error "Python 3.9+ not found. Please install Python from https://www.python.org/downloads/"
    exit 1
fi

# Check Git
if command -v git &> /dev/null; then
    print_success "Git $(git --version) found"
else
    print_error "Git not found. Please install Git from https://git-scm.com/downloads"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    print_error "Please run this script from the project root directory (where README.md is located)"
    exit 1
fi

print_success "All prerequisites met!"

# Create environment files
print_status "Setting up environment files..."

# Backend environment
if [ ! -f "backend/.env" ]; then
    cat > backend/.env << EOF
# Database Configuration
DATABASE_URL=postgresql://nutrigence_user:password@localhost:5432/nutrigence_db

# Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment
ENVIRONMENT=development
FRONTEND_URL=http://localhost:5173
EOF
    print_success "Created backend/.env"
else
    print_warning "backend/.env already exists, skipping..."
fi

# Frontend environment
if [ ! -f "frontend/.env" ]; then
    cat > frontend/.env << EOF
# API Configuration
VITE_API_URL=http://localhost:8000

# Environment
VITE_ENVIRONMENT=development
EOF
    print_success "Created frontend/.env"
else
    print_warning "frontend/.env already exists, skipping..."
fi

# Setup backend
print_status "Setting up backend..."

cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
print_status "Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt
print_success "Backend dependencies installed"

cd ..

# Setup frontend
print_status "Setting up frontend..."

cd frontend

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
npm install
print_success "Frontend dependencies installed"

cd ..

# Database setup
print_status "Setting up database..."

# Check if Docker is available
if command -v docker &> /dev/null; then
    print_status "Docker found. Setting up PostgreSQL with Docker..."
    
    # Check if container already exists
    if docker ps -a --format 'table {{.Names}}' | grep -q "nutrigence-postgres"; then
        print_warning "PostgreSQL container already exists"
        read -p "Do you want to remove the existing container and create a new one? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker stop nutrigence-postgres 2>/dev/null || true
            docker rm nutrigence-postgres 2>/dev/null || true
        fi
    fi
    
    # Create PostgreSQL container
    docker run --name nutrigence-postgres \
        -e POSTGRES_DB=nutrigence_db \
        -e POSTGRES_USER=nutrigence_user \
        -e POSTGRES_PASSWORD=password \
        -p 5432:5432 \
        -d postgres:15
    
    print_success "PostgreSQL container started"
    print_status "Waiting for database to be ready..."
    sleep 5
    
else
    print_warning "Docker not found. Please install PostgreSQL manually:"
    echo "  - Windows: Download from https://www.postgresql.org/download/windows/"
    echo "  - macOS: brew install postgresql && brew services start postgresql"
    echo "  - Linux: sudo apt install postgresql postgresql-contrib"
    echo ""
    echo "Then create the database:"
    echo "  psql -U postgres"
    echo "  CREATE DATABASE nutrigence_db;"
    echo "  CREATE USER nutrigence_user WITH PASSWORD 'password';"
    echo "  GRANT ALL PRIVILEGES ON DATABASE nutrigence_db TO nutrigence_user;"
    echo "  \\q"
fi

print_success "Setup completed successfully!"
echo ""
echo "🎉 Your Nutrigence development environment is ready!"
echo ""
echo "Next steps:"
echo "1. Start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate  # or venv\\Scripts\\activate on Windows"
echo "   python api.py"
echo ""
echo "2. Start the frontend (in a new terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Visit http://localhost:5173 in your browser"
echo ""
echo "📚 For more information, see LOCAL_DEVELOPMENT_SETUP.md"
