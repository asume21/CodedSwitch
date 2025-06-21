@echo off
echo 🚀 CodedSwitch AI Code Translator - Starting Application
echo ====================================================

REM Check if virtual environment exists
if not exist ".venv" (
    echo ❌ Virtual environment not found!
    echo Please run setup.bat first to create the environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Set API key from .env file if it exists
if exist ".env" (
    echo 🔑 Loading environment variables from .env file...
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        if "%%a"=="GEMINI_API_KEY" set GEMINI_API_KEY=%%b
    )
)

REM Check if API key is set
if "%GEMINI_API_KEY%"=="" (
    echo ⚠️ GEMINI_API_KEY not found in environment
    echo Please set your API key in the .env file
    echo.
    set /p GEMINI_API_KEY=Enter your Gemini API key: 
    if "%GEMINI_API_KEY%"=="" (
        echo ❌ No API key provided
        pause
        exit /b 1
    )
)

echo ✅ API key configured
echo 🚀 Starting CodedSwitch...
echo.

REM Run the application
python main.py

echo.
echo 👋 Application closed
pause
