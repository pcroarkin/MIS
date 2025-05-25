#!/bin/bash

# Print MIS Development Environment Setup Script

echo "Setting up Print MIS development environment..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3 and try again."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Found Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo "Please update .env with your configuration settings."
else
    echo ".env file already exists."
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p app/static/uploads
mkdir -p app/static/generated
mkdir -p app/logs
mkdir -p instance

# Initialize the database
echo "Initializing the database..."
flask init_db

# Create demo data if requested
read -p "Would you like to create demo data? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Creating demo data..."
    flask demo_data
fi

echo
echo "Setup complete! You can now run the application with:"
echo "flask run"
echo
echo "Remember to:"
echo "1. Update the .env file with your configuration"
echo "2. Create a new admin password"
echo
echo "Default admin credentials:"
echo "Username: admin"
echo "Password: admin"
echo
echo "For security, please change these credentials after first login."

# Deactivate virtual environment
deactivate
