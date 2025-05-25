@echo off
echo Print MIS Database Fix Script
echo ============================
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Check if instance directory exists
if not exist "instance" (
    echo Creating instance directory...
    mkdir instance
)

echo Attempting to fix database...
python fix_db.py

REM Check Python exit status
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Database fix completed successfully!
    echo.
    echo Next steps:
    echo 1. Restart your Flask application
    echo 2. Try logging in again
    echo 3. If you still experience issues, please check the logs or contact support
) else (
    echo.
    echo Error: Database fix encountered problems.
    echo.
    echo Please try the following:
    echo 1. Ensure you have proper permissions on the instance directory
    echo 2. Make sure no other process is using the database
    echo 3. Check if you have enough disk space
    echo.
    echo If problems persist, please contact support with the error messages above.
)

REM Deactivate virtual environment if it was activated
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\deactivate.bat
)

echo.
pause
