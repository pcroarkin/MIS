#!/bin/bash

# Script to fix database issues in Print MIS

echo "Print MIS Database Fix Script"
echo "============================"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if instance directory exists, if not create it
if [ ! -d "instance" ]; then
    echo "Creating instance directory..."
    mkdir instance
fi

echo "Attempting to fix database..."
python fix_db.py

# Verify Python exit status
if [ $? -eq 0 ]; then
    echo
    echo "Database fix completed successfully!"
    echo
    echo "Next steps:"
    echo "1. Restart your Flask application"
    echo "2. Try logging in again"
    echo "3. If you still experience issues, please check the logs or contact support"
else
    echo
    echo "Error: Database fix encountered problems."
    echo
    echo "Please try the following:"
    echo "1. Ensure you have proper permissions on the instance directory"
    echo "2. Make sure no other process is using the database"
    echo "3. Check if you have enough disk space"
    echo
    echo "If problems persist, please contact support with the error messages above."
fi

# Deactivate virtual environment if it was activated
if [ -d "venv" ]; then
    deactivate
fi
