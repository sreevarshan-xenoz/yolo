@echo off
echo YOLO People Counter Setup and Run Script
echo =======================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Setting up virtual environment...

:: Create virtual environment if it doesn't exist
if not exist venv (
    python -m venv venv
    echo Created virtual environment.
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Install requirements
echo Installing required packages...
pip install -r requirements.txt

echo.
echo Setup complete! Choose an option to run:
echo.
echo 1. Download sample data
echo 2. Count people in an image
echo 3. Count people in a video
echo 4. Use webcam for real-time people counting
echo 5. Exit
echo.

set /p choice=Enter your choice (1-5): 

if "%choice%"=="1" (
    echo.
    echo Downloading sample data...
    python sample_data_downloader.py
    echo.
    pause
    goto :eof
)

if "%choice%"=="2" (
    echo.
    set /p image_path=Enter path to image file: 
    echo Processing image...
    python people_counter.py --source "%image_path%" --output "result_image.jpg"
    echo.
    pause
    goto :eof
)

if "%choice%"=="3" (
    echo.
    set /p video_path=Enter path to video file: 
    echo Processing video...
    python people_counter.py --source "%video_path%" --output "result_video.mp4"
    echo.
    pause
    goto :eof
)

if "%choice%"=="4" (
    echo.
    echo Starting webcam people counter...
    python webcam_counter.py
    echo.
    pause
    goto :eof
)

if "%choice%"=="5" (
    echo Exiting...
    goto :eof
)

echo Invalid choice. Please run the script again.
pause