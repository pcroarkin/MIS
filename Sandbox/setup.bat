@echo off
SETLOCAL

echo Setting up Print MIS development environment...

:: Check if Python 3 is installed
python --version > NUL 2>&1
if errorlevel 1 (
    echo Python 3 is required but not installed. Please install Python 3 and try again.
    exit /b 1
)

:: Display Python version
python -c "import sys; print('Found Python version:', '.'.join(map(str, sys.version_info[:2])))"

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists.
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

:: Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file from example...
    copy .env.example .env
    echo Please update .env with your configuration settings.
) else (
    echo .env file already exists.
)

:: Create necessary directories
echo Creating necessary directories...
if not exist "app\static\uploads" mkdir app\static\uploads
if not exist "app\static\generated" mkdir app\static\generated
if not exist "app\logs" mkdir app\logs
if not exist "instance" mkdir instance

:: Initialize the database
echo Initializing the database...
flask init_db

:: Ask about demo data
set /p DEMO="Would you like to create demo data? (y/n): "
if /i "%DEMO%"=="y" (
    echo Creating demo data...
    flask demo_data
)

echo.
echo Setup complete! You can now run the application with:
echo flask run
echo.
echo Remember to:
echo 1. Update the .env file with your configuration
echo 2. Create a new admin password
echo.
echo Default admin credentials:
echo Username: admin
echo Password: admin
echo.
echo For security, please change these credentials after first login.

:: Deactivate virtual environment
deactivate

ENDLOCAL
