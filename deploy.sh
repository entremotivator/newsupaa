#!/bin/bash

# Enhanced Streamlit User Management System - Deployment Script
# This script helps set up and deploy the application

set -e  # Exit on any error

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

# Function to check Python version
check_python_version() {
    print_status "Checking Python version..."
    
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
            print_success "Python $PYTHON_VERSION detected (✓)"
            return 0
        else
            print_error "Python 3.11+ required, found $PYTHON_VERSION"
            return 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.11 or higher."
        return 1
    fi
}

# Function to set up virtual environment
setup_venv() {
    print_status "Setting up virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip
    print_success "Pip upgraded"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed"
    else
        print_error "requirements.txt not found"
        return 1
    fi
}

# Function to set up environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Environment file created from template"
            print_warning "Please edit .env with your actual configuration values"
            print_warning "Especially update the Supabase credentials:"
            print_warning "  - SUPABASE_URL"
            print_warning "  - SUPABASE_ANON_KEY"
            print_warning "  - SUPABASE_SERVICE_ROLE_KEY"
        else
            print_error ".env.example not found"
            return 1
        fi
    else
        print_warning "Environment file already exists"
    fi
}

# Function to run setup validation
run_validation() {
    print_status "Running setup validation..."
    
    if [ -f "test_setup.py" ]; then
        python test_setup.py
        if [ $? -eq 0 ]; then
            print_success "All tests passed!"
        else
            print_warning "Some tests failed, but application may still work"
        fi
    else
        print_warning "test_setup.py not found, skipping validation"
    fi
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p .streamlit
    mkdir -p assets
    mkdir -p components
    mkdir -p config
    mkdir -p pages
    mkdir -p logs
    mkdir -p uploads
    
    print_success "Directories created"
}

# Function to set file permissions
set_permissions() {
    print_status "Setting file permissions..."
    
    chmod +x deploy.sh
    chmod +x test_setup.py 2>/dev/null || true
    
    print_success "Permissions set"
}

# Function to start the application
start_application() {
    print_status "Starting the application..."
    
    print_success "Application is ready to start!"
    echo ""
    echo "To start the application, run:"
    echo "  source venv/bin/activate  # Activate virtual environment"
    echo "  streamlit run main.py     # Start the application"
    echo ""
    echo "The application will be available at: http://localhost:8501"
    echo ""
    echo "Default admin credentials (if using demo mode):"
    echo "  Email: admin@example.com"
    echo "  Password: admin123"
    echo ""
    echo "Remember to:"
    echo "  1. Configure your Supabase credentials in .env"
    echo "  2. Set up your database tables"
    echo "  3. Create your first admin user"
}

# Function to show help
show_help() {
    echo "Enhanced Streamlit User Management System - Deployment Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  setup     Full setup (default)"
    echo "  install   Install dependencies only"
    echo "  validate  Run validation tests only"
    echo "  start     Start the application"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup     # Full setup process"
    echo "  $0 install   # Install dependencies"
    echo "  $0 validate  # Run tests"
    echo "  $0 start     # Start application"
}

# Main deployment function
main_setup() {
    echo "🚀 Enhanced Streamlit User Management System"
    echo "=============================================="
    echo ""
    
    # Check prerequisites
    if ! check_python_version; then
        exit 1
    fi
    
    # Create directories
    create_directories
    
    # Set up virtual environment
    setup_venv
    
    # Install dependencies
    if ! install_dependencies; then
        exit 1
    fi
    
    # Set up environment
    setup_environment
    
    # Set permissions
    set_permissions
    
    # Run validation
    run_validation
    
    # Show start instructions
    start_application
}

# Parse command line arguments
case "${1:-setup}" in
    setup)
        main_setup
        ;;
    install)
        print_status "Installing dependencies only..."
        setup_venv
        install_dependencies
        ;;
    validate)
        print_status "Running validation only..."
        run_validation
        ;;
    start)
        print_status "Starting application..."
        if [ -d "venv" ]; then
            source venv/bin/activate
        fi
        streamlit run main.py
        ;;
    help)
        show_help
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac
